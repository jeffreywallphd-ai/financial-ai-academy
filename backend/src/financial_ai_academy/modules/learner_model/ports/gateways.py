"""Learner-model evidence-source boundary."""

from __future__ import annotations

from typing import Protocol

from ..domain.models import (
    SourceCompletionEvidence,
    SourcePracticeHistory,
    SourceProjectCompletion,
)


class CompletionEvidenceSourcePort(Protocol):
    def list_for_lesson(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[SourceCompletionEvidence, ...]: ...

    def read_practice_history(
        self, *, learner_id: str, placement_id: str
    ) -> SourcePracticeHistory: ...

    def list_for_project(
        self, *, learner_id: str, project_id: str
    ) -> tuple[SourceProjectCompletion, ...]: ...
