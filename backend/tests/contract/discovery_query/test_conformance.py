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
    DiscoveryQueryContractValidator,
    approved_values,
    canonicalize_request,
    default_corpus_dir,
    default_schema_dir,
    normalize_query_text,
)


CORPUS = default_corpus_dir()
REPOSITORY = Path(__file__).resolve().parents[4]
SCENARIOS = json.loads(
    (CORPUS / "vectors/scenarios.json").read_text(encoding="utf-8")
)


def _set_at(value: dict[str, Any], path: list[object], replacement: object) -> None:
    current: Any = value
    for part in path[:-1]:
        current = current[part]
    current[path[-1]] = replacement


def test_query_schemas_are_valid_draft_2020_12() -> None:
    schemas = list(default_schema_dir().glob("*.schema.json"))
    assert {path.name for path in schemas} == {
        "applied-query.schema.json",
        "page.schema.json",
        "request.schema.json",
    }
    for path in schemas:
        Draft202012Validator.check_schema(
            json.loads(path.read_text(encoding="utf-8"))
        )


def test_approved_query_and_page_validate() -> None:
    request, page = approved_values()
    validator = DiscoveryQueryContractValidator()
    validator.validate_request(request)
    validator.validate_page(page)
    assert page["applied_query"] == canonicalize_request(request)
    assert len(request["topics"]) > len(page["applied_query"]["topics"])
    assert page["records"][0]["opportunity_id"] == (
        "intro-risk-return-primary"
    )


@pytest.mark.parametrize(
    "vector",
    json.loads((CORPUS / "vectors/normalization.json").read_text(encoding="utf-8")),
    ids=lambda vector: vector["id"],
)
def test_normalization_vectors_are_stable(vector: dict[str, str]) -> None:
    assert normalize_query_text(vector["input"]) == vector["normalized"]


@pytest.mark.parametrize(
    "case",
    SCENARIOS["query_cases"],
    ids=lambda case: case["id"],
)
def test_multi_record_query_scenarios_are_stable(
    case: dict[str, Any],
) -> None:
    request = copy.deepcopy(SCENARIOS["request_defaults"])
    request.update(case["overrides"])
    validator = DiscoveryQueryContractValidator()
    validator.validate_request(request)
    applied = canonicalize_request(request)
    validator._shape(validator._applied, applied, "applied_query")
    validator._canonical_text(applied)
    validator._canonical_filters(applied)
    validator._duration(applied)
    for key, expected in case.get("expected_applied", {}).items():
        assert applied[key] == expected
    matches = [
        record
        for record in SCENARIOS["records"]
        if validator._matches(record, applied)
    ]
    ordered = validator._sorted(matches, applied["sort"])
    assert [record["opportunity_id"] for record in ordered] == case[
        "expected_ids"
    ]


def test_cursor_scenario_vectors_cover_required_semantics() -> None:
    cursor_cases = {case["id"]: case for case in SCENARIOS["cursor_cases"]}
    assert set(cursor_cases) == {
        "multi-page-continuity-and-replay",
        "checksum-mismatch",
        "query-mismatch",
        "generation-mismatch",
    }
    continuity = cursor_cases["multi-page-continuity-and-replay"]
    assert continuity["expected_pages"] == [
        ["zulu-unavailable", "alpha-available"],
        ["beta-available", "alpha-planned"],
    ]
    assert cursor_cases["checksum-mismatch"]["expected_code"] == (
        "invalid_query"
    )
    assert cursor_cases["query-mismatch"]["expected_code"] == "invalid_query"
    assert cursor_cases["generation-mismatch"]["expected_code"] == (
        "stale_cursor"
    )


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_denial_corpus_fails_closed_with_bounded_codes(
    case: dict[str, Any],
) -> None:
    request, page = approved_values()
    target = copy.deepcopy(request if case["target"] == "request" else page)
    _set_at(target, case["path"], case["value"])
    validator = DiscoveryQueryContractValidator()
    with pytest.raises(ConformanceFailure) as captured:
        if case["target"] == "request":
            validator.validate_request(target)
        else:
            validator.validate_page(target)
    diagnostic = captured.value.diagnostic
    assert diagnostic.code == case["expected_code"]
    assert len(diagnostic.reference) <= 120
    assert "\n" not in diagnostic.reference
    raw_value = str(case.get("value", "sentinel"))
    if raw_value:
        assert raw_value not in diagnostic.message


def test_cli_emits_bounded_json_without_record_or_stack_trace() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.discovery_query.runner"],
        cwd=REPOSITORY / "backend",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output == {
        "query": "risk return",
        "record_count": 1,
        "total_matches": 1,
        "valid": True,
    }
    combined = completed.stdout + completed.stderr
    assert "Understanding Risk and Return" not in combined
    assert "Traceback" not in combined
