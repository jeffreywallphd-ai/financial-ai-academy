"""Strict mapping adapter for the contextual-help v1 contract."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from ..domain import (
    Applicability,
    ContextHelpReference,
    ContextPurpose,
    ContextualHelpRecord,
    GuidanceError,
    GuidanceErrorCode,
    PublicationFacts,
    SourceArea,
    SourceReference,
    validate_context,
)


def _reject(reference: str) -> None:
    raise GuidanceError(
        GuidanceErrorCode.INVALID_RECORD,
        "Contextual help record is malformed.",
        reference=reference,
    )


def _mapping(value: object, reference: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        _reject(reference)
    return value


def _exact_keys(
    value: Mapping[str, Any],
    required: set[str],
    reference: str,
) -> None:
    if set(value) != required:
        _reject(reference)


def _items(value: object, reference: str) -> tuple[Any, ...]:
    if not isinstance(value, list):
        _reject(reference)
    return tuple(value)


def _applicability(value: object, reference: str) -> Applicability:
    item = _mapping(value, reference)
    _exact_keys(item, {"scope_key", "label"}, reference)
    return Applicability(scope_key=item["scope_key"], label=item["label"])


def _help_reference(value: object, reference: str) -> ContextHelpReference:
    item = _mapping(value, reference)
    _exact_keys(
        item,
        {"topic_id", "topic_version", "purpose", "label"},
        reference,
    )
    try:
        purpose = ContextPurpose(item["purpose"])
    except (TypeError, ValueError):
        _reject(reference)
    return ContextHelpReference(
        topic_id=item["topic_id"],
        topic_version=item["topic_version"],
        purpose=purpose,
        label=item["label"],
    )


def _source(value: object, reference: str) -> SourceReference:
    item = _mapping(value, reference)
    _exact_keys(
        item,
        {"source_key", "title", "area", "source_version", "content_fingerprint"},
        reference,
    )
    try:
        area = SourceArea(item["area"])
    except (TypeError, ValueError):
        _reject(reference)
    return SourceReference(
        source_key=item["source_key"],
        title=item["title"],
        area=area,
        source_version=item["source_version"],
        content_fingerprint=item["content_fingerprint"],
    )


def context_from_mapping(value: Mapping[str, Any]) -> ContextualHelpRecord:
    item = _mapping(value, "context")
    _exact_keys(
        item,
        {
            "schema_version",
            "context_key",
            "context_version",
            "feature_label",
            "applicability",
            "help_references",
            "publication",
            "source_references",
            "context_digest",
        },
        "context",
    )
    try:
        applicability = tuple(
            _applicability(value, f"applicability.{index}")
            for index, value in enumerate(_items(item["applicability"], "applicability"))
        )
        help_references = tuple(
            _help_reference(value, f"help_references.{index}")
            for index, value in enumerate(
                _items(item["help_references"], "help_references")
            )
        )
        publication_value = _mapping(item["publication"], "publication")
        _exact_keys(
            publication_value,
            {"state", "reviewed_on", "updated_at"},
            "publication",
        )
        publication = PublicationFacts(
            state=publication_value["state"],
            reviewed_on=date.fromisoformat(publication_value["reviewed_on"]),
            updated_at=datetime.fromisoformat(
                publication_value["updated_at"].replace("Z", "+00:00")
            ),
        )
        source_references = tuple(
            _source(value, f"source_references.{index}")
            for index, value in enumerate(
                _items(item["source_references"], "source_references")
            )
        )
    except GuidanceError:
        raise
    except (KeyError, TypeError, ValueError):
        _reject("context")
    return validate_context(
        ContextualHelpRecord(
            schema_version=item["schema_version"],
            context_key=item["context_key"],
            context_version=item["context_version"],
            feature_label=item["feature_label"],
            applicability=applicability,
            help_references=help_references,
            publication=publication,
            source_references=source_references,
            context_digest=item["context_digest"],
        )
    )


__all__ = ["context_from_mapping"]
