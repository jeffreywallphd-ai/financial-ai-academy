"""Curriculum port for exact Content public resolution."""

from __future__ import annotations

from typing import Protocol

from financial_ai_academy.modules.content.public import PublishedLesson


class ContentLessonGatewayPort(Protocol):
    def get_exact(
        self,
        package_id: str,
        package_version: str,
        package_digest: str,
    ) -> PublishedLesson: ...
