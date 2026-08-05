"""Checksum-protected PostgreSQL migration runner for local and test hosts."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


_BOOTSTRAP = """
CREATE SCHEMA IF NOT EXISTS platform;
CREATE TABLE IF NOT EXISTS platform.schema_migrations (
    migration_id text PRIMARY KEY,
    sha256 char(64) NOT NULL,
    applied_at timestamptz NOT NULL DEFAULT now()
);
"""


@dataclass(frozen=True, slots=True)
class MigrationStatus:
    migration_id: str
    sha256: str


class PostgresMigrationRunner:
    def __init__(self, dsn: str, migrations_dir: Path) -> None:
        self._dsn = dsn
        self._migrations_dir = migrations_dir

    def apply_all(self) -> tuple[MigrationStatus, ...]:
        migrations = sorted(self._migrations_dir.glob("*.up.sql"))
        with psycopg.connect(
            self._dsn, autocommit=True, row_factory=dict_row
        ) as connection:
            with connection.transaction():
                connection.execute(_BOOTSTRAP)
            applied = self._applied(connection)
            for path in migrations:
                migration_id = path.name.removesuffix(".up.sql")
                sql_bytes = path.read_bytes()
                checksum = hashlib.sha256(sql_bytes).hexdigest()
                previous = applied.get(migration_id)
                if previous is not None:
                    if previous != checksum:
                        raise RuntimeError(
                            f"Applied migration changed: {migration_id}"
                        )
                    continue
                with connection.transaction():
                    connection.execute(sql_bytes.decode("utf-8"))
                    connection.execute(
                        """
                        INSERT INTO platform.schema_migrations (
                            migration_id, sha256
                        )
                        VALUES (%s, %s)
                        """,
                        (migration_id, checksum),
                    )
                applied[migration_id] = checksum
        return tuple(
            MigrationStatus(migration_id, checksum)
            for migration_id, checksum in sorted(applied.items())
        )

    def rollback_all(self) -> None:
        with psycopg.connect(
            self._dsn, autocommit=True, row_factory=dict_row
        ) as connection:
            with connection.transaction():
                connection.execute(_BOOTSTRAP)
            applied = self._applied(connection)
            for migration_id in sorted(applied, reverse=True):
                path = self._migrations_dir / f"{migration_id}.down.sql"
                if not path.is_file():
                    raise RuntimeError(
                        f"Downgrade migration is missing: {migration_id}"
                    )
                with connection.transaction():
                    connection.execute(path.read_text(encoding="utf-8"))
                    connection.execute(
                        """
                        DELETE FROM platform.schema_migrations
                        WHERE migration_id = %s
                        """,
                        (migration_id,),
                    )

    @staticmethod
    def _applied(connection: psycopg.Connection) -> dict[str, str]:
        rows = connection.execute(
            """
            SELECT migration_id, sha256
            FROM platform.schema_migrations
            ORDER BY migration_id
            """
        ).fetchall()
        return {
            str(row["migration_id"]): str(row["sha256"]) for row in rows
        }
