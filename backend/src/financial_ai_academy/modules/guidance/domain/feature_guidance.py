"""Immutable feature-guidance records, mappings, and exact lookup policy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import StrEnum
import hashlib
import json
import re
from typing import Mapping, Sequence
import unicodedata

from .contextual_help import ContextHelpReference, ContextPurpose
from .models import (
    Applicability,
    GuidanceError,
    GuidanceErrorCode,
    PlatformHelpTopic,
    PublicationFacts,
    SourceArea,
    SourceReference,
)


FEATURE_GUIDANCE_SCHEMA_VERSION = "1.0.0"
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
_VERSION = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_DIGEST = re.compile(r"^[a-f0-9]{64}$")
_UNSAFE_INSTRUCTION = re.compile(
    r"(?:https?://|file://|[a-zA-Z]:\\|(?:^|\s)(?:docker|kubectl|powershell|cmd|bash|git|npm|pnpm|yarn|pip|python)\s)",
    re.IGNORECASE,
)
_UNSAFE_GUARANTEE = re.compile(
    r"\b(?:guaranteed|always succeeds|will succeed|cannot fail|fully recovers)\b",
    re.IGNORECASE,
)
_ALLOWED_FORMAT_CODEPOINTS = {0x200C, 0x200D}


class FeatureGuidanceStatus(StrEnum):
    LIMITED = "limited"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"


class FeatureGuidanceActionKind(StrEnum):
    RETRY_UNCHANGED_REQUEST = "retry_unchanged_request"
    RELOAD_CURRENT_STATE = "reload_current_state"
    RETURN_TO_OWNING_TASK = "return_to_owning_task"
    OPEN_HELP_TOPIC = "open_help_topic"
    DOWNLOAD_INERT_ARTIFACT = "download_inert_artifact"


@dataclass(frozen=True, slots=True)
class FeatureGuidanceAction:
    action_kind: FeatureGuidanceActionKind
    label: str
    topic_id: str | None = None
    topic_version: str | None = None


@dataclass(frozen=True, slots=True)
class FeatureGuidanceRecord:
    schema_version: str
    guidance_id: str
    guidance_version: str
    status: FeatureGuidanceStatus
    heading: str
    reason: str
    outcome: str
    actions: tuple[FeatureGuidanceAction, ...]
    help_references: tuple[ContextHelpReference, ...]
    applicability: tuple[Applicability, ...]
    publication: PublicationFacts
    source_references: tuple[SourceReference, ...]
    guidance_digest: str


@dataclass(frozen=True, slots=True)
class FeatureGuidanceMapping:
    schema_version: str
    surface_key: str
    condition_key: str
    mapping_version: str
    guidance_id: str
    guidance_version: str
    publication: PublicationFacts
    source_references: tuple[SourceReference, ...]
    mapping_digest: str


def _reject(code: GuidanceErrorCode, reference: str, message: str) -> None:
    raise GuidanceError(code, message, reference=reference)


def _contains_unsafe_control(value: str) -> bool:
    return any(
        unicodedata.category(character) in {"Cc", "Cs", "Co", "Cn"}
        or (
            unicodedata.category(character) == "Cf"
            and ord(character) not in _ALLOWED_FORMAT_CODEPOINTS
        )
        for character in value
    )


def _plain_text(value: object, reference: str, minimum: int, maximum: int) -> str:
    if (
        not isinstance(value, str)
        or not minimum <= len(value) <= maximum
        or _contains_unsafe_control(value)
    ):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Feature guidance text is invalid.",
        )
    return value


def _text(value: object, reference: str, minimum: int, maximum: int) -> str:
    admitted = _plain_text(value, reference, minimum, maximum)
    if _UNSAFE_INSTRUCTION.search(admitted) or _UNSAFE_GUARANTEE.search(admitted):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Feature guidance text is invalid.",
        )
    return admitted


def _identifier(value: object, reference: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        _reject(GuidanceErrorCode.INVALID_RECORD, reference, "Feature guidance identifier is invalid.")
    return value


def _version(value: object, reference: str) -> str:
    if not isinstance(value, str) or _VERSION.fullmatch(value) is None:
        _reject(GuidanceErrorCode.INVALID_RECORD, reference, "Feature guidance version is invalid.")
    return value


def _digest(value: object, reference: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        _reject(GuidanceErrorCode.INVALID_RECORD, reference, "Feature guidance digest is invalid.")
    return value


def _utc_text(value: datetime, reference: str) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None:
        _reject(GuidanceErrorCode.INVALID_RECORD, reference, "Feature guidance timestamp is invalid.")
    try:
        result = value.astimezone(timezone.utc).isoformat()
    except (OverflowError, ValueError):
        _reject(GuidanceErrorCode.INVALID_RECORD, reference, "Feature guidance timestamp is invalid.")
    return result.removesuffix("+00:00") + "Z"


def _publication_payload(value: PublicationFacts) -> dict[str, str]:
    return {
        "state": value.state,
        "reviewed_on": value.reviewed_on.isoformat(),
        "updated_at": _utc_text(value.updated_at, "publication.updated_at"),
    }


def _source_payload(value: SourceReference) -> dict[str, str]:
    return {
        "source_key": value.source_key,
        "title": value.title,
        "area": value.area.value,
        "source_version": value.source_version,
        "content_fingerprint": value.content_fingerprint,
    }


def feature_guidance_payload(record: FeatureGuidanceRecord) -> dict[str, object]:
    return {
        "schema_version": record.schema_version,
        "guidance_id": record.guidance_id,
        "guidance_version": record.guidance_version,
        "status": record.status.value,
        "heading": record.heading,
        "reason": record.reason,
        "outcome": record.outcome,
        "actions": [
            {
                "action_kind": action.action_kind.value,
                "label": action.label,
                **(
                    {
                        "topic_id": action.topic_id,
                        "topic_version": action.topic_version,
                    }
                    if action.topic_id is not None
                    else {}
                ),
            }
            for action in record.actions
        ],
        "help_references": [
            {
                "topic_id": reference.topic_id,
                "topic_version": reference.topic_version,
                "purpose": reference.purpose.value,
                "label": reference.label,
            }
            for reference in record.help_references
        ],
        "applicability": [
            {"scope_key": item.scope_key, "label": item.label}
            for item in record.applicability
        ],
        "publication": _publication_payload(record.publication),
        "source_references": [_source_payload(item) for item in record.source_references],
        "guidance_digest": record.guidance_digest,
    }


def feature_mapping_payload(mapping: FeatureGuidanceMapping) -> dict[str, object]:
    return {
        "schema_version": mapping.schema_version,
        "surface_key": mapping.surface_key,
        "condition_key": mapping.condition_key,
        "mapping_version": mapping.mapping_version,
        "guidance_id": mapping.guidance_id,
        "guidance_version": mapping.guidance_version,
        "publication": _publication_payload(mapping.publication),
        "source_references": [_source_payload(item) for item in mapping.source_references],
        "mapping_digest": mapping.mapping_digest,
    }


def _canonical(value: dict[str, object], digest_field: str) -> bytes:
    value = dict(value)
    value.pop(digest_field)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def feature_guidance_digest(record: FeatureGuidanceRecord) -> str:
    return hashlib.sha256(
        _canonical(feature_guidance_payload(record), "guidance_digest")
    ).hexdigest()


def feature_mapping_digest(mapping: FeatureGuidanceMapping) -> str:
    return hashlib.sha256(
        _canonical(feature_mapping_payload(mapping), "mapping_digest")
    ).hexdigest()


def _validate_publication(value: object) -> None:
    if not isinstance(value, PublicationFacts) or value.state != "approved" or type(value.reviewed_on) is not date:
        _reject(GuidanceErrorCode.INVALID_RECORD, "publication", "Feature guidance publication facts are invalid.")
    updated = _utc_text(value.updated_at, "publication.updated_at")
    if value.reviewed_on > date.fromisoformat(updated[:10]):
        _reject(GuidanceErrorCode.INVALID_RECORD, "publication", "Feature guidance publication chronology is invalid.")


def _validate_sources(
    values: object,
    source_fingerprints: Mapping[str, str] | None = None,
) -> None:
    if not isinstance(values, tuple) or not 1 <= len(values) <= 20:
        _reject(GuidanceErrorCode.INVALID_RECORD, "source_references", "Feature guidance source references are invalid.")
    keys: list[str] = []
    for index, source in enumerate(values):
        if not isinstance(source, SourceReference) or not isinstance(source.area, SourceArea):
            _reject(GuidanceErrorCode.INVALID_RECORD, "source_references", "Feature guidance source reference is invalid.")
        key = _identifier(source.source_key, f"source_references.{index}.source_key")
        keys.append(key)
        _plain_text(source.title, f"source_references.{index}.title", 1, 200)
        _plain_text(source.source_version, f"source_references.{index}.source_version", 1, 80)
        fingerprint = _digest(source.content_fingerprint, f"source_references.{index}.content_fingerprint")
        if source_fingerprints is not None and source_fingerprints.get(key) != fingerprint:
            _reject(GuidanceErrorCode.DIGEST_MISMATCH, key, "Feature guidance source binding is stale.")
    if len(keys) != len(set(keys)):
        _reject(GuidanceErrorCode.DUPLICATE_IDENTITY, "source_references", "Feature guidance source references repeat.")


def validate_feature_guidance(record: FeatureGuidanceRecord) -> FeatureGuidanceRecord:
    if not isinstance(record, FeatureGuidanceRecord):
        _reject(GuidanceErrorCode.INVALID_RECORD, "guidance", "Feature guidance record is invalid.")
    if record.schema_version != FEATURE_GUIDANCE_SCHEMA_VERSION:
        _reject(GuidanceErrorCode.UNSUPPORTED_VERSION, "schema_version", "Feature guidance contract version is unsupported.")
    _identifier(record.guidance_id, "guidance_id")
    _version(record.guidance_version, "guidance_version")
    if not isinstance(record.status, FeatureGuidanceStatus):
        _reject(GuidanceErrorCode.INVALID_RECORD, "status", "Feature guidance status is invalid.")
    _text(record.heading, "heading", 1, 120)
    _text(record.reason, "reason", 1, 500)
    _text(record.outcome, "outcome", 1, 500)
    if not isinstance(record.actions, tuple) or len(record.actions) > 5:
        _reject(GuidanceErrorCode.INVALID_RECORD, "actions", "Feature guidance actions are invalid.")
    action_keys: list[tuple[object, object, object]] = []
    for index, action in enumerate(record.actions):
        if not isinstance(action, FeatureGuidanceAction) or not isinstance(action.action_kind, FeatureGuidanceActionKind):
            _reject(GuidanceErrorCode.INVALID_RECORD, "actions", "Feature guidance action is invalid.")
        _text(action.label, f"actions.{index}.label", 1, 120)
        if action.action_kind is FeatureGuidanceActionKind.OPEN_HELP_TOPIC:
            _identifier(action.topic_id, f"actions.{index}.topic_id")
            _version(action.topic_version, f"actions.{index}.topic_version")
        elif action.topic_id is not None or action.topic_version is not None:
            _reject(GuidanceErrorCode.INVALID_RECORD, f"actions.{index}", "Feature guidance action target is invalid.")
        action_keys.append((action.action_kind, action.topic_id, action.topic_version))
    if len(action_keys) != len(set(action_keys)):
        _reject(GuidanceErrorCode.DUPLICATE_IDENTITY, "actions", "Feature guidance actions repeat.")
    if not isinstance(record.help_references, tuple) or not 1 <= len(record.help_references) <= 10:
        _reject(GuidanceErrorCode.INVALID_RECORD, "help_references", "Feature guidance help references are invalid.")
    help_keys: list[tuple[str, str]] = []
    purposes: list[ContextPurpose] = []
    for index, reference in enumerate(record.help_references):
        if not isinstance(reference, ContextHelpReference) or not isinstance(reference.purpose, ContextPurpose):
            _reject(GuidanceErrorCode.INVALID_RECORD, "help_references", "Feature guidance help reference is invalid.")
        help_keys.append((
            _identifier(reference.topic_id, f"help_references.{index}.topic_id"),
            _version(reference.topic_version, f"help_references.{index}.topic_version"),
        ))
        purposes.append(reference.purpose)
        _text(reference.label, f"help_references.{index}.label", 1, 160)
    if len(help_keys) != len(set(help_keys)) or len(purposes) != len(set(purposes)):
        _reject(GuidanceErrorCode.DUPLICATE_IDENTITY, "help_references", "Feature guidance help references repeat.")
    for action in record.actions:
        if action.action_kind is FeatureGuidanceActionKind.OPEN_HELP_TOPIC and (action.topic_id, action.topic_version) not in help_keys:
            _reject(GuidanceErrorCode.DANGLING_REFERENCE, "actions", "Feature guidance action topic is unavailable.")
    if not isinstance(record.applicability, tuple) or not 1 <= len(record.applicability) <= 20:
        _reject(GuidanceErrorCode.INVALID_RECORD, "applicability", "Feature guidance applicability is invalid.")
    applicability_keys: list[str] = []
    for index, item in enumerate(record.applicability):
        if not isinstance(item, Applicability):
            _reject(GuidanceErrorCode.INVALID_RECORD, "applicability", "Feature guidance applicability is invalid.")
        applicability_keys.append(_identifier(item.scope_key, f"applicability.{index}.scope_key"))
        _text(item.label, f"applicability.{index}.label", 1, 160)
    if len(applicability_keys) != len(set(applicability_keys)):
        _reject(GuidanceErrorCode.DUPLICATE_IDENTITY, "applicability", "Feature guidance applicability repeats.")
    _validate_publication(record.publication)
    _validate_sources(record.source_references)
    _digest(record.guidance_digest, "guidance_digest")
    if record.guidance_digest != feature_guidance_digest(record):
        _reject(GuidanceErrorCode.DIGEST_MISMATCH, "guidance_digest", "Feature guidance digest does not match.")
    return record


def validate_feature_mapping(mapping: FeatureGuidanceMapping) -> FeatureGuidanceMapping:
    if not isinstance(mapping, FeatureGuidanceMapping):
        _reject(GuidanceErrorCode.INVALID_RECORD, "mapping", "Feature guidance mapping is invalid.")
    if mapping.schema_version != FEATURE_GUIDANCE_SCHEMA_VERSION:
        _reject(GuidanceErrorCode.UNSUPPORTED_VERSION, "schema_version", "Feature guidance contract version is unsupported.")
    _identifier(mapping.surface_key, "surface_key")
    _identifier(mapping.condition_key, "condition_key")
    _version(mapping.mapping_version, "mapping_version")
    _identifier(mapping.guidance_id, "guidance_id")
    _version(mapping.guidance_version, "guidance_version")
    _validate_publication(mapping.publication)
    _validate_sources(mapping.source_references)
    _digest(mapping.mapping_digest, "mapping_digest")
    if mapping.mapping_digest != feature_mapping_digest(mapping):
        _reject(GuidanceErrorCode.DIGEST_MISMATCH, "mapping_digest", "Feature guidance mapping digest does not match.")
    return mapping


class FeatureGuidanceRegistry:
    """Atomically admitted exact mappings over reviewed records and Help topics."""

    def __init__(
        self,
        records: Sequence[FeatureGuidanceRecord],
        mappings: Sequence[FeatureGuidanceMapping],
        topics: Sequence[PlatformHelpTopic],
        source_fingerprints: Mapping[str, str],
    ) -> None:
        admitted_records = tuple(validate_feature_guidance(item) for item in records)
        admitted_mappings = tuple(validate_feature_mapping(item) for item in mappings)
        if not admitted_records or not admitted_mappings:
            _reject(GuidanceErrorCode.INVALID_RECORD, "feature-guidance-registry", "Feature guidance registry is empty.")
        record_keys = [(item.guidance_id, item.guidance_version) for item in admitted_records]
        mapping_keys = [(item.surface_key, item.condition_key, item.mapping_version) for item in admitted_mappings]
        if len(record_keys) != len(set(record_keys)) or len(mapping_keys) != len(set(mapping_keys)):
            _reject(GuidanceErrorCode.DUPLICATE_IDENTITY, "feature-guidance-registry", "Feature guidance identity repeats.")
        topic_keys = {(item.topic_id, item.topic_version) for item in topics}
        record_key_set = set(record_keys)
        for record in admitted_records:
            _validate_sources(record.source_references, source_fingerprints)
            for reference in record.help_references:
                if (reference.topic_id, reference.topic_version) not in topic_keys:
                    _reject(GuidanceErrorCode.DANGLING_REFERENCE, f"{record.guidance_id}@{record.guidance_version}", "Feature guidance topic is unavailable.")
        for mapping in admitted_mappings:
            _validate_sources(mapping.source_references, source_fingerprints)
            if (mapping.guidance_id, mapping.guidance_version) not in record_key_set:
                _reject(GuidanceErrorCode.DANGLING_REFERENCE, f"{mapping.surface_key}:{mapping.condition_key}@{mapping.mapping_version}", "Feature guidance record is unavailable.")
        self._records = tuple(sorted(admitted_records, key=lambda item: (item.guidance_id, item.guidance_version)))
        self._mappings = tuple(sorted(admitted_mappings, key=lambda item: (item.surface_key, item.condition_key, item.mapping_version)))
        self._record_by_key = {(item.guidance_id, item.guidance_version): item for item in self._records}
        self._mapping_by_key = {(item.surface_key, item.condition_key, item.mapping_version): item for item in self._mappings}
        self._digest = hashlib.sha256(json.dumps(
            {
                "records": [feature_guidance_payload(item) for item in self._records],
                "mappings": [feature_mapping_payload(item) for item in self._mappings],
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")).hexdigest()

    @property
    def records(self) -> tuple[FeatureGuidanceRecord, ...]:
        return self._records

    @property
    def mappings(self) -> tuple[FeatureGuidanceMapping, ...]:
        return self._mappings

    @property
    def digest(self) -> str:
        return self._digest

    def resolve(self, surface_key: str, condition_key: str, mapping_version: str) -> FeatureGuidanceRecord:
        _identifier(surface_key, "surface_key")
        _identifier(condition_key, "condition_key")
        _version(mapping_version, "mapping_version")
        try:
            mapping = self._mapping_by_key[(surface_key, condition_key, mapping_version)]
        except KeyError:
            _reject(GuidanceErrorCode.NOT_FOUND, f"{surface_key}:{condition_key}@{mapping_version}", "Feature guidance is unavailable.")
        return self._record_by_key[(mapping.guidance_id, mapping.guidance_version)]


__all__ = [
    "FEATURE_GUIDANCE_SCHEMA_VERSION",
    "FeatureGuidanceAction",
    "FeatureGuidanceActionKind",
    "FeatureGuidanceMapping",
    "FeatureGuidanceRecord",
    "FeatureGuidanceRegistry",
    "FeatureGuidanceStatus",
    "feature_guidance_digest",
    "feature_guidance_payload",
    "feature_mapping_digest",
    "feature_mapping_payload",
    "validate_feature_guidance",
    "validate_feature_mapping",
]
