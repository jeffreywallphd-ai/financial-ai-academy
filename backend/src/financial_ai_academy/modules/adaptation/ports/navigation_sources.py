"""Provider-neutral inputs required to compose navigation state."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from financial_ai_academy.modules.curriculum.public import CurriculumGraph

from ..domain.models import CompletionState


class NavigationSourceErrorCode(StrEnum):
    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"


class NavigationSourceError(RuntimeError):
    """Bounded source failure without upstream payloads or storage details."""

    def __init__(self, code: NavigationSourceErrorCode) -> None:
        super().__init__("Navigation-state source could not be read.")
        self.code = code


@dataclass(frozen=True, slots=True)
class ExactCurriculumGraphRequest:
    curriculum_id: str
    curriculum_version: str


@dataclass(frozen=True, slots=True)
class LessonSourceReference:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str


@dataclass(frozen=True, slots=True)
class AssessmentSourceReference:
    placement_id: str
    assessment_id: str
    assessment_version: str
    definition_digest: str


@dataclass(frozen=True, slots=True)
class LessonCompletionObservation:
    state: CompletionState
    source_digest: str


class CurriculumNavigationSourcePort(Protocol):
    def open_graph(
        self, request: ExactCurriculumGraphRequest
    ) -> CurriculumGraph: ...

    def lesson_is_available(
        self, reference: LessonSourceReference
    ) -> bool: ...

    def assessment_is_available(
        self, reference: AssessmentSourceReference
    ) -> bool: ...


class LessonCompletionSourcePort(Protocol):
    def observe_lesson_completion(
        self,
        *,
        learner_id: str,
        placement_id: str,
        fallback_digest: str,
    ) -> LessonCompletionObservation: ...


class NavigationClockPort(Protocol):
    def now(self) -> datetime: ...
