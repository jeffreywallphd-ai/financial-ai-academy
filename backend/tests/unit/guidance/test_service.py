from __future__ import annotations

import pytest

from financial_ai_academy.modules.guidance.adapters import (
    ImmutableContextualHelpRegistry,
    ImmutablePlatformHelpCorpus,
)
from financial_ai_academy.modules.guidance.application import GuidanceService
from financial_ai_academy.modules.guidance.public import (
    GuidanceError,
    GuidanceErrorCode,
    OpenContextualHelpRequest,
    OpenPlatformHelpTopicRequest,
    SearchRequest,
)


def test_service_exposes_transport_neutral_search_and_exact_reads() -> None:
    corpus = ImmutablePlatformHelpCorpus()
    service = GuidanceService(
        corpus,
        ImmutableContextualHelpRegistry(topics=corpus.topics),
    )

    page = service.search_platform_help(SearchRequest(query="approved help"))
    topic = service.open_platform_help_topic(
        OpenPlatformHelpTopicRequest("approved-help", "1.0.0")
    )
    context = service.open_contextual_help(
        OpenContextualHelpRequest("project-result", "1.0.0")
    )

    assert page.query == "approved help"
    assert [item.topic_id for item in page.results]
    assert topic.topic_id == "approved-help"
    assert topic.source_references
    assert context.context_key == "project-result"
    assert [reference.topic_id for reference in context.help_references]


def test_service_preserves_exact_version_absence_without_substitution() -> None:
    corpus = ImmutablePlatformHelpCorpus()
    service = GuidanceService(
        corpus,
        ImmutableContextualHelpRegistry(topics=corpus.topics),
    )

    with pytest.raises(GuidanceError) as captured:
        service.open_platform_help_topic(
            OpenPlatformHelpTopicRequest("approved-help", "2.0.0")
        )

    assert captured.value.code is GuidanceErrorCode.NOT_FOUND

    with pytest.raises(GuidanceError) as context_captured:
        service.open_contextual_help(
            OpenContextualHelpRequest("project-result", "2.0.0")
        )

    assert context_captured.value.code is GuidanceErrorCode.NOT_FOUND
