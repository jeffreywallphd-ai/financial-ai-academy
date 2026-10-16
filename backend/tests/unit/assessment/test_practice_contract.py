from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import pytest

from financial_ai_academy.modules.assessment.adapters.practice_contract import (
    ContractPracticeDefinitionAdapter,
)
from financial_ai_academy.modules.assessment.domain.practice import (
    MultipleSelectPracticeItem,
    NumericPracticeItem,
    PracticePresentationContext,
    SingleSelectPracticeItem,
)
from financial_ai_academy.modules.assessment.ports.practice_definition import (
    PracticeDefinitionFailure,
)


REPOSITORY = Path(__file__).resolve().parents[4]
SCHEMAS = REPOSITORY / "contracts/learning/assessment/practice/v1"
APPROVED = REPOSITORY / "contracts/compatibility/assessment-practice/v1/approved"


def adapter() -> ContractPracticeDefinitionAdapter:
    return ContractPracticeDefinitionAdapter(SCHEMAS)


def load(name: str) -> dict[str, object]:
    return json.loads((APPROVED / name).read_text(encoding="utf-8"))


def encoded(value: object) -> bytes:
    return json.dumps(value).encode("utf-8")


def refresh_digest(definition: dict[str, object]) -> None:
    definition["definition_digest"] = hashlib.sha256(
        json.dumps(
            definition["practice"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def test_parse_retains_all_private_item_types() -> None:
    definition = adapter().parse((APPROVED / "definition.json").read_bytes())
    assert definition.practice_id == "risk-return-practice"
    assert isinstance(definition.items[0], SingleSelectPracticeItem)
    assert isinstance(definition.items[1], MultipleSelectPracticeItem)
    assert isinstance(definition.items[2], NumericPracticeItem)
    assert definition.items[2].answer.value is not None


def test_production_parser_matches_non_ascii_digest_vector() -> None:
    document = copy.deepcopy(load("definition.json"))
    vector = json.loads(
        (
            REPOSITORY
            / "contracts/compatibility/assessment-practice/v1/vectors/non-ascii-definition-digest.json"
        ).read_text(encoding="utf-8")
    )
    for mutation in vector["mutations"]:
        current: object = document
        for part in mutation["path"][:-1]:
            current = current[part]  # type: ignore[index]
        current[mutation["path"][-1]] = mutation["value"]  # type: ignore[index]
    document["definition_digest"] = vector["definition_digest"]
    definition = adapter().parse(encoded(document))
    assert definition.title == "Practice café and 東京"
    assert definition.definition_digest == vector["definition_digest"]


def test_projection_matches_reviewed_transport_neutral_document() -> None:
    contract = adapter()
    definition = contract.parse((APPROVED / "definition.json").read_bytes())
    presentation = contract.project(
        definition,
        PracticePresentationContext(
            placement_id="risk-return-practice-placement",
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest="a" * 64,
        ),
    )
    assert contract.to_document(presentation) == load("presentation.json")


def test_projection_recursively_omits_answers_and_feedback() -> None:
    contract = adapter()
    definition = contract.parse((APPROVED / "definition.json").read_bytes())
    presentation = contract.project(
        definition,
        PracticePresentationContext("place", "package", "2.0.0", "a" * 64),
    )
    serialized = json.dumps(asdict(presentation))
    for private_name in (
        "answer",
        "correct_option_id",
        "correct_option_ids",
        "feedback",
    ):
        assert f'"{private_name}"' not in serialized


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (("practice", "practice_version"), "2.0.0", "assessment.practice.unsupported_version"),
        (("practice", "items", 0, "item_type"), "essay", "assessment.practice.unsupported_item_type"),
        (("practice", "items", 0, "item_type"), [], "assessment.practice.schema_invalid"),
        (("practice", "items", 2, "answer", "value"), "105.0", "assessment.practice.invalid_decimal"),
    ],
)
def test_parser_rejects_unsupported_or_ambiguous_meaning(
    path: tuple[str | int, ...], value: object, code: str
) -> None:
    document = copy.deepcopy(load("definition.json"))
    current: object = document
    for part in path[:-1]:
        current = current[part]  # type: ignore[index]
    current[path[-1]] = value  # type: ignore[index]
    refresh_digest(document)
    with pytest.raises(PracticeDefinitionFailure) as captured:
        adapter().parse(encoded(document))
    assert captured.value.code == code


def test_projection_allows_new_context_without_changing_practice_meaning() -> None:
    contract = adapter()
    definition = contract.parse((APPROVED / "definition.json").read_bytes())
    context = PracticePresentationContext(
        placement_id="another-placement",
        package_id="another-package",
        package_version="7.4.1",
        package_digest="d" * 64,
    )
    document = contract.to_document(contract.project(definition, context))
    assert document["placement_id"] == "another-placement"
    assert document["package_version"] == "7.4.1"
    assert document["definition_digest"] == definition.definition_digest
