"""Assessment public-operation adapter for Audit reconciliation."""

from __future__ import annotations

from financial_ai_academy.modules.assessment.public import (
    AssessmentOperations,
    ReadCompletedKnowledgeChecksRequest,
)

from ..domain.models import AuditableAssessmentEvent


class AssessmentAuditEventSource:
    def __init__(self, assessment: AssessmentOperations) -> None:
        self._assessment = assessment

    def list_for_lesson(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[AuditableAssessmentEvent, ...]:
        events = self._assessment.read_completed_knowledge_checks(
            ReadCompletedKnowledgeChecksRequest(
                learner_id=learner_id,
                placement_id=placement_id,
            )
        )
        return tuple(
            AuditableAssessmentEvent(
                schema_version=event.schema_version,
                event_id=event.event_id,
                event_type=event.event_type,
                event_version=event.event_version,
                owner=event.owner,
                occurred_at=event.occurred_at,
                idempotency_key=event.idempotency_key,
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
