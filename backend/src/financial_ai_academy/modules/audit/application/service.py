"""Idempotent Audit reconciliation for Assessment completion events."""

from __future__ import annotations

from uuid import UUID

from ..domain.models import (
    InvalidAuditEvidence,
    derive_assessment_audit_batch,
    derive_project_audit_batch,
)
from ..ports.gateways import AssessmentAuditEventSourcePort
from ..ports.repositories import AuditRecordConflict, AuditRepositoryPort
from ..ports.system import ClockPort
from ..public import (
    AuditError,
    AuditErrorCode,
    AuditReconciliationReceipt,
    ProjectAuditReconciliationReceipt,
    ReconcileLessonCompletionAuditRequest,
    ReconcileProjectCompletionAuditRequest,
)


class AuditService:
    def __init__(
        self,
        source: AssessmentAuditEventSourcePort,
        repository: AuditRepositoryPort,
        clock: ClockPort,
    ) -> None:
        self._source = source
        self._repository = repository
        self._clock = clock

    def reconcile_lesson_completion(
        self, request: ReconcileLessonCompletionAuditRequest
    ) -> AuditReconciliationReceipt:
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
        return AuditReconciliationReceipt(
            placement_id=request.placement_id,
            reconciled_event_count=len(batch.records),
            source_digest=batch.source_digest,
        )

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
                "Project context is invalid.",
                reference="project_id",
            )
