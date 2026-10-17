"""PostgreSQL persistence for the learner-owned Personal workspace."""

from __future__ import annotations

import json

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from ..domain.workspace import PersonalWorkspace
from ..ports.repositories import (
    PersonalWorkspaceIdempotencyConflict,
    PersonalWorkspaceRevisionConflict,
)
from ..ports.workspace_contract import PersonalWorkspaceContractPort


class PostgresPersonalWorkspaceRepository:
    def __init__(self, dsn: str, contract: PersonalWorkspaceContractPort) -> None:
        self._dsn = dsn
        self._contract = contract

    def get_workspace(self, learner_id: str) -> PersonalWorkspace | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT workspace FROM personal_workspace.workspaces
                WHERE learner_id = %s
                """,
                (learner_id,),
            ).fetchone()
        return self._parse(row["workspace"]) if row else None

    def get_mutation_replay(
        self, learner_id: str, idempotency_key: str
    ) -> tuple[str, PersonalWorkspace] | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT request_fingerprint, accepted_workspace
                FROM personal_workspace.mutations
                WHERE learner_id = %s AND idempotency_key = %s
                """,
                (learner_id, idempotency_key),
            ).fetchone()
        if row is None:
            return None
        return (
            str(row["request_fingerprint"]),
            self._parse(row["accepted_workspace"]),
        )

    def save_if_revision(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_revision: int,
        workspace: PersonalWorkspace,
    ) -> PersonalWorkspace:
        document = self._contract.workspace_document(workspace)
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            connection.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (workspace.learner_id,),
            )
            replay = connection.execute(
                """
                SELECT request_fingerprint, accepted_workspace
                FROM personal_workspace.mutations
                WHERE learner_id = %s AND idempotency_key = %s
                """,
                (workspace.learner_id, idempotency_key),
            ).fetchone()
            if replay is not None:
                if str(replay["request_fingerprint"]) != request_fingerprint:
                    raise PersonalWorkspaceIdempotencyConflict()
                return self._parse(replay["accepted_workspace"])
            row = connection.execute(
                """
                SELECT revision FROM personal_workspace.workspaces
                WHERE learner_id = %s FOR UPDATE
                """,
                (workspace.learner_id,),
            ).fetchone()
            current_revision = int(row["revision"]) if row else 1
            if (
                current_revision != expected_revision
                or workspace.revision != expected_revision + 1
            ):
                raise PersonalWorkspaceRevisionConflict()
            if row is None:
                connection.execute(
                    """
                    INSERT INTO personal_workspace.workspaces (
                        workspace_id, learner_id, revision, workspace,
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        workspace.workspace_id,
                        workspace.learner_id,
                        workspace.revision,
                        Jsonb(document),
                        workspace.created_at,
                        workspace.updated_at,
                    ),
                )
            else:
                connection.execute(
                    """
                    UPDATE personal_workspace.workspaces
                    SET revision = %s, workspace = %s, updated_at = %s
                    WHERE learner_id = %s
                    """,
                    (
                        workspace.revision,
                        Jsonb(document),
                        workspace.updated_at,
                        workspace.learner_id,
                    ),
                )
            connection.execute(
                """
                INSERT INTO personal_workspace.mutations (
                    learner_id, workspace_id, idempotency_key,
                    request_fingerprint, accepted_workspace, accepted_revision
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    workspace.learner_id,
                    workspace.workspace_id,
                    idempotency_key,
                    request_fingerprint,
                    Jsonb(document),
                    workspace.revision,
                ),
            )
        return workspace

    def _parse(self, value: object) -> PersonalWorkspace:
        return self._contract.parse_workspace(
            json.dumps(
                value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
        )
