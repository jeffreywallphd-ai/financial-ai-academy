"""Dependency-light conformance runner for contextual-help v1."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker

BACKEND_ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = BACKEND_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from financial_ai_academy.modules.guidance.adapters import context_from_mapping
from financial_ai_academy.modules.guidance.domain import GuidanceError


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
    return str(value).replace(chr(0), "").replace("\r", " ").replace("\n", " ")[:120]


def reject(code: str, reference: str, message: str) -> None:
    raise ConformanceFailure(code, _safe_reference(reference), message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_schema_path() -> Path:
    return repository_root() / "contracts/guidance/contextual-help/v1/context.schema.json"


def default_corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/contextual-help/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject("contextual_help.schema_invalid", path.name, "Record must be an object.")
    return value


class ContextualHelpContractValidator:
    def __init__(self, schema_path: Path | None = None) -> None:
        self.schema = load_json(schema_path or default_schema_path())
        Draft202012Validator.check_schema(self.schema)
        self.validator = Draft202012Validator(
            self.schema,
            format_checker=FormatChecker(),
        )

    def validate_context(self, value: Mapping[str, Any]):
        error = next(iter(self.validator.iter_errors(value)), None)
        if error is not None:
            location = ".".join(str(part) for part in error.absolute_path)
            reject(
                "contextual_help.schema_invalid",
                location or "context",
                "Contextual help record is malformed.",
            )
        try:
            return context_from_mapping(value)
        except GuidanceError as error:
            reject(
                f"contextual_help.{error.code.value}",
                error.reference,
                error.message,
            )


def approved_record(corpus: Path | None = None) -> dict[str, Any]:
    return load_json((corpus or default_corpus_dir()) / "approved/context.json")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=default_corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        admitted = ContextualHelpContractValidator().validate_context(
            approved_record(arguments.corpus)
        )
    except (ConformanceFailure, OSError, RuntimeError, ValueError) as error:
        diagnostic = (
            error.diagnostic
            if isinstance(error, ConformanceFailure)
            else Diagnostic(
                "contextual_help.internal_error",
                "contextual-help",
                "Contextual help conformance could not complete.",
            )
        )
        print(json.dumps({"valid": False, "diagnostic": diagnostic.as_dict()}, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "context_key": admitted.context_key,
                "context_version": admitted.context_version,
                "context_digest": admitted.context_digest,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
