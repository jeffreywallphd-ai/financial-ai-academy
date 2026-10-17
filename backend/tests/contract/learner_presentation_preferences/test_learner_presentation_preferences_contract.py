from __future__ import annotations

from copy import deepcopy
import json
from itertools import product
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

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
FIXTURE_DIR = (
    ROOT
    / "contracts"
    / "compatibility"
    / "learner-presentation-preferences"
    / "v1"
)


@pytest.fixture
def adapter() -> ContractPresentationPreferenceAdapter:
    return ContractPresentationPreferenceAdapter(SCHEMA_DIR)


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
    "fixture_name", ["valid-default-profile.json", "valid-adjusted-profile.json"]
)
def test_profile_fixtures_round_trip_canonically(
    adapter: ContractPresentationPreferenceAdapter, fixture_name: str
) -> None:
    profile = adapter.parse_profile(_fixture(fixture_name))
    assert adapter.profile_document(profile) == json.loads(_fixture(fixture_name))


def test_fixed_profile_digests_are_portable(
    adapter: ContractPresentationPreferenceAdapter,
) -> None:
    for name, expected in (
        (
            "valid-default-profile.json",
            "63c2c146622f55b11fdbc0e6b1fe5c8321798dfbeee41d4d83d4edeca3e02f77",
        ),
        (
            "valid-adjusted-profile.json",
            "56ab301cb622e58c5cc57ced7885fc625ea02f747612fe1d0febaf47bd0d572d",
        ),
    ):
        document = json.loads(_fixture(name))
        observed = document.pop("profile_digest")
        assert observed == expected == adapter.canonical_digest(document)


@pytest.mark.parametrize(
    "fixture_name", ["valid-replace-intent.json", "valid-reset-intent.json"]
)
def test_closed_mutation_variants_round_trip(
    adapter: ContractPresentationPreferenceAdapter, fixture_name: str
) -> None:
    intent = adapter.parse_mutation_intent(_fixture(fixture_name))
    assert adapter.mutation_intent_document(intent) == json.loads(_fixture(fixture_name))


def test_history_and_export_round_trip_and_correlate(
    adapter: ContractPresentationPreferenceAdapter,
) -> None:
    history = adapter.parse_history(_fixture("valid-history.json"))
    assert adapter.history_document(history) == json.loads(_fixture("valid-history.json"))
    exported = adapter.parse_export(_fixture("valid-export.json"))
    assert adapter.export_document(exported) == json.loads(_fixture("valid-export.json"))


def test_private_browser_theme_field_fails_closed(
    adapter: ContractPresentationPreferenceAdapter,
) -> None:
    with pytest.raises(PresentationPreferenceContractFailure) as failure:
        adapter.parse_profile(_fixture("invalid-private-field.json"))
    assert failure.value.code == "learner_presentation_preferences.invalid_shape"


@pytest.mark.parametrize(
    "forbidden",
    [
        "access_token",
        "assessment_score",
        "competency",
        "consent",
        "diagnosis",
        "eligibility",
        "mastery",
        "permission",
        "provider_payload",
        "recommendation_score",
        "storage_path",
        "suitability",
        "theme",
    ],
)
def test_contract_family_contains_no_private_inferred_or_authoritative_field(
    forbidden: str,
) -> None:
    documents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in SCHEMA_DIR.glob("*.schema.json")
    ]
    assert f'"{forbidden}"' not in json.dumps(documents, sort_keys=True)


@pytest.mark.parametrize(
    ("text_size", "text_spacing", "reading_width", "motion"),
    list(product(
        ("default", "larger"),
        ("default", "increased"),
        ("standard", "focused"),
        ("system", "reduce"),
    )),
)
def test_every_valid_combination_is_contract_portable(
    adapter: ContractPresentationPreferenceAdapter,
    text_size: str,
    text_spacing: str,
    reading_width: str,
    motion: str,
) -> None:
    document = json.loads(_fixture("valid-replace-intent.json"))
    document["mutation"].update(
        text_size=text_size,
        text_spacing=text_spacing,
        reading_width=reading_width,
        motion=motion,
    )
    parsed = adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))
    assert adapter.mutation_intent_document(parsed) == document


@pytest.mark.parametrize(
    "change",
    [
        {"theme": "dark"},
        {"text_size": "smaller"},
        {"motion": "force"},
        {"diagnosis": "low vision"},
        {"css": "body{font-size:200%}"},
    ],
)
def test_arbitrary_or_weaker_replacement_fields_fail_closed(
    adapter: ContractPresentationPreferenceAdapter, change: dict[str, object]
) -> None:
    document = json.loads(_fixture("valid-replace-intent.json"))
    document["mutation"].update(change)
    with pytest.raises(PresentationPreferenceContractFailure) as failure:
        adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))
    assert failure.value.code == "learner_presentation_preferences.invalid_shape"


def test_incomplete_replacement_and_changed_history_fail_closed(
    adapter: ContractPresentationPreferenceAdapter,
) -> None:
    intent = json.loads(_fixture("valid-replace-intent.json"))
    intent["mutation"].pop("reading_width")
    with pytest.raises(PresentationPreferenceContractFailure):
        adapter.parse_mutation_intent(json.dumps(intent).encode("utf-8"))

    exported = json.loads(_fixture("valid-export.json"))
    exported["history"]["current_revision"] = 1
    exported["history"]["changes"] = []
    with pytest.raises(PresentationPreferenceContractFailure) as failure:
        adapter.parse_export(json.dumps(exported).encode("utf-8"))
    assert failure.value.code == "learner_presentation_preferences.history_mismatch"


def test_export_schema_closes_nested_profile_and_history() -> None:
    schema = json.loads((SCHEMA_DIR / "export.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    document = json.loads(_fixture("valid-export.json"))
    assert validator.is_valid(document)
    changed = deepcopy(document)
    changed["profile"]["theme"] = "light"
    changed["history"]["changes"][0]["previous_values"] = {"motion": "system"}
    assert not validator.is_valid(changed)
