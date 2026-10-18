"""Guidance contract adapters."""

from .immutable_corpus import (
    ImmutablePlatformHelpCorpus,
    PLATFORM_HELP_MANIFEST_VERSION,
    PLATFORM_HELP_SOURCE_FINGERPRINTS,
    REQUIRED_PLATFORM_HELP_IDENTITIES,
    default_platform_help_corpus_dir,
)
from .platform_help_contract import (
    search_page_payload,
    search_request_from_mapping,
    search_request_payload,
    topic_from_mapping,
)

__all__ = [
    "ImmutablePlatformHelpCorpus",
    "PLATFORM_HELP_MANIFEST_VERSION",
    "PLATFORM_HELP_SOURCE_FINGERPRINTS",
    "REQUIRED_PLATFORM_HELP_IDENTITIES",
    "default_platform_help_corpus_dir",
    "search_page_payload",
    "search_request_from_mapping",
    "search_request_payload",
    "topic_from_mapping",
]
