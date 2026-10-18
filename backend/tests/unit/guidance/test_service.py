from __future__ import annotations

import pytest

from financial_ai_academy.modules.guidance.adapters import ImmutablePlatformHelpCorpus
from financial_ai_academy.modules.guidance.application import GuidanceService
from financial_ai_academy.modules.guidance.public import (
    GuidanceError,
    GuidanceErrorCode,
    OpenPlatformHelpTopicRequest,
    SearchRequest,
)


def test_service_exposes_transport_neutral_search_and_exact_reads() -> None:
    service = GuidanceService(ImmutablePlatformHelpCorpus())

    page = service.search_platform_help(SearchRequest(query="approved help"))
    topic = service.open_platform_help_topic(
        OpenPlatformHelpTopicRequest("approved-help", "1.0.0")
    )

    assert page.query == "approved help"
    assert [item.topic_id for item in page.results]
    assert topic.topic_id == "approved-help"
    assert topic.source_references


def test_service_preserves_exact_version_absence_without_substitution() -> None:
    service = GuidanceService(ImmutablePlatformHelpCorpus())

    with pytest.raises(GuidanceError) as captured:
        service.open_platform_help_topic(
            OpenPlatformHelpTopicRequest("approved-help", "2.0.0")
        )

    assert captured.value.code is GuidanceErrorCode.NOT_FOUND
