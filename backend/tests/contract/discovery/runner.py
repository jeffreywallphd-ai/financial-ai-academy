"""Dependency-light conformance runner for learning discovery v1."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


SUPPORTED_VERSION = "1.0.0"


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
    return repository_root() / "contracts/learning/discovery/v1"


def default_corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/discovery/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject("discovery.schema_invalid", path.name, "Record must be an object.")
    return value


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def source_meaning(opportunity: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: opportunity[key]
        for key in opportunity
        if key not in {"source_fingerprint", "projected_at"}
    }


def source_fingerprint(opportunity: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(source_meaning(opportunity))).hexdigest()


def stable_record(opportunity: Mapping[str, Any]) -> dict[str, Any]:
    return {
        **source_meaning(opportunity),
        "source_fingerprint": opportunity["source_fingerprint"],
    }


def projection_generation(records: Sequence[Mapping[str, Any]]) -> str:
    return hashlib.sha256(
        canonical_bytes([stable_record(record) for record in records])
    ).hexdigest()


class DiscoveryContractValidator:
    def __init__(self, schema_dir: Path | None = None) -> None:
        root = schema_dir or default_schema_dir()
        self.opportunity_schema = load_json(root / "opportunity.schema.json")
        self.browse_schema = load_json(root / "browse.schema.json")
        Draft202012Validator.check_schema(self.opportunity_schema)
        Draft202012Validator.check_schema(self.browse_schema)
        registry = Registry().with_resource(
            self.opportunity_schema["$id"],
            Resource.from_contents(self.opportunity_schema),
        )
        self._opportunity = Draft202012Validator(
            self.opportunity_schema,
            format_checker=FormatChecker(),
            registry=registry,
        )
        self._browse = Draft202012Validator(
            self.browse_schema,
            format_checker=FormatChecker(),
            registry=registry,
        )

    @staticmethod
    def _version(value: Mapping[str, Any], reference: str) -> None:
        if value.get("schema_version") != SUPPORTED_VERSION:
            reject(
                "discovery.unsupported_version",
                reference,
                "Learning-discovery contract version is unsupported.",
            )

    @staticmethod
    def _shape(validator, value: Mapping[str, Any], reference: str) -> None:
        error = next(iter(validator.iter_errors(value)), None)
        if error is not None:
            location = ".".join(str(part) for part in error.absolute_path)
            reject(
                "discovery.schema_invalid",
                location or reference,
                "Learning-discovery record is malformed.",
            )

    def validate_opportunity(self, opportunity: Mapping[str, Any]) -> None:
        self._version(opportunity, "opportunity")
        self._shape(self._opportunity, opportunity, "opportunity")
        if opportunity["kind"] != "lesson":
            reject(
                "discovery.unsupported_kind",
                "kind",
                "This discovery profile supports approved lessons only.",
            )
        if opportunity["destination"] != (
            f"/learn/placements/{opportunity['placement_id']}"
        ):
            reject(
                "discovery.destination_mismatch",
                "destination",
                "Learning destination does not match its exact placement.",
            )
        if list(opportunity["topics"]) != sorted(opportunity["topics"]):
            reject(
                "discovery.unstable_topics",
                "topics",
                "Learning-opportunity topics are not stably ordered.",
            )
        if opportunity["source_fingerprint"] != source_fingerprint(opportunity):
            reject(
                "discovery.source_fingerprint_mismatch",
                "source_fingerprint",
                "Learning-opportunity source fingerprint does not match.",
            )

    def validate_browse(self, browse: Mapping[str, Any]) -> None:
        self._version(browse, "browse")
        self._shape(self._browse, browse, "browse")
        records = browse["records"]
        for record in records:
            self.validate_opportunity(record)
        identities = [record["opportunity_id"] for record in records]
        if len(identities) != len(set(identities)):
            reject(
                "discovery.duplicate_identity",
                "records",
                "Learning-opportunity identities must be unique.",
            )
        order = [
            (record["title"].casefold(), record["opportunity_id"])
            for record in records
        ]
        if order != sorted(order):
            reject(
                "discovery.unstable_order",
                "records",
                "Learning opportunities are not stably ordered.",
            )
        if browse["projection_generation"] != projection_generation(records):
            reject(
                "discovery.generation_mismatch",
                "projection_generation",
                "Learning-opportunity projection generation does not match.",
            )


def approved_records(
    corpus: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    root = corpus or default_corpus_dir()
    return (
        load_json(root / "approved/opportunity.json"),
        load_json(root / "approved/browse.json"),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=default_corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        opportunity, browse = approved_records(arguments.corpus)
        validator = DiscoveryContractValidator()
        validator.validate_opportunity(opportunity)
        validator.validate_browse(browse)
    except (ConformanceFailure, OSError, RuntimeError, ValueError) as error:
        diagnostic = (
            error.diagnostic
            if isinstance(error, ConformanceFailure)
            else Diagnostic(
                "discovery.internal_error",
                "discovery",
                "Discovery conformance could not complete.",
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
                "opportunity_id": opportunity["opportunity_id"],
                "source_fingerprint": opportunity["source_fingerprint"],
                "projection_generation": browse["projection_generation"],
                "record_count": len(browse["records"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
