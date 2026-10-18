from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from .runner import (
    ConformanceFailure,
    ContextualHelpContractValidator,
    approved_record,
    default_corpus_dir,
)


def _assign(value: dict[str, object], path: list[object], replacement: object) -> None:
    target: object = value
    for part in path[:-1]:
        target = target[part]  # type: ignore[index]
    target[path[-1]] = replacement  # type: ignore[index]


def test_approved_context_conforms() -> None:
    admitted = ContextualHelpContractValidator().validate_context(approved_record())
    assert admitted.context_key == "project-result"
    assert admitted.context_version == "1.0.0"
    assert len(admitted.context_digest) == 64


def test_declared_denials_fail_closed_without_echoing_values() -> None:
    cases = json.loads(
        (default_corpus_dir() / "cases/denials.json").read_text(encoding="utf-8")
    )["cases"]
    validator = ContextualHelpContractValidator()
    for case in cases:
        value = copy.deepcopy(approved_record())
        _assign(value, case["path"], case["value"])
        with pytest.raises(ConformanceFailure) as captured:
            validator.validate_context(value)
        assert str(case["value"]) not in captured.value.diagnostic.message


def test_canonicalization_vector_matches_approved_record() -> None:
    vector = json.loads(
        (default_corpus_dir() / "vectors/canonicalization.json").read_text(
            encoding="utf-8"
        )
    )
    admitted = ContextualHelpContractValidator().validate_context(approved_record())
    assert admitted.context_key == vector["context_key"]
    assert admitted.context_version == vector["context_version"]
    assert admitted.context_digest == vector["expected_digest"]


def test_runner_reports_bounded_success() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "backend.tests.contract.contextual_help.runner"],
        cwd=Path(__file__).resolve().parents[4],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = json.loads(completed.stdout)
    assert output == {
        "valid": True,
        "context_key": "project-result",
        "context_version": "1.0.0",
        "context_digest": "640edbf063b0978a800e840ccd367b8d7bdc186dd224af84987ee36f5fb2714d",
    }
