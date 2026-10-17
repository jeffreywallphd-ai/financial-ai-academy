"""Audit source-event boundary."""

from __future__ import annotations

from typing import Protocol

from ..domain.models import AuditableAssessmentEvent, AuditableProjectEvent


class AssessmentAuditEventSourcePort(Protocol):
    def list_for_lesson(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[AuditableAssessmentEvent, ...]: ...

    def list_for_project(
        self, *, learner_id: str, project_id: str
    ) -> tuple[AuditableProjectEvent, ...]: ...
