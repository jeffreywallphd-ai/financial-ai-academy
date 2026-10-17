from __future__ import annotations

import os
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import pytest

from financial_ai_academy.modules.audit.adapters.postgres_repository import (
    PostgresAuditRepository,
)
from financial_ai_academy.modules.audit.application.service import AuditService
from financial_ai_academy.modules.audit.domain.models import AuditableProjectEvent
from financial_ai_academy.modules.audit.public import (
    AuditError,
    AuditErrorCode,
    ReconcileProjectCompletionAuditRequest,
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
        connection.execute("DROP SCHEMA IF EXISTS audit CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS platform CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS curriculum CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS content CASCADE")
    root = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS)
    audit = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS / "audit")
    root.apply_all()
    applied = {item.migration_id for item in audit.apply_all()}
    assert "audit_0002_project_completion_records" in applied
    yield
    with psycopg.connect(POSTGRES_DSN) as connection:
        for migration_id in (
            "audit_0002_project_completion_records",
            "audit_0001_assessment_completion_records",
        ):
            connection.execute(
                (MIGRATIONS / f"audit/{migration_id}.down.sql").read_text(
                    encoding="utf-8"
                )
            )
            connection.execute(
                "DELETE FROM platform.schema_migrations WHERE migration_id = %s",
                (migration_id,),
            )
    root.rollback_all()


@pytest.fixture(autouse=True)
def empty_table(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute("TRUNCATE audit.project_completion_records")


def event() -> AuditableProjectEvent:
    return AuditableProjectEvent(
        schema_version="1.0.0",
        event_id="event-retirement-01",
        event_type="assessment.project.completed",
        event_version="1.0.0",
        occurred_at=NOW,
        evidence_id="evidence-retirement-01",
        learner_id=LEARNER_ID,
        submission_id="submission-retirement-01",
        project_id=PROJECT_ID,
        snapshot_id="snapshot-retirement-plan-01",
        snapshot_digest="2" * 64,
        brief_id="brief-retirement-plan",
        brief_version="1.0.0",
        brief_digest="4" * 64,
        placement_id="placement-retirement-project",
        placement_version="1.0.0",
        placement_digest="6" * 64,
        policy_id="assessment-project-closure",
        policy_version="1.0.0",
        milestone_ids=("identify-assumptions", "compare-scenarios"),
        request_fingerprint="7" * 64,
        occurrence=1,
        submitted_at=NOW,
        supersedes_submission_id=None,
    )


class Source:
    def __init__(self, values: tuple[AuditableProjectEvent, ...]) -> None:
        self.values = values

    def list_for_project(
        self, *, learner_id: str, project_id: str
    ) -> tuple[AuditableProjectEvent, ...]:
        return self.values


class Clock:
    def now(self) -> datetime:
        return NOW


def service(
    values: tuple[AuditableProjectEvent, ...],
    *,
    before_commit: object | None = None,
) -> AuditService:
    assert POSTGRES_DSN is not None
    return AuditService(
        Source(values),
        PostgresAuditRepository(
            POSTGRES_DSN,
            before_commit=before_commit,  # type: ignore[arg-type]
        ),
        Clock(),
    )


def request() -> ReconcileProjectCompletionAuditRequest:
    return ReconcileProjectCompletionAuditRequest(LEARNER_ID, PROJECT_ID)


def count() -> int:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        return connection.execute(
            "SELECT count(*) FROM audit.project_completion_records"
        ).fetchone()[0]


def test_project_audit_replay_is_idempotent_and_tamper_conflicts() -> None:
    first = service((event(),)).reconcile_project_completion(request())
    second = service((event(),)).reconcile_project_completion(request())
    assert first == second
    assert count() == 1

    with pytest.raises(AuditError) as captured:
        service(
            (replace(event(), snapshot_digest="9" * 64),)
        ).reconcile_project_completion(request())
    assert captured.value.code is AuditErrorCode.CONFLICT
    assert count() == 1


def test_project_audit_interruption_rolls_back_and_rows_are_immutable() -> None:
    def fail() -> None:
        raise psycopg.OperationalError("private transaction detail")

    with pytest.raises(AuditError) as captured:
        service((event(),), before_commit=fail).reconcile_project_completion(
            request()
        )
    assert captured.value.code is AuditErrorCode.UNAVAILABLE
    assert count() == 0

    service((event(),)).reconcile_project_completion(request())
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        with pytest.raises(psycopg.DatabaseError):
            connection.execute(
                "UPDATE audit.project_completion_records "
                "SET action = 'changed'"
            )
        connection.rollback()
        with pytest.raises(psycopg.DatabaseError):
            connection.execute("DELETE FROM audit.project_completion_records")
    assert count() == 1
