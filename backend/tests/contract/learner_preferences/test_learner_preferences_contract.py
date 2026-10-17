from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from financial_ai_academy.modules.learner_model.adapters.preference_contract import (
    ContractLearnerPreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.ports.preference_contract import (
    LearnerPreferenceContractFailure,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = ROOT / "contracts" / "learning" / "learner-preferences" / "v1"
FIXTURE_DIR = (
    ROOT / "contracts" / "compatibility" / "learner-preferences" / "v1"
)


@pytest.fixture
def adapter() -> ContractLearnerPreferenceAdapter:
    return ContractLearnerPreferenceAdapter(SCHEMA_DIR)


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
    "fixture_name",
    ["valid-empty-profile.json", "valid-populated-profile.json"],
)
def test_profile_fixtures_round_trip_canonically(
    adapter: ContractLearnerPreferenceAdapter,
    fixture_name: str,
) -> None:
    profile = adapter.parse_profile(_fixture(fixture_name))
    assert adapter.profile_document(profile) == json.loads(_fixture(fixture_name))


def test_fixed_profile_digests_cover_empty_and_unicode_shapes(
    adapter: ContractLearnerPreferenceAdapter,
) -> None:
    empty = json.loads(_fixture("valid-empty-profile.json"))
    empty_digest = empty.pop("profile_digest")
    assert empty_digest == "d30eecfd7e88c2f219056d824362e61dc6447dc572816f06a91247d3b5e24bce"
    assert adapter.canonical_digest(empty) == empty_digest

    populated = json.loads(_fixture("valid-populated-profile.json"))
    populated["goals"][0]["detail"] = "Compare café data without normalizing text."
    observed = adapter.canonical_digest(
        {key: value for key, value in populated.items() if key != "profile_digest"}
    )
    decomposed = deepcopy(populated)
    decomposed["goals"][0]["detail"] = "Compare cafe\u0301 data without normalizing text."
    changed = adapter.canonical_digest(
        {key: value for key, value in decomposed.items() if key != "profile_digest"}
    )
    assert observed != changed


def test_intent_history_and_export_fixtures_round_trip(
    adapter: ContractLearnerPreferenceAdapter,
) -> None:
    intent = adapter.parse_mutation_intent(_fixture("valid-create-goal-intent.json"))
    assert adapter.mutation_intent_document(intent) == json.loads(
        _fixture("valid-create-goal-intent.json")
    )

    history = adapter.parse_history(_fixture("valid-history.json"))
    assert adapter.history_document(history) == json.loads(_fixture("valid-history.json"))

    exported = adapter.parse_export(_fixture("valid-export.json"))
    assert adapter.export_document(exported) == json.loads(_fixture("valid-export.json"))


def test_private_or_authoritative_field_fails_closed(
    adapter: ContractLearnerPreferenceAdapter,
) -> None:
    with pytest.raises(LearnerPreferenceContractFailure) as failure:
        adapter.parse_profile(_fixture("invalid-private-field.json"))
    assert failure.value.code == "learner_preferences.invalid_shape"


@pytest.mark.parametrize(
    "forbidden",
    [
        "access_token",
        "answer_key",
        "assessment_score",
        "competency",
        "consent",
        "eligibility",
        "mastery",
        "permission",
        "provider_payload",
        "recommendation_score",
        "storage_path",
        "suitability",
    ],
)
def test_contract_family_contains_no_inferred_evidence_or_private_field(
    forbidden: str,
) -> None:
    documents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in SCHEMA_DIR.glob("*.schema.json")
    ]
    assert f'"{forbidden}"' not in json.dumps(documents, sort_keys=True)


@pytest.mark.parametrize(
    ("operation", "payload"),
    [
        ("update_goal", {"entry_id": "goal.one", "title": "A revised goal", "detail": None}),
        ("archive_goal", {"entry_id": "goal.one"}),
        ("restore_goal", {"entry_id": "goal.one"}),
        ("remove_goal", {"entry_id": "goal.one"}),
        ("reorder_goals", {"ordered_ids": ["goal.two", "goal.one"]}),
        ("create_experience", {"subject": "Python", "level": "new", "detail": None}),
        ("update_experience", {"entry_id": "experience.one", "subject": "Python", "level": "experienced", "detail": "Coursework"}),
        ("remove_experience", {"entry_id": "experience.one"}),
        ("reorder_experience", {"ordered_ids": ["experience.two", "experience.one"]}),
        ("create_interest", {"label": "Market structure"}),
        ("rename_interest", {"entry_id": "interest.one", "label": "Market design"}),
        ("remove_interest", {"entry_id": "interest.one"}),
        ("reorder_interests", {"ordered_ids": ["interest.two", "interest.one"]}),
        ("reset_profile", {}),
    ],
)
def test_closed_mutation_variants_are_portable(
    adapter: ContractLearnerPreferenceAdapter,
    operation: str,
    payload: dict[str, object],
) -> None:
    document = {
        "schema_version": "1.0.0",
        "idempotency_key": f"intent.{operation.replace('_', '-')}",
        "expected_revision": 4,
        "mutation": {"operation": operation, **payload},
    }
    parsed = adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))
    assert adapter.mutation_intent_document(parsed) == document


@pytest.mark.parametrize(
    "change",
    [
        {"mutation": {"operation": "infer_interests"}},
        {"mutation": {"operation": "create_interest", "label": "Markets", "source": "clickstream"}},
        {"learner_id": "11111111-1111-4111-8111-111111111111"},
    ],
)
def test_mutation_rejects_unknown_or_client_authoritative_fields(
    adapter: ContractLearnerPreferenceAdapter,
    change: dict[str, object],
) -> None:
    document = json.loads(_fixture("valid-create-goal-intent.json"))
    document.update(change)
    with pytest.raises(LearnerPreferenceContractFailure) as failure:
        adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))
    assert failure.value.code == "learner_preferences.invalid_shape"


def test_profile_schema_enforces_independent_section_bounds() -> None:
    schema = json.loads((SCHEMA_DIR / "profile.schema.json").read_text(encoding="utf-8"))
    fixture = json.loads(_fixture("valid-populated-profile.json"))
    for field, count in (("goals", 21), ("experience", 21), ("interests", 51)):
        changed = deepcopy(fixture)
        changed[field] = [changed[field][0]] * count
        errors = list(Draft202012Validator(schema).iter_errors(changed))
        assert any(error.validator == "maxItems" for error in errors)


def test_export_rejects_history_that_does_not_match_profile(
    adapter: ContractLearnerPreferenceAdapter,
) -> None:
    document = json.loads(_fixture("valid-export.json"))
    document["history"]["current_revision"] = 3
    document["history"]["changes"].pop()
    with pytest.raises(LearnerPreferenceContractFailure) as failure:
        adapter.parse_export(json.dumps(document).encode("utf-8"))
    assert failure.value.code == "learner_preferences.history_mismatch"
