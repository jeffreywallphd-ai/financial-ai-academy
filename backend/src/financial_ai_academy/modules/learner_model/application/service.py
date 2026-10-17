"""Rebuild and open exact lesson-completion projections."""

from __future__ import annotations

from uuid import UUID

from ..domain.models import (
    InvalidCompletionEvidence,
    LessonCompletionProjection,
    PracticeHistoryProjection,
    ProjectCompletionProjection,
    derive_practice_history,
    derive_project_completion,
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
    OpenPracticeHistoryRequest,
    OpenProjectCompletionRequest,
    PracticeHistoryAttempt,
    PracticeHistoryItemSummary,
    PracticeHistoryView,
    ProjectCompletionHistoryEntry,
    ProjectCompletionView,
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

    def open_practice_history(
        self, request: OpenPracticeHistoryRequest
    ) -> PracticeHistoryView:
        self._validate_practice_context(request)
        try:
            source = self._source.read_practice_history(
                learner_id=request.learner_id,
                placement_id=request.placement_id,
            )
        except LearnerModelError:
            raise
        except Exception as error:
            raise LearnerModelError(
                LearnerModelErrorCode.UNAVAILABLE,
                "Practice history is temporarily unavailable.",
                reference=request.placement_id,
            ) from error
        try:
            projection = derive_practice_history(
                source=source,
                rebuilt_at=self._clock.now(),
            )
        except InvalidCompletionEvidence as error:
            raise LearnerModelError(
                LearnerModelErrorCode.INCONSISTENT_EVIDENCE,
                "Practice evidence could not be reconciled.",
                reference=error.reference,
            ) from error
        try:
            self._repository.replace_practice_history(projection)
        except Exception as error:
            raise LearnerModelError(
                LearnerModelErrorCode.UNAVAILABLE,
                "Practice history is temporarily unavailable.",
                reference=request.placement_id,
            ) from error
        return self._practice_view(projection)

    def open_project_completion(
        self, request: OpenProjectCompletionRequest
    ) -> ProjectCompletionView:
        self._validate_project_context(request)
        try:
            evidence = self._source.list_for_project(
                learner_id=request.learner_id,
                project_id=request.project_id,
            )
        except LearnerModelError:
            raise
        except Exception as error:
            raise LearnerModelError(
                LearnerModelErrorCode.UNAVAILABLE,
                "Project completion evidence is temporarily unavailable.",
                reference=request.project_id,
            ) from error
        try:
            projection = derive_project_completion(
                learner_id=request.learner_id,
                project_id=request.project_id,
                evidence=evidence,
                rebuilt_at=self._clock.now(),
            )
        except InvalidCompletionEvidence as error:
            raise LearnerModelError(
                LearnerModelErrorCode.INCONSISTENT_EVIDENCE,
                "Project completion evidence could not be reconciled.",
                reference=error.reference,
            ) from error
        try:
            self._repository.replace_project_completion(projection)
        except Exception as error:
            raise LearnerModelError(
                LearnerModelErrorCode.UNAVAILABLE,
                "The Project completion view is temporarily unavailable.",
                reference=request.project_id,
            ) from error
        return self._project_view(projection)

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
    def _validate_practice_context(request: OpenPracticeHistoryRequest) -> None:
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
                "Practice placement context is invalid.",
                reference="placement_id",
            )

    @staticmethod
    def _validate_project_context(request: OpenProjectCompletionRequest) -> None:
        try:
            UUID(request.learner_id)
        except (ValueError, AttributeError) as error:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_CONTEXT,
                "Learner context is not authorized.",
                reference="learner",
            ) from error
        value = request.project_id
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
                "Project context is invalid.",
                reference="project_id",
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

    @staticmethod
    def _practice_view(
        projection: PracticeHistoryProjection,
    ) -> PracticeHistoryView:
        return PracticeHistoryView(
            schema_version="1.0.0",
            placement_id=projection.placement_id,
            package_id=projection.package_id,
            package_version=projection.package_version,
            package_digest=projection.package_digest,
            definition_digest=projection.definition_digest,
            practice_id=projection.practice_id,
            practice_version=projection.practice_version,
            attempt_policy_id=projection.attempt_policy_id,
            attempt_policy_version=projection.attempt_policy_version,
            source_digest=projection.source_digest,
            rebuilt_at=projection.rebuilt_at,
            attempts=tuple(
                PracticeHistoryAttempt(
                    attempt_order=attempt.attempt_order,
                    event_id=attempt.event_id,
                    attempt_id=attempt.attempt_id,
                    evidence_id=attempt.evidence_id,
                    submission_id=attempt.submission_id,
                    score=attempt.score,
                    max_score=attempt.max_score,
                    outcome=attempt.outcome,
                    item_summaries=tuple(
                        PracticeHistoryItemSummary(
                            item_id=item.item_id,
                            item_version=item.item_version,
                            item_type=item.item_type,
                            scoring_policy_id=item.scoring_policy_id,
                            scoring_policy_version=(
                                item.scoring_policy_version
                            ),
                            score=item.score,
                            max_score=item.max_score,
                            correct=item.correct,
                            review_reference_ids=item.review_reference_ids,
                        )
                        for item in attempt.item_summaries
                    ),
                    completed_at=attempt.completed_at,
                )
                for attempt in projection.attempts
            ),
        )

    @staticmethod
    def _project_view(
        projection: ProjectCompletionProjection,
    ) -> ProjectCompletionView:
        return ProjectCompletionView(
            project_id=projection.project_id,
            completed=projection.completed,
            completion_meaning=(
                "bounded_project_activity_completed"
                if projection.completed
                else "not_completed"
            ),
            source_digest=projection.source_digest,
            rebuilt_at=projection.rebuilt_at,
            history=tuple(
                ProjectCompletionHistoryEntry(
                    event_id=item.event_id,
                    evidence_id=item.evidence_id,
                    submission_id=item.submission_id,
                    snapshot_id=item.snapshot_id,
                    snapshot_digest=item.snapshot_digest,
                    brief_id=item.brief_id,
                    brief_version=item.brief_version,
                    brief_digest=item.brief_digest,
                    placement_id=item.placement_id,
                    placement_version=item.placement_version,
                    placement_digest=item.placement_digest,
                    policy_id=item.policy_id,
                    policy_version=item.policy_version,
                    milestone_ids=item.milestone_ids,
                    request_fingerprint=item.request_fingerprint,
                    occurrence=item.occurrence,
                    accepted_sequence=item.accepted_sequence,
                    supersedes_submission_id=(
                        item.supersedes_submission_id
                    ),
                    submitted_at=item.submitted_at,
                    occurred_at=item.occurred_at,
                )
                for item in projection.history
            ),
        )
