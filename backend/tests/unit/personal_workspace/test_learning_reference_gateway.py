from __future__ import annotations

from dataclasses import fields
from datetime import date, datetime, timedelta, timezone

import pytest

from financial_ai_academy.modules.content.public import PublicationProvenance
from financial_ai_academy.modules.curriculum.public import (
    DiscoveryProvenance,
    LearningOpportunityBrowse,
    LearningOpportunityRecord,
    LessonReadingResult,
    OpportunityAvailability,
    OpportunityKind,
    OpportunityLevel,
)
from financial_ai_academy.modules.personal_workspace.adapters.learning_reference import (
    PublicCurriculumLearningReferenceGateway,
)
from financial_ai_academy.modules.personal_workspace.domain.workspace import (
    LearningOpportunityReference,
    PlacedLessonReference,
)
from financial_ai_academy.modules.personal_workspace.ports.learning_reference import (
    PersonalWorkspaceSourceUnavailable,
)
from financial_ai_academy.modules.personal_workspace.public import (
    LearningOpportunitySelector,
    PlacedLessonSelector,
)


NOW = datetime(2026, 10, 17, 15, 0, tzinfo=timezone.utc)


def opportunity(*, availability=OpportunityAvailability.AVAILABLE, published_at=NOW):
    return LearningOpportunityRecord(
        schema_version="1.0.0",
        opportunity_id="opportunity.diversification",
        placement_id="placement.diversification",
        destination="/learn/placements/placement.diversification",
        kind=OpportunityKind.LESSON,
        title="Introduction to diversification",
        summary="Compare concentration and diversification.",
        objectives=("Explain diversification.",),
        topics=("diversification",),
        level=OpportunityLevel.INTRODUCTORY,
        estimated_minutes=20,
        prerequisite_summary="No prerequisite.",
        availability=availability,
        availability_reason="Available.",
        package_id="package.diversification",
        package_version="1.0.0",
        package_digest="a" * 64,
        provenance=DiscoveryProvenance(
            published_by="Financial AI Academy",
            published_at=published_at,
            content_reviewed_on=date(2026, 10, 17),
            educational_use_notice="Education and research only.",
        ),
        source_fingerprint="b" * 64,
        projected_at=NOW,
    )


def lesson(*, published_at=NOW):
    return LessonReadingResult(
        placement_id="placement.risk",
        package_id="package.risk",
        package_version="1.0.0",
        package_digest="c" * 64,
        title="Understanding risk",
        objectives=("Explain risk.",),
        body=(),
        sources=(),
        assets=(),
        provenance=PublicationProvenance(
            published_by="Financial AI Academy",
            published_at=published_at,
            content_reviewed_on=date(2026, 10, 17),
            educational_use_notice="Education and research only.",
        ),
    )


class Curriculum:
    def __init__(self, records=(opportunity(),), placed=lesson()) -> None:
        self.records = records
        self.placed = placed
        self.browse_calls = 0
        self.lesson_calls = 0

    def browse_learning_opportunities(self, request):
        self.browse_calls += 1
        return LearningOpportunityBrowse(
            schema_version="1.0.0",
            projection_generation="d" * 64,
            projected_at=NOW,
            records=self.records,
        )

    def open_placed_lesson(self, request):
        self.lesson_calls += 1
        if request.placement_id != self.placed.placement_id:
            raise RuntimeError("not found")
        return self.placed


def test_opportunity_resolution_retains_only_safe_current_public_facts() -> None:
    curriculum = Curriculum()
    result = PublicCurriculumLearningReferenceGateway(curriculum).resolve(
        LearningOpportunitySelector(
            "opportunity.diversification", "placement.diversification"
        ),
        validated_at=NOW,
    )
    assert isinstance(result, LearningOpportunityReference)
    assert result.destination == "/learn/placements/placement.diversification"
    assert result.source_fingerprint == "b" * 64
    assert result.validated_at == NOW
    assert curriculum.browse_calls == 1
    assert curriculum.lesson_calls == 0


def test_lesson_resolution_does_not_copy_body_or_permission_state() -> None:
    curriculum = Curriculum()
    result = PublicCurriculumLearningReferenceGateway(curriculum).resolve(
        PlacedLessonSelector("placement.risk"),
        validated_at=NOW,
    )
    assert isinstance(result, PlacedLessonReference)
    assert result.destination == "/learn/placements/placement.risk"
    assert {field.name for field in fields(result)} == {
        "placement_id",
        "package_id",
        "package_version",
        "package_digest",
        "title",
        "destination",
        "target_status",
        "provenance",
        "validated_at",
        "owner_module",
        "reference_kind",
    }
    assert curriculum.lesson_calls == 1


@pytest.mark.parametrize(
    "records,selector",
    (
        ((), LearningOpportunitySelector("opportunity.missing", "placement.missing")),
        (
            (opportunity(availability=OpportunityAvailability.UNAVAILABLE),),
            LearningOpportunitySelector(
                "opportunity.diversification", "placement.diversification"
            ),
        ),
        (
            (opportunity(published_at=NOW + timedelta(minutes=1)),),
            LearningOpportunitySelector(
                "opportunity.diversification", "placement.diversification"
            ),
        ),
    ),
)
def test_missing_unavailable_or_future_opportunity_fails_closed(records, selector) -> None:
    with pytest.raises(PersonalWorkspaceSourceUnavailable):
        PublicCurriculumLearningReferenceGateway(Curriculum(records=records)).resolve(
            selector,
            validated_at=NOW,
        )
