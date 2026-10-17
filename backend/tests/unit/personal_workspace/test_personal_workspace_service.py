from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.personal_workspace.adapters.system import (
    StableWorkspaceSeed,
)
from financial_ai_academy.modules.personal_workspace.adapters.workspace_contract import (
    ContractPersonalWorkspaceAdapter,
)
from financial_ai_academy.modules.personal_workspace.application.service import (
    PersonalWorkspaceService,
)
from financial_ai_academy.modules.personal_workspace.domain.workspace import (
    ArchiveRecordMutation,
    CreateCollectionMutation,
    RemoveCollectionMutation,
    RemoveRecordMutation,
    RenameCollectionMutation,
    ReorderRecordsMutation,
    RestoreRecordMutation,
    SetCollectionMembersMutation,
    UpdateBookmarkMutation,
    UpdateNoteMutation,
)
from financial_ai_academy.modules.personal_workspace.ports.learning_reference import (
    PersonalWorkspaceSourceUnavailable,
)
from financial_ai_academy.modules.personal_workspace.ports.repositories import (
    PersonalWorkspaceIdempotencyConflict,
    PersonalWorkspaceRevisionConflict,
)
from financial_ai_academy.modules.personal_workspace.public import (
    CreateBookmarkCommand,
    CreateNoteCommand,
    LearningOpportunitySelector,
    MutatePersonalWorkspaceRequest,
    OpenPersonalWorkspaceRequest,
    PersonalWorkspaceError,
    PersonalWorkspaceErrorCode,
    PersonalWorkspaceMutationCommand,
    ProjectArtifactSelector,
    ProjectSnapshotSelector,
    ProjectWorkspaceSelector,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = ROOT / "contracts" / "learning" / "personal-workspace" / "v1"
FIXTURE_DIR = ROOT / "contracts" / "compatibility" / "personal-workspace" / "v1"
NOW = datetime(2026, 10, 17, 13, 0, tzinfo=timezone.utc)


class Repository:
    def __init__(self) -> None:
        self.workspace = None
        self.replays: dict[str, tuple[str, object]] = {}
        self.writes = 0

    def get_workspace(self, learner_id):
        if self.workspace is not None and self.workspace.learner_id == learner_id:
            return self.workspace
        return None

    def get_mutation_replay(self, learner_id, idempotency_key):
        value = self.replays.get(f"{learner_id}:{idempotency_key}")
        return value

    def save_if_revision(
        self,
        *,
        idempotency_key,
        request_fingerprint,
        expected_revision,
        workspace,
    ):
        key = f"{workspace.learner_id}:{idempotency_key}"
        replay = self.replays.get(key)
        if replay is not None:
            if replay[0] != request_fingerprint:
                raise PersonalWorkspaceIdempotencyConflict()
            return replay[1]
        current_revision = self.workspace.revision if self.workspace else 1
        if current_revision != expected_revision:
            raise PersonalWorkspaceRevisionConflict()
        self.workspace = workspace
        self.replays[key] = (request_fingerprint, workspace)
        self.writes += 1
        return workspace


class References:
    def __init__(self, contract, *, unavailable: bool = False) -> None:
        intent = contract.parse_mutation_intent(
            (FIXTURE_DIR / "valid-create-note-intent.json").read_bytes()
        )
        self.reference = intent.mutation.target
        self.calls = 0
        self.learner_ids: list[str] = []
        self.expected_selector = LearningOpportunitySelector(
            opportunity_id="opportunity.diversification",
            placement_id="placement.diversification",
        )
        self.unavailable = unavailable

    def resolve(self, selector, *, learner_id, validated_at):
        self.calls += 1
        self.learner_ids.append(learner_id)
        if self.unavailable:
            raise PersonalWorkspaceSourceUnavailable()
        assert selector == self.expected_selector
        return replace(self.reference, validated_at=validated_at)


class Clock:
    def now(self):
        return NOW


class Identifiers:
    def __init__(self) -> None:
        self.values = iter(
            ("record.note", "record.bookmark", "collection.one")
        )

    def new(self):
        return next(self.values)


def service(*, unavailable_source: bool = False):
    contract = ContractPersonalWorkspaceAdapter(SCHEMA_DIR)
    repository = Repository()
    references = References(contract, unavailable=unavailable_source)
    return (
        PersonalWorkspaceService(
            repository,
            contract,
            references,
            Clock(),
            Identifiers(),
            StableWorkspaceSeed(),
        ),
        repository,
        references,
    )


def note_command(*, key="note.one", revision=1, body="Evidence before opinion"):
    return PersonalWorkspaceMutationCommand(
        schema_version="1.0.0",
        idempotency_key=key,
        expected_revision=revision,
        mutation=CreateNoteCommand(
            selector=LearningOpportunitySelector(
                opportunity_id="opportunity.diversification",
                placement_id="placement.diversification",
            ),
            title="Risk and return",
            body=body,
        ),
    )


def command(mutation, *, key: str, revision: int):
    return PersonalWorkspaceMutationCommand(
        schema_version="1.0.0",
        idempotency_key=key,
        expected_revision=revision,
        mutation=mutation,
    )


def test_empty_read_is_stable_and_does_not_write() -> None:
    operations, repository, references = service()
    first = operations.open_workspace(OpenPersonalWorkspaceRequest("learner.one"))
    second = operations.open_workspace(OpenPersonalWorkspaceRequest("learner.one"))
    assert first == second
    assert first.revision == 1
    assert repository.writes == 0
    assert references.calls == 0


def test_create_note_resolves_source_and_materializes_revision_two() -> None:
    operations, repository, references = service()
    accepted = operations.mutate_workspace(
        MutatePersonalWorkspaceRequest("learner.one", note_command())
    )
    assert accepted.revision == 2
    assert accepted.records[0].record_id == "record.note"
    assert accepted.records[0].target.validated_at == NOW
    assert repository.workspace == accepted
    assert repository.writes == 1
    assert references.calls == 1
    assert references.learner_ids == ["learner.one"]


@pytest.mark.parametrize(
    ("fixture_name", "selector"),
    [
        (
            "valid-project-workspace-note.json",
            ProjectWorkspaceSelector("project.research-1"),
        ),
        (
            "valid-project-snapshot-bookmark.json",
            ProjectSnapshotSelector("project.research-1", "snapshot.baseline-1"),
        ),
        (
            "valid-project-artifact-bookmark.json",
            ProjectArtifactSelector(
                "project.research-1", "artifact.allocation-inputs", 3
            ),
        ),
    ],
)
def test_project_selector_uses_server_learner_and_exact_target(
    fixture_name: str, selector
) -> None:
    operations, repository, references = service()
    contract = ContractPersonalWorkspaceAdapter(SCHEMA_DIR)
    intent = contract.parse_mutation_intent(
        (FIXTURE_DIR / fixture_name).read_bytes()
    )
    references.reference = intent.mutation.target
    references.expected_selector = selector
    command_value = PersonalWorkspaceMutationCommand(
        schema_version="1.0.0",
        idempotency_key=f"save.{selector.reference_kind}",
        expected_revision=1,
        mutation=CreateNoteCommand(
            selector=selector,
            title="Project evidence",
            body="Keep this exact Project reference.",
        ),
    )

    accepted = operations.mutate_workspace(
        MutatePersonalWorkspaceRequest("learner.project", command_value)
    )

    assert accepted.records[0].target == replace(
        references.reference, validated_at=NOW
    )
    assert references.learner_ids == ["learner.project"]
    assert repository.writes == 1


@pytest.mark.parametrize(
    ("fixture_name", "selector", "mismatch"),
    [
        (
            "valid-project-workspace-note.json",
            ProjectWorkspaceSelector("project.research-1"),
            {"project_id": "project.other"},
        ),
        (
            "valid-project-snapshot-bookmark.json",
            ProjectSnapshotSelector("project.research-1", "snapshot.baseline"),
            {"snapshot_id": "snapshot.other"},
        ),
        (
            "valid-project-artifact-bookmark.json",
            ProjectArtifactSelector(
                "project.research-1", "artifact.allocation-inputs", 3
            ),
            {"artifact_version": 4},
        ),
    ],
)
def test_project_result_mismatch_fails_before_workspace_write(
    fixture_name: str, selector, mismatch: dict[str, object]
) -> None:
    operations, repository, references = service()
    contract = ContractPersonalWorkspaceAdapter(SCHEMA_DIR)
    intent = contract.parse_mutation_intent(
        (FIXTURE_DIR / fixture_name).read_bytes()
    )
    references.reference = replace(intent.mutation.target, **mismatch)
    references.expected_selector = selector
    command_value = PersonalWorkspaceMutationCommand(
        schema_version="1.0.0",
        idempotency_key=f"mismatch.{selector.reference_kind}",
        expected_revision=1,
        mutation=CreateBookmarkCommand(selector=selector, label=None),
    )

    with pytest.raises(PersonalWorkspaceError) as failure:
        operations.mutate_workspace(
            MutatePersonalWorkspaceRequest("learner.project", command_value)
        )

    assert failure.value.code == PersonalWorkspaceErrorCode.SOURCE_UNAVAILABLE
    assert repository.writes == 0
    assert repository.workspace is None


def test_exact_retry_precedes_source_resolution_and_changed_reuse_conflicts() -> None:
    operations, repository, references = service()
    request = MutatePersonalWorkspaceRequest("learner.one", note_command())
    first = operations.mutate_workspace(request)
    second = operations.mutate_workspace(request)
    assert second == first
    assert references.calls == 1
    assert repository.writes == 1

    with pytest.raises(PersonalWorkspaceError) as caught:
        operations.mutate_workspace(
            MutatePersonalWorkspaceRequest(
                "learner.one", note_command(body="Changed meaning")
            )
        )
    assert caught.value.code == PersonalWorkspaceErrorCode.IMMUTABLE_CONFLICT
    assert repository.writes == 1


def test_stale_revision_fails_before_source_resolution() -> None:
    operations, repository, references = service()
    operations.mutate_workspace(
        MutatePersonalWorkspaceRequest("learner.one", note_command())
    )
    with pytest.raises(PersonalWorkspaceError) as caught:
        operations.mutate_workspace(
            MutatePersonalWorkspaceRequest(
                "learner.one", note_command(key="note.two", revision=1)
            )
        )
    assert caught.value.code == PersonalWorkspaceErrorCode.STALE_REVISION
    assert references.calls == 1
    assert repository.writes == 1


def test_non_source_mutation_does_not_call_curriculum_gateway() -> None:
    operations, repository, references = service()
    accepted = operations.mutate_workspace(
        MutatePersonalWorkspaceRequest(
            "learner.two",
            PersonalWorkspaceMutationCommand(
                schema_version="1.0.0",
                idempotency_key="collection.one",
                expected_revision=1,
                mutation=CreateCollectionMutation(title="Keep learning"),
            ),
        )
    )
    assert accepted.collections[0].collection_id == "record.note"
    assert references.calls == 0
    assert repository.writes == 1


def test_source_denial_writes_nothing() -> None:
    operations, repository, references = service(unavailable_source=True)
    with pytest.raises(PersonalWorkspaceError) as caught:
        operations.mutate_workspace(
            MutatePersonalWorkspaceRequest("learner.one", note_command())
        )
    assert caught.value.code == PersonalWorkspaceErrorCode.SOURCE_UNAVAILABLE
    assert references.calls == 1
    assert repository.workspace is None
    assert repository.replays == {}
    assert repository.writes == 0


def test_missing_workspace_owned_record_has_distinct_not_found_result() -> None:
    operations, repository, references = service()
    with pytest.raises(PersonalWorkspaceError) as caught:
        operations.mutate_workspace(
            MutatePersonalWorkspaceRequest(
                "learner.one",
                command(
                    RemoveRecordMutation(record_id="record.missing"),
                    key="remove.missing",
                    revision=1,
                ),
            )
        )
    assert caught.value.code == PersonalWorkspaceErrorCode.NOT_FOUND
    assert repository.writes == 0
    assert references.calls == 0


def test_complete_mutation_union_preserves_order_and_collection_integrity(
) -> None:
    operations, repository, references = service()

    def apply(mutation, key: str):
        current = operations.open_workspace(
            OpenPersonalWorkspaceRequest("learner.one")
        )
        return operations.mutate_workspace(
            MutatePersonalWorkspaceRequest(
                "learner.one",
                command(mutation, key=key, revision=current.revision),
            )
        )

    note = operations.mutate_workspace(
        MutatePersonalWorkspaceRequest("learner.one", note_command())
    )
    assert note.records[0].record_id == "record.note"
    bookmark = apply(
        CreateBookmarkCommand(
            selector=LearningOpportunitySelector(
                opportunity_id="opportunity.diversification",
                placement_id="placement.diversification",
            ),
            label=None,
        ),
        "bookmark.one",
    )
    assert bookmark.records[1].record_id == "record.bookmark"
    updated_note = apply(
        UpdateNoteMutation("record.note", "Updated note", "Updated body"),
        "note.update",
    )
    assert updated_note.records[0].title == "Updated note"
    updated_bookmark = apply(
        UpdateBookmarkMutation("record.bookmark", "Read again"),
        "bookmark.update",
    )
    assert updated_bookmark.records[1].label == "Read again"
    collection = apply(CreateCollectionMutation("Key lessons"), "collection.create")
    assert collection.collections[0].collection_id == "collection.one"
    members = apply(
        SetCollectionMembersMutation(
            "collection.one", ("record.bookmark", "record.note")
        ),
        "collection.members",
    )
    assert members.collections[0].member_record_ids == (
        "record.bookmark",
        "record.note",
    )
    reordered = apply(
        ReorderRecordsMutation(("record.bookmark", "record.note")),
        "records.reorder",
    )
    assert tuple(record.record_id for record in reordered.records) == (
        "record.bookmark",
        "record.note",
    )
    archived = apply(ArchiveRecordMutation("record.note"), "note.archive")
    assert archived.records[1].archived is True
    restored = apply(RestoreRecordMutation("record.note"), "note.restore")
    assert restored.records[1].archived is False
    renamed = apply(
        RenameCollectionMutation("collection.one", "Review later"),
        "collection.rename",
    )
    assert renamed.collections[0].title == "Review later"
    no_collection = apply(
        RemoveCollectionMutation("collection.one"), "collection.remove"
    )
    assert no_collection.collections == ()
    final = apply(RemoveRecordMutation("record.bookmark"), "bookmark.remove")
    assert tuple(record.record_id for record in final.records) == ("record.note",)
    assert repository.writes == 12
    assert references.calls == 2


@pytest.mark.parametrize(
    "learner_id",
    ("", "Uppercase", "space here", "../escape", "x" * 129),
)
def test_invalid_learner_identity_is_bounded(learner_id: str) -> None:
    operations, repository, references = service()
    with pytest.raises(PersonalWorkspaceError) as caught:
        operations.open_workspace(OpenPersonalWorkspaceRequest(learner_id))
    assert caught.value.code == PersonalWorkspaceErrorCode.INVALID_REQUEST
    assert repository.writes == 0
    assert references.calls == 0
