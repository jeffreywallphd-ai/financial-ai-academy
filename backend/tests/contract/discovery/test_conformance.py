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
    ConformanceFailure,
    DiscoveryContractValidator,
    approved_records,
    default_corpus_dir,
    default_schema_dir,
    projection_generation,
    source_fingerprint,
)


CORPUS = default_corpus_dir()
REPOSITORY = Path(__file__).resolve().parents[4]


def _set_at(value: dict[str, Any], path: list[object], replacement: object) -> None:
    current: Any = value
    for part in path[:-1]:
        current = current[part]
    current[path[-1]] = replacement


def _remove_at(value: dict[str, Any], path: list[object]) -> None:
    current: Any = value
    for part in path[:-1]:
        current = current[part]
    del current[path[-1]]


def test_discovery_schemas_are_valid_draft_2020_12() -> None:
    schemas = list(default_schema_dir().glob("*.schema.json"))
    assert {path.name for path in schemas} == {
        "browse.schema.json",
        "opportunity.schema.json",
    }
    for path in schemas:
        Draft202012Validator.check_schema(
            json.loads(path.read_text(encoding="utf-8"))
        )


def test_approved_opportunity_and_browse_validate() -> None:
    opportunity, browse = approved_records()
    validator = DiscoveryContractValidator()
    validator.validate_opportunity(opportunity)
    validator.validate_browse(browse)
    assert browse["records"] == [opportunity]


def test_digest_vectors_are_stable_and_independently_computed() -> None:
    opportunity, browse = approved_records()
    vector = json.loads(
        (CORPUS / "vectors/source-fingerprint.json").read_text(encoding="utf-8")
    )
    assert source_fingerprint(opportunity) == vector["source_fingerprint"]
    assert projection_generation(browse["records"]) == vector[
        "projection_generation"
    ]
    assert opportunity["source_fingerprint"] == vector["source_fingerprint"]
    assert browse["projection_generation"] == vector["projection_generation"]


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_denial_corpus_fails_closed_with_bounded_codes(
    case: dict[str, Any],
) -> None:
    opportunity, browse = approved_records()
    target = copy.deepcopy(opportunity if case["target"] == "opportunity" else browse)
    if case["op"] == "set":
        _set_at(target, case["path"], case["value"])
    else:
        _remove_at(target, case["path"])
    validator = DiscoveryContractValidator()
    with pytest.raises(ConformanceFailure) as captured:
        if case["target"] == "opportunity":
            validator.validate_opportunity(target)
        else:
            validator.validate_browse(target)
    diagnostic = captured.value.diagnostic
    assert diagnostic.code == case["expected_code"]
    assert len(diagnostic.reference) <= 120
    assert "\n" not in diagnostic.reference
    assert str(case.get("value", "sentinel")) not in diagnostic.message


def test_cli_emits_bounded_json_without_source_payload_or_stack_trace() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.discovery.runner"],
        cwd=REPOSITORY / "backend",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["valid"] is True
    assert output["record_count"] == 1
    combined = completed.stdout + completed.stderr
    assert "Educational material only" not in combined
    assert "Traceback" not in combined
