from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from financial_ai_academy.modules.learner_model.domain.assistance_preferences import (
    AssistancePreferenceExport,
    AssistancePreferenceHistory,
    AssistancePreferenceMutation,
    AssistancePreferenceMutationIntent,
    InvalidAssistancePreference,
    apply_assistance_preference_mutation,
    default_assistance_preference_profile,
    validate_assistance_preference_export,
    validate_assistance_preference_history,
    validate_assistance_preference_profile,
)


START = datetime(2026, 10, 17, 23, 0, tzinfo=timezone.utc)


def _default(
    profile_id: str = "assistance.local-learner",
    learner_id: str = "11111111-1111-4111-8111-111111111111",
    started_at: datetime = START,
):
    return default_assistance_preference_profile(
        profile_id=profile_id,
        learner_id=learner_id,
        created_at=started_at,
    )


def _intent(revision: int, operation: str, mode: str | None = None):
    return AssistancePreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=f"intent.assistance-{revision}",
        expected_revision=revision,
        mutation=AssistancePreferenceMutation(
            operation=operation,
            assistance_mode=mode,
        ),
    )


def test_default_is_off_and_digest_bound() -> None:
    profile = _default()
    assert profile.assistance_mode == "off"
    assert profile.profile_digest == (
        "fb9f9277cd6ccdf34515cb13a2d4f5e87c4ecd6d9448d86b7135dc7cb6b79329"
    )
    validate_assistance_preference_profile(profile)


def test_replace_and_reset_are_complete_reversible_mutations() -> None:
    enabled, change = apply_assistance_preference_mutation(
        _default(),
        _intent(1, "replace_preferences", "on_request"),
        occurred_at=START + timedelta(minutes=1),
    )
    assert enabled.assistance_mode == "on_request"
    assert enabled.profile_digest == (
        "cabd8b0c017edda15593be28b69307a4ee5e1eeb5de770f8475d14ab7205c50e"
    )
    assert change.operation == "replace_preferences"
    reset, reset_change = apply_assistance_preference_mutation(
        enabled,
        _intent(2, "reset_profile"),
        occurred_at=START + timedelta(minutes=2),
    )
    assert reset.assistance_mode == "off"
    assert reset_change.operation == "reset_profile"


@pytest.mark.parametrize("mode", ["always", "automatic", "provider_a", "enabled"])
def test_unknown_or_authoritative_modes_fail_closed(mode: str) -> None:
    with pytest.raises(InvalidAssistancePreference) as failure:
        apply_assistance_preference_mutation(
            _default(),
            _intent(1, "replace_preferences", mode),
            occurred_at=START + timedelta(minutes=1),
        )
    assert failure.value.code == "learner_assistance_preferences.invalid_choice"


@pytest.mark.parametrize(
    ("profile_id", "learner_id", "started_at", "mutations"),
    [
        (
            "assistance.alpha-01",
            "22222222-2222-4222-8222-222222222222",
            datetime(2027, 2, 3, 8, 15, tzinfo=timezone.utc),
            5,
        ),
        (
            "assistance.beta-99",
            "33333333-3333-4333-8333-333333333333",
            datetime(2028, 7, 9, 18, 45, tzinfo=timezone.utc),
            11,
        ),
    ],
)
def test_generated_facts_and_higher_revisions_are_not_rigid(
    profile_id: str,
    learner_id: str,
    started_at: datetime,
    mutations: int,
) -> None:
    profile = _default(profile_id, learner_id, started_at)
    for offset in range(1, mutations + 1):
        mode = "on_request" if offset % 2 else "off"
        profile, _ = apply_assistance_preference_mutation(
            profile,
            _intent(profile.revision, "replace_preferences", mode),
            occurred_at=started_at + timedelta(minutes=offset * 3),
        )
    assert profile.profile_id == profile_id
    assert profile.learner_id == learner_id
    assert profile.revision == mutations + 1
    validate_assistance_preference_profile(profile)


def test_stale_no_change_and_digest_tampering_fail_closed() -> None:
    profile = _default()
    for intent, code in (
        (_intent(2, "replace_preferences", "on_request"), "stale_revision"),
        (_intent(1, "reset_profile"), "no_change"),
    ):
        with pytest.raises(InvalidAssistancePreference) as failure:
            apply_assistance_preference_mutation(
                profile,
                intent,
                occurred_at=START + timedelta(minutes=1),
            )
        assert failure.value.code == f"learner_assistance_preferences.{code}"
    with pytest.raises(InvalidAssistancePreference) as digest:
        validate_assistance_preference_profile(replace(profile, revision=2))
    assert digest.value.code == "learner_assistance_preferences.digest_mismatch"


def test_history_and_export_require_exact_profile_correlation() -> None:
    profile, change = apply_assistance_preference_mutation(
        _default(),
        _intent(1, "replace_preferences", "on_request"),
        occurred_at=START + timedelta(minutes=1),
    )
    history = AssistancePreferenceHistory(
        schema_version="1.0.0",
        profile_id=profile.profile_id,
        current_revision=profile.revision,
        changes=(change,),
    )
    validate_assistance_preference_history(history, profile)
    validate_assistance_preference_export(
        AssistancePreferenceExport(
            schema_version="1.0.0",
            purpose="Portable AI-help preference review",
            limitations=("No provider or data permission is granted.",),
            exported_at=START + timedelta(minutes=2),
            profile=profile,
            history=history,
        )
    )
    with pytest.raises(InvalidAssistancePreference) as mismatch:
        validate_assistance_preference_history(
            replace(history, current_revision=1), profile
        )
    assert mismatch.value.code == "learner_assistance_preferences.history_mismatch"
