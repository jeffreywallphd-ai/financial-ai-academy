from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.learner_model.adapters.presentation_preference_contract import (
    ContractPresentationPreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.ports.presentation_preference_contract import (
    PresentationPreferenceContractFailure,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = (
    ROOT / "contracts" / "learning" / "learner-presentation-preferences" / "v1"
)
NOW = datetime(2026, 10, 17, 21, 0, tzinfo=timezone.utc)


def _adapter() -> ContractPresentationPreferenceAdapter:
    return ContractPresentationPreferenceAdapter(SCHEMA_DIR)


def test_default_profile_uses_server_facts_and_round_trips() -> None:
    adapter = _adapter()
    profile = adapter.default_profile(
        profile_id="presentation.local-learner",
        learner_id="11111111-1111-4111-8111-111111111111",
        created_at=NOW,
    )
    document = adapter.profile_document(profile)
    assert document["profile_digest"] == (
        "63c2c146622f55b11fdbc0e6b1fe5c8321798dfbeee41d4d83d4edeca3e02f77"
    )
    assert adapter.parse_profile(json.dumps(document).encode("utf-8")) == profile


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        (b"{", "learner_presentation_preferences.invalid_json"),
        (b"[]", "learner_presentation_preferences.invalid_shape"),
    ],
)
def test_invalid_json_and_top_level_array_fail_safely(
    payload: bytes, code: str
) -> None:
    with pytest.raises(PresentationPreferenceContractFailure) as failure:
        _adapter().parse_profile(payload)
    assert failure.value.code == code


def test_invalid_server_identity_fails_safely() -> None:
    with pytest.raises(PresentationPreferenceContractFailure) as failure:
        _adapter().default_profile(
            profile_id="PRESENTATION",
            learner_id="caller-selected-learner",
            created_at=NOW,
        )
    assert failure.value.code == "learner_presentation_preferences.invalid_identity"
