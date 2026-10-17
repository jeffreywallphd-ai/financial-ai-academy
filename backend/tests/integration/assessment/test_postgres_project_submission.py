from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

import psycopg
import pytest

from financial_ai_academy.modules.assessment.adapters.postgres_repository import (
    PostgresAssessmentRepository,
)
from financial_ai_academy.modules.assessment.adapters.project_submission_contract import (
    ContractProjectSubmissionAdapter,
)
from financial_ai_academy.modules.assessment.application.service import AssessmentService
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    AssessmentErrorCode,
    ReadProjectCompletionHistoryRequest,
    SubmitProjectSnapshotRequest,
)
from financial_ai_academy.platform.database.migrations import PostgresMigrationRunner


ROOT = Path(__file__).resolve().parents[4]
SCHEMAS = ROOT / "contracts/learning/assessment/project/v1"
CORPUS = ROOT / "contracts/compatibility/assessment-project/v1/approved"
MIGRATIONS = ROOT / "backend/migrations/assessment"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
LEARNER = "11111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 10, 17, 4, tzinfo=timezone.utc)

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
        "assessment_0004_project_submission_evidence",
    }
    assert {item.migration_id for item in runner.apply_all()} == expected
    assert {item.migration_id for item in runner.apply_all()} == expected
    yield
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                assessment.project_outbox,
                assessment.project_submissions,
                assessment.project_submission_scopes,
                assessment.project_submission_identities
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
                assessment.project_outbox,
                assessment.project_submissions,
                assessment.project_submission_scopes,
                assessment.project_submission_identities
            CASCADE
            """
        )
        connection.execute(
            "ALTER SEQUENCE assessment.project_submission_accepted_sequence RESTART WITH 1"
        )


class Unused:
    def __getattr__(self, name):
        raise AssertionError(f"Unexpected dependency call: {name}")


class Source:
    def __init__(self, candidate):
        self.candidate = candidate

    def resolve(self, *, learner_id, project_id, snapshot_id):
        assert learner_id == LEARNER
        assert project_id == self.candidate.project.project_id
        assert snapshot_id == self.candidate.project.snapshot_id
        return self.candidate


class Clock:
    def __init__(self, offset: int = 0):
        self.value = NOW + timedelta(minutes=offset)

    def now(self):
        return self.value


class Ids:
    def __init__(self, start: int):
        self.value = start

    def new(self):
        self.value += 1
        return str(UUID(int=self.value))


def _approved(name: str) -> dict:
    return json.loads((CORPUS / f"{name}.json").read_text(encoding="utf-8"))


def _service(
    *,
    candidate_document: dict | None = None,
    start: int = 100,
    minute: int = 0,
    before_outbox=None,
):
    assert POSTGRES_DSN is not None
    contract = ContractProjectSubmissionAdapter(SCHEMAS)
    document = candidate_document or _approved("snapshot-candidate")
    candidate = contract.parse_candidate(json.dumps(document).encode())
    repository = PostgresAssessmentRepository(
        POSTGRES_DSN,
        before_outbox=before_outbox,
        project_submission_contract=contract,
    )
    return AssessmentService(
        Unused(),
        Unused(),
        Unused(),
        Unused(),
        repository,
        Clock(minute),
        Ids(start),
        project_submission_source=Source(candidate),
        project_submission_contract=contract,
    )


def _request(
    candidate_document: dict | None = None,
    submission_document: dict | None = None,
) -> SubmitProjectSnapshotRequest:
    candidate = candidate_document or _approved("snapshot-candidate")
    submission = submission_document or _approved("submission")
    return SubmitProjectSnapshotRequest(
        LEARNER,
        candidate["project"]["project_id"],
        candidate["project"]["snapshot_id"],
        json.dumps(submission, ensure_ascii=False).encode(),
    )


def _counts() -> tuple[int, ...]:
    assert POSTGRES_DSN is not None
    tables = (
        "project_submission_identities",
        "project_submission_scopes",
        "project_submissions",
        "project_outbox",
    )
    with psycopg.connect(POSTGRES_DSN) as connection:
        return tuple(
            connection.execute(
                f"SELECT count(*) FROM assessment.{table}"
            ).fetchone()[0]
            for table in tables
        )


def test_project_evidence_commits_atomically_and_reopens_after_restart() -> None:
    accepted = _service().submit_project_snapshot(_request())
    restarted = _service(start=500)
    history = restarted.read_project_completion_history(
        ReadProjectCompletionHistoryRequest(LEARNER, "project-retirement-plan")
    )

    assert accepted.evidence is not None
    assert history.items == (accepted.evidence,)
    assert _counts() == (1, 1, 1, 1)
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        event = connection.execute(
            "SELECT event_payload FROM assessment.project_outbox"
        ).fetchone()[0]
    serialized = json.dumps(event, sort_keys=True)
    assert event["payload"]["project_id"] == "project-retirement-plan"
    assert "learner_id" not in serialized
    assert "milestone_evidence" not in serialized
    assert "content_digest" not in serialized


def test_exact_replay_conflict_and_concurrency_preserve_one_original() -> None:
    services = (_service(start=100), _service(start=300))
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(item.submit_project_snapshot, _request()) for item in services]
    results = [future.result().evidence for future in futures]
    assert results[0] == results[1]
    assert _counts() == (1, 1, 1, 1)

    changed = _approved("submission")
    changed["milestone_evidence"][1]["resources"] = [
        changed["milestone_evidence"][0]["resources"][0]
    ]
    with pytest.raises(AssessmentError) as captured:
        _service(start=700).submit_project_snapshot(
            _request(submission_document=changed)
        )
    assert captured.value.code is AssessmentErrorCode.CONFLICT
    assert _counts() == (1, 1, 1, 1)


def test_later_snapshot_appends_supersession_without_mutation() -> None:
    first = _service(start=100).submit_project_snapshot(_request()).evidence
    assert first is not None
    candidate = _approved("snapshot-candidate")
    candidate["project"]["snapshot_id"] = "snapshot-retirement-plan-02"
    candidate["project"]["snapshot_digest"] = "9" * 64
    candidate["project"]["workspace_revision"] = 8
    candidate["project"]["closed_at"] = "2026-10-17T04:01:00Z"
    submission = _approved("submission")
    submission["submission_id"] = "submission-retirement-02"
    submission["source"]["snapshot_id"] = candidate["project"]["snapshot_id"]
    submission["source"]["snapshot_digest"] = candidate["project"]["snapshot_digest"]

    second = _service(
        candidate_document=candidate, start=300, minute=1
    ).submit_project_snapshot(
        _request(candidate_document=candidate, submission_document=submission)
    ).evidence
    history = _service(
        candidate_document=candidate, start=500, minute=2
    ).read_project_completion_history(
        ReadProjectCompletionHistoryRequest(LEARNER, "project-retirement-plan")
    )

    assert second is not None
    assert first.occurrence == 1
    assert first.supersedes_submission_id is None
    assert second.occurrence == 2
    assert second.supersedes_submission_id == "submission-retirement-01"
    assert history.items == (first, second)
    assert _counts() == (2, 1, 2, 2)


def test_outbox_failure_rolls_back_and_evidence_is_append_only() -> None:
    def fail() -> None:
        raise psycopg.OperationalError("sentinel private database path")

    with pytest.raises(AssessmentError) as captured:
        _service(before_outbox=fail).submit_project_snapshot(_request())
    assert captured.value.code is AssessmentErrorCode.UNAVAILABLE
    assert "sentinel" not in str(captured.value.as_dict())
    assert _counts() == (0, 0, 0, 0)

    accepted = _service().submit_project_snapshot(_request()).evidence
    assert accepted is not None
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        with pytest.raises(psycopg.DatabaseError):
            connection.execute(
                "UPDATE assessment.project_submissions SET occurrence = 9 WHERE evidence_id = %s",
                (accepted.evidence_id,),
            )
        connection.rollback()
        with pytest.raises(psycopg.DatabaseError):
            connection.execute(
                "DELETE FROM assessment.project_outbox WHERE evidence_id = %s",
                (accepted.evidence_id,),
            )
    assert _counts() == (1, 1, 1, 1)
