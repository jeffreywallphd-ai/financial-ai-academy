"""Public-only Project snapshot adapter for cross-domain provenance v2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from financial_ai_academy.modules.project.public import (
    OpenProjectSnapshotRequest,
    ProjectOperations,
)

from ..domain.cross_domain_provenance import (
    CrossDomainOwnerModule,
    CrossDomainProducer,
    CrossDomainProfile,
    CrossDomainProvenanceEnvelope,
    CrossDomainProvenanceLabel,
    CrossDomainResourceKind,
    CrossDomainResourceReference,
    CrossDomainValidationStatus,
    InvalidCrossDomainProvenance,
    ProjectSnapshotIdentity,
    validate_cross_domain_envelope,
)


@dataclass(frozen=True, slots=True)
class ProjectSnapshotReferenceAdapter:
    """Issue one safe reference from Project's exact public snapshot read."""

    operations: ProjectOperations
    learner_id: str
    project_id: str
    snapshot_id: str

    profile: ClassVar[CrossDomainProfile] = CrossDomainProfile.PROJECT_SNAPSHOT

    def issue_reference(self) -> CrossDomainProvenanceEnvelope:
        snapshot = self.operations.open_snapshot(
            OpenProjectSnapshotRequest(
                learner_id=self.learner_id,
                project_id=self.project_id,
                snapshot_id=self.snapshot_id,
            )
        )
        material = snapshot.snapshot
        if (
            snapshot.snapshot_id != self.snapshot_id
            or material.project_id != self.project_id
            or material.learner_id != self.learner_id
        ):
            raise InvalidCrossDomainProvenance("project.snapshot")

        return validate_cross_domain_envelope(
            CrossDomainProvenanceEnvelope(
                schema_version="2.0.0",
                resource=CrossDomainResourceReference(
                    profile=self.profile,
                    owner_module=CrossDomainOwnerModule.PROJECT,
                    resource_kind=CrossDomainResourceKind.PROJECT_SNAPSHOT,
                    resource_id=snapshot.snapshot_id,
                    identity=ProjectSnapshotIdentity(
                        project_id=material.project_id,
                        snapshot_id=snapshot.snapshot_id,
                        project_revision=material.project_revision,
                        workspace_revision=material.workspace_revision,
                    ),
                    integrity_digest=snapshot.snapshot_digest,
                    recorded_at=snapshot.closed_at,
                    provenance_label=CrossDomainProvenanceLabel.OBSERVED,
                    validation_status=CrossDomainValidationStatus.VALIDATED,
                ),
                producer=CrossDomainProducer(
                    producer_id="project-snapshot-adapter",
                    producer_version="2.0.0",
                ),
                sources=(),
            )
        )


__all__ = ["ProjectSnapshotReferenceAdapter"]
