"""Immutable values for versioned formative practice definitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import re
from typing import Literal, Mapping, TypeAlias


@dataclass(frozen=True, slots=True)
class PracticeResourceReference:
    resource_id: str
    resource_version: str
    resource_digest: str
    title: str


@dataclass(frozen=True, slots=True)
class PracticeAttemptPolicy:
    policy_id: str
    policy_version: str
    max_attempts: int
    resume_allowed: bool
    history_visible: bool


@dataclass(frozen=True, slots=True)
class PracticeOption:
    option_id: str
    label: str


@dataclass(frozen=True, slots=True)
class PracticeFeedback:
    feedback_id: str
    text: str
    review_reference_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PracticeFeedbackPair:
    correct: PracticeFeedback
    incorrect: PracticeFeedback


@dataclass(frozen=True, slots=True)
class PracticeScoringPolicy:
    policy_id: str
    policy_version: str
    max_score: int


@dataclass(frozen=True, slots=True)
class SingleSelectPracticeItem:
    item_id: str
    item_version: str
    item_type: Literal["single_select"]
    prompt: str
    scoring_policy: PracticeScoringPolicy
    options: tuple[PracticeOption, ...]
    correct_option_id: str
    feedback: PracticeFeedbackPair


@dataclass(frozen=True, slots=True)
class MultipleSelectPracticeItem:
    item_id: str
    item_version: str
    item_type: Literal["multiple_select"]
    prompt: str
    scoring_policy: PracticeScoringPolicy
    options: tuple[PracticeOption, ...]
    correct_option_ids: tuple[str, ...]
    feedback: PracticeFeedbackPair


@dataclass(frozen=True, slots=True)
class NumericPracticeResponse:
    scale: int
    unit_label: str
    allow_negative: bool


@dataclass(frozen=True, slots=True)
class NumericPracticeAnswer:
    mode: Literal["exact", "inclusive_range"]
    value: Decimal | None = None
    lower: Decimal | None = None
    upper: Decimal | None = None


@dataclass(frozen=True, slots=True)
class NumericPracticeItem:
    item_id: str
    item_version: str
    item_type: Literal["numeric_entry"]
    prompt: str
    scoring_policy: PracticeScoringPolicy
    response: NumericPracticeResponse
    answer: NumericPracticeAnswer
    feedback: PracticeFeedbackPair


PracticeItem: TypeAlias = (
    SingleSelectPracticeItem | MultipleSelectPracticeItem | NumericPracticeItem
)


@dataclass(frozen=True, slots=True)
class PracticeDefinition:
    practice_id: str
    practice_version: str
    definition_digest: str
    title: str
    purpose: str
    instructions: str
    attempt_policy: PracticeAttemptPolicy
    source_references: tuple[PracticeResourceReference, ...]
    review_references: tuple[PracticeResourceReference, ...]
    items: tuple[PracticeItem, ...]


@dataclass(frozen=True, slots=True)
class PracticePresentationContext:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str


@dataclass(frozen=True, slots=True)
class SelectPracticePresentationItem:
    item_id: str
    item_version: str
    item_type: Literal["single_select", "multiple_select"]
    prompt: str
    scoring_policy_id: str
    scoring_policy_version: str
    max_score: int
    options: tuple[PracticeOption, ...]


@dataclass(frozen=True, slots=True)
class NumericPracticePresentationItem:
    item_id: str
    item_version: str
    item_type: Literal["numeric_entry"]
    prompt: str
    scoring_policy_id: str
    scoring_policy_version: str
    max_score: int
    scale: int
    unit_label: str
    allow_negative: bool


PracticePresentationItem: TypeAlias = (
    SelectPracticePresentationItem | NumericPracticePresentationItem
)


@dataclass(frozen=True, slots=True)
class PracticePresentation:
    schema_version: str
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    definition_digest: str
    practice_id: str
    practice_version: str
    title: str
    purpose: str
    instructions: str
    attempt_policy: PracticeAttemptPolicy
    source_references: tuple[PracticeResourceReference, ...]
    review_references: tuple[PracticeResourceReference, ...]
    items: tuple[PracticePresentationItem, ...]


@dataclass(frozen=True, slots=True)
class SingleSelectPracticeResponse:
    item_id: str
    item_version: str
    item_type: Literal["single_select"]
    scoring_policy_id: str
    scoring_policy_version: str
    selected_option_id: str


@dataclass(frozen=True, slots=True)
class MultipleSelectPracticeResponse:
    item_id: str
    item_version: str
    item_type: Literal["multiple_select"]
    scoring_policy_id: str
    scoring_policy_version: str
    selected_option_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NumericEntryPracticeResponse:
    item_id: str
    item_version: str
    item_type: Literal["numeric_entry"]
    scoring_policy_id: str
    scoring_policy_version: str
    entered_value: str


PracticeResponse: TypeAlias = (
    SingleSelectPracticeResponse
    | MultipleSelectPracticeResponse
    | NumericEntryPracticeResponse
)


@dataclass(frozen=True, slots=True)
class PracticeItemOutcome:
    response: PracticeResponse
    score: int
    max_score: int
    correct: bool
    feedback: PracticeFeedback


@dataclass(frozen=True, slots=True)
class PracticeAggregateOutcome:
    item_results: tuple[PracticeItemOutcome, ...]
    score: int
    max_score: int
    outcome: Literal["all_correct", "review_needed"]
    review_reference_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PracticeResult:
    schema_version: str
    attempt_id: str
    evidence_id: str
    learner_id: str
    submission_id: str
    request_fingerprint: str
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    definition_digest: str
    practice_id: str
    practice_version: str
    attempt_policy_id: str
    attempt_policy_version: str
    score: int
    max_score: int
    outcome: Literal["all_correct", "review_needed"]
    review_reference_ids: tuple[str, ...]
    item_results: tuple[PracticeItemOutcome, ...]
    submitted_at: datetime


@dataclass(frozen=True, slots=True)
class PracticeSubmissionCandidate:
    result: PracticeResult
    request_fingerprint: str
    event_id: str
    event: Mapping[str, object]
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class PracticeScope:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    definition_digest: str
    practice_id: str
    practice_version: str
    attempt_policy_id: str
    attempt_policy_version: str


@dataclass(frozen=True, slots=True)
class PracticeDraftSave:
    scope: PracticeScope
    expected_revision: int
    responses: tuple[PracticeResponse, ...]
    response_fingerprint: str


@dataclass(frozen=True, slots=True)
class PracticeDraft:
    scope: PracticeScope
    responses: tuple[PracticeResponse, ...]
    revision: int
    saved_at: datetime
    response_fingerprint: str


@dataclass(frozen=True, slots=True)
class PracticeRetryState:
    scope: PracticeScope
    attempts_used: int
    max_attempts: int
    attempts_remaining: int
    can_retry: bool
    state: Literal["available", "exhausted"]


@dataclass(frozen=True, slots=True)
class PracticeCompletionItemScore:
    item_id: str
    item_version: str
    item_type: Literal["single_select", "multiple_select", "numeric_entry"]
    scoring_policy_id: str
    scoring_policy_version: str
    score: int
    max_score: int


@dataclass(frozen=True, slots=True)
class PracticeCompletionEvent:
    schema_version: str
    event_id: str
    event_type: str
    event_version: str
    owner: str
    occurred_at: datetime
    idempotency_key: str
    attempt_id: str
    evidence_id: str
    learner_id: str
    submission_id: str
    scope: PracticeScope
    score: int
    max_score: int
    outcome: Literal["all_correct", "review_needed"]
    item_scores: tuple[PracticeCompletionItemScore, ...]
    completed_at: datetime


@dataclass(frozen=True, slots=True)
class OrderedPracticeCompletionEvent:
    attempt_order: int
    event: PracticeCompletionEvent


class PracticeScoringError(ValueError):
    def __init__(self, reference: str) -> None:
        super().__init__("Practice response was rejected.")
        self.reference = reference


_DECIMAL_RE = re.compile(r"^-?(0|[1-9][0-9]*)(?:\.([0-9]{1,6}))?$")


def score_practice(
    definition: PracticeDefinition,
    responses: tuple[PracticeResponse, ...],
) -> PracticeAggregateOutcome:
    """Validate and score one complete response set in definition order."""

    by_id = _validated_response_map(definition, responses)
    if set(by_id) != {item.item_id for item in definition.items}:
        raise PracticeScoringError("responses")

    results: list[PracticeItemOutcome] = []
    review_ids: list[str] = []
    for item in definition.items:
        response = by_id[item.item_id]
        _validate_response_identity(item, response)
        correct = _score_item(item, response)
        feedback = item.feedback.correct if correct else item.feedback.incorrect
        results.append(
            PracticeItemOutcome(
                response=response,
                score=1 if correct else 0,
                max_score=item.scoring_policy.max_score,
                correct=correct,
                feedback=feedback,
            )
        )
        for reference_id in feedback.review_reference_ids:
            if reference_id not in review_ids:
                review_ids.append(reference_id)

    score = sum(result.score for result in results)
    maximum = sum(result.max_score for result in results)
    return PracticeAggregateOutcome(
        item_results=tuple(results),
        score=score,
        max_score=maximum,
        outcome="all_correct" if score == maximum else "review_needed",
        review_reference_ids=tuple(review_ids),
    )


def validate_practice_response_subset(
    definition: PracticeDefinition,
    responses: tuple[PracticeResponse, ...],
) -> None:
    """Validate a draft subset without requiring or exposing a score."""

    _validated_response_map(definition, responses)


def _validated_response_map(
    definition: PracticeDefinition,
    responses: tuple[PracticeResponse, ...],
) -> dict[str, PracticeResponse]:
    items = {item.item_id: item for item in definition.items}
    by_id: dict[str, PracticeResponse] = {}
    for response in responses:
        if response.item_id in by_id:
            raise PracticeScoringError("responses")
        item = items.get(response.item_id)
        if item is None:
            raise PracticeScoringError(f"responses.{response.item_id}")
        _validate_response_identity(item, response)
        _score_item(item, response)
        by_id[response.item_id] = response
    return by_id


def _validate_response_identity(
    item: PracticeItem, response: PracticeResponse
) -> None:
    if (
        response.item_version != item.item_version
        or response.item_type != item.item_type
        or response.scoring_policy_id != item.scoring_policy.policy_id
        or response.scoring_policy_version != item.scoring_policy.policy_version
    ):
        raise PracticeScoringError(f"responses.{item.item_id}")


def _score_item(item: PracticeItem, response: PracticeResponse) -> bool:
    if isinstance(item, SingleSelectPracticeItem):
        if not isinstance(response, SingleSelectPracticeResponse):
            raise PracticeScoringError(f"responses.{item.item_id}")
        declared = {option.option_id for option in item.options}
        if response.selected_option_id not in declared:
            raise PracticeScoringError(f"responses.{item.item_id}")
        return response.selected_option_id == item.correct_option_id

    if isinstance(item, MultipleSelectPracticeItem):
        if not isinstance(response, MultipleSelectPracticeResponse):
            raise PracticeScoringError(f"responses.{item.item_id}")
        selected = response.selected_option_ids
        if len(selected) != len(set(selected)):
            raise PracticeScoringError(f"responses.{item.item_id}")
        declared = {option.option_id for option in item.options}
        if not set(selected).issubset(declared):
            raise PracticeScoringError(f"responses.{item.item_id}")
        return set(selected) == set(item.correct_option_ids)

    if not isinstance(response, NumericEntryPracticeResponse):
        raise PracticeScoringError(f"responses.{item.item_id}")
    match = _DECIMAL_RE.fullmatch(response.entered_value)
    if match is None or len(match.group(2) or "") != item.response.scale:
        raise PracticeScoringError(f"responses.{item.item_id}")
    value = Decimal(response.entered_value)
    if response.entered_value.startswith("-0") and value == 0:
        raise PracticeScoringError(f"responses.{item.item_id}")
    if not item.response.allow_negative and value < 0:
        raise PracticeScoringError(f"responses.{item.item_id}")
    if item.answer.mode == "exact":
        return value == item.answer.value
    assert item.answer.lower is not None and item.answer.upper is not None
    return item.answer.lower <= value <= item.answer.upper
