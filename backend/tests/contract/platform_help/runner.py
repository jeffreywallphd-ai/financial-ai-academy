"""Dependency-light conformance runner for platform-help v1."""

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
    search_page_payload,
    search_request_from_mapping,
    topic_from_mapping,
)
from financial_ai_academy.modules.guidance.domain import (
    GuidanceError,
    PlatformHelpCorpus,
)


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


def default_schema_dir() -> Path:
    return repository_root() / "contracts/guidance/platform-help/v1"


def default_corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/platform-help/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject("platform_help.schema_invalid", path.name, "Record must be an object.")
    return value


class PlatformHelpContractValidator:
    def __init__(self, schema_dir: Path | None = None) -> None:
        root = schema_dir or default_schema_dir()
        self.schemas = {
            "topic": load_json(root / "topic.schema.json"),
            "search_request": load_json(root / "search-request.schema.json"),
            "search_page": load_json(root / "search-page.schema.json"),
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
                "platform_help.schema_invalid",
                location or name,
                "Platform help record is malformed.",
            )

    def validate_topic(self, value: Mapping[str, Any]):
        self._shape("topic", value)
        try:
            return topic_from_mapping(value)
        except GuidanceError as error:
            reject(
                f"platform_help.{error.code.value}",
                error.reference,
                error.message,
            )

    def validate_search_request(self, value: Mapping[str, Any]):
        self._shape("search_request", value)
        try:
            return search_request_from_mapping(value)
        except GuidanceError as error:
            reject(
                f"platform_help.{error.code.value}",
                error.reference,
                error.message,
            )

    def validate_search_page(
        self,
        value: Mapping[str, Any],
        *,
        topic: Mapping[str, Any],
        request: Mapping[str, Any],
    ) -> None:
        self._shape("search_page", value)
        admitted_topic = self.validate_topic(topic)
        admitted_request = self.validate_search_request(request)
        expected = search_page_payload(
            PlatformHelpCorpus((admitted_topic,)).search(admitted_request)
        )
        if value != expected:
            reject(
                "platform_help.search_page_mismatch",
                "search_page",
                "Platform help search page does not match deterministic results.",
            )


def approved_records(
    corpus: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = corpus or default_corpus_dir()
    return (
        load_json(root / "approved/topic.json"),
        load_json(root / "approved/search-request.json"),
        load_json(root / "approved/search-page.json"),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=default_corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        topic, request, page = approved_records(arguments.corpus)
        validator = PlatformHelpContractValidator()
        admitted = validator.validate_topic(topic)
        validator.validate_search_request(request)
        validator.validate_search_page(page, topic=topic, request=request)
    except (ConformanceFailure, OSError, RuntimeError, ValueError) as error:
        diagnostic = (
            error.diagnostic
            if isinstance(error, ConformanceFailure)
            else Diagnostic(
                "platform_help.internal_error",
                "platform-help",
                "Platform help conformance could not complete.",
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
                "topic_id": admitted.topic_id,
                "topic_version": admitted.topic_version,
                "topic_digest": admitted.topic_digest,
                "corpus_digest": page["corpus_digest"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
