from __future__ import annotations

from dataclasses import fields, replace
from datetime import datetime, timezone

import pytest

from financial_ai_academy.modules.personal_workspace.adapters.project_reference import (
    PublicProjectLearningReferenceGateway,
)
from financial_ai_academy.modules.personal_workspace.domain.workspace import (
    ProjectArtifactReference,
    ProjectSnapshotReference,
    ProjectWorkspaceReference,
)
from financial_ai_academy.modules.personal_workspace.ports.learning_reference import (
    PersonalWorkspaceSourceUnavailable,
)
from financial_ai_academy.modules.personal_workspace.public import (
    LearningOpportunitySelector,
    ProjectArtifactSelector,
    ProjectSnapshotSelector,
    ProjectWorkspaceSelector,
)
from financial_ai_academy.modules.project.domain.project import (
    IndependentProjectOrigin,
    ProjectShell,
)
from financial_ai_academy.modules.project.domain.workspace import (
    ArtifactKind,
    ArtifactProvenance,
    InspectionMode,
    ProjectArtifact,
    ProjectSnapshot,
    ProjectSnapshotMaterial,
    ProjectWorkspace,
    ProvenanceSourceType,
)
from financial_ai_academy.modules.project.public import (
    OpenProjectRequest,
    OpenProjectSnapshotRequest,
    OpenProjectWorkspaceRequest,
    ProjectError,
    ProjectErrorCode,
)


NOW = datetime(2026, 10, 17, 13, 0, tzinfo=timezone.utc)
CREATED = datetime(2026, 10, 17, 12, 0, tzinfo=timezone.utc)


def shell(**changes) -> ProjectShell:
    value = ProjectShell(
        schema_version="1.0.0",
        project_id="project.demo",
        learner_id="learner.demo",
        title="Evidence comparison",
        charter="Private charter content must not be copied.",
        origin=IndependentProjectOrigin(),
        lifecycle="active",
        revision=3,
        created_at=CREATED,
        updated_at=CREATED,
    )
    return replace(value, **changes)


def artifact(**changes) -> ProjectArtifact:
    value = ProjectArtifact(
        artifact_kind=ArtifactKind.DATASET,
        logical_path="evidence/inputs.csv",
        media_type="text/csv",
        inspection_mode=InspectionMode.PLAIN_TEXT,
        byte_count=17,
        content_digest="b" * 64,
        result_classification=None,
        provenance=ArtifactProvenance(
            source_type=ProvenanceSourceType.EXTERNAL,
            source_title="Private source title",
            source_url="https://private.example/source",
            use_constraints="Private constraints",
        ),
        environment=None,
        assumptions=("Private assumption",),
        artifact_id="artifact.inputs",
        artifact_version=2,
        created_at=CREATED,
    )
    return replace(value, **changes)


def workspace(**changes) -> ProjectWorkspace:
    value = ProjectWorkspace(
        schema_version="1.0.0",
        project_id="project.demo",
        learner_id="learner.demo",
        workspace_revision=5,
        notes=(),
        references=(),
        artifacts=(artifact(),),
        domain_links=(),
        created_at=CREATED,
        updated_at=CREATED,
    )
    return replace(value, **changes)


def snapshot(**changes) -> ProjectSnapshot:
    value = ProjectSnapshot(
        schema_version="1.0.0",
        snapshot_id="snapshot.baseline",
        snapshot_digest="a" * 64,
        snapshot=ProjectSnapshotMaterial(
            project_id="project.demo",
            learner_id="learner.demo",
            project_revision=2,
            project_shell_digest="c" * 64,
            workspace_revision=4,
            workspace_created_at=CREATED,
            workspace_updated_at=CREATED,
            notes=(),
            references=(),
            artifacts=(),
            domain_links=(),
        ),
        closed_at=CREATED,
    )
    return replace(value, **changes)


class Projects:
    def __init__(self) -> None:
        self.shell = shell()
        self.workspace = workspace()
        self.snapshot = snapshot()
        self.calls: list[str] = []
        self.requests: list[object] = []
        self.error: Exception | None = None

    def _result(self, name: str, request: object, value):
        self.calls.append(name)
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return value

    def open_project(self, request):
        return self._result("open_project", request, self.shell)

    def open_workspace(self, request):
        return self._result("open_workspace", request, self.workspace)

    def open_snapshot(self, request):
        return self._result("open_snapshot", request, self.snapshot)

    def download_artifact(self, _request):  # pragma: no cover - must stay unreachable
        raise AssertionError("The Personal workspace must not download artifact bytes.")


@pytest.mark.parametrize(
    ("selector", "expected_type", "expected_calls", "expected_requests"),
    [
        (
            ProjectWorkspaceSelector("project.demo"),
            ProjectWorkspaceReference,
            ["open_project", "open_workspace"],
            [
                OpenProjectRequest("learner.demo", "project.demo"),
                OpenProjectWorkspaceRequest("learner.demo", "project.demo"),
            ],
        ),
        (
            ProjectSnapshotSelector("project.demo", "snapshot.baseline"),
            ProjectSnapshotReference,
            ["open_project", "open_snapshot"],
            [
                OpenProjectRequest("learner.demo", "project.demo"),
                OpenProjectSnapshotRequest(
                    "learner.demo", "project.demo", "snapshot.baseline"
                ),
            ],
        ),
        (
            ProjectArtifactSelector("project.demo", "artifact.inputs", 2),
            ProjectArtifactReference,
            ["open_project", "open_workspace"],
            [
                OpenProjectRequest("learner.demo", "project.demo"),
                OpenProjectWorkspaceRequest("learner.demo", "project.demo"),
            ],
        ),
    ],
)
def test_project_reference_variants_use_only_public_read_operations(
    selector, expected_type, expected_calls, expected_requests
) -> None:
    projects = Projects()
    result = PublicProjectLearningReferenceGateway(projects).resolve(
        selector,
        learner_id="learner.demo",
        validated_at=NOW,
    )

    assert isinstance(result, expected_type)
    assert projects.calls == expected_calls
    assert projects.requests == expected_requests
    assert result.project_id == "project.demo"
    assert result.title == "Evidence comparison"
    assert result.validated_at == NOW


def test_workspace_reference_contains_only_bounded_safe_fields() -> None:
    result = PublicProjectLearningReferenceGateway(Projects()).resolve(
        ProjectWorkspaceSelector("project.demo"),
        learner_id="learner.demo",
        validated_at=NOW,
    )
    assert {field.name for field in fields(result)} == {
        "project_id",
        "title",
        "lifecycle",
        "project_revision",
        "workspace_revision",
        "destination",
        "target_status",
        "validated_at",
        "owner_module",
        "reference_kind",
    }


def test_snapshot_reference_does_not_copy_snapshot_material() -> None:
    result = PublicProjectLearningReferenceGateway(Projects()).resolve(
        ProjectSnapshotSelector("project.demo", "snapshot.baseline"),
        learner_id="learner.demo",
        validated_at=NOW,
    )
    assert isinstance(result, ProjectSnapshotReference)
    assert result.snapshot_digest == "a" * 64
    assert result.workspace_revision == 4
    assert not hasattr(result, "snapshot")
    assert not hasattr(result, "learner_id")


@pytest.mark.parametrize(
    (
        "title",
        "project_revision",
        "workspace_revision",
        "kind",
        "logical_path",
        "media_type",
        "inspection_mode",
        "byte_count",
        "content_digest",
        "created_at",
    ),
    [
        (
            "Evidence comparison",
            1,
            1,
            ArtifactKind.DATASET,
            "inputs/a.csv",
            "text/csv",
            InspectionMode.PLAIN_TEXT,
            0,
            "1" * 64,
            CREATED,
        ),
        (
            "Notebook review",
            7,
            12,
            ArtifactKind.NOTEBOOK,
            "analysis/review.ipynb",
            "application/x-ipynb+json",
            InspectionMode.METADATA_ONLY,
            8200,
            "d" * 64,
            datetime(2026, 10, 17, 12, 30, tzinfo=timezone.utc),
        ),
        (
            "Result record",
            99,
            101,
            ArtifactKind.RESULT,
            "results/final.json",
            "application/json",
            InspectionMode.PLAIN_TEXT,
            10485760,
            "f" * 64,
            NOW,
        ),
    ],
)
def test_artifact_reference_varies_safe_manifest_facts_without_private_payload(
    title: str,
    project_revision: int,
    workspace_revision: int,
    kind: ArtifactKind,
    logical_path: str,
    media_type: str,
    inspection_mode: InspectionMode,
    byte_count: int,
    content_digest: str,
    created_at: datetime,
) -> None:
    projects = Projects()
    projects.shell = shell(title=title, revision=project_revision)
    projects.workspace = workspace(
        workspace_revision=workspace_revision,
        artifacts=(
            artifact(
                artifact_kind=kind,
                logical_path=logical_path,
                media_type=media_type,
                inspection_mode=inspection_mode,
                byte_count=byte_count,
                content_digest=content_digest,
                created_at=created_at,
            ),
        )
    )
    result = PublicProjectLearningReferenceGateway(projects).resolve(
        ProjectArtifactSelector("project.demo", "artifact.inputs", 2),
        learner_id="learner.demo",
        validated_at=NOW,
    )

    assert isinstance(result, ProjectArtifactReference)
    assert result.title == title
    assert result.project_revision == project_revision
    assert result.workspace_revision == workspace_revision
    assert result.artifact_kind == kind.value
    assert result.logical_path == logical_path
    assert result.byte_count == byte_count
    assert result.content_digest == content_digest
    assert result.created_at == created_at
    serialized = repr(result)
    for private in (
        "Private charter",
        "private.example",
        "Private source title",
        "Private constraints",
        "Private assumption",
    ):
        assert private not in serialized


@pytest.mark.parametrize(
    "selector",
    [
        ProjectWorkspaceSelector("project.demo"),
        ProjectSnapshotSelector("project.demo", "snapshot.baseline"),
        ProjectArtifactSelector("project.demo", "artifact.inputs", 2),
    ],
)
def test_server_owned_learner_context_is_required_by_the_gateway(selector) -> None:
    projects = Projects()
    with pytest.raises(TypeError):
        PublicProjectLearningReferenceGateway(projects).resolve(
            selector, validated_at=NOW
        )
    assert projects.calls == []


def test_non_project_selector_fails_without_touching_project() -> None:
    projects = Projects()
    with pytest.raises(PersonalWorkspaceSourceUnavailable):
        PublicProjectLearningReferenceGateway(projects).resolve(
            LearningOpportunitySelector("opportunity.demo", "placement.demo"),
            learner_id="learner.demo",
            validated_at=NOW,
        )
    assert projects.calls == []


@pytest.mark.parametrize(
    "mismatch",
    [
        "shell_learner",
        "shell_project",
        "shell_lifecycle",
        "workspace_learner",
        "workspace_project",
        "snapshot_id",
        "snapshot_learner",
        "snapshot_project",
        "snapshot_revision",
        "artifact",
    ],
)
def test_missing_mismatched_or_denied_project_fails_closed(mismatch: str) -> None:
    projects = Projects()
    selector = ProjectWorkspaceSelector("project.demo")
    if mismatch == "shell_learner":
        projects.shell = shell(learner_id="learner.other")
    elif mismatch == "shell_project":
        projects.shell = shell(project_id="project.other")
    elif mismatch == "shell_lifecycle":
        projects.shell = shell(lifecycle="archived")
    elif mismatch == "workspace_learner":
        projects.workspace = workspace(learner_id="learner.other")
    elif mismatch == "workspace_project":
        projects.workspace = workspace(project_id="project.other")
    elif mismatch == "snapshot_id":
        selector = ProjectSnapshotSelector("project.demo", "snapshot.baseline")
        projects.snapshot = snapshot(snapshot_id="snapshot.other")
    elif mismatch == "snapshot_learner":
        selector = ProjectSnapshotSelector("project.demo", "snapshot.baseline")
        projects.snapshot = snapshot(
            snapshot=replace(snapshot().snapshot, learner_id="learner.other")
        )
    elif mismatch == "snapshot_project":
        selector = ProjectSnapshotSelector("project.demo", "snapshot.baseline")
        projects.snapshot = snapshot(
            snapshot=replace(snapshot().snapshot, project_id="project.other")
        )
    elif mismatch == "snapshot_revision":
        selector = ProjectSnapshotSelector("project.demo", "snapshot.baseline")
        projects.snapshot = snapshot(
            snapshot=replace(snapshot().snapshot, project_revision=4)
        )
    else:
        selector = ProjectArtifactSelector("project.demo", "artifact.missing", 1)

    with pytest.raises(PersonalWorkspaceSourceUnavailable) as failure:
        PublicProjectLearningReferenceGateway(projects).resolve(
            selector,
            learner_id="learner.demo",
            validated_at=NOW,
        )
    assert "learner.other" not in str(failure.value)


@pytest.mark.parametrize(
    ("selector", "future_source"),
    [
        (
            ProjectSnapshotSelector("project.demo", "snapshot.baseline"),
            "snapshot",
        ),
        (
            ProjectArtifactSelector("project.demo", "artifact.inputs", 2),
            "artifact",
        ),
    ],
)
def test_source_time_after_validation_fails_closed(selector, future_source: str) -> None:
    projects = Projects()
    future = datetime(2026, 10, 17, 13, 0, 1, tzinfo=timezone.utc)
    if future_source == "snapshot":
        projects.snapshot = snapshot(closed_at=future)
    else:
        projects.workspace = workspace(artifacts=(artifact(created_at=future),))

    with pytest.raises(PersonalWorkspaceSourceUnavailable):
        PublicProjectLearningReferenceGateway(projects).resolve(
            selector,
            learner_id="learner.demo",
            validated_at=NOW,
        )


@pytest.mark.parametrize(
    ("selector", "boundary_source"),
    [
        (
            ProjectSnapshotSelector("project.demo", "snapshot.baseline"),
            "snapshot",
        ),
        (
            ProjectArtifactSelector("project.demo", "artifact.inputs", 2),
            "artifact",
        ),
    ],
)
def test_source_time_equal_to_validation_is_accepted(
    selector, boundary_source: str
) -> None:
    projects = Projects()
    if boundary_source == "snapshot":
        projects.snapshot = snapshot(closed_at=NOW)
    else:
        projects.workspace = workspace(artifacts=(artifact(created_at=NOW),))

    result = PublicProjectLearningReferenceGateway(projects).resolve(
        selector,
        learner_id="learner.demo",
        validated_at=NOW,
    )
    assert result.validated_at == NOW


@pytest.mark.parametrize(
    "logical_path",
    [
        "../private.txt",
        "evidence\\private.txt",
        "evidence/CON.txt",
        "evidence/cafe\u0301.csv",
        "a" * 241,
    ],
)
def test_noncanonical_project_artifact_path_fails_closed(logical_path: str) -> None:
    projects = Projects()
    projects.workspace = workspace(
        artifacts=(artifact(logical_path=logical_path),)
    )

    with pytest.raises(PersonalWorkspaceSourceUnavailable):
        PublicProjectLearningReferenceGateway(projects).resolve(
            ProjectArtifactSelector("project.demo", "artifact.inputs", 2),
            learner_id="learner.demo",
            validated_at=NOW,
        )


def test_project_artifact_path_accepts_exact_contract_length_boundary() -> None:
    projects = Projects()
    projects.workspace = workspace(
        artifacts=(artifact(logical_path="a" * 240),)
    )

    result = PublicProjectLearningReferenceGateway(projects).resolve(
        ProjectArtifactSelector("project.demo", "artifact.inputs", 2),
        learner_id="learner.demo",
        validated_at=NOW,
    )
    assert isinstance(result, ProjectArtifactReference)
    assert result.logical_path == "a" * 240


def test_project_public_failure_is_bounded_and_confidential() -> None:
    projects = Projects()
    secret = "private-project-storage-value"
    projects.error = ProjectError(
        ProjectErrorCode.NOT_FOUND,
        secret,
        reference=secret,
    )
    with pytest.raises(PersonalWorkspaceSourceUnavailable) as failure:
        PublicProjectLearningReferenceGateway(projects).resolve(
            ProjectWorkspaceSelector("project.demo"),
            learner_id="learner.demo",
            validated_at=NOW,
        )
    assert secret not in str(failure.value)
