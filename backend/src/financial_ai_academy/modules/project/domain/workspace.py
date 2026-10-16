"""Immutable Project workspace, inert-artifact, link, and snapshot values."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Literal, TypeAlias


class ArtifactKind(StrEnum):
    DATASET = "dataset"
    NOTEBOOK = "notebook"
    CODE = "code"
    ENVIRONMENT = "environment"
    RESULT = "result"
    REFLECTION = "reflection"
    SUPPORTING_FILE = "supporting_file"


class InspectionMode(StrEnum):
    METADATA_ONLY = "metadata_only"
    PLAIN_TEXT = "plain_text"


class EvidenceClassification(StrEnum):
    OBSERVED = "observed"
    CALCULATED = "calculated"
    SIMULATED = "simulated"
    PREDICTED = "predicted"
    GENERATED = "generated"
    NARRATIVE = "narrative"


class ProvenanceSourceType(StrEnum):
    LEARNER_CREATED = "learner_created"
    SUPPLIED = "supplied"
    EXTERNAL = "external"


class DomainLinkType(StrEnum):
    CONTEXT = "context"
    INPUT = "input"
    COMPARISON = "comparison"
    OUTPUT = "output"


@dataclass(frozen=True, slots=True)
class ArtifactProvenance:
    source_type: ProvenanceSourceType
    source_title: str
    source_version: str | None = None
    source_url: str | None = None
    source_digest: str | None = None
    license: str | None = None
    use_constraints: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectEnvironment:
    name: str
    version: str
    dependency_digest: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectNote:
    note_id: str
    note_version: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class ProjectReference:
    reference_id: str
    reference_version: int
    title: str
    url: str
    source_name: str
    source_version: str | None
    source_digest: str | None
    license: str | None
    use_constraints: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class ProjectArtifactInput:
    artifact_kind: ArtifactKind
    logical_path: str
    media_type: str
    inspection_mode: InspectionMode
    byte_count: int
    content_digest: str
    result_classification: EvidenceClassification | None
    provenance: ArtifactProvenance
    environment: ProjectEnvironment | None
    assumptions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProjectArtifact(ProjectArtifactInput):
    artifact_id: str
    artifact_version: int
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ProjectDomainLinkInput:
    link_type: DomainLinkType
    owner_module: str
    resource_type: str
    resource_id: str
    resource_version: str | None
    resource_as_of: datetime | None
    provenance: str


@dataclass(frozen=True, slots=True)
class ProjectDomainLink(ProjectDomainLinkInput):
    link_id: str
    owner_reference_digest: str
    target_status: Literal["available"]
    validated_at: datetime
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ProjectWorkspace:
    schema_version: str
    project_id: str
    learner_id: str
    workspace_revision: int
    notes: tuple[ProjectNote, ...]
    references: tuple[ProjectReference, ...]
    artifacts: tuple[ProjectArtifact, ...]
    domain_links: tuple[ProjectDomainLink, ...]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class AddNoteMutation:
    title: str
    body: str
    operation: Literal["add_note"] = "add_note"


@dataclass(frozen=True, slots=True)
class ReplaceNoteMutation:
    note_id: str
    expected_note_version: int
    title: str
    body: str
    operation: Literal["replace_note"] = "replace_note"


@dataclass(frozen=True, slots=True)
class AddReferenceMutation:
    title: str
    url: str
    source_name: str
    source_version: str | None
    source_digest: str | None
    license: str | None
    use_constraints: str | None
    operation: Literal["add_reference"] = "add_reference"


@dataclass(frozen=True, slots=True)
class ReplaceReferenceMutation:
    reference_id: str
    expected_reference_version: int
    title: str
    url: str
    source_name: str
    source_version: str | None
    source_digest: str | None
    license: str | None
    use_constraints: str | None
    operation: Literal["replace_reference"] = "replace_reference"


@dataclass(frozen=True, slots=True)
class AddArtifactMutation:
    artifact: ProjectArtifactInput
    operation: Literal["add_artifact"] = "add_artifact"


@dataclass(frozen=True, slots=True)
class AddDomainLinkMutation:
    link: ProjectDomainLinkInput
    operation: Literal["add_domain_link"] = "add_domain_link"


@dataclass(frozen=True, slots=True)
class RemoveDomainLinkMutation:
    link_id: str
    operation: Literal["remove_domain_link"] = "remove_domain_link"


WorkspaceMutation: TypeAlias = (
    AddNoteMutation
    | ReplaceNoteMutation
    | AddReferenceMutation
    | ReplaceReferenceMutation
    | AddArtifactMutation
    | AddDomainLinkMutation
    | RemoveDomainLinkMutation
)


@dataclass(frozen=True, slots=True)
class WorkspaceMutationIntent:
    schema_version: str
    idempotency_key: str
    expected_workspace_revision: int
    mutation: WorkspaceMutation


@dataclass(frozen=True, slots=True)
class ProjectSnapshotCloseIntent:
    schema_version: str
    idempotency_key: str
    expected_project_revision: int
    expected_workspace_revision: int


@dataclass(frozen=True, slots=True)
class ProjectVersionReference:
    record_id: str
    record_version: int
    record_digest: str


@dataclass(frozen=True, slots=True)
class ProjectArtifactReference:
    artifact_id: str
    artifact_version: int
    manifest_digest: str
    content_digest: str
    byte_count: int


@dataclass(frozen=True, slots=True)
class ProjectDomainLinkReference:
    link_id: str
    record_digest: str
    owner_reference_digest: str


@dataclass(frozen=True, slots=True)
class ProjectSnapshotMaterial:
    project_id: str
    learner_id: str
    project_revision: int
    project_shell_digest: str
    workspace_revision: int
    workspace_created_at: datetime
    workspace_updated_at: datetime
    notes: tuple[ProjectVersionReference, ...]
    references: tuple[ProjectVersionReference, ...]
    artifacts: tuple[ProjectArtifactReference, ...]
    domain_links: tuple[ProjectDomainLinkReference, ...]


@dataclass(frozen=True, slots=True)
class ProjectSnapshot:
    schema_version: str
    snapshot_id: str
    snapshot_digest: str
    snapshot: ProjectSnapshotMaterial
    closed_at: datetime


@dataclass(frozen=True, slots=True)
class EvidenceArtifactFile:
    artifact_id: str
    artifact_version: int
    logical_path: str
    media_type: str
    byte_count: int
    content_digest: str


@dataclass(frozen=True, slots=True)
class ExcludedEvidenceArtifact:
    artifact_id: str
    artifact_version: int
    reason: Literal[
        "source_use_restricted",
        "not_authorized",
        "content_unavailable",
    ]


@dataclass(frozen=True, slots=True)
class ProjectEvidenceExportMaterial:
    project_id: str
    snapshot_id: str
    snapshot_digest: str
    artifact_files: tuple[EvidenceArtifactFile, ...]
    excluded_artifacts: tuple[ExcludedEvidenceArtifact, ...]
    format: Literal["project-evidence-manifest-v1"] = (
        "project-evidence-manifest-v1"
    )


@dataclass(frozen=True, slots=True)
class ProjectEvidenceExport:
    schema_version: str
    export_id: str
    export_digest: str
    export: ProjectEvidenceExportMaterial
    generated_at: datetime
