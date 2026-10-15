"""Deterministic query policy over one validated discovery projection."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from typing import TypeVar

from ..domain.models import discovery_digest
from ..public import (
    AppliedLearningOpportunityQuery,
    DiscoveryError,
    DiscoveryErrorCode,
    LearningOpportunityBrowse,
    LearningOpportunityQueryPage,
    LearningOpportunityRecord,
    OpportunityAvailability,
    OpportunityKind,
    OpportunityLevel,
    OpportunityQuerySort,
    QueryLearningOpportunitiesRequest,
)


_DISCOVERY_QUERY_VERSION = "1.0.0"
_MAX_DISCOVERY_RECORDS = 500
_MAX_QUERY_TEXT = 100
_MAX_QUERY_TERMS = 10
_MAX_QUERY_FILTERS = 8
_MAX_QUERY_CURSOR = 1024
_TOPIC = re.compile(r"^[a-z0-9][a-z0-9-]{1,49}$")
_DIGEST = re.compile(r"^[a-f0-9]{64}$")
_CURSOR = re.compile(r"^[A-Za-z0-9_-]+\.[a-f0-9]{64}$")
_QueryEnum = TypeVar(
    "_QueryEnum",
    OpportunityLevel,
    OpportunityKind,
    OpportunityAvailability,
)


@dataclass(frozen=True, slots=True)
class PreparedLearningOpportunityQuery:
    applied: AppliedLearningOpportunityQuery
    fingerprint: str
    cursor_generation: str | None
    offset: int


def prepare_learning_opportunity_query(
    request: QueryLearningOpportunitiesRequest,
) -> PreparedLearningOpportunityQuery:
    """Validate and canonicalize before any projection repository access."""
    applied = _applied_query(request)
    fingerprint = discovery_digest(_query_json(applied))
    cursor_generation: str | None = None
    offset = 0
    if request.cursor is not None:
        cursor_generation, cursor_query, offset = _decode_cursor(request.cursor)
        if cursor_query != fingerprint:
            _invalid_query(
                "cursor",
                "Learning-opportunity cursor does not match the query.",
            )
    return PreparedLearningOpportunityQuery(
        applied=applied,
        fingerprint=fingerprint,
        cursor_generation=cursor_generation,
        offset=offset,
    )


def query_learning_opportunity_projection(
    browse: LearningOpportunityBrowse,
    prepared: PreparedLearningOpportunityQuery,
) -> LearningOpportunityQueryPage:
    """Apply a prepared query to one already validated projection."""
    if (
        prepared.cursor_generation is not None
        and prepared.cursor_generation != browse.projection_generation
    ):
        raise DiscoveryError(
            DiscoveryErrorCode.STALE_CURSOR,
            "Learning-opportunity results changed; begin a new query.",
            reference="cursor",
        )
    matches = tuple(
        record
        for record in browse.records
        if _matches_query(record, prepared.applied)
    )
    ordered = _sort_query_matches(matches, prepared.applied.sort)
    if prepared.offset >= len(ordered) and prepared.offset != 0:
        _invalid_query(
            "cursor",
            "Learning-opportunity cursor position is invalid.",
        )
    page_end = min(
        prepared.offset + prepared.applied.page_size,
        len(ordered),
    )
    records = ordered[prepared.offset:page_end]
    next_cursor = (
        _encode_cursor(
            browse.projection_generation,
            prepared.fingerprint,
            page_end,
        )
        if page_end < len(ordered)
        else None
    )
    return LearningOpportunityQueryPage(
        schema_version=_DISCOVERY_QUERY_VERSION,
        projection_generation=browse.projection_generation,
        projected_at=browse.projected_at,
        applied_query=prepared.applied,
        total_matches=len(ordered),
        records=records,
        next_cursor=next_cursor,
    )


def _applied_query(
    request: QueryLearningOpportunitiesRequest,
) -> AppliedLearningOpportunityQuery:
    if not isinstance(request, QueryLearningOpportunitiesRequest):
        _invalid_query(
            "query",
            "Learning-opportunity query is invalid.",
        )
    query = _normalize_query_text(request.query, "query")
    prerequisite_query = _normalize_query_text(
        request.prerequisite_query,
        "prerequisite_query",
    )
    topics = _query_topics(request.topics)
    levels = _query_enums(request.levels, OpportunityLevel, "levels")
    kinds = _query_enums(request.kinds, OpportunityKind, "kinds")
    availabilities = _query_enums(
        request.availabilities,
        OpportunityAvailability,
        "availabilities",
    )
    minimum = _query_minutes(request.minimum_minutes, "minimum_minutes")
    maximum = _query_minutes(request.maximum_minutes, "maximum_minutes")
    if minimum is not None and maximum is not None and minimum > maximum:
        _invalid_query(
            "duration",
            "Learning-opportunity duration range is invalid.",
        )
    if not isinstance(request.sort, OpportunityQuerySort):
        _invalid_query(
            "sort",
            "Learning-opportunity sort is unsupported.",
        )
    if (
        not isinstance(request.page_size, int)
        or isinstance(request.page_size, bool)
        or not 1 <= request.page_size <= 50
    ):
        _invalid_query(
            "page_size",
            "Learning-opportunity page size is invalid.",
        )
    if request.cursor is not None and (
        not isinstance(request.cursor, str)
        or not 1 <= len(request.cursor) <= _MAX_QUERY_CURSOR
        or not _CURSOR.fullmatch(request.cursor)
    ):
        _invalid_query(
            "cursor",
            "Learning-opportunity cursor is invalid.",
        )
    return AppliedLearningOpportunityQuery(
        query=query,
        prerequisite_query=prerequisite_query,
        topics=topics,
        levels=levels,
        kinds=kinds,
        availabilities=availabilities,
        minimum_minutes=minimum,
        maximum_minutes=maximum,
        sort=request.sort,
        page_size=request.page_size,
    )


def _normalize_query_text(value: object, reference: str) -> str | None:
    if value is None:
        return None
    if (
        not isinstance(value, str)
        or not 1 <= len(value) <= _MAX_QUERY_TEXT
        or any(character in value for character in ("\x00", "\r", "\n"))
    ):
        _invalid_query(
            reference,
            "Learning-opportunity query text is invalid.",
        )
    normalized = " ".join(unicodedata.normalize("NFKC", value).split()).casefold()
    if (
        not 1 <= len(normalized) <= _MAX_QUERY_TEXT
        or len(normalized.split(" ")) > _MAX_QUERY_TERMS
    ):
        _invalid_query(
            reference,
            "Learning-opportunity query text is invalid.",
        )
    return normalized


def _query_topics(value: object) -> tuple[str, ...]:
    if (
        not isinstance(value, tuple)
        or len(value) > _MAX_QUERY_FILTERS
        or any(
            not isinstance(topic, str) or not _TOPIC.fullmatch(topic)
            for topic in value
        )
    ):
        _invalid_query(
            "topics",
            "Learning-opportunity topic filters are invalid.",
        )
    topics = tuple(sorted(set(value)))
    return topics


def _query_enums(
    value: object,
    enum_type: type[_QueryEnum],
    reference: str,
) -> tuple[_QueryEnum, ...]:
    if (
        not isinstance(value, tuple)
        or len(value) > _MAX_QUERY_FILTERS
        or any(not isinstance(item, enum_type) for item in value)
    ):
        _invalid_query(
            reference,
            "Learning-opportunity filters are invalid.",
        )
    filters = tuple(sorted(set(value), key=str))
    return filters


def _query_minutes(value: object, reference: str) -> int | None:
    if value is None:
        return None
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 1 <= value <= 1440
    ):
        _invalid_query(
            reference,
            "Learning-opportunity duration filter is invalid.",
        )
    return value


def _matches_query(
    record: LearningOpportunityRecord,
    query: AppliedLearningOpportunityQuery,
) -> bool:
    searchable = _search_text(
        " ".join(
            (
                record.title,
                record.summary,
                *record.objectives,
                *record.topics,
                record.prerequisite_summary,
            )
        )
    )
    prerequisite = _search_text(record.prerequisite_summary)
    if query.query is not None and not all(
        term in searchable for term in query.query.split(" ")
    ):
        return False
    if query.prerequisite_query is not None and not all(
        term in prerequisite for term in query.prerequisite_query.split(" ")
    ):
        return False
    return (
        (not query.topics or bool(set(query.topics) & set(record.topics)))
        and (not query.levels or record.level in query.levels)
        and (not query.kinds or record.kind in query.kinds)
        and (
            not query.availabilities
            or record.availability in query.availabilities
        )
        and (
            query.minimum_minutes is None
            or record.estimated_minutes >= query.minimum_minutes
        )
        and (
            query.maximum_minutes is None
            or record.estimated_minutes <= query.maximum_minutes
        )
    )


def _sort_query_matches(
    records: tuple[LearningOpportunityRecord, ...],
    sort: OpportunityQuerySort,
) -> tuple[LearningOpportunityRecord, ...]:
    if sort is OpportunityQuerySort.CATALOG:
        return records
    if sort is OpportunityQuerySort.TITLE:
        key = lambda record: (
            _search_text(record.title),
            record.opportunity_id,
        )
    elif sort is OpportunityQuerySort.DURATION_ASCENDING:
        key = lambda record: (
            record.estimated_minutes,
            _search_text(record.title),
            record.opportunity_id,
        )
    else:
        key = lambda record: (
            -record.estimated_minutes,
            _search_text(record.title),
            record.opportunity_id,
        )
    return tuple(sorted(records, key=key))


def _search_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split()).casefold()


def _query_json(query: AppliedLearningOpportunityQuery) -> dict[str, object]:
    return {
        "query": query.query,
        "prerequisite_query": query.prerequisite_query,
        "topics": list(query.topics),
        "levels": [str(value) for value in query.levels],
        "kinds": [str(value) for value in query.kinds],
        "availabilities": [str(value) for value in query.availabilities],
        "minimum_minutes": query.minimum_minutes,
        "maximum_minutes": query.maximum_minutes,
        "sort": str(query.sort),
        "page_size": query.page_size,
    }


def _encode_cursor(generation: str, query: str, offset: int) -> str:
    payload = {
        "generation": generation,
        "offset": offset,
        "query": query,
        "version": 1,
    }
    encoded = base64.urlsafe_b64encode(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).decode("ascii").rstrip("=")
    digest = hashlib.sha256(encoded.encode("ascii")).hexdigest()
    return f"{encoded}.{digest}"


def _decode_cursor(value: str) -> tuple[str, str, int]:
    try:
        encoded, provided_digest = value.split(".", 1)
        expected_digest = hashlib.sha256(encoded.encode("ascii")).hexdigest()
        if provided_digest != expected_digest:
            raise ValueError
        padding = "=" * (-len(encoded) % 4)
        payload = json.loads(
            base64.b64decode(
                encoded + padding,
                altchars=b"-_",
                validate=True,
            ).decode("utf-8")
        )
        if (
            not isinstance(payload, dict)
            or set(payload) != {"generation", "offset", "query", "version"}
            or payload["version"] != 1
            or not isinstance(payload["generation"], str)
            or not _DIGEST.fullmatch(payload["generation"])
            or not isinstance(payload["query"], str)
            or not _DIGEST.fullmatch(payload["query"])
            or not isinstance(payload["offset"], int)
            or isinstance(payload["offset"], bool)
            or not 1 <= payload["offset"] <= _MAX_DISCOVERY_RECORDS
        ):
            raise ValueError
    except (UnicodeError, ValueError, json.JSONDecodeError) as error:
        raise DiscoveryError(
            DiscoveryErrorCode.INVALID_QUERY,
            "Learning-opportunity cursor is invalid.",
            reference="cursor",
        ) from error
    return payload["generation"], payload["query"], payload["offset"]


def _invalid_query(reference: object, message: str):
    raise DiscoveryError(
        DiscoveryErrorCode.INVALID_QUERY,
        message,
        reference=reference,
    )
