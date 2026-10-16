"""Dependency-light conformance runner for Curriculum practice-review v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker


class PracticeReviewFailure(ValueError):
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
    return (
        repository_root()
        / "contracts/learning/curriculum/v1/practice-review-target/target.schema.json"
    )


def corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/curriculum-practice-review/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PracticeReviewFailure(
            "curriculum.practice_review.schema_invalid", path.name, "Review target must be an object."
        )
    return value


class PracticeReviewValidator:
    def __init__(self, path: Path | None = None) -> None:
        self.schema = load_json(path or schema_path())
        Draft202012Validator.check_schema(self.schema)
        self.validator = Draft202012Validator(
            self.schema, format_checker=FormatChecker()
        )

    def validate(self, value: Mapping[str, Any]) -> None:
        error = next(iter(self.validator.iter_errors(value)), None)
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            raise PracticeReviewFailure(
                "curriculum.practice_review.schema_invalid",
                reference or "target",
                "Practice review target is malformed.",
            )


def select_review_targets(
    declared_reference_ids: Sequence[str],
    incorrect_item_reference_ids: Sequence[Sequence[str]],
    targets: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    """Select unique incorrect-item references in declaration order."""
    requested = {
        reference_id
        for item_references in incorrect_item_reference_ids
        for reference_id in item_references
    }
    ordered = [reference_id for reference_id in declared_reference_ids if reference_id in requested]
    by_id = {str(target["resource_id"]): target for target in targets}
    return [by_id[reference_id] for reference_id in ordered if reference_id in by_id]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        approved = arguments.corpus / "approved"
        targets = [load_json(approved / name) for name in ("available.json", "unavailable.json")]
        validator = PracticeReviewValidator()
        for target in targets:
            validator.validate(target)
    except (OSError, ValueError) as error:
        failure = error if isinstance(error, PracticeReviewFailure) else PracticeReviewFailure(
            "curriculum.practice_review.internal_error", "target", "Review-target conformance could not complete."
        )
        print(json.dumps({"valid": False, "diagnostic": failure.as_dict()}, sort_keys=True))
        return 1
    print(json.dumps({"valid": True, "states": [target["state"] for target in targets]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
