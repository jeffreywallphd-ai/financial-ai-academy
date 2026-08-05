"""PostgreSQL Content metadata repository."""

from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from ..domain.models import StoredLessonPackage
from ..ports.repositories import PackageVersionConflict
from .serialization import lesson_from_dict, lesson_to_dict


class PostgresContentRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def get(
        self, package_id: str, package_version: str
    ) -> StoredLessonPackage | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT lesson, object_key
                FROM content.lesson_package_versions
                WHERE package_id = %s AND package_version = %s
                """,
                (package_id, package_version),
            ).fetchone()
        return self._from_row(row) if row else None

    def save_if_absent(
        self, package: StoredLessonPackage
    ) -> tuple[StoredLessonPackage, bool]:
        lesson = package.lesson
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                INSERT INTO content.lesson_package_versions (
                    package_id,
                    package_version,
                    package_digest,
                    publication_state,
                    published_at,
                    object_key,
                    lesson
                )
                VALUES (%s, %s, %s, 'published', %s, %s, %s)
                ON CONFLICT (package_id, package_version) DO NOTHING
                RETURNING lesson, object_key
                """,
                (
                    lesson.package_id,
                    lesson.package_version,
                    lesson.package_digest,
                    lesson.provenance.published_at,
                    package.object_key,
                    Jsonb(lesson_to_dict(lesson)),
                ),
            ).fetchone()
            if row is not None:
                return self._from_row(row), True
            row = connection.execute(
                """
                SELECT lesson, object_key
                FROM content.lesson_package_versions
                WHERE package_id = %s AND package_version = %s
                """,
                (lesson.package_id, lesson.package_version),
            ).fetchone()
        if row is None:
            raise RuntimeError("Publication insert did not become visible.")
        existing = self._from_row(row)
        if existing.lesson.package_digest != lesson.package_digest:
            raise PackageVersionConflict(
                "Package identity and version already map to another digest."
            )
        return existing, False

    @staticmethod
    def _from_row(row: dict[str, Any]) -> StoredLessonPackage:
        return StoredLessonPackage(
            lesson=lesson_from_dict(row["lesson"]),
            object_key=str(row["object_key"]),
        )
