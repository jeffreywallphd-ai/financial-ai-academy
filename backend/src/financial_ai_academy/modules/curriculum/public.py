"""Stable public types for exact-version Curriculum placement and reading."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
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


class OpportunityKind(StrEnum):
    COURSE = "course"
    LESSON = "lesson"
    LAB = "lab"
    PROJECT = "project"


class OpportunityLevel(StrEnum):
    INTRODUCTORY = "introductory"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class OpportunityAvailability(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    PLANNED = "planned"


class DiscoveryErrorCode(StrEnum):
    INVALID_RECORD = "invalid_record"
    IMMUTABLE_CONFLICT = "immutable_conflict"
    STALE_SOURCE = "stale_source"
    UNAVAILABLE = "unavailable"


class DiscoveryError(RuntimeError):
    """Bounded discovery error without persistence or provider details."""

    def __init__(
        self,
        code: DiscoveryErrorCode,
        message: str,
        *,
        reference: str = "learning-opportunity",
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code.value,
            "message": self.message,
            "reference": self.reference,
        }


@dataclass(frozen=True, slots=True)
class RegisterLessonOpportunityRequest:
    opportunity_id: str
    placement_id: str
    summary: str
    topics: tuple[str, ...]
    level: OpportunityLevel
    estimated_minutes: int
    prerequisite_summary: str
    availability: OpportunityAvailability
    availability_reason: str


@dataclass(frozen=True, slots=True)
class LessonOpportunityClassification:
    opportunity_id: str
    placement_id: str
    summary: str
    topics: tuple[str, ...]
    level: OpportunityLevel
    estimated_minutes: int
    prerequisite_summary: str
    availability: OpportunityAvailability
    availability_reason: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class RebuildLearningOpportunityProjectionRequest:
    pass


@dataclass(frozen=True, slots=True)
class BrowseLearningOpportunitiesRequest:
    pass


@dataclass(frozen=True, slots=True)
class DiscoveryProvenance:
    published_by: str
    published_at: datetime
    content_reviewed_on: date
    educational_use_notice: str


@dataclass(frozen=True, slots=True)
class LearningOpportunityRecord:
    schema_version: str
    opportunity_id: str
    placement_id: str
    destination: str
    kind: OpportunityKind
    title: str
    summary: str
    objectives: tuple[str, ...]
    topics: tuple[str, ...]
    level: OpportunityLevel
    estimated_minutes: int
    prerequisite_summary: str
    availability: OpportunityAvailability
    availability_reason: str
    package_id: str
    package_version: str
    package_digest: str
    provenance: DiscoveryProvenance
    source_fingerprint: str
    projected_at: datetime


@dataclass(frozen=True, slots=True)
class LearningOpportunityBrowse:
    schema_version: str
    projection_generation: str
    projected_at: datetime
    records: tuple[LearningOpportunityRecord, ...]


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

    def register_lesson_opportunity(
        self, request: RegisterLessonOpportunityRequest
    ) -> LessonOpportunityClassification: ...

    def rebuild_learning_opportunity_projection(
        self, request: RebuildLearningOpportunityProjectionRequest
    ) -> LearningOpportunityBrowse: ...

    def browse_learning_opportunities(
        self, request: BrowseLearningOpportunitiesRequest
    ) -> LearningOpportunityBrowse: ...
