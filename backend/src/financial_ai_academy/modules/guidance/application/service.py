"""Read-only application service for admitted platform help."""

from __future__ import annotations

from ..ports import PlatformHelpCorpusPort
from ..public import (
    OpenPlatformHelpTopicRequest,
    PlatformHelpTopic,
    SearchPage,
    SearchRequest,
)


class GuidanceService:
    def __init__(self, corpus: PlatformHelpCorpusPort) -> None:
        self._corpus = corpus

    def search_platform_help(self, request: SearchRequest) -> SearchPage:
        return self._corpus.search(request)

    def open_platform_help_topic(
        self,
        request: OpenPlatformHelpTopicRequest,
    ) -> PlatformHelpTopic:
        return self._corpus.get(request.topic_id, request.topic_version)
