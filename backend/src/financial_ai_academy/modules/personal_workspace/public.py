"""Stable transport-neutral Personal workspace operations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, Protocol, TypeAlias

from .domain.workspace import (
    ArchiveRecordMutation,
    CreateCollectionMutation,
    PersonalWorkspace,
    RemoveCollectionMutation,
    RemoveRecordMutation,
    RenameCollectionMutation,
    ReorderRecordsMutation,
    RestoreRecordMutation,
    SetCollectionMembersMutation,
    UpdateBookmarkMutation,
    UpdateNoteMutation,
    WorkspaceQuery,
    WorkspaceQueryResult,
    WorkspaceSort,
)


class PersonalWorkspaceErrorCode(StrEnum):
    INVALID_REQUEST = "invalid_request"
    IMMUTABLE_CONFLICT = "immutable_conflict"
    STALE_REVISION = "stale_revision"
    SOURCE_UNAVAILABLE = "source_unavailable"
    NOT_FOUND = "not_found"
    INTEGRITY_FAILURE = "integrity_failure"
    UNAVAILABLE = "unavailable"


class PersonalWorkspaceError(RuntimeError):
    """Bounded Personal-workspace error without storage or source internals."""

    def __init__(
        self,
        code: PersonalWorkspaceErrorCode,
        message: str,
        *,
        reference: str = "personal-workspace",
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
class LearningOpportunitySelector:
    opportunity_id: str
    placement_id: str
    reference_kind: Literal["learning_opportunity"] = "learning_opportunity"


@dataclass(frozen=True, slots=True)
class PlacedLessonSelector:
    placement_id: str
    reference_kind: Literal["placed_lesson"] = "placed_lesson"


@dataclass(frozen=True, slots=True)
class ProjectWorkspaceSelector:
    project_id: str
    reference_kind: Literal["project_workspace"] = "project_workspace"


@dataclass(frozen=True, slots=True)
class ProjectSnapshotSelector:
    project_id: str
    snapshot_id: str
    reference_kind: Literal["project_snapshot"] = "project_snapshot"


@dataclass(frozen=True, slots=True)
class ProjectArtifactSelector:
    project_id: str
    artifact_id: str
    artifact_version: int
    reference_kind: Literal["project_artifact"] = "project_artifact"


LearningReferenceSelector: TypeAlias = (
    LearningOpportunitySelector
    | PlacedLessonSelector
    | ProjectWorkspaceSelector
    | ProjectSnapshotSelector
    | ProjectArtifactSelector
)


@dataclass(frozen=True, slots=True)
class CreateNoteCommand:
    selector: LearningReferenceSelector
    title: str
    body: str
    operation: Literal["create_note"] = "create_note"


@dataclass(frozen=True, slots=True)
class CreateBookmarkCommand:
    selector: LearningReferenceSelector
    label: str | None
    operation: Literal["create_bookmark"] = "create_bookmark"


WorkspaceCommandMutation: TypeAlias = (
    CreateNoteCommand
    | UpdateNoteMutation
    | CreateBookmarkCommand
    | UpdateBookmarkMutation
    | CreateCollectionMutation
    | RenameCollectionMutation
    | RemoveCollectionMutation
    | SetCollectionMembersMutation
    | ReorderRecordsMutation
    | ArchiveRecordMutation
    | RestoreRecordMutation
    | RemoveRecordMutation
)


@dataclass(frozen=True, slots=True)
class PersonalWorkspaceMutationCommand:
    schema_version: str
    idempotency_key: str
    expected_revision: int
    mutation: WorkspaceCommandMutation


@dataclass(frozen=True, slots=True)
class OpenPersonalWorkspaceRequest:
    learner_id: str


@dataclass(frozen=True, slots=True)
class MutatePersonalWorkspaceRequest:
    learner_id: str
    command: PersonalWorkspaceMutationCommand


class PersonalWorkspaceOperations(Protocol):
    def open_workspace(
        self, request: OpenPersonalWorkspaceRequest
    ) -> PersonalWorkspace: ...

    def mutate_workspace(
        self, request: MutatePersonalWorkspaceRequest
    ) -> PersonalWorkspace: ...


__all__ = [
    "CreateBookmarkCommand",
    "CreateNoteCommand",
    "LearningOpportunitySelector",
    "LearningReferenceSelector",
    "MutatePersonalWorkspaceRequest",
    "OpenPersonalWorkspaceRequest",
    "PersonalWorkspace",
    "PersonalWorkspaceError",
    "PersonalWorkspaceErrorCode",
    "PersonalWorkspaceMutationCommand",
    "PersonalWorkspaceOperations",
    "PlacedLessonSelector",
    "ProjectArtifactSelector",
    "ProjectSnapshotSelector",
    "ProjectWorkspaceSelector",
    "WorkspaceQuery",
    "WorkspaceQueryResult",
    "WorkspaceSort",
    "WorkspaceCommandMutation",
]
