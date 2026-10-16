from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import pytest

from financial_ai_academy.modules.assessment.adapters.postgres_repository import (
    PostgresAssessmentRepository,
)
from financial_ai_academy.modules.assessment.adapters.practice_contract import (
    ContractPracticeDefinitionAdapter,
)
from financial_ai_academy.modules.assessment.adapters.practice_submission_contract import (
    ContractPracticeSubmissionAdapter,
)
from financial_ai_academy.modules.assessment.application.service import (
    AssessmentService,
)
from financial_ai_academy.modules.assessment.ports.gateways import (
    PlacedPracticeReference,
    PracticeDefinitionDocument,
)
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    AssessmentErrorCode,
    SubmitPlacedPracticeRequest,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)


REPOSITORY = Path(__file__).resolve().parents[4]
SCHEMAS = REPOSITORY / "contracts/learning/assessment/practice/v1"
DEFINITION = (
    REPOSITORY
    / "contracts/compatibility/assessment-practice/v1/approved/definition.json"
)
SUBMISSION = (
    REPOSITORY
    / "contracts/compatibility/assessment-practice/v1/approved/submission.json"
)
MIGRATIONS = REPOSITORY / "backend/migrations/assessment"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
DEFINITION_DIGEST = (
    "82cdc82c402aacdb0070fb19671d896ae22a4c16d338ccbf27f02a51a396d527"
)

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
        connection.execute("DROP SCHEMA IF EXISTS assessment CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS platform CASCADE")
    runner = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS)
    expected = {
        "assessment_0001_knowledge_check_evidence",
        "assessment_0002_practice_evidence",
    }
    assert {item.migration_id for item in runner.apply_all()} == expected
    assert {item.migration_id for item in runner.apply_all()} == expected
    yield
    runner.rollback_all()


@pytest.fixture(autouse=True)
def empty_tables(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                assessment.practice_outbox,
                assessment.practice_completion_evidence,
                assessment.practice_scores,
                assessment.practice_responses,
                assessment.practice_attempts
            CASCADE
            """
        )


class CurriculumGateway:
    def resolve_practice(self, placement_id: str) -> PlacedPracticeReference:
        assert placement_id == "risk-return-practice-placement"
        return PlacedPracticeReference(
            placement_id=placement_id,
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest="a" * 64,
            practice_id="risk-return-practice",
            practice_version="1.0.0",
            definition_digest=DEFINITION_DIGEST,
        )


class ContentGateway:
    def get_practice_exact(
        self, _reference: PlacedPracticeReference
    ) -> PracticeDefinitionDocument:
        return PracticeDefinitionDocument(
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest="a" * 64,
            practice_id="risk-return-practice",
            schema_version="1.0.0",
            file_digest="b" * 64,
            value=DEFINITION.read_bytes(),
        )


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 10, 16, 15, 0, tzinfo=timezone.utc)


class SequentialIds:
    def __init__(self, start: int) -> None:
        self.value = start

    def new(self) -> str:
        self.value += 1
        return f"00000000-0000-4000-8000-{self.value:012d}"


def build_service(
    *, start: int = 100, before_outbox: object | None = None
) -> AssessmentService:
    assert POSTGRES_DSN is not None
    return AssessmentService(
        CurriculumGateway(),  # type: ignore[arg-type]
        ContentGateway(),  # type: ignore[arg-type]
        object(),
        object(),
        PostgresAssessmentRepository(
            POSTGRES_DSN,
            before_outbox=before_outbox,  # type: ignore[arg-type]
        ),
        FixedClock(),
        SequentialIds(start),
        ContractPracticeDefinitionAdapter(SCHEMAS),
        ContractPracticeSubmissionAdapter(SCHEMAS),
    )


def request(
    *,
    submission_id: str = "22222222-2222-4222-8222-222222222222",
    reorder: bool = False,
    conflicting: bool = False,
) -> SubmitPlacedPracticeRequest:
    document = json.loads(SUBMISSION.read_text(encoding="utf-8"))
    document["submission_id"] = submission_id
    if reorder:
        document["responses"].reverse()
        for response in document["responses"]:
            selected = response.get("selected_option_ids")
            if selected is not None:
                selected.reverse()
    if conflicting:
        for response in document["responses"]:
            if response["item_type"] == "single_select":
                response["selected_option_id"] = "guarantee"
    return SubmitPlacedPracticeRequest(
        learner_id=LEARNER_ID,
        placement_id="risk-return-practice-placement",
        submission=json.dumps(document).encode("utf-8"),
    )


def row_counts() -> tuple[int, ...]:
    assert POSTGRES_DSN is not None
    tables = (
        "practice_attempts",
        "practice_responses",
        "practice_scores",
        "practice_completion_evidence",
        "practice_outbox",
    )
    with psycopg.connect(POSTGRES_DSN) as connection:
        return tuple(
            connection.execute(
                f"SELECT count(*) FROM assessment.{table}"
            ).fetchone()[0]
            for table in tables
        )


def test_complete_attempt_commits_ordered_confidential_evidence() -> None:
    result = build_service().submit_placed_practice(request())

    assert result.score == 2
    assert result.max_score == 3
    assert row_counts() == (1, 3, 3, 1, 1)
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        positions = connection.execute(
            """
            SELECT item_position, item_id
            FROM assessment.practice_responses
            ORDER BY item_position
            """
        ).fetchall()
        event = connection.execute(
            "SELECT event_payload FROM assessment.practice_outbox"
        ).fetchone()[0]
        stored_result = connection.execute(
            "SELECT result FROM assessment.practice_completion_evidence"
        ).fetchone()[0]
    assert positions == [
        (0, "risk-meaning"),
        (1, "diversification-actions"),
        (2, "simple-growth"),
    ]
    serialized = json.dumps(event, sort_keys=True)
    assert event["source"]["evidence_id"] == result.evidence_id
    assert event["payload"]["score"] == 2
    assert stored_result["submitted_at"] == "2026-10-16T15:00:00Z"
    assert "selected_option_id" not in serialized
    assert "entered_value" not in serialized
    assert "feedback" not in serialized
    assert "correct_option" not in serialized


def test_exact_replay_is_order_independent_and_survives_restart() -> None:
    accepted = build_service(start=100).submit_placed_practice(request())
    restarted = build_service(start=300)

    replayed = restarted.submit_placed_practice(request(reorder=True))

    assert replayed == accepted
    assert row_counts() == (1, 3, 3, 1, 1)


def test_conflict_and_second_attempt_preserve_original_evidence() -> None:
    service = build_service()
    service.submit_placed_practice(request())

    with pytest.raises(AssessmentError) as conflict:
        service.submit_placed_practice(request(conflicting=True))
    assert conflict.value.code is AssessmentErrorCode.CONFLICT

    with pytest.raises(AssessmentError) as completed:
        service.submit_placed_practice(
            request(submission_id="33333333-3333-4333-8333-333333333333")
        )
    assert completed.value.code is AssessmentErrorCode.ALREADY_COMPLETED
    assert row_counts() == (1, 3, 3, 1, 1)


def test_concurrent_exact_duplicate_returns_one_original_result() -> None:
    services = (build_service(start=400), build_service(start=500))
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(service.submit_placed_practice, request())
            for service in services
        ]
    results = [future.result() for future in futures]

    assert results[0] == results[1]
    assert row_counts() == (1, 3, 3, 1, 1)


def test_outbox_failure_rolls_back_every_practice_evidence_table() -> None:
    def fail() -> None:
        raise psycopg.OperationalError("sentinel response and database path")

    with pytest.raises(AssessmentError) as captured:
        build_service(before_outbox=fail).submit_placed_practice(request())

    assert captured.value.code is AssessmentErrorCode.UNAVAILABLE
    assert "sentinel" not in str(captured.value.as_dict())
    assert row_counts() == (0, 0, 0, 0, 0)


def test_accepted_practice_evidence_rejects_update_and_delete() -> None:
    result = build_service().submit_placed_practice(request())
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        with pytest.raises(psycopg.DatabaseError):
            connection.execute(
                """
                UPDATE assessment.practice_scores
                SET score = 0
                WHERE attempt_id = %s
                """,
                (result.attempt_id,),
            )
        connection.rollback()
        with pytest.raises(psycopg.DatabaseError):
            connection.execute(
                """
                DELETE FROM assessment.practice_attempts
                WHERE attempt_id = %s
                """,
                (result.attempt_id,),
            )
    assert row_counts() == (1, 3, 3, 1, 1)
