"""Strict mapping adapters for feature-guidance v1."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from ..domain import (
    Applicability,
    ContextHelpReference,
    ContextPurpose,
    FeatureGuidanceAction,
    FeatureGuidanceActionKind,
    FeatureGuidanceMapping,
    FeatureGuidanceRecord,
    FeatureGuidanceStatus,
    GuidanceError,
    GuidanceErrorCode,
    PublicationFacts,
    SourceArea,
    SourceReference,
    validate_feature_guidance,
    validate_feature_mapping,
)


def _reject(reference: str) -> None:
    raise GuidanceError(
        GuidanceErrorCode.INVALID_RECORD,
        "Feature guidance is malformed.",
        reference=reference,
    )


def _mapping(value: object, reference: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        _reject(reference)
    return value


def _exact(value: Mapping[str, Any], keys: set[str], reference: str) -> None:
    if set(value) != keys:
        _reject(reference)


def _items(value: object, reference: str) -> tuple[Any, ...]:
    if not isinstance(value, list):
        _reject(reference)
    return tuple(value)


def _publication(value: object) -> PublicationFacts:
    item = _mapping(value, "publication")
    _exact(item, {"state", "reviewed_on", "updated_at"}, "publication")
    return PublicationFacts(
        state=item["state"],
        reviewed_on=date.fromisoformat(item["reviewed_on"]),
        updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00")),
    )


def _source(value: object, reference: str) -> SourceReference:
    item = _mapping(value, reference)
    _exact(item, {"source_key", "title", "area", "source_version", "content_fingerprint"}, reference)
    return SourceReference(
        source_key=item["source_key"],
        title=item["title"],
        area=SourceArea(item["area"]),
        source_version=item["source_version"],
        content_fingerprint=item["content_fingerprint"],
    )


def _sources(value: object) -> tuple[SourceReference, ...]:
    return tuple(_source(item, f"source_references.{index}") for index, item in enumerate(_items(value, "source_references")))


def feature_guidance_from_mapping(value: Mapping[str, Any]) -> FeatureGuidanceRecord:
    item = _mapping(value, "guidance")
    _exact(item, {
        "schema_version", "guidance_id", "guidance_version", "status", "heading",
        "reason", "outcome", "actions", "help_references", "applicability",
        "publication", "source_references", "guidance_digest",
    }, "guidance")
    try:
        actions: list[FeatureGuidanceAction] = []
        for index, value_item in enumerate(_items(item["actions"], "actions")):
            action = _mapping(value_item, f"actions.{index}")
            kind = FeatureGuidanceActionKind(action.get("action_kind"))
            expected = {"action_kind", "label", "topic_id", "topic_version"} if kind is FeatureGuidanceActionKind.OPEN_HELP_TOPIC else {"action_kind", "label"}
            _exact(action, expected, f"actions.{index}")
            actions.append(FeatureGuidanceAction(
                action_kind=kind,
                label=action["label"],
                topic_id=action.get("topic_id"),
                topic_version=action.get("topic_version"),
            ))
        references: list[ContextHelpReference] = []
        for index, value_item in enumerate(_items(item["help_references"], "help_references")):
            reference = _mapping(value_item, f"help_references.{index}")
            _exact(reference, {"topic_id", "topic_version", "purpose", "label"}, f"help_references.{index}")
            references.append(ContextHelpReference(
                topic_id=reference["topic_id"],
                topic_version=reference["topic_version"],
                purpose=ContextPurpose(reference["purpose"]),
                label=reference["label"],
            ))
        applicability: list[Applicability] = []
        for index, value_item in enumerate(_items(item["applicability"], "applicability")):
            scope = _mapping(value_item, f"applicability.{index}")
            _exact(scope, {"scope_key", "label"}, f"applicability.{index}")
            applicability.append(Applicability(scope_key=scope["scope_key"], label=scope["label"]))
        record = FeatureGuidanceRecord(
            schema_version=item["schema_version"],
            guidance_id=item["guidance_id"],
            guidance_version=item["guidance_version"],
            status=FeatureGuidanceStatus(item["status"]),
            heading=item["heading"],
            reason=item["reason"],
            outcome=item["outcome"],
            actions=tuple(actions),
            help_references=tuple(references),
            applicability=tuple(applicability),
            publication=_publication(item["publication"]),
            source_references=_sources(item["source_references"]),
            guidance_digest=item["guidance_digest"],
        )
    except GuidanceError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError):
        _reject("guidance")
    return validate_feature_guidance(record)


def feature_mapping_from_mapping(value: Mapping[str, Any]) -> FeatureGuidanceMapping:
    item = _mapping(value, "mapping")
    _exact(item, {
        "schema_version", "surface_key", "condition_key", "mapping_version",
        "guidance_id", "guidance_version", "publication", "source_references",
        "mapping_digest",
    }, "mapping")
    try:
        mapping = FeatureGuidanceMapping(
            schema_version=item["schema_version"],
            surface_key=item["surface_key"],
            condition_key=item["condition_key"],
            mapping_version=item["mapping_version"],
            guidance_id=item["guidance_id"],
            guidance_version=item["guidance_version"],
            publication=_publication(item["publication"]),
            source_references=_sources(item["source_references"]),
            mapping_digest=item["mapping_digest"],
        )
    except GuidanceError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError):
        _reject("mapping")
    return validate_feature_mapping(mapping)


__all__ = ["feature_guidance_from_mapping", "feature_mapping_from_mapping"]
