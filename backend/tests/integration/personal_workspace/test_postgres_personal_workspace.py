from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
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
from financial_ai_academy.modules.personal_workspace.public import (
    CreateNoteCommand,
    LearningOpportunitySelector,
    MutatePersonalWorkspaceRequest,
    OpenPersonalWorkspaceRequest,
    PersonalWorkspaceError,
    PersonalWorkspaceErrorCode,
    PersonalWorkspaceMutationCommand,
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


class ReferenceGateway:
    def __init__(self, contract) -> None:
        intent = contract.parse_mutation_intent(
            (FIXTURES / "valid-create-note-intent.json").read_bytes()
        )
        self.reference = intent.mutation.target
        self.calls = 0

    def resolve(self, selector, *, validated_at):
        self.calls += 1
        assert selector.opportunity_id == "opportunity.diversification"
        return replace(self.reference, validated_at=validated_at)


def service(identifier: str = "note.postgres"):
    assert POSTGRES_DSN is not None
    contract = ContractPersonalWorkspaceAdapter(SCHEMAS)
    gateway = ReferenceGateway(contract)
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
