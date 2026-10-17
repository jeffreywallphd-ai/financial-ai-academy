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
    CreateCollectionMutation,
)
from financial_ai_academy.modules.personal_workspace.ports.repositories import (
    PersonalWorkspaceIdempotencyConflict,
    PersonalWorkspaceRevisionConflict,
)
from financial_ai_academy.modules.personal_workspace.public import (
    CreateNoteCommand,
    LearningOpportunitySelector,
    MutatePersonalWorkspaceRequest,
    OpenPersonalWorkspaceRequest,
    PersonalWorkspaceError,
    PersonalWorkspaceErrorCode,
    PersonalWorkspaceMutationCommand,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = ROOT / "contracts" / "learning" / "personal-workspace" / "v1"
FIXTURE_DIR = ROOT / "contracts" / "compatibility" / "personal-workspace" / "v1"
NOW = datetime(2026, 10, 17, 12, 30, tzinfo=timezone.utc)


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
    def __init__(self, contract) -> None:
        intent = contract.parse_mutation_intent(
            (FIXTURE_DIR / "valid-create-note-intent.json").read_bytes()
        )
        self.reference = intent.mutation.target
        self.calls = 0

    def resolve(self, selector, *, validated_at):
        self.calls += 1
        assert selector == LearningOpportunitySelector(
            opportunity_id="opportunity.diversification",
            placement_id="placement.diversification",
        )
        return replace(self.reference, validated_at=validated_at)


class Clock:
    def now(self):
        return NOW


class Identifiers:
    def __init__(self) -> None:
        self.values = iter(("record.one", "collection.one", "record.two"))

    def new(self):
        return next(self.values)


def service():
    contract = ContractPersonalWorkspaceAdapter(SCHEMA_DIR)
    repository = Repository()
    references = References(contract)
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
    assert accepted.records[0].record_id == "record.one"
    assert accepted.records[0].target.validated_at == NOW
    assert repository.workspace == accepted
    assert repository.writes == 1
    assert references.calls == 1


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
    assert accepted.collections[0].collection_id == "record.one"
    assert references.calls == 0
    assert repository.writes == 1


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
