from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from itertools import product

import pytest

from financial_ai_academy.modules.learner_model.domain.presentation_preferences import (
    InvalidPresentationPreference,
    PresentationPreferenceExport,
    PresentationPreferenceHistory,
    PresentationPreferenceMutation,
    PresentationPreferenceMutationIntent,
    apply_presentation_preference_mutation,
    default_presentation_preference_profile,
    validate_presentation_preference_export,
    validate_presentation_preference_history,
    validate_presentation_preference_profile,
)


START = datetime(2026, 10, 17, 21, 0, tzinfo=timezone.utc)


def _default():
    return default_presentation_preference_profile(
        profile_id="presentation.local-learner",
        learner_id="11111111-1111-4111-8111-111111111111",
        created_at=START,
    )


def _intent(revision: int, operation: str, **values: object):
    return PresentationPreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=f"intent.presentation-{revision}",
        expected_revision=revision,
        mutation=PresentationPreferenceMutation(operation=operation, **values),
    )


def test_default_profile_is_complete_and_digest_bound() -> None:
    profile = _default()
    assert (
        profile.text_size,
        profile.text_spacing,
        profile.reading_width,
        profile.motion,
    ) == ("default", "default", "standard", "system")
    assert profile.profile_digest == (
        "63c2c146622f55b11fdbc0e6b1fe5c8321798dfbeee41d4d83d4edeca3e02f77"
    )
    validate_presentation_preference_profile(profile)


@pytest.mark.parametrize(
    ("text_size", "text_spacing", "reading_width", "motion"),
    list(product(
        ("default", "larger"),
        ("default", "increased"),
        ("standard", "focused"),
        ("system", "reduce"),
    )),
)
def test_every_nondefault_valid_combination_replaces_as_one_complete_value(
    text_size: str,
    text_spacing: str,
    reading_width: str,
    motion: str,
) -> None:
    expected = (text_size, text_spacing, reading_width, motion)
    if expected == ("default", "default", "standard", "system"):
        return
    profile, change = apply_presentation_preference_mutation(
        _default(),
        _intent(
            1,
            "replace_preferences",
            text_size=text_size,
            text_spacing=text_spacing,
            reading_width=reading_width,
            motion=motion,
        ),
        occurred_at=START + timedelta(minutes=1),
    )
    assert (
        profile.text_size,
        profile.text_spacing,
        profile.reading_width,
        profile.motion,
    ) == expected
    assert change.operation == "replace_preferences"
    assert change.object_kind == "profile" and change.object_id is None


def test_reset_restores_safe_defaults_and_produces_noncontent_history() -> None:
    adjusted, _ = apply_presentation_preference_mutation(
        _default(),
        _intent(
            1,
            "replace_preferences",
            text_size="larger",
            text_spacing="increased",
            reading_width="focused",
            motion="reduce",
        ),
        occurred_at=START + timedelta(minutes=1),
    )
    reset, change = apply_presentation_preference_mutation(
        adjusted,
        _intent(2, "reset_profile"),
        occurred_at=START + timedelta(minutes=2),
    )
    assert (reset.text_size, reset.text_spacing, reset.reading_width, reset.motion) == (
        "default",
        "default",
        "standard",
        "system",
    )
    assert change.operation == "reset_profile"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("text_size", "smaller"),
        ("text_spacing", "tight"),
        ("reading_width", "unlimited"),
        ("motion", "force"),
    ],
)
def test_weaker_or_arbitrary_choices_fail_closed(field: str, value: str) -> None:
    values = {
        "text_size": "larger",
        "text_spacing": "increased",
        "reading_width": "focused",
        "motion": "reduce",
    }
    values[field] = value
    with pytest.raises(InvalidPresentationPreference) as failure:
        apply_presentation_preference_mutation(
            _default(),
            _intent(1, "replace_preferences", **values),
            occurred_at=START + timedelta(minutes=1),
        )
    assert failure.value.code == "learner_presentation_preferences.invalid_choice"


def test_stale_revision_no_change_and_digest_tampering_fail_closed() -> None:
    profile = _default()
    with pytest.raises(InvalidPresentationPreference) as stale:
        apply_presentation_preference_mutation(
            profile,
            _intent(2, "reset_profile"),
            occurred_at=START + timedelta(minutes=1),
        )
    assert stale.value.code == "learner_presentation_preferences.stale_revision"
    with pytest.raises(InvalidPresentationPreference) as unchanged:
        apply_presentation_preference_mutation(
            profile,
            _intent(1, "reset_profile"),
            occurred_at=START + timedelta(minutes=1),
        )
    assert unchanged.value.code == "learner_presentation_preferences.no_change"
    with pytest.raises(InvalidPresentationPreference) as digest:
        validate_presentation_preference_profile(replace(profile, revision=2))
    assert digest.value.code == "learner_presentation_preferences.digest_mismatch"


def test_history_and_export_require_exact_profile_correlation() -> None:
    profile, change = apply_presentation_preference_mutation(
        _default(),
        _intent(
            1,
            "replace_preferences",
            text_size="larger",
            text_spacing="increased",
            reading_width="focused",
            motion="reduce",
        ),
        occurred_at=START + timedelta(minutes=1),
    )
    history = PresentationPreferenceHistory(
        schema_version="1.0.0",
        profile_id=profile.profile_id,
        current_revision=profile.revision,
        changes=(change,),
    )
    validate_presentation_preference_history(history, profile)
    validate_presentation_preference_export(
        PresentationPreferenceExport(
            schema_version="1.0.0",
            purpose="Portable display preference review",
            limitations=("Explicit presentation choices only",),
            exported_at=START + timedelta(minutes=2),
            profile=profile,
            history=history,
        )
    )
    with pytest.raises(InvalidPresentationPreference) as mismatch:
        validate_presentation_preference_history(
            replace(history, current_revision=1), profile
        )
    assert mismatch.value.code == "learner_presentation_preferences.history_mismatch"
