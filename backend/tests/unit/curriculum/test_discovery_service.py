from __future__ import annotations

from dataclasses import fields, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.content.adapters.lesson_package import (
    ContractLessonPackageValidator,
)
from financial_ai_academy.modules.content.public import (
    LessonErrorCode,
    LessonReadError,
    PublishedLesson,
)
from financial_ai_academy.modules.curriculum.application.service import (
    CurriculumService,
)
from financial_ai_academy.modules.curriculum.ports.repositories import (
    OpportunityConflict,
    PlacementConflict,
)
from financial_ai_academy.modules.curriculum.public import (
    AssessmentPlacement,
    AppliedLearningOpportunityQuery,
    BrowseLearningOpportunitiesRequest,
    CreateLessonPlacementRequest,
    DiscoveryError,
    DiscoveryErrorCode,
    LearningOpportunityRecord,
    LearningOpportunityQueryPage,
    LessonOpportunityClassification,
    LessonPlacement,
    OpportunityAvailability,
    OpportunityKind,
    OpportunityLevel,
    OpportunityQuerySort,
    QueryLearningOpportunitiesRequest,
    RebuildLearningOpportunityProjectionRequest,
    RegisterLessonOpportunityRequest,
)


REPOSITORY = Path(__file__).resolve().parents[4]
APPROVED = (
    REPOSITORY
    / "contracts/compatibility/lesson-package/v1/approved/intro-risk-return-knowledge-check"
)
SCHEMAS = REPOSITORY / "contracts/learning/lesson-package/v1"
NOW = datetime(2026, 10, 15, 17, 0, tzinfo=timezone.utc)
EXPECTED_SOURCE = "6206218a3a49b2439ec3d46054f2c96f004cc680021b8b25e0f62b1f211894f5"
EXPECTED_GENERATION = "746b3442477c7e3d70b0886cee11a0e1a439b58b7fcc4b660d790ce3cf92f3d8"


class MemoryDiscoveryRepository:
    def __init__(self) -> None:
        self.placements: dict[str, LessonPlacement] = {}
        self.classifications: dict[str, LessonOpportunityClassification] = {}
        self.projection: tuple[
            str,
            datetime,
            tuple[LearningOpportunityRecord, ...],
        ] | None = None
        self.fail_replace = False
        self.projection_reads = 0

    def get(self, placement_id: str) -> LessonPlacement | None:
        return self.placements.get(placement_id)

    def save_if_absent(
        self, placement: LessonPlacement
    ) -> tuple[LessonPlacement, bool]:
        existing = self.placements.get(placement.placement_id)
        if existing is not None:
            if existing != placement:
                raise PlacementConflict
            return existing, False
        self.placements[placement.placement_id] = placement
        return placement, True

    def get_assessment(self, placement_id: str) -> AssessmentPlacement | None:
        return None

    def save_assessment_if_absent(
        self, placement: AssessmentPlacement
    ) -> tuple[AssessmentPlacement, bool]:
        raise NotImplementedError

    def get_opportunity_classification(
        self, opportunity_id: str
    ) -> LessonOpportunityClassification | None:
        return self.classifications.get(opportunity_id)

    def save_opportunity_classification_if_absent(
        self, classification: LessonOpportunityClassification
    ) -> tuple[LessonOpportunityClassification, bool]:
        existing = self.classifications.get(classification.opportunity_id)
        if existing is None:
            self.classifications[classification.opportunity_id] = classification
            return classification, True
        comparable = (
            "placement_id",
            "summary",
            "topics",
            "level",
            "estimated_minutes",
            "prerequisite_summary",
            "availability",
            "availability_reason",
        )
        if any(
            getattr(existing, name) != getattr(classification, name)
            for name in comparable
        ):
            raise OpportunityConflict
        return existing, False

    def list_opportunity_classifications(
        self,
    ) -> tuple[LessonOpportunityClassification, ...]:
        return tuple(self.classifications.values())

    def replace_discovery_projection(
        self,
        generation: str,
        projected_at: datetime,
        records: tuple[LearningOpportunityRecord, ...],
    ) -> None:
        if self.fail_replace:
            raise RuntimeError("synthetic storage failure")
        self.projection = generation, projected_at, records

    def read_discovery_projection(
        self,
    ) -> tuple[
        str,
        datetime,
        tuple[LearningOpportunityRecord, ...],
    ] | None:
        self.projection_reads += 1
        return self.projection


class FakeContentGateway:
    def __init__(self, lesson: PublishedLesson) -> None:
        self.lesson = lesson
        self.available = True
        self.fail_unexpected = False

    def get_exact(
        self,
        package_id: str,
        package_version: str,
        package_digest: str,
    ) -> PublishedLesson:
        if self.fail_unexpected:
            raise RuntimeError("synthetic provider detail")
        if not self.available or (
            package_id,
            package_version,
            package_digest,
        ) != (
            self.lesson.package_id,
            self.lesson.package_version,
            self.lesson.package_digest,
        ):
            raise LessonReadError(
                LessonErrorCode.NOT_FOUND,
                "Exact lesson not found.",
                reference=package_id,
            )
        return self.lesson


@pytest.fixture
def lesson() -> PublishedLesson:
    return ContractLessonPackageValidator(SCHEMAS).validate_directory(
        APPROVED
    ).lesson


def service_for(
    lesson: PublishedLesson,
) -> tuple[CurriculumService, MemoryDiscoveryRepository, FakeContentGateway]:
    repository = MemoryDiscoveryRepository()
    gateway = FakeContentGateway(lesson)
    service = CurriculumService(repository, gateway, clock=lambda: NOW)
    placement = service.create_lesson_placement(
        CreateLessonPlacementRequest(
            placement_id="intro-risk-return-primary",
            package_id=lesson.package_id,
            package_version=lesson.package_version,
            package_digest=lesson.package_digest,
        )
    )
    assert placement.placement_id == "intro-risk-return-primary"
    return service, repository, gateway


def request(
    *,
    opportunity_id: str = "intro-risk-return-primary",
    placement_id: str = "intro-risk-return-primary",
    summary: str = (
        "Learn why potential return and investment risk must be considered "
        "together."
    ),
    topics: tuple[str, ...] = ("risk-and-return", "investing-basics"),
    level: OpportunityLevel = OpportunityLevel.INTRODUCTORY,
    estimated_minutes: int = 15,
    prerequisite_summary: str = "No prior lesson is required.",
    availability: OpportunityAvailability = OpportunityAvailability.AVAILABLE,
) -> RegisterLessonOpportunityRequest:
    return RegisterLessonOpportunityRequest(
        opportunity_id=opportunity_id,
        placement_id=placement_id,
        summary=summary,
        topics=topics,
        level=level,
        estimated_minutes=estimated_minutes,
        prerequisite_summary=prerequisite_summary,
        availability=availability,
        availability_reason="Available in this local learning catalog.",
    )


def add_opportunity(
    service: CurriculumService,
    repository: MemoryDiscoveryRepository,
    *,
    opportunity_id: str,
    summary: str,
    topics: tuple[str, ...],
    estimated_minutes: int,
    prerequisite_summary: str,
    level: OpportunityLevel = OpportunityLevel.INTRODUCTORY,
    availability: OpportunityAvailability = OpportunityAvailability.AVAILABLE,
) -> None:
    repository.placements[opportunity_id] = replace(
        repository.placements["intro-risk-return-primary"],
        placement_id=opportunity_id,
    )
    service.register_lesson_opportunity(
        request(
            opportunity_id=opportunity_id,
            placement_id=opportunity_id,
            summary=summary,
            topics=topics,
            level=level,
            estimated_minutes=estimated_minutes,
            prerequisite_summary=prerequisite_summary,
            availability=availability,
        )
    )


def test_register_rebuild_and_browse_exact_approved_lesson(
    lesson: PublishedLesson,
) -> None:
    service, repository, _gateway = service_for(lesson)
    first = service.register_lesson_opportunity(request())
    repeated = service.register_lesson_opportunity(request())
    rebuilt = service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )
    browsed = service.browse_learning_opportunities(
        BrowseLearningOpportunitiesRequest()
    )
    queried = service.query_learning_opportunities(
        QueryLearningOpportunitiesRequest(page_size=50)
    )

    assert first == repeated
    assert first.topics == ("investing-basics", "risk-and-return")
    assert rebuilt == browsed
    assert rebuilt.projection_generation == EXPECTED_GENERATION
    assert rebuilt.records[0].source_fingerprint == EXPECTED_SOURCE
    assert rebuilt.records[0].package_digest == lesson.package_digest
    assert rebuilt.records[0].destination == (
        "/learn/placements/intro-risk-return-primary"
    )
    assert queried.records == browsed.records
    assert queried.total_matches == 1
    assert queried.next_cursor is None
    assert queried.applied_query.sort is OpportunityQuerySort.CATALOG
    assert repository.projection is not None


def test_repeat_rebuild_is_semantically_stable(
    lesson: PublishedLesson,
) -> None:
    service, _repository, _gateway = service_for(lesson)
    service.register_lesson_opportunity(request())

    first = service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )
    second = service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )

    assert first == second
    assert first.records[0].source_fingerprint == EXPECTED_SOURCE


def test_browse_uses_stable_title_then_identity_order(
    lesson: PublishedLesson,
) -> None:
    service, repository, _gateway = service_for(lesson)
    repository.placements["intro-risk-return-secondary"] = replace(
        repository.placements["intro-risk-return-primary"],
        placement_id="intro-risk-return-secondary",
    )
    service.register_lesson_opportunity(
        request(
            opportunity_id="intro-risk-return-secondary",
            placement_id="intro-risk-return-secondary",
        )
    )
    service.register_lesson_opportunity(request())

    result = service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )

    assert [record.opportunity_id for record in result.records] == [
        "intro-risk-return-primary",
        "intro-risk-return-secondary",
    ]


def test_conflicting_classification_is_immutable(
    lesson: PublishedLesson,
) -> None:
    service, _repository, _gateway = service_for(lesson)
    service.register_lesson_opportunity(request())

    with pytest.raises(DiscoveryError) as captured:
        service.register_lesson_opportunity(
            replace(request(), estimated_minutes=20)
        )

    assert captured.value.code is DiscoveryErrorCode.IMMUTABLE_CONFLICT


def test_missing_placement_and_exact_content_fail_closed(
    lesson: PublishedLesson,
) -> None:
    service, _repository, gateway = service_for(lesson)
    with pytest.raises(DiscoveryError) as missing:
        service.register_lesson_opportunity(
            request(placement_id="missing-placement")
        )
    assert missing.value.code is DiscoveryErrorCode.STALE_SOURCE

    service.register_lesson_opportunity(request())
    gateway.available = False
    with pytest.raises(DiscoveryError) as stale:
        service.rebuild_learning_opportunity_projection(
            RebuildLearningOpportunityProjectionRequest()
        )
    assert stale.value.code is DiscoveryErrorCode.STALE_SOURCE


def test_failed_replacement_retains_last_complete_generation(
    lesson: PublishedLesson,
) -> None:
    service, repository, _gateway = service_for(lesson)
    service.register_lesson_opportunity(request())
    expected = service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )
    repository.fail_replace = True

    with pytest.raises(DiscoveryError) as captured:
        service.rebuild_learning_opportunity_projection(
            RebuildLearningOpportunityProjectionRequest()
        )

    assert captured.value.code is DiscoveryErrorCode.UNAVAILABLE
    assert service.browse_learning_opportunities(
        BrowseLearningOpportunitiesRequest()
    ) == expected


def test_corrupt_source_and_over_limit_rebuild_retain_last_generation(
    lesson: PublishedLesson,
) -> None:
    service, repository, _gateway = service_for(lesson)
    stored = service.register_lesson_opportunity(request())
    expected = service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )
    repository.classifications[stored.opportunity_id] = replace(
        stored,
        summary="x",
    )

    with pytest.raises(DiscoveryError) as corrupt:
        service.rebuild_learning_opportunity_projection(
            RebuildLearningOpportunityProjectionRequest()
        )

    assert corrupt.value.code is DiscoveryErrorCode.INVALID_RECORD
    assert repository.projection == (
        expected.projection_generation,
        expected.projected_at,
        expected.records,
    )

    repository.classifications = {
        f"opportunity-{index:04d}": replace(
            stored,
            opportunity_id=f"opportunity-{index:04d}",
        )
        for index in range(501)
    }
    with pytest.raises(DiscoveryError) as over_limit:
        service.rebuild_learning_opportunity_projection(
            RebuildLearningOpportunityProjectionRequest()
        )
    assert over_limit.value.code is DiscoveryErrorCode.INVALID_RECORD
    assert repository.projection == (
        expected.projection_generation,
        expected.projected_at,
        expected.records,
    )


def test_missing_or_tampered_projection_is_never_returned(
    lesson: PublishedLesson,
) -> None:
    service, repository, _gateway = service_for(lesson)
    with pytest.raises(DiscoveryError) as missing:
        service.browse_learning_opportunities(
            BrowseLearningOpportunitiesRequest()
        )
    assert missing.value.code is DiscoveryErrorCode.UNAVAILABLE

    service.register_lesson_opportunity(request())
    result = service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )
    repository.projection = (
        "f" * 64,
        result.projected_at,
        result.records,
    )
    with pytest.raises(DiscoveryError) as tampered:
        service.browse_learning_opportunities(
            BrowseLearningOpportunitiesRequest()
        )
    assert tampered.value.code is DiscoveryErrorCode.STALE_SOURCE

    repository.projection = (
        result.projection_generation,
        result.projected_at,
        (
            replace(
                result.records[0],
                projected_at=result.projected_at + timedelta(seconds=1),
            ),
        ),
    )
    with pytest.raises(DiscoveryError) as mixed_timestamp:
        service.browse_learning_opportunities(
            BrowseLearningOpportunitiesRequest()
        )
    assert mixed_timestamp.value.code is DiscoveryErrorCode.STALE_SOURCE


def test_unexpected_content_failure_is_bounded_and_redacted(
    lesson: PublishedLesson,
) -> None:
    service, repository, gateway = service_for(lesson)
    gateway.fail_unexpected = True

    with pytest.raises(DiscoveryError) as captured:
        service.register_lesson_opportunity(request())

    assert captured.value.code is DiscoveryErrorCode.UNAVAILABLE
    assert "provider" not in captured.value.message
    assert repository.classifications == {}


@pytest.mark.parametrize(
    "candidate",
    [
        replace(request(), opportunity_id="BAD"),
        replace(request(), opportunity_id=None),
        replace(request(), summary="short"),
        replace(request(), topics=("not valid",)),
        replace(request(), topics=None),
        replace(request(), topics=("investing-basics", 3)),
        replace(request(), estimated_minutes=0),
        replace(request(), prerequisite_summary="\nnone"),
        replace(request(), availability_reason="brief"),
    ],
)
def test_invalid_classification_creates_no_source_record(
    lesson: PublishedLesson,
    candidate: RegisterLessonOpportunityRequest,
) -> None:
    service, repository, _gateway = service_for(lesson)
    with pytest.raises(DiscoveryError) as captured:
        service.register_lesson_opportunity(candidate)
    assert captured.value.code is DiscoveryErrorCode.INVALID_RECORD
    assert repository.classifications == {}


def test_discovery_records_exclude_storage_identity_and_ranking_fields() -> None:
    prohibited = {
        "learner_id",
        "provider_id",
        "object_key",
        "storage_key",
        "rank",
        "score",
        "eligible",
        "recommended",
    }
    names = {field.name for field in fields(LearningOpportunityRecord)}
    assert names.isdisjoint(prohibited)


def test_query_normalizes_text_and_combines_filters(
    lesson: PublishedLesson,
) -> None:
    service, repository, _gateway = service_for(lesson)
    service.register_lesson_opportunity(
        request(summary="Café basics connect investment return and risk.")
    )
    add_opportunity(
        service,
        repository,
        opportunity_id="risk-return-intermediate",
        summary="Intermediate portfolio risk comparison practice.",
        topics=("portfolio", "risk-and-return"),
        level=OpportunityLevel.INTERMEDIATE,
        estimated_minutes=30,
        prerequisite_summary="Understanding Risk and Return is required.",
    )
    service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )

    result = service.query_learning_opportunities(
        QueryLearningOpportunitiesRequest(
            query="  CAFE\u0301   RISK ",
            prerequisite_query="  NO   PRIOR ",
            topics=("risk-and-return", "investing-basics", "risk-and-return"),
            levels=(OpportunityLevel.INTERMEDIATE, OpportunityLevel.INTRODUCTORY),
            kinds=(OpportunityKind.LESSON,),
            availabilities=(OpportunityAvailability.AVAILABLE,),
            minimum_minutes=10,
            maximum_minutes=20,
            page_size=5,
        )
    )

    assert result.applied_query.query == "café risk"
    assert result.applied_query.prerequisite_query == "no prior"
    assert result.applied_query.topics == (
        "investing-basics",
        "risk-and-return",
    )
    assert result.applied_query.levels == (
        OpportunityLevel.INTERMEDIATE,
        OpportunityLevel.INTRODUCTORY,
    )
    assert result.total_matches == 1
    assert result.records[0].opportunity_id == "intro-risk-return-primary"


def test_query_sorts_and_pages_without_duplicates(
    lesson: PublishedLesson,
) -> None:
    service, repository, _gateway = service_for(lesson)
    service.register_lesson_opportunity(request(estimated_minutes=20))
    add_opportunity(
        service,
        repository,
        opportunity_id="risk-return-alpha",
        summary="Alpha lesson summary for deterministic ordering.",
        topics=("investing-basics",),
        estimated_minutes=10,
        prerequisite_summary="No prior lesson is required.",
    )
    add_opportunity(
        service,
        repository,
        opportunity_id="risk-return-zulu",
        summary="Zulu lesson summary for deterministic ordering.",
        topics=("risk-and-return",),
        estimated_minutes=20,
        prerequisite_summary="No prior lesson is required.",
    )
    service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )

    first = service.query_learning_opportunities(
        QueryLearningOpportunitiesRequest(
            sort=OpportunityQuerySort.DURATION_ASCENDING,
            page_size=2,
        )
    )
    assert first.total_matches == 3
    assert [record.opportunity_id for record in first.records] == [
        "risk-return-alpha",
        "intro-risk-return-primary",
    ]
    assert first.next_cursor is not None

    second = service.query_learning_opportunities(
        QueryLearningOpportunitiesRequest(
            sort=OpportunityQuerySort.DURATION_ASCENDING,
            page_size=2,
            cursor=first.next_cursor,
        )
    )
    assert [record.opportunity_id for record in second.records] == [
        "risk-return-zulu"
    ]
    assert second.next_cursor is None
    replay = service.query_learning_opportunities(
        QueryLearningOpportunitiesRequest(
            sort=OpportunityQuerySort.DURATION_ASCENDING,
            page_size=2,
            cursor=first.next_cursor,
        )
    )
    assert replay == second

    longest = service.query_learning_opportunities(
        QueryLearningOpportunitiesRequest(
            sort=OpportunityQuerySort.DURATION_DESCENDING,
            page_size=3,
        )
    )
    assert [record.opportunity_id for record in longest.records] == [
        "intro-risk-return-primary",
        "risk-return-zulu",
        "risk-return-alpha",
    ]


def test_query_rejects_malformed_request_before_projection_read(
    lesson: PublishedLesson,
) -> None:
    service, repository, _gateway = service_for(lesson)
    invalid = (
        QueryLearningOpportunitiesRequest(query=" "),
        QueryLearningOpportunitiesRequest(query="word " * 11),
        QueryLearningOpportunitiesRequest(topics=("not valid",)),
        QueryLearningOpportunitiesRequest(levels=("introductory",)),
        QueryLearningOpportunitiesRequest(minimum_minutes=30, maximum_minutes=10),
        QueryLearningOpportunitiesRequest(page_size=0),
        QueryLearningOpportunitiesRequest(cursor="not-a-cursor"),
    )

    for candidate in invalid:
        with pytest.raises(DiscoveryError) as captured:
            service.query_learning_opportunities(candidate)
        assert captured.value.code is DiscoveryErrorCode.INVALID_QUERY
    assert repository.projection_reads == 0


def test_query_rejects_tampered_mismatched_and_stale_cursor(
    lesson: PublishedLesson,
) -> None:
    service, repository, _gateway = service_for(lesson)
    service.register_lesson_opportunity(request())
    add_opportunity(
        service,
        repository,
        opportunity_id="risk-return-secondary",
        summary="Secondary lesson summary for cursor evidence.",
        topics=("risk-and-return",),
        estimated_minutes=25,
        prerequisite_summary="No prior lesson is required.",
    )
    service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )
    first = service.query_learning_opportunities(
        QueryLearningOpportunitiesRequest(page_size=1)
    )
    assert first.next_cursor is not None

    tampered = first.next_cursor[:-1] + (
        "0" if first.next_cursor[-1] != "0" else "1"
    )
    with pytest.raises(DiscoveryError) as tamper_error:
        service.query_learning_opportunities(
            QueryLearningOpportunitiesRequest(page_size=1, cursor=tampered)
        )
    assert tamper_error.value.code is DiscoveryErrorCode.INVALID_QUERY

    with pytest.raises(DiscoveryError) as mismatch:
        service.query_learning_opportunities(
            QueryLearningOpportunitiesRequest(
                query="risk",
                page_size=1,
                cursor=first.next_cursor,
            )
        )
    assert mismatch.value.code is DiscoveryErrorCode.INVALID_QUERY

    add_opportunity(
        service,
        repository,
        opportunity_id="risk-return-third",
        summary="Third lesson summary for stale cursor evidence.",
        topics=("risk-and-return",),
        estimated_minutes=35,
        prerequisite_summary="No prior lesson is required.",
    )
    service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )
    with pytest.raises(DiscoveryError) as stale:
        service.query_learning_opportunities(
            QueryLearningOpportunitiesRequest(
                page_size=1,
                cursor=first.next_cursor,
            )
        )
    assert stale.value.code is DiscoveryErrorCode.STALE_CURSOR


def test_query_public_types_exclude_authority_and_ranking_fields() -> None:
    prohibited = {
        "learner_id",
        "provider_id",
        "storage_key",
        "rank",
        "score",
        "eligible",
        "recommended",
        "secret",
    }
    names = {
        field.name
        for public_type in (
            QueryLearningOpportunitiesRequest,
            AppliedLearningOpportunityQuery,
            LearningOpportunityQueryPage,
        )
        for field in fields(public_type)
    }
    assert names.isdisjoint(prohibited)
