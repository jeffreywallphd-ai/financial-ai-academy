"""Dependency-light conformance runner for provenance v1."""

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

from financial_ai_academy.modules.audit.adapters import (
    envelope_from_mapping,
    envelope_payload,
    lineage_view_from_mapping,
    lineage_view_payload,
)
from financial_ai_academy.modules.audit.domain import InvalidProvenance


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


def default_schema_dir() -> Path:
    return repository_root() / "contracts/provenance/v1"


def default_corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/provenance/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject("provenance.schema_invalid", path.name, "Record must be an object.")
    return value


class ProvenanceContractValidator:
    def __init__(self, schema_dir: Path | None = None) -> None:
        root = schema_dir or default_schema_dir()
        self.schemas = {
            "envelope": load_json(root / "envelope.schema.json"),
            "lineage_request": load_json(root / "lineage-request.schema.json"),
            "lineage_view": load_json(root / "lineage-view.schema.json"),
        }
        for schema in self.schemas.values():
            Draft202012Validator.check_schema(schema)
        self.validators = {
            name: Draft202012Validator(schema, format_checker=FormatChecker())
            for name, schema in self.schemas.items()
        }

    def _shape(self, name: str, value: Mapping[str, Any]) -> None:
        error = next(iter(self.validators[name].iter_errors(value)), None)
        if error is not None:
            location = ".".join(str(part) for part in error.absolute_path)
            reject(
                "provenance.schema_invalid",
                location or name,
                "Provenance record is malformed.",
            )

    def validate_envelope(self, value: Mapping[str, Any]):
        self._shape("envelope", value)
        try:
            return envelope_from_mapping(value)
        except (InvalidProvenance, TypeError, ValueError) as error:
            reference = error.reference if isinstance(error, InvalidProvenance) else "envelope"
            reject("provenance.invalid", reference, "Provenance record is inconsistent.")

    def validate_lineage_request(self, value: Mapping[str, Any]) -> None:
        self._shape("lineage_request", value)

    def validate_lineage_view(self, value: Mapping[str, Any]):
        self._shape("lineage_view", value)
        try:
            return lineage_view_from_mapping(value)
        except (InvalidProvenance, TypeError, ValueError) as error:
            reference = error.reference if isinstance(error, InvalidProvenance) else "lineage_view"
            reject("provenance.invalid", reference, "Provenance record is inconsistent.")


def approved_records(
    corpus: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = corpus or default_corpus_dir()
    return (
        load_json(root / "approved/published-lesson-envelope.json"),
        load_json(root / "approved/knowledge-check-envelope.json"),
        load_json(root / "approved/lineage-view.json"),
        load_json(root / "approved/incomplete-lineage-view.json"),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=default_corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        lesson, completion, view, incomplete = approved_records(arguments.corpus)
        validator = ProvenanceContractValidator()
        lesson_value = validator.validate_envelope(lesson)
        completion_value = validator.validate_envelope(completion)
        view_value = validator.validate_lineage_view(view)
        incomplete_value = validator.validate_lineage_view(incomplete)
        envelope_payload(lesson_value)
        envelope_payload(completion_value)
        lineage_view_payload(view_value)
        lineage_view_payload(incomplete_value)
    except (ConformanceFailure, OSError, RuntimeError, ValueError) as error:
        diagnostic = (
            error.diagnostic
            if isinstance(error, ConformanceFailure)
            else Diagnostic(
                "provenance.internal_error",
                "provenance",
                "Provenance conformance could not complete.",
            )
        )
        print(json.dumps({"valid": False, "diagnostic": diagnostic.as_dict()}, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "lesson_resource_id": lesson_value.resource.resource_id,
                "completion_resource_id": completion_value.resource.resource_id,
                "lineage_view_digest": view_value.view_digest,
                "incomplete_lineage_view_digest": incomplete_value.view_digest,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
