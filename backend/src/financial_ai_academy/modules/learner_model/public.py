"""Stable public lesson-completion projection operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from .domain.preferences import (
    LearnerPreferenceProfile,
    PreferenceExport,
    PreferenceHistory,
    PreferenceMutationIntent,
)
from .domain.presentation_preferences import (
    PresentationPreferenceExport,
    PresentationPreferenceHistory,
    PresentationPreferenceMutationIntent,
    PresentationPreferenceProfile,
)


class LearnerModelErrorCode(StrEnum):
    INVALID_REQUEST = "invalid_request"
    INVALID_CONTEXT = "invalid_context"
    INCONSISTENT_EVIDENCE = "inconsistent_evidence"
    IMMUTABLE_CONFLICT = "immutable_conflict"
    STALE_REVISION = "stale_revision"
    NOT_FOUND = "not_found"
    PREFERENCE_LIMIT = "preference_limit"
    INTEGRITY_FAILURE = "integrity_failure"
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


@dataclass(frozen=True, slots=True)
class OpenProjectCompletionRequest:
    learner_id: str
    project_id: str


@dataclass(frozen=True, slots=True)
class OpenLearnerPreferencesRequest:
    learner_id: str


@dataclass(frozen=True, slots=True)
class MutateLearnerPreferencesRequest:
    learner_id: str
    intent: PreferenceMutationIntent


@dataclass(frozen=True, slots=True)
class ReadLearnerPreferenceHistoryRequest:
    learner_id: str


@dataclass(frozen=True, slots=True)
class ExportLearnerPreferencesRequest:
    learner_id: str


@dataclass(frozen=True, slots=True)
class OpenPresentationPreferencesRequest:
    learner_id: str


@dataclass(frozen=True, slots=True)
class MutatePresentationPreferencesRequest:
    learner_id: str
    intent: PresentationPreferenceMutationIntent


@dataclass(frozen=True, slots=True)
class ReadPresentationPreferenceHistoryRequest:
    learner_id: str


@dataclass(frozen=True, slots=True)
class ExportPresentationPreferencesRequest:
    learner_id: str


@dataclass(frozen=True, slots=True)
class ProjectCompletionHistoryEntry:
    event_id: str
    evidence_id: str
    submission_id: str
    snapshot_id: str
    snapshot_digest: str
    brief_id: str
    brief_version: str
    brief_digest: str
    placement_id: str
    placement_version: str
    placement_digest: str
    policy_id: str
    policy_version: str
    milestone_ids: tuple[str, ...]
    request_fingerprint: str
    occurrence: int
    accepted_sequence: int
    supersedes_submission_id: str | None
    submitted_at: datetime
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class ProjectCompletionView:
    project_id: str
    completed: bool
    completion_meaning: str
    source_digest: str
    rebuilt_at: datetime
    history: tuple[ProjectCompletionHistoryEntry, ...]


class LearnerModelOperations(Protocol):
    def open_lesson_completion(
        self, request: OpenLessonCompletionRequest
    ) -> LessonCompletionView: ...

    def open_practice_history(
        self, request: OpenPracticeHistoryRequest
    ) -> PracticeHistoryView: ...

    def open_project_completion(
        self, request: OpenProjectCompletionRequest
    ) -> ProjectCompletionView: ...

    def open_preferences(
        self, request: OpenLearnerPreferencesRequest
    ) -> LearnerPreferenceProfile: ...

    def mutate_preferences(
        self, request: MutateLearnerPreferencesRequest
    ) -> LearnerPreferenceProfile: ...

    def read_preference_history(
        self, request: ReadLearnerPreferenceHistoryRequest
    ) -> PreferenceHistory: ...

    def export_preferences(
        self, request: ExportLearnerPreferencesRequest
    ) -> PreferenceExport: ...

    def open_presentation_preferences(
        self, request: OpenPresentationPreferencesRequest
    ) -> PresentationPreferenceProfile: ...

    def mutate_presentation_preferences(
        self, request: MutatePresentationPreferencesRequest
    ) -> PresentationPreferenceProfile: ...

    def read_presentation_preference_history(
        self, request: ReadPresentationPreferenceHistoryRequest
    ) -> PresentationPreferenceHistory: ...

    def export_presentation_preferences(
        self, request: ExportPresentationPreferencesRequest
    ) -> PresentationPreferenceExport: ...
