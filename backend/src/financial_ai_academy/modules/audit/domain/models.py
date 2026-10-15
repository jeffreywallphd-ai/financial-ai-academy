"""Append-oriented Assessment completion audit derivation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5


class InvalidAuditEvidence(ValueError):
    def __init__(self, reference: str) -> None:
        super().__init__("Audit source evidence is inconsistent.")
        self.reference = reference


@dataclass(frozen=True, slots=True)
class AuditableAssessmentEvent:
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
class AssessmentCompletionAuditRecord:
    audit_id: str
    event_id: str
    evidence_id: str
    attempt_id: str
    actor_id: str
    action: str
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    assessment_id: str
    assessment_version: str
    definition_digest: str
    occurred_at: datetime
    integrity_digest: str
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class AssessmentAuditBatch:
    source_digest: str
    records: tuple[AssessmentCompletionAuditRecord, ...]


def derive_assessment_audit_batch(
    *,
    learner_id: str,
    placement_id: str,
    events: tuple[AuditableAssessmentEvent, ...],
    recorded_at: datetime,
) -> AssessmentAuditBatch:
    if recorded_at.tzinfo is None:
        raise InvalidAuditEvidence("recorded_at")
    records: list[AssessmentCompletionAuditRecord] = []
    seen: set[str] = set()
    for event in sorted(events, key=lambda item: (item.occurred_at, item.event_id)):
        _validate_event(event, learner_id, placement_id)
        if event.event_id in seen:
            raise InvalidAuditEvidence("event_id")
        seen.add(event.event_id)
        integrity_digest = hashlib.sha256(
            json.dumps(
                _contract_value(event),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        records.append(
            AssessmentCompletionAuditRecord(
                audit_id=str(
                    uuid5(
                        NAMESPACE_URL,
                        f"financial-ai-academy:audit:{event.event_id}",
                    )
                ),
                event_id=event.event_id,
                evidence_id=event.evidence_id,
                attempt_id=event.attempt_id,
                actor_id=event.learner_id,
                action=event.event_type,
                placement_id=event.placement_id,
                package_id=event.package_id,
                package_version=event.package_version,
                package_digest=event.package_digest,
                assessment_id=event.assessment_id,
                assessment_version=event.assessment_version,
                definition_digest=event.definition_digest,
                occurred_at=event.occurred_at,
                integrity_digest=integrity_digest,
                recorded_at=recorded_at.astimezone(timezone.utc),
            )
        )
    source_digest = hashlib.sha256(
        json.dumps(
            [record.integrity_digest for record in records],
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return AssessmentAuditBatch(source_digest, tuple(records))


def _validate_event(
    event: AuditableAssessmentEvent,
    learner_id: str,
    placement_id: str,
) -> None:
    if event.learner_id != learner_id:
        raise InvalidAuditEvidence("learner_id")
    if event.placement_id != placement_id:
        raise InvalidAuditEvidence("placement_id")
    if (
        event.schema_version != "1.0.0"
        or event.event_type != "assessment.knowledge-check.completed"
        or event.event_version != "1.0.0"
        or event.owner != "assessment"
    ):
        raise InvalidAuditEvidence("event_version")
    if event.idempotency_key != event.evidence_id:
        raise InvalidAuditEvidence("idempotency_key")
    if event.occurred_at != event.completed_at:
        raise InvalidAuditEvidence("completed_at")
    if event.score not in {0, 1} or event.max_score != 1:
        raise InvalidAuditEvidence("score")


def _contract_value(event: AuditableAssessmentEvent) -> dict[str, object]:
    timestamp = _timestamp(event.occurred_at)
    return {
        "schema_version": event.schema_version,
        "event_id": event.event_id,
        "event_type": event.event_type,
        "event_version": event.event_version,
        "owner": event.owner,
        "occurred_at": timestamp,
        "idempotency_key": event.idempotency_key,
        "aggregate": {
            "aggregate_type": "knowledge_check_attempt",
            "aggregate_id": event.attempt_id,
        },
        "source": {"evidence_id": event.evidence_id},
        "payload": {
            "learner_id": event.learner_id,
            "placement_id": event.placement_id,
            "package_id": event.package_id,
            "package_version": event.package_version,
            "package_digest": event.package_digest,
            "assessment_id": event.assessment_id,
            "assessment_version": event.assessment_version,
            "definition_digest": event.definition_digest,
            "item_id": event.item_id,
            "item_version": event.item_version,
            "scoring_policy_id": event.scoring_policy_id,
            "scoring_policy_version": event.scoring_policy_version,
            "score": event.score,
            "max_score": event.max_score,
            "completed_at": _timestamp(event.completed_at),
        },
    }


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise InvalidAuditEvidence("timestamp")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
