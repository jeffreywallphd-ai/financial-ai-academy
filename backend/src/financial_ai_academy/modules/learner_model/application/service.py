"""Rebuild and open exact lesson-completion projections."""

from __future__ import annotations

from uuid import UUID

from ..domain.models import (
    InvalidCompletionEvidence,
    LessonCompletionProjection,
    derive_lesson_completion,
)
from ..ports.gateways import CompletionEvidenceSourcePort
from ..ports.repositories import CompletionProjectionRepositoryPort
from ..ports.system import ClockPort
from ..public import (
    LearnerModelError,
    LearnerModelErrorCode,
    LessonCompletionHistoryEntry,
    LessonCompletionView,
    OpenLessonCompletionRequest,
)


class LearnerModelService:
    def __init__(
        self,
        source: CompletionEvidenceSourcePort,
        repository: CompletionProjectionRepositoryPort,
        clock: ClockPort,
    ) -> None:
        self._source = source
        self._repository = repository
        self._clock = clock

    def open_lesson_completion(
        self, request: OpenLessonCompletionRequest
    ) -> LessonCompletionView:
        self._validate_context(request)
        try:
            evidence = self._source.list_for_lesson(
                learner_id=request.learner_id,
                placement_id=request.placement_id,
            )
        except LearnerModelError:
            raise
        except Exception as error:
            raise LearnerModelError(
                LearnerModelErrorCode.UNAVAILABLE,
                "Completion evidence is temporarily unavailable.",
                reference=request.placement_id,
            ) from error
        try:
            projection = derive_lesson_completion(
                learner_id=request.learner_id,
                placement_id=request.placement_id,
                evidence=evidence,
                rebuilt_at=self._clock.now(),
            )
        except InvalidCompletionEvidence as error:
            raise LearnerModelError(
                LearnerModelErrorCode.INCONSISTENT_EVIDENCE,
                "Completion evidence could not be reconciled.",
                reference=error.reference,
            ) from error
        try:
            self._repository.replace(projection)
        except Exception as error:
            raise LearnerModelError(
                LearnerModelErrorCode.UNAVAILABLE,
                "The completion view is temporarily unavailable.",
                reference=request.placement_id,
            ) from error
        return self._view(projection)

    @staticmethod
    def _validate_context(request: OpenLessonCompletionRequest) -> None:
        try:
            UUID(request.learner_id)
        except (ValueError, AttributeError) as error:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_CONTEXT,
                "Learner context is not authorized.",
                reference="learner",
            ) from error
        value = request.placement_id
        if (
            not 3 <= len(value) <= 64
            or not value[0].isalnum()
            or not all(
                character.islower()
                or character.isdigit()
                or character in "._-"
                for character in value
            )
        ):
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_CONTEXT,
                "Lesson placement context is invalid.",
                reference="placement_id",
            )

    @staticmethod
    def _view(projection: LessonCompletionProjection) -> LessonCompletionView:
        return LessonCompletionView(
            placement_id=projection.placement_id,
            completed=projection.completed,
            completion_meaning=(
                "bounded_knowledge_check_completed"
                if projection.completed
                else "not_completed"
            ),
            source_digest=projection.source_digest,
            rebuilt_at=projection.rebuilt_at,
            history=tuple(
                LessonCompletionHistoryEntry(
                    event_id=item.event_id,
                    attempt_id=item.attempt_id,
                    evidence_id=item.evidence_id,
                    package_id=item.package_id,
                    package_version=item.package_version,
                    package_digest=item.package_digest,
                    assessment_id=item.assessment_id,
                    assessment_version=item.assessment_version,
                    definition_digest=item.definition_digest,
                    item_id=item.item_id,
                    item_version=item.item_version,
                    scoring_policy_id=item.scoring_policy_id,
                    scoring_policy_version=item.scoring_policy_version,
                    score=item.score,
                    max_score=item.max_score,
                    completed_at=item.completed_at,
                )
                for item in projection.history
            ),
        )
