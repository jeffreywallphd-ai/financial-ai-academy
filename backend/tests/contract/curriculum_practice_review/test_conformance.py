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
    PracticeReviewFailure,
    PracticeReviewValidator,
    corpus_dir,
    load_json,
    schema_path,
    select_review_targets,
)


CORPUS = corpus_dir()


def _approved() -> tuple[dict[str, Any], dict[str, Any]]:
    approved = CORPUS / "approved"
    return load_json(approved / "available.json"), load_json(approved / "unavailable.json")


def _set_at(value: dict[str, Any], path: list[object], replacement: object) -> None:
    target: Any = value
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = replacement


def test_schema_and_both_states_validate() -> None:
    Draft202012Validator.check_schema(load_json(schema_path()))
    validator = PracticeReviewValidator()
    for target in _approved():
        validator.validate(target)


def test_selection_is_unique_and_declaration_ordered_not_ranked() -> None:
    available, unavailable = _approved()
    selected = select_review_targets(
        ["additional-review", "risk-return-review", "unused-review"],
        [["risk-return-review", "additional-review"], ["risk-return-review"]],
        [available, unavailable],
    )
    assert [target["resource_id"] for target in selected] == [
        "additional-review",
        "risk-return-review",
    ]
    assert selected[0]["state"] == "unavailable"


def test_missing_mapping_is_not_substituted() -> None:
    available, _ = _approved()
    assert select_review_targets(
        ["unmapped-review", "risk-return-review"],
        [["unmapped-review"]],
        [available],
    ) == []


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_denial_corpus_fails_closed(case: dict[str, Any]) -> None:
    available, unavailable = map(copy.deepcopy, _approved())
    target = available if case["target"] == "available" else unavailable
    if case["op"] == "delete":
        container: Any = target
        for part in case["path"][:-1]:
            container = container[part]
        del container[case["path"][-1]]
    elif case["op"] == "copy_destination":
        target["destination"] = copy.deepcopy(available["destination"])
    else:
        _set_at(target, case["path"], case["value"])
    with pytest.raises(PracticeReviewFailure) as captured:
        PracticeReviewValidator().validate(target)
    assert captured.value.code == case["expected_code"]
    assert len(captured.value.reference) <= 120
    assert "\n" not in captured.value.reference


def test_cli_emits_only_bounded_public_summary() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.curriculum_practice_review.runner"],
        cwd=Path(__file__).resolve().parents[3],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == {"states": ["available", "unavailable"], "valid": True}
    assert "https://" not in completed.stdout
    assert "Traceback" not in completed.stderr
