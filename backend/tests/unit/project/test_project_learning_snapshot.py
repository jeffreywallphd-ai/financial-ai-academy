from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.project.adapters.project_contract import (
    ContractProjectAdapter,
)
from financial_ai_academy.modules.project.application.service import ProjectService
from financial_ai_academy.modules.project.domain.project import (
    LearningProjectOrigin,
    ProjectShell,
)
from financial_ai_academy.modules.project.domain.workspace import (
    ArtifactKind,
    ArtifactProvenance,
    DomainLinkType,
    EvidenceClassification,
    InspectionMode,
    ProjectArtifact,
    ProjectDomainLink,
    ProjectNote,
    ProjectReference,
    ProjectSnapshot,
    ProjectWorkspace,
    ProvenanceSourceType,
)
from financial_ai_academy.modules.project.ports.repositories import (
    StoredProjectSnapshot,
)
from financial_ai_academy.modules.project.public import (
    OpenProjectLearningSnapshotRequest,
    ProjectError,
    ProjectErrorCode,
)


ROOT = Path(__file__).resolve().parents[4]
NOW = datetime(2026, 10, 17, 3, tzinfo=timezone.utc)
DIGEST = "a" * 64


class Repository:
    def __init__(self, shell: ProjectShell, stored: StoredProjectSnapshot | None):
        self.shell = shell
        self.stored = stored

    def get_for_learner(self, learner_id, project_id):
        if (learner_id, project_id) == (
            self.shell.learner_id,
            self.shell.project_id,
        ):
            return self.shell
        return None

    def get_snapshot(self, learner_id, project_id, snapshot_id):
        if (
            self.stored is not None
            and (learner_id, project_id, snapshot_id)
            == (
                self.shell.learner_id,
                self.shell.project_id,
                self.stored.snapshot.snapshot_id,
            )
        ):
            return self.stored
        return None


class Unused:
    def __getattr__(self, name):
        raise AssertionError(f"Unexpected dependency call: {name}")


def _subject():
    contract = ContractProjectAdapter(ROOT / "contracts/learning/project/v1")
    origin = LearningProjectOrigin(
        project_brief_schema_version="1.0.0",
        package_id="package-1",
        package_version="1.0.0",
        package_digest=DIGEST,
        brief_id="brief-1",
        brief_version="1.0.0",
        brief_digest="b" * 64,
        curriculum_id="curriculum-1",
        curriculum_version="1.0.0",
        curriculum_digest="c" * 64,
        placement_id="placement-1",
        placement_version="1.0.0",
        placement_digest="d" * 64,
        brief_title="Evidence project",
        brief_purpose="Close exact evidence.",
    )
    shell = ProjectShell(
        "1.0.0",
        "project-1",
        "learner-1",
        "Evidence project",
        "Close exact evidence without executing it.",
        origin,
        "active",
        1,
        NOW,
        NOW,
    )
    workspace = ProjectWorkspace(
        "1.0.0",
        shell.project_id,
        shell.learner_id,
        4,
        (ProjectNote("note-1", 2, "Reflection", "Closed note", NOW, NOW),),
        (
            ProjectReference(
                "source-1",
                1,
                "Reviewed source",
                "https://example.test/source",
                "Example",
                "1.0.0",
                DIGEST,
                "educational",
                None,
                NOW,
                NOW,
            ),
        ),
        (
            ProjectArtifact(
                ArtifactKind.RESULT,
                "results/output.csv",
                "text/csv",
                InspectionMode.PLAIN_TEXT,
                12,
                "e" * 64,
                EvidenceClassification.SIMULATED,
                ArtifactProvenance(
                    ProvenanceSourceType.LEARNER_CREATED,
                    "Learner result",
                ),
                None,
                (),
                "artifact-1",
                3,
                NOW,
            ),
        ),
        (
            ProjectDomainLink(
                DomainLinkType.CONTEXT,
                "portfolio",
                "simulation",
                "portfolio-1",
                "1.2.3",
                None,
                "Learner-selected context",
                "link-1",
                "f" * 64,
                "available",
                NOW,
                NOW,
            ),
        ),
        NOW,
        NOW,
    )
    repository = Repository(shell, None)
    subject = ProjectService(
        repository, contract, Unused(), Unused(), Unused(), Unused()
    )
    material, document = subject._snapshot_material(shell, workspace)  # noqa: SLF001
    snapshot = ProjectSnapshot(
        "1.0.0",
        "snapshot-1",
        contract.canonical_digest(document),
        material,
        NOW,
    )
    repository.stored = StoredProjectSnapshot(snapshot, workspace)
    return subject, repository


def test_learning_snapshot_exposes_only_closed_safe_resource_facts() -> None:
    subject, _repository = _subject()

    result = subject.open_learning_snapshot(
        OpenProjectLearningSnapshotRequest(
            "learner-1", "project-1", "snapshot-1"
        )
    )

    assert result.origin.brief_id == "brief-1"
    assert [item.resource_kind for item in result.resources] == [
        "note",
        "source",
        "artifact",
        "domain_resource",
    ]
    domain = result.resources[-1]
    assert domain.resource_id == "portfolio-1"
    assert domain.resource_version == "1.2.3"
    assert domain.owner_reference_digest == "f" * 64
    assert not hasattr(domain, "provenance")
    assert not hasattr(domain, "content")


def test_learning_snapshot_rejects_changed_retained_domain_link() -> None:
    subject, repository = _subject()
    assert repository.stored is not None
    workspace = repository.stored.workspace
    changed = workspace.domain_links[0]
    repository.stored = StoredProjectSnapshot(
        repository.stored.snapshot,
        ProjectWorkspace(
            workspace.schema_version,
            workspace.project_id,
            workspace.learner_id,
            workspace.workspace_revision,
            workspace.notes,
            workspace.references,
            workspace.artifacts,
            (
                ProjectDomainLink(
                    changed.link_type,
                    changed.owner_module,
                    changed.resource_type,
                    changed.resource_id,
                    "9.9.9",
                    None,
                    changed.provenance,
                    changed.link_id,
                    changed.owner_reference_digest,
                    changed.target_status,
                    changed.validated_at,
                    changed.created_at,
                ),
            ),
            workspace.created_at,
            workspace.updated_at,
        ),
    )

    with pytest.raises(ProjectError) as captured:
        subject.open_learning_snapshot(
            OpenProjectLearningSnapshotRequest(
                "learner-1", "project-1", "snapshot-1"
            )
        )

    assert captured.value.code is ProjectErrorCode.INTEGRITY_FAILURE
