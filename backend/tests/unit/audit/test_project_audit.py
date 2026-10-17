from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.assessment.adapters.project_submission_contract import (
    ContractProjectSubmissionAdapter,
)
from financial_ai_academy.modules.assessment.domain.project_submission import (
    ProjectEvidenceMetadata,
)
from financial_ai_academy.modules.assessment.public import (
    OrderedProjectCompletionEvent,
)
from financial_ai_academy.modules.audit.adapters.assessment_gateway import (
    AssessmentAuditEventSource,
)

from financial_ai_academy.modules.audit.application.service import AuditService
from financial_ai_academy.modules.audit.domain.models import (
    AuditableProjectEvent,
    ProjectCompletionAuditRecord,
)
from financial_ai_academy.modules.audit.ports.repositories import (
    AuditRecordConflict,
)
from financial_ai_academy.modules.audit.public import (
    AuditError,
    AuditErrorCode,
    ReconcileProjectCompletionAuditRequest,
)


LEARNER_ID = "11111111-1111-4111-8111-111111111111"
PROJECT_ID = "project-retirement-plan"
NOW = datetime(2026, 10, 17, 3, 30, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[4]


def event() -> AuditableProjectEvent:
    return AuditableProjectEvent(
        schema_version="1.0.0",
        event_id="event-retirement-01",
        event_type="assessment.project.completed",
        event_version="1.0.0",
        occurred_at=NOW,
        evidence_id="evidence-retirement-01",
        learner_id=LEARNER_ID,
        submission_id="submission-retirement-01",
        project_id=PROJECT_ID,
        snapshot_id="snapshot-retirement-plan-01",
        snapshot_digest="2" * 64,
        brief_id="brief-retirement-plan",
        brief_version="1.0.0",
        brief_digest="4" * 64,
        placement_id="placement-retirement-project",
        placement_version="1.0.0",
        placement_digest="6" * 64,
        policy_id="assessment-project-closure",
        policy_version="1.0.0",
        milestone_ids=("identify-assumptions", "compare-scenarios"),
        request_fingerprint="7" * 64,
        occurrence=1,
        submitted_at=NOW,
        supersedes_submission_id=None,
    )


class Source:
    def __init__(self, values: tuple[AuditableProjectEvent, ...]) -> None:
        self.values = values

    def list_for_project(
        self, *, learner_id: str, project_id: str
    ) -> tuple[AuditableProjectEvent, ...]:
        assert learner_id == LEARNER_ID
        assert project_id == PROJECT_ID
        return self.values


class Repository:
    def __init__(self, *, fail: bool = False) -> None:
        self.values: dict[str, ProjectCompletionAuditRecord] = {}
        self.fail = fail

    def append_project_completion_records(
        self, records: tuple[ProjectCompletionAuditRecord, ...]
    ) -> None:
        if self.fail:
            raise RuntimeError("private audit storage")
        for record in records:
            prior = self.values.get(record.event_id)
            if prior is not None and prior != record:
                raise AuditRecordConflict
            self.values[record.event_id] = record


class Clock:
    def now(self) -> datetime:
        return NOW


def service(
    values: tuple[AuditableProjectEvent, ...],
    repository: Repository | None = None,
) -> AuditService:
    return AuditService(Source(values), repository or Repository(), Clock())


def request() -> ReconcileProjectCompletionAuditRequest:
    return ReconcileProjectCompletionAuditRequest(LEARNER_ID, PROJECT_ID)


def test_empty_exact_and_duplicate_project_reconciliation_are_bounded() -> None:
    empty = service(()).reconcile_project_completion(request())
    assert empty.reconciled_event_count == 0

    repository = Repository()
    first = service((event(),), repository).reconcile_project_completion(request())
    second = service((event(),), repository).reconcile_project_completion(request())
    assert first == second
    assert len(repository.values) == 1
    record = next(iter(repository.values.values()))
    assert record.project_id == PROJECT_ID
    assert record.evidence_id == event().evidence_id
    assert len(record.integrity_digest) == 64


@pytest.mark.parametrize(
    "invalid",
    [
        replace(event(), learner_id="22222222-2222-4222-8222-222222222222"),
        replace(event(), event_version="2.0.0"),
        replace(event(), policy_id="qualitative-grade"),
        replace(event(), snapshot_digest="not-a-digest"),
    ],
)
def test_inconsistent_project_source_fails_before_append(
    invalid: AuditableProjectEvent,
) -> None:
    repository = Repository()
    with pytest.raises(AuditError) as captured:
        service((invalid,), repository).reconcile_project_completion(request())
    assert captured.value.code is AuditErrorCode.INCONSISTENT_EVIDENCE
    assert repository.values == {}


def test_changed_same_event_conflicts_and_storage_failure_is_bounded() -> None:
    repository = Repository()
    service((event(),), repository).reconcile_project_completion(request())
    with pytest.raises(AuditError) as conflict:
        service(
            (replace(event(), snapshot_digest="9" * 64),), repository
        ).reconcile_project_completion(request())
    assert conflict.value.code is AuditErrorCode.CONFLICT

    with pytest.raises(AuditError) as unavailable:
        service((event(),), Repository(fail=True)).reconcile_project_completion(
            request()
        )
    assert unavailable.value.code is AuditErrorCode.UNAVAILABLE
    assert "private" not in unavailable.value.safe_message


def test_assessment_adapter_maps_only_the_public_project_event() -> None:
    contract = ContractProjectSubmissionAdapter(
        ROOT / "contracts/learning/assessment/project/v1"
    )
    corpus = ROOT / "contracts/compatibility/assessment-project/v1/approved"
    candidate = contract.parse_candidate((corpus / "snapshot-candidate.json").read_bytes())
    submission = contract.parse_submission((corpus / "submission.json").read_bytes())
    validation = contract.validate(candidate, submission)
    assert validation.accepted is not None
    evidence = contract.project_evidence(
        validation.accepted,
        ProjectEvidenceMetadata(
            evidence_id="evidence-retirement-01",
            learner_id=LEARNER_ID,
            occurrence=1,
            accepted_sequence=41,
            submitted_at=NOW,
        ),
    )
    public_event = contract.project_event(
        evidence,
        event_id="event-retirement-01",
        occurred_at=NOW,
    )
    accepted = evidence.accepted
    submission_value = accepted.submission
    safe_event = OrderedProjectCompletionEvent(
        schema_version=public_event.schema_version,
        event_id=public_event.event_id,
        event_type=public_event.event_type,
        event_version=public_event.event_version,
        occurred_at=public_event.occurred_at,
        evidence_id=evidence.evidence_id,
        learner_id=evidence.learner_id,
        submission_id=submission_value.submission_id,
        project_id=submission_value.project_id,
        snapshot_id=submission_value.snapshot_id,
        snapshot_digest=submission_value.snapshot_digest,
        brief_id=submission_value.brief_id,
        brief_version=submission_value.brief_version,
        brief_digest=submission_value.brief_digest,
        placement_id=submission_value.placement_id,
        placement_version=submission_value.placement_version,
        placement_digest=submission_value.placement_digest,
        policy_id=submission_value.policy_id,
        policy_version=submission_value.policy_version,
        milestone_ids=tuple(
            item.milestone_id for item in accepted.candidate.milestones
        ),
        request_fingerprint=accepted.request_fingerprint,
        occurrence=evidence.occurrence,
        accepted_sequence=evidence.accepted_sequence,
        submitted_at=evidence.submitted_at,
        supersedes_submission_id=evidence.supersedes_submission_id,
    )

    class Assessment:
        def read_completed_projects(self, _request: object):
            return (safe_event,)

    mapped = AssessmentAuditEventSource(Assessment()).list_for_project(
        learner_id=LEARNER_ID,
        project_id=PROJECT_ID,
    )

    assert mapped[0].event_id == safe_event.event_id
    assert mapped[0].evidence_id == evidence.evidence_id
    assert mapped[0].milestone_ids == (
        "identify-assumptions",
        "compare-scenarios",
    )
