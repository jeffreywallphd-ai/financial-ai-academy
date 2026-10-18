"""Dependency-light conformance runner for cross-domain provenance v2."""

from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, Sequence
import unicodedata

from jsonschema import Draft202012Validator, FormatChecker


TIME_FIELDS = frozenset(
    {"recorded_at", "observed_at", "as_of", "decision_at", "action_at"}
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
    return repository_root() / "contracts/provenance/v2"


def default_corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/provenance/v2"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject("provenance_v2.schema_invalid", path.name, "Record must be an object.")
    return value


def _utc_timestamp(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        reject("provenance_v2.schema_invalid", "timestamp", "Timestamp must be aware.")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalized(value: object, *, field: str | None = None) -> object:
    if field in TIME_FIELDS and isinstance(value, str):
        return _utc_timestamp(value)
    if isinstance(value, Mapping):
        normalized = {
            str(key): _normalized(item, field=str(key))
            for key, item in value.items()
        }
        if "sources" in normalized and isinstance(normalized["sources"], list):
            normalized["sources"] = sorted(
                normalized["sources"], key=lambda item: canonical_bytes(item)
            )
        return normalized
    if isinstance(value, list):
        return [_normalized(item) for item in value]
    return value


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_digest(value: object) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def _identifier_is_safe(value: object) -> bool:
    if not isinstance(value, str) or not value or len(value) > 128:
        return False
    if not value[0].isalnum():
        return False
    return all(
        not character.isspace()
        and not unicodedata.category(character).startswith("C")
        and character not in "/\\?#"
        for character in value
    )


def approved_records(corpus: Path | None = None) -> dict[str, dict[str, Any]]:
    root = (corpus or default_corpus_dir()) / "approved"
    records: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("*-envelope.json")):
        record = load_json(path)
        profile = str(record.get("resource", {}).get("profile", ""))
        if not profile or profile in records:
            reject("provenance_v2.catalog_invalid", path.name, "Approved profile is invalid.")
        records[profile] = record
    return records


def current_v1_fingerprints(root: Path | None = None) -> dict[str, str]:
    repository = root or repository_root()
    paths = sorted((repository / "contracts/provenance/v1").glob("*.schema.json"))
    paths += sorted(
        (repository / "contracts/compatibility/provenance/v1/approved").glob("*.json")
    )
    return {
        path.relative_to(repository).as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in paths
    }


class CrossDomainContractValidator:
    def __init__(self, schema_dir: Path | None = None) -> None:
        root = schema_dir or default_schema_dir()
        self.envelope_schema = load_json(root / "envelope.schema.json")
        self.catalog_schema = load_json(root / "profile-catalog.schema.json")
        self.catalog = load_json(root / "profile-catalog.json")
        Draft202012Validator.check_schema(self.envelope_schema)
        Draft202012Validator.check_schema(self.catalog_schema)
        self.envelope_validator = Draft202012Validator(
            self.envelope_schema, format_checker=FormatChecker()
        )
        self.catalog_validator = Draft202012Validator(self.catalog_schema)
        catalog_error = next(iter(self.catalog_validator.iter_errors(self.catalog)), None)
        if catalog_error is not None:
            reject(
                "provenance_v2.catalog_invalid",
                "catalog",
                "Profile catalog is malformed.",
            )
        profiles = self.catalog["profiles"]
        self.profiles = {str(item["profile"]): item for item in profiles}
        if len(self.profiles) != len(profiles):
            reject(
                "provenance_v2.catalog_invalid",
                "profiles",
                "Profile catalog contains duplicates.",
            )
        for profile_id, profile in self.profiles.items():
            variants = profile["identity_variants"]
            variant_ids = {str(variant["variant_id"]) for variant in variants}
            if len(variant_ids) != len(variants):
                reject(
                    "provenance_v2.catalog_invalid",
                    profile_id,
                    "Profile catalog contains duplicate identity variants.",
                )
            for variant in variants:
                resource_id_field = variant.get("resource_id_field")
                if (
                    variant["resource_id_strategy"] == "field"
                    and resource_id_field not in variant["identity_fields"]
                ):
                    reject(
                        "provenance_v2.catalog_invalid",
                        profile_id,
                        "Profile catalog identity variant is malformed.",
                    )

    def validate_corpus(
        self, records: Mapping[str, Mapping[str, Any]]
    ) -> None:
        expected = set(self.profiles)
        actual = set(records)
        if actual != expected:
            reject(
                "provenance_v2.corpus_incomplete",
                "approved",
                "Approved corpus does not exactly cover the closed profile catalog.",
            )

    def _shape(self, value: Mapping[str, Any]) -> None:
        error = next(iter(self.envelope_validator.iter_errors(value)), None)
        if error is not None:
            location = ".".join(str(part) for part in error.absolute_path)
            reject(
                "provenance_v2.schema_invalid",
                location or "envelope",
                "Cross-domain provenance record is malformed.",
            )

    def _resource(self, value: Mapping[str, Any], reference: str) -> None:
        profile_id = str(value["profile"])
        profile = self.profiles.get(profile_id)
        if profile is None:
            reject(
                "provenance_v2.profile_invalid",
                reference,
                "Cross-domain provenance profile is unsupported.",
            )
        if (
            value["owner_module"] != profile["owner_module"]
            or value["resource_kind"] != profile["resource_kind"]
            or value["provenance_label"] not in profile["allowed_provenance_labels"]
        ):
            reject(
                "provenance_v2.profile_invalid",
                reference,
                "Cross-domain provenance profile is inconsistent.",
            )
        identity = value["identity"]
        variants = [
            variant
            for variant in profile["identity_variants"]
            if set(identity) == set(variant["identity_fields"])
        ]
        if len(variants) != 1:
            reject(
                "provenance_v2.identity_invalid",
                reference,
                "Cross-domain provenance identity is inconsistent.",
            )
        variant = variants[0]
        variant_id = str(variant["variant_id"])
        if variant_id != "default" and identity.get("subject_kind") != variant_id:
            reject(
                "provenance_v2.identity_invalid",
                reference,
                "Cross-domain provenance identity is inconsistent.",
            )
        expected_resource_id = (
            identity[variant["resource_id_field"]]
            if variant["resource_id_strategy"] == "field"
            else canonical_digest(_normalized(identity))
        )
        if value["resource_id"] != expected_resource_id:
            reject(
                "provenance_v2.identity_invalid",
                reference,
                "Cross-domain provenance identity is inconsistent.",
            )
        identifiers = [value["resource_id"]]
        identifiers.extend(
            item for key, item in identity.items() if key.endswith("_id")
        )
        if not all(_identifier_is_safe(item) for item in identifiers):
            reject(
                "provenance_v2.identity_invalid",
                reference,
                "Cross-domain provenance identity is inconsistent.",
            )

    def validate_envelope(self, value: Mapping[str, Any]) -> dict[str, Any]:
        self._shape(value)
        if not _identifier_is_safe(value["producer"]["producer_id"]):
            reject(
                "provenance_v2.identity_invalid",
                "producer.producer_id",
                "Cross-domain provenance producer is inconsistent.",
            )
        resource = value["resource"]
        self._resource(resource, "resource")
        allowed_relations = set(self.profiles[resource["profile"]]["allowed_source_relations"])
        seen: dict[bytes, bytes] = {
            canonical_bytes(
                {
                    "profile": resource["profile"],
                    "identity": _normalized(resource["identity"]),
                }
            ): canonical_bytes(_normalized(resource))
        }
        for index, source in enumerate(value["sources"]):
            if source["relation"] not in allowed_relations:
                reject(
                    "provenance_v2.relation_invalid",
                    f"sources.{index}.relation",
                    "Cross-domain provenance relation is not allowed for this profile.",
                )
            reference = source["reference"]
            self._resource(reference, f"sources.{index}.reference")
            key = canonical_bytes(
                {
                    "profile": reference["profile"],
                    "identity": _normalized(reference["identity"]),
                }
            )
            meaning = canonical_bytes(_normalized(reference))
            if key in seen:
                code = (
                    "provenance_v2.identity_conflict"
                    if seen[key] != meaning
                    else "provenance_v2.duplicate_reference"
                )
                reject(code, f"sources.{index}", "Cross-domain provenance source is duplicated.")
            seen[key] = meaning
        return copy.deepcopy(_normalized(value))

    def envelope_digest(self, value: Mapping[str, Any]) -> str:
        return canonical_digest(self.validate_envelope(value))

    def catalog_digest(self) -> str:
        return canonical_digest(self.catalog)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=default_corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        validator = CrossDomainContractValidator()
        records = approved_records(arguments.corpus)
        validator.validate_corpus(records)
        digests = {
            profile: validator.envelope_digest(record)
            for profile, record in sorted(records.items())
        }
    except (ConformanceFailure, OSError, RuntimeError, TypeError, ValueError) as error:
        diagnostic = (
            error.diagnostic
            if isinstance(error, ConformanceFailure)
            else Diagnostic(
                "provenance_v2.internal_error",
                "provenance_v2",
                "Cross-domain provenance conformance could not complete.",
            )
        )
        print(json.dumps({"valid": False, "diagnostic": diagnostic.as_dict()}, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "profile_count": len(records),
                "catalog_digest": validator.catalog_digest(),
                "envelope_digests": digests,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
