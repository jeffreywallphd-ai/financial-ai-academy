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
class AssessmentPlacement:
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
    created_at: datetime


@dataclass(frozen=True, slots=True)
class CreateAssessmentPlacementRequest:
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


@dataclass(frozen=True, slots=True)
class ResolvePlacedAssessmentRequest:
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

    def create_assessment_placement(
        self, request: CreateAssessmentPlacementRequest
    ) -> AssessmentPlacement: ...

    def resolve_placed_assessment(
        self, request: ResolvePlacedAssessmentRequest
    ) -> AssessmentPlacement: ...
