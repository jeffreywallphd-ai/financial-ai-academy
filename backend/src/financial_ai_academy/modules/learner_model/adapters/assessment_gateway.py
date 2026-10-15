"""Assessment public-operation adapter for completion replay."""

from __future__ import annotations

from financial_ai_academy.modules.assessment.public import (
    AssessmentOperations,
    ReadCompletedKnowledgeChecksRequest,
)

from ..domain.models import SourceCompletionEvidence


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
