"""Dependency-light conformance runner for adaptation navigation state v1."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator


SUPPORTED_VERSION = "1.0.0"
TIMESTAMP_PROFILE = re.compile(
    r"^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])"
    r"T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$"
)


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    reference: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "reference": safe_reference(self.reference),
            "message": self.message,
        }


class ConformanceFailure(ValueError):
    def __init__(self, code: str, reference: str, message: str) -> None:
        self.diagnostic = Diagnostic(code, safe_reference(reference), message)
        super().__init__(message)


def safe_reference(value: object) -> str:
    return (
        str(value)
        .replace(chr(0), "")
        .replace("\r", " ")
        .replace("\n", " ")[:120]
    )


def reject(code: str, reference: str, message: str) -> None:
    raise ConformanceFailure(code, reference, message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_schema_dir() -> Path:
    return repository_root() / "contracts/learning/adaptation/v1"


def default_corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/adaptation-navigation/v1"


def default_graph_path() -> Path:
    return (
        repository_root()
        / "contracts/compatibility/curriculum-graph/v1/approved/graph.json"
    )


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject(
            "adaptation_navigation.schema_invalid",
            path.name,
            "Adaptation navigation input must be an object.",
        )
    return value


def canonical_timestamp(value: object) -> str:
    if not isinstance(value, str) or TIMESTAMP_PROFILE.fullmatch(value) is None:
        raise ValueError("timestamp is outside the supported profile")
    try:
        parsed = datetime.fromisoformat(
            value.removesuffix("Z") + ("+00:00" if value.endswith("Z") else "")
        )
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("timestamp requires an offset")
        return parsed.astimezone(timezone.utc).isoformat().removesuffix(
            "+00:00"
        ) + "Z"
    except (OverflowError, ValueError) as error:
        raise ValueError("timestamp cannot be represented canonically") from error


def canonical_source_set_bytes(source: Mapping[str, Any]) -> bytes:
    meaning = {
        "schema_version": source["schema_version"],
        "curriculum_id": source["curriculum_id"],
        "curriculum_version": source["curriculum_version"],
        "graph_digest": source["graph_digest"],
        "activity_facts": deepcopy(source["activity_facts"]),
    }
    return json.dumps(
        meaning,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def source_set_digest(source: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_source_set_bytes(source)).hexdigest()


def canonical_projection_bytes(projection: Mapping[str, Any]) -> bytes:
    meaning = deepcopy(
        {key: value for key, value in projection.items() if key != "projection_digest"}
    )
    meaning["evaluated_at"] = canonical_timestamp(meaning["evaluated_at"])
    return json.dumps(
        meaning,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def projection_digest(projection: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_projection_bytes(projection)).hexdigest()


def expected_activity_states(
    source: Mapping[str, Any],
    graph: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Independently derive the complete deterministic policy result."""
    facts = {item["activity_id"]: item for item in source["activity_facts"]}
    requirements = {
        item["activity_id"]: "unassigned" for item in graph["activities"]
    }
    for branch in graph["branches"]:
        requirement = "required" if branch["kind"] == "required" else "optional"
        for activity_id in branch["activity_ids"]:
            requirements[activity_id] = requirement
    prerequisites: dict[str, list[Mapping[str, Any]]] = {
        item["activity_id"]: [] for item in graph["activities"]
    }
    for relationship in graph["relationships"]:
        if relationship["kind"] == "activity_prerequisite":
            prerequisites[relationship["target_id"]].append(relationship)

    requirement_reasons = {
        "required": (
            "required_activity",
            "This activity belongs to a required curriculum branch.",
        ),
        "optional": (
            "optional_activity",
            "This activity belongs to an optional curriculum branch.",
        ),
        "unassigned": (
            "unassigned_activity",
            "This activity is not assigned to a required or optional branch.",
        ),
    }
    states: list[dict[str, Any]] = []
    for activity in graph["activities"]:
        activity_id = activity["activity_id"]
        fact = facts[activity_id]
        requirement = requirements[activity_id]
        reasons: list[dict[str, Any]] = []
        if fact["completion_state"] == "completed":
            reasons.append(
                {
                    "code": "activity_completed",
                    "explanation": (
                        "Accepted completion evidence exists for this exact activity."
                    ),
                    "references": [activity_id],
                }
            )
        requirement_code, requirement_text = requirement_reasons[requirement]
        reasons.append(
            {
                "code": requirement_code,
                "explanation": requirement_text,
                "references": [activity_id],
            }
        )

        if fact["activity_source_state"] == "unavailable":
            eligibility = "unavailable"
            reasons.append(
                {
                    "code": "activity_source_unavailable",
                    "explanation": (
                        "The exact activity source is currently unavailable."
                    ),
                    "references": [activity_id],
                }
            )
        elif fact["completion_state"] == "unavailable":
            eligibility = "unavailable"
            reasons.append(
                {
                    "code": "completion_source_unavailable",
                    "explanation": (
                        "Current completion evidence cannot be evaluated safely."
                    ),
                    "references": [activity_id],
                }
            )
        else:
            incoming = prerequisites[activity_id]
            unmet = [
                relationship
                for relationship in incoming
                if facts[relationship["source_id"]]["completion_state"]
                != "completed"
                or facts[relationship["source_id"]]["activity_source_state"]
                != "available"
            ]
            if unmet:
                eligibility = "locked"
                for relationship in unmet:
                    prerequisite = facts[relationship["source_id"]]
                    unavailable = (
                        prerequisite["completion_state"] == "unavailable"
                        or prerequisite["activity_source_state"] == "unavailable"
                    )
                    reasons.append(
                        {
                            "code": (
                                "prerequisite_unavailable"
                                if unavailable
                                else "prerequisite_incomplete"
                            ),
                            "explanation": (
                                "A required prerequisite cannot be evaluated safely."
                                if unavailable
                                else "A required prerequisite is not complete."
                            ),
                            "references": [
                                activity_id,
                                relationship["source_id"],
                                relationship["relationship_id"],
                            ],
                        }
                    )
            else:
                eligibility = "eligible"
                if incoming:
                    for relationship in incoming:
                        reasons.append(
                            {
                                "code": "prerequisite_satisfied",
                                "explanation": (
                                    "A required activity prerequisite is complete."
                                ),
                                "references": [
                                    activity_id,
                                    relationship["source_id"],
                                    relationship["relationship_id"],
                                ],
                            }
                        )
                else:
                    reasons.append(
                        {
                            "code": "entry_activity",
                            "explanation": (
                                "This activity has no activity prerequisite."
                            ),
                            "references": [activity_id],
                        }
                    )
        states.append(
            {
                "activity_id": activity_id,
                "completion": fact["completion_state"],
                "eligibility": eligibility,
                "requirement": requirement,
                "availability": fact["activity_source_state"],
                "reasons": reasons,
            }
        )
    return states


class AdaptationNavigationContractValidator:
    def __init__(self, schema_dir: Path | None = None) -> None:
        root = schema_dir or default_schema_dir()
        self.source_schema = load_json(root / "source-facts.schema.json")
        self.projection_schema = load_json(root / "navigation-state.schema.json")
        Draft202012Validator.check_schema(self.source_schema)
        Draft202012Validator.check_schema(self.projection_schema)
        self._source = Draft202012Validator(self.source_schema)
        self._projection = Draft202012Validator(self.projection_schema)

    @staticmethod
    def _version(value: Mapping[str, Any]) -> None:
        if value.get("schema_version") != SUPPORTED_VERSION:
            reject(
                "adaptation_navigation.unsupported_version",
                "schema_version",
                "Adaptation navigation version is unsupported.",
            )

    @staticmethod
    def _shape(
        validator: Draft202012Validator,
        value: Mapping[str, Any],
        reference: str,
    ) -> None:
        error = next(iter(validator.iter_errors(value)), None)
        if error is not None:
            location = ".".join(str(part) for part in error.absolute_path)
            reject(
                "adaptation_navigation.schema_invalid",
                location or reference,
                "Adaptation navigation record is malformed.",
            )

    @staticmethod
    def _timestamp(value: Mapping[str, Any]) -> None:
        try:
            canonical_timestamp(value["evaluated_at"])
        except (KeyError, TypeError, ValueError):
            reject(
                "adaptation_navigation.schema_invalid",
                "evaluated_at",
                "Adaptation navigation record is malformed.",
            )

    def validate_pair(
        self,
        source: Mapping[str, Any],
        projection: Mapping[str, Any],
        graph: Mapping[str, Any],
    ) -> None:
        self._version(source)
        self._version(projection)
        self._shape(self._source, source, "source-facts")
        self._shape(self._projection, projection, "navigation-state")
        self._timestamp(source)
        self._timestamp(projection)
        shared = (
            "curriculum_id",
            "curriculum_version",
            "graph_digest",
            "policy_id",
            "policy_version",
            "evaluated_at",
        )
        if any(
            canonical_timestamp(source[key]) != canonical_timestamp(projection[key])
            if key == "evaluated_at"
            else source[key] != projection[key]
            for key in shared
        ):
            reject(
                "adaptation_navigation.context_mismatch",
                "navigation-state",
                "Adaptation navigation context does not match.",
            )
        if (
            source["curriculum_id"] != graph.get("curriculum_id")
            or source["curriculum_version"] != graph.get("curriculum_version")
            or source["graph_digest"] != graph.get("graph_digest")
        ):
            reject(
                "adaptation_navigation.context_mismatch",
                "curriculum-graph",
                "Adaptation navigation graph context does not match.",
            )
        activity_ids = [item["activity_id"] for item in graph["activities"]]
        fact_ids = [item["activity_id"] for item in source["activity_facts"]]
        state_ids = [item["activity_id"] for item in projection["activity_states"]]
        if (
            len(fact_ids) != len(activity_ids)
            or set(fact_ids) != set(activity_ids)
            or state_ids != activity_ids
        ):
            reject(
                "adaptation_navigation.source_closure_invalid",
                "activities",
                "Adaptation navigation source closure is invalid.",
            )
        facts_by_id = {
            item["activity_id"]: item for item in source["activity_facts"]
        }
        ordered_source = deepcopy(source)
        ordered_source["activity_facts"] = [
            facts_by_id[activity_id] for activity_id in activity_ids
        ]
        if projection["source_set_digest"] != source_set_digest(ordered_source):
            reject(
                "adaptation_navigation.source_digest_mismatch",
                "source_set_digest",
                "Adaptation navigation source digest does not match.",
            )
        if projection["projection_digest"] != projection_digest(projection):
            reject(
                "adaptation_navigation.projection_digest_mismatch",
                "projection_digest",
                "Adaptation navigation projection digest does not match.",
            )
        if projection["activity_states"] != expected_activity_states(
            ordered_source,
            graph,
        ):
            reject(
                "adaptation_navigation.source_meaning_mismatch",
                "activity_states",
                "Adaptation navigation source meaning does not match.",
            )


def approved_pair(
    corpus: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    root = corpus or default_corpus_dir()
    return (
        load_json(root / "approved/source-facts.json"),
        load_json(root / "approved/navigation-state.json"),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=default_corpus_dir())
    parser.add_argument("--graph", type=Path, default=default_graph_path())
    arguments = parser.parse_args(argv)
    try:
        source, projection = approved_pair(arguments.corpus)
        graph = load_json(arguments.graph)
        AdaptationNavigationContractValidator().validate_pair(
            source,
            projection,
            graph,
        )
    except (ConformanceFailure, OSError, RuntimeError, ValueError) as error:
        diagnostic = (
            error.diagnostic
            if isinstance(error, ConformanceFailure)
            else Diagnostic(
                "adaptation_navigation.internal_error",
                "navigation-state",
                "Adaptation navigation conformance could not complete.",
            )
        )
        print(
            json.dumps(
                {"valid": False, "diagnostic": diagnostic.as_dict()},
                sort_keys=True,
            )
        )
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "curriculum_id": projection["curriculum_id"],
                "curriculum_version": projection["curriculum_version"],
                "activity_count": len(projection["activity_states"]),
                "projection_digest": projection["projection_digest"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
