from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from financial_ai_academy.modules.learner_model.domain.preferences import (
    MAX_GOALS,
    InvalidLearnerPreference,
    LearnerPreferenceProfile,
    PreferenceMutation,
    PreferenceMutationIntent,
    apply_preference_mutation,
    empty_preference_profile,
    validate_preference_profile,
)


START = datetime(2026, 10, 17, 18, 0, tzinfo=timezone.utc)


def _empty() -> LearnerPreferenceProfile:
    return empty_preference_profile(
        profile_id="profile.local-learner",
        learner_id="11111111-1111-4111-8111-111111111111",
        created_at=START,
    )


def _intent(revision: int, operation: str, **values: object) -> PreferenceMutationIntent:
    return PreferenceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=f"intent.{revision}.{operation.replace('_', '-')}",
        expected_revision=revision,
        mutation=PreferenceMutation(operation=operation, **values),
    )


def _apply(
    profile: LearnerPreferenceProfile,
    operation: str,
    *,
    minute: int,
    issued_id: str | None = None,
    **values: object,
):
    return apply_preference_mutation(
        profile,
        _intent(profile.revision, operation, **values),
        occurred_at=START + timedelta(minutes=minute),
        issued_id=issued_id,
    )


def test_explicit_goal_experience_and_interest_are_independent_ordered_values() -> None:
    profile, goal_change = _apply(
        _empty(),
        "create_goal",
        minute=1,
        issued_id="goal.research",
        title="Check claims against evidence",
        detail=None,
    )
    profile, experience_change = _apply(
        profile,
        "create_experience",
        minute=2,
        issued_id="experience.python",
        subject="Python",
        level="some_experience",
        detail="Class exercises",
    )
    profile, interest_change = _apply(
        profile,
        "create_interest",
        minute=3,
        issued_id="interest.market-design",
        label="Market design",
    )

    assert [item.goal_id for item in profile.goals] == ["goal.research"]
    assert [item.experience_id for item in profile.experience] == ["experience.python"]
    assert [item.interest_id for item in profile.interests] == ["interest.market-design"]
    assert [goal_change.object_kind, experience_change.object_kind, interest_change.object_kind] == ["goal", "experience", "interest"]
    assert profile.revision == 4
    validate_preference_profile(profile)


def test_update_archive_restore_and_remove_goal_preserve_other_sections() -> None:
    profile, _ = _apply(
        _empty(), "create_goal", minute=1, issued_id="goal.one", title="First", detail=None
    )
    profile, _ = _apply(
        profile, "create_interest", minute=2, issued_id="interest.one", label="Markets"
    )
    profile, _ = _apply(
        profile,
        "update_goal",
        minute=3,
        entry_id="goal.one",
        title="Revised",
        detail="More detail",
    )
    profile, _ = _apply(profile, "archive_goal", minute=4, entry_id="goal.one")
    assert profile.goals[0].archived is True
    profile, _ = _apply(profile, "restore_goal", minute=5, entry_id="goal.one")
    profile, change = _apply(profile, "remove_goal", minute=6, entry_id="goal.one")
    assert profile.goals == ()
    assert profile.interests[0].label == "Markets"
    assert change.object_id == "goal.one"


def test_reorder_requires_exact_unique_membership_and_changes_only_order() -> None:
    profile = _empty()
    for minute, identifier in enumerate(("interest.one", "interest.two"), start=1):
        profile, _ = _apply(
            profile,
            "create_interest",
            minute=minute,
            issued_id=identifier,
            label=identifier,
        )
    reordered, _ = _apply(
        profile,
        "reorder_interests",
        minute=3,
        ordered_ids=("interest.two", "interest.one"),
    )
    assert [item.interest_id for item in reordered.interests] == ["interest.two", "interest.one"]

    with pytest.raises(InvalidLearnerPreference) as failure:
        _apply(
            reordered,
            "reorder_interests",
            minute=4,
            ordered_ids=("interest.one",),
        )
    assert failure.value.code == "learner_preferences.invalid_order"


def test_reset_creates_empty_next_revision_without_changing_identity() -> None:
    profile, _ = _apply(
        _empty(), "create_interest", minute=1, issued_id="interest.one", label="Markets"
    )
    reset, change = _apply(profile, "reset_profile", minute=2)
    assert reset.profile_id == profile.profile_id
    assert reset.learner_id == profile.learner_id
    assert reset.revision == profile.revision + 1
    assert reset.goals == reset.experience == reset.interests == ()
    assert change.operation == "reset_profile"
    assert change.object_kind == "profile"


def test_stale_revision_duplicate_identity_and_naive_time_fail_closed() -> None:
    profile = _empty()
    stale = _intent(2, "create_interest", label="Markets")
    with pytest.raises(InvalidLearnerPreference) as failure:
        apply_preference_mutation(
            profile,
            stale,
            occurred_at=START + timedelta(minutes=1),
            issued_id="interest.one",
        )
    assert failure.value.code == "learner_preferences.stale_revision"

    profile, _ = _apply(
        profile, "create_interest", minute=1, issued_id="interest.one", label="Markets"
    )
    with pytest.raises(InvalidLearnerPreference) as failure:
        _apply(
            profile,
            "create_goal",
            minute=2,
            issued_id="interest.one",
            title="Goal",
            detail=None,
        )
    assert failure.value.code == "learner_preferences.duplicate_id"

    with pytest.raises(InvalidLearnerPreference) as failure:
        apply_preference_mutation(
            profile,
            _intent(profile.revision, "remove_interest", entry_id="interest.one"),
            occurred_at=datetime(2026, 10, 17, 18, 2),
        )
    assert failure.value.code == "learner_preferences.invalid_time"


@pytest.mark.parametrize(
    ("field", "value"),
    [("title", " leading"), ("title", "trailing "), ("title", "bad\u0001text")],
)
def test_learner_text_is_bounded_without_rewriting(field: str, value: str) -> None:
    with pytest.raises(InvalidLearnerPreference) as failure:
        _apply(
            _empty(),
            "create_goal",
            minute=1,
            issued_id="goal.one",
            title=value,
            detail=None,
        )
    assert failure.value.code == "learner_preferences.invalid_text"


def test_goal_quota_is_exact_and_not_fixture_count_rigid() -> None:
    profile = _empty()
    for index in range(MAX_GOALS):
        profile, _ = _apply(
            profile,
            "create_goal",
            minute=index + 1,
            issued_id=f"goal.{index:02d}",
            title=f"Goal {index}",
            detail=None,
        )
    assert len(profile.goals) == MAX_GOALS
    with pytest.raises(InvalidLearnerPreference) as failure:
        _apply(
            profile,
            "create_goal",
            minute=MAX_GOALS + 1,
            issued_id="goal.overflow",
            title="One too many",
            detail=None,
        )
    assert failure.value.code == "learner_preferences.goal_limit"


def test_profile_digest_detects_semantic_change() -> None:
    profile = _empty()
    with pytest.raises(InvalidLearnerPreference) as failure:
        validate_preference_profile(replace(profile, revision=2))
    assert failure.value.code == "learner_preferences.digest_mismatch"
