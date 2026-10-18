"""Stable public operations and values for the Guidance module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .adapters.platform_help_contract import search_page_payload
from .domain import (
    ContextualHelpRecord,
    GuidanceError,
    GuidanceErrorCode,
    PlatformHelpTopic,
    SearchPage,
    SearchRequest,
    TopicKind,
    context_payload,
    topic_payload,
)


@dataclass(frozen=True, slots=True)
class OpenPlatformHelpTopicRequest:
    topic_id: str
    topic_version: str


@dataclass(frozen=True, slots=True)
class OpenContextualHelpRequest:
    context_key: str
    context_version: str


class GuidanceOperations(Protocol):
    def search_platform_help(self, request: SearchRequest) -> SearchPage: ...

    def open_platform_help_topic(
        self,
        request: OpenPlatformHelpTopicRequest,
    ) -> PlatformHelpTopic: ...

    def open_contextual_help(
        self,
        request: OpenContextualHelpRequest,
    ) -> ContextualHelpRecord: ...


__all__ = [
    "GuidanceError",
    "GuidanceErrorCode",
    "GuidanceOperations",
    "ContextualHelpRecord",
    "OpenContextualHelpRequest",
    "OpenPlatformHelpTopicRequest",
    "PlatformHelpTopic",
    "SearchPage",
    "SearchRequest",
    "TopicKind",
    "context_payload",
    "search_page_payload",
    "topic_payload",
]
