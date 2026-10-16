"""Exact-version lesson placement and safe read composition."""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import date, datetime, timezone

from financial_ai_academy.modules.content.public import (
    LessonErrorCode,
    LessonReadError,
    PublishedLesson,
)

from ..ports.content_gateway import ContentLessonGatewayPort
from ..ports.repositories import (
    CurriculumGraphConflict,
    CurriculumRepositoryPort,
    PlacementConflict,
)
from ..domain.models import discovery_digest, projection_generation
from ..ports.repositories import OpportunityConflict
from ..public import (
    AssessmentPlacement,
    AssessmentActivityReference,
    BrowseLearningOpportunitiesRequest,
    CreateAssessmentPlacementRequest,
    CreateLessonPlacementRequest,
    CreatePracticePlacementRequest,
    CurriculumGraph,
    CurriculumGraphError,
    CurriculumGraphErrorCode,
    DiscoveryError,
    DiscoveryErrorCode,
    DiscoveryProvenance,
    LearningOpportunityBrowse,
    LearningOpportunityQueryPage,
    LearningOpportunityRecord,
    LessonOpportunityClassification,
    LessonActivityReference,
    LessonPlacement,
    LessonReadingResult,
    OpenPlacedLessonRequest,
    OpenCurriculumGraphRequest,
    OpportunityAvailability,
    OpportunityKind,
    OpportunityLevel,
    PracticePlacement,
    QueryLearningOpportunitiesRequest,
    PublishCurriculumGraphRequest,
    RebuildLearningOpportunityProjectionRequest,
    RegisterLessonOpportunityRequest,
    ResolvePlacedAssessmentRequest,
    ResolvePlacedPracticeRequest,
    validate_curriculum_graph,
)
from .query import (
    prepare_learning_opportunity_query,
    query_learning_opportunity_projection,
)


_PLACEMENT_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
_TOPIC = re.compile(r"^[a-z0-9][a-z0-9-]{1,49}$")
_SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?$"
)
_DIGEST = re.compile(r"^[a-f0-9]{64}$")
_DISCOVERY_VERSION = "1.0.0"
_MAX_DISCOVERY_RECORDS = 500


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

    def create_practice_placement(
        self, request: CreatePracticePlacementRequest
    ) -> PracticePlacement:
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
                "Practice placement does not match the exact lesson.",
                reference=request.placement_id,
            )
        self._validate_practice_reference(request)
        candidate = PracticePlacement(
            placement_id=request.placement_id,
            package_id=request.package_id,
            package_version=request.package_version,
            package_digest=request.package_digest,
            practice_id=request.practice_id,
            practice_version=request.practice_version,
            definition_digest=request.definition_digest,
            created_at=self._clock(),
        )
        try:
            stored, _created = self._repository.save_practice_if_absent(
                candidate
            )
        except PlacementConflict as error:
            raise LessonReadError(
                LessonErrorCode.IMMUTABLE_CONFLICT,
                "The placement already maps to another practice.",
                reference=request.placement_id,
            ) from error
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Practice placement storage is unavailable.",
                reference=request.placement_id,
            ) from error
        return stored

    def resolve_placed_practice(
        self, request: ResolvePlacedPracticeRequest
    ) -> PracticePlacement:
        try:
            placement = self._repository.get_practice(request.placement_id)
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Practice placement storage is unavailable.",
                reference=request.placement_id,
            ) from error
        if placement is None:
            raise LessonReadError(
                LessonErrorCode.NOT_FOUND,
                "Practice placement was not found.",
                reference=request.placement_id,
            )
        return placement

    def publish_curriculum_graph(
        self,
        request: PublishCurriculumGraphRequest,
    ) -> CurriculumGraph:
        if not isinstance(request, PublishCurriculumGraphRequest):
            raise self._graph_error(
                CurriculumGraphErrorCode.INVALID_RECORD,
                "Curriculum graph publication request is invalid.",
            )
        graph = validate_curriculum_graph(request.graph)
        self._verify_graph_activity_references(graph)
        try:
            stored, _created = self._repository.save_graph_if_absent(graph)
        except CurriculumGraphConflict as error:
            raise self._graph_error(
                CurriculumGraphErrorCode.IMMUTABLE_CONFLICT,
                "The curriculum graph version already maps to different meaning.",
                reference=graph.curriculum_id,
            ) from error
        except CurriculumGraphError:
            raise
        except Exception as error:
            raise self._graph_error(
                CurriculumGraphErrorCode.UNAVAILABLE,
                "Curriculum graph storage is unavailable.",
                reference=graph.curriculum_id,
            ) from error
        return self._validated_stored_graph(
            stored,
            graph.curriculum_id,
            graph.curriculum_version,
        )

    def open_curriculum_graph(
        self,
        request: OpenCurriculumGraphRequest,
    ) -> CurriculumGraph:
        if (
            not isinstance(request, OpenCurriculumGraphRequest)
            or not isinstance(request.curriculum_id, str)
            or not _PLACEMENT_ID.fullmatch(request.curriculum_id)
            or not isinstance(request.curriculum_version, str)
            or not _SEMVER.fullmatch(request.curriculum_version)
        ):
            raise self._graph_error(
                CurriculumGraphErrorCode.INVALID_RECORD,
                "Curriculum graph reference is invalid.",
            )
        try:
            graph = self._repository.get_graph_exact(
                request.curriculum_id,
                request.curriculum_version,
            )
        except CurriculumGraphError:
            raise
        except Exception as error:
            raise self._graph_error(
                CurriculumGraphErrorCode.UNAVAILABLE,
                "Curriculum graph storage is unavailable.",
                reference=request.curriculum_id,
            ) from error
        if graph is None:
            raise self._graph_error(
                CurriculumGraphErrorCode.NOT_FOUND,
                "The exact curriculum graph version was not found.",
                reference=request.curriculum_id,
            )
        return self._validated_stored_graph(
            graph,
            request.curriculum_id,
            request.curriculum_version,
        )

    def _verify_graph_activity_references(
        self,
        graph: CurriculumGraph,
    ) -> None:
        for activity in graph.activities:
            reference = activity.reference
            try:
                if isinstance(reference, LessonActivityReference):
                    placement = self._repository.get(reference.placement_id)
                    matches = placement is not None and (
                        placement.package_id,
                        placement.package_version,
                        placement.package_digest,
                    ) == (
                        reference.package_id,
                        reference.package_version,
                        reference.package_digest,
                    )
                elif isinstance(reference, AssessmentActivityReference):
                    placement = self._repository.get_assessment(
                        reference.placement_id
                    )
                    matches = placement is not None and (
                        placement.assessment_id,
                        placement.assessment_version,
                        placement.definition_digest,
                    ) == (
                        reference.assessment_id,
                        reference.assessment_version,
                        reference.definition_digest,
                    )
                else:
                    matches = False
            except Exception as error:
                raise self._graph_error(
                    CurriculumGraphErrorCode.UNAVAILABLE,
                    "Curriculum graph reference storage is unavailable.",
                    reference=activity.activity_id,
                ) from error
            if not matches:
                raise self._graph_error(
                    CurriculumGraphErrorCode.STALE_REFERENCE,
                    "Curriculum graph activity reference is unavailable.",
                    reference=activity.activity_id,
                )

    @staticmethod
    def _validated_stored_graph(
        graph: object,
        curriculum_id: str,
        curriculum_version: str,
    ) -> CurriculumGraph:
        try:
            if not isinstance(graph, CurriculumGraph):
                raise TypeError("stored graph type is invalid")
            validated = validate_curriculum_graph(graph)
            if (
                validated.curriculum_id != curriculum_id
                or validated.curriculum_version != curriculum_version
            ):
                raise ValueError("stored graph identity does not match")
            return validated
        except CurriculumGraphError as error:
            raise CurriculumGraphError(
                CurriculumGraphErrorCode.UNAVAILABLE,
                "Stored curriculum graph is unavailable.",
                reference=curriculum_id,
            ) from error
        except (AttributeError, TypeError, ValueError) as error:
            raise CurriculumGraphError(
                CurriculumGraphErrorCode.UNAVAILABLE,
                "Stored curriculum graph is unavailable.",
                reference=curriculum_id,
            ) from error

    @staticmethod
    def _graph_error(
        code: CurriculumGraphErrorCode,
        message: str,
        *,
        reference: str = "curriculum-graph",
    ) -> CurriculumGraphError:
        return CurriculumGraphError(code, message, reference=reference)

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
        if (
            not isinstance(classifications, tuple)
            or len(classifications) > _MAX_DISCOVERY_RECORDS
        ):
            self._invalid(
                "learning-opportunity",
                "Learning-opportunity sources are invalid.",
            )
        records: list[LearningOpportunityRecord] = []
        for classification in classifications:
            self._validate_stored_classification(classification)
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
        self._validate_projection(
            generation,
            projected_at,
            ordered,
            code=DiscoveryErrorCode.INVALID_RECORD,
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
        if not isinstance(projection, tuple) or len(projection) != 3:
            self._projection_invalid(DiscoveryErrorCode.STALE_SOURCE)
        generation, projected_at, records = projection
        self._validate_projection(
            generation,
            projected_at,
            records,
            code=DiscoveryErrorCode.STALE_SOURCE,
        )
        return LearningOpportunityBrowse(
            schema_version=_DISCOVERY_VERSION,
            projection_generation=generation,
            projected_at=projected_at,
            records=records,
        )

    def query_learning_opportunities(
        self, request: QueryLearningOpportunitiesRequest
    ) -> LearningOpportunityQueryPage:
        prepared = prepare_learning_opportunity_query(request)
        browse = self.browse_learning_opportunities(
            BrowseLearningOpportunitiesRequest()
        )
        return query_learning_opportunity_projection(browse, prepared)

    def _classification(
        self, request: RegisterLessonOpportunityRequest
    ) -> LessonOpportunityClassification:
        if (
            not isinstance(request.opportunity_id, str)
            or not isinstance(request.placement_id, str)
            or not _PLACEMENT_ID.fullmatch(request.opportunity_id)
            or not _PLACEMENT_ID.fullmatch(request.placement_id)
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
        if not isinstance(request.topics, tuple) or any(
            not isinstance(topic, str) for topic in request.topics
        ):
            self._invalid(request.opportunity_id, "Opportunity topics are invalid.")
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

    def _validate_stored_classification(self, value: object) -> None:
        if not isinstance(value, LessonOpportunityClassification):
            self._invalid(
                "learning-opportunity",
                "Learning-opportunity sources are invalid.",
            )
        normalized = self._classification(
            RegisterLessonOpportunityRequest(
                opportunity_id=value.opportunity_id,
                placement_id=value.placement_id,
                summary=value.summary,
                topics=value.topics,
                level=value.level,
                estimated_minutes=value.estimated_minutes,
                prerequisite_summary=value.prerequisite_summary,
                availability=value.availability,
                availability_reason=value.availability_reason,
            )
        )
        semantic_fields = (
            "opportunity_id",
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
            getattr(value, field) != getattr(normalized, field)
            for field in semantic_fields
        ) or not self._aware_datetime(value.created_at):
            self._invalid(
                value.opportunity_id,
                "Learning-opportunity sources are invalid.",
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
        if (
            not isinstance(placement, LessonPlacement)
            or placement.placement_id != placement_id
            or not self._identifier(placement.placement_id)
            or not self._identifier(placement.package_id)
            or not isinstance(placement.package_version, str)
            or not _SEMVER.fullmatch(placement.package_version)
            or not isinstance(placement.package_digest, str)
            or not _DIGEST.fullmatch(placement.package_digest)
            or not self._aware_datetime(placement.created_at)
        ):
            raise DiscoveryError(
                DiscoveryErrorCode.STALE_SOURCE,
                "The exact learning destination is invalid.",
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
        except Exception as error:
            raise DiscoveryError(
                DiscoveryErrorCode.UNAVAILABLE,
                "The exact published opportunity source is unavailable.",
                reference=placement.placement_id,
            ) from error
        if not isinstance(lesson, PublishedLesson):
            raise DiscoveryError(
                DiscoveryErrorCode.STALE_SOURCE,
                "The published opportunity source is invalid.",
                reference=placement.placement_id,
            )
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

    @classmethod
    def _validate_projection(
        cls,
        generation: object,
        projected_at: object,
        records: object,
        *,
        code: DiscoveryErrorCode,
    ) -> None:
        if (
            not isinstance(generation, str)
            or not _DIGEST.fullmatch(generation)
            or not cls._aware_datetime(projected_at)
            or not isinstance(records, tuple)
            or len(records) > _MAX_DISCOVERY_RECORDS
        ):
            cls._projection_invalid(code)
        identities: list[str] = []
        for record in records:
            cls._validate_record(record, projected_at, code=code)
            identities.append(record.opportunity_id)
        if len(identities) != len(set(identities)):
            cls._projection_invalid(code)
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
            [cls._stable_record(record) for record in ordered]
        )
        if records != ordered or generation != expected:
            cls._projection_invalid(code)

    @classmethod
    def _validate_record(
        cls,
        record: object,
        projected_at: datetime,
        *,
        code: DiscoveryErrorCode,
    ) -> None:
        if not isinstance(record, LearningOpportunityRecord):
            cls._projection_invalid(code)
        provenance = record.provenance
        if (
            record.schema_version != _DISCOVERY_VERSION
            or not cls._identifier(record.opportunity_id)
            or not cls._identifier(record.placement_id)
            or record.destination
            != f"/learn/placements/{record.placement_id}"
            or record.kind is not OpportunityKind.LESSON
            or not cls._bounded_text(record.title, 1, 240)
            or not cls._bounded_text(record.summary, 20, 500)
            or not cls._bounded_text_tuple(record.objectives, 1, 20, 500)
            or not cls._valid_topics(record.topics)
            or not isinstance(record.level, OpportunityLevel)
            or not isinstance(record.estimated_minutes, int)
            or isinstance(record.estimated_minutes, bool)
            or not 1 <= record.estimated_minutes <= 1440
            or not cls._bounded_text(record.prerequisite_summary, 2, 500)
            or not isinstance(record.availability, OpportunityAvailability)
            or not cls._bounded_text(record.availability_reason, 10, 500)
            or not cls._identifier(record.package_id)
            or not isinstance(record.package_version, str)
            or not _SEMVER.fullmatch(record.package_version)
            or not isinstance(record.package_digest, str)
            or not _DIGEST.fullmatch(record.package_digest)
            or not isinstance(provenance, DiscoveryProvenance)
            or not cls._bounded_text(provenance.published_by, 1, 160)
            or not cls._aware_datetime(provenance.published_at)
            or type(provenance.content_reviewed_on) is not date
            or not cls._bounded_text(
                provenance.educational_use_notice,
                1,
                500,
            )
            or not isinstance(record.source_fingerprint, str)
            or not _DIGEST.fullmatch(record.source_fingerprint)
            or not cls._aware_datetime(record.projected_at)
            or record.projected_at != projected_at
        ):
            cls._projection_invalid(code)
        expected_source = discovery_digest(
            cls._json_meaning(
                {
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
            )
        )
        if record.source_fingerprint != expected_source:
            cls._projection_invalid(code)

    @staticmethod
    def _identifier(value: object) -> bool:
        return isinstance(value, str) and bool(_PLACEMENT_ID.fullmatch(value))

    @staticmethod
    def _aware_datetime(value: object) -> bool:
        return (
            isinstance(value, datetime)
            and value.tzinfo is not None
            and value.utcoffset() is not None
        )

    @staticmethod
    def _bounded_text(value: object, minimum: int, maximum: int) -> bool:
        return (
            isinstance(value, str)
            and minimum <= len(value) <= maximum
            and value == value.strip()
            and not any(character in value for character in ("\x00", "\r", "\n"))
        )

    @classmethod
    def _bounded_text_tuple(
        cls,
        value: object,
        minimum_items: int,
        maximum_items: int,
        maximum_length: int,
    ) -> bool:
        return (
            isinstance(value, tuple)
            and minimum_items <= len(value) <= maximum_items
            and all(cls._bounded_text(item, 1, maximum_length) for item in value)
            and len(value) == len(set(value))
        )

    @staticmethod
    def _valid_topics(value: object) -> bool:
        return (
            isinstance(value, tuple)
            and 1 <= len(value) <= 8
            and all(
                isinstance(topic, str) and bool(_TOPIC.fullmatch(topic))
                for topic in value
            )
            and value == tuple(sorted(value))
            and len(value) == len(set(value))
        )

    @staticmethod
    def _projection_invalid(code: DiscoveryErrorCode):
        raise DiscoveryError(
            code,
            "Learning-opportunity projection integrity failed.",
        )

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
    def _invalid(reference: object, message: str):
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

    @staticmethod
    def _validate_practice_reference(
        request: CreatePracticePlacementRequest,
    ) -> None:
        if (
            not _PLACEMENT_ID.fullmatch(request.practice_id)
            or request.practice_version != "1.0.0"
            or not _DIGEST.fullmatch(request.definition_digest)
        ):
            raise LessonReadError(
                LessonErrorCode.INVALID_PACKAGE,
                "Practice placement reference is invalid.",
                reference=request.placement_id,
            )
