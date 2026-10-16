from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import pytest

from financial_ai_academy.modules.curriculum.adapters.postgres_repository import (
    PostgresCurriculumRepository,
)
from financial_ai_academy.modules.curriculum.ports.repositories import (
    PlacementConflict,
)
from financial_ai_academy.modules.curriculum.public import ProjectBriefPlacement
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)


ROOT = Path(__file__).resolve().parents[4]
MIGRATIONS = ROOT / "backend/migrations"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
NOW = datetime(2026, 10, 16, tzinfo=timezone.utc)

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
        for schema in ("curriculum", "content", "platform"):
            connection.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
    PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS).apply_all()
    statuses = PostgresMigrationRunner(
        POSTGRES_DSN, MIGRATIONS / "curriculum"
    ).apply_all()
    assert statuses[-1].migration_id == (
        "curriculum_0006_project_brief_placements"
    )
    yield
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as connection:
        for schema in ("curriculum", "content", "platform"):
            connection.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")


@pytest.fixture(autouse=True)
def empty_placements(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            "TRUNCATE TABLE curriculum.project_brief_placements"
        )


def placement(digest: str = "a" * 64) -> ProjectBriefPlacement:
    return ProjectBriefPlacement(
        placement_id="risk-return-project-primary",
        placement_version="1.0.0",
        placement_digest=digest,
        curriculum_id="financial-foundations",
        curriculum_version="1.0.0",
        curriculum_digest="b" * 64,
        package_id="intro-risk-return-project",
        package_version="1.0.0",
        package_digest="c" * 64,
        brief_id="risk-return-project",
        brief_version="1.0.0",
        brief_digest="d" * 64,
        project_brief_schema_version="1.0.0",
        created_at=NOW,
    )


def test_exact_placement_survives_restart_and_replays_idempotently() -> None:
    assert POSTGRES_DSN is not None
    first = PostgresCurriculumRepository(POSTGRES_DSN)
    created, was_created = first.save_project_brief_if_absent(placement())
    replay, replay_created = first.save_project_brief_if_absent(placement())
    second = PostgresCurriculumRepository(POSTGRES_DSN)

    assert was_created is True
    assert replay_created is False
    assert replay == created
    assert second.get_project_brief(created.placement_id) == created


def test_same_placement_identity_rejects_changed_exact_meaning() -> None:
    assert POSTGRES_DSN is not None
    selected = PostgresCurriculumRepository(POSTGRES_DSN)
    selected.save_project_brief_if_absent(placement())

    with pytest.raises(PlacementConflict):
        selected.save_project_brief_if_absent(placement("e" * 64))
