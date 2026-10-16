"""PostgreSQL persistence for learner-owned Project state."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from ..domain.project import ProjectShell
from ..domain.workspace import ProjectSnapshot, ProjectWorkspace
from ..ports.project_contract import ProjectContractPort
from ..ports.repositories import (
    ProjectIdempotencyConflict,
    ProjectRevisionConflict,
    StoredProjectArtifact,
    StoredProjectSnapshot,
)


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

    def get_or_create_workspace(
        self, candidate: ProjectWorkspace
    ) -> ProjectWorkspace:
        document = self._contract.workspace_document(candidate)
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            connection.execute(
                """
                INSERT INTO project.project_workspaces (
                    project_id, learner_id, workspace_revision, workspace,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (project_id) DO NOTHING
                """,
                (
                    candidate.project_id,
                    candidate.learner_id,
                    candidate.workspace_revision,
                    Jsonb(document),
                    candidate.created_at,
                    candidate.updated_at,
                ),
            )
            row = connection.execute(
                """
                SELECT workspace FROM project.project_workspaces
                WHERE learner_id = %s AND project_id = %s
                """,
                (candidate.learner_id, candidate.project_id),
            ).fetchone()
        if row is None:
            raise RuntimeError("Project workspace insert did not become visible.")
        return self._workspace_from_row(row)

    def get_workspace(
        self, learner_id: str, project_id: str
    ) -> ProjectWorkspace | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT workspace FROM project.project_workspaces
                WHERE learner_id = %s AND project_id = %s
                """,
                (learner_id, project_id),
            ).fetchone()
        return self._workspace_from_row(row) if row else None

    def get_workspace_mutation_replay(
        self,
        learner_id: str,
        project_id: str,
        idempotency_key: str,
    ) -> tuple[str, ProjectWorkspace] | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT request_fingerprint, accepted_workspace
                FROM project.project_workspace_mutations
                WHERE learner_id = %s AND project_id = %s
                  AND idempotency_key = %s
                """,
                (learner_id, project_id, idempotency_key),
            ).fetchone()
        if row is None:
            return None
        return (
            str(row["request_fingerprint"]),
            self._parse_workspace(row["accepted_workspace"]),
        )

    def save_workspace_if_revision(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_revision: int,
        workspace: ProjectWorkspace,
        artifact: StoredProjectArtifact | None = None,
    ) -> ProjectWorkspace:
        document = self._contract.workspace_document(workspace)
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT workspace_revision FROM project.project_workspaces
                WHERE learner_id = %s AND project_id = %s
                FOR UPDATE
                """,
                (workspace.learner_id, workspace.project_id),
            ).fetchone()
            replay = connection.execute(
                """
                SELECT request_fingerprint, accepted_workspace
                FROM project.project_workspace_mutations
                WHERE learner_id = %s AND project_id = %s
                  AND idempotency_key = %s
                """,
                (
                    workspace.learner_id,
                    workspace.project_id,
                    idempotency_key,
                ),
            ).fetchone()
            if replay is not None:
                if str(replay["request_fingerprint"]) != request_fingerprint:
                    raise ProjectIdempotencyConflict(
                        "Idempotency key maps to another workspace mutation."
                    )
                return self._parse_workspace(replay["accepted_workspace"])
            if row is None or int(row["workspace_revision"]) != expected_revision:
                raise ProjectRevisionConflict("Workspace revision is stale.")
            if workspace.workspace_revision != expected_revision + 1:
                raise ProjectRevisionConflict("Workspace revision is invalid.")
            if artifact is not None:
                connection.execute(
                    """
                    INSERT INTO project.project_artifact_objects (
                        learner_id, project_id, artifact_id, artifact_version,
                        object_key, content_digest, byte_count
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        artifact.learner_id,
                        artifact.project_id,
                        artifact.artifact_id,
                        artifact.artifact_version,
                        artifact.object_key,
                        artifact.content_digest,
                        artifact.byte_count,
                    ),
                )
            connection.execute(
                """
                UPDATE project.project_workspaces
                SET workspace_revision = %s, workspace = %s, updated_at = %s
                WHERE learner_id = %s AND project_id = %s
                """,
                (
                    workspace.workspace_revision,
                    Jsonb(document),
                    workspace.updated_at,
                    workspace.learner_id,
                    workspace.project_id,
                ),
            )
            connection.execute(
                """
                INSERT INTO project.project_workspace_mutations (
                    learner_id, project_id, idempotency_key,
                    request_fingerprint, accepted_workspace, accepted_revision
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    workspace.learner_id,
                    workspace.project_id,
                    idempotency_key,
                    request_fingerprint,
                    Jsonb(document),
                    workspace.workspace_revision,
                ),
            )
        return workspace

    def get_artifact(
        self,
        learner_id: str,
        project_id: str,
        artifact_id: str,
        artifact_version: int,
    ) -> StoredProjectArtifact | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT * FROM project.project_artifact_objects
                WHERE learner_id = %s AND project_id = %s
                  AND artifact_id = %s AND artifact_version = %s
                """,
                (learner_id, project_id, artifact_id, artifact_version),
            ).fetchone()
        return self._artifact_from_row(row) if row else None

    def get_snapshot_by_idempotency(
        self,
        learner_id: str,
        project_id: str,
        idempotency_key: str,
    ) -> tuple[str, StoredProjectSnapshot] | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT * FROM project.project_snapshots
                WHERE learner_id = %s AND project_id = %s
                  AND idempotency_key = %s
                """,
                (learner_id, project_id, idempotency_key),
            ).fetchone()
        if row is None:
            return None
        return str(row["request_fingerprint"]), self._snapshot_from_row(row)

    def create_snapshot_if_absent(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_workspace_revision: int,
        snapshot: ProjectSnapshot,
        workspace: ProjectWorkspace,
    ) -> StoredProjectSnapshot:
        snapshot_document = self._contract.snapshot_document(snapshot)
        workspace_document = self._contract.workspace_document(workspace)
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            current = connection.execute(
                """
                SELECT workspace_revision FROM project.project_workspaces
                WHERE learner_id = %s AND project_id = %s
                FOR UPDATE
                """,
                (workspace.learner_id, workspace.project_id),
            ).fetchone()
            replay = connection.execute(
                """
                SELECT * FROM project.project_snapshots
                WHERE learner_id = %s AND project_id = %s
                  AND idempotency_key = %s
                """,
                (workspace.learner_id, workspace.project_id, idempotency_key),
            ).fetchone()
            if replay is not None:
                if str(replay["request_fingerprint"]) != request_fingerprint:
                    raise ProjectIdempotencyConflict(
                        "Idempotency key maps to another snapshot request."
                    )
                return self._snapshot_from_row(replay)
            if (
                current is None
                or int(current["workspace_revision"])
                != expected_workspace_revision
                or workspace.workspace_revision != expected_workspace_revision
            ):
                raise ProjectRevisionConflict("Workspace revision is stale.")
            connection.execute(
                """
                INSERT INTO project.project_snapshots (
                    snapshot_id, learner_id, project_id, idempotency_key,
                    request_fingerprint, snapshot_digest, workspace_revision,
                    snapshot, workspace, closed_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    snapshot.snapshot_id,
                    workspace.learner_id,
                    workspace.project_id,
                    idempotency_key,
                    request_fingerprint,
                    snapshot.snapshot_digest,
                    workspace.workspace_revision,
                    Jsonb(snapshot_document),
                    Jsonb(workspace_document),
                    snapshot.closed_at,
                ),
            )
        return StoredProjectSnapshot(snapshot, workspace)

    def get_snapshot(
        self, learner_id: str, project_id: str, snapshot_id: str
    ) -> StoredProjectSnapshot | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT * FROM project.project_snapshots
                WHERE learner_id = %s AND project_id = %s AND snapshot_id = %s
                """,
                (learner_id, project_id, snapshot_id),
            ).fetchone()
        return self._snapshot_from_row(row) if row else None

    def list_snapshots(
        self, learner_id: str, project_id: str
    ) -> tuple[ProjectSnapshot, ...]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            rows = connection.execute(
                """
                SELECT snapshot FROM project.project_snapshots
                WHERE learner_id = %s AND project_id = %s
                ORDER BY closed_at, snapshot_id
                """,
                (learner_id, project_id),
            ).fetchall()
        return tuple(self._parse_snapshot(row["snapshot"]) for row in rows)

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

    def _workspace_from_row(self, row: dict[str, Any]) -> ProjectWorkspace:
        return self._parse_workspace(row["workspace"])

    def _snapshot_from_row(self, row: dict[str, Any]) -> StoredProjectSnapshot:
        return StoredProjectSnapshot(
            self._parse_snapshot(row["snapshot"]),
            self._parse_workspace(row["workspace"]),
        )

    def _parse_workspace(self, value: object) -> ProjectWorkspace:
        return self._contract.parse_workspace(self._json_bytes(value))

    def _parse_snapshot(self, value: object) -> ProjectSnapshot:
        return self._contract.parse_snapshot(self._json_bytes(value))

    @staticmethod
    def _artifact_from_row(row: dict[str, Any]) -> StoredProjectArtifact:
        return StoredProjectArtifact(
            learner_id=str(row["learner_id"]),
            project_id=str(row["project_id"]),
            artifact_id=str(row["artifact_id"]),
            artifact_version=int(row["artifact_version"]),
            object_key=str(row["object_key"]),
            content_digest=str(row["content_digest"]),
            byte_count=int(row["byte_count"]),
        )

    @staticmethod
    def _json_bytes(value: object) -> bytes:
        if not isinstance(value, dict):
            raise ValueError("Stored Project document is invalid.")
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

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
