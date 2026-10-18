"""Append-oriented Audit persistence boundary."""

from __future__ import annotations

from typing import Protocol

from ..domain.models import (
    AssessmentCompletionAuditRecord,
    ProjectCompletionAuditRecord,
)


class AuditRecordConflict(RuntimeError):
    pass


class AuditRepositoryPort(Protocol):
    def append_assessment_completion_records(
        self, records: tuple[AssessmentCompletionAuditRecord, ...]
    ) -> None: ...

    def append_project_completion_records(
        self, records: tuple[ProjectCompletionAuditRecord, ...]
    ) -> None: ...

    def read_assessment_completion_record(
        self,
        *,
        actor_id: str,
        placement_id: str,
        evidence_id: str,
    ) -> AssessmentCompletionAuditRecord | None: ...
