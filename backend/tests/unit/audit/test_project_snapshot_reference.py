from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json

import pytest

from financial_ai_academy.modules.audit.adapters.project_snapshot_reference import (
    ProjectSnapshotReferenceAdapter,
)
from financial_ai_academy.modules.audit.application.cross_domain_conformance import (
    CrossDomainConformanceCode,
    evaluate_cross_domain_reference,
)
from financial_ai_academy.modules.audit.domain.cross_domain_provenance import (
    CrossDomainOwnerModule,
    CrossDomainProfile,
    CrossDomainProvenanceLabel,
    CrossDomainResourceKind,
    CrossDomainValidationStatus,
    ProjectSnapshotIdentity,
    cross_domain_envelope_digest,
    cross_domain_envelope_payload,
)
from financial_ai_academy.modules.project.public import (
    OpenProjectSnapshotRequest,
    ProjectError,
    ProjectErrorCode,
    ProjectSnapshot,
)
from financial_ai_academy.modules.project.domain.workspace import (
    ProjectSnapshotMaterial,
)


NOW = datetime(2026, 10, 18, 9, 40, tzinfo=timezone.utc)


def _snapshot() -> ProjectSnapshot:
    return ProjectSnapshot(
        schema_version="project-workspace-v1",
        snapshot_id="snapshot-provenance-001",
        snapshot_digest="a" * 64,
        snapshot=ProjectSnapshotMaterial(
            project_id="project-independent-001",
            learner_id="learner-private-001",
            project_revision=3,
            project_shell_digest="b" * 64,
            workspace_revision=7,
            workspace_created_at=NOW,
            workspace_updated_at=NOW,
            notes=(),
            references=(),
            artifacts=(),
            domain_links=(),
        ),
        closed_at=NOW,
    )


@dataclass
class StubProjectOperations:
    snapshot: ProjectSnapshot
    failure: Exception | None = None

    def __post_init__(self) -> None:
        self.requests: list[OpenProjectSnapshotRequest] = []

    def open_snapshot(
        self, request: OpenProjectSnapshotRequest
    ) -> ProjectSnapshot:
        self.requests.append(request)
        if self.failure is not None:
            raise self.failure
        return self.snapshot


def _adapter(operations: StubProjectOperations) -> ProjectSnapshotReferenceAdapter:
    return ProjectSnapshotReferenceAdapter(
        operations=operations,  # type: ignore[arg-type]
        learner_id="learner-private-001",
        project_id="project-independent-001",
        snapshot_id="snapshot-provenance-001",
    )


def test_adapter_issues_minimal_exact_project_snapshot_reference() -> None:
    operations = StubProjectOperations(_snapshot())
    adapter = _adapter(operations)

    envelope = adapter.issue_reference()
    case = evaluate_cross_domain_reference(adapter)

    assert operations.requests == [
        OpenProjectSnapshotRequest(
            learner_id="learner-private-001",
            project_id="project-independent-001",
            snapshot_id="snapshot-provenance-001",
        ),
        OpenProjectSnapshotRequest(
            learner_id="learner-private-001",
            project_id="project-independent-001",
            snapshot_id="snapshot-provenance-001",
        ),
    ]
    assert envelope.resource.profile is CrossDomainProfile.PROJECT_SNAPSHOT
    assert envelope.resource.owner_module is CrossDomainOwnerModule.PROJECT
    assert envelope.resource.resource_kind is CrossDomainResourceKind.PROJECT_SNAPSHOT
    assert envelope.resource.identity == ProjectSnapshotIdentity(
        project_id="project-independent-001",
        snapshot_id="snapshot-provenance-001",
        project_revision=3,
        workspace_revision=7,
    )
    assert envelope.resource.integrity_digest == "a" * 64
    assert envelope.resource.recorded_at == NOW
    assert envelope.resource.provenance_label is CrossDomainProvenanceLabel.OBSERVED
    assert envelope.resource.validation_status is CrossDomainValidationStatus.VALIDATED
    assert envelope.sources == ()
    assert case.valid is True
    assert case.envelope_digest == cross_domain_envelope_digest(envelope)


def test_adapter_excludes_private_project_and_learner_fields() -> None:
    payload = cross_domain_envelope_payload(
        _adapter(StubProjectOperations(_snapshot())).issue_reference()
    )
    serialized = json.dumps(payload, sort_keys=True)

    for private_value in (
        "learner-private-001",
        "project-workspace-v1",
        "project_shell_digest",
        "notes",
        "references",
        "artifacts",
        "domain_links",
        "workspace_created_at",
        "workspace_updated_at",
    ):
        assert private_value not in serialized


@pytest.mark.parametrize(
    ("changed", "value"),
    [
        ("snapshot_id", "snapshot-other"),
        ("project_id", "project-other"),
        ("learner_id", "learner-other"),
        ("project_revision", 0),
        ("workspace_revision", 0),
    ],
)
def test_mismatched_or_malformed_public_snapshot_fails_closed(
    changed: str, value: str | int
) -> None:
    snapshot = _snapshot()
    if changed == "snapshot_id":
        snapshot = replace(snapshot, snapshot_id=str(value))
    elif changed in {"project_id", "learner_id", "project_revision", "workspace_revision"}:
        snapshot = replace(
            snapshot,
            snapshot=replace(snapshot.snapshot, **{changed: value}),
        )

    case = evaluate_cross_domain_reference(
        _adapter(StubProjectOperations(snapshot))
    )

    assert case.valid is False
    assert case.code is CrossDomainConformanceCode.INVALID_REFERENCE
    assert case.reference == "adapter.reference"
    assert case.envelope_digest is None


def test_project_failure_is_isolated_without_message_or_reference_leakage() -> None:
    secret = "https://private.example/token=secret"
    operations = StubProjectOperations(
        _snapshot(),
        ProjectError(
            ProjectErrorCode.UNAVAILABLE,
            f"provider failed at {secret}",
            reference=secret,
        ),
    )

    case = evaluate_cross_domain_reference(_adapter(operations))
    serialized = repr(case)

    assert case.valid is False
    assert case.code is CrossDomainConformanceCode.ADAPTER_FAILURE
    assert case.reference == "adapter.reference"
    assert secret not in serialized
    assert "provider failed" not in serialized
