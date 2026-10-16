"""Adapter from Curriculum's port to the public Content facade."""

from __future__ import annotations

from financial_ai_academy.modules.content.public import (
    ContentOperations,
    GetPublishedLessonVersionRequest,
    GetPublishedProjectBriefRequest,
    PublishedLesson,
    PublishedProjectBrief,
)


class PublicContentGateway:
    def __init__(self, content: ContentOperations) -> None:
        self._content = content

    def get_exact(
        self,
        package_id: str,
        package_version: str,
        package_digest: str,
    ) -> PublishedLesson:
        return self._content.get_published_lesson_version(
            GetPublishedLessonVersionRequest(
                package_id=package_id,
                package_version=package_version,
                package_digest=package_digest,
            )
        )

    def get_project_brief_exact(
        self,
        package_id: str,
        package_version: str,
        package_digest: str,
        brief_id: str,
    ) -> PublishedProjectBrief:
        return self._content.get_published_project_brief(
            GetPublishedProjectBriefRequest(
                package_id=package_id,
                package_version=package_version,
                package_digest=package_digest,
                brief_id=brief_id,
            )
        )
