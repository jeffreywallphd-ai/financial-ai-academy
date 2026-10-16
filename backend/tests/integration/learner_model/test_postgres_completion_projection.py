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
    SourcePracticeAttempt,
    SourcePracticeHistory,
    SourcePracticeItemSummary,
    SourceCompletionEvidence,
)
from financial_ai_academy.modules.learner_model.public import (
    LearnerModelError,
    LearnerModelErrorCode,
    OpenLessonCompletionRequest,
    OpenPracticeHistoryRequest,
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
        connection.execute("DROP SCHEMA IF EXISTS learner_model CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS platform CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS curriculum CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS content CASCADE")
    root = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS)
    learner = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS / "learner_model")
    root.apply_all()
    applied = {item.migration_id for item in learner.apply_all()}
    assert "learner_model_0001_completion_projection" in applied
    assert "learner_model_0002_practice_history" in applied
    assert {item.migration_id for item in learner.apply_all()} == {
        "0001_content_lesson_package_versions",
        "0002_curriculum_lesson_placements",
        "learner_model_0001_completion_projection",
        "learner_model_0002_practice_history",
    }
    yield
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            (
                MIGRATIONS
                / "learner_model/learner_model_0002_practice_history.down.sql"
            ).read_text(encoding="utf-8")
        )
        connection.execute(
            "DELETE FROM platform.schema_migrations WHERE migration_id = %s",
            ("learner_model_0002_practice_history",),
        )
        connection.execute(
            (
                MIGRATIONS
                / "learner_model/learner_model_0001_completion_projection.down.sql"
            ).read_text(encoding="utf-8")
        )
        connection.execute(
            "DELETE FROM platform.schema_migrations WHERE migration_id = %s",
            ("learner_model_0001_completion_projection",),
        )
    root.rollback_all()


@pytest.fixture(autouse=True)
def empty_tables(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            "TRUNCATE learner_model.practice_history_attempts, "
            "learner_model.practice_history_projections, "
            "learner_model.lesson_completion_history, "
            "learner_model.lesson_completion_projections"
        )


def evidence() -> SourceCompletionEvidence:
    return SourceCompletionEvidence(
        event_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        event_version="1.0.0",
        occurred_at=NOW,
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
    def __init__(self, values: tuple[SourceCompletionEvidence, ...]) -> None:
        self.values = values

    def list_for_lesson(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[SourceCompletionEvidence, ...]:
        return self.values


class Clock:
    def now(self) -> datetime:
        return NOW


def service(
    values: tuple[SourceCompletionEvidence, ...],
    *,
    before_projection: object | None = None,
) -> LearnerModelService:
    assert POSTGRES_DSN is not None
    return LearnerModelService(
        Source(values),
        PostgresCompletionProjectionRepository(
            POSTGRES_DSN,
            before_projection=before_projection,  # type: ignore[arg-type]
        ),
        Clock(),
    )


def request() -> OpenLessonCompletionRequest:
    return OpenLessonCompletionRequest(LEARNER_ID, "intro-risk-return")


def counts() -> tuple[int, int]:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        projection = connection.execute(
            "SELECT count(*) FROM learner_model.lesson_completion_projections"
        ).fetchone()[0]
        history = connection.execute(
            "SELECT count(*) FROM learner_model.lesson_completion_history"
        ).fetchone()[0]
    return projection, history


def test_empty_and_exact_rebuilds_are_queryable() -> None:
    empty = service(()).open_lesson_completion(request())
    assert empty.completed is False
    assert counts() == (1, 0)
    complete = service((evidence(),)).open_lesson_completion(request())
    assert complete.completed is True
    assert complete.history[0].evidence_id == evidence().evidence_id
    assert counts() == (1, 1)


def test_duplicate_replay_replaces_one_derived_history_set() -> None:
    first = service((evidence(),)).open_lesson_completion(request())
    second = service((evidence(),)).open_lesson_completion(request())
    assert first == second
    assert counts() == (1, 1)


def test_interrupted_replace_preserves_the_complete_prior_projection() -> None:
    accepted = service((evidence(),)).open_lesson_completion(request())

    def fail() -> None:
        raise psycopg.OperationalError("private transaction details")

    with pytest.raises(LearnerModelError) as captured:
        service((), before_projection=fail).open_lesson_completion(request())
    assert captured.value.code is LearnerModelErrorCode.UNAVAILABLE
    assert counts() == (1, 1)
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        row = connection.execute(
            """
            SELECT completed, history_count, source_digest
            FROM learner_model.lesson_completion_projections
            """
        ).fetchone()
    assert row == (True, 1, accepted.source_digest)


class PracticeSource:
    def __init__(self, value: SourcePracticeHistory) -> None:
        self.value = value

    def read_practice_history(
        self, *, learner_id: str, placement_id: str
    ) -> SourcePracticeHistory:
        assert learner_id == self.value.learner_id
        assert placement_id == self.value.placement_id
        return self.value


def practice_source(attempt_count: int) -> SourcePracticeHistory:
    attempts = tuple(
        SourcePracticeAttempt(
            attempt_order=order,
            event_id=f"00000000-0000-4000-8001-{order:012d}",
            attempt_id=f"00000000-0000-4000-8002-{order:012d}",
            evidence_id=f"00000000-0000-4000-8003-{order:012d}",
            learner_id=LEARNER_ID,
            submission_id=f"00000000-0000-4000-8004-{order:012d}",
            placement_id="risk-return-practice-placement",
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest="a" * 64,
            definition_digest="b" * 64,
            practice_id="risk-return-practice",
            practice_version="1.0.0",
            attempt_policy_id="formative-retry",
            attempt_policy_version="1.0.0",
            score=0,
            max_score=1,
            outcome="review_needed",
            item_summaries=(
                SourcePracticeItemSummary(
                    item_id="risk-meaning",
                    item_version="1.0.0",
                    item_type="single_select",
                    scoring_policy_id="single-select-exact-match",
                    scoring_policy_version="1.0.0",
                    score=0,
                    max_score=1,
                    correct=False,
                    review_reference_ids=("risk-return-review",),
                ),
            ),
            completed_at=NOW + timedelta(minutes=order),
        )
        for order in range(1, attempt_count + 1)
    )
    return SourcePracticeHistory(
        learner_id=LEARNER_ID,
        placement_id="risk-return-practice-placement",
        package_id="intro-risk-return",
        package_version="2.0.0",
        package_digest="a" * 64,
        definition_digest="b" * 64,
        practice_id="risk-return-practice",
        practice_version="1.0.0",
        attempt_policy_id="formative-retry",
        attempt_policy_version="1.0.0",
        attempts=attempts,
    )


def practice_service(
    attempt_count: int, *, before_projection: object | None = None
) -> LearnerModelService:
    assert POSTGRES_DSN is not None
    return LearnerModelService(
        PracticeSource(practice_source(attempt_count)),  # type: ignore[arg-type]
        PostgresCompletionProjectionRepository(
            POSTGRES_DSN,
            before_practice_projection=before_projection,  # type: ignore[arg-type]
        ),
        Clock(),
    )


def practice_request() -> OpenPracticeHistoryRequest:
    return OpenPracticeHistoryRequest(
        learner_id=LEARNER_ID,
        placement_id="risk-return-practice-placement",
    )


@pytest.mark.parametrize("attempt_count", (0, 1, 4, 10))
def test_practice_history_rebuilds_all_supported_shapes_after_restart(
    attempt_count: int,
) -> None:
    first = practice_service(attempt_count).open_practice_history(
        practice_request()
    )
    reopened = practice_service(attempt_count).open_practice_history(
        practice_request()
    )

    assert first == reopened
    assert len(first.attempts) == attempt_count
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        projection = connection.execute(
            """
            SELECT attempt_count, source_digest
            FROM learner_model.practice_history_projections
            WHERE learner_id = %s
            """,
            (LEARNER_ID,),
        ).fetchone()
        history_count = connection.execute(
            """
            SELECT count(*)
            FROM learner_model.practice_history_attempts
            WHERE learner_id = %s
            """,
            (LEARNER_ID,),
        ).fetchone()[0]
    assert projection == (attempt_count, first.source_digest)
    assert history_count == attempt_count


def test_interrupted_practice_replacement_preserves_prior_complete_history() -> None:
    accepted = practice_service(4).open_practice_history(practice_request())

    def fail() -> None:
        raise psycopg.OperationalError("private transaction details")

    with pytest.raises(LearnerModelError) as captured:
        practice_service(1, before_projection=fail).open_practice_history(
            practice_request()
        )
    assert captured.value.code is LearnerModelErrorCode.UNAVAILABLE
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        projection = connection.execute(
            """
            SELECT attempt_count, source_digest
            FROM learner_model.practice_history_projections
            WHERE learner_id = %s
            """,
            (LEARNER_ID,),
        ).fetchone()
        history_count = connection.execute(
            """
            SELECT count(*)
            FROM learner_model.practice_history_attempts
            WHERE learner_id = %s
            """,
            (LEARNER_ID,),
        ).fetchone()[0]
    assert projection == (4, accepted.source_digest)
    assert history_count == 4
