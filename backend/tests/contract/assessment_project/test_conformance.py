from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from financial_ai_academy.modules.assessment.adapters.project_submission_contract import (
    ContractProjectSubmissionAdapter,
)
from financial_ai_academy.modules.assessment.ports.project_submission import (
    ProjectSubmissionContractFailure,
)
from .runner import (
    CORPUS,
    SCHEMAS,
    approved_chain,
    load,
)


def _set_at(value: dict[str, Any], path: list[object], replacement: object) -> None:
    current: Any = value
    for part in path[:-1]:
        current = current[part]
    current[path[-1]] = replacement


def test_all_schemas_are_valid_and_closed() -> None:
    paths = sorted(SCHEMAS.glob("*.schema.json"))
    assert [path.name for path in paths] == [
        "completion-event.schema.json",
        "evidence.schema.json",
        "history.schema.json",
        "snapshot-candidate.schema.json",
        "submission.schema.json",
        "validation-result.schema.json",
    ]
    for path in paths:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False


def test_approved_chain_reproduces_every_fixture() -> None:
    adapter, _, _, validation, evidence, event, history = approved_chain()
    assert adapter.project_validation(validation) == load(
        "approved/validation-result.json"
    )
    assert adapter.to_evidence_document(evidence) == load("approved/evidence.json")
    assert adapter.to_event_document(event) == load("approved/completion-event.json")
    assert adapter.to_history_document(history) == load("approved/history.json")
    event_text = json.dumps(adapter.to_event_document(event), sort_keys=True)
    assert "learner_id" not in event_text
    assert "milestone_evidence" not in event_text


def test_order_equivalent_submission_has_fixed_fingerprint() -> None:
    adapter, candidate, _, validation, *_ = approved_chain()
    equivalent = adapter.parse_submission(
        (CORPUS / "vectors/order-equivalent-submission.json").read_bytes()
    )
    vector = load("vectors/request-fingerprint.json")
    assert validation.request_fingerprint == vector["request_fingerprint"]
    assert adapter.validate(candidate, equivalent).request_fingerprint == vector[
        "request_fingerprint"
    ]


@pytest.mark.parametrize(
    "case",
    load("cases/denials.json"),
    ids=lambda case: case["id"],
)
def test_denials_are_deterministic_and_bounded(case: dict[str, Any]) -> None:
    candidate_document = load("approved/snapshot-candidate.json")
    submission_document = load("approved/submission.json")
    target = submission_document
    path = case["path"]
    if case["op"] == "delete_index":
        current: Any = target
        for part in path[:-1]:
            current = current[part]
        del current[path[-1]]
    elif case["op"] == "copy_index":
        current = target
        for part in path[:-1]:
            current = current[part]
        current.append(copy.deepcopy(current[path[-1]]))
    else:
        _set_at(target, path, case["value"])
    adapter = ContractProjectSubmissionAdapter(SCHEMAS)
    result = adapter.validate(
        adapter.parse_candidate(json.dumps(candidate_document).encode()),
        adapter.parse_submission(json.dumps(submission_document).encode()),
    )
    assert result.status == "refused"
    assert case["expected_code"] in {issue.code for issue in result.issues}
    assert all(len(issue.reference) <= 120 for issue in result.issues)
    assert all("\n" not in issue.reference for issue in result.issues)


@pytest.mark.parametrize(
    "case",
    load("cases/malicious-expansions.json"),
    ids=lambda case: case["id"],
)
def test_private_active_and_authority_expansions_fail_closed(
    case: dict[str, Any],
) -> None:
    document = load(
        "approved/snapshot-candidate.json"
        if case["target"] == "candidate"
        else "approved/submission.json"
    )
    _set_at(document, case["path"], case["value"])
    adapter = ContractProjectSubmissionAdapter(SCHEMAS)
    method = (
        adapter.parse_candidate
        if case["target"] == "candidate"
        else adapter.parse_submission
    )
    with pytest.raises(ProjectSubmissionContractFailure) as captured:
        method(json.dumps(document).encode())
    assert captured.value.code == "assessment.project.schema_invalid"
    assert len(captured.value.reference) <= 120


def test_cli_emits_only_bounded_summary() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.assessment_project.runner"],
        cwd=Path(__file__).resolve().parents[3],
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["valid"] is True
    assert output["resource_kinds"] == [
        "artifact",
        "domain_resource",
        "note",
        "source",
    ]
    assert "local-learner" not in completed.stdout
    assert "Traceback" not in completed.stderr
