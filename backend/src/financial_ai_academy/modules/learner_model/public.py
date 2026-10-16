"""Stable public lesson-completion projection operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol


class LearnerModelErrorCode(StrEnum):
    INVALID_CONTEXT = "invalid_context"
    INCONSISTENT_EVIDENCE = "inconsistent_evidence"
    UNAVAILABLE = "unavailable"


class LearnerModelError(RuntimeError):
    def __init__(
        self,
        code: LearnerModelErrorCode,
        safe_message: str,
        *,
        reference: str = "completion",
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
class OpenLessonCompletionRequest:
    learner_id: str
    placement_id: str


@dataclass(frozen=True, slots=True)
class LessonCompletionHistoryEntry:
    event_id: str
    attempt_id: str
    evidence_id: str
    package_id: str
    package_version: str
    package_digest: str
    assessment_id: str
    assessment_version: str
    definition_digest: str
    item_id: str
    item_version: str
    scoring_policy_id: str
    scoring_policy_version: str
    score: int
    max_score: int
    completed_at: datetime


@dataclass(frozen=True, slots=True)
class LessonCompletionView:
    placement_id: str
    completed: bool
    completion_meaning: str
    source_digest: str
    rebuilt_at: datetime
    history: tuple[LessonCompletionHistoryEntry, ...]


@dataclass(frozen=True, slots=True)
class OpenPracticeHistoryRequest:
    learner_id: str
    placement_id: str


@dataclass(frozen=True, slots=True)
class PracticeHistoryItemSummary:
    item_id: str
    item_version: str
    item_type: str
    scoring_policy_id: str
    scoring_policy_version: str
    score: int
    max_score: int
    correct: bool
    review_reference_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PracticeHistoryAttempt:
    attempt_order: int
    event_id: str
    attempt_id: str
    evidence_id: str
    submission_id: str
    score: int
    max_score: int
    outcome: str
    item_summaries: tuple[PracticeHistoryItemSummary, ...]
    completed_at: datetime


@dataclass(frozen=True, slots=True)
class PracticeHistoryView:
    schema_version: str
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    definition_digest: str
    practice_id: str
    practice_version: str
    attempt_policy_id: str
    attempt_policy_version: str
    source_digest: str
    rebuilt_at: datetime
    attempts: tuple[PracticeHistoryAttempt, ...]


class LearnerModelOperations(Protocol):
    def open_lesson_completion(
        self, request: OpenLessonCompletionRequest
    ) -> LessonCompletionView: ...

    def open_practice_history(
        self, request: OpenPracticeHistoryRequest
    ) -> PracticeHistoryView: ...
