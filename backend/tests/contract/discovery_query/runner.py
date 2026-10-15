"""Dependency-light conformance runner for discovery-query v1."""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

SUPPORTED_VERSION = "1.0.0"
MAX_QUERY_TEXT = 100
MAX_QUERY_TERMS = 10


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
        self.diagnostic = Diagnostic(code, reference, message)
        super().__init__(message)


def safe_reference(value: object) -> str:
    return (
        str(value)
        .replace(chr(0), "")
        .replace("\r", " ")
        .replace("\n", " ")[:120]
    )


def reject(code: str, reference: str, message: str) -> None:
    raise ConformanceFailure(code, safe_reference(reference), message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_schema_dir() -> Path:
    return repository_root() / "contracts/learning/discovery/query/v1"


def default_discovery_schema_dir() -> Path:
    return repository_root() / "contracts/learning/discovery/v1"


def default_corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/discovery/query/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject(
            "discovery_query.schema_invalid",
            path.name,
            "Learning-opportunity query value must be an object.",
        )
    return value


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def normalize_query_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split()).casefold()


def canonicalize_request(request: Mapping[str, Any]) -> dict[str, Any]:
    """Project a validated tolerant request into its canonical applied form."""
    return {
        "query": (
            normalize_query_text(request["query"])
            if request["query"] is not None
            else None
        ),
        "prerequisite_query": (
            normalize_query_text(request["prerequisite_query"])
            if request["prerequisite_query"] is not None
            else None
        ),
        "topics": sorted(set(request["topics"])),
        "levels": sorted(set(request["levels"])),
        "kinds": sorted(set(request["kinds"])),
        "availabilities": sorted(set(request["availabilities"])),
        "minimum_minutes": request["minimum_minutes"],
        "maximum_minutes": request["maximum_minutes"],
        "sort": request["sort"],
        "page_size": request["page_size"],
    }


class DiscoveryQueryContractValidator:
    def __init__(self, schema_dir: Path | None = None) -> None:
        root = schema_dir or default_schema_dir()
        self.request_schema = load_json(root / "request.schema.json")
        self.applied_schema = load_json(root / "applied-query.schema.json")
        self.page_schema = load_json(root / "page.schema.json")
        opportunity_schema = load_json(
            default_discovery_schema_dir() / "opportunity.schema.json"
        )
        schemas = (
            self.request_schema,
            self.applied_schema,
            self.page_schema,
            opportunity_schema,
        )
        registry = Registry()
        for schema in schemas:
            Draft202012Validator.check_schema(schema)
            registry = registry.with_resource(
                schema["$id"],
                Resource.from_contents(schema),
            )
        self._request = Draft202012Validator(
            self.request_schema,
            registry=registry,
        )
        self._applied = Draft202012Validator(
            self.applied_schema,
            registry=registry,
        )
        self._page = Draft202012Validator(
            self.page_schema,
            format_checker=FormatChecker(),
            registry=registry,
        )
        self._opportunity = Draft202012Validator(
            opportunity_schema,
            format_checker=FormatChecker(),
            registry=registry,
        )

    @staticmethod
    def _version(value: Mapping[str, Any], reference: str) -> None:
        if value.get("schema_version") != SUPPORTED_VERSION:
            reject(
                "discovery_query.unsupported_version",
                reference,
                "Learning-opportunity query version is unsupported.",
            )

    @staticmethod
    def _shape(validator, value: Mapping[str, Any], reference: str) -> None:
        error = next(iter(validator.iter_errors(value)), None)
        if error is not None:
            location = ".".join(str(part) for part in error.absolute_path)
            reject(
                "discovery_query.schema_invalid",
                location or reference,
                "Learning-opportunity query is malformed.",
            )

    @staticmethod
    def _canonical_filters(value: Mapping[str, Any]) -> None:
        for key in ("topics", "levels", "kinds", "availabilities"):
            if value[key] != sorted(value[key]):
                reject(
                    "discovery_query.noncanonical_filter",
                    key,
                    "Learning-opportunity filters are not canonical.",
                )

    @staticmethod
    def _canonical_text(value: Mapping[str, Any]) -> None:
        for key in ("query", "prerequisite_query"):
            if value[key] is not None and value[key] != normalize_query_text(
                value[key]
            ):
                reject(
                    "discovery_query.noncanonical_text",
                    key,
                    "Learning-opportunity query text is not canonical.",
                )

    @staticmethod
    def _text_bounds(value: Mapping[str, Any]) -> None:
        for key in ("query", "prerequisite_query"):
            raw = value[key]
            if raw is None:
                continue
            normalized = normalize_query_text(raw)
            if (
                not normalized
                or len(normalized) > MAX_QUERY_TEXT
                or len(normalized.split(" ")) > MAX_QUERY_TERMS
            ):
                reject(
                    "discovery_query.schema_invalid",
                    key,
                    "Learning-opportunity query is malformed.",
                )

    @staticmethod
    def _duration(value: Mapping[str, Any]) -> None:
        minimum = value["minimum_minutes"]
        maximum = value["maximum_minutes"]
        if minimum is not None and maximum is not None and minimum > maximum:
            reject(
                "discovery_query.invalid_duration",
                "duration",
                "Learning-opportunity duration range is invalid.",
            )

    def validate_request(self, request: Mapping[str, Any]) -> None:
        self._version(request, "request")
        self._shape(self._request, request, "request")
        self._text_bounds(request)
        self._duration(request)

    def validate_page(self, page: Mapping[str, Any]) -> None:
        self._version(page, "page")
        self._shape(self._page, page, "page")
        applied = page["applied_query"]
        self._shape(self._applied, applied, "applied_query")
        self._canonical_text(applied)
        self._text_bounds(applied)
        self._canonical_filters(applied)
        self._duration(applied)
        records = page["records"]
        for record in records:
            self._validate_opportunity(record)
        identities = [record["opportunity_id"] for record in records]
        if len(identities) != len(set(identities)):
            reject(
                "discovery_query.duplicate_identity",
                "records",
                "Learning-opportunity query identities must be unique.",
            )
        if len(records) > page["total_matches"]:
            reject(
                "discovery_query.count_mismatch",
                "total_matches",
                "Learning-opportunity result count is inconsistent.",
            )
        if any(
            record["projected_at"] != page["projected_at"]
            for record in records
        ):
            reject(
                "discovery_query.projection_mismatch",
                "records",
                "Learning-opportunity result generation is inconsistent.",
            )
        if len(records) > applied["page_size"]:
            reject(
                "discovery_query.page_bound",
                "records",
                "Learning-opportunity result page exceeds its bound.",
            )
        if any(not self._matches(record, applied) for record in records):
            reject(
                "discovery_query.record_mismatch",
                "records",
                "Learning-opportunity result does not match its applied query.",
            )
        expected_order = self._sorted(records, applied["sort"])
        if records != expected_order:
            reject(
                "discovery_query.unstable_order",
                "records",
                "Learning-opportunity query records are not stably ordered.",
            )

    def _validate_opportunity(self, record: Mapping[str, Any]) -> None:
        error = next(iter(self._opportunity.iter_errors(record)), None)
        if error is not None:
            reject(
                "discovery_query.record_invalid",
                "records",
                "Learning-opportunity query record is invalid.",
            )
        if record["kind"] != "lesson" or record["destination"] != (
            f"/learn/placements/{record['placement_id']}"
        ):
            reject(
                "discovery_query.record_invalid",
                "records",
                "Learning-opportunity query record is invalid.",
            )
        if record["topics"] != sorted(record["topics"]):
            reject(
                "discovery_query.record_invalid",
                "records",
                "Learning-opportunity query record is invalid.",
            )
        meaning = {
            key: value
            for key, value in record.items()
            if key not in {"source_fingerprint", "projected_at"}
        }
        expected = hashlib.sha256(canonical_bytes(meaning)).hexdigest()
        if record["source_fingerprint"] != expected:
            reject(
                "discovery_query.record_invalid",
                "records",
                "Learning-opportunity query record is invalid.",
            )

    @staticmethod
    def _matches(
        record: Mapping[str, Any],
        query: Mapping[str, Any],
    ) -> bool:
        searchable = normalize_query_text(
            " ".join(
                (
                    record["title"],
                    record["summary"],
                    *record["objectives"],
                    *record["topics"],
                    record["prerequisite_summary"],
                )
            )
        )
        prerequisite = normalize_query_text(record["prerequisite_summary"])
        if query["query"] is not None and not all(
            term in searchable for term in query["query"].split(" ")
        ):
            return False
        if query["prerequisite_query"] is not None and not all(
            term in prerequisite
            for term in query["prerequisite_query"].split(" ")
        ):
            return False
        return (
            (
                not query["topics"]
                or bool(set(query["topics"]) & set(record["topics"]))
            )
            and (
                not query["levels"] or record["level"] in query["levels"]
            )
            and (not query["kinds"] or record["kind"] in query["kinds"])
            and (
                not query["availabilities"]
                or record["availability"] in query["availabilities"]
            )
            and (
                query["minimum_minutes"] is None
                or record["estimated_minutes"] >= query["minimum_minutes"]
            )
            and (
                query["maximum_minutes"] is None
                or record["estimated_minutes"] <= query["maximum_minutes"]
            )
        )

    @staticmethod
    def _sorted(records: list[Mapping[str, Any]], sort: str):
        if sort == "catalog":
            return records
        if sort == "title":
            key = lambda record: (
                normalize_query_text(record["title"]),
                record["opportunity_id"],
            )
        elif sort == "duration_ascending":
            key = lambda record: (
                record["estimated_minutes"],
                normalize_query_text(record["title"]),
                record["opportunity_id"],
            )
        else:
            key = lambda record: (
                -record["estimated_minutes"],
                normalize_query_text(record["title"]),
                record["opportunity_id"],
            )
        return sorted(records, key=key)


def approved_values(
    corpus: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    root = corpus or default_corpus_dir()
    return (
        load_json(root / "approved/request.json"),
        load_json(root / "approved/page.json"),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=default_corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        request, page = approved_values(arguments.corpus)
        validator = DiscoveryQueryContractValidator()
        validator.validate_request(request)
        validator.validate_page(page)
    except (ConformanceFailure, OSError, RuntimeError, ValueError) as error:
        diagnostic = (
            error.diagnostic
            if isinstance(error, ConformanceFailure)
            else Diagnostic(
                "discovery_query.internal_error",
                "discovery_query",
                "Discovery-query conformance could not complete.",
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
                "query": page["applied_query"]["query"],
                "record_count": len(page["records"]),
                "total_matches": page["total_matches"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
