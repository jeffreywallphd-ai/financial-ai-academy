"""Append-oriented Assessment completion audit derivation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from uuid import NAMESPACE_URL, UUID, uuid5


_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_VERSION = re.compile(
    r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$"
)
_DIGEST = re.compile(r"^[a-f0-9]{64}$")


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


@dataclass(frozen=True, slots=True)
class AuditableProjectEvent:
    schema_version: str
    event_id: str
    event_type: str
    event_version: str
    occurred_at: datetime
    evidence_id: str
    learner_id: str
    submission_id: str
    project_id: str
    snapshot_id: str
    snapshot_digest: str
    brief_id: str
    brief_version: str
    brief_digest: str
    placement_id: str
    placement_version: str
    placement_digest: str
    policy_id: str
    policy_version: str
    milestone_ids: tuple[str, ...]
    request_fingerprint: str
    occurrence: int
    submitted_at: datetime
    supersedes_submission_id: str | None


@dataclass(frozen=True, slots=True)
class ProjectCompletionAuditRecord:
    audit_id: str
    event_id: str
    evidence_id: str
    submission_id: str
    actor_id: str
    action: str
    project_id: str
    snapshot_id: str
    snapshot_digest: str
    brief_id: str
    brief_version: str
    brief_digest: str
    placement_id: str
    placement_version: str
    placement_digest: str
    policy_id: str
    policy_version: str
    occurrence: int
    supersedes_submission_id: str | None
    occurred_at: datetime
    integrity_digest: str
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class ProjectAuditBatch:
    source_digest: str
    records: tuple[ProjectCompletionAuditRecord, ...]


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


def derive_project_audit_batch(
    *,
    learner_id: str,
    project_id: str,
    events: tuple[AuditableProjectEvent, ...],
    recorded_at: datetime,
) -> ProjectAuditBatch:
    if recorded_at.tzinfo is None:
        raise InvalidAuditEvidence("recorded_at")
    records: list[ProjectCompletionAuditRecord] = []
    seen: set[str] = set()
    for event in sorted(events, key=lambda item: (item.occurrence, item.event_id)):
        _validate_project_event(event, learner_id, project_id)
        if event.event_id in seen:
            raise InvalidAuditEvidence("event_id")
        seen.add(event.event_id)
        integrity_digest = hashlib.sha256(
            json.dumps(
                _project_contract_value(event),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        records.append(
            ProjectCompletionAuditRecord(
                audit_id=str(
                    uuid5(
                        NAMESPACE_URL,
                        f"financial-ai-academy:audit:{event.event_id}",
                    )
                ),
                event_id=event.event_id,
                evidence_id=event.evidence_id,
                submission_id=event.submission_id,
                actor_id=event.learner_id,
                action=event.event_type,
                project_id=event.project_id,
                snapshot_id=event.snapshot_id,
                snapshot_digest=event.snapshot_digest,
                brief_id=event.brief_id,
                brief_version=event.brief_version,
                brief_digest=event.brief_digest,
                placement_id=event.placement_id,
                placement_version=event.placement_version,
                placement_digest=event.placement_digest,
                policy_id=event.policy_id,
                policy_version=event.policy_version,
                occurrence=event.occurrence,
                supersedes_submission_id=event.supersedes_submission_id,
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
    return ProjectAuditBatch(source_digest, tuple(records))


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


def _validate_project_event(
    event: AuditableProjectEvent,
    learner_id: str,
    project_id: str,
) -> None:
    try:
        UUID(event.learner_id)
    except (ValueError, AttributeError) as error:
        raise InvalidAuditEvidence("learner_id") from error
    identifiers = (
        event.event_id,
        event.evidence_id,
        event.submission_id,
        event.project_id,
        event.snapshot_id,
        event.brief_id,
        event.placement_id,
        event.policy_id,
        *event.milestone_ids,
    )
    versions = (event.brief_version, event.placement_version)
    digests = (
        event.snapshot_digest,
        event.brief_digest,
        event.placement_digest,
        event.request_fingerprint,
    )
    if event.learner_id != learner_id:
        raise InvalidAuditEvidence("learner_id")
    if event.project_id != project_id:
        raise InvalidAuditEvidence("project_id")
    if (
        event.schema_version != "1.0.0"
        or event.event_type != "assessment.project.completed"
        or event.event_version != "1.0.0"
        or event.policy_id != "assessment-project-closure"
        or event.policy_version != "1.0.0"
        or any(_ID.fullmatch(value) is None for value in identifiers)
        or any(_VERSION.fullmatch(value) is None for value in versions)
        or any(_DIGEST.fullmatch(value) is None for value in digests)
        or event.occurrence < 1
        or not 1 <= len(event.milestone_ids) <= 20
        or len(set(event.milestone_ids)) != len(event.milestone_ids)
        or event.occurred_at.tzinfo is None
        or event.submitted_at.tzinfo is None
        or event.occurred_at < event.submitted_at
    ):
        raise InvalidAuditEvidence("event_version")
    if (
        event.supersedes_submission_id is not None
        and _ID.fullmatch(event.supersedes_submission_id) is None
    ):
        raise InvalidAuditEvidence("supersedes_submission_id")


def _project_contract_value(event: AuditableProjectEvent) -> dict[str, object]:
    payload: dict[str, object] = {
        "evidence_id": event.evidence_id,
        "submission_id": event.submission_id,
        "project_id": event.project_id,
        "snapshot_id": event.snapshot_id,
        "snapshot_digest": event.snapshot_digest,
        "brief_id": event.brief_id,
        "brief_version": event.brief_version,
        "brief_digest": event.brief_digest,
        "placement_id": event.placement_id,
        "placement_version": event.placement_version,
        "placement_digest": event.placement_digest,
        "policy_id": event.policy_id,
        "policy_version": event.policy_version,
        "milestone_ids": list(event.milestone_ids),
        "request_fingerprint": event.request_fingerprint,
        "occurrence": event.occurrence,
        "submitted_at": _timestamp(event.submitted_at),
    }
    if event.supersedes_submission_id is not None:
        payload["supersedes_submission_id"] = event.supersedes_submission_id
    return {
        "schema_version": event.schema_version,
        "event_id": event.event_id,
        "event_type": event.event_type,
        "event_version": event.event_version,
        "occurred_at": _timestamp(event.occurred_at),
        "payload": payload,
    }


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise InvalidAuditEvidence("timestamp")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
