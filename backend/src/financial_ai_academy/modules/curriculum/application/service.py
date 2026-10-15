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
    AssessmentPlacement,
    CreateAssessmentPlacementRequest,
    CreateLessonPlacementRequest,
    LessonPlacement,
    LessonReadingResult,
    OpenPlacedLessonRequest,
    ResolvePlacedAssessmentRequest,
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

    def create_assessment_placement(
        self, request: CreateAssessmentPlacementRequest
    ) -> AssessmentPlacement:
        lesson = self._get_placement(request.placement_id)
        if (
            lesson.package_id,
            lesson.package_version,
            lesson.package_digest,
        ) != (
            request.package_id,
            request.package_version,
            request.package_digest,
        ):
            raise LessonReadError(
                LessonErrorCode.INVALID_PACKAGE,
                "Assessment placement does not match the exact lesson.",
                reference=request.placement_id,
            )
        self._validate_assessment_reference(request)
        candidate = AssessmentPlacement(
            placement_id=request.placement_id,
            package_id=request.package_id,
            package_version=request.package_version,
            package_digest=request.package_digest,
            assessment_id=request.assessment_id,
            assessment_version=request.assessment_version,
            definition_digest=request.definition_digest,
            item_id=request.item_id,
            item_version=request.item_version,
            scoring_policy_id=request.scoring_policy_id,
            scoring_policy_version=request.scoring_policy_version,
            created_at=datetime.now(timezone.utc),
        )
        try:
            stored, _created = self._repository.save_assessment_if_absent(
                candidate
            )
        except PlacementConflict as error:
            raise LessonReadError(
                LessonErrorCode.IMMUTABLE_CONFLICT,
                "The placement already maps to another assessment.",
                reference=request.placement_id,
            ) from error
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Assessment placement storage is unavailable.",
                reference=request.placement_id,
            ) from error
        return stored

    def resolve_placed_assessment(
        self, request: ResolvePlacedAssessmentRequest
    ) -> AssessmentPlacement:
        try:
            placement = self._repository.get_assessment(request.placement_id)
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Assessment placement storage is unavailable.",
                reference=request.placement_id,
            ) from error
        if placement is None:
            raise LessonReadError(
                LessonErrorCode.NOT_FOUND,
                "Assessment placement was not found.",
                reference=request.placement_id,
            )
        return placement

    def _get_placement(self, placement_id: str) -> LessonPlacement:
        try:
            placement = self._repository.get(placement_id)
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Lesson placement storage is unavailable.",
                reference=placement_id,
            ) from error
        if placement is None:
            raise LessonReadError(
                LessonErrorCode.NOT_FOUND,
                "Lesson placement was not found.",
                reference=placement_id,
            )
        return placement

    @staticmethod
    def _validate_assessment_reference(
        request: CreateAssessmentPlacementRequest,
    ) -> None:
        identifiers = (
            request.assessment_id,
            request.item_id,
            request.scoring_policy_id,
        )
        versions = (
            request.assessment_version,
            request.item_version,
            request.scoring_policy_version,
        )
        if (
            any(not _PLACEMENT_ID.fullmatch(value) for value in identifiers)
            or any(value != "1.0.0" for value in versions)
            or not re.fullmatch(r"[a-f0-9]{64}", request.definition_digest)
        ):
            raise LessonReadError(
                LessonErrorCode.INVALID_PACKAGE,
                "Assessment placement reference is invalid.",
                reference=request.placement_id,
            )
