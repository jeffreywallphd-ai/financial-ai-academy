"""Immutable Personal workspace records and closed mutation intents."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, TypeAlias


@dataclass(frozen=True, slots=True)
class PublicationProvenance:
    published_by: str
    published_at: datetime
    content_reviewed_on: str
    educational_use_notice: str


@dataclass(frozen=True, slots=True)
class LearningOpportunityReference:
    opportunity_id: str
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    source_fingerprint: str
    title: str
    destination: str
    target_status: Literal["available"]
    provenance: PublicationProvenance
    validated_at: datetime
    owner_module: Literal["curriculum"] = "curriculum"
    reference_kind: Literal["learning_opportunity"] = "learning_opportunity"


@dataclass(frozen=True, slots=True)
class PlacedLessonReference:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    title: str
    destination: str
    target_status: Literal["available"]
    provenance: PublicationProvenance
    validated_at: datetime
    owner_module: Literal["curriculum"] = "curriculum"
    reference_kind: Literal["placed_lesson"] = "placed_lesson"


LearningReference: TypeAlias = LearningOpportunityReference | PlacedLessonReference


@dataclass(frozen=True, slots=True)
class WorkspaceNote:
    record_id: str
    title: str
    body: str
    target: LearningReference
    archived: bool
    created_at: datetime
    updated_at: datetime
    record_kind: Literal["note"] = "note"


@dataclass(frozen=True, slots=True)
class WorkspaceBookmark:
    record_id: str
    target: LearningReference
    label: str | None
    archived: bool
    created_at: datetime
    updated_at: datetime
    record_kind: Literal["bookmark"] = "bookmark"


WorkspaceRecord: TypeAlias = WorkspaceNote | WorkspaceBookmark


@dataclass(frozen=True, slots=True)
class WorkspaceCollection:
    collection_id: str
    title: str
    member_record_ids: tuple[str, ...]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class PersonalWorkspace:
    schema_version: str
    workspace_id: str
    learner_id: str
    revision: int
    records: tuple[WorkspaceRecord, ...]
    collections: tuple[WorkspaceCollection, ...]
    created_at: datetime
    updated_at: datetime
    workspace_digest: str


@dataclass(frozen=True, slots=True)
class CreateNoteMutation:
    target: LearningReference
    title: str
    body: str
    operation: Literal["create_note"] = "create_note"


@dataclass(frozen=True, slots=True)
class UpdateNoteMutation:
    record_id: str
    title: str
    body: str
    operation: Literal["update_note"] = "update_note"


@dataclass(frozen=True, slots=True)
class CreateBookmarkMutation:
    target: LearningReference
    label: str | None
    operation: Literal["create_bookmark"] = "create_bookmark"


@dataclass(frozen=True, slots=True)
class UpdateBookmarkMutation:
    record_id: str
    label: str | None
    operation: Literal["update_bookmark"] = "update_bookmark"


@dataclass(frozen=True, slots=True)
class CreateCollectionMutation:
    title: str
    operation: Literal["create_collection"] = "create_collection"


@dataclass(frozen=True, slots=True)
class RenameCollectionMutation:
    collection_id: str
    title: str
    operation: Literal["rename_collection"] = "rename_collection"


@dataclass(frozen=True, slots=True)
class RemoveCollectionMutation:
    collection_id: str
    operation: Literal["remove_collection"] = "remove_collection"


@dataclass(frozen=True, slots=True)
class SetCollectionMembersMutation:
    collection_id: str
    member_record_ids: tuple[str, ...]
    operation: Literal["set_collection_members"] = "set_collection_members"


@dataclass(frozen=True, slots=True)
class ReorderRecordsMutation:
    record_ids: tuple[str, ...]
    operation: Literal["reorder_records"] = "reorder_records"


@dataclass(frozen=True, slots=True)
class ArchiveRecordMutation:
    record_id: str
    operation: Literal["archive_record"] = "archive_record"


@dataclass(frozen=True, slots=True)
class RestoreRecordMutation:
    record_id: str
    operation: Literal["restore_record"] = "restore_record"


@dataclass(frozen=True, slots=True)
class RemoveRecordMutation:
    record_id: str
    operation: Literal["remove_record"] = "remove_record"


WorkspaceMutation: TypeAlias = (
    CreateNoteMutation
    | UpdateNoteMutation
    | CreateBookmarkMutation
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
class WorkspaceMutationIntent:
    schema_version: str
    idempotency_key: str
    expected_revision: int
    mutation: WorkspaceMutation
