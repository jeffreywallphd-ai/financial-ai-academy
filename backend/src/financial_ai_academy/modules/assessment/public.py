"""Stable public operations for deterministic placed knowledge checks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from .domain.practice import (
    OrderedPracticeCompletionEvent,
    PracticeDraft,
    PracticePresentation,
    PracticeResult,
    PracticeRetryState,
)


class AssessmentErrorCode(StrEnum):
    INVALID_DEFINITION = "invalid_definition"
    INVALID_SUBMISSION = "invalid_submission"
    UNSUPPORTED_VERSION = "unsupported_version"
    NOT_FOUND = "not_found"
    STALE_REFERENCE = "stale_reference"
    UNKNOWN_OPTION = "unknown_option"
    CONFLICT = "conflict"
    ALREADY_COMPLETED = "already_completed"
    ATTEMPT_LIMIT_REACHED = "attempt_limit_reached"
    UNAUTHORIZED_CONTEXT = "unauthorized_context"
    UNAVAILABLE = "unavailable"


class AssessmentError(RuntimeError):
    def __init__(
        self,
        code: AssessmentErrorCode,
        safe_message: str,
        *,
        reference: str = "assessment",
        diagnostic_code: str | None = None,
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
        self.diagnostic_code = diagnostic_code

    def as_dict(self) -> dict[str, str]:
        value = {
            "code": self.code.value,
            "message": self.safe_message,
            "reference": self.reference,
        }
        if self.diagnostic_code:
            value["diagnostic_code"] = self.diagnostic_code
        return value


@dataclass(frozen=True, slots=True)
class KnowledgeCheckOption:
    option_id: str
    label: str


@dataclass(frozen=True, slots=True)
class KnowledgeCheckPresentation:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    assessment_id: str
    assessment_version: str
    definition_digest: str
    item_type: str
    item_id: str
    item_version: str
    scoring_policy_id: str
    scoring_policy_version: str
    prompt: str
    options: tuple[KnowledgeCheckOption, ...]


@dataclass(frozen=True, slots=True)
class OpenPlacedKnowledgeCheckRequest:
    placement_id: str


@dataclass(frozen=True, slots=True)
class OpenPlacedPracticeRequest:
    placement_id: str


@dataclass(frozen=True, slots=True)
class SubmitPlacedPracticeRequest:
    learner_id: str
    placement_id: str
    submission: bytes


@dataclass(frozen=True, slots=True)
class ReadPlacedPracticeProgressRequest:
    learner_id: str
    placement_id: str


@dataclass(frozen=True, slots=True)
class SavePlacedPracticeDraftRequest:
    learner_id: str
    placement_id: str
    draft: bytes


@dataclass(frozen=True, slots=True)
class ReadCompletedPracticesRequest:
    learner_id: str
    placement_id: str


@dataclass(frozen=True, slots=True)
class SubmitPlacedKnowledgeCheckRequest:
    learner_id: str
    submission_id: str
    placement_id: str
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
    selected_option_id: str


@dataclass(frozen=True, slots=True)
class ReadCompletedKnowledgeChecksRequest:
    learner_id: str
    placement_id: str


@dataclass(frozen=True, slots=True)
class KnowledgeCheckFeedback:
    feedback_id: str
    text: str


@dataclass(frozen=True, slots=True)
class KnowledgeCheckResult:
    attempt_id: str
    evidence_id: str
    learner_id: str
    submission_id: str
    placement_id: str
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
    selected_option_id: str
    score: int
    max_score: int
    correct: bool
    feedback: KnowledgeCheckFeedback
    submitted_at: datetime


@dataclass(frozen=True, slots=True)
class KnowledgeCheckCompletionEvent:
    schema_version: str
    event_id: str
    event_type: str
    event_version: str
    owner: str
    occurred_at: datetime
    idempotency_key: str
    attempt_id: str
    evidence_id: str
    learner_id: str
    placement_id: str
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


class AssessmentOperations(Protocol):
    def open_placed_knowledge_check(
        self, request: OpenPlacedKnowledgeCheckRequest
    ) -> KnowledgeCheckPresentation: ...

    def open_placed_practice(
        self, request: OpenPlacedPracticeRequest
    ) -> PracticePresentation: ...

    def submit_placed_practice(
        self, request: SubmitPlacedPracticeRequest
    ) -> PracticeResult: ...

    def read_placed_practice_draft(
        self, request: ReadPlacedPracticeProgressRequest
    ) -> PracticeDraft | None: ...

    def save_placed_practice_draft(
        self, request: SavePlacedPracticeDraftRequest
    ) -> PracticeDraft: ...

    def read_placed_practice_retry_state(
        self, request: ReadPlacedPracticeProgressRequest
    ) -> PracticeRetryState: ...

    def read_completed_practices(
        self, request: ReadCompletedPracticesRequest
    ) -> tuple[OrderedPracticeCompletionEvent, ...]: ...

    def submit_placed_knowledge_check(
        self, request: SubmitPlacedKnowledgeCheckRequest
    ) -> KnowledgeCheckResult: ...

    def read_completed_knowledge_checks(
        self, request: ReadCompletedKnowledgeChecksRequest
    ) -> tuple[KnowledgeCheckCompletionEvent, ...]: ...
