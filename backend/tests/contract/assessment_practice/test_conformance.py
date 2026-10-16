from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from .runner import (
    PracticeConformanceFailure,
    PracticeContractValidator,
    approved_pair,
    canonical_practice_bytes,
    corpus_dir,
    definition_digest,
    schema_dir,
)


CORPUS = corpus_dir()


def _set_at(value: dict[str, Any], path: list[object], replacement: object) -> None:
    current: Any = value
    for part in path[:-1]:
        current = current[part]
    current[path[-1]] = replacement


def _mutated(case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    definition, presentation = map(copy.deepcopy, approved_pair())
    target = definition if case["target"] == "definition" else presentation
    _set_at(target, case["path"], case["value"])
    if case.get("refresh_definition_digest"):
        definition["definition_digest"] = definition_digest(definition)
    return definition, presentation


def test_schemas_are_valid_draft_2020_12() -> None:
    paths = sorted(schema_dir().glob("*.schema.json"))
    assert [path.name for path in paths] == [
        "definition.schema.json",
        "presentation.schema.json",
    ]
    for path in paths:
        Draft202012Validator.check_schema(
            json.loads(path.read_text(encoding="utf-8"))
        )


def test_approved_definition_and_safe_projection_validate() -> None:
    definition, presentation = approved_pair()
    validator = PracticeContractValidator()
    validator.validate_presentation(definition, presentation)
    assert [item["item_type"] for item in presentation["items"]] == [
        "single_select",
        "multiple_select",
        "numeric_entry",
    ]
    assert validator.project(
        definition,
        placement_id=presentation["placement_id"],
        package_id=presentation["package_id"],
        package_version=presentation["package_version"],
        package_digest=presentation["package_digest"],
    ) == presentation


def test_definition_digest_vector_fixes_private_meaning() -> None:
    definition, _ = approved_pair()
    vector = json.loads(
        (CORPUS / "vectors/definition-digest.json").read_text(encoding="utf-8")
    )
    assert definition_digest(definition) == vector["definition_digest"]
    assert definition["definition_digest"] == vector["definition_digest"]
    reloaded = json.loads(json.dumps(definition["practice"], sort_keys=False))
    assert canonical_practice_bytes(definition["practice"]) == (
        canonical_practice_bytes(reloaded)
    )


def test_presentation_recursively_excludes_private_fields() -> None:
    _, presentation = approved_pair()
    serialized = json.dumps(presentation, sort_keys=True)
    for private_name in (
        "correct_option_id",
        "correct_option_ids",
        '"answer"',
        '"feedback"',
    ):
        assert private_name not in serialized


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_denial_corpus_fails_closed(case: dict[str, Any]) -> None:
    definition, presentation = _mutated(case)
    with pytest.raises(PracticeConformanceFailure) as captured:
        PracticeContractValidator().validate_presentation(definition, presentation)
    assert captured.value.code == case["expected_code"]
    assert len(captured.value.reference) <= 120
    assert "\n" not in captured.value.reference
    assert str(case.get("value", "sentinel")) not in captured.value.message


def test_compatible_counts_order_and_range_rule_are_not_fixture_locked() -> None:
    definition, presentation = map(copy.deepcopy, approved_pair())
    practice = definition["practice"]
    practice["source_references"].append(
        {
            "resource_id": "additional-source",
            "resource_version": "1.0.0",
            "resource_digest": "e" * 64,
            "title": "Additional approved source",
        }
    )
    practice["items"].reverse()
    practice["items"][2]["options"].reverse()
    numeric = practice["items"][0]
    numeric["answer"] = {
        "mode": "inclusive_range",
        "lower": "104.50",
        "upper": "105.50",
    }
    definition["definition_digest"] = definition_digest(definition)
    validator = PracticeContractValidator()
    projection = validator.project(
        definition,
        placement_id=presentation["placement_id"],
        package_id=presentation["package_id"],
        package_version=presentation["package_version"],
        package_digest=presentation["package_digest"],
    )
    validator.validate_presentation(definition, projection)
    assert len(projection["source_references"]) == 2
    assert projection["items"][0]["item_type"] == "numeric_entry"


def test_cli_emits_bounded_output_without_private_answers() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.assessment_practice.runner"],
        cwd=Path(__file__).resolve().parents[3],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["valid"] is True
    assert output["item_types"] == [
        "single_select",
        "multiple_select",
        "numeric_entry",
    ]
    combined = completed.stdout + completed.stderr
    assert "105.00" not in combined
    assert "Traceback" not in combined
