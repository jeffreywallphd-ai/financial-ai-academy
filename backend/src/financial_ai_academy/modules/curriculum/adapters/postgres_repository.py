"""PostgreSQL Curriculum placement repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row

from ..ports.repositories import PlacementConflict
from ..public import AssessmentPlacement, LessonPlacement


class PostgresCurriculumRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

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
