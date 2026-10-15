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


class LearnerModelOperations(Protocol):
    def open_lesson_completion(
        self, request: OpenLessonCompletionRequest
    ) -> LessonCompletionView: ...
