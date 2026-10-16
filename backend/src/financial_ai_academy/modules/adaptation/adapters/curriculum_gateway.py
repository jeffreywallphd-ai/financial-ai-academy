"""Curriculum public-surface adapter for exact navigation sources."""

from __future__ import annotations

from financial_ai_academy.modules.curriculum.public import (
    CurriculumGraph,
    CurriculumGraphError,
    CurriculumGraphErrorCode,
    CurriculumOperations,
    OpenCurriculumGraphRequest,
    OpenPlacedLessonRequest,
    ResolvePlacedAssessmentRequest,
)

from ..ports.navigation_sources import (
    AssessmentSourceReference,
    ExactCurriculumGraphRequest,
    LessonSourceReference,
    NavigationSourceError,
    NavigationSourceErrorCode,
)


class PublicCurriculumNavigationGateway:
    def __init__(self, operations: CurriculumOperations) -> None:
        self._operations = operations

    def open_graph(
        self, request: ExactCurriculumGraphRequest
    ) -> CurriculumGraph:
        try:
            return self._operations.open_curriculum_graph(
                OpenCurriculumGraphRequest(
                    curriculum_id=request.curriculum_id,
                    curriculum_version=request.curriculum_version,
                )
            )
        except CurriculumGraphError as error:
            code = (
                NavigationSourceErrorCode.NOT_FOUND
                if error.code is CurriculumGraphErrorCode.NOT_FOUND
                else NavigationSourceErrorCode.UNAVAILABLE
            )
            raise NavigationSourceError(code) from error
        except Exception as error:
            raise NavigationSourceError(
                NavigationSourceErrorCode.UNAVAILABLE
            ) from error

    def lesson_is_available(
        self, reference: LessonSourceReference
    ) -> bool:
        try:
            reading = self._operations.open_placed_lesson(
                OpenPlacedLessonRequest(reference.placement_id)
            )
            return (
                reading.placement_id == reference.placement_id
                and reading.package_id == reference.package_id
                and reading.package_version == reference.package_version
                and reading.package_digest == reference.package_digest
            )
        except Exception:
            return False

    def assessment_is_available(
        self, reference: AssessmentSourceReference
    ) -> bool:
        try:
            placement = self._operations.resolve_placed_assessment(
                ResolvePlacedAssessmentRequest(reference.placement_id)
            )
            return (
                placement.placement_id == reference.placement_id
                and placement.assessment_id == reference.assessment_id
                and placement.assessment_version
                == reference.assessment_version
                and placement.definition_digest
                == reference.definition_digest
            )
        except Exception:
            return False
