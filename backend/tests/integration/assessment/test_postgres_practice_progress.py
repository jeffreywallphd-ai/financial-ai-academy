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
from financial_ai_academy.modules.assessment.adapters.practice_progress_contract import (
    ContractPracticeProgressAdapter,
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
    ReadCompletedPracticesRequest,
    ReadPlacedPracticeProgressRequest,
    SavePlacedPracticeDraftRequest,
    SubmitPlacedPracticeRequest,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)


REPOSITORY = Path(__file__).resolve().parents[4]
SCHEMAS = REPOSITORY / "contracts/learning/assessment/practice/v1"
CORPUS = REPOSITORY / "contracts/compatibility/assessment-practice/v1/approved"
MIGRATIONS = REPOSITORY / "backend/migrations/assessment"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
LEARNER_ID = "11111111-1111-4111-8111-111111111111"

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
        "assessment_0003_practice_progress",
    }
    assert {item.migration_id for item in runner.apply_all()} == expected
    assert {item.migration_id for item in runner.apply_all()} == expected
    yield
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                assessment.practice_drafts,
                assessment.practice_outbox,
                assessment.practice_completion_evidence,
                assessment.practice_scores,
                assessment.practice_responses,
                assessment.practice_attempts,
                assessment.practice_retry_scopes
            CASCADE
            """
        )
    runner.rollback_all()


@pytest.fixture(autouse=True)
def empty_tables(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                assessment.practice_drafts,
                assessment.practice_outbox,
                assessment.practice_completion_evidence,
                assessment.practice_scores,
                assessment.practice_responses,
                assessment.practice_attempts,
                assessment.practice_retry_scopes
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
            definition_digest=(
                "82cdc82c402aacdb0070fb19671d896ae22a4c16d338ccbf27f02a51a396d527"
            ),
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
            value=(CORPUS / "definition.json").read_bytes(),
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
        ContractPracticeProgressAdapter(SCHEMAS),
    )


def draft_bytes(
    *, expected_revision: int = 0, changed: bool = False, reorder: bool = False
) -> bytes:
    document = json.loads((CORPUS / "draft-save.json").read_text(encoding="utf-8"))
    document["expected_revision"] = expected_revision
    if changed:
        document["responses"] = document["responses"][:1]
    if reorder:
        document["responses"].reverse()
    return json.dumps(document).encode("utf-8")


def save_request(**changes: object) -> SavePlacedPracticeDraftRequest:
    return SavePlacedPracticeDraftRequest(
        learner_id=str(changes.pop("learner_id", LEARNER_ID)),
        placement_id="risk-return-practice-placement",
        draft=draft_bytes(**changes),  # type: ignore[arg-type]
    )


def submit_request(submission_id: str) -> SubmitPlacedPracticeRequest:
    document = json.loads(
        (CORPUS / "submission.json").read_text(encoding="utf-8")
    )
    document["submission_id"] = submission_id
    return SubmitPlacedPracticeRequest(
        learner_id=LEARNER_ID,
        placement_id="risk-return-practice-placement",
        submission=json.dumps(document).encode("utf-8"),
    )


def progress_request() -> ReadPlacedPracticeProgressRequest:
    return ReadPlacedPracticeProgressRequest(
        learner_id=LEARNER_ID,
        placement_id="risk-return-practice-placement",
    )


def test_conditional_draft_save_replay_replace_conflict_and_restart() -> None:
    service = build_service()
    created = service.save_placed_practice_draft(save_request())
    replayed = service.save_placed_practice_draft(save_request(reorder=True))
    replaced = service.save_placed_practice_draft(
        save_request(expected_revision=1, changed=True)
    )

    assert created.revision == replayed.revision == 1
    assert created.response_fingerprint == replayed.response_fingerprint
    assert replaced.revision == 2
    with pytest.raises(AssessmentError) as stale:
        service.save_placed_practice_draft(
            save_request(expected_revision=0)
        )
    assert stale.value.code is AssessmentErrorCode.CONFLICT
    assert build_service(start=500).read_placed_practice_draft(
        progress_request()
    ) == replaced
    assert build_service(start=600).read_placed_practice_draft(
        ReadPlacedPracticeProgressRequest(
            learner_id="99999999-9999-4999-8999-999999999999",
            placement_id="risk-return-practice-placement",
        )
    ) is None


def test_corrupt_draft_fails_closed_without_exposing_stored_values() -> None:
    service = build_service()
    service.save_placed_practice_draft(save_request())
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            UPDATE assessment.practice_drafts
            SET responses = jsonb_set(
                responses,
                '{0,correct_answer}',
                '"sentinel-private-answer"'::jsonb
            )
            """
        )

    with pytest.raises(AssessmentError) as captured:
        service.read_placed_practice_draft(progress_request())

    assert captured.value.code is AssessmentErrorCode.UNAVAILABLE
    assert "sentinel" not in str(captured.value.as_dict())


def test_success_clears_only_matching_draft_and_failure_preserves_it() -> None:
    service = build_service()
    service.save_placed_practice_draft(save_request())
    service.submit_placed_practice(
        submit_request("22222222-2222-4222-8222-222222222222")
    )
    assert service.read_placed_practice_draft(progress_request()) is None

    def fail() -> None:
        raise psycopg.OperationalError("sentinel private database failure")

    failing = build_service(start=700, before_outbox=fail)
    failing.save_placed_practice_draft(save_request())
    with pytest.raises(AssessmentError) as captured:
        failing.submit_placed_practice(
            submit_request("33333333-3333-4333-8333-333333333333")
        )
    assert captured.value.code is AssessmentErrorCode.UNAVAILABLE
    assert build_service(start=800).read_placed_practice_draft(
        progress_request()
    ) is not None


def test_retry_state_and_typed_replay_survive_restart_without_answers() -> None:
    service = build_service()
    service.submit_placed_practice(
        submit_request("22222222-2222-4222-8222-222222222222")
    )
    service.submit_placed_practice(
        submit_request("33333333-3333-4333-8333-333333333333")
    )
    restarted = build_service(start=900)
    retry = restarted.read_placed_practice_retry_state(progress_request())
    replay = restarted.read_completed_practices(
        ReadCompletedPracticesRequest(
            learner_id=LEARNER_ID,
            placement_id="risk-return-practice-placement",
        )
    )

    assert (retry.attempts_used, retry.attempts_remaining, retry.can_retry) == (
        2,
        1,
        True,
    )
    assert [item.attempt_order for item in replay] == [1, 2]
    serialized = json.dumps(
        [item.event.item_scores[0].item_id for item in replay]
    )
    assert "selected_option" not in serialized
    assert "entered_value" not in serialized
    assert "feedback" not in serialized


def test_concurrent_final_slot_accepts_at_most_one_distinct_submission() -> None:
    initial = build_service()
    initial.submit_placed_practice(
        submit_request("22222222-2222-4222-8222-222222222222")
    )
    initial.submit_placed_practice(
        submit_request("33333333-3333-4333-8333-333333333333")
    )
    calls = (
        (build_service(start=1000), "44444444-4444-4444-8444-444444444444"),
        (build_service(start=2000), "55555555-5555-4555-8555-555555555555"),
    )

    def submit(call: tuple[AssessmentService, str]) -> object:
        service, submission_id = call
        try:
            return service.submit_placed_practice(submit_request(submission_id))
        except AssessmentError as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(submit, calls))

    assert sum(not isinstance(item, AssessmentError) for item in results) == 1
    denials = [item for item in results if isinstance(item, AssessmentError)]
    assert denials[0].code is AssessmentErrorCode.ATTEMPT_LIMIT_REACHED
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute(
            "SELECT attempt_order FROM assessment.practice_attempts ORDER BY attempt_order"
        ).fetchall() == [(1,), (2,), (3,)]


def test_retained_result_and_event_bytes_do_not_gain_attempt_order() -> None:
    result = build_service().submit_placed_practice(
        submit_request("22222222-2222-4222-8222-222222222222")
    )
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        stored = connection.execute(
            """
            SELECT e.result, o.event_payload, a.attempt_order
            FROM assessment.practice_attempts AS a
            JOIN assessment.practice_completion_evidence AS e
              ON e.attempt_id = a.attempt_id
            JOIN assessment.practice_outbox AS o
              ON o.evidence_id = e.evidence_id
            WHERE a.attempt_id = %s
            """,
            (result.attempt_id,),
        ).fetchone()
    assert stored[2] == 1
    assert "attempt_order" not in stored[0]
    assert "attempt_order" not in stored[1]


def test_progress_migration_round_trip_preserves_existing_evidence_bytes() -> None:
    result = build_service().submit_placed_practice(
        submit_request("22222222-2222-4222-8222-222222222222")
    )
    assert POSTGRES_DSN is not None
    down = MIGRATIONS / "assessment_0003_practice_progress.down.sql"
    with psycopg.connect(POSTGRES_DSN) as connection:
        before = connection.execute(
            """
            SELECT e.result::text, o.event_payload::text
            FROM assessment.practice_completion_evidence AS e
            JOIN assessment.practice_outbox AS o
              ON o.evidence_id = e.evidence_id
            WHERE e.attempt_id = %s
            """,
            (result.attempt_id,),
        ).fetchone()
        connection.execute(down.read_text(encoding="utf-8"))
        connection.execute(
            """
            DELETE FROM platform.schema_migrations
            WHERE migration_id = 'assessment_0003_practice_progress'
            """
        )
    reapplied = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS).apply_all()
    assert {item.migration_id for item in reapplied} == {
        "assessment_0001_knowledge_check_evidence",
        "assessment_0002_practice_evidence",
        "assessment_0003_practice_progress",
    }
    with psycopg.connect(POSTGRES_DSN) as connection:
        after = connection.execute(
            """
            SELECT e.result::text, o.event_payload::text, a.attempt_order
            FROM assessment.practice_completion_evidence AS e
            JOIN assessment.practice_outbox AS o
              ON o.evidence_id = e.evidence_id
            JOIN assessment.practice_attempts AS a
              ON a.attempt_id = e.attempt_id
            WHERE e.attempt_id = %s
            """,
            (result.attempt_id,),
        ).fetchone()
    assert after[:2] == before
    assert after[2] == 1
