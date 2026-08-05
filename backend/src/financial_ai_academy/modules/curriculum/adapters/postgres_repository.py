"""PostgreSQL Curriculum placement repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row

from ..ports.repositories import PlacementConflict
from ..public import LessonPlacement


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
