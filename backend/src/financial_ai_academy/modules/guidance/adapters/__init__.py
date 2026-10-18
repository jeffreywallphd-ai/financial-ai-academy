"""Guidance contract adapters."""

from .contextual_help_contract import context_from_mapping
from .feature_guidance_contract import (
    feature_guidance_from_mapping,
    feature_mapping_from_mapping,
)
from .immutable_context_registry import (
    CONTEXTUAL_HELP_MANIFEST_VERSION,
    ImmutableContextualHelpRegistry,
    REQUIRED_CONTEXTUAL_HELP_IDENTITIES,
    default_contextual_help_registry_dir,
)

from .immutable_corpus import (
    ImmutablePlatformHelpCorpus,
    PLATFORM_HELP_MANIFEST_VERSION,
    PLATFORM_HELP_SOURCE_FINGERPRINTS,
    REQUIRED_PLATFORM_HELP_IDENTITIES,
    default_platform_help_corpus_dir,
)
from .immutable_feature_guidance_registry import (
    FEATURE_GUIDANCE_MANIFEST_VERSION,
    ImmutableFeatureGuidanceRegistry,
    REQUIRED_FEATURE_GUIDANCE_IDENTITIES,
    REQUIRED_FEATURE_MAPPING_IDENTITIES,
    default_feature_guidance_registry_dir,
)
from .platform_help_contract import (
    search_page_payload,
    search_request_from_mapping,
    search_request_payload,
    topic_from_mapping,
)

__all__ = [
    "CONTEXTUAL_HELP_MANIFEST_VERSION",
    "FEATURE_GUIDANCE_MANIFEST_VERSION",
    "ImmutableFeatureGuidanceRegistry",
    "ImmutableContextualHelpRegistry",
    "ImmutablePlatformHelpCorpus",
    "PLATFORM_HELP_MANIFEST_VERSION",
    "PLATFORM_HELP_SOURCE_FINGERPRINTS",
    "REQUIRED_PLATFORM_HELP_IDENTITIES",
    "REQUIRED_CONTEXTUAL_HELP_IDENTITIES",
    "REQUIRED_FEATURE_GUIDANCE_IDENTITIES",
    "REQUIRED_FEATURE_MAPPING_IDENTITIES",
    "context_from_mapping",
    "default_contextual_help_registry_dir",
    "default_feature_guidance_registry_dir",
    "default_platform_help_corpus_dir",
    "search_page_payload",
    "search_request_from_mapping",
    "search_request_payload",
    "topic_from_mapping",
    "feature_guidance_from_mapping",
    "feature_mapping_from_mapping",
]
