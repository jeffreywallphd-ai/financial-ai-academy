"""Stable public types for exact-version Curriculum placement and reading."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from financial_ai_academy.modules.content.public import (
    BodyNode,
    EducationalSource,
    PassiveAsset,
    PublicationProvenance,
)


@dataclass(frozen=True, slots=True)
class LessonPlacement:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class CreateLessonPlacementRequest:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str


@dataclass(frozen=True, slots=True)
class OpenPlacedLessonRequest:
    placement_id: str


@dataclass(frozen=True, slots=True)
class LessonReadingResult:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    title: str
    objectives: tuple[str, ...]
    body: tuple[BodyNode, ...]
    sources: tuple[EducationalSource, ...]
    assets: tuple[PassiveAsset, ...]
    provenance: PublicationProvenance


class CurriculumOperations(Protocol):
    def create_lesson_placement(
        self, request: CreateLessonPlacementRequest
    ) -> LessonPlacement: ...

    def open_placed_lesson(
        self, request: OpenPlacedLessonRequest
    ) -> LessonReadingResult: ...
