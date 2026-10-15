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
from financial_ai_academy.modules.audit.domain.models import (
    AuditableAssessmentEvent,
)
from financial_ai_academy.modules.audit.public import (
    AuditError,
    AuditErrorCode,
    ReconcileLessonCompletionAuditRequest,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)


REPOSITORY = Path(__file__).resolve().parents[4]
MIGRATIONS = REPOSITORY / "backend/migrations"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)

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
    assert "audit_0001_assessment_completion_records" in applied
    yield
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            (
                MIGRATIONS
                / "audit/audit_0001_assessment_completion_records.down.sql"
            ).read_text(encoding="utf-8")
        )
        connection.execute(
            "DELETE FROM platform.schema_migrations WHERE migration_id = %s",
            ("audit_0001_assessment_completion_records",),
        )
    root.rollback_all()


@pytest.fixture(autouse=True)
def empty_table(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute("TRUNCATE audit.assessment_completion_records")


def event() -> AuditableAssessmentEvent:
    return AuditableAssessmentEvent(
        schema_version="1.0.0",
        event_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        event_type="assessment.knowledge-check.completed",
        event_version="1.0.0",
        owner="assessment",
        occurred_at=NOW,
        idempotency_key="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        attempt_id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
        evidence_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        learner_id=LEARNER_ID,
        placement_id="intro-risk-return",
        package_id="intro-risk-return",
        package_version="1.1.0",
        package_digest="7cf84bc2f7483d9131db315260b3812f3ea29821bf296571c0c7e38f05b536bc",
        assessment_id="risk-return-check-1",
        assessment_version="1.0.0",
        definition_digest="98e941f9b53ef429cb6d359246ddb9812e354db2a9381a2ee180ed5758343d2b",
        item_id="risk-return-tradeoff",
        item_version="1.0.0",
        scoring_policy_id="single-select-exact-match",
        scoring_policy_version="1.0.0",
        score=1,
        max_score=1,
        completed_at=NOW,
    )


class Source:
    def __init__(self, values: tuple[AuditableAssessmentEvent, ...]) -> None:
        self.values = values

    def list_for_lesson(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[AuditableAssessmentEvent, ...]:
        return self.values


class Clock:
    def now(self) -> datetime:
        return NOW


def service(
    values: tuple[AuditableAssessmentEvent, ...],
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


def request() -> ReconcileLessonCompletionAuditRequest:
    return ReconcileLessonCompletionAuditRequest(
        LEARNER_ID, "intro-risk-return"
    )


def count() -> int:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        return connection.execute(
            "SELECT count(*) FROM audit.assessment_completion_records"
        ).fetchone()[0]


def test_empty_exact_and_duplicate_reconciliation_are_idempotent() -> None:
    assert service(()).reconcile_lesson_completion(request()).reconciled_event_count == 0
    first = service((event(),)).reconcile_lesson_completion(request())
    second = service((event(),)).reconcile_lesson_completion(request())
    assert first == second
    assert count() == 1


def test_conflicting_same_event_identity_preserves_original() -> None:
    service((event(),)).reconcile_lesson_completion(request())
    with pytest.raises(AuditError) as captured:
        service((replace(event(), score=0),)).reconcile_lesson_completion(request())
    assert captured.value.code is AuditErrorCode.CONFLICT
    assert count() == 1


def test_interrupted_append_rolls_back_and_records_are_immutable() -> None:
    def fail() -> None:
        raise psycopg.OperationalError("private transaction detail")

    with pytest.raises(AuditError) as captured:
        service((event(),), before_commit=fail).reconcile_lesson_completion(
            request()
        )
    assert captured.value.code is AuditErrorCode.UNAVAILABLE
    assert count() == 0
    service((event(),)).reconcile_lesson_completion(request())
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        with pytest.raises(psycopg.DatabaseError):
            connection.execute(
                "UPDATE audit.assessment_completion_records "
                "SET action = 'changed'"
            )
        connection.rollback()
        with pytest.raises(psycopg.DatabaseError):
            connection.execute(
                "DELETE FROM audit.assessment_completion_records"
            )
    assert count() == 1
