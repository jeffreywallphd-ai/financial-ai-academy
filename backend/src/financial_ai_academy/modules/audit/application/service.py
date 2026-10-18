"""Idempotent Audit reconciliation for Assessment completion events."""

from __future__ import annotations

from uuid import UUID

from ..domain.models import (
    AssessmentAuditBatch,
    AuditableAssessmentEvent,
    InvalidAuditEvidence,
    derive_assessment_audit_batch,
    derive_project_audit_batch,
)
from ..domain.learning_lineage import (
    InvalidLearningLineage,
    compose_knowledge_check_completion_lineage,
    compose_published_lesson_lineage,
)
from ..domain.provenance import LineageView
from ..ports.gateways import (
    AssessmentAuditEventSourcePort,
    ContentLearningLineageSourcePort,
)
from ..ports.repositories import AuditRecordConflict, AuditRepositoryPort
from ..ports.system import ClockPort
from ..public import (
    AuditError,
    AuditErrorCode,
    AuditReconciliationReceipt,
    ProjectAuditReconciliationReceipt,
    ReadKnowledgeCheckCompletionLineageRequest,
    ReadPublishedLessonLineageRequest,
    ReconcileLessonCompletionAuditRequest,
    ReconcileProjectCompletionAuditRequest,
)


class AuditService:
    def __init__(
        self,
        source: AssessmentAuditEventSourcePort,
        repository: AuditRepositoryPort,
        clock: ClockPort,
        content_lineage: ContentLearningLineageSourcePort | None = None,
    ) -> None:
        self._source = source
        self._repository = repository
        self._clock = clock
        self._content_lineage = content_lineage

    def reconcile_lesson_completion(
        self, request: ReconcileLessonCompletionAuditRequest
    ) -> AuditReconciliationReceipt:
        _events, batch = self._reconcile_lesson_records(request)
        return AuditReconciliationReceipt(
            placement_id=request.placement_id,
            reconciled_event_count=len(batch.records),
            source_digest=batch.source_digest,
        )

    def read_published_lesson_lineage(
        self, request: ReadPublishedLessonLineageRequest
    ) -> LineageView:
        if self._content_lineage is None:
            raise AuditError(
                AuditErrorCode.UNAVAILABLE,
                "Learning lineage is temporarily unavailable.",
                reference="published_lesson",
            )
        try:
            fragment = self._content_lineage.read_lesson(
                package_id=request.package_id,
                package_version=request.package_version,
                package_digest=request.package_digest,
            )
            return compose_published_lesson_lineage(fragment)
        except AuditError:
            raise
        except InvalidLearningLineage as error:
            raise AuditError(
                AuditErrorCode.INCONSISTENT_EVIDENCE,
                "Learning lineage facts are inconsistent.",
                reference=error.reference,
            ) from error
        except Exception as error:
            raise AuditError(
                AuditErrorCode.UNAVAILABLE,
                "Learning lineage is temporarily unavailable.",
                reference="published_lesson",
            ) from error

    def read_knowledge_check_completion_lineage(
        self, request: ReadKnowledgeCheckCompletionLineageRequest
    ) -> LineageView:
        context = ReconcileLessonCompletionAuditRequest(
            learner_id=request.learner_id,
            placement_id=request.placement_id,
        )
        if request.occurrence < 1 or not request.evidence_id:
            raise AuditError(
                AuditErrorCode.INVALID_CONTEXT,
                "Completion lineage context is invalid.",
                reference="completion",
            )
        events, batch = self._reconcile_lesson_records(context)
        events_by_id = {event.event_id: event for event in events}
        selected = None
        for occurrence, record in enumerate(batch.records, start=1):
            if occurrence == request.occurrence and record.evidence_id == request.evidence_id:
                selected = (events_by_id.get(record.event_id), record)
                break
        if selected is None or selected[0] is None:
            raise AuditError(
                AuditErrorCode.INVALID_CONTEXT,
                "Completion lineage context is invalid.",
                reference="completion",
            )
        if self._content_lineage is None:
            raise AuditError(
                AuditErrorCode.UNAVAILABLE,
                "Learning lineage is temporarily unavailable.",
                reference="completion",
            )
        event, _derived = selected
        try:
            retained = self._repository.read_assessment_completion_record(
                actor_id=request.learner_id,
                placement_id=request.placement_id,
                evidence_id=request.evidence_id,
            )
            if retained is None:
                raise InvalidLearningLineage("audit_reference")
            content = self._content_lineage.read_lesson(
                package_id=event.package_id,
                package_version=event.package_version,
                package_digest=event.package_digest,
            )
            return compose_knowledge_check_completion_lineage(
                event=event,
                retained=retained,
                occurrence=request.occurrence,
                content=content,
            )
        except AuditError:
            raise
        except InvalidLearningLineage as error:
            raise AuditError(
                AuditErrorCode.INCONSISTENT_EVIDENCE,
                "Learning lineage facts are inconsistent.",
                reference=error.reference,
            ) from error
        except Exception as error:
            raise AuditError(
                AuditErrorCode.UNAVAILABLE,
                "Learning lineage is temporarily unavailable.",
                reference="completion",
            ) from error

    def reconcile_project_completion(
        self, request: ReconcileProjectCompletionAuditRequest
    ) -> ProjectAuditReconciliationReceipt:
        self._validate_project_context(request)
        try:
            events = self._source.list_for_project(
                learner_id=request.learner_id,
                project_id=request.project_id,
            )
        except AuditError:
            raise
        except Exception as error:
            raise AuditError(
                AuditErrorCode.UNAVAILABLE,
                "Audit source evidence is temporarily unavailable.",
                reference=request.project_id,
            ) from error
        try:
            batch = derive_project_audit_batch(
                learner_id=request.learner_id,
                project_id=request.project_id,
                events=events,
                recorded_at=self._clock.now(),
            )
        except InvalidAuditEvidence as error:
            raise AuditError(
                AuditErrorCode.INCONSISTENT_EVIDENCE,
                "Audit source evidence could not be reconciled.",
                reference=error.reference,
            ) from error
        try:
            self._repository.append_project_completion_records(batch.records)
        except AuditRecordConflict as error:
            raise AuditError(
                AuditErrorCode.CONFLICT,
                "An Audit event identity conflicts with retained evidence.",
                reference="event_id",
            ) from error
        except Exception as error:
            raise AuditError(
                AuditErrorCode.UNAVAILABLE,
                "Audit evidence is temporarily unavailable.",
                reference=request.project_id,
            ) from error
        return ProjectAuditReconciliationReceipt(
            project_id=request.project_id,
            reconciled_event_count=len(batch.records),
            source_digest=batch.source_digest,
        )

    def _reconcile_lesson_records(
        self, request: ReconcileLessonCompletionAuditRequest
    ) -> tuple[tuple[AuditableAssessmentEvent, ...], AssessmentAuditBatch]:
        self._validate_context(request)
        try:
            events = self._source.list_for_lesson(
                learner_id=request.learner_id,
                placement_id=request.placement_id,
            )
        except AuditError:
            raise
        except Exception as error:
            raise AuditError(
                AuditErrorCode.UNAVAILABLE,
                "Audit source evidence is temporarily unavailable.",
                reference=request.placement_id,
            ) from error
        try:
            batch = derive_assessment_audit_batch(
                learner_id=request.learner_id,
                placement_id=request.placement_id,
                events=events,
                recorded_at=self._clock.now(),
            )
        except InvalidAuditEvidence as error:
            raise AuditError(
                AuditErrorCode.INCONSISTENT_EVIDENCE,
                "Audit source evidence could not be reconciled.",
                reference=error.reference,
            ) from error
        try:
            self._repository.append_assessment_completion_records(batch.records)
        except AuditRecordConflict as error:
            raise AuditError(
                AuditErrorCode.CONFLICT,
                "An Audit event identity conflicts with retained evidence.",
                reference="event_id",
            ) from error
        except Exception as error:
            raise AuditError(
                AuditErrorCode.UNAVAILABLE,
                "Audit evidence is temporarily unavailable.",
                reference=request.placement_id,
            ) from error
        return events, batch

    @staticmethod
    def _validate_context(
        request: ReconcileLessonCompletionAuditRequest,
    ) -> None:
        try:
            UUID(request.learner_id)
        except (ValueError, AttributeError) as error:
            raise AuditError(
                AuditErrorCode.INVALID_CONTEXT,
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
            raise AuditError(
                AuditErrorCode.INVALID_CONTEXT,
                "Lesson placement context is invalid.",
                reference="placement_id",
            )

    @staticmethod
    def _validate_project_context(
        request: ReconcileProjectCompletionAuditRequest,
    ) -> None:
        try:
            UUID(request.learner_id)
        except (ValueError, AttributeError) as error:
            raise AuditError(
                AuditErrorCode.INVALID_CONTEXT,
                "Learner context is not authorized.",
                reference="learner",
            ) from error
        value = request.project_id
        if (
            not 1 <= len(value) <= 128
            or not value[0].isalnum()
            or not all(
                character.islower()
                or character.isdigit()
                or character in "._-"
                for character in value
            )
        ):
            raise AuditError(
                AuditErrorCode.INVALID_CONTEXT,
                "Project context is invalid.",
                reference="project_id",
            )
