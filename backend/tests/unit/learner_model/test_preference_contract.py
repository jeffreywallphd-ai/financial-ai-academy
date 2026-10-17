from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.learner_model.adapters.preference_contract import (
    ContractLearnerPreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.ports.preference_contract import (
    LearnerPreferenceContractFailure,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = ROOT / "contracts" / "learning" / "learner-preferences" / "v1"
NOW = datetime(2026, 10, 17, 18, 0, tzinfo=timezone.utc)


def _adapter() -> ContractLearnerPreferenceAdapter:
    return ContractLearnerPreferenceAdapter(SCHEMA_DIR)


def test_empty_profile_uses_server_facts_and_has_stable_digest() -> None:
    adapter = _adapter()
    profile = adapter.empty_profile(
        profile_id="profile.local-learner",
        learner_id="11111111-1111-4111-8111-111111111111",
        created_at=NOW,
    )
    assert profile.revision == 1
    assert profile.profile_digest == "d30eecfd7e88c2f219056d824362e61dc6447dc572816f06a91247d3b5e24bce"
    assert adapter.parse_profile(
        json.dumps(adapter.profile_document(profile)).encode("utf-8")
    ) == profile


@pytest.mark.parametrize(
    ("profile_id", "learner_id"),
    [
        ("profile.ok", "caller-selected-learner"),
        ("PROFILE", "11111111-1111-4111-8111-111111111111"),
    ],
)
def test_empty_profile_rejects_invalid_server_identity(
    profile_id: str,
    learner_id: str,
) -> None:
    with pytest.raises(LearnerPreferenceContractFailure):
        _adapter().empty_profile(
            profile_id=profile_id,
            learner_id=learner_id,
            created_at=NOW,
        )


def test_invalid_json_and_top_level_array_fail_safely() -> None:
    adapter = _adapter()
    for payload, code in ((b"{", "learner_preferences.invalid_json"), (b"[]", "learner_preferences.invalid_shape")):
        with pytest.raises(LearnerPreferenceContractFailure) as failure:
            adapter.parse_profile(payload)
        assert failure.value.code == code
