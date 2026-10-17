from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from threading import Event

import psycopg
import pytest

from financial_ai_academy.modules.learner_model.adapters.postgres_repository import (
    PostgresCompletionProjectionRepository,
)
from financial_ai_academy.modules.learner_model.adapters.presentation_preference_contract import (  # noqa: E501
    ContractPresentationPreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.adapters.system import (
    StablePresentationPreferenceSeed,
)
from financial_ai_academy.modules.learner_model.application.service import (
    LearnerModelService,
)
from financial_ai_academy.modules.learner_model.domain.presentation_preferences import (
    PresentationPreferenceMutation,
    PresentationPreferenceMutationIntent,
)
from financial_ai_academy.modules.learner_model.public import (
    ExportPresentationPreferencesRequest,
    LearnerModelError,
    LearnerModelErrorCode,
    MutatePresentationPreferencesRequest,
    OpenPresentationPreferencesRequest,
    ReadPresentationPreferenceHistoryRequest,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)


ROOT = Path(__file__).parents[4]
MIGRATIONS = ROOT / "backend" / "migrations"
LEARNER_MIGRATIONS = MIGRATIONS / "learner_model"
SCHEMAS = (
    ROOT / "contracts" / "learning" / "learner-presentation-preferences" / "v1"
)
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
OTHER_LEARNER_ID = "22222222-2222-4222-8222-222222222222"
NOW = datetime(2026, 10, 17, 20, 0, tzinfo=timezone.utc)

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
        "learner_model_0005_presentation_preferences"
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
            "TRUNCATE learner_model.presentation_preference_profiles CASCADE"
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
    contract = ContractPresentationPreferenceAdapter(SCHEMAS)
    repository = PostgresCompletionProjectionRepository(
        POSTGRES_DSN,
        presentation_preference_contract=contract,
        before_presentation_preference_save=before_save,
        after_presentation_preference_snapshot=after_snapshot,
    )
    return LearnerModelService(
        Source(),
        repository,
        Clock(),
        presentation_preference_repository=repository,
        presentation_preference_contract=contract,
        presentation_preference_seeds=StablePresentationPreferenceSeed(),
    )


def intent(
    key: str,
    revision: int,
    *,
    text_size: str = "larger",
    text_spacing: str = "increased",
    reading_width: str = "focused",
    motion: str = "reduce",
) -> PresentationPreferenceMutationIntent:
    return PresentationPreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=key,
        expected_revision=revision,
        mutation=PresentationPreferenceMutation(
            operation="replace_preferences",
            text_size=text_size,  # type: ignore[arg-type]
            text_spacing=text_spacing,  # type: ignore[arg-type]
            reading_width=reading_width,  # type: ignore[arg-type]
            motion=motion,  # type: ignore[arg-type]
        ),
    )


def reset_intent(key: str, revision: int) -> PresentationPreferenceMutationIntent:
    return PresentationPreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=key,
        expected_revision=revision,
        mutation=PresentationPreferenceMutation(operation="reset_profile"),
    )


def mutate(
    subject: LearnerModelService,
    command: PresentationPreferenceMutationIntent,
    learner_id: str = LEARNER_ID,
):
    return subject.mutate_presentation_preferences(
        MutatePresentationPreferencesRequest(learner_id, command)
    )


def counts() -> tuple[int, int, int]:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        return (
            connection.execute(
                "SELECT count(*) FROM "
                "learner_model.presentation_preference_profiles"
            ).fetchone()[0],
            connection.execute(
                "SELECT count(*) FROM "
                "learner_model.presentation_preference_changes"
            ).fetchone()[0],
            connection.execute(
                "SELECT count(*) FROM "
                "learner_model.presentation_preference_mutations"
            ).fetchone()[0],
        )


def test_default_is_virtual_and_mutation_and_replay_survive_restart() -> None:
    opened = service().open_presentation_preferences(
        OpenPresentationPreferencesRequest(LEARNER_ID)
    )
    assert opened.revision == 1
    assert (opened.text_size, opened.motion) == ("default", "system")
    assert counts() == (0, 0, 0)

    command = intent("display.first", 1)
    accepted = mutate(service(), command)
    reopened = service().open_presentation_preferences(
        OpenPresentationPreferencesRequest(LEARNER_ID)
    )
    replayed = mutate(service(), command)

    assert reopened == accepted == replayed
    assert counts() == (1, 1, 1)


def test_stale_changed_key_and_other_learner_write_nothing() -> None:
    mutate(service(), intent("display.first", 1))
    before = counts()

    with pytest.raises(LearnerModelError) as changed:
        mutate(
            service(),
            intent("display.first", 1, text_size="default"),
        )
    assert changed.value.code is LearnerModelErrorCode.IMMUTABLE_CONFLICT

    with pytest.raises(LearnerModelError) as stale:
        mutate(service(), intent("display.stale", 1, motion="system"))
    assert stale.value.code is LearnerModelErrorCode.STALE_REVISION

    other = service().open_presentation_preferences(
        OpenPresentationPreferencesRequest(OTHER_LEARNER_ID)
    )
    assert other.revision == 1
    assert other.profile_id != service().open_presentation_preferences(
        OpenPresentationPreferencesRequest(LEARNER_ID)
    ).profile_id
    assert counts() == before


def test_history_is_bounded_and_export_omits_browser_theme() -> None:
    subject = service()
    profile = mutate(subject, intent("display.001", 1))
    for index in range(2, 106):
        default_choices = index % 2 == 0
        profile = mutate(
            subject,
            intent(
                f"display.{index:03d}",
                profile.revision,
                text_size="default" if default_choices else "larger",
                text_spacing="default" if default_choices else "increased",
                reading_width="standard" if default_choices else "focused",
                motion="system" if default_choices else "reduce",
            ),
        )

    history = subject.read_presentation_preference_history(
        ReadPresentationPreferenceHistoryRequest(LEARNER_ID)
    )
    exported = subject.export_presentation_preferences(
        ExportPresentationPreferencesRequest(LEARNER_ID)
    )
    document = ContractPresentationPreferenceAdapter(SCHEMAS).export_document(
        exported
    )

    assert profile.revision == 106
    assert len(history.changes) == 100
    assert history.changes[0].revision == 7
    assert history.changes[-1].revision == 106
    assert "theme" not in document["profile"]
    assert all("theme" not in change for change in document["history"]["changes"])
    assert document["profile"] == ContractPresentationPreferenceAdapter(
        SCHEMAS
    ).profile_document(profile)


def test_mixed_preferences_reset_and_replay_remain_correlated() -> None:
    subject = service()
    mixed = mutate(
        subject,
        intent(
            "display.mixed",
            1,
            text_size="larger",
            text_spacing="default",
            reading_width="focused",
            motion="system",
        ),
    )
    command = reset_intent("display.reset", mixed.revision)
    reset = mutate(subject, command)
    replayed = mutate(service(), command)
    exported = subject.export_presentation_preferences(
        ExportPresentationPreferencesRequest(LEARNER_ID)
    )

    assert reset == replayed == exported.profile
    assert (reset.revision, reset.text_size, reset.motion) == (
        3,
        "default",
        "system",
    )
    assert exported.history.current_revision == reset.revision
    assert [change.operation for change in exported.history.changes] == [
        "replace_preferences",
        "reset_profile",
    ]
    assert counts() == (1, 2, 2)


def test_export_uses_one_coherent_snapshot_during_concurrent_mutation() -> None:
    first = mutate(
        service(),
        intent(
            "display.snapshot-first",
            1,
            text_size="larger",
            text_spacing="default",
            reading_width="focused",
            motion="system",
        ),
    )
    snapshot_loaded = Event()
    mutation_finished = Event()

    def pause_after_snapshot() -> None:
        snapshot_loaded.set()
        assert mutation_finished.wait(timeout=5)

    with ThreadPoolExecutor(max_workers=1) as executor:
        pending = executor.submit(
            service(after_snapshot=pause_after_snapshot).export_presentation_preferences,
            ExportPresentationPreferencesRequest(LEARNER_ID),
        )
        assert snapshot_loaded.wait(timeout=5)
        latest = mutate(
            service(),
            intent(
                "display.snapshot-second",
                first.revision,
                text_size="default",
                text_spacing="increased",
                reading_width="standard",
                motion="reduce",
            ),
        )
        mutation_finished.set()
        exported = pending.result(timeout=5)

    assert exported.profile.revision == first.revision
    assert exported.history.current_revision == first.revision
    assert exported.history.changes[-1].resulting_profile_digest == (
        exported.profile.profile_digest
    )
    assert latest.revision == first.revision + 1
    current = service().export_presentation_preferences(
        ExportPresentationPreferencesRequest(LEARNER_ID)
    )
    assert (
        current.profile.revision
        == current.history.current_revision
        == latest.revision
    )


def test_interruption_rolls_back_profile_change_and_replay() -> None:
    def fail() -> None:
        raise psycopg.OperationalError("private interruption")

    with pytest.raises(LearnerModelError) as failure:
        mutate(service(before_save=fail), intent("display.interrupted", 1))
    assert failure.value.code is LearnerModelErrorCode.UNAVAILABLE
    assert counts() == (0, 0, 0)


def test_retained_data_refuses_down_and_empty_down_reapplies() -> None:
    assert POSTGRES_DSN is not None
    down = (
        LEARNER_MIGRATIONS
        / "learner_model_0005_presentation_preferences.down.sql"
    ).read_text(encoding="utf-8")
    up = (
        LEARNER_MIGRATIONS
        / "learner_model_0005_presentation_preferences.up.sql"
    ).read_text(encoding="utf-8")
    mutate(service(), intent("display.retained", 1))
    with pytest.raises(psycopg.Error):
        with psycopg.connect(POSTGRES_DSN) as connection:
            connection.execute(down)
    assert counts() == (1, 1, 1)

    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            "TRUNCATE learner_model.presentation_preference_profiles CASCADE"
        )
        connection.execute(down)
        connection.execute(up)
    assert service().open_presentation_preferences(
        OpenPresentationPreferencesRequest(LEARNER_ID)
    ).revision == 1
