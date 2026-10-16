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
    PracticeConformanceFailure,
    PracticeContractValidator,
    approved_chain,
    approved_pair,
    approved_progress,
    canonical_practice_bytes,
    canonical_draft_responses_bytes,
    canonical_submission_bytes,
    corpus_dir,
    definition_digest,
    draft_response_fingerprint,
    schema_dir,
    submission_fingerprint,
)


CORPUS = corpus_dir()


def _set_at(value: dict[str, Any], path: list[object], replacement: object) -> None:
    current: Any = value
    for part in path[:-1]:
        current = current[part]
    current[path[-1]] = replacement


def _mutated(case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    definition, presentation = map(copy.deepcopy, approved_pair())
    target = definition if case["target"] == "definition" else presentation
    _set_at(target, case["path"], case["value"])
    if case.get("refresh_definition_digest"):
        definition["definition_digest"] = definition_digest(definition)
    return definition, presentation


def test_schemas_are_valid_draft_2020_12() -> None:
    paths = sorted(schema_dir().glob("*.schema.json"))
    assert [path.name for path in paths] == [
        "completion-event.schema.json",
        "definition.schema.json",
        "draft-save.schema.json",
        "draft.schema.json",
        "presentation.schema.json",
        "result.schema.json",
        "retry-state.schema.json",
        "submission.schema.json",
    ]
    for path in paths:
        Draft202012Validator.check_schema(
            json.loads(path.read_text(encoding="utf-8"))
        )


def test_approved_definition_and_safe_projection_validate() -> None:
    definition, presentation = approved_pair()
    validator = PracticeContractValidator()
    validator.validate_presentation(definition, presentation)
    assert [item["item_type"] for item in presentation["items"]] == [
        "single_select",
        "multiple_select",
        "numeric_entry",
    ]
    assert validator.project(
        definition,
        placement_id=presentation["placement_id"],
        package_id=presentation["package_id"],
        package_version=presentation["package_version"],
        package_digest=presentation["package_digest"],
    ) == presentation


def test_approved_draft_save_server_draft_and_retry_state_validate() -> None:
    definition, presentation = approved_pair()
    draft_save, draft, retry_state = approved_progress()
    validator = PracticeContractValidator()
    validator.validate_draft_save(definition, presentation, draft_save)
    validator.validate_draft(definition, presentation, draft)
    validator.validate_retry_state(definition, presentation, retry_state)
    assert draft["response_fingerprint"] == draft_response_fingerprint(
        draft["responses"]
    )
    assert "learner_id" not in json.dumps(
        {"draft_save": draft_save, "draft": draft, "retry": retry_state}
    )


def test_draft_fingerprint_is_order_independent_and_supports_empty_progress() -> None:
    definition, presentation = approved_pair()
    draft_save, _, _ = map(copy.deepcopy, approved_progress())
    forward = canonical_draft_responses_bytes(draft_save["responses"])
    draft_save["responses"].reverse()
    assert canonical_draft_responses_bytes(draft_save["responses"]) == forward
    PracticeContractValidator().validate_draft_save(
        definition, presentation, draft_save
    )
    draft_save["responses"] = []
    PracticeContractValidator().validate_draft_save(
        definition, presentation, draft_save
    )


@pytest.mark.parametrize("maximum", range(1, 11))
def test_retry_state_accepts_every_policy_limit(maximum: int) -> None:
    definition, presentation = map(copy.deepcopy, approved_pair())
    _, _, retry_state = map(copy.deepcopy, approved_progress())
    definition["practice"]["attempt_policy"]["max_attempts"] = maximum
    definition["definition_digest"] = definition_digest(definition)
    presentation = PracticeContractValidator().project(
        definition,
        placement_id=presentation["placement_id"],
        package_id=presentation["package_id"],
        package_version=presentation["package_version"],
        package_digest=presentation["package_digest"],
    )
    retry_state["definition_digest"] = definition["definition_digest"]
    retry_state["attempts_used"] = maximum
    retry_state["max_attempts"] = maximum
    retry_state["attempts_remaining"] = 0
    retry_state["can_retry"] = False
    retry_state["state"] = "exhausted"
    PracticeContractValidator().validate_retry_state(
        definition, presentation, retry_state
    )


def _progress_denial(case: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    values = dict(zip(("draft_save", "draft", "retry_state"), map(copy.deepcopy, approved_progress())))
    target = values[case["target"]]
    if case["op"] == "append_response_copy":
        target["responses"].append(copy.deepcopy(target["responses"][0]))
    else:
        _set_at(target, case["path"], case["value"])
    return case["target"], target


@pytest.mark.parametrize(
    "case",
    json.loads(
        (CORPUS / "cases/draft-retry-denials.json").read_text(encoding="utf-8")
    ),
    ids=lambda case: case["id"],
)
def test_draft_and_retry_denials_are_bounded(case: dict[str, Any]) -> None:
    definition, presentation = approved_pair()
    target_name, target = _progress_denial(case)
    validator = PracticeContractValidator()
    method = {
        "draft_save": validator.validate_draft_save,
        "draft": validator.validate_draft,
        "retry_state": validator.validate_retry_state,
    }[target_name]
    with pytest.raises(PracticeConformanceFailure) as captured:
        method(definition, presentation, target)
    assert captured.value.code == case["expected_code"]
    assert len(captured.value.reference) <= 120
    assert "\n" not in captured.value.reference


def test_definition_digest_vector_fixes_private_meaning() -> None:
    definition, _ = approved_pair()
    vector = json.loads(
        (CORPUS / "vectors/definition-digest.json").read_text(encoding="utf-8")
    )
    assert definition_digest(definition) == vector["definition_digest"]
    assert definition["definition_digest"] == vector["definition_digest"]
    reloaded = json.loads(json.dumps(definition["practice"], sort_keys=False))
    assert canonical_practice_bytes(definition["practice"]) == (
        canonical_practice_bytes(reloaded)
    )


def test_non_ascii_digest_vector_fixes_raw_utf8_serialization() -> None:
    definition, _ = map(copy.deepcopy, approved_pair())
    vector = json.loads(
        (CORPUS / "vectors/non-ascii-definition-digest.json").read_text(
            encoding="utf-8"
        )
    )
    for mutation in vector["mutations"]:
        _set_at(definition, mutation["path"], mutation["value"])
    canonical = canonical_practice_bytes(definition["practice"])
    assert "café".encode() in canonical
    assert b"\\u00e9" not in canonical
    assert definition_digest(definition) == vector["definition_digest"]
    definition["definition_digest"] = vector["definition_digest"]
    PracticeContractValidator().validate_definition(definition)


def test_presentation_recursively_excludes_private_fields() -> None:
    _, presentation = approved_pair()
    serialized = json.dumps(presentation, sort_keys=True)
    for private_name in (
        "correct_option_id",
        "correct_option_ids",
        '"answer"',
        '"feedback"',
    ):
        assert private_name not in serialized


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_denial_corpus_fails_closed(case: dict[str, Any]) -> None:
    definition, presentation = _mutated(case)
    with pytest.raises(PracticeConformanceFailure) as captured:
        PracticeContractValidator().validate_presentation(definition, presentation)
    assert captured.value.code == case["expected_code"]
    assert len(captured.value.reference) <= 120
    assert "\n" not in captured.value.reference
    assert str(case.get("value", "sentinel")) not in captured.value.message


def test_compatible_counts_order_and_range_rule_are_not_fixture_locked() -> None:
    definition, presentation = map(copy.deepcopy, approved_pair())
    practice = definition["practice"]
    practice["source_references"].append(
        {
            "resource_id": "additional-source",
            "resource_version": "1.0.0",
            "resource_digest": "e" * 64,
            "title": "Additional approved source",
        }
    )
    practice["items"].reverse()
    practice["items"][2]["options"].reverse()
    numeric = practice["items"][0]
    numeric["answer"] = {
        "mode": "inclusive_range",
        "lower": "104.50",
        "upper": "105.50",
    }
    definition["definition_digest"] = definition_digest(definition)
    validator = PracticeContractValidator()
    projection = validator.project(
        definition,
        placement_id=presentation["placement_id"],
        package_id=presentation["package_id"],
        package_version=presentation["package_version"],
        package_digest=presentation["package_digest"],
    )
    validator.validate_presentation(definition, projection)
    assert len(projection["source_references"]) == 2
    assert projection["items"][0]["item_type"] == "numeric_entry"


@pytest.mark.parametrize(
    ("scale", "value", "allow_negative"),
    [
        (0, "105", False),
        (6, "105.000000", False),
        (2, "-105.00", True),
    ],
)
def test_numeric_scale_edges_and_permitted_negative_are_accepted(
    scale: int, value: str, allow_negative: bool
) -> None:
    definition, presentation = map(copy.deepcopy, approved_pair())
    numeric = definition["practice"]["items"][2]
    numeric["response"]["scale"] = scale
    numeric["response"]["allow_negative"] = allow_negative
    numeric["answer"] = {"mode": "exact", "value": value}
    definition["definition_digest"] = definition_digest(definition)
    validator = PracticeContractValidator()
    projected = validator.project(
        definition,
        placement_id=presentation["placement_id"],
        package_id=presentation["package_id"],
        package_version=presentation["package_version"],
        package_digest=presentation["package_digest"],
    )
    validator.validate_presentation(definition, projected)


def _options(count: int) -> list[dict[str, str]]:
    return [
        {"option_id": f"option-{index:02d}", "label": f"Option {index + 1}"}
        for index in range(count)
    ]


def _references(count: int) -> list[dict[str, str]]:
    return [
        {
            "resource_id": f"resource-{index:02d}",
            "resource_version": "1.0.0",
            "resource_digest": f"{index + 1:x}" * 64,
            "title": f"Resource {index + 1}",
        }
        for index in range(count)
    ]


@pytest.mark.parametrize("count", [1, 20])
def test_item_count_edges_are_accepted(count: int) -> None:
    definition, _ = map(copy.deepcopy, approved_pair())
    template = definition["practice"]["items"][0]
    definition["practice"]["items"] = []
    for index in range(count):
        item = copy.deepcopy(template)
        item["item_id"] = f"item-{index:02d}"
        definition["practice"]["items"].append(item)
    definition["definition_digest"] = definition_digest(definition)
    PracticeContractValidator().validate_definition(definition)


@pytest.mark.parametrize(
    ("item_index", "count"),
    [(0, 2), (0, 8), (1, 3), (1, 12)],
)
def test_select_option_count_edges_are_accepted(
    item_index: int, count: int
) -> None:
    definition, _ = map(copy.deepcopy, approved_pair())
    item = definition["practice"]["items"][item_index]
    item["options"] = _options(count)
    if item["item_type"] == "single_select":
        item["correct_option_id"] = "option-00"
    else:
        item["correct_option_ids"] = ["option-00", f"option-{count - 1:02d}"]
    definition["definition_digest"] = definition_digest(definition)
    PracticeContractValidator().validate_definition(definition)


@pytest.mark.parametrize(("reference_name", "count"), [("source_references", 1), ("source_references", 8), ("review_references", 1), ("review_references", 8)])
def test_reference_count_edges_are_accepted(
    reference_name: str, count: int
) -> None:
    definition, _ = map(copy.deepcopy, approved_pair())
    references = _references(count)
    definition["practice"][reference_name] = references
    if reference_name == "review_references":
        for item in definition["practice"]["items"]:
            for feedback in item["feedback"].values():
                feedback["review_reference_ids"] = [references[0]["resource_id"]]
    definition["definition_digest"] = definition_digest(definition)
    PracticeContractValidator().validate_definition(definition)


@pytest.mark.parametrize(
    ("boundary", "count"),
    [
        ("items", 0),
        ("items", 21),
        ("single_options", 1),
        ("single_options", 9),
        ("multiple_options", 2),
        ("multiple_options", 13),
        ("source_references", 0),
        ("source_references", 9),
        ("review_references", 0),
        ("review_references", 9),
    ],
)
def test_resource_count_overflow_and_underflow_fail_closed(
    boundary: str, count: int
) -> None:
    definition, _ = map(copy.deepcopy, approved_pair())
    practice = definition["practice"]
    if boundary == "items":
        template = practice["items"][0]
        practice["items"] = []
        for index in range(count):
            item = copy.deepcopy(template)
            item["item_id"] = f"item-{index:02d}"
            practice["items"].append(item)
    elif boundary == "single_options":
        practice["items"][0]["options"] = _options(count)
        practice["items"][0]["correct_option_id"] = "option-00"
    elif boundary == "multiple_options":
        practice["items"][1]["options"] = _options(count)
        practice["items"][1]["correct_option_ids"] = ["option-00"]
    else:
        practice[boundary] = _references(count)
    definition["definition_digest"] = definition_digest(definition)
    with pytest.raises(PracticeConformanceFailure) as captured:
        PracticeContractValidator().validate_definition(definition)
    assert captured.value.code == "assessment.practice.schema_invalid"


def test_cli_emits_bounded_output_without_private_answers() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.assessment_practice.runner"],
        cwd=Path(__file__).resolve().parents[3],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["valid"] is True
    assert output["item_types"] == [
        "single_select",
        "multiple_select",
        "numeric_entry",
    ]
    combined = completed.stdout + completed.stderr
    assert "105.00" not in combined
    assert "Traceback" not in combined


def test_approved_submission_result_and_event_chain_validate() -> None:
    chain = approved_chain()
    PracticeContractValidator().validate_submission_chain(*chain)
    result = chain[3]
    assert result["score"] == 2
    assert result["max_score"] == 3
    assert result["outcome"] == "review_needed"
    assert [item["item_id"] for item in result["item_results"]] == [
        "risk-meaning",
        "diversification-actions",
        "simple-growth",
    ]
    assert chain[4]["payload"]["score"] == result["score"]
    assert chain[4]["payload"]["item_scores"] == [
        {
            key: item[key]
            for key in (
                "item_id",
                "item_version",
                "item_type",
                "scoring_policy_id",
                "scoring_policy_version",
                "score",
                "max_score",
            )
        }
        for item in result["item_results"]
    ]


def test_request_fingerprint_is_fixed_and_order_independent() -> None:
    submission = approved_chain()[2]
    equivalent = json.loads(
        (CORPUS / "vectors/order-equivalent-submission.json").read_text(
            encoding="utf-8"
        )
    )
    vector = json.loads(
        (CORPUS / "vectors/request-fingerprint.json").read_text(
            encoding="utf-8"
        )
    )
    assert submission_fingerprint(submission) == vector["request_fingerprint"]
    assert submission_fingerprint(equivalent) == vector["request_fingerprint"]
    assert canonical_submission_bytes(submission) == canonical_submission_bytes(
        equivalent
    )


def _submission_denial_chain(
    case: dict[str, Any],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    chain = list(map(copy.deepcopy, approved_chain()))
    target_index = {"submission": 2, "result": 3, "event": 4}[
        case["target"]
    ]
    target: Any = chain[target_index]
    for part in case["path"][:-1]:
        target = target[part]
    final = case["path"][-1]
    if case["op"] == "delete":
        del target[final]
    else:
        target[final] = case["value"]
    return tuple(chain)  # type: ignore[return-value]


@pytest.mark.parametrize(
    "case",
    json.loads(
        (CORPUS / "cases/submission-denials.json").read_text(encoding="utf-8")
    ),
    ids=lambda case: case["id"],
)
def test_submission_denial_corpus_fails_closed(case: dict[str, Any]) -> None:
    with pytest.raises(PracticeConformanceFailure) as captured:
        PracticeContractValidator().validate_submission_chain(
            *_submission_denial_chain(case)
        )
    assert captured.value.code == case["expected_code"]
    assert len(captured.value.reference) <= 120
    assert "\n" not in captured.value.reference


def test_result_and_event_recursively_exclude_private_answers() -> None:
    result = approved_chain()[3]
    event = approved_chain()[4]
    serialized = json.dumps({"result": result, "event": event}, sort_keys=True)
    for private_name in (
        "correct_option_id",
        "correct_option_ids",
        '"answer"',
    ):
        assert private_name not in serialized
    event_serialized = json.dumps(event, sort_keys=True)
    for retained_only_name in (
        "selected_option_id",
        "selected_option_ids",
        "entered_value",
        '"feedback"',
    ):
        assert retained_only_name not in event_serialized


def test_result_and_event_require_canonical_utc_timestamps() -> None:
    chain = list(map(copy.deepcopy, approved_chain()))
    chain[3]["submitted_at"] = "2026-10-16T11:00:00-04:00"
    chain[4]["occurred_at"] = "2026-10-16T11:00:00-04:00"
    chain[4]["payload"]["completed_at"] = "2026-10-16T11:00:00-04:00"
    with pytest.raises(PracticeConformanceFailure) as captured:
        PracticeContractValidator().validate_submission_chain(*chain)
    assert captured.value.code == "assessment.practice.schema_invalid"
    assert captured.value.reference == "submitted_at"
