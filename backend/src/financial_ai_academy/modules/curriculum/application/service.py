"""Exact-version lesson placement and safe read composition."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from financial_ai_academy.modules.content.public import (
    LessonErrorCode,
    LessonReadError,
)

from ..ports.content_gateway import ContentLessonGatewayPort
from ..ports.repositories import CurriculumRepositoryPort, PlacementConflict
from ..public import (
    CreateLessonPlacementRequest,
    LessonPlacement,
    LessonReadingResult,
    OpenPlacedLessonRequest,
)


_PLACEMENT_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")


class CurriculumService:
    def __init__(
        self,
        repository: CurriculumRepositoryPort,
        content: ContentLessonGatewayPort,
    ) -> None:
        self._repository = repository
        self._content = content

    def create_lesson_placement(
        self, request: CreateLessonPlacementRequest
    ) -> LessonPlacement:
        if not _PLACEMENT_ID.fullmatch(request.placement_id):
            raise LessonReadError(
                LessonErrorCode.INVALID_PACKAGE,
                "Lesson placement identity is invalid.",
                reference=request.placement_id,
            )
        self._content.get_exact(
            request.package_id,
            request.package_version,
            request.package_digest,
        )
        candidate = LessonPlacement(
            placement_id=request.placement_id,
            package_id=request.package_id,
            package_version=request.package_version,
            package_digest=request.package_digest,
            created_at=datetime.now(timezone.utc),
        )
        try:
            stored, _created = self._repository.save_if_absent(candidate)
        except PlacementConflict as error:
            raise LessonReadError(
                LessonErrorCode.IMMUTABLE_CONFLICT,
                "The placement identity already maps to another lesson.",
                reference=request.placement_id,
            ) from error
        except LessonReadError:
            raise
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Lesson placement storage is unavailable.",
                reference=request.placement_id,
            ) from error
        return stored

    def open_placed_lesson(
        self, request: OpenPlacedLessonRequest
    ) -> LessonReadingResult:
        try:
            placement = self._repository.get(request.placement_id)
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Lesson placement storage is unavailable.",
                reference=request.placement_id,
            ) from error
        if placement is None:
            raise LessonReadError(
                LessonErrorCode.NOT_FOUND,
                "Lesson placement was not found.",
                reference=request.placement_id,
            )
        try:
            lesson = self._content.get_exact(
                placement.package_id,
                placement.package_version,
                placement.package_digest,
            )
        except LessonReadError as error:
            if error.code is LessonErrorCode.NOT_FOUND:
                raise LessonReadError(
                    LessonErrorCode.UNAVAILABLE,
                    "The placement's exact lesson version is unavailable.",
                    reference=request.placement_id,
                ) from error
            raise
        return LessonReadingResult(
            placement_id=placement.placement_id,
            package_id=lesson.package_id,
            package_version=lesson.package_version,
            package_digest=lesson.package_digest,
            title=lesson.title,
            objectives=lesson.objectives,
            body=lesson.body,
            sources=lesson.sources,
            assets=lesson.assets,
            provenance=lesson.provenance,
        )
