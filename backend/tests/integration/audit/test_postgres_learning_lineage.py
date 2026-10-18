from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timezone
import os
from pathlib import Path

import psycopg
import pytest

from financial_ai_academy.modules.audit.adapters.learning_lineage import (
    ContentLearningLineageSource,
)
from financial_ai_academy.modules.audit.adapters.postgres_repository import (
    PostgresAuditRepository,
)
from financial_ai_academy.modules.audit.application.service import AuditService
from financial_ai_academy.modules.audit.domain.models import AuditableAssessmentEvent
from financial_ai_academy.modules.audit.public import (
    AuditError,
    AuditErrorCode,
    ReadKnowledgeCheckCompletionLineageRequest,
)
from financial_ai_academy.modules.content.public import (
    EducationalSource,
    PublicationProvenance,
    PublishedLesson,
)
from financial_ai_academy.platform.database.migrations import PostgresMigrationRunner


REPOSITORY = Path(__file__).resolve().parents[4]
MIGRATIONS = REPOSITORY / "backend/migrations"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 8, 5, 12, tzinfo=timezone.utc)
PACKAGE_DIGEST = "7" * 64
DEFINITION_DIGEST = "9" * 64

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
    root = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS)
    audit = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS / "audit")
    root.apply_all()
    audit.apply_all()
    yield
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            (
                MIGRATIONS / "audit/audit_0002_project_completion_records.down.sql"
            ).read_text(encoding="utf-8")
        )
        connection.execute(
            "DELETE FROM platform.schema_migrations WHERE migration_id = %s",
            ("audit_0002_project_completion_records",),
        )
        connection.execute(
            (
                MIGRATIONS / "audit/audit_0001_assessment_completion_records.down.sql"
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


def _event() -> AuditableAssessmentEvent:
    return AuditableAssessmentEvent(
        "1.0.0",
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "assessment.knowledge-check.completed",
        "1.0.0",
        "assessment",
        NOW,
        "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
        "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        LEARNER_ID,
        "intro-risk-return",
        "intro-risk-return",
        "1.1.0",
        PACKAGE_DIGEST,
        "risk-return-check-1",
        "1.0.0",
        DEFINITION_DIGEST,
        "risk-return-tradeoff",
        "1.0.0",
        "single-select-exact-match",
        "1.0.0",
        1,
        1,
        NOW,
    )


class Source:
    def __init__(self) -> None:
        self.event = _event()

    def list_for_lesson(self, **_context) -> tuple[AuditableAssessmentEvent, ...]:
        return (self.event,)


class Content:
    def get_published_lesson_version(self, _request: object) -> PublishedLesson:
        return PublishedLesson(
            "intro-risk-return",
            "1.1.0",
            PACKAGE_DIGEST,
            "Risk and return",
            (),
            (),
            (
                EducationalSource(
                    "source-risk-return",
                    "Risk and return source",
                    "University",
                    "https://private.example/source",
                    date(2026, 8, 1),
                    None,
                ),
            ),
            (),
            PublicationProvenance(
                "content-team",
                NOW,
                date(2026, 8, 1),
                "For education.",
            ),
        )


class Clock:
    def now(self) -> datetime:
        return NOW


def _service(source: Source | None = None) -> tuple[AuditService, Source]:
    assert POSTGRES_DSN is not None
    events = source or Source()
    return (
        AuditService(
            events,
            PostgresAuditRepository(POSTGRES_DSN),
            Clock(),
            ContentLearningLineageSource(Content()),
        ),
        events,
    )


def _count() -> int:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        return connection.execute(
            "SELECT count(*) FROM audit.assessment_completion_records"
        ).fetchone()[0]


def test_exact_replay_reads_one_retained_audit_reference() -> None:
    service, _source = _service()
    request = ReadKnowledgeCheckCompletionLineageRequest(
        LEARNER_ID,
        "intro-risk-return",
        _event().evidence_id,
        1,
    )
    first = service.read_knowledge_check_completion_lineage(request)
    second_service, _source = _service()
    second = second_service.read_knowledge_check_completion_lineage(request)

    assert first == second
    assert _count() == 1
    assert len(first.nodes) == 6
    assert first.root.resource.resource_id == _event().evidence_id


def test_changed_replay_conflicts_and_exact_read_is_context_bound() -> None:
    service, source = _service()
    request = ReadKnowledgeCheckCompletionLineageRequest(
        LEARNER_ID,
        "intro-risk-return",
        _event().evidence_id,
        1,
    )
    service.read_knowledge_check_completion_lineage(request)
    source.event = replace(source.event, score=0)
    with pytest.raises(AuditError) as conflict:
        service.read_knowledge_check_completion_lineage(request)
    assert conflict.value.code is AuditErrorCode.CONFLICT
    assert _count() == 1

    assert POSTGRES_DSN is not None
    repository = PostgresAuditRepository(POSTGRES_DSN)
    assert (
        repository.read_assessment_completion_record(
            actor_id="22222222-2222-4222-8222-222222222222",
            placement_id="intro-risk-return",
            evidence_id=_event().evidence_id,
        )
        is None
    )
