"""Persistence contract owned by Curriculum."""

from __future__ import annotations

from typing import Protocol

from ..public import AssessmentPlacement, LessonPlacement


class PlacementConflict(RuntimeError):
    pass


class CurriculumRepositoryPort(Protocol):
    def get(self, placement_id: str) -> LessonPlacement | None: ...

    def save_if_absent(
        self, placement: LessonPlacement
    ) -> tuple[LessonPlacement, bool]: ...

    def get_assessment(
        self, placement_id: str
    ) -> AssessmentPlacement | None: ...

    def save_assessment_if_absent(
        self, placement: AssessmentPlacement
    ) -> tuple[AssessmentPlacement, bool]: ...
