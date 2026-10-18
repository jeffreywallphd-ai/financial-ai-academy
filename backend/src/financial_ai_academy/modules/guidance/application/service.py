"""Read-only application service for admitted platform help."""

from __future__ import annotations

from ..ports import (
    ContextualHelpRegistryPort,
    FeatureGuidanceRegistryPort,
    PlatformHelpCorpusPort,
)
from ..public import (
    ContextualHelpRecord,
    FeatureGuidanceResolution,
    OpenContextualHelpRequest,
    OpenPlatformHelpTopicRequest,
    PlatformHelpTopic,
    ResolveFeatureGuidanceRequest,
    SearchPage,
    SearchRequest,
)


class GuidanceService:
    def __init__(
        self,
        corpus: PlatformHelpCorpusPort,
        context_registry: ContextualHelpRegistryPort,
        feature_registry: FeatureGuidanceRegistryPort,
    ) -> None:
        self._corpus = corpus
        self._context_registry = context_registry
        self._feature_registry = feature_registry

    def search_platform_help(self, request: SearchRequest) -> SearchPage:
        return self._corpus.search(request)

    def open_platform_help_topic(
        self,
        request: OpenPlatformHelpTopicRequest,
    ) -> PlatformHelpTopic:
        return self._corpus.get(request.topic_id, request.topic_version)

    def open_contextual_help(
        self,
        request: OpenContextualHelpRequest,
    ) -> ContextualHelpRecord:
        return self._context_registry.get(
            request.context_key,
            request.context_version,
        )

    def resolve_feature_guidance(
        self,
        request: ResolveFeatureGuidanceRequest,
    ) -> FeatureGuidanceResolution:
        return self._feature_registry.resolve_with_mapping(
            request.surface_key,
            request.condition_key,
            request.mapping_version,
        )
