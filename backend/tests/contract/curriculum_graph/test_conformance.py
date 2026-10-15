from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from financial_ai_academy.modules.curriculum.public import (
    curriculum_graph_digest,
    curriculum_graph_from_mapping,
)

from .runner import (
    ConformanceFailure,
    CurriculumGraphContractValidator,
    approved_graph,
    default_corpus_dir,
    default_schema_dir,
    graph_digest,
)


CORPUS = default_corpus_dir()
REPOSITORY = Path(__file__).resolve().parents[4]


def _set_at(value: dict[str, Any], path: list[object], replacement: object) -> None:
    current: Any = value
    for part in path[:-1]:
        current = current[part]
    current[path[-1]] = replacement


def _append_at(value: dict[str, Any], path: list[object], item: object) -> None:
    current: Any = value
    for part in path:
        current = current[part]
    current.append(item)


def _refresh_digest(value: dict[str, Any]) -> None:
    value["graph_digest"] = graph_digest(value)


def test_curriculum_graph_schema_is_valid_draft_2020_12() -> None:
    schemas = list(default_schema_dir().glob("*.schema.json"))
    assert {path.name for path in schemas} == {"graph.schema.json"}
    for path in schemas:
        Draft202012Validator.check_schema(
            json.loads(path.read_text(encoding="utf-8"))
        )


def test_approved_graph_validates_through_contract_and_domain() -> None:
    graph = approved_graph()
    CurriculumGraphContractValidator().validate_graph(graph)
    public_graph = curriculum_graph_from_mapping(graph)
    assert public_graph.curriculum_id == "investing-foundations"
    assert curriculum_graph_digest(public_graph) == graph["graph_digest"]


def test_digest_vector_is_stable_and_independently_computed() -> None:
    graph = approved_graph()
    vector = json.loads(
        (CORPUS / "vectors/graph-digest.json").read_text(encoding="utf-8")
    )
    assert graph_digest(graph) == vector["graph_digest"]
    assert graph["graph_digest"] == vector["graph_digest"]


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_denial_corpus_fails_closed_with_bounded_codes(
    case: dict[str, Any],
) -> None:
    graph = copy.deepcopy(approved_graph())
    if case["op"] == "set":
        _set_at(graph, case["path"], case["value"])
    else:
        _append_at(graph, case["path"], case["value"])
    validator = CurriculumGraphContractValidator()
    with pytest.raises(ConformanceFailure) as captured:
        validator.validate_graph(graph)
    diagnostic = captured.value.diagnostic
    assert diagnostic.code == case["expected_code"]
    assert len(diagnostic.reference) <= 120
    assert "\n" not in diagnostic.reference
    assert str(case["value"]) not in diagnostic.message


def test_optional_presentation_and_valid_graph_shape_remain_flexible() -> None:
    graph = copy.deepcopy(approved_graph())
    graph.pop("presentation_order")
    graph["objectives"].reverse()
    graph["activities"].reverse()
    graph["branches"].append(
        {
            "branch_id": "branch-reference",
            "title": "Reference material",
            "kind": "optional",
            "activity_ids": ["activity-terms-glossary"],
        }
    )
    graph["branches"].append(
        {
            "branch_id": "branch-reference-alternate",
            "title": "Alternate reference path",
            "kind": "optional",
            "activity_ids": ["activity-terms-glossary"],
        }
    )
    _refresh_digest(graph)
    CurriculumGraphContractValidator().validate_graph(graph)
    curriculum_graph_from_mapping(graph)


def test_graph_allows_multiple_entry_activities_and_unbranched_activity() -> None:
    graph = approved_graph()
    targets = {
        relationship["target_id"]
        for relationship in graph["relationships"]
        if relationship["kind"] == "activity_prerequisite"
    }
    entry_ids = {
        activity["activity_id"] for activity in graph["activities"]
    } - targets
    branch_members = {
        activity_id
        for branch in graph["branches"]
        for activity_id in branch["activity_ids"]
    }
    assert len(entry_ids) > 1
    assert "activity-terms-glossary" not in branch_members
    CurriculumGraphContractValidator().validate_graph(graph)


def test_cli_emits_bounded_json_without_source_payload_or_stack_trace() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.curriculum_graph.runner"],
        cwd=REPOSITORY / "backend",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["valid"] is True
    assert output["activity_count"] == 5
    combined = completed.stdout + completed.stderr
    assert "without personalized financial advice" not in combined
    assert str(REPOSITORY) not in combined
    assert "Traceback" not in combined
