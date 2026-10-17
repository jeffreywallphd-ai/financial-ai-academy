from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.learner_model.adapters.presentation_preference_contract import (
    ContractPresentationPreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.adapters.system import (
    StablePresentationPreferenceSeed,
)
from financial_ai_academy.modules.learner_model.application.service import (
    LearnerModelService,
)
from financial_ai_academy.modules.learner_model.domain.presentation_preferences import (
    PresentationPreferenceChange,
    PresentationPreferenceHistory,
    PresentationPreferenceMutation,
    PresentationPreferenceMutationIntent,
    PresentationPreferenceProfile,
)
from financial_ai_academy.modules.learner_model.ports.repositories import (
    LearnerPreferenceIdempotencyConflict,
    LearnerPreferenceRevisionConflict,
)
from financial_ai_academy.modules.learner_model.public import (
    ExportPresentationPreferencesRequest,
    LearnerModelError,
    LearnerModelErrorCode,
    MutatePresentationPreferencesRequest,
    OpenPresentationPreferencesRequest,
    ReadPresentationPreferenceHistoryRequest,
)


ROOT = Path(__file__).parents[4]
SCHEMAS = (
    ROOT / "contracts" / "learning" / "learner-presentation-preferences" / "v1"
)
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
START = datetime(2026, 10, 17, 22, 0, tzinfo=timezone.utc)


class Source:
    pass


class Repository:
    def __init__(self) -> None:
        self.profile: PresentationPreferenceProfile | None = None
        self.changes: list[PresentationPreferenceChange] = []
        self.replays: dict[str, tuple[str, PresentationPreferenceProfile]] = {}
        self.save_count = 0
        self.snapshot_count = 0
        self.commit_on_profile_read: (
            tuple[str, str, PresentationPreferenceProfile] | None
        ) = None

    def get_presentation_preferences(self, learner_id: str):
        assert learner_id == LEARNER_ID
        if self.commit_on_profile_read is not None:
            key, fingerprint, profile = self.commit_on_profile_read
            self.profile = profile
            self.replays[key] = (fingerprint, profile)
            self.commit_on_profile_read = None
        return self.profile

    def get_presentation_preference_history(self, learner_id: str):
        raise AssertionError("service reads must use one coherent snapshot")

    def get_presentation_preference_snapshot(self, learner_id: str):
        assert learner_id == LEARNER_ID
        self.snapshot_count += 1
        if self.profile is None:
            return None
        return (
            self.profile,
            PresentationPreferenceHistory(
                schema_version="1.0.0",
                profile_id=self.profile.profile_id,
                current_revision=self.profile.revision,
                changes=tuple(self.changes[-100:]),
            ),
        )

    def get_presentation_preference_replay(
        self, learner_id: str, idempotency_key: str
    ):
        assert learner_id == LEARNER_ID
        return self.replays.get(idempotency_key)

    def save_presentation_preferences_if_revision(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_revision: int,
        profile: PresentationPreferenceProfile,
        change: PresentationPreferenceChange,
    ) -> PresentationPreferenceProfile:
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
    contract = ContractPresentationPreferenceAdapter(SCHEMAS)
    subject = LearnerModelService(
        Source(),
        values,
        Clock(),
        presentation_preference_repository=values,
        presentation_preference_contract=contract,
        presentation_preference_seeds=StablePresentationPreferenceSeed(),
    )
    return subject, values


def intent(revision: int, *, adjusted: bool, key: str | None = None):
    return PresentationPreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=key or f"intent.presentation-{revision}",
        expected_revision=revision,
        mutation=PresentationPreferenceMutation(
            operation="replace_preferences",
            text_size="larger" if adjusted else "default",
            text_spacing="increased" if adjusted else "default",
            reading_width="focused" if adjusted else "standard",
            motion="reduce" if adjusted else "system",
        ),
    )


def reset_intent(revision: int, *, key: str = "intent.presentation-reset"):
    return PresentationPreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=key,
        expected_revision=revision,
        mutation=PresentationPreferenceMutation(operation="reset_profile"),
    )


def test_default_open_and_history_are_side_effect_free_and_stable() -> None:
    subject, repository = service()
    profile = subject.open_presentation_preferences(
        OpenPresentationPreferencesRequest(LEARNER_ID)
    )
    reopened = subject.open_presentation_preferences(
        OpenPresentationPreferencesRequest(LEARNER_ID)
    )
    history = subject.read_presentation_preference_history(
        ReadPresentationPreferenceHistoryRequest(LEARNER_ID)
    )
    assert profile == reopened
    assert profile.revision == 1
    assert (profile.text_size, profile.motion) == ("default", "system")
    assert history.current_revision == 1 and history.changes == ()
    assert repository.save_count == 0


def test_replace_retry_history_and_export_share_one_contract() -> None:
    subject, repository = service()
    command = intent(1, adjusted=True)
    request = MutatePresentationPreferencesRequest(LEARNER_ID, command)
    accepted = subject.mutate_presentation_preferences(request)
    replayed = subject.mutate_presentation_preferences(request)
    history = subject.read_presentation_preference_history(
        ReadPresentationPreferenceHistoryRequest(LEARNER_ID)
    )
    exported = subject.export_presentation_preferences(
        ExportPresentationPreferencesRequest(LEARNER_ID)
    )
    assert accepted == replayed
    assert repository.save_count == 1
    assert history.changes[0].operation == "replace_preferences"
    assert exported.profile == accepted and exported.history == history
    assert "theme" in exported.limitations[1].lower()
    assert repository.snapshot_count == 2


def test_reset_and_mixed_choices_remain_correlated_in_one_snapshot() -> None:
    subject, repository = service()
    mixed = PresentationPreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key="intent.presentation-mixed",
        expected_revision=1,
        mutation=PresentationPreferenceMutation(
            operation="replace_preferences",
            text_size="larger",
            text_spacing="default",
            reading_width="focused",
            motion="system",
        ),
    )
    adjusted = subject.mutate_presentation_preferences(
        MutatePresentationPreferencesRequest(LEARNER_ID, mixed)
    )
    reset = subject.mutate_presentation_preferences(
        MutatePresentationPreferencesRequest(
            LEARNER_ID, reset_intent(adjusted.revision)
        )
    )
    exported = subject.export_presentation_preferences(
        ExportPresentationPreferencesRequest(LEARNER_ID)
    )

    assert (reset.revision, reset.text_size, reset.motion) == (
        3,
        "default",
        "system",
    )
    assert exported.profile == reset
    assert exported.history.current_revision == reset.revision
    assert [change.operation for change in exported.history.changes] == [
        "replace_preferences",
        "reset_profile",
    ]
    assert repository.snapshot_count == 1


def test_changed_key_and_stale_revision_write_nothing() -> None:
    subject, repository = service()
    first = intent(1, adjusted=True)
    subject.mutate_presentation_preferences(
        MutatePresentationPreferencesRequest(LEARNER_ID, first)
    )
    changed = intent(1, adjusted=False, key=first.idempotency_key)
    with pytest.raises(LearnerModelError) as conflict:
        subject.mutate_presentation_preferences(
            MutatePresentationPreferencesRequest(LEARNER_ID, changed)
        )
    assert conflict.value.code is LearnerModelErrorCode.IMMUTABLE_CONFLICT
    with pytest.raises(LearnerModelError) as stale:
        subject.mutate_presentation_preferences(
            MutatePresentationPreferencesRequest(
                LEARNER_ID, intent(1, adjusted=False, key="intent.stale-display")
            )
        )
    assert stale.value.code is LearnerModelErrorCode.STALE_REVISION
    assert repository.save_count == 1


def test_replay_is_refreshed_when_winner_commits_between_application_reads() -> None:
    winner, winner_repository = service()
    accepted_command = intent(1, adjusted=True, key="intent.presentation-race")
    accepted = winner.mutate_presentation_preferences(
        MutatePresentationPreferencesRequest(LEARNER_ID, accepted_command)
    )
    fingerprint = winner_repository.replays[accepted_command.idempotency_key][0]

    exact_repository = Repository()
    exact_repository.commit_on_profile_read = (
        accepted_command.idempotency_key,
        fingerprint,
        accepted,
    )
    exact_subject, _ = service(exact_repository)
    replayed = exact_subject.mutate_presentation_preferences(
        MutatePresentationPreferencesRequest(LEARNER_ID, accepted_command)
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
    with pytest.raises(LearnerModelError) as changed:
        changed_subject.mutate_presentation_preferences(
            MutatePresentationPreferencesRequest(
                LEARNER_ID,
                intent(
                    1,
                    adjusted=False,
                    key=accepted_command.idempotency_key,
                ),
            )
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
    with pytest.raises(LearnerModelError) as stale:
        stale_subject.mutate_presentation_preferences(
            MutatePresentationPreferencesRequest(
                LEARNER_ID,
                intent(1, adjusted=False, key="intent.presentation-stale"),
            )
        )
    assert stale.value.code is LearnerModelErrorCode.STALE_REVISION
    assert stale_repository.save_count == 0


def test_history_retains_newest_one_hundred_varied_revisions() -> None:
    subject, repository = service()
    for revision in range(1, 106):
        subject.mutate_presentation_preferences(
            MutatePresentationPreferencesRequest(
                LEARNER_ID, intent(revision, adjusted=revision % 2 == 1)
            )
        )
    history = subject.read_presentation_preference_history(
        ReadPresentationPreferenceHistoryRequest(LEARNER_ID)
    )
    assert repository.save_count == 105
    assert len(history.changes) == 100
    assert history.changes[0].revision == 7
    assert history.changes[-1].revision == 106


def test_invalid_context_and_unconfigured_boundary_fail_safely() -> None:
    subject, repository = service()
    with pytest.raises(LearnerModelError) as invalid:
        subject.open_presentation_preferences(
            OpenPresentationPreferencesRequest("caller-selected")
        )
    assert invalid.value.code is LearnerModelErrorCode.INVALID_CONTEXT
    assert repository.save_count == 0

    unavailable = LearnerModelService(Source(), repository, Clock())
    with pytest.raises(LearnerModelError) as failure:
        unavailable.open_presentation_preferences(
            OpenPresentationPreferencesRequest(LEARNER_ID)
        )
    assert failure.value.code is LearnerModelErrorCode.UNAVAILABLE
