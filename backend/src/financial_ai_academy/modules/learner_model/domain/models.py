"""Deterministic lesson-completion projection rules."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import re
from uuid import UUID


class InvalidCompletionEvidence(ValueError):
    def __init__(self, reference: str) -> None:
        super().__init__("Completion evidence is inconsistent.")
        self.reference = reference


@dataclass(frozen=True, slots=True)
class SourceCompletionEvidence:
    event_id: str
    event_version: str
    occurred_at: datetime
    attempt_id: str
    evidence_id: str
    learner_id: str
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    assessment_id: str
    assessment_version: str
    definition_digest: str
    item_id: str
    item_version: str
    scoring_policy_id: str
    scoring_policy_version: str
    score: int
    max_score: int
    completed_at: datetime


@dataclass(frozen=True, slots=True)
class LessonCompletionProjection:
    learner_id: str
    placement_id: str
    completed: bool
    source_digest: str
    rebuilt_at: datetime
    history: tuple[SourceCompletionEvidence, ...]


def derive_lesson_completion(
    *,
    learner_id: str,
    placement_id: str,
    evidence: tuple[SourceCompletionEvidence, ...],
    rebuilt_at: datetime,
) -> LessonCompletionProjection:
    if rebuilt_at.tzinfo is None:
        raise InvalidCompletionEvidence("rebuilt_at")
    ordered = tuple(
        sorted(evidence, key=lambda item: (item.completed_at, item.event_id))
    )
    seen_events: set[str] = set()
    seen_attempts: set[str] = set()
    seen_evidence: set[str] = set()
    for item in ordered:
        if item.learner_id != learner_id:
            raise InvalidCompletionEvidence("learner_id")
        if item.placement_id != placement_id:
            raise InvalidCompletionEvidence("placement_id")
        if item.event_version != "1.0.0":
            raise InvalidCompletionEvidence("event_version")
        if (
            item.package_version != "1.1.0"
            or item.assessment_version != "1.0.0"
            or item.item_version != "1.0.0"
            or item.scoring_policy_id != "single-select-exact-match"
            or item.scoring_policy_version != "1.0.0"
        ):
            raise InvalidCompletionEvidence("version")
        if item.max_score != 1 or item.score not in {0, 1}:
            raise InvalidCompletionEvidence("score")
        if item.occurred_at != item.completed_at:
            raise InvalidCompletionEvidence("completed_at")
        if item.event_id in seen_events:
            raise InvalidCompletionEvidence("event_id")
        if item.attempt_id in seen_attempts:
            raise InvalidCompletionEvidence("attempt_id")
        if item.evidence_id in seen_evidence:
            raise InvalidCompletionEvidence("evidence_id")
        seen_events.add(item.event_id)
        seen_attempts.add(item.attempt_id)
        seen_evidence.add(item.evidence_id)
    digest_input = [
        {
            **asdict(item),
            "occurred_at": _timestamp(item.occurred_at),
            "completed_at": _timestamp(item.completed_at),
        }
        for item in ordered
    ]
    source_digest = hashlib.sha256(
        json.dumps(
            digest_input,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    return LessonCompletionProjection(
        learner_id=learner_id,
        placement_id=placement_id,
        completed=bool(ordered),
        source_digest=source_digest,
        rebuilt_at=rebuilt_at.astimezone(timezone.utc),
        history=ordered,
    )


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise InvalidCompletionEvidence("timestamp")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
_VERSION = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_DIGEST = re.compile(r"^[a-f0-9]{64}$")
_ITEM_POLICIES = {
    "single_select": "single-select-exact-match",
    "multiple_select": "multiple-select-exact-set",
    "numeric_entry": "numeric-exact-or-inclusive-range",
}


@dataclass(frozen=True, slots=True)
class SourcePracticeItemSummary:
    item_id: str
    item_version: str
    item_type: str
    scoring_policy_id: str
    scoring_policy_version: str
    score: int
    max_score: int
    correct: bool
    review_reference_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SourcePracticeAttempt:
    attempt_order: int
    event_id: str
    attempt_id: str
    evidence_id: str
    learner_id: str
    submission_id: str
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
    outcome: str
    item_summaries: tuple[SourcePracticeItemSummary, ...]
    completed_at: datetime


@dataclass(frozen=True, slots=True)
class SourcePracticeHistory:
    learner_id: str
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    definition_digest: str
    practice_id: str
    practice_version: str
    attempt_policy_id: str
    attempt_policy_version: str
    attempts: tuple[SourcePracticeAttempt, ...]


@dataclass(frozen=True, slots=True)
class PracticeHistoryProjection:
    learner_id: str
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    definition_digest: str
    practice_id: str
    practice_version: str
    attempt_policy_id: str
    attempt_policy_version: str
    source_digest: str
    rebuilt_at: datetime
    attempts: tuple[SourcePracticeAttempt, ...]


def derive_practice_history(
    *, source: SourcePracticeHistory, rebuilt_at: datetime
) -> PracticeHistoryProjection:
    if rebuilt_at.tzinfo is None:
        raise InvalidCompletionEvidence("rebuilt_at")
    _validate_practice_root(source)
    exact_events: dict[str, SourcePracticeAttempt] = {}
    identities: dict[str, set[str]] = {
        "attempt_id": set(),
        "evidence_id": set(),
        "submission_id": set(),
    }
    unique: list[SourcePracticeAttempt] = []
    for attempt in source.attempts:
        prior = exact_events.get(attempt.event_id)
        if prior is not None:
            if prior != attempt:
                raise InvalidCompletionEvidence("event_id")
            continue
        exact_events[attempt.event_id] = attempt
        for field, seen in identities.items():
            value = str(getattr(attempt, field))
            if value in seen:
                raise InvalidCompletionEvidence(field)
            seen.add(value)
        unique.append(attempt)
    ordered = tuple(sorted(unique, key=lambda item: item.attempt_order))
    if len(ordered) > 10:
        raise InvalidCompletionEvidence("attempts")
    expected_signature: tuple[tuple[object, ...], ...] | None = None
    for expected_order, attempt in enumerate(ordered, start=1):
        if attempt.attempt_order != expected_order:
            raise InvalidCompletionEvidence("attempt_order")
        _validate_practice_attempt(source, attempt)
        signature = tuple(
            (
                item.item_id,
                item.item_version,
                item.item_type,
                item.scoring_policy_id,
                item.scoring_policy_version,
                item.max_score,
            )
            for item in attempt.item_summaries
        )
        if expected_signature is None:
            expected_signature = signature
        elif signature != expected_signature:
            raise InvalidCompletionEvidence("item_signature")
    digest_input = [_practice_attempt_payload(item) for item in ordered]
    source_digest = hashlib.sha256(
        json.dumps(
            digest_input,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    return PracticeHistoryProjection(
        learner_id=source.learner_id,
        placement_id=source.placement_id,
        package_id=source.package_id,
        package_version=source.package_version,
        package_digest=source.package_digest,
        definition_digest=source.definition_digest,
        practice_id=source.practice_id,
        practice_version=source.practice_version,
        attempt_policy_id=source.attempt_policy_id,
        attempt_policy_version=source.attempt_policy_version,
        source_digest=source_digest,
        rebuilt_at=rebuilt_at.astimezone(timezone.utc),
        attempts=ordered,
    )


def _validate_practice_root(source: SourcePracticeHistory) -> None:
    try:
        UUID(source.learner_id)
    except (ValueError, AttributeError) as error:
        raise InvalidCompletionEvidence("learner_id") from error
    identifiers = (source.placement_id, source.package_id, source.practice_id)
    if (
        any(_ID.fullmatch(value) is None for value in identifiers)
        or _VERSION.fullmatch(source.package_version) is None
        or _DIGEST.fullmatch(source.package_digest) is None
        or _DIGEST.fullmatch(source.definition_digest) is None
        or source.practice_version != "1.0.0"
        or source.attempt_policy_id != "formative-retry"
        or source.attempt_policy_version != "1.0.0"
    ):
        raise InvalidCompletionEvidence("scope")


def _validate_practice_attempt(
    source: SourcePracticeHistory, attempt: SourcePracticeAttempt
) -> None:
    try:
        UUID(attempt.event_id)
        UUID(attempt.attempt_id)
        UUID(attempt.evidence_id)
        UUID(attempt.submission_id)
    except (ValueError, AttributeError) as error:
        raise InvalidCompletionEvidence("identity") from error
    if (
        attempt.learner_id != source.learner_id
        or attempt.placement_id != source.placement_id
        or attempt.package_id != source.package_id
        or attempt.package_version != source.package_version
        or attempt.package_digest != source.package_digest
        or attempt.definition_digest != source.definition_digest
        or attempt.practice_id != source.practice_id
        or attempt.practice_version != source.practice_version
        or attempt.attempt_policy_id != source.attempt_policy_id
        or attempt.attempt_policy_version != source.attempt_policy_version
        or attempt.completed_at.tzinfo is None
        or not 1 <= len(attempt.item_summaries) <= 20
    ):
        raise InvalidCompletionEvidence("attempt")
    seen_items: set[str] = set()
    score = 0
    max_score = 0
    for item in attempt.item_summaries:
        if (
            _ID.fullmatch(item.item_id) is None
            or item.item_id in seen_items
            or item.item_version != "1.0.0"
            or _ITEM_POLICIES.get(item.item_type) != item.scoring_policy_id
            or item.scoring_policy_version != "1.0.0"
            or item.max_score != 1
            or item.score not in {0, 1}
            or item.correct != (item.score == item.max_score)
            or len(item.review_reference_ids) > 8
            or len(set(item.review_reference_ids))
            != len(item.review_reference_ids)
            or any(
                _ID.fullmatch(reference) is None
                for reference in item.review_reference_ids
            )
            or (item.correct and bool(item.review_reference_ids))
            or (not item.correct and not item.review_reference_ids)
        ):
            raise InvalidCompletionEvidence("item")
        seen_items.add(item.item_id)
        score += item.score
        max_score += item.max_score
    expected_outcome = "all_correct" if score == max_score else "review_needed"
    if (
        attempt.score != score
        or attempt.max_score != max_score
        or attempt.outcome != expected_outcome
    ):
        raise InvalidCompletionEvidence("score")


def _practice_attempt_payload(attempt: SourcePracticeAttempt) -> dict[str, object]:
    return {
        "attempt_order": attempt.attempt_order,
        "event_id": attempt.event_id,
        "attempt_id": attempt.attempt_id,
        "evidence_id": attempt.evidence_id,
        "submission_id": attempt.submission_id,
        "score": attempt.score,
        "max_score": attempt.max_score,
        "outcome": attempt.outcome,
        "item_summaries": [
            {
                "item_id": item.item_id,
                "item_version": item.item_version,
                "item_type": item.item_type,
                "scoring_policy_id": item.scoring_policy_id,
                "scoring_policy_version": item.scoring_policy_version,
                "score": item.score,
                "max_score": item.max_score,
                "correct": item.correct,
                "review_reference_ids": list(item.review_reference_ids),
            }
            for item in attempt.item_summaries
        ],
        "completed_at": _timestamp(attempt.completed_at),
    }
