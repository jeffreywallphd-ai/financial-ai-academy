from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.learner_model.adapters.assistance_preference_contract import (
    ContractAssistancePreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.adapters.system import (
    StableAssistancePreferenceSeed,
)
from financial_ai_academy.modules.learner_model.application.service import (
    LearnerModelService,
)
from financial_ai_academy.modules.learner_model.domain.assistance_preferences import (
    AssistancePreferenceChange,
    AssistancePreferenceHistory,
    AssistancePreferenceMutation,
    AssistancePreferenceMutationIntent,
    AssistancePreferenceProfile,
)
from financial_ai_academy.modules.learner_model.ports.repositories import (
    LearnerPreferenceIdempotencyConflict,
    LearnerPreferenceRevisionConflict,
)
from financial_ai_academy.modules.learner_model.public import (
    ExportAssistancePreferencesRequest,
    LearnerModelError,
    LearnerModelErrorCode,
    MutateAssistancePreferencesRequest,
    OpenAssistancePreferencesRequest,
    ReadAssistancePreferenceHistoryRequest,
)


ROOT = Path(__file__).parents[4]
SCHEMAS = (
    ROOT / "contracts" / "learning" / "learner-assistance-preferences" / "v1"
)
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
START = datetime(2026, 10, 17, 23, 0, tzinfo=timezone.utc)


class Source:
    pass


class Repository:
    def __init__(self) -> None:
        self.profile: AssistancePreferenceProfile | None = None
        self.changes: list[AssistancePreferenceChange] = []
        self.replays: dict[str, tuple[str, AssistancePreferenceProfile]] = {}
        self.save_count = 0
        self.snapshot_count = 0
        self.commit_on_profile_read: (
            tuple[str, str, AssistancePreferenceProfile] | None
        ) = None

    def get_assistance_preferences(self, learner_id: str):
        assert learner_id == LEARNER_ID
        if self.commit_on_profile_read is not None:
            key, fingerprint, profile = self.commit_on_profile_read
            self.profile = profile
            self.replays[key] = (fingerprint, profile)
            self.commit_on_profile_read = None
        return self.profile

    def get_assistance_preference_history(self, learner_id: str):
        raise AssertionError("service reads must use one coherent snapshot")

    def get_assistance_preference_snapshot(self, learner_id: str):
        assert learner_id == LEARNER_ID
        self.snapshot_count += 1
        if self.profile is None:
            return None
        return (
            self.profile,
            AssistancePreferenceHistory(
                schema_version="1.0.0",
                profile_id=self.profile.profile_id,
                current_revision=self.profile.revision,
                changes=tuple(self.changes[-100:]),
            ),
        )

    def get_assistance_preference_replay(
        self, learner_id: str, idempotency_key: str
    ):
        assert learner_id == LEARNER_ID
        return self.replays.get(idempotency_key)

    def save_assistance_preferences_if_revision(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_revision: int,
        profile: AssistancePreferenceProfile,
        change: AssistancePreferenceChange,
    ) -> AssistancePreferenceProfile:
        replay = self.replays.get(idempotency_key)
        if replay is not None:
            if replay[0] != request_fingerprint:
                raise LearnerPreferenceIdempotencyConflict()
            return replay[1]
        current_revision = self.profile.revision if self.profile else 1
        if current_revision != expected_revision:
            raise LearnerPreferenceRevisionConflict()
        self.profile = profile
        self.changes.append(change)
        self.changes = self.changes[-100:]
        self.replays[idempotency_key] = (request_fingerprint, profile)
        self.save_count += 1
        return profile


class Clock:
    def __init__(self) -> None:
        self.minute = 0

    def now(self) -> datetime:
        self.minute += 1
        return START + timedelta(minutes=self.minute)


def service(repository: Repository | None = None):
    values = repository or Repository()
    contract = ContractAssistancePreferenceAdapter(SCHEMAS)
    subject = LearnerModelService(
        Source(),
        values,
        Clock(),
        assistance_preference_repository=values,
        assistance_preference_contract=contract,
        assistance_preference_seeds=StableAssistancePreferenceSeed(),
    )
    return subject, values


def intent(
    revision: int, *, mode: str, key: str | None = None
) -> AssistancePreferenceMutationIntent:
    return AssistancePreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=key or f"intent.assistance-{revision}",
        expected_revision=revision,
        mutation=AssistancePreferenceMutation(
            operation="replace_preferences",
            assistance_mode=mode,  # type: ignore[arg-type]
        ),
    )


def reset_intent(revision: int) -> AssistancePreferenceMutationIntent:
    return AssistancePreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key="intent.assistance-reset",
        expected_revision=revision,
        mutation=AssistancePreferenceMutation(operation="reset_profile"),
    )


def test_default_open_and_history_are_side_effect_free_and_stable() -> None:
    subject, repository = service()
    profile = subject.open_assistance_preferences(
        OpenAssistancePreferencesRequest(LEARNER_ID)
    )
    reopened = subject.open_assistance_preferences(
        OpenAssistancePreferencesRequest(LEARNER_ID)
    )
    history = subject.read_assistance_preference_history(
        ReadAssistancePreferenceHistoryRequest(LEARNER_ID)
    )
    assert profile == reopened
    assert (profile.revision, profile.assistance_mode) == (1, "off")
    assert history.current_revision == 1 and history.changes == ()
    assert repository.save_count == 0


def test_replace_retry_reset_history_and_export_share_one_contract() -> None:
    subject, repository = service()
    command = intent(1, mode="on_request")
    request = MutateAssistancePreferencesRequest(LEARNER_ID, command)
    accepted = subject.mutate_assistance_preferences(request)
    replayed = subject.mutate_assistance_preferences(request)
    reset = subject.mutate_assistance_preferences(
        MutateAssistancePreferencesRequest(
            LEARNER_ID, reset_intent(accepted.revision)
        )
    )
    exported = subject.export_assistance_preferences(
        ExportAssistancePreferencesRequest(LEARNER_ID)
    )

    assert accepted == replayed
    assert (reset.revision, reset.assistance_mode) == (3, "off")
    assert repository.save_count == 2
    assert exported.profile == reset
    assert [change.operation for change in exported.history.changes] == [
        "replace_preferences",
        "reset_profile",
    ]
    assert "does not enable or call" in exported.limitations[0]
    assert repository.snapshot_count == 1


def test_changed_key_and_stale_revision_write_nothing() -> None:
    subject, repository = service()
    first = intent(1, mode="on_request")
    subject.mutate_assistance_preferences(
        MutateAssistancePreferencesRequest(LEARNER_ID, first)
    )
    changed = intent(1, mode="off", key=first.idempotency_key)
    with pytest.raises(LearnerModelError) as conflict:
        subject.mutate_assistance_preferences(
            MutateAssistancePreferencesRequest(LEARNER_ID, changed)
        )
    assert conflict.value.code is LearnerModelErrorCode.IMMUTABLE_CONFLICT
    with pytest.raises(LearnerModelError) as stale:
        subject.mutate_assistance_preferences(
            MutateAssistancePreferencesRequest(
                LEARNER_ID,
                intent(1, mode="off", key="intent.assistance-stale"),
            )
        )
    assert stale.value.code is LearnerModelErrorCode.STALE_REVISION
    assert repository.save_count == 1


def test_replay_is_refreshed_when_winner_commits_between_reads() -> None:
    winner, winner_repository = service()
    command = intent(1, mode="on_request", key="intent.assistance-race")
    accepted = winner.mutate_assistance_preferences(
        MutateAssistancePreferencesRequest(LEARNER_ID, command)
    )
    fingerprint = winner_repository.replays[command.idempotency_key][0]

    exact_repository = Repository()
    exact_repository.commit_on_profile_read = (
        command.idempotency_key,
        fingerprint,
        accepted,
    )
    exact, _ = service(exact_repository)
    assert exact.mutate_assistance_preferences(
        MutateAssistancePreferencesRequest(LEARNER_ID, command)
    ) == accepted
    assert exact_repository.save_count == 0

    stale_repository = Repository()
    stale_repository.commit_on_profile_read = (
        command.idempotency_key,
        fingerprint,
        accepted,
    )
    stale, _ = service(stale_repository)
    with pytest.raises(LearnerModelError) as captured:
        stale.mutate_assistance_preferences(
            MutateAssistancePreferencesRequest(
                LEARNER_ID,
                intent(1, mode="off", key="intent.assistance-loser"),
            )
        )
    assert captured.value.code is LearnerModelErrorCode.STALE_REVISION
    assert stale_repository.save_count == 0


def test_history_retains_newest_one_hundred_varied_revisions() -> None:
    subject, repository = service()
    mode = "on_request"
    for revision in range(1, 106):
        subject.mutate_assistance_preferences(
            MutateAssistancePreferencesRequest(
                LEARNER_ID, intent(revision, mode=mode)
            )
        )
        mode = "off" if mode == "on_request" else "on_request"
    history = subject.read_assistance_preference_history(
        ReadAssistancePreferenceHistoryRequest(LEARNER_ID)
    )
    assert repository.save_count == 105
    assert len(history.changes) == 100
    assert history.changes[0].revision == 7
    assert history.changes[-1].revision == 106


def test_invalid_context_and_unconfigured_boundary_fail_safely() -> None:
    subject, repository = service()
    with pytest.raises(LearnerModelError) as invalid:
        subject.open_assistance_preferences(
            OpenAssistancePreferencesRequest("caller-selected")
        )
    assert invalid.value.code is LearnerModelErrorCode.INVALID_CONTEXT
    assert repository.save_count == 0

    unavailable = LearnerModelService(Source(), repository, Clock())
    with pytest.raises(LearnerModelError) as failure:
        unavailable.open_assistance_preferences(
            OpenAssistancePreferencesRequest(LEARNER_ID)
        )
    assert failure.value.code is LearnerModelErrorCode.UNAVAILABLE
