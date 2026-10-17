from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.learner_model.adapters.assistance_preference_contract import (
    ContractAssistancePreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.ports.assistance_preference_contract import (
    AssistancePreferenceContractFailure,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = ROOT / "contracts" / "learning" / "learner-assistance-preferences" / "v1"
NOW = datetime(2026, 10, 17, 23, 0, tzinfo=timezone.utc)


def _adapter() -> ContractAssistancePreferenceAdapter:
    return ContractAssistancePreferenceAdapter(SCHEMA_DIR)


def test_default_profile_uses_server_facts_and_round_trips() -> None:
    adapter = _adapter()
    profile = adapter.default_profile(
        profile_id="assistance.local-learner",
        learner_id="11111111-1111-4111-8111-111111111111",
        created_at=NOW,
    )
    document = adapter.profile_document(profile)
    assert document["profile_digest"] == (
        "fb9f9277cd6ccdf34515cb13a2d4f5e87c4ecd6d9448d86b7135dc7cb6b79329"
    )
    assert adapter.parse_profile(json.dumps(document).encode("utf-8")) == profile


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        (b"{", "learner_assistance_preferences.invalid_json"),
        (b"[]", "learner_assistance_preferences.invalid_shape"),
    ],
)
def test_invalid_json_and_top_level_array_fail_safely(
    payload: bytes, code: str
) -> None:
    with pytest.raises(AssistancePreferenceContractFailure) as failure:
        _adapter().parse_profile(payload)
    assert failure.value.code == code


def test_invalid_server_identity_fails_safely() -> None:
    with pytest.raises(AssistancePreferenceContractFailure) as failure:
        _adapter().default_profile(
            profile_id="ASSISTANCE",
            learner_id="caller-selected-learner",
            created_at=NOW,
        )
    assert failure.value.code == "learner_assistance_preferences.invalid_identity"
