"""Immutable contextual-help values and exact topic-correlation policy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import StrEnum
import hashlib
import json
import re
from typing import Sequence
import unicodedata

from .models import (
    Applicability,
    GuidanceError,
    GuidanceErrorCode,
    PlatformHelpTopic,
    PublicationFacts,
    SourceArea,
    SourceReference,
)


CONTEXTUAL_HELP_SCHEMA_VERSION = "1.0.0"
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
_VERSION = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)$"
)
_DIGEST = re.compile(r"^[a-f0-9]{64}$")
_ALLOWED_FORMAT_CODEPOINTS = {0x200C, 0x200D}


class ContextPurpose(StrEnum):
    METHOD = "method"
    SOURCE = "source"
    DATA_MEANING = "data_meaning"
    AI_BOUNDARY = "ai_boundary"
    EDUCATION_BOUNDARY = "education_boundary"


@dataclass(frozen=True, slots=True)
class ContextHelpReference:
    topic_id: str
    topic_version: str
    purpose: ContextPurpose
    label: str


@dataclass(frozen=True, slots=True)
class ContextualHelpRecord:
    schema_version: str
    context_key: str
    context_version: str
    feature_label: str
    applicability: tuple[Applicability, ...]
    help_references: tuple[ContextHelpReference, ...]
    publication: PublicationFacts
    source_references: tuple[SourceReference, ...]
    context_digest: str


def _reject(
    code: GuidanceErrorCode,
    reference: str,
    message: str,
) -> None:
    raise GuidanceError(code, message, reference=reference)


def _contains_unsafe_control(value: str) -> bool:
    for character in value:
        category = unicodedata.category(character)
        if category in {"Cc", "Cs", "Co", "Cn"}:
            return True
        if category == "Cf" and ord(character) not in _ALLOWED_FORMAT_CODEPOINTS:
            return True
    return False


def _text(value: object, reference: str, minimum: int, maximum: int) -> str:
    if (
        not isinstance(value, str)
        or not minimum <= len(value) <= maximum
        or _contains_unsafe_control(value)
    ):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Contextual help text is invalid.",
        )
    return value


def _identifier(value: object, reference: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Contextual help identifier is invalid.",
        )
    return value


def _version(value: object, reference: str) -> str:
    if not isinstance(value, str) or _VERSION.fullmatch(value) is None:
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Contextual help version is invalid.",
        )
    return value


def _digest(value: object, reference: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Contextual help digest is invalid.",
        )
    return value


def _utc_text(value: datetime, reference: str) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None:
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Contextual help timestamp is invalid.",
        )
    try:
        result = value.astimezone(timezone.utc).isoformat()
    except (OverflowError, ValueError):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Contextual help timestamp is invalid.",
        )
    return result.removesuffix("+00:00") + "Z"


def context_payload(record: ContextualHelpRecord) -> dict[str, object]:
    return {
        "schema_version": record.schema_version,
        "context_key": record.context_key,
        "context_version": record.context_version,
        "feature_label": record.feature_label,
        "applicability": [
            {"scope_key": item.scope_key, "label": item.label}
            for item in record.applicability
        ],
        "help_references": [
            {
                "topic_id": item.topic_id,
                "topic_version": item.topic_version,
                "purpose": item.purpose.value,
                "label": item.label,
            }
            for item in record.help_references
        ],
        "publication": {
            "state": record.publication.state,
            "reviewed_on": record.publication.reviewed_on.isoformat(),
            "updated_at": _utc_text(
                record.publication.updated_at,
                "publication.updated_at",
            ),
        },
        "source_references": [
            {
                "source_key": item.source_key,
                "title": item.title,
                "area": item.area.value,
                "source_version": item.source_version,
                "content_fingerprint": item.content_fingerprint,
            }
            for item in record.source_references
        ],
        "context_digest": record.context_digest,
    }


def canonical_context_bytes(record: ContextualHelpRecord) -> bytes:
    value = context_payload(record)
    value.pop("context_digest")
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def context_digest(record: ContextualHelpRecord) -> str:
    return hashlib.sha256(canonical_context_bytes(record)).hexdigest()


def validate_context(record: ContextualHelpRecord) -> ContextualHelpRecord:
    if not isinstance(record, ContextualHelpRecord):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            "context",
            "Contextual help record is invalid.",
        )
    if record.schema_version != CONTEXTUAL_HELP_SCHEMA_VERSION:
        _reject(
            GuidanceErrorCode.UNSUPPORTED_VERSION,
            "schema_version",
            "Contextual help contract version is unsupported.",
        )
    _identifier(record.context_key, "context_key")
    _version(record.context_version, "context_version")
    _text(record.feature_label, "feature_label", 1, 160)
    if (
        not isinstance(record.applicability, tuple)
        or not 1 <= len(record.applicability) <= 20
    ):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            "applicability",
            "Context applicability is invalid.",
        )
    applicability_keys: list[str] = []
    for index, item in enumerate(record.applicability):
        if not isinstance(item, Applicability):
            _reject(
                GuidanceErrorCode.INVALID_RECORD,
                "applicability",
                "Context applicability is invalid.",
            )
        applicability_keys.append(
            _identifier(item.scope_key, f"applicability.{index}.scope_key")
        )
        _text(item.label, f"applicability.{index}.label", 1, 160)
    if len(applicability_keys) != len(set(applicability_keys)):
        _reject(
            GuidanceErrorCode.DUPLICATE_IDENTITY,
            "applicability",
            "Context applicability repeats.",
        )
    if (
        not isinstance(record.help_references, tuple)
        or not 1 <= len(record.help_references) <= 10
    ):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            "help_references",
            "Contextual help references are invalid.",
        )
    reference_keys: list[tuple[str, str]] = []
    purposes: list[ContextPurpose] = []
    for index, item in enumerate(record.help_references):
        if not isinstance(item, ContextHelpReference) or not isinstance(
            item.purpose,
            ContextPurpose,
        ):
            _reject(
                GuidanceErrorCode.INVALID_RECORD,
                "help_references",
                "Contextual help reference is invalid.",
            )
        reference_keys.append(
            (
                _identifier(item.topic_id, f"help_references.{index}.topic_id"),
                _version(
                    item.topic_version,
                    f"help_references.{index}.topic_version",
                ),
            )
        )
        purposes.append(item.purpose)
        _text(item.label, f"help_references.{index}.label", 1, 160)
    if len(reference_keys) != len(set(reference_keys)) or len(purposes) != len(
        set(purposes)
    ):
        _reject(
            GuidanceErrorCode.DUPLICATE_IDENTITY,
            "help_references",
            "Contextual help references repeat.",
        )
    if not isinstance(record.publication, PublicationFacts):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            "publication",
            "Context publication facts are invalid.",
        )
    if record.publication.state != "approved" or type(
        record.publication.reviewed_on
    ) is not date:
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            "publication",
            "Context publication facts are invalid.",
        )
    updated = _utc_text(record.publication.updated_at, "publication.updated_at")
    if record.publication.reviewed_on > date.fromisoformat(updated[:10]):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            "publication",
            "Context publication chronology is invalid.",
        )
    if (
        not isinstance(record.source_references, tuple)
        or not 1 <= len(record.source_references) <= 20
    ):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            "source_references",
            "Context source references are invalid.",
        )
    source_keys: list[str] = []
    for index, source in enumerate(record.source_references):
        if not isinstance(source, SourceReference) or not isinstance(
            source.area,
            SourceArea,
        ):
            _reject(
                GuidanceErrorCode.INVALID_RECORD,
                "source_references",
                "Context source reference is invalid.",
            )
        source_keys.append(
            _identifier(source.source_key, f"source_references.{index}.source_key")
        )
        _text(source.title, f"source_references.{index}.title", 1, 200)
        _text(
            source.source_version,
            f"source_references.{index}.source_version",
            1,
            80,
        )
        _digest(
            source.content_fingerprint,
            f"source_references.{index}.content_fingerprint",
        )
    if len(source_keys) != len(set(source_keys)):
        _reject(
            GuidanceErrorCode.DUPLICATE_IDENTITY,
            "source_references",
            "Context source references repeat.",
        )
    _digest(record.context_digest, "context_digest")
    if record.context_digest != context_digest(record):
        _reject(
            GuidanceErrorCode.DIGEST_MISMATCH,
            "context_digest",
            "Contextual help digest does not match.",
        )
    return record


def context_registry_digest(records: Sequence[ContextualHelpRecord]) -> str:
    ordered = sorted(
        (context_payload(record) for record in records),
        key=lambda value: (value["context_key"], value["context_version"]),
    )
    return hashlib.sha256(
        json.dumps(
            ordered,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


class ContextualHelpRegistry:
    """Validated immutable exact contexts correlated to admitted Help topics."""

    def __init__(
        self,
        records: Sequence[ContextualHelpRecord],
        topics: Sequence[PlatformHelpTopic],
    ) -> None:
        if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
            _reject(
                GuidanceErrorCode.INVALID_RECORD,
                "context-registry",
                "Contextual help registry is invalid.",
            )
        admitted = tuple(validate_context(record) for record in records)
        if not admitted:
            _reject(
                GuidanceErrorCode.INVALID_RECORD,
                "context-registry",
                "Contextual help registry is empty.",
            )
        keys = [(record.context_key, record.context_version) for record in admitted]
        if len(keys) != len(set(keys)):
            _reject(
                GuidanceErrorCode.DUPLICATE_IDENTITY,
                "context-registry",
                "Contextual help identity repeats.",
            )
        topic_keys = {(topic.topic_id, topic.topic_version) for topic in topics}
        for record in admitted:
            for reference in record.help_references:
                if (reference.topic_id, reference.topic_version) not in topic_keys:
                    _reject(
                        GuidanceErrorCode.DANGLING_REFERENCE,
                        f"{record.context_key}@{record.context_version}",
                        "Contextual help topic is unavailable.",
                    )
        self._records = tuple(
            sorted(
                admitted,
                key=lambda item: (item.context_key, item.context_version),
            )
        )
        self._by_key = {
            (record.context_key, record.context_version): record
            for record in self._records
        }
        self._digest = context_registry_digest(self._records)

    @property
    def records(self) -> tuple[ContextualHelpRecord, ...]:
        return self._records

    @property
    def digest(self) -> str:
        return self._digest

    def get(self, context_key: str, context_version: str) -> ContextualHelpRecord:
        _identifier(context_key, "context_key")
        _version(context_version, "context_version")
        try:
            return self._by_key[(context_key, context_version)]
        except KeyError:
            _reject(
                GuidanceErrorCode.NOT_FOUND,
                f"{context_key}@{context_version}",
                "Contextual help is unavailable.",
            )


__all__ = [
    "CONTEXTUAL_HELP_SCHEMA_VERSION",
    "ContextHelpReference",
    "ContextPurpose",
    "ContextualHelpRecord",
    "ContextualHelpRegistry",
    "canonical_context_bytes",
    "context_digest",
    "context_payload",
    "context_registry_digest",
    "validate_context",
]
