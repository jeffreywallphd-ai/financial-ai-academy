"""Immutable values for versioned formative practice definitions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, TypeAlias


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
