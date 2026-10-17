from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from financial_ai_academy.modules.personal_workspace.adapters.workspace_contract import (
    ContractPersonalWorkspaceAdapter,
)
from financial_ai_academy.modules.personal_workspace.ports.workspace_contract import (
    PersonalWorkspaceContractFailure,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = ROOT / "contracts" / "learning" / "personal-workspace" / "v1"
FIXTURE_DIR = ROOT / "contracts" / "compatibility" / "personal-workspace" / "v1"


@pytest.fixture
def adapter() -> ContractPersonalWorkspaceAdapter:
    return ContractPersonalWorkspaceAdapter(SCHEMA_DIR)


def test_all_v1_schemas_are_valid_draft_2020_12() -> None:
    names = {path.name for path in SCHEMA_DIR.glob("*.schema.json")}
    assert names == {
        "learning-reference.schema.json",
        "mutation-intent.schema.json",
        "workspace.schema.json",
    }
    for path in SCHEMA_DIR.glob("*.schema.json"):
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


@pytest.mark.parametrize(
    "fixture_name",
    ["valid-empty-workspace.json", "valid-populated-workspace.json"],
)
def test_workspace_compatibility_fixtures_are_canonical(
    adapter: ContractPersonalWorkspaceAdapter,
    fixture_name: str,
) -> None:
    fixture = (FIXTURE_DIR / fixture_name).read_bytes()
    workspace = adapter.parse_workspace(fixture)
    assert adapter.workspace_document(workspace) == json.loads(fixture)


def test_create_note_intent_is_portable(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    fixture = (FIXTURE_DIR / "valid-create-note-intent.json").read_bytes()
    intent = adapter.parse_mutation_intent(fixture)
    assert adapter.mutation_intent_document(intent) == json.loads(fixture)


@pytest.mark.parametrize(
    ("fixture_name", "code"),
    [
        ("invalid-dangling-collection.json", "personal_workspace.contract.dangling_member"),
        ("invalid-private-field.json", "personal_workspace.contract.invalid_shape"),
    ],
)
def test_invalid_compatibility_fixtures_fail_closed(
    adapter: ContractPersonalWorkspaceAdapter,
    fixture_name: str,
    code: str,
) -> None:
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_workspace((FIXTURE_DIR / fixture_name).read_bytes())
    assert failure.value.code == code


def test_contract_has_no_private_or_authoritative_learning_fields() -> None:
    forbidden = {
        "access_token",
        "answer_key",
        "grade",
        "mastery",
        "provider_payload",
        "recommendation_score",
        "storage_path",
    }
    documents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in SCHEMA_DIR.glob("*.schema.json")
    ]
    serialized = json.dumps(documents, sort_keys=True)
    for field in forbidden:
        assert f'"{field}"' not in serialized


def test_workspace_schema_rejects_more_than_declared_record_bound() -> None:
    schema = json.loads((SCHEMA_DIR / "workspace.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    fixture = json.loads((FIXTURE_DIR / "valid-populated-workspace.json").read_text())
    fixture["records"] = [fixture["records"][0]] * 201
    assert any(error.validator == "maxItems" for error in validator.iter_errors(fixture))
