"""Assessment adapter over Curriculum's public placement resolution."""

from __future__ import annotations

from financial_ai_academy.modules.content.public import (
    LessonErrorCode,
    LessonReadError,
)
from financial_ai_academy.modules.curriculum.public import (
    CurriculumOperations,
    ResolvePlacedAssessmentRequest,
    ResolvePlacedPracticeRequest,
)

from ..ports.gateways import PlacedAssessmentReference, PlacedPracticeReference
from ..public import AssessmentError, AssessmentErrorCode


class PublicCurriculumAssessmentGateway:
    def __init__(self, curriculum: CurriculumOperations) -> None:
        self._curriculum = curriculum

    def resolve(self, placement_id: str) -> PlacedAssessmentReference:
        try:
            value = self._curriculum.resolve_placed_assessment(
                ResolvePlacedAssessmentRequest(placement_id)
            )
        except LessonReadError as error:
            code = (
                AssessmentErrorCode.NOT_FOUND
                if error.code is LessonErrorCode.NOT_FOUND
                else AssessmentErrorCode.UNAVAILABLE
            )
            raise AssessmentError(
                code,
                "The knowledge-check placement is unavailable.",
                reference=placement_id,
            ) from error
        return PlacedAssessmentReference(
            placement_id=value.placement_id,
            package_id=value.package_id,
            package_version=value.package_version,
            package_digest=value.package_digest,
            assessment_id=value.assessment_id,
            assessment_version=value.assessment_version,
            definition_digest=value.definition_digest,
            item_id=value.item_id,
            item_version=value.item_version,
            scoring_policy_id=value.scoring_policy_id,
            scoring_policy_version=value.scoring_policy_version,
        )

    def resolve_practice(self, placement_id: str) -> PlacedPracticeReference:
        try:
            value = self._curriculum.resolve_placed_practice(
                ResolvePlacedPracticeRequest(placement_id)
            )
        except LessonReadError as error:
            code = (
                AssessmentErrorCode.NOT_FOUND
                if error.code is LessonErrorCode.NOT_FOUND
                else AssessmentErrorCode.UNAVAILABLE
            )
            raise AssessmentError(
                code,
                "The practice placement is unavailable.",
                reference=placement_id,
            ) from error
        return PlacedPracticeReference(
            placement_id=value.placement_id,
            package_id=value.package_id,
            package_version=value.package_version,
            package_digest=value.package_digest,
            practice_id=value.practice_id,
            practice_version=value.practice_version,
            definition_digest=value.definition_digest,
        )

