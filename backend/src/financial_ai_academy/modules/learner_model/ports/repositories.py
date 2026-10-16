"""Learner-model projection persistence boundary."""

from __future__ import annotations

from typing import Protocol

from ..domain.models import LessonCompletionProjection, PracticeHistoryProjection


class CompletionProjectionRepositoryPort(Protocol):
    def replace(self, projection: LessonCompletionProjection) -> None: ...

    def replace_practice_history(
        self, projection: PracticeHistoryProjection
    ) -> None: ...
