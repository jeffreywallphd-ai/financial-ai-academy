"""Learner-model projection persistence boundary."""

from __future__ import annotations

from typing import Protocol

from ..domain.models import (
    LessonCompletionProjection,
    PracticeHistoryProjection,
    ProjectCompletionProjection,
)
from ..domain.preferences import (
    LearnerPreferenceProfile,
    PreferenceChange,
    PreferenceHistory,
)
from ..domain.presentation_preferences import (
    PresentationPreferenceChange,
    PresentationPreferenceHistory,
    PresentationPreferenceProfile,
)


class LearnerPreferenceIdempotencyConflict(RuntimeError):
    pass


class LearnerPreferenceRevisionConflict(RuntimeError):
    pass


class LearnerPreferenceRepositoryPort(Protocol):
    def get_preferences(
        self, learner_id: str
    ) -> LearnerPreferenceProfile | None: ...

    def get_preference_history(
        self, learner_id: str
    ) -> PreferenceHistory | None: ...

    def get_preference_replay(
        self, learner_id: str, idempotency_key: str
    ) -> tuple[str, LearnerPreferenceProfile] | None: ...

    def save_preferences_if_revision(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_revision: int,
        profile: LearnerPreferenceProfile,
        change: PreferenceChange,
    ) -> LearnerPreferenceProfile: ...


class PresentationPreferenceRepositoryPort(Protocol):
    def get_presentation_preferences(
        self, learner_id: str
    ) -> PresentationPreferenceProfile | None: ...

    def get_presentation_preference_history(
        self, learner_id: str
    ) -> PresentationPreferenceHistory | None: ...

    def get_presentation_preference_replay(
        self, learner_id: str, idempotency_key: str
    ) -> tuple[str, PresentationPreferenceProfile] | None: ...

    def save_presentation_preferences_if_revision(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_revision: int,
        profile: PresentationPreferenceProfile,
        change: PresentationPreferenceChange,
    ) -> PresentationPreferenceProfile: ...


class CompletionProjectionRepositoryPort(Protocol):
    def replace(self, projection: LessonCompletionProjection) -> None: ...

    def replace_practice_history(
        self, projection: PracticeHistoryProjection
    ) -> None: ...

    def replace_project_completion(
        self, projection: ProjectCompletionProjection
    ) -> None: ...
