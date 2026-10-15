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
    AssessmentContractValidator,
    ConformanceFailure,
    approved_chain,
    canonical_definition_bytes,
    default_corpus_dir,
    default_event_schema_dir,
    default_learning_schema_dir,
    definition_digest,
)


REPOSITORY = Path(__file__).resolve().parents[4]
CORPUS = default_corpus_dir()
SUCCESSOR = (
    REPOSITORY
    / "contracts/compatibility/lesson-package/v1/approved/intro-risk-return-knowledge-check"
)
ORIGINAL = (
    REPOSITORY
    / "contracts/compatibility/lesson-package/v1/approved/intro-risk-return"
)


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


def _mutated_chain(case: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    chain = [copy.deepcopy(value) for value in approved_chain(CORPUS, "correct")]
    index = {
        "definition": 0,
        "presentation": 1,
        "submission": 2,
        "result": 3,
        "event": 4,
    }[case["target"]]
    if case["op"] == "set":
        _set_at(chain[index], case["path"], case["value"])
    else:
        _remove_at(chain[index], case["path"])
    if case.get("refresh_definition_digest"):
        chain[0]["definition_digest"] = definition_digest(chain[0])
    return tuple(chain)


def test_all_assessment_schemas_are_valid_draft_2020_12() -> None:
    schemas = [
        *default_learning_schema_dir().glob("*.schema.json"),
        *default_event_schema_dir().glob("*.schema.json"),
    ]
    assert {path.name for path in schemas} == {
        "definition.schema.json",
        "presentation.schema.json",
        "submission.schema.json",
        "result.schema.json",
        "knowledge-check-completed.schema.json",
    }
    for path in schemas:
        Draft202012Validator.check_schema(
            json.loads(path.read_text(encoding="utf-8"))
        )


@pytest.mark.parametrize("outcome", ["correct", "incorrect"])
def test_approved_chains_validate_with_independent_expected_outcomes(
    outcome: str,
) -> None:
    chain = approved_chain(CORPUS, outcome)
    AssessmentContractValidator().validate_chain(*chain)
    expected_score = 1 if outcome == "correct" else 0
    expected_feedback = (
        "risk-return-correct" if outcome == "correct" else "risk-return-review"
    )
    assert chain[3]["score"] == expected_score
    assert chain[3]["correct"] is (outcome == "correct")
    assert chain[3]["feedback"]["feedback_id"] == expected_feedback
    assert chain[4]["payload"]["score"] == expected_score


def test_definition_digest_vector_matches_canonical_private_meaning() -> None:
    definition = approved_chain(CORPUS, "correct")[0]
    vector = json.loads(
        (CORPUS / "vectors/definition-digest.json").read_text(encoding="utf-8")
    )
    assert definition_digest(definition) == vector["definition_digest"]
    assert definition["definition_digest"] == vector["definition_digest"]
    reloaded = json.loads(json.dumps(definition["assessment"], sort_keys=False))
    assert canonical_definition_bytes(definition["assessment"]) == (
        canonical_definition_bytes(reloaded)
    )


def test_presentation_excludes_answer_and_feedback_internals() -> None:
    presentation = approved_chain(CORPUS, "correct")[1]
    serialized = json.dumps(presentation, sort_keys=True)
    assert "correct_option_id" not in serialized
    assert "risk-return-correct" not in serialized
    assert "risk-return-review" not in serialized
    assert "feedback" not in serialized


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_denial_corpus_fails_closed_with_stable_bounded_codes(
    case: dict[str, Any],
) -> None:
    with pytest.raises(ConformanceFailure) as captured:
        AssessmentContractValidator().validate_chain(*_mutated_chain(case))
    diagnostic = captured.value.diagnostic
    assert diagnostic.code == case["expected_code"]
    assert len(diagnostic.reference) <= 120
    assert "\n" not in diagnostic.reference
    assert str(case.get("value", "sentinel")) not in diagnostic.message


def test_successor_package_and_original_have_stable_distinct_digests() -> None:
    def validate_package(path: Path) -> dict[str, Any]:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "tests.contract.lesson_package.runner",
                str(path),
                "--schema-dir",
                str(REPOSITORY / "contracts/learning/lesson-package/v1"),
            ],
            cwd=REPOSITORY / "backend",
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert completed.returncode == 0, completed.stderr
        return json.loads(completed.stdout)

    original = validate_package(ORIGINAL)
    successor = validate_package(SUCCESSOR)
    vector = json.loads(
        (CORPUS / "vectors/successor-package-index.json").read_text(
            encoding="utf-8"
        )
    )
    original_vector = json.loads(
        (
            REPOSITORY
            / "contracts/compatibility/lesson-package/v1/vectors/package-index.json"
        ).read_text(encoding="utf-8")
    )
    assert original["package_version"] == "1.0.0"
    assert successor["package_version"] == "1.1.0"
    assert original["package_digest"] == original_vector["package_digest"]
    assert original["package_digest"] != successor["package_digest"]
    assert successor["package_digest"] == vector["package_digest"]
    assert successor["file_count"] == len(vector["entries"])
    assert (ORIGINAL / "lesson.md").read_bytes() == (
        SUCCESSOR / "lesson.md"
    ).read_bytes()
    assert (CORPUS / "approved/definition.json").read_bytes() == (
        SUCCESSOR / "assessments/check-1.json"
    ).read_bytes()


def test_cli_emits_bounded_json_without_private_answer_or_stack_trace() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "tests.contract.assessment.runner",
            "--outcome",
            "correct",
        ],
        cwd=REPOSITORY / "backend",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["valid"] is True
    assert output["score"] == 1
    combined = completed.stdout + completed.stderr
    assert "higher-potential-higher-uncertainty" not in combined
    assert "Traceback" not in combined
