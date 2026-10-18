from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from financial_ai_academy.modules.audit.adapters import (
    envelope_payload,
    lineage_view_payload,
)

from .runner import (
    ConformanceFailure,
    ProvenanceContractValidator,
    approved_records,
    default_corpus_dir,
    default_schema_dir,
)


CORPUS = default_corpus_dir()
REPOSITORY = Path(__file__).resolve().parents[4]


def _at(value: dict[str, Any], path: list[object]) -> Any:
    current: Any = value
    for part in path:
        current = current[part]
    return current


def _apply(value: dict[str, Any], operation: dict[str, Any]) -> None:
    current: Any = value
    path = operation["path"]
    for part in path[:-1]:
        current = current[part]
    key = path[-1]
    if operation["op"] == "set":
        current[key] = operation["value"]
    elif operation["op"] == "remove":
        del current[key]
    elif operation["op"] == "repeat":
        original = list(_at(value, path))
        current[key] = [copy.deepcopy(original[0]) for _ in range(operation["count"])]
    else:
        raise AssertionError(operation["op"])


def test_provenance_schemas_are_valid_draft_2020_12() -> None:
    schemas = list(default_schema_dir().glob("*.schema.json"))
    assert {path.name for path in schemas} == {
        "envelope.schema.json",
        "lineage-request.schema.json",
        "lineage-view.schema.json",
    }
    for path in schemas:
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_approved_envelopes_round_trip_without_domain_payloads() -> None:
    lesson, completion, _, _ = approved_records()
    validator = ProvenanceContractValidator()
    assert envelope_payload(validator.validate_envelope(lesson)) == lesson
    assert envelope_payload(validator.validate_envelope(completion)) == completion


def test_approved_views_and_canonicalization_vectors_are_stable() -> None:
    _, _, view, incomplete = approved_records()
    validator = ProvenanceContractValidator()
    admitted = validator.validate_lineage_view(view)
    admitted_incomplete = validator.validate_lineage_view(incomplete)
    vector = json.loads((CORPUS / "vectors/canonicalization.json").read_text(encoding="utf-8"))
    assert admitted.view_digest == vector["lineage_view_digest"]
    assert admitted_incomplete.view_digest == vector["incomplete_lineage_view_digest"]
    assert validator.validate_lineage_view(lineage_view_payload(admitted)) == admitted


def test_two_closed_lineage_requests_are_admitted_without_generic_selector() -> None:
    validator = ProvenanceContractValidator()
    validator.validate_lineage_request(
        {
            "schema_version": "1.0.0",
            "root_kind": "published_lesson",
            "package_id": "leçon-diversification-été",
            "package_version": "1.0.0",
            "package_digest": "a" * 64,
        }
    )
    validator.validate_lineage_request(
        {
            "schema_version": "1.0.0",
            "root_kind": "knowledge_check_completion",
            "placement_id": "placement-risk-return",
            "evidence_id": "evidence-check-1",
            "occurrence": 1,
        }
    )
    with pytest.raises(ConformanceFailure):
        validator.validate_lineage_request(
            {
                "schema_version": "1.0.0",
                "root_kind": "generic_resource",
                "owner_module": "audit",
                "resource_id": "private",
            }
        )

    for unsafe in ("placement\x00risk", "placement\u061crisk", "🙂placement"):
        with pytest.raises(ConformanceFailure):
            validator.validate_lineage_request(
                {
                    "schema_version": "1.0.0",
                    "root_kind": "knowledge_check_completion",
                    "placement_id": unsafe,
                    "evidence_id": "evidence-check-1",
                    "occurrence": 1,
                }
            )


def test_equivalent_input_order_projects_one_canonical_view() -> None:
    _, _, view, _ = approved_records()
    reordered = copy.deepcopy(view)
    reordered["nodes"].reverse()
    reordered["edges"].reverse()
    for node in reordered["nodes"]:
        node["envelope"]["sources"].reverse()
    validator = ProvenanceContractValidator()
    expected = lineage_view_payload(validator.validate_lineage_view(view))
    assert lineage_view_payload(validator.validate_lineage_view(reordered)) == expected


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_denial_corpus_fails_closed_with_bounded_codes(case: dict[str, Any]) -> None:
    lesson, completion, view, incomplete = approved_records()
    values = {
        "published_lesson_envelope": lesson,
        "knowledge_check_envelope": completion,
        "lineage_view": view,
        "incomplete_lineage_view": incomplete,
    }
    target = copy.deepcopy(values[case["target"]])
    for operation in case["ops"]:
        _apply(target, operation)
    validator = ProvenanceContractValidator()
    with pytest.raises(ConformanceFailure) as captured:
        if "envelope" in case["target"]:
            validator.validate_envelope(target)
        else:
            validator.validate_lineage_view(target)
    diagnostic = captured.value.diagnostic
    assert diagnostic.code == case["expected_code"]
    assert len(diagnostic.reference) <= 120
    assert "\n" not in diagnostic.reference
    assert "private-learner" not in diagnostic.message
    assert "https://" not in diagnostic.message


def test_cli_emits_bounded_json_without_payload_or_stack_trace() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.provenance.runner"],
        cwd=REPOSITORY / "backend",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["valid"] is True
    assert output["lesson_resource_id"] == "intro-risk-return"
    combined = completed.stdout + completed.stderr
    assert "private" not in combined
    assert "Traceback" not in combined
