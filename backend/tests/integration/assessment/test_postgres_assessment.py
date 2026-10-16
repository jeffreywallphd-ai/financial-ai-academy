from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import pytest

from financial_ai_academy.modules.assessment.adapters.content_gateway import (
    PublicContentDefinitionGateway,
)
from financial_ai_academy.modules.assessment.adapters.contract import (
    ContractAssessmentDefinitionParser,
)
from financial_ai_academy.modules.assessment.adapters.curriculum_gateway import (
    PublicCurriculumAssessmentGateway,
)
from financial_ai_academy.modules.assessment.adapters.event_contract import (
    ContractAssessmentEventParser,
)
from financial_ai_academy.modules.assessment.adapters.postgres_repository import (
    PostgresAssessmentRepository,
)
from financial_ai_academy.modules.assessment.application.service import (
    AssessmentService,
)
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    AssessmentErrorCode,
    OpenPlacedKnowledgeCheckRequest,
    ReadCompletedKnowledgeChecksRequest,
    SubmitPlacedKnowledgeCheckRequest,
)
from financial_ai_academy.modules.content.adapters.lesson_package import (
    ContractLessonPackageValidator,
)
from financial_ai_academy.modules.content.adapters.postgres_repository import (
    PostgresContentRepository,
)
from financial_ai_academy.modules.content.application.service import ContentService
from financial_ai_academy.modules.content.public import AdmitLessonPackageRequest
from financial_ai_academy.modules.curriculum.adapters.content_gateway import (
    PublicContentGateway,
)
from financial_ai_academy.modules.curriculum.adapters.postgres_repository import (
    PostgresCurriculumRepository,
)
from financial_ai_academy.modules.curriculum.application.service import (
    CurriculumService,
)
from financial_ai_academy.modules.curriculum.public import (
    CreateAssessmentPlacementRequest,
    CreateLessonPlacementRequest,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)
from financial_ai_academy.platform.object_storage.filesystem import (
    FilesystemObjectStorage,
)


REPOSITORY = Path(__file__).resolve().parents[4]
PACKAGE = (
    REPOSITORY
    / "contracts/compatibility/lesson-package/v1/approved/intro-risk-return-knowledge-check"
)
LESSON_SCHEMAS = REPOSITORY / "contracts/learning/lesson-package/v1"
ASSESSMENT_SCHEMAS = REPOSITORY / "contracts/learning/assessment/v1"
EVENT_SCHEMAS = REPOSITORY / "contracts/events/assessment/v1"
MIGRATIONS = REPOSITORY / "backend/migrations"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
LEARNER_ID = "11111111-1111-4111-8111-111111111111"

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(
        POSTGRES_DSN is None,
        reason="FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN is not configured",
    ),
]


def _remove_stream(migration_id: str, down: Path) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(down.read_text(encoding="utf-8"))
        connection.execute(
            "DELETE FROM platform.schema_migrations WHERE migration_id = %s",
            (migration_id,),
        )


@pytest.fixture(scope="module", autouse=True)
def migrated_database() -> object:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute("DROP SCHEMA IF EXISTS assessment CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS identity CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS curriculum CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS content CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS platform CASCADE")
    root = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS)
    curriculum = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS / "curriculum")
    assessment = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS / "assessment")
    assert [item.migration_id for item in root.apply_all()] == [
        "0001_content_lesson_package_versions",
        "0002_curriculum_lesson_placements",
    ]
    curriculum_ids = {
        item.migration_id for item in curriculum.apply_all()
    }
    assert "curriculum_0001_assessment_placements" in curriculum_ids
    assessment_ids = {item.migration_id for item in assessment.apply_all()}
    assert "assessment_0001_knowledge_check_evidence" in assessment_ids
    assert "assessment_0002_practice_evidence" in assessment_ids
    assert {item.migration_id for item in assessment.apply_all()} == {
        "0001_content_lesson_package_versions",
        "0002_curriculum_lesson_placements",
        "curriculum_0001_assessment_placements",
        "curriculum_0002_discovery_projection",
        "curriculum_0003_curriculum_graphs",
        "curriculum_0004_practice_placements",
        "assessment_0001_knowledge_check_evidence",
        "assessment_0002_practice_evidence",
    }
    yield
    _remove_stream(
        "assessment_0002_practice_evidence",
        MIGRATIONS / "assessment/assessment_0002_practice_evidence.down.sql",
    )
    _remove_stream(
        "assessment_0001_knowledge_check_evidence",
        MIGRATIONS
        / "assessment/assessment_0001_knowledge_check_evidence.down.sql",
    )
    _remove_stream(
        "curriculum_0004_practice_placements",
        MIGRATIONS
        / "curriculum/curriculum_0004_practice_placements.down.sql",
    )
    _remove_stream(
        "curriculum_0003_curriculum_graphs",
        MIGRATIONS
        / "curriculum/curriculum_0003_curriculum_graphs.down.sql",
    )
    _remove_stream(
        "curriculum_0002_discovery_projection",
        MIGRATIONS
        / "curriculum/curriculum_0002_discovery_projection.down.sql",
    )
    _remove_stream(
        "curriculum_0001_assessment_placements",
        MIGRATIONS
        / "curriculum/curriculum_0001_assessment_placements.down.sql",
    )
    root.rollback_all()


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
                assessment.practice_attempts,
                assessment.outbox,
                assessment.completion_evidence,
                assessment.scores,
                assessment.responses,
                assessment.attempts,
                curriculum.assessment_placements,
                curriculum.lesson_placements,
                content.lesson_package_versions
            CASCADE
            """
        )


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)


class SequentialIds:
    def __init__(self, start: int = 100) -> None:
        self._value = start

    def new(self) -> str:
        self._value += 1
        return f"00000000-0000-4000-8000-{self._value:012d}"


def build_service(
    tmp_path: Path,
    *,
    ids_start: int = 100,
    before_outbox: object | None = None,
) -> AssessmentService:
    assert POSTGRES_DSN is not None
    content = ContentService(
        PostgresContentRepository(POSTGRES_DSN),
        FilesystemObjectStorage(tmp_path / "objects"),
        ContractLessonPackageValidator(LESSON_SCHEMAS),
    )
    curriculum = CurriculumService(
        PostgresCurriculumRepository(POSTGRES_DSN),
        PublicContentGateway(content),
    )
    accepted = content.admit_lesson_package(AdmitLessonPackageRequest(PACKAGE))
    lesson = curriculum.create_lesson_placement(
        CreateLessonPlacementRequest(
            placement_id="intro-risk-return",
            package_id=accepted.package_id,
            package_version=accepted.package_version,
            package_digest=accepted.package_digest,
        )
    )
    curriculum.create_assessment_placement(
        CreateAssessmentPlacementRequest(
            placement_id=lesson.placement_id,
            package_id=accepted.package_id,
            package_version=accepted.package_version,
            package_digest=accepted.package_digest,
            assessment_id="risk-return-check-1",
            assessment_version="1.0.0",
            definition_digest="98e941f9b53ef429cb6d359246ddb9812e354db2a9381a2ee180ed5758343d2b",
            item_id="risk-return-tradeoff",
            item_version="1.0.0",
            scoring_policy_id="single-select-exact-match",
            scoring_policy_version="1.0.0",
        )
    )
    repository = PostgresAssessmentRepository(
        POSTGRES_DSN,
        before_outbox=before_outbox,  # type: ignore[arg-type]
    )
    return AssessmentService(
        PublicCurriculumAssessmentGateway(curriculum),
        PublicContentDefinitionGateway(content),
        ContractAssessmentDefinitionParser(ASSESSMENT_SCHEMAS),
        ContractAssessmentEventParser(EVENT_SCHEMAS),
        repository,
        FixedClock(),
        SequentialIds(ids_start),
    )


def submission(
    service: AssessmentService,
    *,
    submission_id: str = "22222222-2222-4222-8222-222222222222",
    option_id: str = "higher-potential-higher-uncertainty",
) -> SubmitPlacedKnowledgeCheckRequest:
    value = service.open_placed_knowledge_check(
        OpenPlacedKnowledgeCheckRequest("intro-risk-return")
    )
    return SubmitPlacedKnowledgeCheckRequest(
        learner_id=LEARNER_ID,
        submission_id=submission_id,
        placement_id=value.placement_id,
        package_id=value.package_id,
        package_version=value.package_version,
        package_digest=value.package_digest,
        assessment_id=value.assessment_id,
        assessment_version=value.assessment_version,
        definition_digest=value.definition_digest,
        item_id=value.item_id,
        item_version=value.item_version,
        scoring_policy_id=value.scoring_policy_id,
        scoring_policy_version=value.scoring_policy_version,
        selected_option_id=option_id,
    )


def row_counts() -> tuple[int, ...]:
    assert POSTGRES_DSN is not None
    tables = (
        "attempts",
        "responses",
        "scores",
        "completion_evidence",
        "outbox",
    )
    with psycopg.connect(POSTGRES_DSN) as connection:
        return tuple(
            connection.execute(
                f"SELECT count(*) FROM assessment.{table}"
            ).fetchone()[0]
            for table in tables
        )


@pytest.mark.parametrize(
    ("option_id", "expected_score", "feedback_id"),
    [
        ("higher-potential-higher-uncertainty", 1, "risk-return-correct"),
        ("higher-risk-guarantees-return", 0, "risk-return-review"),
    ],
)
def test_correct_and_incorrect_results_commit_one_atomic_evidence_set(
    tmp_path: Path,
    option_id: str,
    expected_score: int,
    feedback_id: str,
) -> None:
    service = build_service(tmp_path)
    result = service.submit_placed_knowledge_check(
        submission(service, option_id=option_id)
    )
    assert result.score == expected_score
    assert result.correct is (expected_score == 1)
    assert result.feedback.feedback_id == feedback_id
    assert row_counts() == (1, 1, 1, 1, 1)
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        event = connection.execute(
            "SELECT event_payload FROM assessment.outbox"
        ).fetchone()[0]
    serialized = str(event)
    assert event["source"]["evidence_id"] == result.evidence_id
    assert event["payload"]["score"] == expected_score
    assert "selected_option_id" not in serialized
    assert "feedback" not in serialized
    assert "correct_option_id" not in serialized


def test_exact_replay_conflict_and_already_completed_preserve_one_set(
    tmp_path: Path,
) -> None:
    service = build_service(tmp_path)
    request = submission(service)
    accepted = service.submit_placed_knowledge_check(request)
    assert service.submit_placed_knowledge_check(request) == accepted
    with pytest.raises(AssessmentError) as conflict:
        service.submit_placed_knowledge_check(
            replace(request, selected_option_id="higher-risk-guarantees-return")
        )
    assert conflict.value.code is AssessmentErrorCode.CONFLICT
    with pytest.raises(AssessmentError) as completed:
        service.submit_placed_knowledge_check(
            replace(
                request,
                submission_id="33333333-3333-4333-8333-333333333333",
            )
        )
    assert completed.value.code is AssessmentErrorCode.ALREADY_COMPLETED
    assert row_counts() == (1, 1, 1, 1, 1)


def test_completion_event_query_is_exact_filtered_and_read_only(
    tmp_path: Path,
) -> None:
    service = build_service(tmp_path)
    result = service.submit_placed_knowledge_check(submission(service))
    request = ReadCompletedKnowledgeChecksRequest(
        learner_id=LEARNER_ID,
        placement_id="intro-risk-return",
    )
    first = service.read_completed_knowledge_checks(request)
    second = service.read_completed_knowledge_checks(request)
    assert first == second
    assert len(first) == 1
    assert first[0].attempt_id == result.attempt_id
    assert first[0].evidence_id == result.evidence_id
    assert row_counts() == (1, 1, 1, 1, 1)
    assert service.read_completed_knowledge_checks(
        replace(request, learner_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    ) == ()
    assert service.read_completed_knowledge_checks(
        replace(request, placement_id="another-placement")
    ) == ()


def test_concurrent_exact_duplicate_returns_one_original_result(
    tmp_path: Path,
) -> None:
    first = build_service(tmp_path / "first", ids_start=200)
    second = build_service(tmp_path / "first", ids_start=300)
    request = submission(first)
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(service.submit_placed_knowledge_check, request)
            for service in (first, second)
        ]
    results = [future.result() for future in futures]
    assert results[0] == results[1]
    assert row_counts() == (1, 1, 1, 1, 1)


def test_stale_or_unknown_input_creates_no_evidence(
    tmp_path: Path,
) -> None:
    service = build_service(tmp_path)
    request = submission(service)
    with pytest.raises(AssessmentError) as stale:
        service.submit_placed_knowledge_check(
            replace(request, definition_digest="a" * 64)
        )
    assert stale.value.code is AssessmentErrorCode.STALE_REFERENCE
    with pytest.raises(AssessmentError) as unknown:
        service.submit_placed_knowledge_check(
            replace(request, selected_option_id="not-declared")
        )
    assert unknown.value.code is AssessmentErrorCode.UNKNOWN_OPTION
    assert row_counts() == (0, 0, 0, 0, 0)


def test_outbox_failure_rolls_back_every_evidence_table(
    tmp_path: Path,
) -> None:
    def fail() -> None:
        raise psycopg.OperationalError("sentinel path and response")

    service = build_service(tmp_path, before_outbox=fail)
    with pytest.raises(AssessmentError) as captured:
        service.submit_placed_knowledge_check(submission(service))
    assert captured.value.code is AssessmentErrorCode.UNAVAILABLE
    assert "sentinel" not in str(captured.value.as_dict())
    assert row_counts() == (0, 0, 0, 0, 0)


def test_accepted_evidence_rejects_update_and_delete(
    tmp_path: Path,
) -> None:
    service = build_service(tmp_path)
    result = service.submit_placed_knowledge_check(submission(service))
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        with pytest.raises(psycopg.DatabaseError):
            connection.execute(
                "UPDATE assessment.scores SET score = 0 WHERE attempt_id = %s",
                (result.attempt_id,),
            )
        connection.rollback()
        with pytest.raises(psycopg.DatabaseError):
            connection.execute(
                "DELETE FROM assessment.attempts WHERE attempt_id = %s",
                (result.attempt_id,),
            )
    assert row_counts() == (1, 1, 1, 1, 1)
