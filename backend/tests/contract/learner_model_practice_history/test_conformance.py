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
    PracticeHistoryFailure,
    PracticeHistoryValidator,
    corpus_dir,
    load_json,
    ordered_unique_attempts,
    schema_path,
    source_digest,
)


CORPUS = corpus_dir()


def _approved() -> dict[str, Any]:
    return load_json(CORPUS / "approved/history.json")


def _set_at(value: dict[str, Any], path: list[object], replacement: object) -> None:
    target: Any = value
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = replacement


def test_schema_and_approved_history_validate() -> None:
    Draft202012Validator.check_schema(load_json(schema_path()))
    PracticeHistoryValidator().validate(_approved())


def test_empty_history_is_valid_and_rebuildable() -> None:
    history = _approved()
    history["attempts"] = []
    history["source_digest"] = source_digest([])
    PracticeHistoryValidator().validate(history)


def test_exact_duplicate_replay_is_idempotent_and_input_order_independent() -> None:
    attempt = _approved()["attempts"][0]
    assert ordered_unique_attempts([attempt, copy.deepcopy(attempt)]) == [attempt]


def test_inconsistent_duplicate_event_fails_closed() -> None:
    attempt = _approved()["attempts"][0]
    changed = copy.deepcopy(attempt)
    changed["score"] = 1
    with pytest.raises(PracticeHistoryFailure) as captured:
        ordered_unique_attempts([attempt, changed])
    assert captured.value.code == "learner_model.practice_history.inconsistent_duplicate"


def test_variable_attempt_count_and_input_order_are_not_fixture_locked() -> None:
    history = _approved()
    template = history["attempts"][0]
    attempts = []
    for index in range(1, 11):
        attempt = copy.deepcopy(template)
        attempt["attempt_order"] = index
        suffix = f"{index:012d}"
        attempt["event_id"] = f"55555555-5555-4555-8555-{suffix}"
        attempt["attempt_id"] = f"33333333-3333-4333-8333-{suffix}"
        attempt["evidence_id"] = f"44444444-4444-4444-8444-{suffix}"
        attempt["submission_id"] = f"22222222-2222-4222-8222-{suffix}"
        attempts.append(attempt)
    history["attempts"] = ordered_unique_attempts(list(reversed(attempts)))
    history["source_digest"] = source_digest(history["attempts"])
    PracticeHistoryValidator().validate(history)


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_denial_corpus_fails_closed(case: dict[str, Any]) -> None:
    history = _approved()
    _set_at(history, case["path"], case["value"])
    with pytest.raises(PracticeHistoryFailure) as captured:
        PracticeHistoryValidator().validate(history)
    assert captured.value.code == case["expected_code"]
    assert len(captured.value.reference) <= 120
    assert "\n" not in captured.value.reference


def test_cli_emits_bounded_summary_without_private_values() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.learner_model_practice_history.runner"],
        cwd=Path(__file__).resolve().parents[3],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["valid"] is True
    assert output["attempt_count"] == 1
    assert "uncertainty" not in completed.stdout
    assert "Traceback" not in completed.stderr
