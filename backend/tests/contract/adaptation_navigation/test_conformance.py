from __future__ import annotations

import copy
from datetime import datetime
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from financial_ai_academy.modules.adaptation.public import (
    ActivitySourceFact,
    ActivitySourceState,
    CompletionState,
    EvaluateNavigationStateRequest,
    evaluate_navigation_state,
    navigation_state_payload,
    source_facts_payload,
)
from financial_ai_academy.modules.curriculum.public import (
    curriculum_graph_from_mapping,
)

from curriculum_graph.runner import (
    CurriculumGraphContractValidator,
    graph_digest,
)

from .runner import (
    AdaptationNavigationContractValidator,
    ConformanceFailure,
    approved_pair,
    default_corpus_dir,
    default_graph_path,
    default_schema_dir,
    load_json,
    projection_digest,
    source_set_digest,
)


REPOSITORY = Path(__file__).resolve().parents[4]
CORPUS = default_corpus_dir()


def _domain_request(
    source: dict[str, Any],
    graph: dict[str, Any] | None = None,
) -> EvaluateNavigationStateRequest:
    domain_graph = curriculum_graph_from_mapping(
        graph or load_json(default_graph_path())
    )
    facts = tuple(
        ActivitySourceFact(
            activity_id=item["activity_id"],
            activity_source_state=ActivitySourceState(
                item["activity_source_state"]
            ),
            completion_state=CompletionState(item["completion_state"]),
            source_digest=item["source_digest"],
        )
        for item in source["activity_facts"]
    )
    return EvaluateNavigationStateRequest(
        graph=domain_graph,
        activity_facts=facts,
        evaluated_at=datetime.fromisoformat(
            source["evaluated_at"].replace("Z", "+00:00")
        ),
        policy_id=source["policy_id"],
        policy_version=source["policy_version"],
    )


def test_navigation_schemas_are_valid_draft_2020_12() -> None:
    schemas = list(default_schema_dir().glob("*.schema.json"))
    assert {path.name for path in schemas} == {
        "activity-launch.schema.json",
        "navigation-state.schema.json",
        "source-facts.schema.json",
    }
    for path in schemas:
        Draft202012Validator.check_schema(
            json.loads(path.read_text(encoding="utf-8"))
        )


def test_approved_pair_matches_contract_and_public_policy_exactly() -> None:
    source, expected = approved_pair()
    graph = load_json(default_graph_path())
    AdaptationNavigationContractValidator().validate_pair(source, expected, graph)
    request = _domain_request(source)
    assert source_facts_payload(request) == source
    assert navigation_state_payload(evaluate_navigation_state(request)) == expected


def test_digest_vectors_are_stable_and_independently_computed() -> None:
    source, projection = approved_pair()
    assert source_set_digest(source) == projection["source_set_digest"]
    assert projection_digest(projection) == projection["projection_digest"]


def test_source_fact_input_order_is_not_policy_authority() -> None:
    source, projection = copy.deepcopy(approved_pair())
    source["activity_facts"].reverse()
    AdaptationNavigationContractValidator().validate_pair(
        source,
        projection,
        load_json(default_graph_path()),
    )


def test_flexible_corpus_preserves_shape_and_state_independence() -> None:
    case = load_json(CORPUS / "flexible/case.json")
    graph = load_json(default_graph_path())
    activities_by_id = {
        item["activity_id"]: item for item in graph["activities"]
    }
    graph["activities"] = [
        activities_by_id[activity_id]
        for activity_id in case["activity_order"]
    ]
    if case["remove_presentation_order"]:
        graph.pop("presentation_order", None)
    graph["branches"].extend(case["additional_branches"])
    graph["relationships"].extend(case["additional_relationships"])
    graph["graph_digest"] = graph_digest(graph)
    CurriculumGraphContractValidator().validate_graph(graph)

    source, _ = approved_pair()
    source["graph_digest"] = graph["graph_digest"]
    source["activity_facts"] = case["activity_facts"]
    projection = navigation_state_payload(
        evaluate_navigation_state(_domain_request(source, graph))
    )
    AdaptationNavigationContractValidator().validate_pair(
        source,
        projection,
        graph,
    )

    expected = case["expected"]
    states = {
        item["activity_id"]: item for item in projection["activity_states"]
    }
    assert [
        item["activity_id"] for item in projection["activity_states"]
    ] == expected["state_order"]
    assert [
        activity_id
        for activity_id in expected["optional_locked_activity_ids"]
        if states[activity_id]["requirement"] == "optional"
        and states[activity_id]["eligibility"] == "locked"
    ] == expected["optional_locked_activity_ids"]
    multiple_unmet = states[expected["multiple_unmet_activity_id"]]
    assert [
        reason["references"]
        for reason in multiple_unmet["reasons"]
        if reason["code"] == "prerequisite_incomplete"
    ] == expected["multiple_unmet_references"]
    assert [
        item["activity_id"]
        for item in projection["activity_states"]
        if item["reasons"][-1]["code"] == "entry_activity"
    ] == expected["entry_activity_ids"]


@pytest.mark.parametrize(
    "mutation,expected_code",
    [
        ("missing", "adaptation_navigation.source_closure_invalid"),
        ("duplicate", "adaptation_navigation.source_closure_invalid"),
        ("unknown", "adaptation_navigation.source_closure_invalid"),
        ("bad_digest", "adaptation_navigation.schema_invalid"),
    ],
)
def test_source_closure_denials_are_bounded(
    mutation: str,
    expected_code: str,
) -> None:
    source, projection = copy.deepcopy(approved_pair())
    if mutation == "missing":
        source["activity_facts"].pop()
    elif mutation == "duplicate":
        source["activity_facts"][-1] = copy.deepcopy(
            source["activity_facts"][0]
        )
        source["activity_facts"][-1]["source_digest"] = "f" * 64
    elif mutation == "unknown":
        source["activity_facts"][-1]["activity_id"] = "activity-unknown"
    else:
        source["activity_facts"][0]["source_digest"] = "private-payload\npath"
    with pytest.raises(ConformanceFailure) as captured:
        AdaptationNavigationContractValidator().validate_pair(
            source,
            projection,
            load_json(default_graph_path()),
        )
    assert captured.value.diagnostic.code == expected_code
    assert len(captured.value.diagnostic.reference) <= 120
    assert "\n" not in captured.value.diagnostic.reference
    assert "private-payload" not in captured.value.diagnostic.message


def test_tampered_projection_digest_fails_closed() -> None:
    source, projection = copy.deepcopy(approved_pair())
    projection["activity_states"][0]["completion"] = "incomplete"
    with pytest.raises(ConformanceFailure) as digest_failure:
        AdaptationNavigationContractValidator().validate_pair(
            source,
            projection,
            load_json(default_graph_path()),
        )
    assert digest_failure.value.diagnostic.code == (
        "adaptation_navigation.projection_digest_mismatch"
    )



@pytest.mark.parametrize(
    "mutation",
    ["requirement", "eligibility", "reason_code", "direction", "reason_order"],
)
def test_recomputed_digest_cannot_hide_semantic_tampering(
    mutation: str,
) -> None:
    source, projection = copy.deepcopy(approved_pair())
    if mutation == "requirement":
        projection["activity_states"][2]["requirement"] = "required"
    elif mutation == "eligibility":
        projection["activity_states"][2]["eligibility"] = "locked"
    elif mutation == "reason_code":
        projection["activity_states"][2]["reasons"][0]["code"] = (
            "required_activity"
        )
    elif mutation == "direction":
        references = projection["activity_states"][1]["reasons"][1][
            "references"
        ]
        references[0], references[1] = references[1], references[0]
    else:
        projection["activity_states"][0]["reasons"].reverse()
    projection["projection_digest"] = projection_digest(projection)
    with pytest.raises(ConformanceFailure) as semantic_failure:
        AdaptationNavigationContractValidator().validate_pair(
            source,
            projection,
            load_json(default_graph_path()),
        )
    assert semantic_failure.value.diagnostic.code == (
        "adaptation_navigation.source_meaning_mismatch"
    )


def test_cli_emits_bounded_success_without_source_facts_or_paths() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.adaptation_navigation.runner"],
        cwd=REPOSITORY / "backend",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output == {
        "activity_count": 5,
        "curriculum_id": "investing-foundations",
        "curriculum_version": "1.0.0",
        "projection_digest": (
            "2804565cf538b0a2418a6ed9364be862c3999c75cfc02141d3119994beb4dd57"
        ),
        "valid": True,
    }
    combined = completed.stdout + completed.stderr
    assert "aaaaaaaaaaaaaaaa" not in combined
    assert str(REPOSITORY) not in combined
    assert "Traceback" not in combined


def test_cli_denial_is_sanitized(tmp_path: Path) -> None:
    corpus = tmp_path / "invalid-corpus"
    approved = corpus / "approved"
    approved.mkdir(parents=True)
    source, projection = approved_pair()
    source["schema_version"] = "2.0.0"
    (approved / "source-facts.json").write_text(
        json.dumps(source), encoding="utf-8"
    )
    (approved / "navigation-state.json").write_text(
        json.dumps(projection), encoding="utf-8"
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "tests.contract.adaptation_navigation.runner",
            "--corpus",
            str(corpus),
        ],
        cwd=REPOSITORY / "backend",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 1
    assert json.loads(completed.stdout) == {
        "diagnostic": {
            "code": "adaptation_navigation.unsupported_version",
            "message": "Adaptation navigation version is unsupported.",
            "reference": "schema_version",
        },
        "valid": False,
    }
    combined = completed.stdout + completed.stderr
    assert "2.0.0" not in combined
    assert str(corpus) not in combined
    assert "Traceback" not in combined
