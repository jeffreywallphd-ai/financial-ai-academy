"""Transport-neutral read port for an admitted platform-help corpus."""

from __future__ import annotations

from typing import Protocol

from ..domain import PlatformHelpTopic, SearchPage, SearchRequest


class PlatformHelpCorpusPort(Protocol):
    @property
    def topics(self) -> tuple[PlatformHelpTopic, ...]: ...

    def get(self, topic_id: str, topic_version: str) -> PlatformHelpTopic: ...

    def search(self, request: SearchRequest) -> SearchPage: ...
