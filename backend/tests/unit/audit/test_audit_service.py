from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from financial_ai_academy.modules.assessment.public import (
    KnowledgeCheckCompletionEvent,
)
from financial_ai_academy.modules.audit.adapters.assessment_gateway import (
    AssessmentAuditEventSource,
)
from financial_ai_academy.modules.audit.application.service import AuditService
from financial_ai_academy.modules.audit.domain.models import (
    AssessmentCompletionAuditRecord,
    AuditableAssessmentEvent,
)
from financial_ai_academy.modules.audit.ports.repositories import (
    AuditRecordConflict,
)
from financial_ai_academy.modules.audit.public import (
    AuditError,
    AuditErrorCode,
    ReconcileLessonCompletionAuditRequest,
)


LEARNER_ID = "11111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)
PACKAGE_DIGEST = "7cf84bc2f7483d9131db315260b3812f3ea29821bf296571c0c7e38f05b536bc"
DEFINITION_DIGEST = "98e941f9b53ef429cb6d359246ddb9812e354db2a9381a2ee180ed5758343d2b"


def event() -> AuditableAssessmentEvent:
    return AuditableAssessmentEvent(
        schema_version="1.0.0",
        event_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        event_type="assessment.knowledge-check.completed",
        event_version="1.0.0",
        owner="assessment",
        occurred_at=NOW,
        idempotency_key="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        attempt_id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
        evidence_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        learner_id=LEARNER_ID,
        placement_id="intro-risk-return",
        package_id="intro-risk-return",
        package_version="1.1.0",
        package_digest=PACKAGE_DIGEST,
        assessment_id="risk-return-check-1",
        assessment_version="1.0.0",
        definition_digest=DEFINITION_DIGEST,
        item_id="risk-return-tradeoff",
        item_version="1.0.0",
        scoring_policy_id="single-select-exact-match",
        scoring_policy_version="1.0.0",
        score=1,
        max_score=1,
        completed_at=NOW,
    )


class Source:
    def __init__(self, values: tuple[AuditableAssessmentEvent, ...]) -> None:
        self.values = values

    def list_for_lesson(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[AuditableAssessmentEvent, ...]:
        return self.values


class Repository:
    def __init__(self, *, conflict: bool = False, fail: bool = False) -> None:
        self.records: list[tuple[AssessmentCompletionAuditRecord, ...]] = []
        self.conflict = conflict
        self.fail = fail

    def append_assessment_completion_records(
        self, records: tuple[AssessmentCompletionAuditRecord, ...]
    ) -> None:
        if self.conflict:
            raise AuditRecordConflict
        if self.fail:
            raise RuntimeError("private audit storage")
        self.records.append(records)


class Clock:
    def now(self) -> datetime:
        return NOW


def service(
    values: tuple[AuditableAssessmentEvent, ...],
    repository: Repository | None = None,
) -> AuditService:
    return AuditService(Source(values), repository or Repository(), Clock())


def request() -> ReconcileLessonCompletionAuditRequest:
    return ReconcileLessonCompletionAuditRequest(
        LEARNER_ID, "intro-risk-return"
    )


def test_empty_and_exact_reconciliation_are_bounded() -> None:
    empty = service(()).reconcile_lesson_completion(request())
    assert empty.reconciled_event_count == 0
    repository = Repository()
    exact = service((event(),), repository).reconcile_lesson_completion(request())
    assert exact.reconciled_event_count == 1
    record = repository.records[0][0]
    assert record.actor_id == LEARNER_ID
    assert record.evidence_id == event().evidence_id
    assert record.action == "assessment.knowledge-check.completed"
    assert len(record.integrity_digest) == 64


@pytest.mark.parametrize(
    "invalid",
    [
        replace(event(), learner_id="dddddddd-dddd-4ddd-8ddd-dddddddddddd"),
        replace(event(), event_version="2.0.0"),
        replace(event(), idempotency_key="eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"),
    ],
)
def test_inconsistent_source_fails_before_audit_append(
    invalid: AuditableAssessmentEvent,
) -> None:
    repository = Repository()
    with pytest.raises(AuditError) as captured:
        service((invalid,), repository).reconcile_lesson_completion(request())
    assert captured.value.code is AuditErrorCode.INCONSISTENT_EVIDENCE
    assert repository.records == []


def test_conflict_and_storage_failure_are_bounded() -> None:
    with pytest.raises(AuditError) as conflict:
        service((event(),), Repository(conflict=True)).reconcile_lesson_completion(
            request()
        )
    assert conflict.value.code is AuditErrorCode.CONFLICT
    with pytest.raises(AuditError) as unavailable:
        service((event(),), Repository(fail=True)).reconcile_lesson_completion(
            request()
        )
    assert unavailable.value.code is AuditErrorCode.UNAVAILABLE
    assert "private" not in unavailable.value.safe_message


class Assessment:
    def read_completed_knowledge_checks(
        self, _request: object
    ) -> tuple[KnowledgeCheckCompletionEvent, ...]:
        value = event()
        return (
            KnowledgeCheckCompletionEvent(
                schema_version=value.schema_version,
                event_id=value.event_id,
                event_type=value.event_type,
                event_version=value.event_version,
                owner=value.owner,
                occurred_at=value.occurred_at,
                idempotency_key=value.idempotency_key,
                attempt_id=value.attempt_id,
                evidence_id=value.evidence_id,
                learner_id=value.learner_id,
                placement_id=value.placement_id,
                package_id=value.package_id,
                package_version=value.package_version,
                package_digest=value.package_digest,
                assessment_id=value.assessment_id,
                assessment_version=value.assessment_version,
                definition_digest=value.definition_digest,
                item_id=value.item_id,
                item_version=value.item_version,
                scoring_policy_id=value.scoring_policy_id,
                scoring_policy_version=value.scoring_policy_version,
                score=value.score,
                max_score=value.max_score,
                completed_at=value.completed_at,
            ),
        )


def test_assessment_adapter_maps_only_the_public_event() -> None:
    values = AssessmentAuditEventSource(Assessment()).list_for_lesson(
        learner_id=LEARNER_ID,
        placement_id="intro-risk-return",
    )
    assert values == (event(),)
