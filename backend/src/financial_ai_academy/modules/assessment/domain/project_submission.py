"""Immutable values for deterministic Project learning submissions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, TypeAlias


ResourceKind: TypeAlias = Literal["note", "source", "artifact", "domain_resource"]


@dataclass(frozen=True, slots=True)
class ProjectSource:
    project_id: str
    project_revision: int
    project_shell_digest: str
    snapshot_id: str
    snapshot_digest: str
    workspace_revision: int
    closed_at: datetime


@dataclass(frozen=True, slots=True)
class LearningOrigin:
    package_id: str
    package_version: str
    package_digest: str
    brief_id: str
    brief_version: str
    brief_digest: str
    curriculum_id: str
    curriculum_version: str
    curriculum_digest: str
    placement_id: str
    placement_version: str
    placement_digest: str


@dataclass(frozen=True, slots=True)
class ProjectMilestone:
    milestone_id: str
    milestone_version: str
    sequence: int
    title: str


@dataclass(frozen=True, slots=True)
class SnapshotResource:
    resource_kind: ResourceKind
    resource_id: str
    resource_version: int | str | None
    resource_as_of: datetime | None
    record_digest: str
    content_digest: str | None = None
    byte_count: int | None = None
    owner_reference_digest: str | None = None

    @property
    def identity(self) -> tuple[object, ...]:
        """Return exact immutable identity, excluding no versioned facts."""

        return (
            self.resource_kind,
            self.resource_id,
            self.resource_version,
            self.resource_as_of,
            self.record_digest,
            self.content_digest,
            self.byte_count,
            self.owner_reference_digest,
        )


@dataclass(frozen=True, slots=True)
class ProjectSnapshotCandidate:
    schema_version: str
    project: ProjectSource
    origin: LearningOrigin
    policy_id: str
    policy_version: str
    milestones: tuple[ProjectMilestone, ...]
    resources: tuple[SnapshotResource, ...]


@dataclass(frozen=True, slots=True)
class MilestoneEvidence:
    milestone_id: str
    resources: tuple[SnapshotResource, ...]


@dataclass(frozen=True, slots=True)
class ProjectSubmission:
    schema_version: str
    submission_id: str
    project_id: str
    snapshot_id: str
    snapshot_digest: str
    brief_id: str
    brief_version: str
    brief_digest: str
    placement_id: str
    placement_version: str
    placement_digest: str
    policy_id: str
    policy_version: str
    milestone_evidence: tuple[MilestoneEvidence, ...]


@dataclass(frozen=True, slots=True)
class ProjectValidationIssue:
    code: str
    reference: str
    message: str


@dataclass(frozen=True, slots=True)
class AcceptedProjectSubmission:
    candidate: ProjectSnapshotCandidate
    submission: ProjectSubmission
    request_fingerprint: str


@dataclass(frozen=True, slots=True)
class ProjectValidationResult:
    status: Literal["accepted", "refused"]
    request_fingerprint: str | None
    issues: tuple[ProjectValidationIssue, ...]
    accepted: AcceptedProjectSubmission | None


@dataclass(frozen=True, slots=True)
class ProjectEvidenceMetadata:
    evidence_id: str
    learner_id: str
    occurrence: int
    accepted_sequence: int
    submitted_at: datetime
    supersedes_submission_id: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectCompletionEvidence:
    schema_version: str
    evidence_id: str
    learner_id: str
    occurrence: int
    accepted_sequence: int
    submitted_at: datetime
    supersedes_submission_id: str | None
    accepted: AcceptedProjectSubmission


@dataclass(frozen=True, slots=True)
class ProjectCompletionEvent:
    schema_version: str
    event_id: str
    event_type: Literal["assessment.project.completed"]
    event_version: str
    occurred_at: datetime
    evidence: ProjectCompletionEvidence


@dataclass(frozen=True, slots=True)
class ProjectHistory:
    schema_version: str
    project_id: str
    items: tuple[ProjectCompletionEvidence, ...]
