"""Dependency-light conformance runner for practice-history v1."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker


PRIVATE_NAMES = {
    "learner_id", "selected_option_id", "selected_option_ids", "entered_value",
    "feedback", "answer", "correct_option_id", "correct_option_ids", "mastery",
}


class PracticeHistoryFailure(ValueError):
    def __init__(self, code: str, reference: str, message: str) -> None:
        self.code = code
        self.reference = str(reference).replace("\r", " ").replace("\n", " ")[:120]
        self.message = message
        super().__init__(message)

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "reference": self.reference, "message": self.message}


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def schema_path() -> Path:
    return repository_root() / "contracts/learning/learner-model/practice/v1/history.schema.json"


def corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/learner-model-practice-history/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PracticeHistoryFailure(
            "learner_model.practice_history.schema_invalid", path.name, "Practice history must be an object."
        )
    return value


def _private_name(value: object) -> str | None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key in PRIVATE_NAMES:
                return str(key)
            found = _private_name(nested)
            if found:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = _private_name(nested)
            if found:
                return found
    return None


def canonical_source_bytes(attempts: Sequence[Mapping[str, Any]]) -> bytes:
    return json.dumps(
        list(attempts), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def source_digest(attempts: Sequence[Mapping[str, Any]]) -> str:
    return hashlib.sha256(canonical_source_bytes(attempts)).hexdigest()


def ordered_unique_attempts(
    attempts: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return stable attempt order while making exact event replay idempotent."""
    by_event: dict[str, dict[str, Any]] = {}
    for value in attempts:
        attempt = copy.deepcopy(dict(value))
        event_id = str(attempt.get("event_id", ""))
        previous = by_event.get(event_id)
        if previous is not None and previous != attempt:
            raise PracticeHistoryFailure(
                "learner_model.practice_history.inconsistent_duplicate",
                "event_id",
                "A source event identity was reused for different meaning.",
            )
        by_event[event_id] = attempt
    return sorted(by_event.values(), key=lambda value: int(value.get("attempt_order", 0)))


class PracticeHistoryValidator:
    def __init__(self, path: Path | None = None) -> None:
        self.schema = load_json(path or schema_path())
        Draft202012Validator.check_schema(self.schema)
        self.validator = Draft202012Validator(
            self.schema, format_checker=FormatChecker()
        )

    def validate(self, history: Mapping[str, Any]) -> None:
        error = next(iter(self.validator.iter_errors(history)), None)
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            raise PracticeHistoryFailure(
                "learner_model.practice_history.schema_invalid",
                reference or "history",
                "Practice history is malformed.",
            )
        leaked = _private_name(history)
        if leaked:
            raise PracticeHistoryFailure(
                "learner_model.practice_history.private_field", leaked, "Practice history contains a private field."
            )
        attempts = history["attempts"]
        if ordered_unique_attempts(attempts) != attempts:
            raise PracticeHistoryFailure(
                "learner_model.practice_history.inconsistent_attempt",
                "attempts",
                "Practice attempts must have stable unique order.",
            )
        expected_orders = list(range(1, len(attempts) + 1))
        if [attempt["attempt_order"] for attempt in attempts] != expected_orders:
            raise PracticeHistoryFailure(
                "learner_model.practice_history.inconsistent_attempt",
                "attempt_order",
                "Practice attempt order must be contiguous.",
            )
        for attempt in attempts:
            item_score = sum(item["score"] for item in attempt["item_summaries"])
            item_maximum = sum(item["max_score"] for item in attempt["item_summaries"])
            for item in attempt["item_summaries"]:
                if item["correct"] is not (item["score"] == item["max_score"]):
                    self._inconsistent("correct")
                if item["correct"] and item["review_reference_ids"]:
                    self._inconsistent("review_reference_ids")
            if (
                attempt["score"] != item_score
                or attempt["max_score"] != item_maximum
                or attempt["outcome"] != ("all_correct" if item_score == item_maximum else "review_needed")
            ):
                self._inconsistent("score")
        if history["source_digest"] != source_digest(attempts):
            raise PracticeHistoryFailure(
                "learner_model.practice_history.source_digest_mismatch",
                "source_digest",
                "Practice history source digest does not match its attempts.",
            )

    @staticmethod
    def _inconsistent(reference: str) -> None:
        raise PracticeHistoryFailure(
            "learner_model.practice_history.inconsistent_attempt",
            reference,
            "Practice attempt summary is internally inconsistent.",
        )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        history = load_json(arguments.corpus / "approved/history.json")
        PracticeHistoryValidator().validate(history)
    except (OSError, ValueError) as error:
        failure = error if isinstance(error, PracticeHistoryFailure) else PracticeHistoryFailure(
            "learner_model.practice_history.internal_error", "history", "Practice-history conformance could not complete."
        )
        print(json.dumps({"valid": False, "diagnostic": failure.as_dict()}, sort_keys=True))
        return 1
    print(json.dumps({"valid": True, "attempt_count": len(history["attempts"]), "source_digest": history["source_digest"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
