"""Learner-model projection persistence boundary."""

from __future__ import annotations

from typing import Protocol

from ..domain.models import LessonCompletionProjection


class CompletionProjectionRepositoryPort(Protocol):
    def replace(self, projection: LessonCompletionProjection) -> None: ...
