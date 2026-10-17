from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

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
    LearnerPreferenceProfile,
    PreferenceChange,
    PreferenceHistory,
    PreferenceMutation,
    PreferenceMutationIntent,
)
from financial_ai_academy.modules.learner_model.ports.repositories import (
    LearnerPreferenceIdempotencyConflict,
    LearnerPreferenceRevisionConflict,
)
from financial_ai_academy.modules.learner_model.public import (
    ExportLearnerPreferencesRequest,
    LearnerModelError,
    LearnerModelErrorCode,
    MutateLearnerPreferencesRequest,
    OpenLearnerPreferencesRequest,
    ReadLearnerPreferenceHistoryRequest,
)


ROOT = Path(__file__).parents[4]
SCHEMAS = ROOT / "contracts" / "learning" / "learner-preferences" / "v1"
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
START = datetime(2026, 10, 17, 19, 0, tzinfo=timezone.utc)


class Source:
    pass


class Repository:
    def __init__(self) -> None:
        self.profile: LearnerPreferenceProfile | None = None
        self.changes: list[PreferenceChange] = []
        self.replays: dict[str, tuple[str, LearnerPreferenceProfile]] = {}
        self.save_count = 0
        self.commit_on_profile_read: (
            tuple[str, str, LearnerPreferenceProfile] | None
        ) = None

    def get_preferences(self, learner_id: str):
        assert learner_id == LEARNER_ID
        if self.commit_on_profile_read is not None:
            key, fingerprint, profile = self.commit_on_profile_read
            self.profile = profile
            self.replays[key] = (fingerprint, profile)
            self.commit_on_profile_read = None
        return self.profile

    def get_preference_history(self, learner_id: str):
        assert learner_id == LEARNER_ID
        if self.profile is None:
            return None
        return PreferenceHistory(
            schema_version="1.0.0",
            profile_id=self.profile.profile_id,
            current_revision=self.profile.revision,
            changes=tuple(self.changes[-100:]),
        )

    def get_preference_replay(self, learner_id: str, idempotency_key: str):
        assert learner_id == LEARNER_ID
        return self.replays.get(idempotency_key)

    def save_preferences_if_revision(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_revision: int,
        profile: LearnerPreferenceProfile,
        change: PreferenceChange,
    ) -> LearnerPreferenceProfile:
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


class Identifiers:
    def __init__(self) -> None:
        self.value = 0

    def new(self) -> str:
        self.value += 1
        return f"00000000-0000-4000-8000-{self.value:012d}"


def service(repository: Repository | None = None):
    values = repository or Repository()
    contract = ContractLearnerPreferenceAdapter(SCHEMAS)
    subject = LearnerModelService(
        Source(),
        values,
        Clock(),
        values,
        contract,
        Identifiers(),
        StablePreferenceSeed(),
    )
    return subject, values


def intent(revision: int, operation: str, **values: object):
    return PreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=f"intent.{revision}.{operation.replace('_', '-')}",
        expected_revision=revision,
        mutation=PreferenceMutation(operation=operation, **values),
    )


def test_empty_open_and_history_are_side_effect_free_and_stable() -> None:
    subject, repository = service()
    profile = subject.open_preferences(OpenLearnerPreferencesRequest(LEARNER_ID))
    reopened = subject.open_preferences(OpenLearnerPreferencesRequest(LEARNER_ID))
    history = subject.read_preference_history(
        ReadLearnerPreferenceHistoryRequest(LEARNER_ID)
    )

    assert profile == reopened
    assert profile.revision == 1
    assert profile.goals == profile.experience == profile.interests == ()
    assert history.current_revision == 1
    assert history.changes == ()
    assert repository.save_count == 0


def test_mutation_exact_retry_history_and_export_share_one_contract() -> None:
    subject, repository = service()
    command = intent(1, "create_goal", title="Learn evidence checks", detail=None)
    request = MutateLearnerPreferencesRequest(LEARNER_ID, command)

    accepted = subject.mutate_preferences(request)
    replayed = subject.mutate_preferences(request)
    history = subject.read_preference_history(
        ReadLearnerPreferenceHistoryRequest(LEARNER_ID)
    )
    exported = subject.export_preferences(
        ExportLearnerPreferencesRequest(LEARNER_ID)
    )

    assert accepted == replayed
    assert accepted.goals[0].goal_id.startswith("goal.")
    assert repository.save_count == 1
    assert history.changes[0].operation == "create_goal"
    assert exported.profile == accepted
    assert exported.history == history
    assert "competency" in exported.limitations[0]


def test_changed_key_and_stale_revision_write_nothing() -> None:
    subject, repository = service()
    first = intent(1, "create_interest", label="Market design")
    subject.mutate_preferences(MutateLearnerPreferencesRequest(LEARNER_ID, first))

    changed = PreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=first.idempotency_key,
        expected_revision=1,
        mutation=PreferenceMutation(operation="create_interest", label="Risk"),
    )
    with pytest.raises(LearnerModelError) as conflict:
        subject.mutate_preferences(
            MutateLearnerPreferencesRequest(LEARNER_ID, changed)
        )
    assert conflict.value.code is LearnerModelErrorCode.IMMUTABLE_CONFLICT

    stale = PreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key="intent.stale-create-interest",
        expected_revision=1,
        mutation=PreferenceMutation(operation="create_interest", label="Risk"),
    )
    with pytest.raises(LearnerModelError) as stale_error:
        subject.mutate_preferences(
            MutateLearnerPreferencesRequest(LEARNER_ID, stale)
        )
    assert stale_error.value.code is LearnerModelErrorCode.STALE_REVISION
    assert repository.save_count == 1


def test_replay_is_refreshed_when_winner_commits_between_application_reads() -> None:
    winner, winner_repository = service()
    accepted_command = intent(
        1, "create_interest", label="Market microstructure"
    )
    accepted = winner.mutate_preferences(
        MutateLearnerPreferencesRequest(LEARNER_ID, accepted_command)
    )
    fingerprint = winner_repository.replays[accepted_command.idempotency_key][0]

    exact_repository = Repository()
    exact_repository.commit_on_profile_read = (
        accepted_command.idempotency_key,
        fingerprint,
        accepted,
    )
    exact_subject, _ = service(exact_repository)
    replayed = exact_subject.mutate_preferences(
        MutateLearnerPreferencesRequest(LEARNER_ID, accepted_command)
    )
    assert replayed == accepted
    assert exact_repository.save_count == 0

    changed_repository = Repository()
    changed_repository.commit_on_profile_read = (
        accepted_command.idempotency_key,
        fingerprint,
        accepted,
    )
    changed_subject, _ = service(changed_repository)
    changed_command = PreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=accepted_command.idempotency_key,
        expected_revision=1,
        mutation=PreferenceMutation(
            operation="create_interest", label="Different meaning"
        ),
    )
    with pytest.raises(LearnerModelError) as changed:
        changed_subject.mutate_preferences(
            MutateLearnerPreferencesRequest(LEARNER_ID, changed_command)
        )
    assert changed.value.code is LearnerModelErrorCode.IMMUTABLE_CONFLICT
    assert changed_repository.save_count == 0

    stale_repository = Repository()
    stale_repository.commit_on_profile_read = (
        accepted_command.idempotency_key,
        fingerprint,
        accepted,
    )
    stale_subject, _ = service(stale_repository)
    stale_command = PreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key="intent.distinct-stale",
        expected_revision=1,
        mutation=PreferenceMutation(
            operation="create_interest", label="Different key"
        ),
    )
    with pytest.raises(LearnerModelError) as stale:
        stale_subject.mutate_preferences(
            MutateLearnerPreferencesRequest(LEARNER_ID, stale_command)
        )
    assert stale.value.code is LearnerModelErrorCode.STALE_REVISION
    assert stale_repository.save_count == 0


@pytest.mark.parametrize(
    "learner_id",
    ["caller-selected", "", "11111111-1111-1111-1111-not-a-uuid"],
)
def test_invalid_learner_context_fails_before_storage(learner_id: str) -> None:
    subject, repository = service()
    with pytest.raises(LearnerModelError) as failure:
        subject.open_preferences(OpenLearnerPreferencesRequest(learner_id))
    assert failure.value.code is LearnerModelErrorCode.INVALID_CONTEXT
    assert repository.save_count == 0


def test_unconfigured_preference_service_fails_safely() -> None:
    subject = LearnerModelService(Source(), Repository(), Clock())
    with pytest.raises(LearnerModelError) as failure:
        subject.open_preferences(OpenLearnerPreferencesRequest(LEARNER_ID))
    assert failure.value.code is LearnerModelErrorCode.UNAVAILABLE
