from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import pytest
from psycopg.conninfo import make_conninfo

from financial_ai_academy.modules.project.adapters.postgres_repository import (
    PostgresProjectRepository,
)
from financial_ai_academy.modules.project.adapters.project_contract import (
    ContractProjectAdapter,
)
from financial_ai_academy.modules.project.domain.project import (
    IndependentProjectOrigin,
    ProjectShell,
)
from financial_ai_academy.modules.project.ports.repositories import (
    ProjectIdempotencyConflict,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)


ROOT = Path(__file__).resolve().parents[4]
MIGRATIONS = ROOT / "backend/migrations"
SCHEMAS = ROOT / "contracts/learning/project/v1"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
NOW = datetime(2026, 10, 16, 14, tzinfo=timezone.utc)

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
        for schema in ("project", "curriculum", "content", "platform"):
            connection.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
    PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS).apply_all()
    statuses = PostgresMigrationRunner(
        POSTGRES_DSN, MIGRATIONS / "project"
    ).apply_all()
    assert statuses[-1].migration_id == "project_0001_project_shells"
    yield
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as connection:
        for schema in ("project", "curriculum", "content", "platform"):
            connection.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")


@pytest.fixture(autouse=True)
def empty_projects(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute("TRUNCATE TABLE project.project_shells")


def repository(dsn: str | None = None) -> PostgresProjectRepository:
    assert POSTGRES_DSN is not None
    return PostgresProjectRepository(
        dsn or POSTGRES_DSN,
        ContractProjectAdapter(SCHEMAS),
    )


def shell(project_id: str, learner_id: str = "learner-1") -> ProjectShell:
    return ProjectShell(
        "1.0.0",
        project_id,
        learner_id,
        "Compare evidence",
        "Use consistent educational criteria.",
        IndependentProjectOrigin(),
        "active",
        1,
        NOW,
        NOW,
    )


def test_project_survives_repository_restart_and_is_learner_scoped() -> None:
    first = repository()
    created, was_created = first.create_if_absent(
        idempotency_key="restart-1",
        request_fingerprint="a" * 64,
        shell=shell("project-1"),
    )
    second = repository()

    assert was_created is True
    assert second.get_for_learner("learner-1", "project-1") == created
    assert second.get_for_learner("learner-2", "project-1") is None
    assert second.list_for_learner("learner-1") == (created,)


def test_project_read_normalizes_a_non_utc_postgres_session() -> None:
    assert POSTGRES_DSN is not None
    created, _was_created = repository().create_if_absent(
        idempotency_key="timezone-1",
        request_fingerprint="f" * 64,
        shell=shell("project-timezone"),
    )
    non_utc = repository(
        make_conninfo(
            POSTGRES_DSN,
            options="-c timezone=Asia/Kolkata",
        )
    )

    reopened = non_utc.get_for_learner("learner-1", "project-timezone")

    assert reopened == created
    assert reopened is not None
    assert reopened.created_at.utcoffset() == timezone.utc.utcoffset(NOW)


def test_concurrent_exact_retry_creates_one_row_and_returns_one_identity() -> None:
    def create(number: int) -> ProjectShell:
        stored, _created = repository().create_if_absent(
            idempotency_key="concurrent-1",
            request_fingerprint="b" * 64,
            shell=shell(f"project-{number}"),
        )
        return stored

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = tuple(executor.map(create, range(1, 9)))

    assert len({result.project_id for result in results}) == 1
    assert len(repository().list_for_learner("learner-1")) == 1


def test_changed_idempotency_meaning_conflicts_without_overwrite() -> None:
    selected = repository()
    selected.create_if_absent(
        idempotency_key="conflict-1",
        request_fingerprint="c" * 64,
        shell=shell("project-original"),
    )

    with pytest.raises(ProjectIdempotencyConflict):
        selected.create_if_absent(
            idempotency_key="conflict-1",
            request_fingerprint="d" * 64,
            shell=shell("project-changed"),
        )

    assert selected.list_for_learner("learner-1")[0].project_id == (
        "project-original"
    )


def test_down_migration_refuses_retained_project_rows() -> None:
    assert POSTGRES_DSN is not None
    repository().create_if_absent(
        idempotency_key="retained-1",
        request_fingerprint="e" * 64,
        shell=shell("project-retained"),
    )
    down = (
        MIGRATIONS / "project/project_0001_project_shells.down.sql"
    ).read_text(encoding="utf-8")

    with pytest.raises(psycopg.Error):
        with psycopg.connect(POSTGRES_DSN) as connection:
            connection.execute(down)

    assert repository().get_for_learner(
        "learner-1", "project-retained"
    ) is not None


def test_empty_development_down_and_up_are_reversible() -> None:
    assert POSTGRES_DSN is not None
    down = (
        MIGRATIONS / "project/project_0001_project_shells.down.sql"
    ).read_text(encoding="utf-8")
    up = (
        MIGRATIONS / "project/project_0001_project_shells.up.sql"
    ).read_text(encoding="utf-8")

    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(down)
        assert connection.execute(
            "SELECT to_regnamespace('project')"
        ).fetchone() == (None,)
        connection.execute(up)

    assert repository().list_for_learner("learner-1") == ()
