from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg
import pytest

from financial_ai_academy.modules.learner_model.adapters.postgres_repository import (
    PostgresCompletionProjectionRepository,
)
from financial_ai_academy.modules.learner_model.application.service import (
    LearnerModelService,
)
from financial_ai_academy.modules.learner_model.domain.models import (
    SourceProjectCompletion,
)
from financial_ai_academy.modules.learner_model.public import (
    LearnerModelError,
    LearnerModelErrorCode,
    OpenProjectCompletionRequest,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)


REPOSITORY = Path(__file__).resolve().parents[4]
MIGRATIONS = REPOSITORY / "backend/migrations"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
PROJECT_ID = "project-retirement-plan"
NOW = datetime(2026, 10, 17, 3, 30, tzinfo=timezone.utc)

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
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute("DROP SCHEMA IF EXISTS learner_model CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS platform CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS curriculum CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS content CASCADE")
    root = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS)
    learner = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS / "learner_model")
    root.apply_all()
    applied = {item.migration_id for item in learner.apply_all()}
    assert "learner_model_0003_project_completion" in applied
    yield
    with psycopg.connect(POSTGRES_DSN) as connection:
        for migration_id in (
            "learner_model_0003_project_completion",
            "learner_model_0002_practice_history",
            "learner_model_0001_completion_projection",
        ):
            connection.execute(
                (
                    MIGRATIONS / f"learner_model/{migration_id}.down.sql"
                ).read_text(encoding="utf-8")
            )
            connection.execute(
                "DELETE FROM platform.schema_migrations WHERE migration_id = %s",
                (migration_id,),
            )
    root.rollback_all()


@pytest.fixture(autouse=True)
def empty_tables(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            "TRUNCATE learner_model.project_completion_history, "
            "learner_model.project_completion_projections"
        )


def completion(
    occurrence: int,
    *,
    supersedes: str | None = None,
) -> SourceProjectCompletion:
    return SourceProjectCompletion(
        schema_version="1.0.0",
        event_id=f"event-retirement-{occurrence:02d}",
        event_type="assessment.project.completed",
        event_version="1.0.0",
        occurred_at=NOW + timedelta(minutes=occurrence),
        evidence_id=f"evidence-retirement-{occurrence:02d}",
        learner_id=LEARNER_ID,
        occurrence=occurrence,
        accepted_sequence=40 + occurrence,
        submitted_at=NOW + timedelta(minutes=occurrence),
        supersedes_submission_id=supersedes,
        submission_id=f"submission-retirement-{occurrence:02d}",
        project_id=PROJECT_ID,
        snapshot_id=f"snapshot-retirement-plan-{occurrence:02d}",
        snapshot_digest=f"{occurrence}" * 64,
        brief_id="brief-retirement-plan",
        brief_version="1.0.0",
        brief_digest="4" * 64,
        placement_id="placement-retirement-project",
        placement_version="1.0.0",
        placement_digest="6" * 64,
        policy_id="assessment-project-closure",
        policy_version="1.0.0",
        milestone_ids=("identify-assumptions", "compare-scenarios"),
        request_fingerprint=f"{occurrence + 6}" * 64,
    )


class Source:
    def __init__(self, values: tuple[SourceProjectCompletion, ...]) -> None:
        self.values = values

    def list_for_project(
        self, *, learner_id: str, project_id: str
    ) -> tuple[SourceProjectCompletion, ...]:
        return self.values


class Clock:
    def now(self) -> datetime:
        return NOW + timedelta(hours=1)


def service(
    values: tuple[SourceProjectCompletion, ...],
    *,
    before_projection: object | None = None,
) -> LearnerModelService:
    assert POSTGRES_DSN is not None
    return LearnerModelService(
        Source(values),
        PostgresCompletionProjectionRepository(
            POSTGRES_DSN,
            before_project_projection=before_projection,  # type: ignore[arg-type]
        ),
        Clock(),
    )


def request() -> OpenProjectCompletionRequest:
    return OpenProjectCompletionRequest(LEARNER_ID, PROJECT_ID)


def counts() -> tuple[int, int]:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        return (
            connection.execute(
                "SELECT count(*) FROM "
                "learner_model.project_completion_projections"
            ).fetchone()[0],
            connection.execute(
                "SELECT count(*) FROM "
                "learner_model.project_completion_history"
            ).fetchone()[0],
        )


def test_project_projection_rebuilds_and_replays_without_duplicate_rows() -> None:
    first = completion(1)
    second = completion(2, supersedes=first.submission_id)
    initial = service((second, first)).open_project_completion(request())
    reopened = service((first, second, first)).open_project_completion(request())

    assert reopened.source_digest == initial.source_digest
    assert [item.occurrence for item in reopened.history] == [1, 2]
    assert counts() == (1, 2)


def test_interrupted_project_replace_preserves_prior_complete_projection() -> None:
    first = completion(1)
    second = completion(2, supersedes=first.submission_id)
    accepted = service((first, second)).open_project_completion(request())

    def fail() -> None:
        raise psycopg.OperationalError("private transaction detail")

    with pytest.raises(LearnerModelError) as captured:
        service((first,), before_projection=fail).open_project_completion(request())
    assert captured.value.code is LearnerModelErrorCode.UNAVAILABLE
    assert counts() == (1, 2)
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        row = connection.execute(
            "SELECT history_count, source_digest FROM "
            "learner_model.project_completion_projections"
        ).fetchone()
    assert row == (2, accepted.source_digest)
