"""Project-owned persistence contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..domain.project import ProjectShell
from ..domain.workspace import ProjectSnapshot, ProjectWorkspace


class ProjectIdempotencyConflict(RuntimeError):
    pass


class ProjectRevisionConflict(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class StoredProjectArtifact:
    learner_id: str
    project_id: str
    artifact_id: str
    artifact_version: int
    object_key: str
    content_digest: str
    byte_count: int


@dataclass(frozen=True, slots=True)
class StoredProjectSnapshot:
    snapshot: ProjectSnapshot
    workspace: ProjectWorkspace


class ProjectRepositoryPort(Protocol):
    def get_by_idempotency(
        self, learner_id: str, idempotency_key: str
    ) -> tuple[str, ProjectShell] | None: ...

    def create_if_absent(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        shell: ProjectShell,
    ) -> tuple[ProjectShell, bool]: ...

    def get_for_learner(
        self, learner_id: str, project_id: str
    ) -> ProjectShell | None: ...

    def list_for_learner(self, learner_id: str) -> tuple[ProjectShell, ...]: ...

    def get_or_create_workspace(
        self, candidate: ProjectWorkspace
    ) -> ProjectWorkspace: ...

    def get_workspace(
        self, learner_id: str, project_id: str
    ) -> ProjectWorkspace | None: ...

    def get_workspace_mutation_replay(
        self,
        learner_id: str,
        project_id: str,
        idempotency_key: str,
    ) -> tuple[str, ProjectWorkspace] | None: ...

    def save_workspace_if_revision(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_revision: int,
        workspace: ProjectWorkspace,
        artifact: StoredProjectArtifact | None = None,
    ) -> ProjectWorkspace: ...

    def get_artifact(
        self,
        learner_id: str,
        project_id: str,
        artifact_id: str,
        artifact_version: int,
    ) -> StoredProjectArtifact | None: ...

    def get_snapshot_by_idempotency(
        self,
        learner_id: str,
        project_id: str,
        idempotency_key: str,
    ) -> tuple[str, StoredProjectSnapshot] | None: ...

    def create_snapshot_if_absent(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_workspace_revision: int,
        snapshot: ProjectSnapshot,
        workspace: ProjectWorkspace,
    ) -> StoredProjectSnapshot: ...

    def get_snapshot(
        self, learner_id: str, project_id: str, snapshot_id: str
    ) -> StoredProjectSnapshot | None: ...

    def list_snapshots(
        self, learner_id: str, project_id: str
    ) -> tuple[ProjectSnapshot, ...]: ...
