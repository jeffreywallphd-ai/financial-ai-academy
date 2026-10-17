"""Stable public Audit reconciliation operation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class AuditErrorCode(StrEnum):
    INVALID_CONTEXT = "invalid_context"
    INCONSISTENT_EVIDENCE = "inconsistent_evidence"
    CONFLICT = "conflict"
    UNAVAILABLE = "unavailable"


class AuditError(RuntimeError):
    def __init__(
        self,
        code: AuditErrorCode,
        safe_message: str,
        *,
        reference: str = "audit",
    ) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )


@dataclass(frozen=True, slots=True)
class ReconcileLessonCompletionAuditRequest:
    learner_id: str
    placement_id: str


@dataclass(frozen=True, slots=True)
class AuditReconciliationReceipt:
    placement_id: str
    reconciled_event_count: int
    source_digest: str


@dataclass(frozen=True, slots=True)
class ReconcileProjectCompletionAuditRequest:
    learner_id: str
    project_id: str


@dataclass(frozen=True, slots=True)
class ProjectAuditReconciliationReceipt:
    project_id: str
    reconciled_event_count: int
    source_digest: str


class AuditOperations(Protocol):
    def reconcile_lesson_completion(
        self, request: ReconcileLessonCompletionAuditRequest
    ) -> AuditReconciliationReceipt: ...

    def reconcile_project_completion(
        self, request: ReconcileProjectCompletionAuditRequest
    ) -> ProjectAuditReconciliationReceipt: ...
