"""Append-oriented Assessment persistence contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Protocol

from ..domain.models import AssessmentSubmissionCandidate
from ..domain.practice import (
    PracticeDraft,
    PracticeDraftSave,
    PracticeResult,
    PracticeScope,
    PracticeSubmissionCandidate,
)
from ..public import KnowledgeCheckResult


class SubmissionConflict(RuntimeError):
    pass


class KnowledgeCheckAlreadyCompleted(RuntimeError):
    pass


class PracticeSubmissionConflict(RuntimeError):
    pass


class PracticeAlreadyCompleted(RuntimeError):
    pass


class PracticeAttemptLimitReached(RuntimeError):
    pass


class PracticeDraftConflict(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class StoredPracticeCompletionEvent:
    event_id: str
    attempt_id: str
    evidence_id: str
    submission_id: str
    attempt_order: int
    document: Mapping[str, Any]


class AssessmentRepositoryPort(Protocol):
    def record_submission(
        self, candidate: AssessmentSubmissionCandidate
    ) -> tuple[KnowledgeCheckResult, bool]: ...

    def list_completion_event_documents(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[Mapping[str, Any], ...]: ...

    def record_practice_submission(
        self, candidate: PracticeSubmissionCandidate, *, max_attempts: int
    ) -> tuple[PracticeResult, bool]: ...

    def read_practice_draft(
        self, *, learner_id: str, scope: PracticeScope
    ) -> PracticeDraft | None: ...

    def save_practice_draft(
        self,
        *,
        learner_id: str,
        draft: PracticeDraftSave,
        saved_at: datetime,
    ) -> PracticeDraft: ...

    def count_practice_attempts(
        self, *, learner_id: str, scope: PracticeScope
    ) -> int: ...

    def list_practice_completion_event_documents(
        self, *, learner_id: str, scope: PracticeScope
    ) -> tuple[StoredPracticeCompletionEvent, ...]: ...

