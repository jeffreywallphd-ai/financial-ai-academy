"""Deterministic lesson-completion projection rules."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone


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
