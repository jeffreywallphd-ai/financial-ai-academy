from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path

import psycopg
import pytest

from financial_ai_academy.modules.learner_model.adapters.postgres_repository import (
    PostgresCompletionProjectionRepository,
)
from financial_ai_academy.modules.learner_model.adapters.preference_contract import (
    ContractLearnerPreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.adapters.system import (
    StablePreferenceSeed,
)
from financial_ai_academy.modules.learner_model.application.service import (
    LearnerModelService,
)
from financial_ai_academy.modules.learner_model.domain.preferences import (
    PreferenceMutation,
    PreferenceMutationIntent,
)
from financial_ai_academy.modules.learner_model.public import (
    LearnerModelError,
    LearnerModelErrorCode,
    MutateLearnerPreferencesRequest,
    OpenLearnerPreferencesRequest,
    ReadLearnerPreferenceHistoryRequest,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)


ROOT = Path(__file__).parents[4]
MIGRATIONS = ROOT / "backend" / "migrations"
LEARNER_MIGRATIONS = MIGRATIONS / "learner_model"
SCHEMAS = ROOT / "contracts" / "learning" / "learner-preferences" / "v1"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
OTHER_LEARNER_ID = "22222222-2222-4222-8222-222222222222"
NOW = datetime(2026, 10, 17, 19, 0, tzinfo=timezone.utc)

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
    PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS).apply_all()
    statuses = PostgresMigrationRunner(
        POSTGRES_DSN, LEARNER_MIGRATIONS
    ).apply_all()
    assert statuses[-1].migration_id == "learner_model_0004_preferences"
    yield
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as connection:
        connection.execute("DROP SCHEMA IF EXISTS learner_model CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS platform CASCADE")


@pytest.fixture(autouse=True)
def empty_rows(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            "TRUNCATE learner_model.preference_profiles CASCADE"
        )


class Source:
    pass


class Clock:
    def __init__(self) -> None:
        self.minute = 0

    def now(self) -> datetime:
        self.minute += 1
        return NOW + timedelta(minutes=self.minute)


class Identifiers:
    def __init__(self) -> None:
        self.value = 0

    def new(self) -> str:
        self.value += 1
        return f"00000000-0000-4000-8000-{self.value:012d}"


def service(*, before_save=None) -> LearnerModelService:
    assert POSTGRES_DSN is not None
    contract = ContractLearnerPreferenceAdapter(SCHEMAS)
    repository = PostgresCompletionProjectionRepository(
        POSTGRES_DSN,
        preference_contract=contract,
        before_preference_save=before_save,
    )
    return LearnerModelService(
        Source(),
        repository,
        Clock(),
        repository,
        contract,
        Identifiers(),
        StablePreferenceSeed(),
    )


def intent(
    key: str,
    revision: int,
    operation: str,
    **values: object,
) -> PreferenceMutationIntent:
    return PreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=key,
        expected_revision=revision,
        mutation=PreferenceMutation(operation=operation, **values),
    )


def mutate(
    subject: LearnerModelService,
    command: PreferenceMutationIntent,
    learner_id: str = LEARNER_ID,
):
    return subject.mutate_preferences(
        MutateLearnerPreferencesRequest(learner_id, command)
    )


def counts() -> tuple[int, int, int]:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        return (
            connection.execute(
                "SELECT count(*) FROM learner_model.preference_profiles"
            ).fetchone()[0],
            connection.execute(
                "SELECT count(*) FROM learner_model.preference_changes"
            ).fetchone()[0],
            connection.execute(
                "SELECT count(*) FROM learner_model.preference_mutations"
            ).fetchone()[0],
        )


def test_empty_read_is_virtual_and_first_mutation_survives_restart() -> None:
    empty = service().open_preferences(OpenLearnerPreferencesRequest(LEARNER_ID))
    assert empty.revision == 1
    assert counts() == (0, 0, 0)

    command = intent("intent.create-goal", 1, "create_goal", title="Research", detail=None)
    accepted = mutate(service(), command)
    reopened = service().open_preferences(OpenLearnerPreferencesRequest(LEARNER_ID))
    replayed = mutate(service(), command)

    assert reopened == accepted == replayed
    assert counts() == (1, 1, 1)


def test_stale_and_changed_key_reuse_write_nothing() -> None:
    first = intent("intent.create-interest", 1, "create_interest", label="Markets")
    mutate(service(), first)
    before = counts()

    changed = intent("intent.create-interest", 1, "create_interest", label="Risk")
    with pytest.raises(LearnerModelError) as conflict:
        mutate(service(), changed)
    assert conflict.value.code is LearnerModelErrorCode.IMMUTABLE_CONFLICT

    stale = intent("intent.stale", 1, "create_interest", label="Risk")
    with pytest.raises(LearnerModelError) as stale_error:
        mutate(service(), stale)
    assert stale_error.value.code is LearnerModelErrorCode.STALE_REVISION
    assert counts() == before


def test_profiles_and_replays_are_learner_isolated() -> None:
    mutate(
        service(),
        intent("intent.first", 1, "create_interest", label="Markets"),
    )
    other = service().open_preferences(
        OpenLearnerPreferencesRequest(OTHER_LEARNER_ID)
    )
    assert other.revision == 1
    assert other.interests == ()
    assert counts() == (1, 1, 1)


def test_history_retains_newest_one_hundred_summaries() -> None:
    subject = service()
    profile = mutate(
        subject,
        intent("intent.create", 1, "create_interest", label="Label 0"),
    )
    for index in range(1, 101):
        profile = mutate(
            subject,
            intent(
                f"intent.rename.{index:03d}",
                profile.revision,
                "rename_interest",
                entry_id=profile.interests[0].interest_id,
                label=f"Label {index}",
            ),
        )
    history = subject.read_preference_history(
        ReadLearnerPreferenceHistoryRequest(LEARNER_ID)
    )
    assert profile.revision == 102
    assert len(history.changes) == 100
    assert history.changes[0].revision == 3
    assert history.changes[-1].revision == 102


def test_interrupted_mutation_rolls_back_profile_change_and_replay() -> None:
    def fail() -> None:
        raise psycopg.OperationalError("private interruption")

    with pytest.raises(LearnerModelError) as failure:
        mutate(
            service(before_save=fail),
            intent("intent.interrupted", 1, "create_interest", label="Markets"),
        )
    assert failure.value.code is LearnerModelErrorCode.UNAVAILABLE
    assert counts() == (0, 0, 0)


def test_retained_data_refuses_down_and_empty_down_reapplies() -> None:
    assert POSTGRES_DSN is not None
    down = (
        LEARNER_MIGRATIONS / "learner_model_0004_preferences.down.sql"
    ).read_text(encoding="utf-8")
    up = (
        LEARNER_MIGRATIONS / "learner_model_0004_preferences.up.sql"
    ).read_text(encoding="utf-8")
    mutate(
        service(),
        intent("intent.retained", 1, "create_interest", label="Markets"),
    )
    with pytest.raises(psycopg.Error):
        with psycopg.connect(POSTGRES_DSN) as connection:
            connection.execute(down)
    assert counts() == (1, 1, 1)

    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            "TRUNCATE learner_model.preference_profiles CASCADE"
        )
        connection.execute(down)
        connection.execute(up)
    assert service().open_preferences(
        OpenLearnerPreferencesRequest(LEARNER_ID)
    ).revision == 1
