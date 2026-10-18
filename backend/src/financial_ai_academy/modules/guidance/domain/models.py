"""Immutable platform-help values, integrity rules, and literal search policy."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Sequence
import unicodedata


SCHEMA_VERSION = "1.0.0"
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
_VERSION = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)$"
)
_DIGEST = re.compile(r"^[a-f0-9]{64}$")
# Zero-width non-joiner and joiner carry legitimate shaping/emoji meaning.
_ALLOWED_FORMAT_CODEPOINTS = {0x200C, 0x200D}


class TopicKind(StrEnum):
    GLOSSARY = "glossary"
    HELP = "help"
    METHOD = "method"
    LIMITATION = "limitation"
    TROUBLESHOOTING = "troubleshooting"


class ListKind(StrEnum):
    ORDERED = "ordered"
    UNORDERED = "unordered"


class NoteKind(StrEnum):
    EDUCATIONAL = "educational"
    LIMITATION = "limitation"
    WARNING = "warning"


class SourceArea(StrEnum):
    PRODUCT = "product"
    DOMAIN = "domain"
    CONTRACT = "contract"
    ARCHITECTURE = "architecture"
    RISK = "risk"
    METHOD = "method"


class GuidanceErrorCode(StrEnum):
    INVALID_RECORD = "invalid_record"
    UNSUPPORTED_VERSION = "unsupported_version"
    DIGEST_MISMATCH = "digest_mismatch"
    DUPLICATE_IDENTITY = "duplicate_identity"
    DANGLING_REFERENCE = "dangling_reference"
    NOT_FOUND = "not_found"
    INVALID_CURSOR = "invalid_cursor"
    UNAVAILABLE = "unavailable"


class GuidanceError(ValueError):
    """Bounded public failure without rejected payload or private path data."""

    def __init__(
        self,
        code: GuidanceErrorCode,
        message: str,
        *,
        reference: str = "platform-help",
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code.value,
            "message": self.message,
            "reference": self.reference,
        }


@dataclass(frozen=True, slots=True)
class HeadingNode:
    level: int
    text: str


@dataclass(frozen=True, slots=True)
class ParagraphNode:
    text: str


@dataclass(frozen=True, slots=True)
class ListNode:
    list_kind: ListKind
    items: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NoteNode:
    note_kind: NoteKind
    text: str


@dataclass(frozen=True, slots=True)
class TopicReferenceNode:
    topic_id: str
    topic_version: str
    label: str


type BodyNode = (
    HeadingNode | ParagraphNode | ListNode | NoteNode | TopicReferenceNode
)


@dataclass(frozen=True, slots=True)
class Applicability:
    scope_key: str
    label: str


@dataclass(frozen=True, slots=True)
class PublicationFacts:
    state: str
    reviewed_on: date
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class SourceReference:
    source_key: str
    title: str
    area: SourceArea
    source_version: str
    content_fingerprint: str


@dataclass(frozen=True, slots=True)
class RelatedTopic:
    topic_id: str
    topic_version: str
    relationship: str


@dataclass(frozen=True, slots=True)
class PlatformHelpTopic:
    schema_version: str
    topic_id: str
    topic_version: str
    topic_kind: TopicKind
    title: str
    summary: str
    keywords: tuple[str, ...]
    body: tuple[BodyNode, ...]
    applicability: tuple[Applicability, ...]
    publication: PublicationFacts
    source_references: tuple[SourceReference, ...]
    related_topics: tuple[RelatedTopic, ...]
    topic_digest: str
    glossary_term: str | None = None


@dataclass(frozen=True, slots=True)
class SearchRequest:
    query: str = ""
    topic_kind: TopicKind | None = None
    page_size: int = 20
    cursor: str | None = None
    schema_version: str = SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SearchResult:
    topic_id: str
    topic_version: str
    topic_kind: TopicKind
    title: str
    summary: str
    applicability: tuple[Applicability, ...]
    publication: PublicationFacts
    source_references: tuple[SourceReference, ...]
    topic_digest: str
    glossary_term: str | None = None


@dataclass(frozen=True, slots=True)
class SearchPage:
    schema_version: str
    corpus_digest: str
    query: str
    topic_kind: TopicKind | None
    results: tuple[SearchResult, ...]
    next_cursor: str | None


def _reject(
    code: GuidanceErrorCode,
    reference: str,
    message: str,
) -> None:
    raise GuidanceError(code, message, reference=reference)


def _text(
    value: object,
    reference: str,
    *,
    minimum: int,
    maximum: int,
) -> str:
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Platform help text is invalid.",
        )
    if _contains_unsafe_control(value):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Platform help text contains unsupported control content.",
        )
    return value


def _contains_unsafe_control(value: str) -> bool:
    for character in value:
        category = unicodedata.category(character)
        if category in {"Cc", "Cs", "Co", "Cn"}:
            return True
        if category == "Cf" and ord(character) not in _ALLOWED_FORMAT_CODEPOINTS:
            return True
    return False


def _identifier(value: object, reference: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Platform help identifier is invalid.",
        )
    return value


def _version(value: object, reference: str) -> str:
    if not isinstance(value, str) or _VERSION.fullmatch(value) is None:
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Platform help version is invalid.",
        )
    return value


def _digest(value: object, reference: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Platform help digest is invalid.",
        )
    return value


def _utc_text(value: datetime, reference: str) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None:
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Platform help timestamp is invalid.",
        )
    try:
        result = value.astimezone(timezone.utc).isoformat()
    except (OverflowError, ValueError):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Platform help timestamp is invalid.",
        )
    return result.removesuffix("+00:00") + "Z"


def _body_payload(node: BodyNode) -> dict[str, object]:
    if isinstance(node, HeadingNode):
        return {"node_kind": "heading", "level": node.level, "text": node.text}
    if isinstance(node, ParagraphNode):
        return {"node_kind": "paragraph", "text": node.text}
    if isinstance(node, ListNode):
        return {
            "node_kind": "list",
            "list_kind": node.list_kind.value,
            "items": list(node.items),
        }
    if isinstance(node, NoteNode):
        return {
            "node_kind": "note",
            "note_kind": node.note_kind.value,
            "text": node.text,
        }
    return {
        "node_kind": "topic_reference",
        "topic_id": node.topic_id,
        "topic_version": node.topic_version,
        "label": node.label,
    }


def topic_payload(topic: PlatformHelpTopic) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": topic.schema_version,
        "topic_id": topic.topic_id,
        "topic_version": topic.topic_version,
        "topic_kind": topic.topic_kind.value,
        "title": topic.title,
        "summary": topic.summary,
        "keywords": list(topic.keywords),
        "body": [_body_payload(node) for node in topic.body],
        "applicability": [
            {"scope_key": item.scope_key, "label": item.label}
            for item in topic.applicability
        ],
        "publication": {
            "state": topic.publication.state,
            "reviewed_on": topic.publication.reviewed_on.isoformat(),
            "updated_at": _utc_text(topic.publication.updated_at, "updated_at"),
        },
        "source_references": [
            {
                "source_key": item.source_key,
                "title": item.title,
                "area": item.area.value,
                "source_version": item.source_version,
                "content_fingerprint": item.content_fingerprint,
            }
            for item in topic.source_references
        ],
        "related_topics": [
            {
                "topic_id": item.topic_id,
                "topic_version": item.topic_version,
                "relationship": item.relationship,
            }
            for item in topic.related_topics
        ],
        "topic_digest": topic.topic_digest,
    }
    if topic.glossary_term is not None:
        value["glossary_term"] = topic.glossary_term
    return value


def canonical_topic_bytes(topic: PlatformHelpTopic) -> bytes:
    value = topic_payload(topic)
    value.pop("topic_digest")
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def topic_digest(topic: PlatformHelpTopic) -> str:
    return hashlib.sha256(canonical_topic_bytes(topic)).hexdigest()


def _validate_body(node: BodyNode, reference: str) -> None:
    if isinstance(node, HeadingNode):
        if type(node.level) is not int or not 2 <= node.level <= 4:
            _reject(GuidanceErrorCode.INVALID_RECORD, reference, "Heading is invalid.")
        _text(node.text, reference, minimum=1, maximum=160)
    elif isinstance(node, ParagraphNode):
        _text(node.text, reference, minimum=1, maximum=2000)
    elif isinstance(node, ListNode):
        if not isinstance(node.list_kind, ListKind) or not isinstance(node.items, tuple):
            _reject(GuidanceErrorCode.INVALID_RECORD, reference, "List is invalid.")
        if not 1 <= len(node.items) <= 30:
            _reject(GuidanceErrorCode.INVALID_RECORD, reference, "List is invalid.")
        for index, item in enumerate(node.items):
            _text(item, f"{reference}.items.{index}", minimum=1, maximum=500)
    elif isinstance(node, NoteNode):
        if not isinstance(node.note_kind, NoteKind):
            _reject(GuidanceErrorCode.INVALID_RECORD, reference, "Note is invalid.")
        _text(node.text, reference, minimum=1, maximum=1000)
    elif isinstance(node, TopicReferenceNode):
        _identifier(node.topic_id, f"{reference}.topic_id")
        _version(node.topic_version, f"{reference}.topic_version")
        _text(node.label, f"{reference}.label", minimum=1, maximum=160)
    else:
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            reference,
            "Platform help body node is invalid.",
        )


def validate_topic(topic: PlatformHelpTopic) -> PlatformHelpTopic:
    if not isinstance(topic, PlatformHelpTopic):
        _reject(GuidanceErrorCode.INVALID_RECORD, "topic", "Topic is invalid.")
    if topic.schema_version != SCHEMA_VERSION:
        _reject(
            GuidanceErrorCode.UNSUPPORTED_VERSION,
            "schema_version",
            "Platform help contract version is unsupported.",
        )
    _identifier(topic.topic_id, "topic_id")
    _version(topic.topic_version, "topic_version")
    if not isinstance(topic.topic_kind, TopicKind):
        _reject(GuidanceErrorCode.INVALID_RECORD, "topic_kind", "Topic kind is invalid.")
    _text(topic.title, "title", minimum=1, maximum=160)
    _text(topic.summary, "summary", minimum=20, maximum=500)
    if topic.glossary_term is not None:
        _text(topic.glossary_term, "glossary_term", minimum=1, maximum=120)
    if not isinstance(topic.keywords, tuple) or len(topic.keywords) > 16:
        _reject(GuidanceErrorCode.INVALID_RECORD, "keywords", "Keywords are invalid.")
    for index, keyword in enumerate(topic.keywords):
        _text(keyword, f"keywords.{index}", minimum=1, maximum=80)
    if len(topic.keywords) != len(set(topic.keywords)):
        _reject(GuidanceErrorCode.DUPLICATE_IDENTITY, "keywords", "Keywords repeat.")
    if not isinstance(topic.body, tuple) or not 1 <= len(topic.body) <= 100:
        _reject(GuidanceErrorCode.INVALID_RECORD, "body", "Topic body is invalid.")
    for index, node in enumerate(topic.body):
        _validate_body(node, f"body.{index}")
    if (
        not isinstance(topic.applicability, tuple)
        or not 1 <= len(topic.applicability) <= 20
    ):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            "applicability",
            "Topic applicability is invalid.",
        )
    for index, item in enumerate(topic.applicability):
        if not isinstance(item, Applicability):
            _reject(GuidanceErrorCode.INVALID_RECORD, "applicability", "Applicability is invalid.")
        _identifier(item.scope_key, f"applicability.{index}.scope_key")
        _text(item.label, f"applicability.{index}.label", minimum=1, maximum=160)
    scope_keys = [item.scope_key for item in topic.applicability]
    if len(scope_keys) != len(set(scope_keys)):
        _reject(GuidanceErrorCode.DUPLICATE_IDENTITY, "applicability", "Applicability repeats.")
    if not isinstance(topic.publication, PublicationFacts):
        _reject(GuidanceErrorCode.INVALID_RECORD, "publication", "Publication facts are invalid.")
    if topic.publication.state != "approved" or type(
        topic.publication.reviewed_on
    ) is not date:
        _reject(GuidanceErrorCode.INVALID_RECORD, "publication", "Publication facts are invalid.")
    updated = _utc_text(topic.publication.updated_at, "publication.updated_at")
    if topic.publication.reviewed_on > date.fromisoformat(updated[:10]):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            "publication",
            "Publication chronology is invalid.",
        )
    if (
        not isinstance(topic.source_references, tuple)
        or not 1 <= len(topic.source_references) <= 20
    ):
        _reject(
            GuidanceErrorCode.INVALID_RECORD,
            "source_references",
            "Source references are invalid.",
        )
    for index, source in enumerate(topic.source_references):
        if not isinstance(source, SourceReference) or not isinstance(source.area, SourceArea):
            _reject(
                GuidanceErrorCode.INVALID_RECORD,
                "source_references",
                "Source reference is invalid.",
            )
        _identifier(source.source_key, f"source_references.{index}.source_key")
        _text(source.title, f"source_references.{index}.title", minimum=1, maximum=200)
        _text(
            source.source_version,
            f"source_references.{index}.source_version",
            minimum=1,
            maximum=80,
        )
        _digest(source.content_fingerprint, f"source_references.{index}.content_fingerprint")
    source_keys = [item.source_key for item in topic.source_references]
    if len(source_keys) != len(set(source_keys)):
        _reject(
            GuidanceErrorCode.DUPLICATE_IDENTITY,
            "source_references",
            "Source references repeat.",
        )
    if not isinstance(topic.related_topics, tuple) or len(topic.related_topics) > 20:
        _reject(GuidanceErrorCode.INVALID_RECORD, "related_topics", "Related topics are invalid.")
    related_keys: list[tuple[str, str]] = []
    for index, item in enumerate(topic.related_topics):
        if not isinstance(item, RelatedTopic) or item.relationship not in {
            "see_also",
            "prerequisite",
            "explains",
        }:
            _reject(GuidanceErrorCode.INVALID_RECORD, "related_topics", "Related topic is invalid.")
        key = (
            _identifier(item.topic_id, f"related_topics.{index}.topic_id"),
            _version(item.topic_version, f"related_topics.{index}.topic_version"),
        )
        if key == (topic.topic_id, topic.topic_version):
            _reject(
                GuidanceErrorCode.INVALID_RECORD,
                "related_topics",
                "Topic cannot relate to itself.",
            )
        related_keys.append(key)
    if len(related_keys) != len(set(related_keys)):
        _reject(GuidanceErrorCode.DUPLICATE_IDENTITY, "related_topics", "Related topics repeat.")
    _digest(topic.topic_digest, "topic_digest")
    if topic.topic_digest != topic_digest(topic):
        _reject(
            GuidanceErrorCode.DIGEST_MISMATCH,
            "topic_digest",
            "Platform help topic digest does not match.",
        )
    return topic


def corpus_digest(topics: Sequence[PlatformHelpTopic]) -> str:
    ordered = sorted(
        (topic_payload(topic) for topic in topics),
        key=lambda value: (value["topic_id"], value["topic_version"]),
    )
    return hashlib.sha256(
        json.dumps(
            ordered,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def normalize_query(value: object) -> str:
    if not isinstance(value, str) or len(value) > 200:
        _reject(GuidanceErrorCode.INVALID_RECORD, "query", "Search query is invalid.")
    if _contains_unsafe_control(value):
        _reject(GuidanceErrorCode.INVALID_RECORD, "query", "Search query contains control content.")
    return " ".join(value.split()).casefold()


def _version_key(value: str) -> tuple[int, int, int]:
    matched = _VERSION.fullmatch(value)
    assert matched is not None
    return (
        int(matched.group(1)),
        int(matched.group(2)),
        int(matched.group(3)),
    )


def _rank(topic: PlatformHelpTopic, query: str) -> int | None:
    if not query:
        return 0
    title = topic.title.casefold()
    term = (topic.glossary_term or "").casefold()
    if query in {title, term}:
        return 0
    if title.startswith(query) or term.startswith(query):
        return 1
    tokens = query.split()
    title_area = f"{title} {term}"
    if all(token in title_area for token in tokens):
        return 2
    detail_area = " ".join(
        [topic.summary.casefold(), *(value.casefold() for value in topic.keywords)]
    )
    if all(token in detail_area for token in tokens):
        return 3
    return None


def _cursor_bytes(value: dict[str, object]) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _cursor_digest(value: dict[str, object]) -> str:
    return hashlib.sha256(b"platform-help-cursor-v1\0" + _cursor_bytes(value)).hexdigest()


def _cursor_text(value: dict[str, object]) -> str:
    envelope = {**value, "d": _cursor_digest(value)}
    raw = _cursor_bytes(envelope)
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _cursor_value(value: str) -> dict[str, object]:
    if not isinstance(value, str) or not 1 <= len(value) <= 4096:
        _reject(GuidanceErrorCode.INVALID_CURSOR, "cursor", "Search cursor is invalid.")
    try:
        padding = "=" * (-len(value) % 4)
        decoded = base64.b64decode(
            value + padding,
            altchars=b"-_",
            validate=True,
        )
        result = json.loads(decoded.decode("utf-8"))
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
        _reject(GuidanceErrorCode.INVALID_CURSOR, "cursor", "Search cursor is invalid.")
    if not isinstance(result, dict) or set(result) != {"a", "c", "d", "k", "p", "q", "v"}:
        _reject(GuidanceErrorCode.INVALID_CURSOR, "cursor", "Search cursor is invalid.")
    supplied_digest = result["d"]
    payload = {key: item for key, item in result.items() if key != "d"}
    if (
        not isinstance(supplied_digest, str)
        or _DIGEST.fullmatch(supplied_digest) is None
        or not hmac.compare_digest(supplied_digest, _cursor_digest(payload))
    ):
        _reject(GuidanceErrorCode.INVALID_CURSOR, "cursor", "Search cursor is invalid.")
    return result


class PlatformHelpCorpus:
    """Atomically validated in-memory corpus with exact reads and stable search."""

    def __init__(self, topics: Sequence[PlatformHelpTopic]) -> None:
        if not isinstance(topics, Sequence) or isinstance(topics, (str, bytes)):
            _reject(GuidanceErrorCode.INVALID_RECORD, "corpus", "Help corpus is invalid.")
        admitted = tuple(validate_topic(topic) for topic in topics)
        if not admitted:
            _reject(GuidanceErrorCode.INVALID_RECORD, "corpus", "Help corpus is empty.")
        keys = [(topic.topic_id, topic.topic_version) for topic in admitted]
        if len(keys) != len(set(keys)):
            _reject(GuidanceErrorCode.DUPLICATE_IDENTITY, "corpus", "Topic identities repeat.")
        key_set = set(keys)
        for topic in admitted:
            references = [
                (item.topic_id, item.topic_version) for item in topic.related_topics
            ] + [
                (node.topic_id, node.topic_version)
                for node in topic.body
                if isinstance(node, TopicReferenceNode)
            ]
            if any(reference not in key_set for reference in references):
                _reject(
                    GuidanceErrorCode.DANGLING_REFERENCE,
                    topic.topic_id,
                    "Platform help topic reference is unavailable.",
                )
        self._topics = admitted
        self._by_key = dict(zip(keys, admitted, strict=True))
        self.digest = corpus_digest(admitted)

    @property
    def topics(self) -> tuple[PlatformHelpTopic, ...]:
        return self._topics

    def get(self, topic_id: str, topic_version: str) -> PlatformHelpTopic:
        _identifier(topic_id, "topic_id")
        _version(topic_version, "topic_version")
        try:
            return self._by_key[(topic_id, topic_version)]
        except KeyError:
            _reject(
                GuidanceErrorCode.NOT_FOUND,
                f"{topic_id}@{topic_version}",
                "That exact platform help topic is unavailable.",
            )

    def search(self, request: SearchRequest) -> SearchPage:
        if not isinstance(request, SearchRequest):
            _reject(GuidanceErrorCode.INVALID_RECORD, "search", "Search request is invalid.")
        if request.schema_version != SCHEMA_VERSION:
            _reject(
                GuidanceErrorCode.UNSUPPORTED_VERSION,
                "schema_version",
                "Platform help search version is unsupported.",
            )
        query = normalize_query(request.query)
        if request.topic_kind is not None and not isinstance(request.topic_kind, TopicKind):
            _reject(GuidanceErrorCode.INVALID_RECORD, "topic_kind", "Topic kind is invalid.")
        if type(request.page_size) is not int or not 1 <= request.page_size <= 50:
            _reject(GuidanceErrorCode.INVALID_RECORD, "page_size", "Page size is invalid.")
        ranked: list[tuple[int, PlatformHelpTopic]] = []
        for topic in self._topics:
            if request.topic_kind is not None and topic.topic_kind is not request.topic_kind:
                continue
            rank = _rank(topic, query)
            if rank is not None:
                ranked.append((rank, topic))
        ranked.sort(
            key=lambda item: (
                item[0],
                item[1].topic_id,
                _version_key(item[1].topic_version),
            )
        )
        position = 0
        kind = request.topic_kind.value if request.topic_kind is not None else ""
        if request.cursor is not None:
            cursor = _cursor_value(request.cursor)
            if (
                cursor["v"] != 1
                or cursor["q"] != query
                or cursor["k"] != kind
                or cursor["c"] != self.digest
                or type(cursor["p"]) is not int
                or not 0 < cursor["p"] < len(ranked)
                or cursor["a"]
                != [
                    ranked[cursor["p"] - 1][0],
                    ranked[cursor["p"] - 1][1].topic_id,
                    ranked[cursor["p"] - 1][1].topic_version,
                ]
            ):
                _reject(GuidanceErrorCode.INVALID_CURSOR, "cursor", "Search cursor does not match.")
            position = cursor["p"]
        selected = ranked[position : position + request.page_size]
        next_position = position + len(selected)
        next_cursor = (
            _cursor_text(
                {
                    "v": 1,
                    "q": query,
                    "k": kind,
                    "c": self.digest,
                    "p": next_position,
                    "a": [
                        selected[-1][0],
                        selected[-1][1].topic_id,
                        selected[-1][1].topic_version,
                    ],
                }
            )
            if next_position < len(ranked)
            else None
        )
        return SearchPage(
            schema_version=SCHEMA_VERSION,
            corpus_digest=self.digest,
            query=query,
            topic_kind=request.topic_kind,
            results=tuple(
                SearchResult(
                    topic_id=topic.topic_id,
                    topic_version=topic.topic_version,
                    topic_kind=topic.topic_kind,
                    title=topic.title,
                    summary=topic.summary,
                    applicability=topic.applicability,
                    publication=topic.publication,
                    source_references=topic.source_references,
                    glossary_term=topic.glossary_term,
                    topic_digest=topic.topic_digest,
                )
                for _, topic in selected
            ),
            next_cursor=next_cursor,
        )
