from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from financial_ai_academy.modules.learner_model.adapters.assistance_preference_contract import (
    ContractAssistancePreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.ports.assistance_preference_contract import (
    AssistancePreferenceContractFailure,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = ROOT / "contracts" / "learning" / "learner-assistance-preferences" / "v1"
FIXTURE_DIR = ROOT / "contracts" / "compatibility" / "learner-assistance-preferences" / "v1"


@pytest.fixture
def adapter() -> ContractAssistancePreferenceAdapter:
    return ContractAssistancePreferenceAdapter(SCHEMA_DIR)


def _fixture(name: str) -> bytes:
    return (FIXTURE_DIR / name).read_bytes()


def test_all_v1_schemas_are_valid_draft_2020_12() -> None:
    names = {path.name for path in SCHEMA_DIR.glob("*.schema.json")}
    assert names == {
        "export.schema.json",
        "history.schema.json",
        "mutation-intent.schema.json",
        "profile.schema.json",
    }
    for path in SCHEMA_DIR.glob("*.schema.json"):
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


@pytest.mark.parametrize(
    "fixture_name", ["valid-default-profile.json", "valid-on-request-profile.json"]
)
def test_both_closed_profile_values_round_trip(
    adapter: ContractAssistancePreferenceAdapter, fixture_name: str
) -> None:
    profile = adapter.parse_profile(_fixture(fixture_name))
    assert adapter.profile_document(profile) == json.loads(_fixture(fixture_name))


def test_fixed_profile_digests_are_portable(
    adapter: ContractAssistancePreferenceAdapter,
) -> None:
    for name, expected in (
        ("valid-default-profile.json", "fb9f9277cd6ccdf34515cb13a2d4f5e87c4ecd6d9448d86b7135dc7cb6b79329"),
        ("valid-on-request-profile.json", "cabd8b0c017edda15593be28b69307a4ee5e1eeb5de770f8475d14ab7205c50e"),
    ):
        document = json.loads(_fixture(name))
        observed = document.pop("profile_digest")
        assert observed == expected == adapter.canonical_digest(document)


@pytest.mark.parametrize(
    "fixture_name", ["valid-replace-intent.json", "valid-reset-intent.json"]
)
def test_closed_mutation_variants_round_trip(
    adapter: ContractAssistancePreferenceAdapter, fixture_name: str
) -> None:
    intent = adapter.parse_mutation_intent(_fixture(fixture_name))
    assert adapter.mutation_intent_document(intent) == json.loads(_fixture(fixture_name))


def test_history_and_export_round_trip_and_correlate(
    adapter: ContractAssistancePreferenceAdapter,
) -> None:
    history = adapter.parse_history(_fixture("valid-history.json"))
    assert adapter.history_document(history) == json.loads(_fixture("valid-history.json"))
    exported = adapter.parse_export(_fixture("valid-export.json"))
    assert adapter.export_document(exported) == json.loads(_fixture("valid-export.json"))


def test_provider_field_fails_closed(
    adapter: ContractAssistancePreferenceAdapter,
) -> None:
    with pytest.raises(AssistancePreferenceContractFailure) as failure:
        adapter.parse_profile(_fixture("invalid-provider-field.json"))
    assert failure.value.code == "learner_assistance_preferences.invalid_shape"


@pytest.mark.parametrize(
    "forbidden",
    [
        "access_token", "assessment_score", "competency", "consent",
        "credential", "data_permission", "eligibility", "mastery", "model",
        "notification", "permission", "prompt", "provider", "recommendation",
        "storage_path", "suitability", "tool",
    ],
)
def test_family_contains_no_provider_private_or_authoritative_field(
    forbidden: str,
) -> None:
    documents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in SCHEMA_DIR.glob("*.schema.json")
    ]
    assert f'"{forbidden}"' not in json.dumps(documents, sort_keys=True)


@pytest.mark.parametrize("mode", ["always", "automatic", "provider_a", "enabled"])
def test_unknown_or_execution_implying_values_fail_closed(
    adapter: ContractAssistancePreferenceAdapter, mode: str
) -> None:
    document = json.loads(_fixture("valid-replace-intent.json"))
    document["mutation"]["assistance_mode"] = mode
    with pytest.raises(AssistancePreferenceContractFailure) as failure:
        adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))
    assert failure.value.code == "learner_assistance_preferences.invalid_shape"


def test_history_bound_accepts_newest_hundred_and_rejects_overflow(
    adapter: ContractAssistancePreferenceAdapter,
) -> None:
    document = json.loads(_fixture("valid-history.json"))
    template = document["changes"][0]
    document["current_revision"] = 101
    document["changes"] = []
    for revision in range(2, 102):
        change = deepcopy(template)
        change["revision"] = revision
        document["changes"].append(change)
    adapter.parse_history(json.dumps(document).encode("utf-8"))
    overflow = deepcopy(document)
    overflow["current_revision"] = 102
    extra = deepcopy(template)
    extra["revision"] = 102
    overflow["changes"].append(extra)
    with pytest.raises(AssistancePreferenceContractFailure) as failure:
        adapter.parse_history(json.dumps(overflow).encode("utf-8"))
    assert failure.value.code == "learner_assistance_preferences.history_limit"


def test_export_schema_closes_nested_profile_and_history() -> None:
    schema = json.loads((SCHEMA_DIR / "export.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    document = json.loads(_fixture("valid-export.json"))
    assert validator.is_valid(document)
    changed = deepcopy(document)
    changed["profile"]["provider"] = "example"
    changed["history"]["changes"][0]["previous_value"] = "off"
    assert not validator.is_valid(changed)
