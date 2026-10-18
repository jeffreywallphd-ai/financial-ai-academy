"""Dependency-light conformance runner for feature-guidance v1."""

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

from financial_ai_academy.modules.guidance.adapters import (
    feature_guidance_from_mapping,
    feature_mapping_from_mapping,
)
from financial_ai_academy.modules.guidance.domain import GuidanceError


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    reference: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "reference": _safe(self.reference), "message": self.message}


class ConformanceFailure(ValueError):
    def __init__(self, code: str, reference: str, message: str) -> None:
        self.diagnostic = Diagnostic(code, reference, message)
        super().__init__(message)


def _safe(value: object) -> str:
    return str(value).replace(chr(0), "").replace("\r", " ").replace("\n", " ")[:120]


def _reject(code: str, reference: str, message: str) -> None:
    raise ConformanceFailure(code, _safe(reference), message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_contract_dir() -> Path:
    return repository_root() / "contracts/guidance/feature-guidance/v1"


def default_corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/feature-guidance/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        _reject("feature_guidance.schema_invalid", path.name, "Artifact must be an object.")
    return value


class FeatureGuidanceContractValidator:
    def __init__(self, contract_dir: Path | None = None) -> None:
        root = contract_dir or default_contract_dir()
        record_schema = load_json(root / "record.schema.json")
        mapping_schema = load_json(root / "mapping.schema.json")
        Draft202012Validator.check_schema(record_schema)
        Draft202012Validator.check_schema(mapping_schema)
        self._record = Draft202012Validator(record_schema, format_checker=FormatChecker())
        self._mapping = Draft202012Validator(mapping_schema, format_checker=FormatChecker())

    def _schema(self, validator: Draft202012Validator, value: Mapping[str, Any], reference: str) -> None:
        error = next(iter(validator.iter_errors(value)), None)
        if error is not None:
            location = ".".join(str(part) for part in error.absolute_path)
            _reject("feature_guidance.schema_invalid", location or reference, "Feature guidance is malformed.")

    def validate_record(self, value: Mapping[str, Any]):
        self._schema(self._record, value, "record")
        try:
            return feature_guidance_from_mapping(value)
        except GuidanceError as error:
            _reject(f"feature_guidance.{error.code.value}", error.reference, error.message)

    def validate_mapping(self, value: Mapping[str, Any]):
        self._schema(self._mapping, value, "mapping")
        try:
            return feature_mapping_from_mapping(value)
        except GuidanceError as error:
            _reject(f"feature_guidance.{error.code.value}", error.reference, error.message)


def approved(corpus: Path | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    root = corpus or default_corpus_dir()
    return load_json(root / "approved/record.json"), load_json(root / "approved/mapping.json")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=default_corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        record_value, mapping_value = approved(arguments.corpus)
        validator = FeatureGuidanceContractValidator()
        record = validator.validate_record(record_value)
        mapping = validator.validate_mapping(mapping_value)
    except (ConformanceFailure, OSError, RuntimeError, ValueError) as error:
        diagnostic = error.diagnostic if isinstance(error, ConformanceFailure) else Diagnostic("feature_guidance.internal_error", "feature-guidance", "Feature guidance conformance could not complete.")
        print(json.dumps({"valid": False, "diagnostic": diagnostic.as_dict()}, sort_keys=True))
        return 1
    print(json.dumps({
        "valid": True,
        "guidance_id": record.guidance_id,
        "guidance_version": record.guidance_version,
        "surface_key": mapping.surface_key,
        "condition_key": mapping.condition_key,
        "mapping_version": mapping.mapping_version,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
