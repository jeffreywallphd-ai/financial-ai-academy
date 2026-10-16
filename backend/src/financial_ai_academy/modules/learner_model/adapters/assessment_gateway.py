"""Assessment public-operation adapter for completion replay."""

from __future__ import annotations

from financial_ai_academy.modules.assessment.public import (
    AssessmentOperations,
    ReadCompletedKnowledgeChecksRequest,
    ReadCompletedPracticesRequest,
)

from ..domain.models import (
    SourceCompletionEvidence,
    SourcePracticeAttempt,
    SourcePracticeHistory,
    SourcePracticeItemSummary,
)


class AssessmentCompletionEvidenceSource:
    def __init__(
        self, assessment: AssessmentOperations
    ) -> None:
        self._assessment = assessment

    def list_for_lesson(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[SourceCompletionEvidence, ...]:
        events = self._assessment.read_completed_knowledge_checks(
            ReadCompletedKnowledgeChecksRequest(
                learner_id=learner_id,
                placement_id=placement_id,
            )
        )
        return tuple(
            SourceCompletionEvidence(
                event_id=event.event_id,
                event_version=event.event_version,
                occurred_at=event.occurred_at,
                attempt_id=event.attempt_id,
                evidence_id=event.evidence_id,
                learner_id=event.learner_id,
                placement_id=event.placement_id,
                package_id=event.package_id,
                package_version=event.package_version,
                package_digest=event.package_digest,
                assessment_id=event.assessment_id,
                assessment_version=event.assessment_version,
                definition_digest=event.definition_digest,
                item_id=event.item_id,
                item_version=event.item_version,
                scoring_policy_id=event.scoring_policy_id,
                scoring_policy_version=event.scoring_policy_version,
                score=event.score,
                max_score=event.max_score,
                completed_at=event.completed_at,
            )
            for event in events
        )

    def read_practice_history(
        self, *, learner_id: str, placement_id: str
    ) -> SourcePracticeHistory:
        source = self._assessment.read_practice_history_source(
            ReadCompletedPracticesRequest(
                learner_id=learner_id,
                placement_id=placement_id,
            )
        )
        return SourcePracticeHistory(
            learner_id=source.learner_id,
            placement_id=source.placement_id,
            package_id=source.package_id,
            package_version=source.package_version,
            package_digest=source.package_digest,
            definition_digest=source.definition_digest,
            practice_id=source.practice_id,
            practice_version=source.practice_version,
            attempt_policy_id=source.attempt_policy_id,
            attempt_policy_version=source.attempt_policy_version,
            attempts=tuple(
                SourcePracticeAttempt(
                    attempt_order=attempt.attempt_order,
                    event_id=attempt.event_id,
                    attempt_id=attempt.attempt_id,
                    evidence_id=attempt.evidence_id,
                    learner_id=attempt.learner_id,
                    submission_id=attempt.submission_id,
                    placement_id=attempt.placement_id,
                    package_id=attempt.package_id,
                    package_version=attempt.package_version,
                    package_digest=attempt.package_digest,
                    definition_digest=attempt.definition_digest,
                    practice_id=attempt.practice_id,
                    practice_version=attempt.practice_version,
                    attempt_policy_id=attempt.attempt_policy_id,
                    attempt_policy_version=attempt.attempt_policy_version,
                    score=attempt.score,
                    max_score=attempt.max_score,
                    outcome=attempt.outcome,
                    item_summaries=tuple(
                        SourcePracticeItemSummary(
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
                for attempt in source.attempts
            ),
        )
