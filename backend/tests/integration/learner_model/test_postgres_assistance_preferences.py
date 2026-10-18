from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path

import psycopg
import pytest

from financial_ai_academy.modules.learner_model.adapters.assistance_preference_contract import (
    ContractAssistancePreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.adapters.postgres_repository import (
    PostgresCompletionProjectionRepository,
)
from financial_ai_academy.modules.learner_model.adapters.system import (
    StableAssistancePreferenceSeed,
)
from financial_ai_academy.modules.learner_model.application.service import (
    LearnerModelService,
)
from financial_ai_academy.modules.learner_model.domain.assistance_preferences import (
    AssistancePreferenceMutation,
    AssistancePreferenceMutationIntent,
)
from financial_ai_academy.modules.learner_model.public import (
    ExportAssistancePreferencesRequest,
    LearnerModelError,
    LearnerModelErrorCode,
    MutateAssistancePreferencesRequest,
    OpenAssistancePreferencesRequest,
    ReadAssistancePreferenceHistoryRequest,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)


ROOT = Path(__file__).parents[4]
MIGRATIONS = ROOT / "backend" / "migrations"
LEARNER_MIGRATIONS = MIGRATIONS / "learner_model"
SCHEMAS = (
    ROOT / "contracts" / "learning" / "learner-assistance-preferences" / "v1"
)
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
OTHER_LEARNER_ID = "22222222-2222-4222-8222-222222222222"
NOW = datetime(2026, 10, 17, 23, 0, tzinfo=timezone.utc)

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
        connection.execute("DROP SCHEMA IF EXISTS learner_model CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS platform CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS curriculum CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS content CASCADE")
    PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS).apply_all()
    statuses = PostgresMigrationRunner(
        POSTGRES_DSN, LEARNER_MIGRATIONS
    ).apply_all()
    assert statuses[-1].migration_id == (
        "learner_model_0006_assistance_preferences"
    )
    yield
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as connection:
        connection.execute("DROP SCHEMA IF EXISTS learner_model CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS platform CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS curriculum CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS content CASCADE")


@pytest.fixture(autouse=True)
def empty_rows(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            "TRUNCATE learner_model.assistance_preference_profiles CASCADE"
        )


class Source:
    pass


class Clock:
    def __init__(self) -> None:
        self.minute = 0

    def now(self) -> datetime:
        self.minute += 1
        return NOW + timedelta(minutes=self.minute)


def service(*, before_save=None, after_snapshot=None) -> LearnerModelService:
    assert POSTGRES_DSN is not None
    contract = ContractAssistancePreferenceAdapter(SCHEMAS)
    repository = PostgresCompletionProjectionRepository(
        POSTGRES_DSN,
        assistance_preference_contract=contract,
        before_assistance_preference_save=before_save,
        after_assistance_preference_snapshot=after_snapshot,
    )
    return LearnerModelService(
        Source(),
        repository,
        Clock(),
        assistance_preference_repository=repository,
        assistance_preference_contract=contract,
        assistance_preference_seeds=StableAssistancePreferenceSeed(),
    )


def intent(
    key: str, revision: int, mode: str = "on_request"
) -> AssistancePreferenceMutationIntent:
    return AssistancePreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=key,
        expected_revision=revision,
        mutation=AssistancePreferenceMutation(
            operation="replace_preferences",
            assistance_mode=mode,  # type: ignore[arg-type]
        ),
    )


def mutate(
    subject: LearnerModelService,
    command: AssistancePreferenceMutationIntent,
    learner_id: str = LEARNER_ID,
):
    return subject.mutate_assistance_preferences(
        MutateAssistancePreferencesRequest(learner_id, command)
    )


def counts(learner_id: str = LEARNER_ID) -> tuple[int, int, int]:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        return (
            connection.execute(
                "SELECT count(*) FROM learner_model.assistance_preference_profiles "
                "WHERE learner_id = %s",
                (learner_id,),
            ).fetchone()[0],
            connection.execute(
                "SELECT count(*) FROM learner_model.assistance_preference_changes "
                "WHERE learner_id = %s",
                (learner_id,),
            ).fetchone()[0],
            connection.execute(
                "SELECT count(*) FROM learner_model.assistance_preference_mutations "
                "WHERE learner_id = %s",
                (learner_id,),
            ).fetchone()[0],
        )


def test_default_is_virtual_and_mutation_and_replay_survive_restart() -> None:
    opened = service().open_assistance_preferences(
        OpenAssistancePreferencesRequest(LEARNER_ID)
    )
    assert (opened.revision, opened.assistance_mode) == (1, "off")
    assert counts() == (0, 0, 0)

    command = intent("assistance.first", 1)
    accepted = mutate(service(), command)
    reopened = service().open_assistance_preferences(
        OpenAssistancePreferencesRequest(LEARNER_ID)
    )
    replayed = mutate(service(), command)

    assert reopened == accepted == replayed
    assert counts() == (1, 1, 1)


def test_stale_changed_key_and_other_learner_are_isolated() -> None:
    accepted = mutate(service(), intent("assistance.one", 1))
    with pytest.raises(LearnerModelError) as changed:
        mutate(service(), intent("assistance.one", 1, "off"))
    assert changed.value.code is LearnerModelErrorCode.IMMUTABLE_CONFLICT
    with pytest.raises(LearnerModelError) as stale:
        mutate(service(), intent("assistance.stale", 1, "off"))
    assert stale.value.code is LearnerModelErrorCode.STALE_REVISION

    other = mutate(service(), intent("assistance.other", 1), OTHER_LEARNER_ID)
    assert accepted.learner_id == LEARNER_ID
    assert other.learner_id == OTHER_LEARNER_ID
    assert counts() == (1, 1, 1)
    assert counts(OTHER_LEARNER_ID) == (1, 1, 1)


def test_save_failure_rolls_back_profile_change_and_replay() -> None:
    def fail_before_replay() -> None:
        raise RuntimeError("simulated storage interruption")

    with pytest.raises(LearnerModelError) as captured:
        mutate(
            service(before_save=fail_before_replay),
            intent("assistance.rollback", 1),
        )
    assert captured.value.code is LearnerModelErrorCode.UNAVAILABLE
    assert counts() == (0, 0, 0)


def test_newest_one_hundred_history_and_export_are_coherent() -> None:
    subject = service()
    mode = "on_request"
    for revision in range(1, 106):
        mutate(
            subject,
            intent(f"assistance.history-{revision}", revision, mode),
        )
        mode = "off" if mode == "on_request" else "on_request"

    history = subject.read_assistance_preference_history(
        ReadAssistancePreferenceHistoryRequest(LEARNER_ID)
    )
    exported = subject.export_assistance_preferences(
        ExportAssistancePreferencesRequest(LEARNER_ID)
    )

    assert len(history.changes) == 100
    assert (history.changes[0].revision, history.changes[-1].revision) == (7, 106)
    assert exported.profile.revision == exported.history.current_revision == 106
    assert exported.history.changes[-1].resulting_profile_digest == (
        exported.profile.profile_digest
    )
    assert counts() == (1, 100, 105)


def test_history_and_export_fail_closed_when_a_retained_summary_is_missing() -> None:
    subject = service()
    mutate(subject, intent("assistance.integrity-1", 1))
    mutate(subject, intent("assistance.integrity-2", 2, "off"))
    mutate(subject, intent("assistance.integrity-3", 3))

    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            "DELETE FROM learner_model.assistance_preference_changes "
            "WHERE learner_id = %s AND revision = 3",
            (LEARNER_ID,),
        )

    for operation in (
        lambda: subject.read_assistance_preference_history(
            ReadAssistancePreferenceHistoryRequest(LEARNER_ID)
        ),
        lambda: subject.export_assistance_preferences(
            ExportAssistancePreferencesRequest(LEARNER_ID)
        ),
    ):
        with pytest.raises(LearnerModelError) as captured:
            operation()
        assert captured.value.code is LearnerModelErrorCode.INTEGRITY_FAILURE


def test_simultaneous_writers_accept_one_and_reject_one_without_partial_state() -> None:
    commands = (
        intent("assistance.concurrent-a", 1),
        intent("assistance.concurrent-b", 1),
    )

    def attempt(command: AssistancePreferenceMutationIntent):
        try:
            return ("accepted", mutate(service(), command).revision)
        except LearnerModelError as error:
            return (error.code.value, None)

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(attempt, commands))

    assert sorted(outcome[0] for outcome in outcomes) == [
        "accepted",
        "stale_revision",
    ]
    assert counts() == (1, 1, 1)


def test_down_refuses_retained_data_then_supports_empty_development_rollback() -> None:
    assert POSTGRES_DSN is not None
    mutate(service(), intent("assistance.retained", 1))
    down = (
        LEARNER_MIGRATIONS
        / "learner_model_0006_assistance_preferences.down.sql"
    ).read_text(encoding="utf-8")
    up = (
        LEARNER_MIGRATIONS
        / "learner_model_0006_assistance_preferences.up.sql"
    ).read_text(encoding="utf-8")

    with psycopg.connect(POSTGRES_DSN, autocommit=True) as connection:
        with pytest.raises(psycopg.errors.RaiseException):
            connection.execute(down)
        connection.execute(
            "TRUNCATE learner_model.assistance_preference_profiles CASCADE"
        )
        connection.execute(down)
        connection.execute(up)

    assert counts() == (0, 0, 0)
