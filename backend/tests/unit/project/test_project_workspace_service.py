from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.project.adapters.project_contract import (
    ContractProjectAdapter,
)
from financial_ai_academy.modules.project.application.service import ProjectService
from financial_ai_academy.modules.project.domain.project import (
    IndependentProjectOrigin,
    ProjectCreateIntent,
    ProjectShell,
)
from financial_ai_academy.modules.project.domain.workspace import (
    AddArtifactMutation,
    AddDomainLinkMutation,
    AddNoteMutation,
    ArtifactKind,
    ArtifactProvenance,
    DomainLinkType,
    InspectionMode,
    ProjectArtifactInput,
    ProjectDomainLinkInput,
    ProjectSnapshotCloseIntent,
    ProjectWorkspace,
    ProvenanceSourceType,
    ReplaceNoteMutation,
    WorkspaceMutationIntent,
)
from financial_ai_academy.modules.project.ports.object_storage import (
    StagedProjectObject,
)
from financial_ai_academy.modules.project.ports.repositories import (
    ProjectIdempotencyConflict,
    ProjectRevisionConflict,
    StoredProjectArtifact,
    StoredProjectSnapshot,
)
from financial_ai_academy.modules.project.public import (
    CloseProjectSnapshotRequest,
    CreateProjectRequest,
    DownloadProjectArtifactRequest,
    ExportProjectSnapshotRequest,
    MutateProjectWorkspaceRequest,
    OpenProjectWorkspaceRequest,
    ProjectError,
    ProjectErrorCode,
    UploadProjectArtifactRequest,
)


ROOT = Path(__file__).resolve().parents[4]
NOW = datetime(2026, 10, 16, 20, tzinfo=timezone.utc)


class MemoryRepository:
    def __init__(self) -> None:
        self.shells: dict[str, tuple[str, str, ProjectShell]] = {}
        self.workspaces: dict[tuple[str, str], ProjectWorkspace] = {}
        self.mutations: dict[
            tuple[str, str, str], tuple[str, ProjectWorkspace]
        ] = {}
        self.artifacts: dict[
            tuple[str, str, str, int], StoredProjectArtifact
        ] = {}
        self.snapshots: dict[
            tuple[str, str, str], tuple[str, StoredProjectSnapshot]
        ] = {}

    def get_by_idempotency(self, learner_id, idempotency_key):
        value = self.shells.get(f"{learner_id}:{idempotency_key}")
        return (value[0], value[2]) if value else None

    def create_if_absent(
        self, *, idempotency_key, request_fingerprint, shell
    ):
        key = f"{shell.learner_id}:{idempotency_key}"
        existing = self.shells.get(key)
        if existing:
            if existing[0] != request_fingerprint:
                raise ProjectIdempotencyConflict
            return existing[2], False
        self.shells[key] = (request_fingerprint, shell.project_id, shell)
        return shell, True

    def get_for_learner(self, learner_id, project_id):
        return next(
            (
                row[2]
                for row in self.shells.values()
                if row[2].learner_id == learner_id
                and row[2].project_id == project_id
            ),
            None,
        )

    def list_for_learner(self, learner_id):
        return tuple(
            row[2]
            for row in self.shells.values()
            if row[2].learner_id == learner_id
        )

    def get_or_create_workspace(self, candidate):
        return self.workspaces.setdefault(
            (candidate.learner_id, candidate.project_id), candidate
        )

    def get_workspace(self, learner_id, project_id):
        return self.workspaces.get((learner_id, project_id))

    def get_workspace_mutation_replay(
        self, learner_id, project_id, idempotency_key
    ):
        return self.mutations.get((learner_id, project_id, idempotency_key))

    def save_workspace_if_revision(
        self,
        *,
        idempotency_key,
        request_fingerprint,
        expected_revision,
        workspace,
        artifact=None,
    ):
        replay_key = (
            workspace.learner_id,
            workspace.project_id,
            idempotency_key,
        )
        replay = self.mutations.get(replay_key)
        if replay:
            if replay[0] != request_fingerprint:
                raise ProjectIdempotencyConflict
            return replay[1]
        current = self.workspaces[
            (workspace.learner_id, workspace.project_id)
        ]
        if current.workspace_revision != expected_revision:
            raise ProjectRevisionConflict
        self.workspaces[(workspace.learner_id, workspace.project_id)] = workspace
        self.mutations[replay_key] = (request_fingerprint, workspace)
        if artifact:
            self.artifacts[
                (
                    artifact.learner_id,
                    artifact.project_id,
                    artifact.artifact_id,
                    artifact.artifact_version,
                )
            ] = artifact
        return workspace

    def get_artifact(
        self, learner_id, project_id, artifact_id, artifact_version
    ):
        return self.artifacts.get(
            (learner_id, project_id, artifact_id, artifact_version)
        )

    def get_snapshot_by_idempotency(
        self, learner_id, project_id, idempotency_key
    ):
        return self.snapshots.get((learner_id, project_id, idempotency_key))

    def create_snapshot_if_absent(
        self,
        *,
        idempotency_key,
        request_fingerprint,
        expected_workspace_revision,
        snapshot,
        workspace,
    ):
        key = (workspace.learner_id, workspace.project_id, idempotency_key)
        existing = self.snapshots.get(key)
        if existing:
            if existing[0] != request_fingerprint:
                raise ProjectIdempotencyConflict
            return existing[1]
        if (
            self.workspaces[(workspace.learner_id, workspace.project_id)]
            .workspace_revision
            != expected_workspace_revision
        ):
            raise ProjectRevisionConflict
        stored = StoredProjectSnapshot(snapshot, workspace)
        self.snapshots[key] = (request_fingerprint, stored)
        return stored

    def get_snapshot(self, learner_id, project_id, snapshot_id):
        return next(
            (
                value[1]
                for key, value in self.snapshots.items()
                if key[:2] == (learner_id, project_id)
                and value[1].snapshot.snapshot_id == snapshot_id
            ),
            None,
        )

    def list_snapshots(self, learner_id, project_id):
        return tuple(
            value[1].snapshot
            for key, value in self.snapshots.items()
            if key[:2] == (learner_id, project_id)
        )


class MemoryObjects:
    def __init__(self) -> None:
        self.staged: dict[str, tuple[str, bytes]] = {}
        self.objects: dict[str, bytes] = {}

    def stage(self, object_key: str, content: bytes) -> StagedProjectObject:
        stage_id = f"stage-{len(self.staged) + 1}"
        self.staged[stage_id] = (object_key, content)
        return StagedProjectObject(stage_id, object_key)

    def finalize(self, staged: StagedProjectObject) -> None:
        object_key, content = self.staged.pop(staged.stage_id)
        self.objects.setdefault(object_key, content)

    def discard_stage(self, staged: StagedProjectObject) -> None:
        self.staged.pop(staged.stage_id, None)

    def read(self, object_key: str) -> bytes:
        return self.objects[object_key]


class FailingFinalizeObjects(MemoryObjects):
    def finalize(self, staged: StagedProjectObject) -> None:
        raise OSError("simulated finalize interruption")


class Clock:
    def __init__(self) -> None:
        self.tick = 0

    def now(self) -> datetime:
        self.tick += 1
        return NOW + timedelta(minutes=self.tick)


class FixedClock:
    def __init__(self, value: datetime) -> None:
        self.value = value

    def now(self) -> datetime:
        return self.value


class Identifiers:
    def __init__(self) -> None:
        self.value = 0

    def new(self) -> str:
        self.value += 1
        return f"record-{self.value:04d}"


class UnusedGateway:
    def resolve(self, _value):
        raise AssertionError("Independent workspace must not resolve learning.")

    def list(self):
        return ()


def service(
    clock: Clock | FixedClock | None = None,
) -> tuple[ProjectService, MemoryRepository, MemoryObjects]:
    repository = MemoryRepository()
    objects = MemoryObjects()
    subject = ProjectService(
        repository,
        ContractProjectAdapter(ROOT / "contracts/learning/project/v1"),
        UnusedGateway(),
        UnusedGateway(),
        clock or Clock(),
        Identifiers(),
        objects,
    )
    return subject, repository, objects


def create(subject: ProjectService) -> ProjectShell:
    return subject.create_project(
        CreateProjectRequest(
            "learner-1",
            ProjectCreateIntent(
                "1.0.0",
                "create-1",
                "Evidence notebook",
                "Keep bounded educational evidence without financial advice.",
                IndependentProjectOrigin(),
            ),
        )
    )


def intent(key: str, revision: int, mutation) -> WorkspaceMutationIntent:
    return WorkspaceMutationIntent("1.0.0", key, revision, mutation)


def test_workspace_artifact_snapshot_and_export_are_one_headless_core() -> None:
    subject, repository, _objects = service()
    shell = create(subject)
    opened = subject.open_workspace(
        OpenProjectWorkspaceRequest("learner-1", shell.project_id)
    )
    assert repository.workspaces == {}
    noted = subject.mutate_workspace(
        MutateProjectWorkspaceRequest(
            "learner-1",
            shell.project_id,
            intent("note-1", 1, AddNoteMutation("Question", "Compare inputs.")),
        )
    )
    content = b"scenario,value\nbase,1\n"
    artifact_input = ProjectArtifactInput(
        ArtifactKind.DATASET,
        "data/scenario.csv",
        "text/csv",
        InspectionMode.PLAIN_TEXT,
        len(content),
        hashlib.sha256(content).hexdigest(),
        None,
        ArtifactProvenance(
            ProvenanceSourceType.LEARNER_CREATED,
            "Learner scenario",
        ),
        None,
        (),
    )
    with_artifact = subject.upload_artifact(
        UploadProjectArtifactRequest(
            "learner-1",
            shell.project_id,
            intent("artifact-1", 2, AddArtifactMutation(artifact_input)),
            content,
        )
    )
    artifact = with_artifact.artifacts[0]
    downloaded = subject.download_artifact(
        DownloadProjectArtifactRequest(
            "learner-1",
            shell.project_id,
            artifact.artifact_id,
            artifact.artifact_version,
        )
    )
    snapshot = subject.close_snapshot(
        CloseProjectSnapshotRequest(
            "learner-1",
            shell.project_id,
            ProjectSnapshotCloseIntent(
                "1.0.0", "snapshot-1", 1, with_artifact.workspace_revision
            ),
        )
    )
    continued = subject.mutate_workspace(
        MutateProjectWorkspaceRequest(
            "learner-1",
            shell.project_id,
            intent(
                "note-2",
                with_artifact.workspace_revision,
                AddNoteMutation("Later", "This does not change the snapshot."),
            ),
        )
    )
    exported = subject.export_snapshot(
        ExportProjectSnapshotRequest(
            "learner-1", shell.project_id, snapshot.snapshot_id
        )
    )

    assert opened.workspace_revision == 1
    assert noted.notes[0].title == "Question"
    assert downloaded.content == content
    assert snapshot.snapshot.workspace_revision == 3
    assert continued.workspace_revision == 4
    assert exported.manifest.export.workspace_record.workspace_revision == 3
    assert exported.files[0].content == content


def test_snapshot_digest_reuses_contract_canonical_fractional_timestamp() -> None:
    timestamp = datetime(2026, 10, 16, 20, 0, 0, 123450, tzinfo=timezone.utc)
    subject, _repository, _objects = service(FixedClock(timestamp))
    shell = create(subject)
    workspace = subject.mutate_workspace(
        MutateProjectWorkspaceRequest(
            "learner-1",
            shell.project_id,
            intent("note-1", 1, AddNoteMutation("Question", "Compare inputs.")),
        )
    )

    snapshot = subject.close_snapshot(
        CloseProjectSnapshotRequest(
            "learner-1",
            shell.project_id,
            ProjectSnapshotCloseIntent(
                "1.0.0", "snapshot-1", 1, workspace.workspace_revision
            ),
        )
    )
    contract = ContractProjectAdapter(ROOT / "contracts/learning/project/v1")
    snapshot_document = contract.snapshot_document(snapshot)
    exported = subject.export_snapshot(
        ExportProjectSnapshotRequest(
            "learner-1", shell.project_id, snapshot.snapshot_id
        )
    )

    assert snapshot_document["snapshot"]["workspace_created_at"] == (
        "2026-10-16T20:00:00.12345Z"
    )
    assert snapshot_document["snapshot"]["workspace_updated_at"] == (
        "2026-10-16T20:00:00.12345Z"
    )
    assert snapshot.snapshot_digest == contract.canonical_digest(
        snapshot_document["snapshot"]
    )
    assert exported.manifest.export.snapshot_record == snapshot


def test_artifact_replay_revalidates_bytes_before_returning_accepted_work() -> None:
    subject, repository, objects = service()
    shell = create(subject)
    content = b"accepted bytes"
    artifact = ProjectArtifactInput(
        ArtifactKind.SUPPORTING_FILE,
        "evidence.txt",
        "text/plain",
        InspectionMode.PLAIN_TEXT,
        len(content),
        hashlib.sha256(content).hexdigest(),
        None,
        ArtifactProvenance(
            ProvenanceSourceType.LEARNER_CREATED, "Replay evidence"
        ),
        None,
        (),
    )
    request = UploadProjectArtifactRequest(
        "learner-1",
        shell.project_id,
        intent("artifact-replay", 1, AddArtifactMutation(artifact)),
        content,
    )
    accepted = subject.upload_artifact(request)

    assert subject.upload_artifact(request) == accepted
    with pytest.raises(ProjectError) as changed_bytes:
        subject.upload_artifact(
            UploadProjectArtifactRequest(
                request.learner_id,
                request.project_id,
                request.intent,
                b"altered bytes!",
            )
        )

    assert changed_bytes.value.code is ProjectErrorCode.INTEGRITY_FAILURE
    assert repository.workspaces[("learner-1", shell.project_id)] == accepted
    assert len(objects.objects) == 1


def test_interrupted_artifact_finalize_exposes_no_workspace_manifest() -> None:
    repository = MemoryRepository()
    objects = FailingFinalizeObjects()
    subject = ProjectService(
        repository,
        ContractProjectAdapter(ROOT / "contracts/learning/project/v1"),
        UnusedGateway(),
        UnusedGateway(),
        Clock(),
        Identifiers(),
        objects,
    )
    shell = create(subject)
    content = b"bounded evidence"
    artifact = ProjectArtifactInput(
        ArtifactKind.SUPPORTING_FILE,
        "evidence.txt",
        "text/plain",
        InspectionMode.PLAIN_TEXT,
        len(content),
        hashlib.sha256(content).hexdigest(),
        None,
        ArtifactProvenance(
            ProvenanceSourceType.LEARNER_CREATED, "Interrupted evidence"
        ),
        None,
        (),
    )

    with pytest.raises(ProjectError) as interrupted:
        subject.upload_artifact(
            UploadProjectArtifactRequest(
                "learner-1",
                shell.project_id,
                intent("artifact-interrupted", 1, AddArtifactMutation(artifact)),
                content,
            )
        )

    assert interrupted.value.code is ProjectErrorCode.UNAVAILABLE
    assert subject.open_workspace(
        OpenProjectWorkspaceRequest("learner-1", shell.project_id)
    ).artifacts == ()
    assert repository.mutations == {}
    assert repository.artifacts == {}
    assert objects.staged == {}
    assert objects.objects == {}


def test_exact_replay_stale_revision_and_changed_key_fail_without_overwrite() -> None:
    subject, _repository, _objects = service()
    shell = create(subject)
    request = MutateProjectWorkspaceRequest(
        "learner-1",
        shell.project_id,
        intent("note-1", 1, AddNoteMutation("One", "First body")),
    )
    accepted = subject.mutate_workspace(request)
    replay = subject.mutate_workspace(request)

    with pytest.raises(ProjectError) as changed:
        subject.mutate_workspace(
            MutateProjectWorkspaceRequest(
                "learner-1",
                shell.project_id,
                intent("note-1", 1, AddNoteMutation("Two", "Changed body")),
            )
        )
    with pytest.raises(ProjectError) as stale:
        subject.mutate_workspace(
            MutateProjectWorkspaceRequest(
                "learner-1",
                shell.project_id,
                intent("note-2", 1, AddNoteMutation("Two", "Stale body")),
            )
        )

    assert replay == accepted
    assert changed.value.code is ProjectErrorCode.IMMUTABLE_CONFLICT
    assert stale.value.code is ProjectErrorCode.STALE_REVISION


def test_artifact_integrity_and_unadmitted_domain_owner_fail_closed() -> None:
    subject, _repository, objects = service()
    shell = create(subject)
    content = b"safe"
    artifact = ProjectArtifactInput(
        ArtifactKind.SUPPORTING_FILE,
        "evidence.txt",
        "text/plain",
        InspectionMode.PLAIN_TEXT,
        len(content),
        "0" * 64,
        None,
        ArtifactProvenance(ProvenanceSourceType.LEARNER_CREATED, "Evidence"),
        None,
        (),
    )
    with pytest.raises(ProjectError) as mismatch:
        subject.upload_artifact(
            UploadProjectArtifactRequest(
                "learner-1",
                shell.project_id,
                intent("artifact-1", 1, AddArtifactMutation(artifact)),
                content,
            )
        )
    link = ProjectDomainLinkInput(
        DomainLinkType.CONTEXT,
        "portfolio",
        "simulated_portfolio",
        "portfolio-1",
        "1.0.0",
        None,
        "Learner-requested context.",
    )
    with pytest.raises(ProjectError) as unavailable:
        subject.mutate_workspace(
            MutateProjectWorkspaceRequest(
                "learner-1",
                shell.project_id,
                intent("link-1", 1, AddDomainLinkMutation(link)),
            )
        )

    assert mismatch.value.code is ProjectErrorCode.INTEGRITY_FAILURE
    assert unavailable.value.code is ProjectErrorCode.UNAVAILABLE
    assert objects.objects == {}
