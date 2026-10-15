"""Exact-version lesson placement and safe read composition."""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import datetime, timezone

from financial_ai_academy.modules.content.public import (
    LessonErrorCode,
    LessonReadError,
)

from ..ports.content_gateway import ContentLessonGatewayPort
from ..ports.repositories import CurriculumRepositoryPort, PlacementConflict
from ..domain.models import discovery_digest, projection_generation
from ..ports.repositories import OpportunityConflict
from ..public import (
    AssessmentPlacement,
    BrowseLearningOpportunitiesRequest,
    CreateAssessmentPlacementRequest,
    CreateLessonPlacementRequest,
    DiscoveryError,
    DiscoveryErrorCode,
    DiscoveryProvenance,
    LearningOpportunityBrowse,
    LearningOpportunityRecord,
    LessonOpportunityClassification,
    LessonPlacement,
    LessonReadingResult,
    OpenPlacedLessonRequest,
    OpportunityAvailability,
    OpportunityKind,
    OpportunityLevel,
    RebuildLearningOpportunityProjectionRequest,
    RegisterLessonOpportunityRequest,
    ResolvePlacedAssessmentRequest,
)


_PLACEMENT_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
_TOPIC = re.compile(r"^[a-z0-9][a-z0-9-]{1,49}$")
_DISCOVERY_VERSION = "1.0.0"


class CurriculumService:
    def __init__(
        self,
        repository: CurriculumRepositoryPort,
        content: ContentLessonGatewayPort,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository
        self._content = content
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def create_lesson_placement(
        self, request: CreateLessonPlacementRequest
    ) -> LessonPlacement:
        if not _PLACEMENT_ID.fullmatch(request.placement_id):
            raise LessonReadError(
                LessonErrorCode.INVALID_PACKAGE,
                "Lesson placement identity is invalid.",
                reference=request.placement_id,
            )
        self._content.get_exact(
            request.package_id,
            request.package_version,
            request.package_digest,
        )
        candidate = LessonPlacement(
            placement_id=request.placement_id,
            package_id=request.package_id,
            package_version=request.package_version,
            package_digest=request.package_digest,
            created_at=datetime.now(timezone.utc),
        )
        try:
            stored, _created = self._repository.save_if_absent(candidate)
        except PlacementConflict as error:
            raise LessonReadError(
                LessonErrorCode.IMMUTABLE_CONFLICT,
                "The placement identity already maps to another lesson.",
                reference=request.placement_id,
            ) from error
        except LessonReadError:
            raise
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Lesson placement storage is unavailable.",
                reference=request.placement_id,
            ) from error
        return stored

    def open_placed_lesson(
        self, request: OpenPlacedLessonRequest
    ) -> LessonReadingResult:
        try:
            placement = self._repository.get(request.placement_id)
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Lesson placement storage is unavailable.",
                reference=request.placement_id,
            ) from error
        if placement is None:
            raise LessonReadError(
                LessonErrorCode.NOT_FOUND,
                "Lesson placement was not found.",
                reference=request.placement_id,
            )
        try:
            lesson = self._content.get_exact(
                placement.package_id,
                placement.package_version,
                placement.package_digest,
            )
        except LessonReadError as error:
            if error.code is LessonErrorCode.NOT_FOUND:
                raise LessonReadError(
                    LessonErrorCode.UNAVAILABLE,
                    "The placement's exact lesson version is unavailable.",
                    reference=request.placement_id,
                ) from error
            raise
        return LessonReadingResult(
            placement_id=placement.placement_id,
            package_id=lesson.package_id,
            package_version=lesson.package_version,
            package_digest=lesson.package_digest,
            title=lesson.title,
            objectives=lesson.objectives,
            body=lesson.body,
            sources=lesson.sources,
            assets=lesson.assets,
            provenance=lesson.provenance,
        )

    def create_assessment_placement(
        self, request: CreateAssessmentPlacementRequest
    ) -> AssessmentPlacement:
        lesson = self._get_placement(request.placement_id)
        if (
            lesson.package_id,
            lesson.package_version,
            lesson.package_digest,
        ) != (
            request.package_id,
            request.package_version,
            request.package_digest,
        ):
            raise LessonReadError(
                LessonErrorCode.INVALID_PACKAGE,
                "Assessment placement does not match the exact lesson.",
                reference=request.placement_id,
            )
        self._validate_assessment_reference(request)
        candidate = AssessmentPlacement(
            placement_id=request.placement_id,
            package_id=request.package_id,
            package_version=request.package_version,
            package_digest=request.package_digest,
            assessment_id=request.assessment_id,
            assessment_version=request.assessment_version,
            definition_digest=request.definition_digest,
            item_id=request.item_id,
            item_version=request.item_version,
            scoring_policy_id=request.scoring_policy_id,
            scoring_policy_version=request.scoring_policy_version,
            created_at=datetime.now(timezone.utc),
        )
        try:
            stored, _created = self._repository.save_assessment_if_absent(
                candidate
            )
        except PlacementConflict as error:
            raise LessonReadError(
                LessonErrorCode.IMMUTABLE_CONFLICT,
                "The placement already maps to another assessment.",
                reference=request.placement_id,
            ) from error
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Assessment placement storage is unavailable.",
                reference=request.placement_id,
            ) from error
        return stored

    def resolve_placed_assessment(
        self, request: ResolvePlacedAssessmentRequest
    ) -> AssessmentPlacement:
        try:
            placement = self._repository.get_assessment(request.placement_id)
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Assessment placement storage is unavailable.",
                reference=request.placement_id,
            ) from error
        if placement is None:
            raise LessonReadError(
                LessonErrorCode.NOT_FOUND,
                "Assessment placement was not found.",
                reference=request.placement_id,
            )
        return placement

    def register_lesson_opportunity(
        self, request: RegisterLessonOpportunityRequest
    ) -> LessonOpportunityClassification:
        classification = self._classification(request)
        placement = self._discovery_placement(classification.placement_id)
        self._discovery_lesson(placement)
        try:
            stored, _created = (
                self._repository.save_opportunity_classification_if_absent(
                    classification
                )
            )
        except OpportunityConflict as error:
            raise DiscoveryError(
                DiscoveryErrorCode.IMMUTABLE_CONFLICT,
                "Learning-opportunity identity already maps to different facts.",
                reference=request.opportunity_id,
            ) from error
        except DiscoveryError:
            raise
        except Exception as error:
            raise DiscoveryError(
                DiscoveryErrorCode.UNAVAILABLE,
                "Learning-opportunity source storage is unavailable.",
                reference=request.opportunity_id,
            ) from error
        return stored

    def rebuild_learning_opportunity_projection(
        self, _request: RebuildLearningOpportunityProjectionRequest
    ) -> LearningOpportunityBrowse:
        try:
            classifications = (
                self._repository.list_opportunity_classifications()
            )
        except Exception as error:
            raise DiscoveryError(
                DiscoveryErrorCode.UNAVAILABLE,
                "Learning-opportunity sources are unavailable.",
            ) from error
        projected_at = self._now()
        records: list[LearningOpportunityRecord] = []
        for classification in classifications:
            placement = self._discovery_placement(classification.placement_id)
            lesson = self._discovery_lesson(placement)
            meaning = self._record_meaning(classification, placement, lesson)
            records.append(
                LearningOpportunityRecord(
                    **meaning,
                    source_fingerprint=discovery_digest(
                        self._json_meaning(meaning)
                    ),
                    projected_at=projected_at,
                )
            )
        ordered = tuple(
            sorted(
                records,
                key=lambda record: (
                    record.title.casefold(),
                    record.opportunity_id,
                ),
            )
        )
        generation = projection_generation(
            [self._stable_record(record) for record in ordered]
        )
        try:
            self._repository.replace_discovery_projection(
                generation,
                projected_at,
                ordered,
            )
        except Exception as error:
            raise DiscoveryError(
                DiscoveryErrorCode.UNAVAILABLE,
                "Learning-opportunity projection could not be replaced.",
            ) from error
        return LearningOpportunityBrowse(
            schema_version=_DISCOVERY_VERSION,
            projection_generation=generation,
            projected_at=projected_at,
            records=ordered,
        )

    def browse_learning_opportunities(
        self, _request: BrowseLearningOpportunitiesRequest
    ) -> LearningOpportunityBrowse:
        try:
            projection = self._repository.read_discovery_projection()
        except Exception as error:
            raise DiscoveryError(
                DiscoveryErrorCode.UNAVAILABLE,
                "Learning-opportunity projection is unavailable.",
            ) from error
        if projection is None:
            raise DiscoveryError(
                DiscoveryErrorCode.UNAVAILABLE,
                "Learning-opportunity projection is unavailable.",
            )
        generation, projected_at, records = projection
        ordered = tuple(
            sorted(
                records,
                key=lambda record: (
                    record.title.casefold(),
                    record.opportunity_id,
                ),
            )
        )
        expected = projection_generation(
            [self._stable_record(record) for record in ordered]
        )
        if records != ordered or generation != expected:
            raise DiscoveryError(
                DiscoveryErrorCode.STALE_SOURCE,
                "Learning-opportunity projection integrity failed.",
            )
        return LearningOpportunityBrowse(
            schema_version=_DISCOVERY_VERSION,
            projection_generation=generation,
            projected_at=projected_at,
            records=records,
        )

    def _classification(
        self, request: RegisterLessonOpportunityRequest
    ) -> LessonOpportunityClassification:
        if not _PLACEMENT_ID.fullmatch(request.opportunity_id) or not (
            _PLACEMENT_ID.fullmatch(request.placement_id)
        ):
            self._invalid(request.opportunity_id, "Opportunity identity is invalid.")
        if not isinstance(request.level, OpportunityLevel) or not isinstance(
            request.availability, OpportunityAvailability
        ):
            self._invalid(
                request.opportunity_id,
                "Opportunity classification is unsupported.",
            )
        if (
            not isinstance(request.estimated_minutes, int)
            or isinstance(request.estimated_minutes, bool)
            or request.estimated_minutes < 1
            or request.estimated_minutes > 1440
        ):
            self._invalid(
                request.opportunity_id,
                "Estimated duration is invalid.",
            )
        topics = tuple(sorted(request.topics))
        if (
            not 1 <= len(topics) <= 8
            or len(topics) != len(set(topics))
            or any(not _TOPIC.fullmatch(topic) for topic in topics)
        ):
            self._invalid(request.opportunity_id, "Opportunity topics are invalid.")
        return LessonOpportunityClassification(
            opportunity_id=request.opportunity_id,
            placement_id=request.placement_id,
            summary=self._clean_text(request.summary, 20, 500, "summary"),
            topics=topics,
            level=request.level,
            estimated_minutes=request.estimated_minutes,
            prerequisite_summary=self._clean_text(
                request.prerequisite_summary,
                2,
                500,
                "prerequisite_summary",
            ),
            availability=request.availability,
            availability_reason=self._clean_text(
                request.availability_reason,
                10,
                500,
                "availability_reason",
            ),
            created_at=self._now(),
        )

    def _discovery_placement(self, placement_id: str) -> LessonPlacement:
        try:
            placement = self._repository.get(placement_id)
        except Exception as error:
            raise DiscoveryError(
                DiscoveryErrorCode.UNAVAILABLE,
                "Learning-opportunity source storage is unavailable.",
                reference=placement_id,
            ) from error
        if placement is None:
            raise DiscoveryError(
                DiscoveryErrorCode.STALE_SOURCE,
                "The exact learning destination is unavailable.",
                reference=placement_id,
            )
        return placement

    def _discovery_lesson(self, placement: LessonPlacement):
        try:
            lesson = self._content.get_exact(
                placement.package_id,
                placement.package_version,
                placement.package_digest,
            )
        except LessonReadError as error:
            code = (
                DiscoveryErrorCode.UNAVAILABLE
                if error.code is LessonErrorCode.UNAVAILABLE
                else DiscoveryErrorCode.STALE_SOURCE
            )
            raise DiscoveryError(
                code,
                "The exact published opportunity source is unavailable.",
                reference=placement.placement_id,
            ) from error
        if (
            lesson.package_id,
            lesson.package_version,
            lesson.package_digest,
        ) != (
            placement.package_id,
            placement.package_version,
            placement.package_digest,
        ):
            raise DiscoveryError(
                DiscoveryErrorCode.STALE_SOURCE,
                "The published opportunity source does not match its placement.",
                reference=placement.placement_id,
            )
        return lesson

    @staticmethod
    def _record_meaning(classification, placement, lesson) -> dict[str, object]:
        return {
            "schema_version": _DISCOVERY_VERSION,
            "opportunity_id": classification.opportunity_id,
            "placement_id": placement.placement_id,
            "destination": f"/learn/placements/{placement.placement_id}",
            "kind": OpportunityKind.LESSON,
            "title": lesson.title,
            "summary": classification.summary,
            "objectives": lesson.objectives,
            "topics": classification.topics,
            "level": classification.level,
            "estimated_minutes": classification.estimated_minutes,
            "prerequisite_summary": classification.prerequisite_summary,
            "availability": classification.availability,
            "availability_reason": classification.availability_reason,
            "package_id": lesson.package_id,
            "package_version": lesson.package_version,
            "package_digest": lesson.package_digest,
            "provenance": DiscoveryProvenance(
                published_by=lesson.provenance.published_by,
                published_at=lesson.provenance.published_at,
                content_reviewed_on=lesson.provenance.content_reviewed_on,
                educational_use_notice=(
                    lesson.provenance.educational_use_notice
                ),
            ),
        }

    @staticmethod
    def _json_meaning(value: dict[str, object]) -> dict[str, object]:
        provenance = value["provenance"]
        assert isinstance(provenance, DiscoveryProvenance)
        return {
            **value,
            "kind": str(value["kind"]),
            "objectives": list(value["objectives"]),
            "topics": list(value["topics"]),
            "level": str(value["level"]),
            "availability": str(value["availability"]),
            "provenance": {
                "published_by": provenance.published_by,
                "published_at": (
                    provenance.published_at.astimezone(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z")
                ),
                "content_reviewed_on": (
                    provenance.content_reviewed_on.isoformat()
                ),
                "educational_use_notice": (
                    provenance.educational_use_notice
                ),
            },
        }

    @classmethod
    def _stable_record(
        cls, record: LearningOpportunityRecord
    ) -> dict[str, object]:
        meaning = {
            field: getattr(record, field)
            for field in (
                "schema_version",
                "opportunity_id",
                "placement_id",
                "destination",
                "kind",
                "title",
                "summary",
                "objectives",
                "topics",
                "level",
                "estimated_minutes",
                "prerequisite_summary",
                "availability",
                "availability_reason",
                "package_id",
                "package_version",
                "package_digest",
                "provenance",
            )
        }
        value = cls._json_meaning(meaning)
        return {**value, "source_fingerprint": record.source_fingerprint}

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None:
            raise DiscoveryError(
                DiscoveryErrorCode.INVALID_RECORD,
                "Discovery clock must produce an aware timestamp.",
            )
        return value.astimezone(timezone.utc)

    @staticmethod
    def _clean_text(
        value: object,
        minimum: int,
        maximum: int,
        reference: str,
    ) -> str:
        if not isinstance(value, str):
            CurriculumService._invalid(reference, "Discovery text is invalid.")
        normalized = value.strip()
        if (
            value != normalized
            or not minimum <= len(normalized) <= maximum
            or any(character in normalized for character in ("\x00", "\r", "\n"))
        ):
            CurriculumService._invalid(reference, "Discovery text is invalid.")
        return normalized

    @staticmethod
    def _invalid(reference: str, message: str):
        raise DiscoveryError(
            DiscoveryErrorCode.INVALID_RECORD,
            message,
            reference=reference,
        )

    def _get_placement(self, placement_id: str) -> LessonPlacement:
        try:
            placement = self._repository.get(placement_id)
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Lesson placement storage is unavailable.",
                reference=placement_id,
            ) from error
        if placement is None:
            raise LessonReadError(
                LessonErrorCode.NOT_FOUND,
                "Lesson placement was not found.",
                reference=placement_id,
            )
        return placement

    @staticmethod
    def _validate_assessment_reference(
        request: CreateAssessmentPlacementRequest,
    ) -> None:
        identifiers = (
            request.assessment_id,
            request.item_id,
            request.scoring_policy_id,
        )
        versions = (
            request.assessment_version,
            request.item_version,
            request.scoring_policy_version,
        )
        if (
            any(not _PLACEMENT_ID.fullmatch(value) for value in identifiers)
            or any(value != "1.0.0" for value in versions)
            or not re.fullmatch(r"[a-f0-9]{64}", request.definition_digest)
        ):
            raise LessonReadError(
                LessonErrorCode.INVALID_PACKAGE,
                "Assessment placement reference is invalid.",
                reference=request.placement_id,
            )
