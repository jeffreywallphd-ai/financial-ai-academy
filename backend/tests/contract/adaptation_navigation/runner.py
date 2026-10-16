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
        known_references = set(activity_ids) | {
            item["relationship_id"] for item in graph["relationships"]
        }
        for state in projection["activity_states"]:
            fact = facts_by_id[state["activity_id"]]
            if (
                state["completion"] != fact["completion_state"]
                or state["availability"] != fact["activity_source_state"]
            ):
                reject(
                    "adaptation_navigation.source_meaning_mismatch",
                    state["activity_id"],
                    "Adaptation navigation source meaning does not match.",
                )
            for reason in state["reasons"]:
                if any(item not in known_references for item in reason["references"]):
                    reject(
                        "adaptation_navigation.reason_reference_invalid",
                        state["activity_id"],
                        "Adaptation navigation reason reference is invalid.",
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
