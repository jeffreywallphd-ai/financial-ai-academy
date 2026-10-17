"""Resolve accepted learning references only through Curriculum public reads."""

from __future__ import annotations

from datetime import datetime

from financial_ai_academy.modules.curriculum.public import (
    BrowseLearningOpportunitiesRequest,
    CurriculumOperations,
    OpenPlacedLessonRequest,
    OpportunityAvailability,
)

from ..domain.workspace import (
    LearningOpportunityReference,
    LearningReference,
    PlacedLessonReference,
    PublicationProvenance,
)
from ..ports.learning_reference import PersonalWorkspaceSourceUnavailable
from ..public import LearningOpportunitySelector, LearningReferenceSelector


class PublicCurriculumLearningReferenceGateway:
    def __init__(self, curriculum: CurriculumOperations) -> None:
        self._curriculum = curriculum

    def resolve(
        self,
        selector: LearningReferenceSelector,
        *,
        validated_at: datetime,
    ) -> LearningReference:
        try:
            if isinstance(selector, LearningOpportunitySelector):
                browse = self._curriculum.browse_learning_opportunities(
                    BrowseLearningOpportunitiesRequest()
                )
                record = next(
                    (
                        candidate
                        for candidate in browse.records
                        if candidate.opportunity_id == selector.opportunity_id
                        and candidate.placement_id == selector.placement_id
                    ),
                    None,
                )
                if (
                    record is None
                    or record.availability != OpportunityAvailability.AVAILABLE
                ):
                    raise PersonalWorkspaceSourceUnavailable()
                return LearningOpportunityReference(
                    opportunity_id=record.opportunity_id,
                    placement_id=record.placement_id,
                    package_id=record.package_id,
                    package_version=record.package_version,
                    package_digest=record.package_digest,
                    source_fingerprint=record.source_fingerprint,
                    title=record.title,
                    destination=record.destination,
                    target_status="available",
                    provenance=PublicationProvenance(
                        published_by=record.provenance.published_by,
                        published_at=record.provenance.published_at,
                        content_reviewed_on=(
                            record.provenance.content_reviewed_on.isoformat()
                        ),
                        educational_use_notice=(
                            record.provenance.educational_use_notice
                        ),
                    ),
                    validated_at=max(validated_at, record.provenance.published_at),
                )
            lesson = self._curriculum.open_placed_lesson(
                OpenPlacedLessonRequest(selector.placement_id)
            )
            return PlacedLessonReference(
                placement_id=lesson.placement_id,
                package_id=lesson.package_id,
                package_version=lesson.package_version,
                package_digest=lesson.package_digest,
                title=lesson.title,
                destination=f"/learn/placements/{lesson.placement_id}",
                target_status="available",
                provenance=PublicationProvenance(
                    published_by=lesson.provenance.published_by,
                    published_at=lesson.provenance.published_at,
                    content_reviewed_on=(
                        lesson.provenance.content_reviewed_on.isoformat()
                    ),
                    educational_use_notice=(
                        lesson.provenance.educational_use_notice
                    ),
                ),
                validated_at=max(validated_at, lesson.provenance.published_at),
            )
        except PersonalWorkspaceSourceUnavailable:
            raise
        except Exception as error:
            raise PersonalWorkspaceSourceUnavailable() from error
