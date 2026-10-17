from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path

import psycopg
import pytest

from financial_ai_academy.modules.personal_workspace.adapters.postgres_repository import (
    PostgresPersonalWorkspaceRepository,
)
from financial_ai_academy.modules.personal_workspace.adapters.system import (
    StableWorkspaceSeed,
)
from financial_ai_academy.modules.personal_workspace.adapters.workspace_contract import (
    ContractPersonalWorkspaceAdapter,
)
from financial_ai_academy.modules.personal_workspace.application.service import (
    PersonalWorkspaceService,
)
from financial_ai_academy.modules.personal_workspace.ports.learning_reference import (
    PersonalWorkspaceSourceUnavailable,
)
from financial_ai_academy.modules.personal_workspace.public import (
    CreateBookmarkCommand,
    CreateCollectionMutation,
    CreateNoteCommand,
    ExportPersonalWorkspaceRequest,
    LearningOpportunitySelector,
    MutatePersonalWorkspaceRequest,
    OpenPersonalWorkspaceRequest,
    PersonalWorkspaceError,
    PersonalWorkspaceErrorCode,
    PersonalWorkspaceMutationCommand,
    ProjectArtifactSelector,
    ProjectSnapshotSelector,
    ProjectWorkspaceSelector,
    QueryPersonalWorkspaceRequest,
    RemoveRecordMutation,
    RefreshReferenceMutation,
    SetCollectionMembersMutation,
    WorkspaceQuery,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)


ROOT = Path(__file__).parents[4]
MIGRATIONS = ROOT / "backend" / "migrations" / "personal_workspace"
SCHEMAS = ROOT / "contracts" / "learning" / "personal-workspace" / "v1"
FIXTURES = ROOT / "contracts" / "compatibility" / "personal-workspace" / "v1"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
NOW = datetime(2026, 10, 17, 14, 0, tzinfo=timezone.utc)

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(
        POSTGRES_DSN is None,
        reason="FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN is not configured",
    ),
]


@pytest.fixture(scope="module", autouse=True)
def migrated_database() -> object:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as connection:
        for schema in ("personal_workspace", "platform"):
            connection.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
    statuses = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS).apply_all()
    assert statuses[-1].migration_id == "personal_workspace_0001_workspaces"
    yield
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as connection:
        for schema in ("personal_workspace", "platform"):
            connection.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")


@pytest.fixture(autouse=True)
def empty_workspace_rows(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            "TRUNCATE TABLE personal_workspace.workspaces CASCADE"
        )


class Clock:
    def now(self):
        return NOW


class Identifier:
    def __init__(self, value: str) -> None:
        self.value = value

    def new(self):
        return self.value


class SequentialIdentifier:
    def __init__(self, *values: str) -> None:
        self.values = iter(values)

    def new(self):
        return next(self.values)


class ReferenceGateway:
    def __init__(self, contract, *, unavailable: bool = False) -> None:
        intent = contract.parse_mutation_intent(
            (FIXTURES / "valid-create-note-intent.json").read_bytes()
        )
        self.reference = intent.mutation.target
        self.project_references = {
            fixture.removeprefix("valid-project-").removesuffix(".json"): (
                contract.parse_mutation_intent((FIXTURES / fixture).read_bytes())
                .mutation.target
            )
            for fixture in (
                "valid-project-workspace-note.json",
                "valid-project-snapshot-bookmark.json",
                "valid-project-artifact-bookmark.json",
            )
        }
        self.calls = 0
        self.learner_ids: list[str] = []
        self.unavailable = unavailable

    def resolve(self, selector, *, learner_id, validated_at):
        self.calls += 1
        self.learner_ids.append(learner_id)
        if self.unavailable:
            raise PersonalWorkspaceSourceUnavailable()
        if isinstance(selector, ProjectWorkspaceSelector):
            reference = self.project_references["workspace-note"]
        elif isinstance(selector, ProjectSnapshotSelector):
            reference = self.project_references["snapshot-bookmark"]
        elif isinstance(selector, ProjectArtifactSelector):
            reference = self.project_references["artifact-bookmark"]
        else:
            assert selector.opportunity_id == "opportunity.diversification"
            reference = self.reference
        return replace(reference, validated_at=validated_at)


def service(
    identifier: str = "note.postgres", *, unavailable_source: bool = False
):
    assert POSTGRES_DSN is not None
    contract = ContractPersonalWorkspaceAdapter(SCHEMAS)
    gateway = ReferenceGateway(contract, unavailable=unavailable_source)
    return (
        PersonalWorkspaceService(
            PostgresPersonalWorkspaceRepository(POSTGRES_DSN, contract),
            contract,
            gateway,
            Clock(),
            Identifier(identifier),
            StableWorkspaceSeed(),
        ),
        gateway,
    )


def command(key: str, *, revision: int = 1, body: str = "Keep exact evidence"):
    return PersonalWorkspaceMutationCommand(
        schema_version="1.0.0",
        idempotency_key=key,
        expected_revision=revision,
        mutation=CreateNoteCommand(
            selector=LearningOpportunitySelector(
                opportunity_id="opportunity.diversification",
                placement_id="placement.diversification",
            ),
            title="Diversification",
            body=body,
        ),
    )


def refresh_command(key: str, revision: int):
    return PersonalWorkspaceMutationCommand(
        schema_version="1.0.0",
        idempotency_key=key,
        expected_revision=revision,
        mutation=RefreshReferenceMutation(record_id="note.postgres"),
    )


def test_empty_read_is_side_effect_free_and_stable() -> None:
    assert POSTGRES_DSN is not None
    subject, gateway = service()
    first = subject.open_workspace(OpenPersonalWorkspaceRequest("learner.one"))
    second = service()[0].open_workspace(
        OpenPersonalWorkspaceRequest("learner.one")
    )
    assert first == second
    assert first.revision == 1
    assert gateway.calls == 0
    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute(
            "SELECT count(*) FROM personal_workspace.workspaces"
        ).fetchone() == (0,)


def test_first_mutation_survives_restart_and_exact_retry_skips_source() -> None:
    subject, gateway = service()
    request = MutatePersonalWorkspaceRequest("learner.one", command("note.one"))
    accepted = subject.mutate_workspace(request)
    restarted, restarted_gateway = service("unused.identifier")
    reopened = restarted.open_workspace(
        OpenPersonalWorkspaceRequest("learner.one")
    )
    replayed = restarted.mutate_workspace(request)
    assert accepted == reopened == replayed
    assert accepted.revision == 2
    assert gateway.calls == 1
    assert restarted_gateway.calls == 0


def test_export_and_removal_survive_restart_without_new_persistence_shape() -> None:
    assert POSTGRES_DSN is not None
    subject, gateway = service()
    empty = subject.export_workspace(
        ExportPersonalWorkspaceRequest("learner.one")
    )
    assert empty.workspace.revision == 1
    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute(
            "SELECT count(*) FROM personal_workspace.workspaces"
        ).fetchone() == (0,)

    accepted = subject.mutate_workspace(
        MutatePersonalWorkspaceRequest("learner.one", command("note.one"))
    )
    first_export = subject.export_workspace(
        ExportPersonalWorkspaceRequest("learner.one")
    )
    restarted, restarted_gateway = service("unused.identifier")
    restarted_export = restarted.export_workspace(
        ExportPersonalWorkspaceRequest("learner.one")
    )
    assert first_export.workspace == accepted
    assert restarted_export == first_export
    assert first_export.workspace_digest == accepted.workspace_digest

    removal = MutatePersonalWorkspaceRequest(
        "learner.one",
        PersonalWorkspaceMutationCommand(
            "1.0.0",
            "remove.saved-note",
            accepted.revision,
            RemoveRecordMutation("note.postgres"),
        ),
    )
    removed = restarted.mutate_workspace(removal)
    replayed = service("unused.replay")[0].mutate_workspace(removal)
    after_removal = service("unused.export")[0].export_workspace(
        ExportPersonalWorkspaceRequest("learner.one")
    )
    assert removed == replayed == after_removal.workspace
    assert after_removal.workspace.records == ()
    assert after_removal.workspace_digest != first_export.workspace_digest
    assert gateway.calls == 1
    assert restarted_gateway.calls == 0


def test_record_capacity_denial_writes_no_aggregate_or_replay_change() -> None:
    assert POSTGRES_DSN is not None
    contract = ContractPersonalWorkspaceAdapter(SCHEMAS)
    document = json.loads(
        (FIXTURES / "valid-populated-workspace.json").read_text(encoding="utf-8")
    )
    template = document["records"][1]
    document["workspace_id"] = "workspace.full"
    document["learner_id"] = "learner.full"
    document["revision"] = 2
    document["records"] = []
    document["collections"] = []
    for index in range(200):
        record = deepcopy(template)
        record["record_id"] = f"bookmark.{index:03d}"
        record["label"] = None if index % 2 == 0 else f"Saved {index}"
        document["records"].append(record)
    document.pop("workspace_digest", None)
    document["workspace_digest"] = contract.canonical_digest(document)
    full = contract.parse_workspace(
        json.dumps(document, ensure_ascii=False).encode("utf-8")
    )
    repository = PostgresPersonalWorkspaceRepository(POSTGRES_DSN, contract)
    repository.save_if_revision(
        idempotency_key="seed.full",
        request_fingerprint="a" * 64,
        expected_revision=1,
        workspace=full,
    )
    subject = PersonalWorkspaceService(
        repository,
        contract,
        ReferenceGateway(contract),
        Clock(),
        Identifier("bookmark.overflow"),
        StableWorkspaceSeed(),
    )

    with pytest.raises(PersonalWorkspaceError) as caught:
        subject.mutate_workspace(
            MutatePersonalWorkspaceRequest(
                "learner.full",
                command("record.overflow", revision=2),
            )
        )

    assert caught.value.code == PersonalWorkspaceErrorCode.RECORD_LIMIT
    exported = subject.export_workspace(
        ExportPersonalWorkspaceRequest("learner.full")
    )
    assert len(exported.workspace.records) == 200
    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute(
            "SELECT revision FROM personal_workspace.workspaces "
            "WHERE learner_id = 'learner.full'"
        ).fetchone() == (2,)
        assert connection.execute(
            "SELECT count(*) FROM personal_workspace.mutations "
            "WHERE learner_id = 'learner.full'"
        ).fetchone() == (1,)


@pytest.mark.parametrize(
    "capacity_kind",
    ("collection", "collection_member"),
)
def test_collection_capacity_denials_write_no_aggregate_or_replay_change(
    capacity_kind: str,
) -> None:
    assert POSTGRES_DSN is not None
    contract = ContractPersonalWorkspaceAdapter(SCHEMAS)
    document = json.loads(
        (FIXTURES / "valid-populated-workspace.json").read_text(encoding="utf-8")
    )
    document["workspace_id"] = f"workspace.full-{capacity_kind}"
    document["learner_id"] = f"learner.full-{capacity_kind}"
    document["revision"] = 2
    template_record = document["records"][1]
    template_collection = document["collections"][0]

    if capacity_kind == "collection":
        document["collections"] = []
        for index in range(50):
            collection = deepcopy(template_collection)
            collection["collection_id"] = f"collection.{index:03d}"
            collection["title"] = f"Collection {index}"
            document["collections"].append(collection)
        mutation = CreateCollectionMutation("Overflow collection")
        expected_code = PersonalWorkspaceErrorCode.COLLECTION_LIMIT
    else:
        document["records"] = []
        for index in range(101):
            record = deepcopy(template_record)
            record["record_id"] = f"bookmark.{index:03d}"
            document["records"].append(record)
        document["collections"] = [deepcopy(template_collection)]
        document["collections"][0]["member_record_ids"] = [
            f"bookmark.{index:03d}" for index in range(100)
        ]
        mutation = SetCollectionMembersMutation(
            "collection.foundations",
            tuple(f"bookmark.{index:03d}" for index in range(101)),
        )
        expected_code = PersonalWorkspaceErrorCode.COLLECTION_MEMBER_LIMIT

    document.pop("workspace_digest", None)
    document["workspace_digest"] = contract.canonical_digest(document)
    full = contract.parse_workspace(
        json.dumps(document, ensure_ascii=False).encode("utf-8")
    )
    repository = PostgresPersonalWorkspaceRepository(POSTGRES_DSN, contract)
    repository.save_if_revision(
        idempotency_key=f"seed.full-{capacity_kind}",
        request_fingerprint="b" * 64,
        expected_revision=1,
        workspace=full,
    )
    subject = PersonalWorkspaceService(
        repository,
        contract,
        ReferenceGateway(contract),
        Clock(),
        Identifier("collection.overflow"),
        StableWorkspaceSeed(),
    )

    with pytest.raises(PersonalWorkspaceError) as caught:
        subject.mutate_workspace(
            MutatePersonalWorkspaceRequest(
                document["learner_id"],
                PersonalWorkspaceMutationCommand(
                    "1.0.0",
                    f"overflow.{capacity_kind}",
                    2,
                    mutation,
                ),
            )
        )

    assert caught.value.code == expected_code
    exported = subject.export_workspace(
        ExportPersonalWorkspaceRequest(document["learner_id"])
    )
    assert exported.workspace == full
    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute(
            "SELECT revision FROM personal_workspace.workspaces "
            "WHERE learner_id = %s",
            (document["learner_id"],),
        ).fetchone() == (2,)
        assert connection.execute(
            "SELECT count(*) FROM personal_workspace.mutations "
            "WHERE learner_id = %s",
            (document["learner_id"],),
        ).fetchone() == (1,)


def test_query_survives_restart_without_writing_or_resolving_source() -> None:
    assert POSTGRES_DSN is not None
    subject, gateway = service()
    subject.mutate_workspace(
        MutatePersonalWorkspaceRequest("learner.one", command("note.one"))
    )
    restarted, restarted_gateway = service("unused.identifier")

    result = restarted.query_workspace(
        QueryPersonalWorkspaceRequest(
            "learner.one",
            WorkspaceQuery(text="diversification", limit=1),
        )
    )

    assert tuple(record.record_id for record in result.records) == (
        "note.postgres",
    )
    assert gateway.calls == 1
    assert restarted_gateway.calls == 0
    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute(
            "SELECT count(*) FROM personal_workspace.mutations"
        ).fetchone() == (1,)


def test_refresh_statuses_and_replay_survive_restart_without_migration() -> None:
    subject, gateway = service()
    created = subject.mutate_workspace(
        MutatePersonalWorkspaceRequest("learner.one", command("note.one"))
    )
    available_request = MutatePersonalWorkspaceRequest(
        "learner.one",
        refresh_command("refresh.available", created.revision),
        frozenset({"learning_opportunity"}),
    )
    available = subject.mutate_workspace(available_request)
    assert available.records[0].target.target_status == "available"

    restarted, restarted_gateway = service("unused.identifier")
    replay = restarted.mutate_workspace(available_request)
    assert replay == available
    assert restarted_gateway.calls == 0

    restarted_gateway.reference = replace(
        restarted_gateway.reference,
        package_digest="c" * 64,
    )
    stale = restarted.mutate_workspace(
        MutatePersonalWorkspaceRequest(
            "learner.one",
            refresh_command("refresh.stale", available.revision),
            frozenset({"learning_opportunity"}),
        )
    )
    assert stale.records[0].target.target_status == "stale"

    unavailable = restarted.mutate_workspace(
        MutatePersonalWorkspaceRequest(
            "learner.one",
            refresh_command("refresh.unavailable", stale.revision),
            frozenset(),
        )
    )
    reopened = service("unused.identifier")[0].open_workspace(
        OpenPersonalWorkspaceRequest("learner.one")
    )
    assert reopened == unavailable
    assert reopened.records[0].target.target_status == "unavailable"
    assert gateway.calls == 2
    assert restarted_gateway.calls == 1


def test_concurrent_refreshes_accept_exactly_one_revision() -> None:
    created_by, _ = service()
    created = created_by.mutate_workspace(
        MutatePersonalWorkspaceRequest("learner.one", command("note.one"))
    )
    first, _ = service("unused.first")
    second, _ = service("unused.second")

    def run(subject, key):
        try:
            return subject.mutate_workspace(
                MutatePersonalWorkspaceRequest(
                    "learner.one",
                    refresh_command(key, created.revision),
                    frozenset({"learning_opportunity"}),
                )
            )
        except PersonalWorkspaceError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = tuple(
            pool.map(
                lambda args: run(*args),
                ((first, "refresh.first"), (second, "refresh.second")),
            )
        )
    assert sum(hasattr(result, "revision") for result in results) == 1
    assert results.count(PersonalWorkspaceErrorCode.STALE_REVISION) == 1


def test_project_reference_variants_survive_restart_and_exact_replay() -> None:
    assert POSTGRES_DSN is not None
    contract = ContractPersonalWorkspaceAdapter(SCHEMAS)
    gateway = ReferenceGateway(contract)
    subject = PersonalWorkspaceService(
        PostgresPersonalWorkspaceRepository(POSTGRES_DSN, contract),
        contract,
        gateway,
        Clock(),
        SequentialIdentifier(
            "record.project-workspace",
            "record.project-snapshot",
            "record.project-artifact",
        ),
        StableWorkspaceSeed(),
    )
    requests = (
        MutatePersonalWorkspaceRequest(
            "learner.project",
            PersonalWorkspaceMutationCommand(
                "1.0.0",
                "project-workspace",
                1,
                CreateNoteCommand(
                    ProjectWorkspaceSelector("project.research-1"),
                    "Continue this Project",
                    "Review the saved assumptions.",
                ),
            ),
        ),
        MutatePersonalWorkspaceRequest(
            "learner.project",
            PersonalWorkspaceMutationCommand(
                "1.0.0",
                "project-snapshot",
                2,
                CreateBookmarkCommand(
                    ProjectSnapshotSelector(
                        "project.research-1", "snapshot.baseline-1"
                    ),
                    "Baseline checkpoint",
                ),
            ),
        ),
        MutatePersonalWorkspaceRequest(
            "learner.project",
            PersonalWorkspaceMutationCommand(
                "1.0.0",
                "project-artifact",
                3,
                CreateBookmarkCommand(
                    ProjectArtifactSelector(
                        "project.research-1", "artifact.allocation-inputs", 3
                    ),
                    "Allocation inputs",
                ),
            ),
        ),
    )
    accepted = None
    for request in requests:
        accepted = subject.mutate_workspace(request)

    restarted, restarted_gateway = service("unused.identifier")
    reopened = restarted.open_workspace(
        OpenPersonalWorkspaceRequest("learner.project")
    )
    replayed = restarted.mutate_workspace(requests[-1])

    assert accepted == reopened == replayed
    assert reopened.revision == 4
    assert tuple(record.target.reference_kind for record in reopened.records) == (
        "project_workspace",
        "project_snapshot",
        "project_artifact",
    )
    assert gateway.learner_ids == ["learner.project"] * 3
    assert restarted_gateway.calls == 0

    available_request = MutatePersonalWorkspaceRequest(
        "learner.project",
        PersonalWorkspaceMutationCommand(
            "1.0.0",
            "refresh-project-artifact-available",
            reopened.revision,
            RefreshReferenceMutation("record.project-artifact"),
        ),
        frozenset({"project_artifact"}),
    )
    available = subject.mutate_workspace(available_request)
    assert available.records[-1].target.target_status == "available"

    gateway.project_references["artifact-bookmark"] = replace(
        gateway.project_references["artifact-bookmark"],
        content_digest="c" * 64,
    )
    stale = subject.mutate_workspace(
        MutatePersonalWorkspaceRequest(
            "learner.project",
            PersonalWorkspaceMutationCommand(
                "1.0.0",
                "refresh-project-artifact-stale",
                available.revision,
                RefreshReferenceMutation("record.project-artifact"),
            ),
            frozenset({"project_artifact"}),
        )
    )
    assert stale.records[-1].target.target_status == "stale"

    unavailable_request = MutatePersonalWorkspaceRequest(
        "learner.project",
        PersonalWorkspaceMutationCommand(
            "1.0.0",
            "refresh-project-artifact-unavailable",
            stale.revision,
            RefreshReferenceMutation("record.project-artifact"),
        ),
        frozenset(),
    )
    unavailable = subject.mutate_workspace(unavailable_request)
    restarted_after_refresh, replay_gateway = service("unused.identifier")
    assert restarted_after_refresh.open_workspace(
        OpenPersonalWorkspaceRequest("learner.project")
    ) == unavailable
    assert restarted_after_refresh.mutate_workspace(unavailable_request) == unavailable
    assert replay_gateway.calls == 0


def test_changed_idempotency_and_stale_revision_do_not_overwrite() -> None:
    subject, _gateway = service()
    accepted = subject.mutate_workspace(
        MutatePersonalWorkspaceRequest("learner.one", command("note.one"))
    )
    with pytest.raises(PersonalWorkspaceError) as changed:
        subject.mutate_workspace(
            MutatePersonalWorkspaceRequest(
                "learner.one", command("note.one", body="Changed")
            )
        )
    with pytest.raises(PersonalWorkspaceError) as stale:
        subject.mutate_workspace(
            MutatePersonalWorkspaceRequest(
                "learner.one", command("note.two", revision=1)
            )
        )
    assert changed.value.code == PersonalWorkspaceErrorCode.IMMUTABLE_CONFLICT
    assert stale.value.code == PersonalWorkspaceErrorCode.STALE_REVISION
    assert subject.open_workspace(
        OpenPersonalWorkspaceRequest("learner.one")
    ) == accepted


def test_concurrent_first_writes_accept_exactly_one_revision() -> None:
    first, _ = service("note.first")
    second, _ = service("note.second")

    def run(subject, key):
        try:
            return subject.mutate_workspace(
                MutatePersonalWorkspaceRequest("learner.one", command(key))
            )
        except PersonalWorkspaceError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = tuple(
            pool.map(
                lambda args: run(*args),
                ((first, "first"), (second, "second")),
            )
        )
    assert sum(hasattr(result, "revision") for result in results) == 1
    assert results.count(PersonalWorkspaceErrorCode.STALE_REVISION) == 1


def test_source_denial_and_learner_isolation_write_no_unrelated_state(
) -> None:
    assert POSTGRES_DSN is not None
    denied, denied_gateway = service(unavailable_source=True)
    with pytest.raises(PersonalWorkspaceError) as caught:
        denied.mutate_workspace(
            MutatePersonalWorkspaceRequest("learner.denied", command("denied"))
        )
    assert caught.value.code == PersonalWorkspaceErrorCode.SOURCE_UNAVAILABLE
    assert denied_gateway.calls == 1

    accepted, _ = service()
    accepted.mutate_workspace(
        MutatePersonalWorkspaceRequest("learner.one", command("accepted"))
    )
    other = accepted.open_workspace(
        OpenPersonalWorkspaceRequest("learner.two")
    )
    assert other.learner_id == "learner.two"
    assert other.revision == 1
    assert other.records == ()
    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute(
            "SELECT learner_id FROM personal_workspace.workspaces "
            "ORDER BY learner_id"
        ).fetchall() == [("learner.one",)]
        assert connection.execute(
            "SELECT learner_id FROM personal_workspace.mutations "
            "ORDER BY learner_id"
        ).fetchall() == [("learner.one",)]


def test_malformed_stored_workspace_fails_as_integrity_error() -> None:
    assert POSTGRES_DSN is not None
    subject, _ = service()
    subject.mutate_workspace(
        MutatePersonalWorkspaceRequest("learner.one", command("accepted"))
    )
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            UPDATE personal_workspace.workspaces
            SET workspace = workspace - 'records'
            WHERE learner_id = 'learner.one'
            """
        )
    with pytest.raises(PersonalWorkspaceError) as caught:
        subject.open_workspace(OpenPersonalWorkspaceRequest("learner.one"))
    assert caught.value.code == PersonalWorkspaceErrorCode.INTEGRITY_FAILURE


def test_interrupted_mutation_rolls_back_workspace_and_replay_together() -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            CREATE FUNCTION personal_workspace.reject_mutation_for_test()
            RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
                RAISE EXCEPTION 'simulated interruption';
            END;
            $$;
            CREATE TRIGGER reject_mutation_for_test
            BEFORE INSERT ON personal_workspace.mutations
            FOR EACH ROW EXECUTE FUNCTION
                personal_workspace.reject_mutation_for_test();
            """
        )
    try:
        subject, _ = service()
        with pytest.raises(PersonalWorkspaceError) as caught:
            subject.mutate_workspace(
                MutatePersonalWorkspaceRequest(
                    "learner.one", command("interrupted")
                )
            )
        assert caught.value.code == PersonalWorkspaceErrorCode.UNAVAILABLE
        with psycopg.connect(POSTGRES_DSN) as connection:
            assert connection.execute(
                "SELECT count(*) FROM personal_workspace.workspaces"
            ).fetchone() == (0,)
            assert connection.execute(
                "SELECT count(*) FROM personal_workspace.mutations"
            ).fetchone() == (0,)
    finally:
        with psycopg.connect(POSTGRES_DSN) as connection:
            connection.execute(
                "DROP TRIGGER IF EXISTS reject_mutation_for_test "
                "ON personal_workspace.mutations"
            )
            connection.execute(
                "DROP FUNCTION IF EXISTS "
                "personal_workspace.reject_mutation_for_test()"
            )


def test_retained_data_refuses_destructive_down() -> None:
    assert POSTGRES_DSN is not None
    subject, _ = service()
    subject.mutate_workspace(
        MutatePersonalWorkspaceRequest("learner.one", command("retained"))
    )
    down = (MIGRATIONS / "personal_workspace_0001_workspaces.down.sql").read_text(
        encoding="utf-8"
    )
    with pytest.raises(psycopg.Error):
        with psycopg.connect(POSTGRES_DSN) as connection:
            connection.execute(down)
    assert subject.open_workspace(
        OpenPersonalWorkspaceRequest("learner.one")
    ).revision == 2


def test_empty_development_down_and_up_are_reversible() -> None:
    assert POSTGRES_DSN is not None
    down = (MIGRATIONS / "personal_workspace_0001_workspaces.down.sql").read_text(
        encoding="utf-8"
    )
    up = (MIGRATIONS / "personal_workspace_0001_workspaces.up.sql").read_text(
        encoding="utf-8"
    )
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(down)
        assert connection.execute(
            "SELECT to_regnamespace('personal_workspace')"
        ).fetchone() == (None,)
        connection.execute(up)
    assert service()[0].open_workspace(
        OpenPersonalWorkspaceRequest("learner.one")
    ).revision == 1
