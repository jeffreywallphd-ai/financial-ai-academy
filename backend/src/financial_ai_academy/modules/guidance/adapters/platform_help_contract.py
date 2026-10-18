"""Strict mapping adapter for the platform-help v1 public contract."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Mapping

from ..domain import (
    Applicability,
    GuidanceError,
    GuidanceErrorCode,
    HeadingNode,
    ListKind,
    ListNode,
    NoteKind,
    NoteNode,
    ParagraphNode,
    PlatformHelpTopic,
    PublicationFacts,
    RelatedTopic,
    SearchPage,
    SearchRequest,
    SourceArea,
    SourceReference,
    TopicKind,
    TopicReferenceNode,
    topic_payload,
)
from ..domain.models import validate_topic


def _reject(reference: str) -> None:
    raise GuidanceError(
        GuidanceErrorCode.INVALID_RECORD,
        "Platform help record is malformed.",
        reference=reference,
    )


def _mapping(value: object, reference: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        _reject(reference)
    return value


def _exact_keys(
    value: Mapping[str, Any],
    required: set[str],
    optional: set[str],
    reference: str,
) -> None:
    keys = set(value)
    if not required <= keys or not keys <= required | optional:
        _reject(reference)


def _tuple(value: object, reference: str) -> tuple[Any, ...]:
    if not isinstance(value, list):
        _reject(reference)
    return tuple(value)


def _body_node(value: object, reference: str):
    item = _mapping(value, reference)
    kind = item.get("node_kind")
    if kind == "heading":
        _exact_keys(item, {"node_kind", "level", "text"}, set(), reference)
        return HeadingNode(level=item["level"], text=item["text"])
    if kind == "paragraph":
        _exact_keys(item, {"node_kind", "text"}, set(), reference)
        return ParagraphNode(text=item["text"])
    if kind == "list":
        _exact_keys(item, {"node_kind", "list_kind", "items"}, set(), reference)
        try:
            list_kind = ListKind(item["list_kind"])
        except (TypeError, ValueError):
            _reject(reference)
        return ListNode(
            list_kind=list_kind,
            items=_tuple(item["items"], f"{reference}.items"),
        )
    if kind == "note":
        _exact_keys(item, {"node_kind", "note_kind", "text"}, set(), reference)
        try:
            note_kind = NoteKind(item["note_kind"])
        except (TypeError, ValueError):
            _reject(reference)
        return NoteNode(note_kind=note_kind, text=item["text"])
    if kind == "topic_reference":
        _exact_keys(
            item,
            {"node_kind", "topic_id", "topic_version", "label"},
            set(),
            reference,
        )
        return TopicReferenceNode(
            topic_id=item["topic_id"],
            topic_version=item["topic_version"],
            label=item["label"],
        )
    _reject(reference)


def topic_from_mapping(value: Mapping[str, Any]) -> PlatformHelpTopic:
    item = _mapping(value, "topic")
    _exact_keys(
        item,
        {
            "schema_version",
            "topic_id",
            "topic_version",
            "topic_kind",
            "title",
            "summary",
            "keywords",
            "body",
            "applicability",
            "publication",
            "source_references",
            "related_topics",
            "topic_digest",
        },
        {"glossary_term"},
        "topic",
    )
    try:
        topic_kind = TopicKind(item["topic_kind"])
        keywords = _tuple(item["keywords"], "keywords")
        body = tuple(
            _body_node(node, f"body.{index}")
            for index, node in enumerate(_tuple(item["body"], "body"))
        )
        applicability = tuple(
            Applicability(**_closed_pair(value, "scope_key", "label", f"applicability.{index}"))
            for index, value in enumerate(_tuple(item["applicability"], "applicability"))
        )
        publication_value = _mapping(item["publication"], "publication")
        _exact_keys(
            publication_value,
            {"state", "reviewed_on", "updated_at"},
            set(),
            "publication",
        )
        publication = PublicationFacts(
            state=publication_value["state"],
            reviewed_on=date.fromisoformat(publication_value["reviewed_on"]),
            updated_at=datetime.fromisoformat(
                publication_value["updated_at"].replace("Z", "+00:00")
            ),
        )
        sources = tuple(
            _source(value, f"source_references.{index}")
            for index, value in enumerate(
                _tuple(item["source_references"], "source_references")
            )
        )
        related = tuple(
            RelatedTopic(**_closed_triple(
                value,
                "topic_id",
                "topic_version",
                "relationship",
                f"related_topics.{index}",
            ))
            for index, value in enumerate(_tuple(item["related_topics"], "related_topics"))
        )
    except GuidanceError:
        raise
    except (KeyError, TypeError, ValueError):
        _reject("topic")
    topic = PlatformHelpTopic(
        schema_version=item["schema_version"],
        topic_id=item["topic_id"],
        topic_version=item["topic_version"],
        topic_kind=topic_kind,
        title=item["title"],
        summary=item["summary"],
        glossary_term=item.get("glossary_term"),
        keywords=keywords,
        body=body,
        applicability=applicability,
        publication=publication,
        source_references=sources,
        related_topics=related,
        topic_digest=item["topic_digest"],
    )
    return validate_topic(topic)


def _closed_pair(
    value: object,
    first: str,
    second: str,
    reference: str,
) -> dict[str, Any]:
    item = _mapping(value, reference)
    _exact_keys(item, {first, second}, set(), reference)
    return {first: item[first], second: item[second]}


def _closed_triple(
    value: object,
    first: str,
    second: str,
    third: str,
    reference: str,
) -> dict[str, Any]:
    item = _mapping(value, reference)
    _exact_keys(item, {first, second, third}, set(), reference)
    return {first: item[first], second: item[second], third: item[third]}


def _source(value: object, reference: str) -> SourceReference:
    item = _mapping(value, reference)
    _exact_keys(
        item,
        {"source_key", "title", "area", "source_version", "content_fingerprint"},
        set(),
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


def search_request_from_mapping(value: Mapping[str, Any]) -> SearchRequest:
    item = _mapping(value, "search")
    _exact_keys(
        item,
        {"schema_version", "query", "page_size"},
        {"topic_kind", "cursor"},
        "search",
    )
    try:
        topic_kind = (
            TopicKind(item["topic_kind"]) if "topic_kind" in item else None
        )
    except (TypeError, ValueError):
        _reject("topic_kind")
    return SearchRequest(
        schema_version=item["schema_version"],
        query=item["query"],
        topic_kind=topic_kind,
        page_size=item["page_size"],
        cursor=item.get("cursor"),
    )


def search_request_payload(value: SearchRequest) -> dict[str, object]:
    result: dict[str, object] = {
        "schema_version": value.schema_version,
        "query": value.query,
        "page_size": value.page_size,
    }
    if value.topic_kind is not None:
        result["topic_kind"] = value.topic_kind.value
    if value.cursor is not None:
        result["cursor"] = value.cursor
    return result


def search_page_payload(value: SearchPage) -> dict[str, object]:
    result: dict[str, object] = {
        "schema_version": value.schema_version,
        "corpus_digest": value.corpus_digest,
        "query": value.query,
        "results": [
            {
                **{
                    "topic_id": item.topic_id,
                    "topic_version": item.topic_version,
                    "topic_kind": item.topic_kind.value,
                    "title": item.title,
                    "summary": item.summary,
                    "applicability": [
                        {"scope_key": fact.scope_key, "label": fact.label}
                        for fact in item.applicability
                    ],
                    "publication": {
                        "state": item.publication.state,
                        "reviewed_on": item.publication.reviewed_on.isoformat(),
                        "updated_at": item.publication.updated_at.astimezone(
                            timezone.utc
                        ).isoformat().removesuffix("+00:00")
                        + "Z",
                    },
                    "source_references": [
                        {
                            "source_key": source.source_key,
                            "title": source.title,
                            "area": source.area.value,
                            "source_version": source.source_version,
                            "content_fingerprint": source.content_fingerprint,
                        }
                        for source in item.source_references
                    ],
                    "topic_digest": item.topic_digest,
                },
                **(
                    {"glossary_term": item.glossary_term}
                    if item.glossary_term is not None
                    else {}
                ),
            }
            for item in value.results
        ],
        "next_cursor": value.next_cursor,
    }
    if value.topic_kind is not None:
        result["topic_kind"] = value.topic_kind.value
    return result


__all__ = [
    "search_page_payload",
    "search_request_from_mapping",
    "search_request_payload",
    "topic_from_mapping",
    "topic_payload",
]
