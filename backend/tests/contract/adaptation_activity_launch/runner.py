"""Dependency-light conformance runner for activity-launch v1."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
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


def default_schema_path() -> Path:
    return repository_root() / "contracts/learning/adaptation/v1/activity-launch.schema.json"


def default_corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/adaptation-activity-launch/v1"


def default_graph_path() -> Path:
    return repository_root() / "contracts/compatibility/curriculum-graph/v1/approved/graph.json"


def default_navigation_path() -> Path:
    return repository_root() / "contracts/compatibility/adaptation-navigation/v1/approved/navigation-state.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject(
            "adaptation_activity_launch.schema_invalid",
            path.name,
            "Activity launch input must be an object.",
        )
    return value


def canonical_timestamp(value: object) -> str:
    if not isinstance(value, str) or TIMESTAMP_PROFILE.fullmatch(value) is None:
        raise ValueError("timestamp is outside the supported profile")
    parsed = datetime.fromisoformat(
        value.removesuffix("Z") + ("+00:00" if value.endswith("Z") else "")
    )
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp requires an offset")
    return parsed.astimezone(timezone.utc).isoformat().removesuffix("+00:00") + "Z"


def projection_digest(projection: Mapping[str, Any]) -> str:
    meaning = {key: value for key, value in projection.items() if key != "projection_digest"}
    meaning["evaluated_at"] = canonical_timestamp(meaning["evaluated_at"])
    payload = json.dumps(
        meaning,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class ActivityLaunchContractValidator:
    def __init__(self, schema_path: Path | None = None) -> None:
        self.schema = load_json(schema_path or default_schema_path())
        self.navigation_schema = load_json(
            (schema_path or default_schema_path()).parent
            / "navigation-state.schema.json"
        )
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator.check_schema(self.navigation_schema)
        self._validator = Draft202012Validator(self.schema)
        self._navigation_validator = Draft202012Validator(
            self.navigation_schema
        )

    def validate(
        self,
        launch: Mapping[str, Any],
        graph: Mapping[str, Any],
        navigation: Mapping[str, Any],
    ) -> None:
        if launch.get("schema_version") != SUPPORTED_VERSION:
            reject(
                "adaptation_activity_launch.unsupported_version",
                "schema_version",
                "Activity launch version is unsupported.",
            )
        if navigation.get("schema_version") != SUPPORTED_VERSION:
            reject(
                "adaptation_activity_launch.navigation_mismatch",
                "navigation-state",
                "Activity launch navigation state does not match.",
            )
        error = next(iter(self._validator.iter_errors(launch)), None)
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            reject(
                "adaptation_activity_launch.schema_invalid",
                reference or "activity-launch",
                "Activity launch record is malformed.",
            )
        navigation_error = next(
            iter(self._navigation_validator.iter_errors(navigation)), None
        )
        if navigation_error is not None:
            reference = ".".join(
                str(part) for part in navigation_error.absolute_path
            )
            reject(
                "adaptation_activity_launch.navigation_mismatch",
                reference or "navigation-state",
                "Activity launch navigation state does not match.",
            )
        shared = ("curriculum_id", "curriculum_version", "graph_digest")
        if any(
            launch[key] != graph.get(key) or launch[key] != navigation.get(key)
            for key in shared
        ):
            reject(
                "adaptation_activity_launch.context_mismatch",
                "curriculum-context",
                "Activity launch context does not match.",
            )
        try:
            evaluated_at = canonical_timestamp(launch["evaluated_at"])
            navigation_time = canonical_timestamp(navigation["evaluated_at"])
        except (KeyError, OverflowError, TypeError, ValueError):
            reject(
                "adaptation_activity_launch.schema_invalid",
                "evaluated_at",
                "Activity launch record is malformed.",
            )
        if (
            evaluated_at != navigation_time
            or launch["navigation_projection_digest"]
            != navigation.get("projection_digest")
            or navigation.get("projection_digest") != projection_digest(navigation)
        ):
            reject(
                "adaptation_activity_launch.navigation_mismatch",
                "navigation-state",
                "Activity launch navigation state does not match.",
            )
        graph_activities = graph.get("activities", [])
        navigation_states = navigation.get("activity_states", [])
        if [item.get("activity_id") for item in navigation_states] != [
            item.get("activity_id") for item in graph_activities
        ]:
            reject(
                "adaptation_activity_launch.navigation_mismatch",
                "activity_states",
                "Activity launch navigation state does not match.",
            )
        activities = {
            item["activity_id"]: item for item in graph_activities
        }
        states = {
            item["activity_id"]: item
            for item in navigation_states
        }
        activity = activities.get(launch["activity_id"])
        state = states.get(launch["activity_id"])
        if activity is None or state is None:
            reject(
                "adaptation_activity_launch.activity_not_found",
                launch["activity_id"],
                "Activity is not part of this curriculum version.",
            )
        reference = activity.get("reference", {})
        if activity.get("kind") != "lesson" or reference.get(
            "reference_kind"
        ) != "lesson_placement":
            reject(
                "adaptation_activity_launch.unsupported_activity",
                launch["activity_id"],
                "This activity type cannot be opened here.",
            )
        if state.get("availability") != "available" or state.get("completion") == "unavailable" or state.get("eligibility") == "unavailable":
            reject(
                "adaptation_activity_launch.activity_unavailable",
                launch["activity_id"],
                "Activity is currently unavailable.",
            )
        if state.get("eligibility") == "locked":
            reject(
                "adaptation_activity_launch.activity_locked",
                launch["activity_id"],
                "Activity is not ready to open.",
            )
        if state.get("eligibility") != "eligible":
            reject(
                "adaptation_activity_launch.navigation_mismatch",
                launch["activity_id"],
                "Activity launch navigation state does not match.",
            )
        expected = {
            "placement_id": reference.get("placement_id"),
            "package_id": reference.get("package_id"),
            "package_version": reference.get("package_version"),
            "package_digest": reference.get("package_digest"),
            "destination": f"/learn/placements/{reference.get('placement_id')}",
        }
        if any(launch[key] != value for key, value in expected.items()):
            reject(
                "adaptation_activity_launch.reference_mismatch",
                launch["activity_id"],
                "Activity launch reference does not match.",
            )


def approved_launch(corpus: Path | None = None) -> dict[str, Any]:
    return load_json((corpus or default_corpus_dir()) / "approved/launch.json")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=default_corpus_dir())
    parser.add_argument("--graph", type=Path, default=default_graph_path())
    parser.add_argument("--navigation", type=Path, default=default_navigation_path())
    arguments = parser.parse_args(argv)
    try:
        launch = approved_launch(arguments.corpus)
        ActivityLaunchContractValidator().validate(
            launch,
            load_json(arguments.graph),
            load_json(arguments.navigation),
        )
    except (ConformanceFailure, OSError, RuntimeError, ValueError) as error:
        diagnostic = error.diagnostic if isinstance(error, ConformanceFailure) else Diagnostic(
            "adaptation_activity_launch.internal_error",
            "activity-launch",
            "Activity launch conformance could not complete.",
        )
        print(json.dumps({"valid": False, "diagnostic": diagnostic.as_dict()}, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "activity_id": launch["activity_id"],
                "curriculum_id": launch["curriculum_id"],
                "curriculum_version": launch["curriculum_version"],
                "destination": launch["destination"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
