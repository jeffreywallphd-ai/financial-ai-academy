"""Dependency-light conformance runner for Assessment v1 contracts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker


SUPPORTED_VERSION = "1.0.0"
SUPPORTED_ITEM_TYPE = "single_select"
SUPPORTED_POLICY_ID = "single-select-exact-match"
SUPPORTED_POLICY_VERSION = "1.0.0"
SUPPORTED_EVENT_TYPE = "assessment.knowledge-check.completed"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    reference: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "reference": _safe_reference(self.reference),
            "message": self.message,
        }


class ConformanceFailure(ValueError):
    def __init__(self, code: str, reference: str, message: str) -> None:
        self.diagnostic = Diagnostic(code, reference, message)
        super().__init__(message)


def _safe_reference(value: object) -> str:
    return (
        str(value)
        .replace(chr(0), "")
        .replace("\r", " ")
        .replace("\n", " ")[:120]
    )


def reject(code: str, reference: str, message: str) -> None:
    raise ConformanceFailure(code, _safe_reference(reference), message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_learning_schema_dir() -> Path:
    return repository_root() / "contracts/learning/assessment/v1"


def default_event_schema_dir() -> Path:
    return repository_root() / "contracts/events/assessment/v1"


def default_corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/assessment/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject("assessment.schema_invalid", path.name, "Record must be an object.")
    return value


def canonical_definition_bytes(assessment: Mapping[str, Any]) -> bytes:
    return json.dumps(
        assessment,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def definition_digest(definition: Mapping[str, Any]) -> str:
    assessment = definition.get("assessment")
    if not isinstance(assessment, Mapping):
        reject(
            "assessment.schema_invalid",
            "assessment",
            "Private definition is malformed.",
        )
    return hashlib.sha256(canonical_definition_bytes(assessment)).hexdigest()


class AssessmentContractValidator:
    def __init__(
        self,
        learning_schema_dir: Path | None = None,
        event_schema_dir: Path | None = None,
    ) -> None:
        learning = learning_schema_dir or default_learning_schema_dir()
        events = event_schema_dir or default_event_schema_dir()
        self._schemas = {
            "definition": load_json(learning / "definition.schema.json"),
            "presentation": load_json(learning / "presentation.schema.json"),
            "submission": load_json(learning / "submission.schema.json"),
            "result": load_json(learning / "result.schema.json"),
            "event": load_json(events / "knowledge-check-completed.schema.json"),
        }
        for schema in self._schemas.values():
            Draft202012Validator.check_schema(schema)

    def _shape(self, kind: str, value: Mapping[str, Any]) -> None:
        self._supported_versions(kind, value)
        validator = Draft202012Validator(
            self._schemas[kind], format_checker=FormatChecker()
        )
        error = next(iter(validator.iter_errors(value)), None)
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            reject(
                "assessment.schema_invalid",
                reference or kind,
                f"{kind.capitalize()} record is malformed.",
            )
        timestamps: tuple[tuple[str, object], ...] = ()
        if kind == "result":
            timestamps = (("submitted_at", value.get("submitted_at")),)
        elif kind == "event":
            payload = value.get("payload")
            completed_at = (
                payload.get("completed_at")
                if isinstance(payload, Mapping)
                else None
            )
            timestamps = (
                ("occurred_at", value.get("occurred_at")),
                ("payload.completed_at", completed_at),
            )
        for reference, timestamp in timestamps:
            try:
                parsed = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
            except ValueError:
                parsed = None
            if parsed is None or parsed.tzinfo is None:
                reject(
                    "assessment.schema_invalid",
                    reference,
                    f"{kind.capitalize()} record is malformed.",
                )

    @staticmethod
    def _supported_versions(kind: str, value: Mapping[str, Any]) -> None:
        if value.get("schema_version") != SUPPORTED_VERSION:
            reject(
                "assessment.unsupported_version",
                kind,
                "Assessment contract version is unsupported.",
            )
        if kind == "definition":
            assessment = value.get("assessment")
            if isinstance(assessment, Mapping):
                if assessment.get("assessment_version") != SUPPORTED_VERSION:
                    reject(
                        "assessment.unsupported_version",
                        "assessment_version",
                        "Assessment definition version is unsupported.",
                    )
                if assessment.get("item_type") != SUPPORTED_ITEM_TYPE:
                    reject(
                        "assessment.unsupported_item_type",
                        "item_type",
                        "Assessment item type is unsupported.",
                    )
                policy = assessment.get("scoring_policy")
                if isinstance(policy, Mapping) and (
                    policy.get("policy_id") != SUPPORTED_POLICY_ID
                    or policy.get("policy_version") != SUPPORTED_POLICY_VERSION
                ):
                    reject(
                        "assessment.unsupported_policy",
                        "scoring_policy",
                        "Assessment scoring policy is unsupported.",
                    )
        if kind == "event" and (
            value.get("event_type") != SUPPORTED_EVENT_TYPE
            or value.get("event_version") != SUPPORTED_VERSION
        ):
            reject(
                "assessment.unsupported_event_version",
                "event",
                "Assessment event version is unsupported.",
            )

    def validate_definition(self, definition: Mapping[str, Any]) -> None:
        self._shape("definition", definition)
        if definition_digest(definition) != definition["definition_digest"]:
            reject(
                "assessment.definition_digest_mismatch",
                "definition_digest",
                "Assessment definition digest does not match its meaning.",
            )
        item = definition["assessment"]["item"]
        option_ids = [option["option_id"] for option in item["options"]]
        if len(option_ids) != len(set(option_ids)):
            reject(
                "assessment.invalid_definition",
                "options",
                "Assessment option identities must be unique.",
            )
        if item["correct_option_id"] not in option_ids:
            reject(
                "assessment.invalid_definition",
                "correct_option_id",
                "Correct option must reference one declared option.",
            )

    def validate_presentation(
        self,
        definition: Mapping[str, Any],
        presentation: Mapping[str, Any],
    ) -> None:
        self.validate_definition(definition)
        self._shape("presentation", presentation)
        assessment = definition["assessment"]
        item = assessment["item"]
        expected = {
            "assessment_id": assessment["assessment_id"],
            "assessment_version": assessment["assessment_version"],
            "definition_digest": definition["definition_digest"],
            "item_type": assessment["item_type"],
            "item_id": item["item_id"],
            "item_version": item["item_version"],
            "scoring_policy_id": assessment["scoring_policy"]["policy_id"],
            "scoring_policy_version": assessment["scoring_policy"]["policy_version"],
            "prompt": item["prompt"],
            "options": item["options"],
        }
        for field, value in expected.items():
            if presentation.get(field) != value:
                reject(
                    "assessment.stale_reference",
                    field,
                    "Learner presentation does not match the exact definition.",
                )
        private_names = {"correct_option_id", "feedback", "scoring_policy"}
        if private_names.intersection(presentation):
            reject(
                "assessment.presentation_leak",
                "presentation",
                "Learner presentation contains private Assessment fields.",
            )

    def validate_submission(
        self,
        presentation: Mapping[str, Any],
        submission: Mapping[str, Any],
    ) -> None:
        self._shape("submission", submission)
        references = (
            "placement_id",
            "package_id",
            "package_version",
            "package_digest",
            "assessment_id",
            "assessment_version",
            "definition_digest",
            "item_id",
            "item_version",
            "scoring_policy_id",
            "scoring_policy_version",
        )
        for field in references:
            if submission.get(field) != presentation.get(field):
                reject(
                    "assessment.stale_reference",
                    field,
                    "Submission reference does not match the presented version.",
                )
        declared = {option["option_id"] for option in presentation["options"]}
        if submission["selected_option_id"] not in declared:
            reject(
                "assessment.unknown_option",
                "selected_option_id",
                "Selected option is not declared by this item version.",
            )

    def validate_result(
        self,
        definition: Mapping[str, Any],
        presentation: Mapping[str, Any],
        submission: Mapping[str, Any],
        result: Mapping[str, Any],
    ) -> None:
        self.validate_presentation(definition, presentation)
        self.validate_submission(presentation, submission)
        self._shape("result", result)
        copied = (
            "submission_id",
            "placement_id",
            "package_id",
            "package_version",
            "package_digest",
            "assessment_id",
            "assessment_version",
            "definition_digest",
            "item_id",
            "item_version",
            "scoring_policy_id",
            "scoring_policy_version",
            "selected_option_id",
        )
        if any(result.get(field) != submission.get(field) for field in copied):
            reject(
                "assessment.inconsistent_evidence",
                "provenance",
                "Result evidence does not match the submitted response.",
            )
        item = definition["assessment"]["item"]
        correct = submission["selected_option_id"] == item["correct_option_id"]
        feedback = item["feedback"]["correct" if correct else "incorrect"]
        if (
            result.get("score") != (1 if correct else 0)
            or result.get("max_score") != 1
            or result.get("correct") is not correct
            or result.get("feedback") != feedback
        ):
            reject(
                "assessment.inconsistent_evidence",
                "score",
                "Result does not match deterministic scoring and feedback.",
            )

    def validate_event(
        self, result: Mapping[str, Any], event: Mapping[str, Any]
    ) -> None:
        self._shape("event", event)
        payload = event["payload"]
        copied = (
            "learner_id",
            "placement_id",
            "package_id",
            "package_version",
            "package_digest",
            "assessment_id",
            "assessment_version",
            "definition_digest",
            "item_id",
            "item_version",
            "scoring_policy_id",
            "scoring_policy_version",
            "score",
            "max_score",
        )
        consistent = all(payload.get(field) == result.get(field) for field in copied)
        consistent = consistent and (
            event["aggregate"]["aggregate_id"] == result["attempt_id"]
            and event["source"]["evidence_id"] == result["evidence_id"]
            and event["idempotency_key"] == result["evidence_id"]
            and event["occurred_at"] == result["submitted_at"]
            and payload["completed_at"] == result["submitted_at"]
        )
        if not consistent:
            reject(
                "assessment.inconsistent_event",
                "event",
                "Completion event does not match its durable evidence.",
            )

    def validate_chain(
        self,
        definition: Mapping[str, Any],
        presentation: Mapping[str, Any],
        submission: Mapping[str, Any],
        result: Mapping[str, Any],
        event: Mapping[str, Any],
    ) -> None:
        self.validate_result(definition, presentation, submission, result)
        self.validate_event(result, event)


def approved_chain(
    corpus: Path, outcome: str
) -> tuple[dict[str, Any], ...]:
    approved = corpus / "approved"
    return (
        load_json(approved / "definition.json"),
        load_json(approved / "presentation.json"),
        load_json(approved / "submissions" / f"{outcome}.json"),
        load_json(approved / "results" / f"{outcome}.json"),
        load_json(approved / "events" / f"{outcome}.json"),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=default_corpus_dir())
    parser.add_argument(
        "--outcome", choices=("correct", "incorrect"), default="correct"
    )
    arguments = parser.parse_args(argv)
    try:
        chain = approved_chain(arguments.corpus, arguments.outcome)
        AssessmentContractValidator().validate_chain(*copy.deepcopy(chain))
    except (ConformanceFailure, OSError, RuntimeError, ValueError) as error:
        diagnostic = (
            error.diagnostic
            if isinstance(error, ConformanceFailure)
            else Diagnostic(
                "assessment.internal_error",
                "assessment",
                "Assessment conformance could not complete.",
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
                "outcome": arguments.outcome,
                "assessment_id": chain[0]["assessment"]["assessment_id"],
                "definition_digest": chain[0]["definition_digest"],
                "score": chain[3]["score"],
                "max_score": chain[3]["max_score"],
                "event_type": chain[4]["event_type"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
