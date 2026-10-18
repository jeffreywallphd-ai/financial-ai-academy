from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timezone

import pytest

from financial_ai_academy.modules.guidance.domain import (
    Applicability,
    GuidanceError,
    GuidanceErrorCode,
    HeadingNode,
    ListKind,
    ListNode,
    NoteKind,
    NoteNode,
    ParagraphNode,
    PlatformHelpCorpus,
    PlatformHelpTopic,
    PublicationFacts,
    RelatedTopic,
    SourceArea,
    SourceReference,
    TopicKind,
    TopicReferenceNode,
    canonical_topic_bytes,
    corpus_digest,
    topic_digest,
    topic_payload,
)


EMPTY_DIGEST = "0" * 64


def make_topic(
    topic_id: str = "alpha-topic",
    *,
    version: str = "1.0.0",
    title: str = "Alpha topic",
    summary: str = "A reviewed explanation for the shared platform surface.",
    kind: TopicKind = TopicKind.HELP,
    glossary_term: str | None = None,
    keywords: tuple[str, ...] = ("alpha", "shared"),
    body=None,
    related: tuple[RelatedTopic, ...] = (),
) -> PlatformHelpTopic:
    topic = PlatformHelpTopic(
        schema_version="1.0.0",
        topic_id=topic_id,
        topic_version=version,
        topic_kind=kind,
        title=title,
        summary=summary,
        glossary_term=glossary_term,
        keywords=keywords,
        body=body
        or (
            HeadingNode(level=2, text="Reviewed meaning"),
            ParagraphNode(text="Read this safe inert explanation."),
            ListNode(list_kind=ListKind.UNORDERED, items=("One fact", "Two facts")),
            NoteNode(note_kind=NoteKind.LIMITATION, text="This does not replace its source."),
        ),
        applicability=(
            Applicability(scope_key="shared-platform", label="Shared platform"),
        ),
        publication=PublicationFacts(
            state="approved",
            reviewed_on=date(2026, 10, 18),
            updated_at=datetime(2026, 10, 18, tzinfo=timezone.utc),
        ),
        source_references=(
            SourceReference(
                source_key="product-source",
                title="Product source",
                area=SourceArea.PRODUCT,
                source_version="2026-10-18",
                content_fingerprint="a" * 64,
            ),
        ),
        related_topics=related,
        topic_digest=EMPTY_DIGEST,
    )
    return replace(topic, topic_digest=topic_digest(topic))


def test_topic_payload_covers_closed_safe_node_union_and_exact_digest() -> None:
    target = make_topic("target-topic", title="Target topic")
    topic = make_topic(
        body=(
            HeadingNode(level=3, text="Heading"),
            ParagraphNode(text="Paragraph"),
            ListNode(list_kind=ListKind.ORDERED, items=("First", "Second")),
            NoteNode(note_kind=NoteKind.EDUCATIONAL, text="Educational note"),
            TopicReferenceNode(
                topic_id=target.topic_id,
                topic_version=target.topic_version,
                label="Read target",
            ),
        ),
        related=(
            RelatedTopic(
                topic_id=target.topic_id,
                topic_version=target.topic_version,
                relationship="see_also",
            ),
        ),
    )
    corpus = PlatformHelpCorpus((topic, target))
    value = topic_payload(corpus.get("alpha-topic", "1.0.0"))
    assert [node["node_kind"] for node in value["body"]] == [
        "heading",
        "paragraph",
        "list",
        "note",
        "topic_reference",
    ]
    assert value["topic_digest"] == topic_digest(topic)
    assert b"topic_digest" not in canonical_topic_bytes(topic)


def test_corpus_digest_is_insertion_order_independent_and_unicode_preserving() -> None:
    alpha = make_topic(summary="A reviewed café explanation for the platform.")
    beta = make_topic("beta-topic", title="Béta topic")
    family = make_topic(
        "family-topic",
        summary="A reviewed family 👩‍👩‍👧‍👦 explanation for the platform.",
    )
    assert corpus_digest((alpha, beta)) == corpus_digest((beta, alpha))
    assert "café".encode() in canonical_topic_bytes(alpha)
    assert "👩‍👩‍👧‍👦".encode() in canonical_topic_bytes(family)
    PlatformHelpCorpus((family,))


def test_duplicate_and_dangling_topics_fail_atomically() -> None:
    topic = make_topic()
    with pytest.raises(GuidanceError) as duplicate:
        PlatformHelpCorpus((topic, topic))
    assert duplicate.value.code is GuidanceErrorCode.DUPLICATE_IDENTITY

    dangling = make_topic(
        related=(
            RelatedTopic(
                topic_id="missing-topic",
                topic_version="1.0.0",
                relationship="see_also",
            ),
        )
    )
    with pytest.raises(GuidanceError) as absent:
        PlatformHelpCorpus((dangling,))
    assert absent.value.code is GuidanceErrorCode.DANGLING_REFERENCE


def test_exact_lookup_never_substitutes_a_different_version() -> None:
    corpus = PlatformHelpCorpus((make_topic(version="2.0.0"),))
    with pytest.raises(GuidanceError) as captured:
        corpus.get("alpha-topic", "1.0.0")
    assert captured.value.code is GuidanceErrorCode.NOT_FOUND
    assert "2.0.0" not in captured.value.message


@pytest.mark.parametrize("version", ["1.0.0-01", "1.0.0-alpha..1", "1.0.0+build"])
def test_v1_versions_use_only_the_stable_semver_core(version: str) -> None:
    with pytest.raises(GuidanceError) as captured:
        PlatformHelpCorpus((make_topic(version=version),))
    assert captured.value.code is GuidanceErrorCode.INVALID_RECORD


@pytest.mark.parametrize(
    "topic, code",
    [
        (
            replace(make_topic(), topic_digest="f" * 64),
            GuidanceErrorCode.DIGEST_MISMATCH,
        ),
        (
            replace(
                make_topic(),
                publication=PublicationFacts(
                    state="approved",
                    reviewed_on=date(2026, 10, 19),
                    updated_at=datetime(2026, 10, 18, tzinfo=timezone.utc),
                ),
            ),
            GuidanceErrorCode.INVALID_RECORD,
        ),
        (
            make_topic(body=(ParagraphNode(text="unsafe\u0000text"),)),
            GuidanceErrorCode.INVALID_RECORD,
        ),
        (
            make_topic(body=(ParagraphNode(text="unsafe\u202etext"),)),
            GuidanceErrorCode.INVALID_RECORD,
        ),
        (
            replace(
                make_topic(),
                publication=PublicationFacts(
                    state="approved",
                    reviewed_on=datetime(2026, 10, 18, tzinfo=timezone.utc),
                    updated_at=datetime(2026, 10, 18, tzinfo=timezone.utc),
                ),
            ),
            GuidanceErrorCode.INVALID_RECORD,
        ),
    ],
)
def test_integrity_chronology_and_control_content_fail_closed(
    topic: PlatformHelpTopic,
    code: GuidanceErrorCode,
) -> None:
    with pytest.raises(GuidanceError) as captured:
        PlatformHelpCorpus((topic,))
    assert captured.value.code is code
    assert "unsafe" not in captured.value.message


def test_private_payload_fields_have_no_domain_representation() -> None:
    names = set(PlatformHelpTopic.__dataclass_fields__)
    assert names.isdisjoint(
        {
            "repository_path",
            "url",
            "html",
            "reviewer",
            "approval",
            "prompt",
            "learner_id",
            "provider_payload",
        }
    )
