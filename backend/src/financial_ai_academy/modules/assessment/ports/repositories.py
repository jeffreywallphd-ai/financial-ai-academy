"""Append-oriented Assessment persistence contract."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from ..domain.models import AssessmentSubmissionCandidate
from ..public import KnowledgeCheckResult


class SubmissionConflict(RuntimeError):
    pass


class KnowledgeCheckAlreadyCompleted(RuntimeError):
    pass


class AssessmentRepositoryPort(Protocol):
    def record_submission(
        self, candidate: AssessmentSubmissionCandidate
    ) -> tuple[KnowledgeCheckResult, bool]: ...

    def list_completion_event_documents(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[Mapping[str, Any], ...]: ...

