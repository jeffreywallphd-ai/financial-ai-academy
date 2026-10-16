"""PostgreSQL persistence for learner-owned Project shells."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from ..domain.project import ProjectShell
from ..ports.project_contract import ProjectContractPort
from ..ports.repositories import ProjectIdempotencyConflict


class PostgresProjectRepository:
    def __init__(self, dsn: str, contract: ProjectContractPort) -> None:
        self._dsn = dsn
        self._contract = contract

    def get_by_idempotency(
        self, learner_id: str, idempotency_key: str
    ) -> tuple[str, ProjectShell] | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT * FROM project.project_shells
                WHERE learner_id = %s AND idempotency_key = %s
                """,
                (learner_id, idempotency_key),
            ).fetchone()
        if row is None:
            return None
        return str(row["request_fingerprint"]), self._from_row(row)

    def create_if_absent(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        shell: ProjectShell,
    ) -> tuple[ProjectShell, bool]:
        document = self._contract.shell_document(shell)
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                INSERT INTO project.project_shells (
                    project_id, learner_id, idempotency_key,
                    request_fingerprint, schema_version, title, charter,
                    origin, lifecycle, revision, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                ON CONFLICT (learner_id, idempotency_key) DO NOTHING
                RETURNING *
                """,
                (
                    shell.project_id,
                    shell.learner_id,
                    idempotency_key,
                    request_fingerprint,
                    shell.schema_version,
                    shell.title,
                    shell.charter,
                    Jsonb(document["origin"]),
                    shell.lifecycle,
                    shell.revision,
                    shell.created_at,
                    shell.updated_at,
                ),
            ).fetchone()
            if row is not None:
                return self._from_row(row), True
            row = connection.execute(
                """
                SELECT * FROM project.project_shells
                WHERE learner_id = %s AND idempotency_key = %s
                """,
                (shell.learner_id, idempotency_key),
            ).fetchone()
        if row is None:
            raise RuntimeError("Project insert did not become visible.")
        if str(row["request_fingerprint"]) != request_fingerprint:
            raise ProjectIdempotencyConflict(
                "Idempotency key maps to another canonical request."
            )
        return self._from_row(row), False

    def get_for_learner(
        self, learner_id: str, project_id: str
    ) -> ProjectShell | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT * FROM project.project_shells
                WHERE learner_id = %s AND project_id = %s
                """,
                (learner_id, project_id),
            ).fetchone()
        return self._from_row(row) if row else None

    def list_for_learner(self, learner_id: str) -> tuple[ProjectShell, ...]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            rows = connection.execute(
                """
                SELECT * FROM project.project_shells
                WHERE learner_id = %s
                ORDER BY created_at, project_id
                """,
                (learner_id,),
            ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def _from_row(self, row: dict[str, Any]) -> ProjectShell:
        created_at = row["created_at"]
        updated_at = row["updated_at"]
        origin = row["origin"]
        if (
            not isinstance(created_at, datetime)
            or not isinstance(updated_at, datetime)
            or not isinstance(origin, dict)
        ):
            raise ValueError("Stored Project shell is invalid.")
        document = {
            "schema_version": str(row["schema_version"]),
            "project_id": str(row["project_id"]),
            "learner_id": str(row["learner_id"]),
            "title": str(row["title"]),
            "charter": str(row["charter"]),
            "origin": origin,
            "lifecycle": str(row["lifecycle"]),
            "revision": row["revision"],
            "created_at": self._timestamp(created_at),
            "updated_at": self._timestamp(updated_at),
        }
        return self._contract.parse_shell(
            json.dumps(
                document,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        )

    @staticmethod
    def _timestamp(value: datetime) -> str:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Stored Project timestamp must include an offset.")
        rendered = (
            value.astimezone(timezone.utc)
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z")
        )
        return rendered.replace(".000000Z", "Z")
