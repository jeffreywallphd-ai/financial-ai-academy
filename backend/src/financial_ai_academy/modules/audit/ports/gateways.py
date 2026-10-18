"""Audit source-event boundary."""

from __future__ import annotations

from typing import Protocol

from ..domain.models import AuditableAssessmentEvent, AuditableProjectEvent
from ..domain.learning_lineage import ContentLineageFragment


class AssessmentAuditEventSourcePort(Protocol):
    def list_for_lesson(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[AuditableAssessmentEvent, ...]: ...

    def list_for_project(
        self, *, learner_id: str, project_id: str
    ) -> tuple[AuditableProjectEvent, ...]: ...


class ContentLearningLineageSourcePort(Protocol):
    def read_lesson(
        self,
        *,
        package_id: str,
        package_version: str,
        package_digest: str,
    ) -> ContentLineageFragment: ...
