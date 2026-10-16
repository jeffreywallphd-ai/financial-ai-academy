from __future__ import annotations

import copy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.assessment.adapters.practice_contract import (
    ContractPracticeDefinitionAdapter,
)
from financial_ai_academy.modules.assessment.adapters.practice_submission_contract import (
    ContractPracticeSubmissionAdapter,
)
from financial_ai_academy.modules.assessment.domain.practice import (
    NumericPracticeAnswer,
    NumericPracticeItem,
    PracticePresentationContext,
)
from financial_ai_academy.modules.assessment.ports.practice_submission import (
    PracticeSubmissionFailure,
)


REPOSITORY = Path(__file__).resolve().parents[4]
SCHEMAS = REPOSITORY / "contracts/learning/assessment/practice/v1"
APPROVED = REPOSITORY / "contracts/compatibility/assessment-practice/v1/approved"
VECTORS = REPOSITORY / "contracts/compatibility/assessment-practice/v1/vectors"
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
ATTEMPT_ID = "33333333-3333-4333-8333-333333333333"
EVIDENCE_ID = "44444444-4444-4444-8444-444444444444"
EVENT_ID = "55555555-5555-4555-8555-555555555555"
SUBMITTED_AT = datetime(2026, 10, 16, 15, 0, tzinfo=timezone.utc)


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def setup() -> tuple[
    ContractPracticeSubmissionAdapter,
    object,
    PracticePresentationContext,
    dict[str, object],
]:
    definition = ContractPracticeDefinitionAdapter(SCHEMAS).parse(
        (APPROVED / "definition.json").read_bytes()
    )
    submission = load(APPROVED / "submission.json")
    context = PracticePresentationContext(
        placement_id=str(submission["placement_id"]),
        package_id=str(submission["package_id"]),
        package_version=str(submission["package_version"]),
        package_digest=str(submission["package_digest"]),
    )
    return ContractPracticeSubmissionAdapter(SCHEMAS), definition, context, submission


def score(
    submission: dict[str, object] | None = None,
    *,
    definition: object | None = None,
    submitted_at: datetime = SUBMITTED_AT,
):
    adapter, default_definition, context, default_submission = setup()
    document = submission or default_submission
    return adapter.parse_and_score(
        json.dumps(document).encode("utf-8"),
        definition or default_definition,  # type: ignore[arg-type]
        context,
        learner_id=LEARNER_ID,
        attempt_id=ATTEMPT_ID,
        evidence_id=EVIDENCE_ID,
        event_id=EVENT_ID,
        submitted_at=submitted_at,
    )


def test_approved_submission_matches_fixed_result_and_event() -> None:
    candidate = score()
    document = ContractPracticeSubmissionAdapter.to_result_document(
        candidate.result
    )
    assert document == load(APPROVED / "result.json")
    assert candidate.event == load(APPROVED / "completion-event.json")
    assert candidate.result.score == 2
    assert candidate.result.max_score == 3
    assert candidate.result.outcome == "review_needed"
    assert [item.response.item_id for item in candidate.result.item_results] == [
        "risk-meaning",
        "diversification-actions",
        "simple-growth",
    ]


def test_request_and_multiple_selection_order_do_not_change_identity_or_score() -> None:
    equivalent = load(VECTORS / "order-equivalent-submission.json")
    original = score()
    reordered = score(equivalent)
    assert reordered.request_fingerprint == original.request_fingerprint
    assert reordered.result.score == original.result.score
    assert reordered.result.item_results == original.result.item_results


def test_exact_multiple_set_can_make_the_whole_activity_correct() -> None:
    _, _, _, submission = setup()
    changed = copy.deepcopy(submission)
    multiple = next(
        response
        for response in changed["responses"]  # type: ignore[union-attr]
        if response["item_type"] == "multiple_select"
    )
    multiple["selected_option_ids"] = ["more-types", "more-issuers"]
    candidate = score(changed)
    assert candidate.result.score == 3
    assert candidate.result.outcome == "all_correct"


@pytest.mark.parametrize(
    ("item_type", "field", "value", "expected_score"),
    [
        ("single_select", "selected_option_id", "guarantee", 1),
        ("multiple_select", "selected_option_ids", ["more-types"], 2),
        ("numeric_entry", "entered_value", "104.99", 1),
    ],
)
def test_each_incorrect_branch_selects_only_its_reviewed_feedback(
    item_type: str, field: str, value: object, expected_score: int
) -> None:
    _, _, _, submission = setup()
    changed = copy.deepcopy(submission)
    response = next(
        item
        for item in changed["responses"]  # type: ignore[union-attr]
        if item["item_type"] == item_type
    )
    response[field] = value
    candidate = score(changed)
    assert candidate.result.score == expected_score
    outcome = next(
        item
        for item in candidate.result.item_results
        if item.response.item_type == item_type
    )
    assert outcome.correct is False
    assert outcome.feedback.feedback_id.endswith("review")


@pytest.mark.parametrize(
    ("value", "code"),
    [
        ("105.0", "assessment.practice.invalid_response"),
        ("0105.00", "assessment.practice.schema_invalid"),
        ("1.05e2", "assessment.practice.schema_invalid"),
        ("105,00", "assessment.practice.schema_invalid"),
        ("-0.00", "assessment.practice.invalid_response"),
        ("-105.00", "assessment.practice.invalid_response"),
    ],
)
def test_numeric_response_requires_canonical_declared_scale(
    value: str, code: str
) -> None:
    _, _, _, submission = setup()
    changed = copy.deepcopy(submission)
    numeric = next(
        item
        for item in changed["responses"]  # type: ignore[union-attr]
        if item["item_type"] == "numeric_entry"
    )
    numeric["entered_value"] = value
    with pytest.raises(PracticeSubmissionFailure) as captured:
        score(changed)
    assert captured.value.code == code


def test_inclusive_range_endpoints_are_scored_with_decimal() -> None:
    _, definition, _, submission = setup()
    items = list(definition.items)  # type: ignore[union-attr]
    numeric = items[2]
    assert isinstance(numeric, NumericPracticeItem)
    items[2] = replace(
        numeric,
        answer=NumericPracticeAnswer(
            mode="inclusive_range",
            lower=numeric.answer.value,
            upper=numeric.answer.value,
        ),
    )
    ranged = replace(definition, items=tuple(items))  # type: ignore[arg-type]
    assert score(submission, definition=ranged).result.item_results[2].correct


@pytest.mark.parametrize(
    "mutation",
    ["missing", "duplicate", "extra", "unknown-option", "wrong-type"],
)
def test_incomplete_extra_or_incompatible_response_sets_fail_closed(
    mutation: str,
) -> None:
    _, _, _, submission = setup()
    changed = copy.deepcopy(submission)
    responses = changed["responses"]  # type: ignore[assignment]
    if mutation == "missing":
        responses.pop()
    elif mutation == "duplicate":
        responses.append(copy.deepcopy(responses[0]))
    elif mutation == "extra":
        extra = copy.deepcopy(responses[0])
        extra["item_id"] = "extra-item"
        responses.append(extra)
    elif mutation == "unknown-option":
        next(
            item for item in responses if item["item_type"] == "single_select"
        )["selected_option_id"] = "not-declared"
    else:
        next(
            item for item in responses if item["item_type"] == "single_select"
        )["item_type"] = "numeric_entry"
    with pytest.raises(PracticeSubmissionFailure):
        score(changed)


def test_definition_order_not_fixture_order_controls_result_order() -> None:
    _, definition, _, submission = setup()
    reordered = replace(
        definition, items=tuple(reversed(definition.items))  # type: ignore[union-attr]
    )
    candidate = score(submission, definition=reordered)
    assert [item.response.item_id for item in candidate.result.item_results] == [
        "simple-growth",
        "diversification-actions",
        "risk-meaning",
    ]


def test_result_and_event_do_not_expose_private_answers() -> None:
    candidate = score()
    serialized = json.dumps(
        {
            "result": ContractPracticeSubmissionAdapter.to_result_document(
                candidate.result
            ),
            "event": candidate.event,
        },
        sort_keys=True,
    )
    for private_name in (
        "correct_option_id",
        "correct_option_ids",
        '"answer"',
    ):
        assert private_name not in serialized
    event_serialized = json.dumps(candidate.event, sort_keys=True)
    for retained_only_name in (
        "selected_option_id",
        "selected_option_ids",
        "entered_value",
        '"feedback"',
    ):
        assert retained_only_name not in event_serialized


def test_server_metadata_requires_utc_and_valid_opaque_ids() -> None:
    with pytest.raises(PracticeSubmissionFailure) as captured:
        score(submitted_at=datetime(2026, 10, 16, 15, 0))
    assert captured.value.code == "assessment.practice.invalid_server_metadata"

    non_utc = datetime(
        2026,
        10,
        16,
        11,
        0,
        tzinfo=timezone(-timedelta(hours=4)),
    )
    with pytest.raises(PracticeSubmissionFailure) as non_utc_error:
        score(submitted_at=non_utc)
    assert non_utc_error.value.code == (
        "assessment.practice.invalid_server_metadata"
    )

    adapter, definition, context, submission = setup()
    with pytest.raises(PracticeSubmissionFailure) as invalid_id:
        adapter.parse_and_score(
            json.dumps(submission).encode(),
            definition,  # type: ignore[arg-type]
            context,
            learner_id="caller-selected",
            attempt_id=ATTEMPT_ID,
            evidence_id=EVIDENCE_ID,
            event_id=EVENT_ID,
            submitted_at=SUBMITTED_AT,
        )
    assert invalid_id.value.code == "assessment.practice.schema_invalid"
