from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.project.adapters.project_contract import (
    ContractProjectAdapter,
)
from financial_ai_academy.modules.project.domain.project import (
    IndependentProjectOrigin,
    LearningProjectOrigin,
)
from financial_ai_academy.modules.project.ports.project_contract import (
    ProjectContractFailure,
)


REPOSITORY = Path(__file__).resolve().parents[4]
SCHEMAS = REPOSITORY / "contracts/learning/project/v1"
APPROVED = REPOSITORY / "contracts/compatibility/project-workspace/v1/approved"


def adapter() -> ContractProjectAdapter:
    return ContractProjectAdapter(SCHEMAS)


def load(name: str) -> dict[str, object]:
    return json.loads((APPROVED / name).read_text(encoding="utf-8"))


def encoded(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False).encode("utf-8")


def test_parser_returns_immutable_brief_values() -> None:
    contract = adapter()
    document = load("brief.json")
    brief = contract.parse_brief(encoded(document))
    document["brief"]["title"] = "Changed later"  # type: ignore[index]
    assert brief.title == "Review a sample portfolio"
    assert len(brief.milestones) == 2
    with pytest.raises(FrozenInstanceError):
        brief.title = "Cannot change"  # type: ignore[misc]


def test_both_origin_variants_round_trip_to_reviewed_shapes() -> None:
    contract = adapter()
    brief = contract.parse_brief((APPROVED / "brief.json").read_bytes())
    independent = contract.parse_intent(
        (APPROVED / "independent-intent.json").read_bytes()
    )
    learning = contract.parse_intent(
        (APPROVED / "learning-intent.json").read_bytes(),
        approved_brief=brief,
    )
    assert isinstance(independent.origin, IndependentProjectOrigin)
    assert isinstance(learning.origin, LearningProjectOrigin)
    assert contract.intent_document(independent) == load("independent-intent.json")
    assert contract.intent_document(learning) == load("learning-intent.json")


@pytest.mark.parametrize("name", ["independent-shell.json", "learning-shell.json"])
def test_shell_round_trip_preserves_server_owned_values(name: str) -> None:
    contract = adapter()
    shell = contract.parse_shell((APPROVED / name).read_bytes())
    assert shell.learner_id == "learner-local"
    assert shell.lifecycle == "active"
    assert shell.revision == 1
    assert contract.shell_document(shell) == load(name)


def test_learning_intent_fails_closed_without_exact_brief() -> None:
    contract = adapter()
    value = (APPROVED / "learning-intent.json").read_bytes()
    with pytest.raises(ProjectContractFailure) as missing:
        contract.parse_intent(value)
    assert missing.value.code == "project.contract.learning_brief_required"

    brief_document = copy.deepcopy(load("brief.json"))
    brief_document["brief"]["title"] = "Changed source"  # type: ignore[index]
    brief_document["brief_digest"] = "f" * 64
    with pytest.raises(ProjectContractFailure) as invalid:
        contract.parse_brief(encoded(brief_document))
    assert invalid.value.code == "project.contract.brief_digest_mismatch"


@pytest.mark.parametrize(
    ("name", "field"),
    [
        ("independent-intent.json", "learner_id"),
        ("independent-intent.json", "project_id"),
        ("independent-intent.json", "revision"),
        ("independent-shell.json", "storage_key"),
        ("independent-shell.json", "provider_payload"),
        ("independent-shell.json", "execution"),
        ("independent-shell.json", "score"),
    ],
)
def test_parser_rejects_client_authority_and_private_fields(
    name: str,
    field: str,
) -> None:
    contract = adapter()
    document = load(name)
    document[field] = "not allowed"
    operation = contract.parse_intent if name.endswith("intent.json") else contract.parse_shell
    with pytest.raises(ProjectContractFailure) as captured:
        operation(encoded(document))
    assert captured.value.code == "project.contract.schema_invalid"
    assert "not allowed" not in str(captured.value)


@pytest.mark.parametrize(
    ("title", "charter", "key"),
    [
        ("A", "One clear purpose.", "key-a"),
        ("Café study", "Compare examples in 東京.", "key-b"),
        ("A" * 120, "B" * 4000, "key-at-limits"),
    ],
)
def test_independent_intent_accepts_valid_text_without_fixture_assumptions(
    title: str,
    charter: str,
    key: str,
) -> None:
    contract = adapter()
    document = load("independent-intent.json")
    document.update(title=title, charter=charter, idempotency_key=key)
    parsed = contract.parse_intent(encoded(document))
    assert parsed.title == title
    assert parsed.charter == charter


def test_contract_adapter_is_side_effect_free() -> None:
    contract = adapter()
    first = contract.parse_shell((APPROVED / "learning-shell.json").read_bytes())
    second = contract.parse_shell((APPROVED / "learning-shell.json").read_bytes())
    assert first == second
    assert contract.shell_document(first) == contract.shell_document(second)
