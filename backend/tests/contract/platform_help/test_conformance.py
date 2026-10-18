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
    PlatformHelpContractValidator,
    approved_records,
    default_corpus_dir,
    default_schema_dir,
)
from financial_ai_academy.modules.guidance.domain import (
    PlatformHelpCorpus,
    corpus_digest,
    topic_digest,
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


def test_platform_help_schemas_are_valid_draft_2020_12() -> None:
    schemas = list(default_schema_dir().glob("*.schema.json"))
    assert {path.name for path in schemas} == {
        "search-page.schema.json",
        "search-request.schema.json",
        "topic.schema.json",
    }
    for path in schemas:
        Draft202012Validator.check_schema(
            json.loads(path.read_text(encoding="utf-8"))
        )


def test_approved_topic_request_and_page_validate() -> None:
    topic, request, page = approved_records()
    validator = PlatformHelpContractValidator()
    admitted = validator.validate_topic(topic)
    validator.validate_search_request(request)
    validator.validate_search_page(page, topic=topic, request=request)
    assert admitted.topic_id == "approved-help"


def test_digest_vectors_are_stable_and_independently_computed() -> None:
    topic, _, _ = approved_records()
    admitted = PlatformHelpContractValidator().validate_topic(topic)
    vector = json.loads(
        (CORPUS / "vectors/canonicalization.json").read_text(encoding="utf-8")
    )
    assert topic_digest(admitted) == vector["topic_digest"]
    assert corpus_digest((admitted,)) == vector["corpus_digest"]


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_denial_corpus_fails_closed_with_bounded_codes(
    case: dict[str, Any],
) -> None:
    topic, request, page = approved_records()
    values = {"topic": topic, "search_request": request, "search_page": page}
    target = copy.deepcopy(values[case["target"]])
    if case["op"] == "set":
        _set_at(target, case["path"], case["value"])
    else:
        _remove_at(target, case["path"])
    validator = PlatformHelpContractValidator()
    with pytest.raises(ConformanceFailure) as captured:
        if case["target"] == "topic":
            validator.validate_topic(target)
        elif case["target"] == "search_request":
            validator.validate_search_request(target)
        else:
            validator.validate_search_page(target, topic=topic, request=request)
    diagnostic = captured.value.diagnostic
    assert diagnostic.code == case["expected_code"]
    assert len(diagnostic.reference) <= 120
    assert "\n" not in diagnostic.reference
    assert str(case.get("value", "sentinel")) not in diagnostic.message


def test_cli_emits_bounded_json_without_payload_or_stack_trace() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.platform_help.runner"],
        cwd=REPOSITORY / "backend",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["valid"] is True
    assert output["topic_id"] == "approved-help"
    combined = completed.stdout + completed.stderr
    assert "C:/private" not in combined
    assert "Traceback" not in combined
