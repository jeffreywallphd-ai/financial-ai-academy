"""Assessment public-operation adapter for Audit reconciliation."""

from __future__ import annotations

from financial_ai_academy.modules.assessment.public import (
    AssessmentOperations,
    ReadCompletedKnowledgeChecksRequest,
    ReadCompletedProjectsRequest,
)

from ..domain.models import AuditableAssessmentEvent, AuditableProjectEvent


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

    def list_for_project(
        self, *, learner_id: str, project_id: str
    ) -> tuple[AuditableProjectEvent, ...]:
        events = self._assessment.read_completed_projects(
            ReadCompletedProjectsRequest(
                learner_id=learner_id,
                project_id=project_id,
            )
        )
        return tuple(
            AuditableProjectEvent(
                schema_version=event.schema_version,
                event_id=event.event_id,
                event_type=event.event_type,
                event_version=event.event_version,
                occurred_at=event.occurred_at,
                evidence_id=event.evidence_id,
                learner_id=event.learner_id,
                submission_id=event.submission_id,
                project_id=event.project_id,
                snapshot_id=event.snapshot_id,
                snapshot_digest=event.snapshot_digest,
                brief_id=event.brief_id,
                brief_version=event.brief_version,
                brief_digest=event.brief_digest,
                placement_id=event.placement_id,
                placement_version=event.placement_version,
                placement_digest=event.placement_digest,
                policy_id=event.policy_id,
                policy_version=event.policy_version,
                milestone_ids=event.milestone_ids,
                request_fingerprint=event.request_fingerprint,
                occurrence=event.occurrence,
                submitted_at=event.submitted_at,
                supersedes_submission_id=event.supersedes_submission_id,
            )
            for event in events
        )
