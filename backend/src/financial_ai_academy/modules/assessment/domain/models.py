"""Pure deterministic Assessment values and scoring policy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from ..public import KnowledgeCheckFeedback, KnowledgeCheckResult


@dataclass(frozen=True, slots=True)
class AssessmentOption:
    option_id: str
    label: str


@dataclass(frozen=True, slots=True)
class AssessmentDefinition:
    assessment_id: str
    assessment_version: str
    definition_digest: str
    item_type: str
    item_id: str
    item_version: str
    scoring_policy_id: str
    scoring_policy_version: str
    prompt: str
    options: tuple[AssessmentOption, ...]
    correct_option_id: str
    correct_feedback: KnowledgeCheckFeedback
    incorrect_feedback: KnowledgeCheckFeedback


@dataclass(frozen=True, slots=True)
class ScoreOutcome:
    score: int
    max_score: int
    correct: bool
    feedback: KnowledgeCheckFeedback


def score_single_select(
    definition: AssessmentDefinition, selected_option_id: str
) -> ScoreOutcome:
    declared = {option.option_id for option in definition.options}
    if selected_option_id not in declared:
        raise ValueError("selected option is not declared")
    correct = selected_option_id == definition.correct_option_id
    return ScoreOutcome(
        score=1 if correct else 0,
        max_score=1,
        correct=correct,
        feedback=(
            definition.correct_feedback
            if correct
            else definition.incorrect_feedback
        ),
    )


@dataclass(frozen=True, slots=True)
class AssessmentSubmissionCandidate:
    result: KnowledgeCheckResult
    request_fingerprint: str
    event_id: str
    event: Mapping[str, object]
    occurred_at: datetime

