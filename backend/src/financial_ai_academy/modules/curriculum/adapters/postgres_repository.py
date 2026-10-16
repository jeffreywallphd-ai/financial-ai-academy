"""PostgreSQL Curriculum placement repository."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from ..ports.repositories import (
    CurriculumGraphConflict,
    OpportunityConflict,
    PlacementConflict,
    PracticeReviewConflict,
)
from ..public import (
    AssessmentPlacement,
    CurriculumGraph,
    DiscoveryProvenance,
    LearningOpportunityRecord,
    LessonOpportunityClassification,
    LessonPlacement,
    OpportunityAvailability,
    OpportunityKind,
    OpportunityLevel,
    PracticePlacement,
    PracticeReviewDestination,
    PracticeReviewState,
    PracticeReviewTarget,
    PracticeReviewUnavailableReason,
    curriculum_graph_from_mapping,
    curriculum_graph_payload,
)


class PostgresCurriculumRepository:
    def __init__(
        self,
        dsn: str,
        *,
        before_projection_commit: Callable[[], None] | None = None,
    ) -> None:
        self._dsn = dsn
        self._before_projection_commit = before_projection_commit

    def get(self, placement_id: str) -> LessonPlacement | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT
                    placement_id,
                    package_id,
                    package_version,
                    package_digest,
                    created_at
                FROM curriculum.lesson_placements
                WHERE placement_id = %s
                """,
                (placement_id,),
            ).fetchone()
        return self._from_row(row) if row else None

    def save_if_absent(
        self, placement: LessonPlacement
    ) -> tuple[LessonPlacement, bool]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                INSERT INTO curriculum.lesson_placements (
                    placement_id,
                    package_id,
                    package_version,
                    package_digest,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (placement_id) DO NOTHING
                RETURNING
                    placement_id,
                    package_id,
                    package_version,
                    package_digest,
                    created_at
                """,
                (
                    placement.placement_id,
                    placement.package_id,
                    placement.package_version,
                    placement.package_digest,
                    placement.created_at,
                ),
            ).fetchone()
            if row is not None:
                return self._from_row(row), True
            row = connection.execute(
                """
                SELECT
                    placement_id,
                    package_id,
                    package_version,
                    package_digest,
                    created_at
                FROM curriculum.lesson_placements
                WHERE placement_id = %s
                """,
                (placement.placement_id,),
            ).fetchone()
        if row is None:
            raise RuntimeError("Placement insert did not become visible.")
        existing = self._from_row(row)
        if (
            existing.package_id,
            existing.package_version,
            existing.package_digest,
        ) != (
            placement.package_id,
            placement.package_version,
            placement.package_digest,
        ):
            raise PlacementConflict(
                "Placement identity already maps to another exact lesson."
            )
        return existing, False

    def get_assessment(
        self, placement_id: str
    ) -> AssessmentPlacement | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT
                    placement_id,
                    package_id,
                    package_version,
                    package_digest,
                    assessment_id,
                    assessment_version,
                    definition_digest,
                    item_id,
                    item_version,
                    scoring_policy_id,
                    scoring_policy_version,
                    created_at
                FROM curriculum.assessment_placements
                WHERE placement_id = %s
                """,
                (placement_id,),
            ).fetchone()
        return self._assessment_from_row(row) if row else None

    def save_assessment_if_absent(
        self, placement: AssessmentPlacement
    ) -> tuple[AssessmentPlacement, bool]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                INSERT INTO curriculum.assessment_placements (
                    placement_id,
                    package_id,
                    package_version,
                    package_digest,
                    assessment_id,
                    assessment_version,
                    definition_digest,
                    item_id,
                    item_version,
                    scoring_policy_id,
                    scoring_policy_version,
                    created_at
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (placement_id) DO NOTHING
                RETURNING *
                """,
                (
                    placement.placement_id,
                    placement.package_id,
                    placement.package_version,
                    placement.package_digest,
                    placement.assessment_id,
                    placement.assessment_version,
                    placement.definition_digest,
                    placement.item_id,
                    placement.item_version,
                    placement.scoring_policy_id,
                    placement.scoring_policy_version,
                    placement.created_at,
                ),
            ).fetchone()
            if row is not None:
                return self._assessment_from_row(row), True
            row = connection.execute(
                """
                SELECT * FROM curriculum.assessment_placements
                WHERE placement_id = %s
                """,
                (placement.placement_id,),
            ).fetchone()
        if row is None:
            raise RuntimeError("Assessment placement insert did not become visible.")
        existing = self._assessment_from_row(row)
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
            raise PlacementConflict(
                "Placement identity already maps to another assessment."
            )
        return existing, False

    def get_practice(self, placement_id: str) -> PracticePlacement | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT
                    placement_id,
                    package_id,
                    package_version,
                    package_digest,
                    practice_id,
                    practice_version,
                    definition_digest,
                    created_at
                FROM curriculum.practice_placements
                WHERE placement_id = %s
                """,
                (placement_id,),
            ).fetchone()
        return self._practice_from_row(row) if row else None

    def save_practice_if_absent(
        self, placement: PracticePlacement
    ) -> tuple[PracticePlacement, bool]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                INSERT INTO curriculum.practice_placements (
                    placement_id,
                    package_id,
                    package_version,
                    package_digest,
                    practice_id,
                    practice_version,
                    definition_digest,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (placement_id) DO NOTHING
                RETURNING *
                """,
                (
                    placement.placement_id,
                    placement.package_id,
                    placement.package_version,
                    placement.package_digest,
                    placement.practice_id,
                    placement.practice_version,
                    placement.definition_digest,
                    placement.created_at,
                ),
            ).fetchone()
            if row is not None:
                return self._practice_from_row(row), True
            row = connection.execute(
                """
                SELECT * FROM curriculum.practice_placements
                WHERE placement_id = %s
                """,
                (placement.placement_id,),
            ).fetchone()
        if row is None:
            raise RuntimeError("Practice placement insert did not become visible.")
        existing = self._practice_from_row(row)
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
            raise PlacementConflict(
                "Placement identity already maps to another practice."
            )
        return existing, False

    def get_practice_review_target(
        self,
        practice_placement_id: str,
        resource_id: str,
        resource_version: str,
        resource_digest: str,
    ) -> PracticeReviewTarget | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT *
                FROM curriculum.practice_review_targets
                WHERE practice_placement_id = %s
                  AND resource_id = %s
                  AND resource_version = %s
                  AND resource_digest = %s
                """,
                (
                    practice_placement_id,
                    resource_id,
                    resource_version,
                    resource_digest,
                ),
            ).fetchone()
        return self._practice_review_target_from_row(row) if row else None

    def save_practice_review_target_if_absent(
        self, target: PracticeReviewTarget
    ) -> tuple[PracticeReviewTarget, bool]:
        destination = target.destination
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                INSERT INTO curriculum.practice_review_targets (
                    practice_placement_id,
                    resource_id,
                    resource_version,
                    resource_digest,
                    resource_title,
                    state,
                    destination_placement_id,
                    destination_package_id,
                    destination_package_version,
                    destination_package_digest,
                    destination_section_id,
                    unavailable_reason
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (
                    practice_placement_id,
                    resource_id,
                    resource_version,
                    resource_digest
                ) DO NOTHING
                RETURNING *
                """,
                (
                    target.practice_placement_id,
                    target.resource_id,
                    target.resource_version,
                    target.resource_digest,
                    target.resource_title,
                    target.state.value,
                    destination.placement_id if destination else None,
                    destination.package_id if destination else None,
                    destination.package_version if destination else None,
                    destination.package_digest if destination else None,
                    destination.section_id if destination else None,
                    (
                        target.unavailable_reason.value
                        if target.unavailable_reason
                        else None
                    ),
                ),
            ).fetchone()
            if row is not None:
                return self._practice_review_target_from_row(row), True
            row = connection.execute(
                """
                SELECT *
                FROM curriculum.practice_review_targets
                WHERE practice_placement_id = %s
                  AND resource_id = %s
                  AND resource_version = %s
                  AND resource_digest = %s
                """,
                (
                    target.practice_placement_id,
                    target.resource_id,
                    target.resource_version,
                    target.resource_digest,
                ),
            ).fetchone()
        if row is None:
            raise RuntimeError("Review target insert did not become visible.")
        existing = self._practice_review_target_from_row(row)
        if existing != target:
            raise PracticeReviewConflict(
                "Review resource identity already maps to different meaning."
            )
        return existing, False

    def get_graph_exact(
        self,
        curriculum_id: str,
        curriculum_version: str,
    ) -> CurriculumGraph | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT
                    curriculum_id,
                    curriculum_version,
                    graph_digest,
                    published_at,
                    graph_payload
                FROM curriculum.curriculum_graph_versions
                WHERE curriculum_id = %s AND curriculum_version = %s
                """,
                (curriculum_id, curriculum_version),
            ).fetchone()
        return self._graph_from_row(row) if row else None

    def save_graph_if_absent(
        self,
        graph: CurriculumGraph,
    ) -> tuple[CurriculumGraph, bool]:
        payload = curriculum_graph_payload(graph)
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                INSERT INTO curriculum.curriculum_graph_versions (
                    curriculum_id,
                    curriculum_version,
                    graph_digest,
                    published_at,
                    graph_payload
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (curriculum_id, curriculum_version) DO NOTHING
                RETURNING
                    curriculum_id,
                    curriculum_version,
                    graph_digest,
                    published_at,
                    graph_payload
                """,
                (
                    graph.curriculum_id,
                    graph.curriculum_version,
                    graph.graph_digest,
                    graph.published_at,
                    Jsonb(payload),
                ),
            ).fetchone()
            if row is not None:
                return self._graph_from_row(row), True
            row = connection.execute(
                """
                SELECT
                    curriculum_id,
                    curriculum_version,
                    graph_digest,
                    published_at,
                    graph_payload
                FROM curriculum.curriculum_graph_versions
                WHERE curriculum_id = %s AND curriculum_version = %s
                """,
                (graph.curriculum_id, graph.curriculum_version),
            ).fetchone()
        if row is None:
            raise RuntimeError("Curriculum graph insert did not become visible.")
        existing = self._graph_from_row(row)
        if existing != graph:
            raise CurriculumGraphConflict(
                "Curriculum graph identity already maps to different meaning."
            )
        return existing, False

    def get_opportunity_classification(
        self,
        opportunity_id: str,
    ) -> LessonOpportunityClassification | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT
                    opportunity_id,
                    placement_id,
                    summary,
                    topics,
                    level,
                    estimated_minutes,
                    prerequisite_summary,
                    availability,
                    availability_reason,
                    created_at
                FROM curriculum.lesson_opportunity_classifications
                WHERE opportunity_id = %s
                """,
                (opportunity_id,),
            ).fetchone()
        return self._classification_from_row(row) if row else None

    def save_opportunity_classification_if_absent(
        self,
        classification: LessonOpportunityClassification,
    ) -> tuple[LessonOpportunityClassification, bool]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                INSERT INTO curriculum.lesson_opportunity_classifications (
                    opportunity_id,
                    placement_id,
                    summary,
                    topics,
                    level,
                    estimated_minutes,
                    prerequisite_summary,
                    availability,
                    availability_reason,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (opportunity_id) DO NOTHING
                RETURNING *
                """,
                (
                    classification.opportunity_id,
                    classification.placement_id,
                    classification.summary,
                    list(classification.topics),
                    classification.level.value,
                    classification.estimated_minutes,
                    classification.prerequisite_summary,
                    classification.availability.value,
                    classification.availability_reason,
                    classification.created_at,
                ),
            ).fetchone()
            if row is not None:
                return self._classification_from_row(row), True
            row = connection.execute(
                """
                SELECT *
                FROM curriculum.lesson_opportunity_classifications
                WHERE opportunity_id = %s
                """,
                (classification.opportunity_id,),
            ).fetchone()
        if row is None:
            raise RuntimeError(
                "Opportunity classification insert did not become visible."
            )
        existing = self._classification_from_row(row)
        fields = (
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
            getattr(existing, field) != getattr(classification, field)
            for field in fields
        ):
            raise OpportunityConflict(
                "Opportunity identity already maps to another classification."
            )
        return existing, False

    def list_opportunity_classifications(
        self,
    ) -> tuple[LessonOpportunityClassification, ...]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM curriculum.lesson_opportunity_classifications
                ORDER BY opportunity_id
                LIMIT 501
                """
            ).fetchall()
        return tuple(self._classification_from_row(row) for row in rows)

    def replace_discovery_projection(
        self,
        generation: str,
        projected_at: datetime,
        records: tuple[LearningOpportunityRecord, ...],
    ) -> None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.transaction():
                connection.execute(
                    """
                    SELECT pg_advisory_xact_lock(
                        hashtextextended('curriculum.discovery-projection', 0)
                    )
                    """
                )
                connection.execute(
                    "DELETE FROM curriculum.discovery_projection_records"
                )
                connection.execute(
                    """
                    INSERT INTO curriculum.discovery_projection_state (
                        singleton,
                        generation,
                        projected_at,
                        record_count
                    )
                    VALUES (true, %s, %s, %s)
                    ON CONFLICT (singleton) DO UPDATE SET
                        generation = EXCLUDED.generation,
                        projected_at = EXCLUDED.projected_at,
                        record_count = EXCLUDED.record_count
                    """,
                    (generation, projected_at, len(records)),
                )
                for ordinal, record in enumerate(records):
                    connection.execute(
                        """
                        INSERT INTO curriculum.discovery_projection_records (
                            generation,
                            ordinal,
                            schema_version,
                            opportunity_id,
                            placement_id,
                            destination,
                            kind,
                            title,
                            summary,
                            objectives,
                            topics,
                            level,
                            estimated_minutes,
                            prerequisite_summary,
                            availability,
                            availability_reason,
                            package_id,
                            package_version,
                            package_digest,
                            published_by,
                            published_at,
                            content_reviewed_on,
                            educational_use_notice,
                            source_fingerprint
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            generation,
                            ordinal,
                            record.schema_version,
                            record.opportunity_id,
                            record.placement_id,
                            record.destination,
                            record.kind.value,
                            record.title,
                            record.summary,
                            list(record.objectives),
                            list(record.topics),
                            record.level.value,
                            record.estimated_minutes,
                            record.prerequisite_summary,
                            record.availability.value,
                            record.availability_reason,
                            record.package_id,
                            record.package_version,
                            record.package_digest,
                            record.provenance.published_by,
                            record.provenance.published_at,
                            record.provenance.content_reviewed_on,
                            record.provenance.educational_use_notice,
                            record.source_fingerprint,
                        ),
                    )
                if self._before_projection_commit is not None:
                    self._before_projection_commit()

    def read_discovery_projection(
        self,
    ) -> tuple[
        str,
        datetime,
        tuple[LearningOpportunityRecord, ...],
    ] | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            rows = connection.execute(
                """
                SELECT
                    state.generation,
                    state.projected_at,
                    state.record_count,
                    record.ordinal,
                    record.schema_version,
                    record.opportunity_id,
                    record.placement_id,
                    record.destination,
                    record.kind,
                    record.title,
                    record.summary,
                    record.objectives,
                    record.topics,
                    record.level,
                    record.estimated_minutes,
                    record.prerequisite_summary,
                    record.availability,
                    record.availability_reason,
                    record.package_id,
                    record.package_version,
                    record.package_digest,
                    record.published_by,
                    record.published_at,
                    record.content_reviewed_on,
                    record.educational_use_notice,
                    record.source_fingerprint
                FROM curriculum.discovery_projection_state AS state
                LEFT JOIN curriculum.discovery_projection_records AS record
                    ON record.generation = state.generation
                WHERE state.singleton = true
                ORDER BY record.ordinal
                """
            ).fetchall()
        if not rows:
            return None
        generation = str(rows[0]["generation"])
        projected_at = rows[0]["projected_at"]
        if not isinstance(projected_at, datetime):
            raise ValueError("Discovery projection timestamp is invalid.")
        records = tuple(
            self._discovery_record_from_row(row, projected_at)
            for row in rows
            if row["opportunity_id"] is not None
        )
        record_count = rows[0]["record_count"]
        if (
            not isinstance(record_count, int)
            or isinstance(record_count, bool)
            or record_count != len(records)
        ):
            raise ValueError("Discovery projection count is invalid.")
        return generation, projected_at, records

    @staticmethod
    def _from_row(row: dict[str, Any]) -> LessonPlacement:
        created_at = row["created_at"]
        if not isinstance(created_at, datetime):
            raise ValueError("Placement timestamp is invalid.")
        return LessonPlacement(
            placement_id=str(row["placement_id"]),
            package_id=str(row["package_id"]),
            package_version=str(row["package_version"]),
            package_digest=str(row["package_digest"]),
            created_at=created_at,
        )

    @staticmethod
    def _assessment_from_row(row: dict[str, Any]) -> AssessmentPlacement:
        created_at = row["created_at"]
        if not isinstance(created_at, datetime):
            raise ValueError("Assessment placement timestamp is invalid.")
        return AssessmentPlacement(
            placement_id=str(row["placement_id"]),
            package_id=str(row["package_id"]),
            package_version=str(row["package_version"]),
            package_digest=str(row["package_digest"]),
            assessment_id=str(row["assessment_id"]),
            assessment_version=str(row["assessment_version"]),
            definition_digest=str(row["definition_digest"]),
            item_id=str(row["item_id"]),
            item_version=str(row["item_version"]),
            scoring_policy_id=str(row["scoring_policy_id"]),
            scoring_policy_version=str(row["scoring_policy_version"]),
            created_at=created_at,
        )

    @staticmethod
    def _practice_from_row(row: dict[str, Any]) -> PracticePlacement:
        created_at = row["created_at"]
        if not isinstance(created_at, datetime):
            raise ValueError("Practice placement timestamp is invalid.")
        return PracticePlacement(
            placement_id=str(row["placement_id"]),
            package_id=str(row["package_id"]),
            package_version=str(row["package_version"]),
            package_digest=str(row["package_digest"]),
            practice_id=str(row["practice_id"]),
            practice_version=str(row["practice_version"]),
            definition_digest=str(row["definition_digest"]),
            created_at=created_at,
        )

    @staticmethod
    def _practice_review_target_from_row(
        row: dict[str, Any],
    ) -> PracticeReviewTarget:
        state = PracticeReviewState(str(row["state"]))
        destination = None
        if state is PracticeReviewState.AVAILABLE:
            destination = PracticeReviewDestination(
                placement_id=str(row["destination_placement_id"]),
                package_id=str(row["destination_package_id"]),
                package_version=str(row["destination_package_version"]),
                package_digest=str(row["destination_package_digest"]),
                section_id=(
                    str(row["destination_section_id"])
                    if row["destination_section_id"] is not None
                    else None
                ),
            )
        reason = (
            PracticeReviewUnavailableReason(str(row["unavailable_reason"]))
            if row["unavailable_reason"] is not None
            else None
        )
        return PracticeReviewTarget(
            schema_version="1.0.0",
            practice_placement_id=str(row["practice_placement_id"]),
            resource_id=str(row["resource_id"]),
            resource_version=str(row["resource_version"]),
            resource_digest=str(row["resource_digest"]),
            resource_title=str(row["resource_title"]),
            state=state,
            destination=destination,
            unavailable_reason=reason,
        )

    @staticmethod
    def _graph_from_row(row: dict[str, Any]) -> CurriculumGraph:
        payload = row["graph_payload"]
        published_at = row["published_at"]
        if not isinstance(payload, dict) or not isinstance(
            published_at, datetime
        ):
            raise ValueError("Stored curriculum graph is invalid.")
        graph = curriculum_graph_from_mapping(payload)
        if (
            str(row["curriculum_id"]) != graph.curriculum_id
            or str(row["curriculum_version"]) != graph.curriculum_version
            or str(row["graph_digest"]) != graph.graph_digest
            or published_at != graph.published_at
        ):
            raise ValueError("Stored curriculum graph root fields do not match.")
        return graph

    @staticmethod
    def _classification_from_row(
        row: dict[str, Any],
    ) -> LessonOpportunityClassification:
        created_at = row["created_at"]
        if not isinstance(created_at, datetime):
            raise ValueError("Opportunity classification timestamp is invalid.")
        return LessonOpportunityClassification(
            opportunity_id=str(row["opportunity_id"]),
            placement_id=str(row["placement_id"]),
            summary=str(row["summary"]),
            topics=PostgresCurriculumRepository._text_tuple(row["topics"]),
            level=OpportunityLevel(str(row["level"])),
            estimated_minutes=int(row["estimated_minutes"]),
            prerequisite_summary=str(row["prerequisite_summary"]),
            availability=OpportunityAvailability(str(row["availability"])),
            availability_reason=str(row["availability_reason"]),
            created_at=created_at,
        )

    @staticmethod
    def _discovery_record_from_row(
        row: dict[str, Any],
        projected_at: datetime,
    ) -> LearningOpportunityRecord:
        published_at = row["published_at"]
        reviewed_on = row["content_reviewed_on"]
        if not isinstance(published_at, datetime) or type(reviewed_on) is not date:
            raise ValueError("Discovery provenance timestamp is invalid.")
        return LearningOpportunityRecord(
            schema_version=str(row["schema_version"]),
            opportunity_id=str(row["opportunity_id"]),
            placement_id=str(row["placement_id"]),
            destination=str(row["destination"]),
            kind=OpportunityKind(str(row["kind"])),
            title=str(row["title"]),
            summary=str(row["summary"]),
            objectives=PostgresCurriculumRepository._text_tuple(
                row["objectives"]
            ),
            topics=PostgresCurriculumRepository._text_tuple(row["topics"]),
            level=OpportunityLevel(str(row["level"])),
            estimated_minutes=int(row["estimated_minutes"]),
            prerequisite_summary=str(row["prerequisite_summary"]),
            availability=OpportunityAvailability(str(row["availability"])),
            availability_reason=str(row["availability_reason"]),
            package_id=str(row["package_id"]),
            package_version=str(row["package_version"]),
            package_digest=str(row["package_digest"]),
            provenance=DiscoveryProvenance(
                published_by=str(row["published_by"]),
                published_at=published_at,
                content_reviewed_on=reviewed_on,
                educational_use_notice=str(row["educational_use_notice"]),
            ),
            source_fingerprint=str(row["source_fingerprint"]),
            projected_at=projected_at,
        )

    @staticmethod
    def _text_tuple(value: object) -> tuple[str, ...]:
        if not isinstance(value, (list, tuple)) or any(
            not isinstance(item, str) for item in value
        ):
            raise ValueError("Stored discovery text array is invalid.")
        return tuple(value)
