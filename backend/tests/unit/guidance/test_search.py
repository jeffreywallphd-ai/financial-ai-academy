from __future__ import annotations

from dataclasses import replace

import pytest

from financial_ai_academy.modules.guidance.domain import (
    GuidanceError,
    GuidanceErrorCode,
    PlatformHelpCorpus,
    SearchRequest,
    TopicKind,
    normalize_query,
)

from .test_models import make_topic


def search_corpus(order: tuple[int, ...] = (0, 1, 2, 3)) -> PlatformHelpCorpus:
    topics = (
        make_topic(
            "exact-topic",
            title="Approved help",
            glossary_term="Reviewed guidance",
            keywords=("source",),
        ),
        make_topic(
            "prefix-topic",
            title="Approved help for projects",
            keywords=("project",),
        ),
        make_topic(
            "token-topic",
            title="Help with approved methods",
            keywords=("method",),
            kind=TopicKind.METHOD,
        ),
        make_topic(
            "detail-topic",
            title="Read limitations",
            summary="This reviewed summary covers approved help for safe use.",
            keywords=("approved", "help"),
            kind=TopicKind.LIMITATION,
        ),
    )
    return PlatformHelpCorpus(tuple(topics[index] for index in order))


def test_normalization_and_declared_ranking_are_deterministic() -> None:
    corpus = search_corpus()
    page = corpus.search(SearchRequest(query="  APPROVED   help  ", page_size=10))
    assert page.query == "approved help"
    assert [item.topic_id for item in page.results] == [
        "exact-topic",
        "prefix-topic",
        "token-topic",
        "detail-topic",
    ]
    assert normalize_query(" CAFÉ ") == "café"


def test_browse_and_search_ignore_insertion_order() -> None:
    forward = search_corpus((0, 1, 2, 3))
    reverse = search_corpus((3, 2, 1, 0))
    for query in ("", "approved help"):
        left = forward.search(SearchRequest(query=query, page_size=50))
        right = reverse.search(SearchRequest(query=query, page_size=50))
        assert [item.topic_id for item in left.results] == [
            item.topic_id for item in right.results
        ]
        assert left.corpus_digest == right.corpus_digest


def test_kind_filter_and_clear_filter_have_closed_meaning() -> None:
    corpus = search_corpus()
    filtered = corpus.search(
        SearchRequest(query="approved help", topic_kind=TopicKind.METHOD)
    )
    assert [item.topic_kind for item in filtered.results] == [TopicKind.METHOD]
    assert len(corpus.search(SearchRequest(query="approved help")).results) > 1


def test_cursor_is_bound_to_query_filter_and_corpus() -> None:
    corpus = search_corpus()
    first = corpus.search(SearchRequest(query="approved help", page_size=1))
    assert first.next_cursor is not None
    second = corpus.search(
        SearchRequest(
            query="APPROVED HELP",
            page_size=2,
            cursor=first.next_cursor,
        )
    )
    assert [item.topic_id for item in second.results] == [
        "prefix-topic",
        "token-topic",
    ]

    for request in (
        SearchRequest(query="different", cursor=first.next_cursor),
        SearchRequest(
            query="approved help",
            topic_kind=TopicKind.HELP,
            cursor=first.next_cursor,
        ),
        SearchRequest(query="approved help", cursor=first.next_cursor + "!"),
    ):
        with pytest.raises(GuidanceError) as captured:
            corpus.search(request)
        assert captured.value.code is GuidanceErrorCode.INVALID_CURSOR

    changed = PlatformHelpCorpus((*corpus.topics, make_topic("extra-topic")))
    with pytest.raises(GuidanceError) as stale:
        changed.search(
            SearchRequest(query="approved help", cursor=first.next_cursor)
        )
    assert stale.value.code is GuidanceErrorCode.INVALID_CURSOR


def test_flexible_valid_counts_and_optional_glossary_do_not_freeze_fixtures() -> None:
    topics = tuple(
        make_topic(
            f"topic-{index:02d}",
            title=f"Topic {index:02d}",
            glossary_term=None if index % 2 else f"Term {index:02d}",
            keywords=(f"keyword-{index:02d}",),
        )
        for index in range(1, 13)
    )
    corpus = PlatformHelpCorpus(topics)
    page = corpus.search(SearchRequest(page_size=5))
    assert len(page.results) == 5
    assert page.next_cursor is not None
    assert len(
        corpus.search(SearchRequest(page_size=50)).results
    ) == len(topics)


@pytest.mark.parametrize(
    "search_request, code",
    [
        (SearchRequest(page_size=0), GuidanceErrorCode.INVALID_RECORD),
        (SearchRequest(page_size=True), GuidanceErrorCode.INVALID_RECORD),
        (SearchRequest(query="bad\nquery"), GuidanceErrorCode.INVALID_RECORD),
        (
            replace(SearchRequest(), schema_version="2.0.0"),
            GuidanceErrorCode.UNSUPPORTED_VERSION,
        ),
    ],
)
def test_invalid_search_requests_fail_before_results(
    search_request: SearchRequest,
    code: GuidanceErrorCode,
) -> None:
    with pytest.raises(GuidanceError) as captured:
        search_corpus().search(search_request)
    assert captured.value.code is code
