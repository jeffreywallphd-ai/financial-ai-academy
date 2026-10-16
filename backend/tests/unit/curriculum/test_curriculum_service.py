from __future__ import annotations

from dataclasses import fields
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
    PlacementConflict,
)
from financial_ai_academy.modules.curriculum.public import (
    AssessmentPlacement,
    CreateAssessmentPlacementRequest,
    CreateLessonPlacementRequest,
    CreatePracticePlacementRequest,
    LessonPlacement,
    LessonReadingResult,
    OpenPlacedLessonRequest,
    PracticePlacement,
    ResolvePlacedAssessmentRequest,
    ResolvePlacedPracticeRequest,
)


REPOSITORY = Path(__file__).resolve().parents[4]
APPROVED = (
    REPOSITORY
    / "contracts/compatibility/lesson-package/v1/approved/intro-risk-return"
)
SCHEMAS = REPOSITORY / "contracts/learning/lesson-package/v1"


class MemoryCurriculumRepository:
    def __init__(self) -> None:
        self.records: dict[str, LessonPlacement] = {}
        self.assessments: dict[str, AssessmentPlacement] = {}
        self.practices: dict[str, PracticePlacement] = {}

    def get(self, placement_id: str) -> LessonPlacement | None:
        return self.records.get(placement_id)

    def save_if_absent(
        self, placement: LessonPlacement
    ) -> tuple[LessonPlacement, bool]:
        existing = self.records.get(placement.placement_id)
        if existing is None:
            self.records[placement.placement_id] = placement
            return placement, True
        if (
            existing.package_id,
            existing.package_version,
            existing.package_digest,
        ) != (
            placement.package_id,
            placement.package_version,
            placement.package_digest,
        ):
            raise PlacementConflict
        return existing, False

    def get_assessment(
        self, placement_id: str
    ) -> AssessmentPlacement | None:
        return self.assessments.get(placement_id)

    def save_assessment_if_absent(
        self, placement: AssessmentPlacement
    ) -> tuple[AssessmentPlacement, bool]:
        existing = self.assessments.get(placement.placement_id)
        if existing is None:
            self.assessments[placement.placement_id] = placement
            return placement, True
        comparable = (
            "package_id",
            "package_version",
            "package_digest",
            "assessment_id",
            "assessment_version",
            "definition_digest",
            "item_id",
            "item_version",
            "scoring_policy_id",
            "scoring_policy_version",
        )
        if any(
            getattr(existing, field) != getattr(placement, field)
            for field in comparable
        ):
            raise PlacementConflict
        return existing, False

    def get_practice(self, placement_id: str) -> PracticePlacement | None:
        return self.practices.get(placement_id)

    def save_practice_if_absent(
        self, placement: PracticePlacement
    ) -> tuple[PracticePlacement, bool]:
        existing = self.practices.get(placement.placement_id)
        if existing is None:
            self.practices[placement.placement_id] = placement
            return placement, True
        comparable = (
            "package_id",
            "package_version",
            "package_digest",
            "practice_id",
            "practice_version",
            "definition_digest",
        )
        if any(
            getattr(existing, field) != getattr(placement, field)
            for field in comparable
        ):
            raise PlacementConflict
        return existing, False


class FakeContentGateway:
    def __init__(self, lesson: PublishedLesson) -> None:
        self.lesson = lesson
        self.calls: list[tuple[str, str, str]] = []
        self.available = True

    def get_exact(
        self,
        package_id: str,
        package_version: str,
        package_digest: str,
    ) -> PublishedLesson:
        self.calls.append((package_id, package_version, package_digest))
        if (
            not self.available
            or (
                package_id,
                package_version,
                package_digest,
            )
            != (
                self.lesson.package_id,
                self.lesson.package_version,
                self.lesson.package_digest,
            )
        ):
            raise LessonReadError(
                LessonErrorCode.NOT_FOUND,
                "Exact lesson not found.",
                reference=f"{package_id}@{package_version}",
            )
        return self.lesson


@pytest.fixture
def lesson() -> PublishedLesson:
    return ContractLessonPackageValidator(SCHEMAS).validate_directory(
        APPROVED
    ).lesson


def request_for(lesson: PublishedLesson) -> CreateLessonPlacementRequest:
    return CreateLessonPlacementRequest(
        placement_id="intro-risk-return-primary",
        package_id=lesson.package_id,
        package_version=lesson.package_version,
        package_digest=lesson.package_digest,
    )


def test_create_and_open_use_only_the_exact_content_reference(
    lesson: PublishedLesson,
) -> None:
    repository = MemoryCurriculumRepository()
    gateway = FakeContentGateway(lesson)
    service = CurriculumService(repository, gateway)
    request = request_for(lesson)

    first = service.create_lesson_placement(request)
    second = service.create_lesson_placement(request)
    reading = service.open_placed_lesson(
        OpenPlacedLessonRequest(first.placement_id)
    )

    assert first == second
    assert reading.package_digest == lesson.package_digest
    assert reading.title == lesson.title
    assert gateway.calls == [
        (
            lesson.package_id,
            lesson.package_version,
            lesson.package_digest,
        )
    ] * 3
    assert len(repository.records) == 1


def test_stale_exact_version_never_substitutes_a_newer_lesson(
    lesson: PublishedLesson,
) -> None:
    repository = MemoryCurriculumRepository()
    gateway = FakeContentGateway(lesson)
    service = CurriculumService(repository, gateway)
    placement = service.create_lesson_placement(request_for(lesson))
    gateway.available = False

    with pytest.raises(LessonReadError) as captured:
        service.open_placed_lesson(
            OpenPlacedLessonRequest(placement.placement_id)
        )

    assert captured.value.code is LessonErrorCode.UNAVAILABLE
    assert gateway.calls[-1] == (
        lesson.package_id,
        lesson.package_version,
        lesson.package_digest,
    )


def test_missing_placement_is_distinct_from_stale_content(
    lesson: PublishedLesson,
) -> None:
    service = CurriculumService(
        MemoryCurriculumRepository(), FakeContentGateway(lesson)
    )

    with pytest.raises(LessonReadError) as captured:
        service.open_placed_lesson(OpenPlacedLessonRequest("missing-placement"))

    assert captured.value.code is LessonErrorCode.NOT_FOUND


def test_conflicting_placement_identity_is_immutable(
    lesson: PublishedLesson,
) -> None:
    repository = MemoryCurriculumRepository()
    service = CurriculumService(repository, FakeContentGateway(lesson))
    service.create_lesson_placement(request_for(lesson))
    repository.records["intro-risk-return-primary"] = LessonPlacement(
        placement_id="intro-risk-return-primary",
        package_id=lesson.package_id,
        package_version=lesson.package_version,
        package_digest="f" * 64,
        created_at=next(iter(repository.records.values())).created_at,
    )

    with pytest.raises(LessonReadError) as captured:
        service.create_lesson_placement(request_for(lesson))

    assert captured.value.code is LessonErrorCode.IMMUTABLE_CONFLICT


def test_reading_result_has_no_content_storage_or_driver_field() -> None:
    prohibited = {"path", "object_key", "storage_key", "row", "driver"}
    result_fields = {field.name for field in fields(LessonReadingResult)}
    assert result_fields.isdisjoint(prohibited)


def test_create_and_resolve_exact_assessment_reference(
    lesson: PublishedLesson,
) -> None:
    repository = MemoryCurriculumRepository()
    service = CurriculumService(repository, FakeContentGateway(lesson))
    lesson_placement = service.create_lesson_placement(request_for(lesson))
    request = CreateAssessmentPlacementRequest(
        placement_id=lesson_placement.placement_id,
        package_id=lesson.package_id,
        package_version=lesson.package_version,
        package_digest=lesson.package_digest,
        assessment_id="risk-return-check-1",
        assessment_version="1.0.0",
        definition_digest="a" * 64,
        item_id="risk-return-tradeoff",
        item_version="1.0.0",
        scoring_policy_id="single-select-exact-match",
        scoring_policy_version="1.0.0",
    )
    created = service.create_assessment_placement(request)
    repeated = service.create_assessment_placement(request)
    resolved = service.resolve_placed_assessment(
        ResolvePlacedAssessmentRequest(lesson_placement.placement_id)
    )
    assert created == repeated == resolved
    assert resolved.definition_digest == "a" * 64


def test_assessment_reference_must_match_exact_lesson(
    lesson: PublishedLesson,
) -> None:
    repository = MemoryCurriculumRepository()
    service = CurriculumService(repository, FakeContentGateway(lesson))
    lesson_placement = service.create_lesson_placement(request_for(lesson))
    request = CreateAssessmentPlacementRequest(
        placement_id=lesson_placement.placement_id,
        package_id=lesson.package_id,
        package_version=lesson.package_version,
        package_digest="b" * 64,
        assessment_id="risk-return-check-1",
        assessment_version="1.0.0",
        definition_digest="a" * 64,
        item_id="risk-return-tradeoff",
        item_version="1.0.0",
        scoring_policy_id="single-select-exact-match",
        scoring_policy_version="1.0.0",
    )
    with pytest.raises(LessonReadError) as captured:
        service.create_assessment_placement(request)
    assert captured.value.code is LessonErrorCode.INVALID_PACKAGE
    assert repository.assessments == {}


def practice_request_for(
    lesson: PublishedLesson,
) -> CreatePracticePlacementRequest:
    return CreatePracticePlacementRequest(
        placement_id="intro-risk-return-primary",
        package_id=lesson.package_id,
        package_version=lesson.package_version,
        package_digest=lesson.package_digest,
        practice_id="risk-return-practice",
        practice_version="1.0.0",
        definition_digest="a" * 64,
    )


def test_create_and_resolve_exact_practice_reference(
    lesson: PublishedLesson,
) -> None:
    repository = MemoryCurriculumRepository()
    service = CurriculumService(repository, FakeContentGateway(lesson))
    lesson_placement = service.create_lesson_placement(request_for(lesson))
    request = practice_request_for(lesson)

    created = service.create_practice_placement(request)
    repeated = service.create_practice_placement(request)
    resolved = service.resolve_placed_practice(
        ResolvePlacedPracticeRequest(lesson_placement.placement_id)
    )

    assert created == repeated == resolved
    assert resolved.definition_digest == "a" * 64


def test_practice_reference_must_match_exact_lesson(
    lesson: PublishedLesson,
) -> None:
    repository = MemoryCurriculumRepository()
    service = CurriculumService(repository, FakeContentGateway(lesson))
    service.create_lesson_placement(request_for(lesson))
    request = practice_request_for(lesson)
    mismatched = CreatePracticePlacementRequest(
        placement_id=request.placement_id,
        package_id=request.package_id,
        package_version=request.package_version,
        package_digest="b" * 64,
        practice_id=request.practice_id,
        practice_version=request.practice_version,
        definition_digest=request.definition_digest,
    )

    with pytest.raises(LessonReadError) as captured:
        service.create_practice_placement(mismatched)

    assert captured.value.code is LessonErrorCode.INVALID_PACKAGE
    assert repository.practices == {}


def test_practice_reference_is_immutable_for_a_placement(
    lesson: PublishedLesson,
) -> None:
    repository = MemoryCurriculumRepository()
    service = CurriculumService(repository, FakeContentGateway(lesson))
    service.create_lesson_placement(request_for(lesson))
    request = practice_request_for(lesson)
    service.create_practice_placement(request)
    conflict = CreatePracticePlacementRequest(
        placement_id=request.placement_id,
        package_id=request.package_id,
        package_version=request.package_version,
        package_digest=request.package_digest,
        practice_id="another-practice",
        practice_version=request.practice_version,
        definition_digest="b" * 64,
    )

    with pytest.raises(LessonReadError) as captured:
        service.create_practice_placement(conflict)

    assert captured.value.code is LessonErrorCode.IMMUTABLE_CONFLICT
