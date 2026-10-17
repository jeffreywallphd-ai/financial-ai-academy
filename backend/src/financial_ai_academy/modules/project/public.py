"""Stable transport-neutral Project workspace operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Literal, Protocol

from .domain.project import (
    IndependentProjectOrigin,
    LearningProjectBrief,
    LearningProjectOrigin,
    ProjectCreateIntent,
    ProjectOrigin,
    ProjectShell,
)
from .domain.workspace import (
    ProjectArtifact,
    ProjectEvidenceExport,
    ProjectSnapshot,
    ProjectSnapshotCloseIntent,
    ProjectWorkspace,
    WorkspaceMutationIntent,
)


class ProjectErrorCode(StrEnum):
    INVALID_REQUEST = "invalid_request"
    IMMUTABLE_CONFLICT = "immutable_conflict"
    STALE_REVISION = "stale_revision"
    INTEGRITY_FAILURE = "integrity_failure"
    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"


class ProjectError(RuntimeError):
    """Bounded Project error without persistence or provider details."""

    def __init__(
        self,
        code: ProjectErrorCode,
        message: str,
        *,
        reference: str = "project",
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code.value,
            "message": self.message,
            "reference": self.reference,
        }


@dataclass(frozen=True, slots=True)
class CreateProjectRequest:
    learner_id: str
    intent: ProjectCreateIntent


@dataclass(frozen=True, slots=True)
class ListProjectsRequest:
    learner_id: str


@dataclass(frozen=True, slots=True)
class OpenProjectRequest:
    learner_id: str
    project_id: str


@dataclass(frozen=True, slots=True)
class OpenProjectWorkspaceRequest:
    learner_id: str
    project_id: str


@dataclass(frozen=True, slots=True)
class MutateProjectWorkspaceRequest:
    learner_id: str
    project_id: str
    intent: WorkspaceMutationIntent


@dataclass(frozen=True, slots=True)
class UploadProjectArtifactRequest:
    learner_id: str
    project_id: str
    intent: WorkspaceMutationIntent
    content: bytes


@dataclass(frozen=True, slots=True)
class DownloadProjectArtifactRequest:
    learner_id: str
    project_id: str
    artifact_id: str
    artifact_version: int


@dataclass(frozen=True, slots=True)
class ProjectArtifactDownload:
    artifact: ProjectArtifact
    content: bytes


@dataclass(frozen=True, slots=True)
class CloseProjectSnapshotRequest:
    learner_id: str
    project_id: str
    intent: ProjectSnapshotCloseIntent


@dataclass(frozen=True, slots=True)
class ListProjectSnapshotsRequest:
    learner_id: str
    project_id: str


@dataclass(frozen=True, slots=True)
class OpenProjectSnapshotRequest:
    learner_id: str
    project_id: str
    snapshot_id: str


@dataclass(frozen=True, slots=True)
class OpenProjectLearningSnapshotRequest:
    learner_id: str
    project_id: str
    snapshot_id: str


@dataclass(frozen=True, slots=True)
class ProjectLearningSnapshotResource:
    resource_kind: Literal["note", "source", "artifact", "domain_resource"]
    resource_id: str
    resource_version: int | str | None
    resource_as_of: datetime | None
    record_digest: str
    content_digest: str | None = None
    byte_count: int | None = None
    owner_reference_digest: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectLearningSnapshot:
    origin: LearningProjectOrigin
    snapshot: ProjectSnapshot
    resources: tuple[ProjectLearningSnapshotResource, ...]


@dataclass(frozen=True, slots=True)
class ExportProjectSnapshotRequest:
    learner_id: str
    project_id: str
    snapshot_id: str


@dataclass(frozen=True, slots=True)
class ProjectEvidenceFileContent:
    artifact_id: str
    artifact_version: int
    logical_path: str
    content: bytes


@dataclass(frozen=True, slots=True)
class ProjectEvidenceExportBundle:
    manifest: ProjectEvidenceExport
    files: tuple[ProjectEvidenceFileContent, ...]


@dataclass(frozen=True, slots=True)
class ResolveLearningProjectStartOptionRequest:
    placement_id: str


@dataclass(frozen=True, slots=True)
class ListLearningProjectStartOptionsRequest:
    pass


@dataclass(frozen=True, slots=True)
class LearningProjectStartOption:
    title: str
    purpose: str
    origin: LearningProjectOrigin


class ProjectOperations(Protocol):
    def create_project(self, request: CreateProjectRequest) -> ProjectShell: ...

    def list_projects(
        self, request: ListProjectsRequest
    ) -> tuple[ProjectShell, ...]: ...

    def open_project(self, request: OpenProjectRequest) -> ProjectShell: ...

    def open_workspace(
        self, request: OpenProjectWorkspaceRequest
    ) -> ProjectWorkspace: ...

    def mutate_workspace(
        self, request: MutateProjectWorkspaceRequest
    ) -> ProjectWorkspace: ...

    def upload_artifact(
        self, request: UploadProjectArtifactRequest
    ) -> ProjectWorkspace: ...

    def download_artifact(
        self, request: DownloadProjectArtifactRequest
    ) -> ProjectArtifactDownload: ...

    def close_snapshot(
        self, request: CloseProjectSnapshotRequest
    ) -> ProjectSnapshot: ...

    def list_snapshots(
        self, request: ListProjectSnapshotsRequest
    ) -> tuple[ProjectSnapshot, ...]: ...

    def open_snapshot(
        self, request: OpenProjectSnapshotRequest
    ) -> ProjectSnapshot: ...

    def open_learning_snapshot(
        self, request: OpenProjectLearningSnapshotRequest
    ) -> ProjectLearningSnapshot: ...

    def export_snapshot(
        self, request: ExportProjectSnapshotRequest
    ) -> ProjectEvidenceExportBundle: ...

    def resolve_learning_project_start_option(
        self, request: ResolveLearningProjectStartOptionRequest
    ) -> LearningProjectStartOption: ...

    def list_learning_project_start_options(
        self, request: ListLearningProjectStartOptionsRequest
    ) -> tuple[LearningProjectStartOption, ...]: ...


__all__ = [
    "CloseProjectSnapshotRequest",
    "CreateProjectRequest",
    "DownloadProjectArtifactRequest",
    "ExportProjectSnapshotRequest",
    "IndependentProjectOrigin",
    "LearningProjectBrief",
    "LearningProjectOrigin",
    "LearningProjectStartOption",
    "ListLearningProjectStartOptionsRequest",
    "ListProjectSnapshotsRequest",
    "ListProjectsRequest",
    "MutateProjectWorkspaceRequest",
    "OpenProjectRequest",
    "OpenProjectLearningSnapshotRequest",
    "OpenProjectSnapshotRequest",
    "OpenProjectWorkspaceRequest",
    "ProjectCreateIntent",
    "ProjectArtifactDownload",
    "ProjectEvidenceExportBundle",
    "ProjectEvidenceFileContent",
    "ProjectError",
    "ProjectErrorCode",
    "ProjectLearningSnapshot",
    "ProjectLearningSnapshotResource",
    "ProjectOperations",
    "ProjectOrigin",
    "ProjectSnapshot",
    "ProjectSnapshotCloseIntent",
    "ProjectShell",
    "ProjectWorkspace",
    "ResolveLearningProjectStartOptionRequest",
    "UploadProjectArtifactRequest",
    "WorkspaceMutationIntent",
]
