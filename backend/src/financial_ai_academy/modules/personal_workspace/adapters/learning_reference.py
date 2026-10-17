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
from ..ports.learning_reference import LearningReferenceGatewayPort
from ..public import (
    LearningOpportunitySelector,
    LearningReferenceSelector,
    PlacedLessonSelector,
    ProjectArtifactSelector,
    ProjectSnapshotSelector,
    ProjectWorkspaceSelector,
)


class PublicCurriculumLearningReferenceGateway:
    def __init__(self, curriculum: CurriculumOperations) -> None:
        self._curriculum = curriculum

    def resolve(
        self,
        selector: LearningReferenceSelector,
        *,
        learner_id: str,
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
                    or record.provenance.published_at > validated_at
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
                    validated_at=validated_at,
                )
            if not isinstance(selector, PlacedLessonSelector):
                raise PersonalWorkspaceSourceUnavailable()
            lesson = self._curriculum.open_placed_lesson(
                OpenPlacedLessonRequest(selector.placement_id)
            )
            if lesson.provenance.published_at > validated_at:
                raise PersonalWorkspaceSourceUnavailable()
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
                validated_at=validated_at,
            )
        except PersonalWorkspaceSourceUnavailable:
            raise
        except Exception as error:
            raise PersonalWorkspaceSourceUnavailable() from error


class PublicLearningReferenceGateway:
    """Dispatch the closed selector union without weakening owner boundaries."""

    def __init__(
        self,
        curriculum: LearningReferenceGatewayPort,
        project: LearningReferenceGatewayPort,
    ) -> None:
        self._curriculum = curriculum
        self._project = project

    def resolve(
        self,
        selector: LearningReferenceSelector,
        *,
        learner_id: str,
        validated_at: datetime,
    ) -> LearningReference:
        if isinstance(
            selector, (LearningOpportunitySelector, PlacedLessonSelector)
        ):
            gateway = self._curriculum
        elif isinstance(
            selector,
            (
                ProjectWorkspaceSelector,
                ProjectSnapshotSelector,
                ProjectArtifactSelector,
            ),
        ):
            gateway = self._project
        else:
            raise PersonalWorkspaceSourceUnavailable()
        return gateway.resolve(
            selector,
            learner_id=learner_id,
            validated_at=validated_at,
        )
