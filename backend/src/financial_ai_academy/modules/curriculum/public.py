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
from financial_ai_academy.modules.curriculum.domain.models import (
    AssessmentActivityReference,
    CurriculumActivity,
    CurriculumActivityKind,
    CurriculumActivityReference,
    CurriculumBranch,
    CurriculumBranchKind,
    CurriculumCompetency,
    CurriculumGraph,
    CurriculumGraphError,
    CurriculumGraphErrorCode,
    CurriculumObjective,
    CurriculumPresentationOrder,
    CurriculumRelationship,
    CurriculumRelationshipKind,
    LessonActivityReference,
    canonical_curriculum_graph_bytes,
    curriculum_graph_digest,
    curriculum_graph_from_mapping,
    curriculum_graph_payload,
    validate_curriculum_graph,
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
class PracticePlacement:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    practice_id: str
    practice_version: str
    definition_digest: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class CreatePracticePlacementRequest:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    practice_id: str
    practice_version: str
    definition_digest: str


@dataclass(frozen=True, slots=True)
class ResolvePlacedPracticeRequest:
    placement_id: str


@dataclass(frozen=True, slots=True)
class ProjectBriefPlacement:
    placement_id: str
    placement_version: str
    placement_digest: str
    curriculum_id: str
    curriculum_version: str
    curriculum_digest: str
    package_id: str
    package_version: str
    package_digest: str
    brief_id: str
    brief_version: str
    brief_digest: str
    project_brief_schema_version: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class CreateProjectBriefPlacementRequest:
    placement_id: str
    placement_version: str
    curriculum_id: str
    curriculum_version: str
    curriculum_digest: str
    package_id: str
    package_version: str
    package_digest: str
    brief_id: str
    brief_version: str
    brief_digest: str
    project_brief_schema_version: str


@dataclass(frozen=True, slots=True)
class ResolveProjectBriefPlacementRequest:
    placement_id: str


class PracticeReviewState(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class PracticeReviewUnavailableReason(StrEnum):
    MAPPING_NOT_FOUND = "mapping_not_found"
    DESTINATION_NOT_AVAILABLE = "destination_not_available"
    VERSION_MISMATCH = "version_mismatch"


class PracticeReviewErrorCode(StrEnum):
    INVALID_RECORD = "invalid_record"
    IMMUTABLE_CONFLICT = "immutable_conflict"
    UNAVAILABLE = "unavailable"


class PracticeReviewError(RuntimeError):
    """Bounded review-target error without storage details."""

    def __init__(
        self,
        code: PracticeReviewErrorCode,
        message: str,
        *,
        reference: str = "practice-review",
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
class PracticeReviewResource:
    resource_id: str
    resource_version: str
    resource_digest: str
    resource_title: str


@dataclass(frozen=True, slots=True)
class PracticeReviewDestination:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    section_id: str | None = None


@dataclass(frozen=True, slots=True)
class PracticeReviewTarget:
    schema_version: str
    practice_placement_id: str
    resource_id: str
    resource_version: str
    resource_digest: str
    resource_title: str
    state: PracticeReviewState
    destination: PracticeReviewDestination | None = None
    unavailable_reason: PracticeReviewUnavailableReason | None = None


@dataclass(frozen=True, slots=True)
class RegisterPracticeReviewTargetRequest:
    target: PracticeReviewTarget


@dataclass(frozen=True, slots=True)
class ResolvePracticeReviewTargetsRequest:
    practice_placement_id: str
    resources: tuple[PracticeReviewResource, ...]


@dataclass(frozen=True, slots=True)
class PublishCurriculumGraphRequest:
    graph: CurriculumGraph


@dataclass(frozen=True, slots=True)
class OpenCurriculumGraphRequest:
    curriculum_id: str
    curriculum_version: str


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
    INVALID_QUERY = "invalid_query"
    IMMUTABLE_CONFLICT = "immutable_conflict"
    STALE_CURSOR = "stale_cursor"
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


class OpportunityQuerySort(StrEnum):
    CATALOG = "catalog"
    TITLE = "title"
    DURATION_ASCENDING = "duration_ascending"
    DURATION_DESCENDING = "duration_descending"


@dataclass(frozen=True, slots=True)
class QueryLearningOpportunitiesRequest:
    query: str | None = None
    prerequisite_query: str | None = None
    topics: tuple[str, ...] = ()
    levels: tuple[OpportunityLevel, ...] = ()
    kinds: tuple[OpportunityKind, ...] = ()
    availabilities: tuple[OpportunityAvailability, ...] = ()
    minimum_minutes: int | None = None
    maximum_minutes: int | None = None
    sort: OpportunityQuerySort = OpportunityQuerySort.CATALOG
    page_size: int = 20
    cursor: str | None = None


@dataclass(frozen=True, slots=True)
class AppliedLearningOpportunityQuery:
    query: str | None
    prerequisite_query: str | None
    topics: tuple[str, ...]
    levels: tuple[OpportunityLevel, ...]
    kinds: tuple[OpportunityKind, ...]
    availabilities: tuple[OpportunityAvailability, ...]
    minimum_minutes: int | None
    maximum_minutes: int | None
    sort: OpportunityQuerySort
    page_size: int


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
class LearningOpportunityQueryPage:
    schema_version: str
    projection_generation: str
    projected_at: datetime
    applied_query: AppliedLearningOpportunityQuery
    total_matches: int
    records: tuple[LearningOpportunityRecord, ...]
    next_cursor: str | None


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

    def create_practice_placement(
        self, request: CreatePracticePlacementRequest
    ) -> PracticePlacement: ...

    def resolve_placed_practice(
        self, request: ResolvePlacedPracticeRequest
    ) -> PracticePlacement: ...

    def create_project_brief_placement(
        self, request: CreateProjectBriefPlacementRequest
    ) -> ProjectBriefPlacement: ...

    def resolve_project_brief_placement(
        self, request: ResolveProjectBriefPlacementRequest
    ) -> ProjectBriefPlacement: ...

    def register_practice_review_target(
        self, request: RegisterPracticeReviewTargetRequest
    ) -> PracticeReviewTarget: ...

    def resolve_practice_review_targets(
        self, request: ResolvePracticeReviewTargetsRequest
    ) -> tuple[PracticeReviewTarget, ...]: ...

    def publish_curriculum_graph(
        self, request: PublishCurriculumGraphRequest
    ) -> CurriculumGraph: ...

    def open_curriculum_graph(
        self, request: OpenCurriculumGraphRequest
    ) -> CurriculumGraph: ...

    def register_lesson_opportunity(
        self, request: RegisterLessonOpportunityRequest
    ) -> LessonOpportunityClassification: ...

    def rebuild_learning_opportunity_projection(
        self, request: RebuildLearningOpportunityProjectionRequest
    ) -> LearningOpportunityBrowse: ...

    def browse_learning_opportunities(
        self, request: BrowseLearningOpportunitiesRequest
    ) -> LearningOpportunityBrowse: ...

    def query_learning_opportunities(
        self, request: QueryLearningOpportunitiesRequest
    ) -> LearningOpportunityQueryPage: ...
