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
    CrossDomainContractValidator,
    approved_records,
    canonical_bytes,
    current_v1_fingerprints,
    default_corpus_dir,
    default_schema_dir,
)


CORPUS = default_corpus_dir()
REPOSITORY = Path(__file__).resolve().parents[4]
EXPECTED_PROFILES = {
    "administrative_action",
    "dataset_snapshot",
    "financial_result",
    "market_observation",
    "model_execution",
    "model_version",
    "project_snapshot",
    "recommendation_record",
    "simulation_result",
}


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
        current[key] = [copy.deepcopy(original[index % len(original)]) for index in range(operation["count"])]
    else:
        raise AssertionError(operation["op"])


def test_v2_schemas_are_valid_draft_2020_12() -> None:
    schemas = list(default_schema_dir().glob("*.schema.json"))
    assert {path.name for path in schemas} == {
        "envelope.schema.json",
        "profile-catalog.schema.json",
    }
    for path in schemas:
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_catalog_and_approved_corpus_cover_each_closed_profile_once() -> None:
    validator = CrossDomainContractValidator()
    records = approved_records()
    assert set(validator.profiles) == EXPECTED_PROFILES
    assert set(records) == EXPECTED_PROFILES
    assert [item["profile"] for item in validator.catalog["profiles"]] == sorted(
        EXPECTED_PROFILES
    )
    for profile, record in records.items():
        admitted = validator.validate_envelope(record)
        assert admitted["resource"]["profile"] == profile


def test_canonical_vectors_and_equivalent_source_order_are_stable() -> None:
    validator = CrossDomainContractValidator()
    records = approved_records()
    vectors = json.loads(
        (CORPUS / "vectors/canonicalization.json").read_text(encoding="utf-8")
    )
    project = records["project_snapshot"]
    reordered = copy.deepcopy(project)
    reordered["sources"].reverse()
    assert validator.catalog_digest() == vectors["catalog_digest"]
    assert validator.envelope_digest(project) == vectors["project_snapshot_envelope_digest"]
    assert validator.envelope_digest(reordered) == vectors["project_snapshot_envelope_digest"]
    assert validator.envelope_digest(records["model_execution"]) == vectors[
        "model_execution_envelope_digest"
    ]
    assert canonical_bytes(validator.validate_envelope(project)) == canonical_bytes(
        validator.validate_envelope(reordered)
    )


def test_valid_values_vary_without_fixture_count_or_timezone_rigidity() -> None:
    validator = CrossDomainContractValidator()
    record = copy.deepcopy(approved_records()["dataset_snapshot"])
    record["resource"]["resource_id"] = "資料-été-02"
    record["resource"]["identity"]["dataset_id"] = "資料-été-02"
    record["resource"]["identity"]["dataset_version"] = "2026.10.19-beta+2"
    record["resource"]["recorded_at"] = "2026-10-18T10:01:00+02:00"
    record["resource"]["provenance_label"] = "generated"
    admitted = validator.validate_envelope(record)
    assert admitted["resource"]["recorded_at"] == "2026-10-18T08:01:00Z"
    assert admitted["sources"] == []


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_denial_corpus_fails_closed_with_bounded_codes(case: dict[str, Any]) -> None:
    target = copy.deepcopy(approved_records()[case["target_profile"]])
    for operation in case["ops"]:
        _apply(target, operation)
    validator = CrossDomainContractValidator()
    with pytest.raises(ConformanceFailure) as captured:
        validator.validate_envelope(target)
    diagnostic = captured.value.diagnostic
    assert diagnostic.code == case["expected_code"]
    assert len(diagnostic.reference) <= 120
    assert "\n" not in diagnostic.reference
    assert "private" not in diagnostic.message
    assert "https://" not in diagnostic.message


def test_changed_and_identical_duplicate_identities_fail_independently() -> None:
    validator = CrossDomainContractValidator()
    project = copy.deepcopy(approved_records()["project_snapshot"])
    duplicate = copy.deepcopy(project["sources"][0])
    project["sources"].append(duplicate)
    with pytest.raises(ConformanceFailure) as captured:
        validator.validate_envelope(project)
    assert captured.value.diagnostic.code == "provenance_v2.duplicate_reference"

    project["sources"][-1]["reference"]["integrity_digest"] = "9" * 64
    with pytest.raises(ConformanceFailure) as captured:
        validator.validate_envelope(project)
    assert captured.value.diagnostic.code == "provenance_v2.identity_conflict"

    self_reference = copy.deepcopy(approved_records()["project_snapshot"])
    root = copy.deepcopy(self_reference["resource"])
    self_reference["sources"] = [{"relation": "derived_from", "reference": root}]
    with pytest.raises(ConformanceFailure) as captured:
        validator.validate_envelope(self_reference)
    assert captured.value.diagnostic.code == "provenance_v2.duplicate_reference"


@pytest.mark.parametrize("unsafe", ["🙂dataset", "_dataset", "dataset\u2060hidden"])
def test_unsafe_identifier_categories_fail_semantic_validation(unsafe: str) -> None:
    record = copy.deepcopy(approved_records()["dataset_snapshot"])
    record["resource"]["resource_id"] = unsafe
    record["resource"]["identity"]["dataset_id"] = unsafe
    with pytest.raises(ConformanceFailure) as captured:
        CrossDomainContractValidator().validate_envelope(record)
    assert captured.value.diagnostic.code in {
        "provenance_v2.schema_invalid",
        "provenance_v2.identity_invalid",
    }


def test_v1_contract_and_approved_corpus_fingerprints_are_unchanged() -> None:
    expected = json.loads(
        (CORPUS / "vectors/v1-fingerprints.json").read_text(encoding="utf-8")
    )
    assert current_v1_fingerprints() == expected


def test_runner_has_no_product_or_runtime_adapter_import() -> None:
    source = (Path(__file__).with_name("runner.py")).read_text(encoding="utf-8")
    assert "financial_ai_academy" not in source
    assert "requests" not in source
    assert "psycopg" not in source


def test_cli_emits_bounded_json_without_payload_or_stack_trace() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.provenance_v2.runner"],
        cwd=REPOSITORY / "backend",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["valid"] is True
    assert output["profile_count"] == 9
    assert set(output["envelope_digests"]) == EXPECTED_PROFILES
    combined = completed.stdout + completed.stderr
    assert "private" not in combined
    assert "Traceback" not in combined
