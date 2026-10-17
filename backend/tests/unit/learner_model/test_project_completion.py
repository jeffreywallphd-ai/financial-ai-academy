from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
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
from financial_ai_academy.modules.learner_model.adapters.assessment_gateway import (
    AssessmentCompletionEvidenceSource,
)

from financial_ai_academy.modules.learner_model.application.service import (
    LearnerModelService,
)
from financial_ai_academy.modules.learner_model.domain.models import (
    ProjectCompletionProjection,
    SourceProjectCompletion,
)
from financial_ai_academy.modules.learner_model.public import (
    LearnerModelError,
    LearnerModelErrorCode,
    OpenProjectCompletionRequest,
)


LEARNER_ID = "11111111-1111-4111-8111-111111111111"
PROJECT_ID = "project-retirement-plan"
NOW = datetime(2026, 10, 17, 3, 30, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[4]


def completion(
    occurrence: int = 1,
    *,
    supersedes: str | None = None,
) -> SourceProjectCompletion:
    return SourceProjectCompletion(
        schema_version="1.0.0",
        event_id=f"event-retirement-{occurrence:02d}",
        event_type="assessment.project.completed",
        event_version="1.0.0",
        occurred_at=NOW + timedelta(minutes=occurrence),
        evidence_id=f"evidence-retirement-{occurrence:02d}",
        learner_id=LEARNER_ID,
        occurrence=occurrence,
        accepted_sequence=40 + occurrence,
        submitted_at=NOW + timedelta(minutes=occurrence),
        supersedes_submission_id=supersedes,
        submission_id=f"submission-retirement-{occurrence:02d}",
        project_id=PROJECT_ID,
        snapshot_id=f"snapshot-retirement-plan-{occurrence:02d}",
        snapshot_digest=f"{occurrence}" * 64,
        brief_id="brief-retirement-plan",
        brief_version="1.0.0",
        brief_digest="4" * 64,
        placement_id="placement-retirement-project",
        placement_version="1.0.0",
        placement_digest="6" * 64,
        policy_id="assessment-project-closure",
        policy_version="1.0.0",
        milestone_ids=("identify-assumptions", "compare-scenarios"),
        request_fingerprint=f"{occurrence + 6}" * 64,
    )


class Source:
    def __init__(self, values: tuple[SourceProjectCompletion, ...]) -> None:
        self.values = values

    def list_for_project(
        self, *, learner_id: str, project_id: str
    ) -> tuple[SourceProjectCompletion, ...]:
        assert learner_id == LEARNER_ID
        assert project_id == PROJECT_ID
        return self.values


class Repository:
    def __init__(self, *, fail: bool = False) -> None:
        self.values: list[ProjectCompletionProjection] = []
        self.fail = fail

    def replace_project_completion(
        self, projection: ProjectCompletionProjection
    ) -> None:
        if self.fail:
            raise RuntimeError("private storage detail")
        self.values.append(projection)


class Clock:
    def now(self) -> datetime:
        return NOW + timedelta(hours=1)


def service(
    values: tuple[SourceProjectCompletion, ...],
    repository: Repository | None = None,
) -> LearnerModelService:
    return LearnerModelService(Source(values), repository or Repository(), Clock())


def request() -> OpenProjectCompletionRequest:
    return OpenProjectCompletionRequest(LEARNER_ID, PROJECT_ID)


def test_empty_and_exact_project_completion_have_bounded_meaning() -> None:
    empty = service(()).open_project_completion(request())
    assert empty.completed is False
    assert empty.completion_meaning == "not_completed"

    repository = Repository()
    exact = service((completion(),), repository).open_project_completion(request())
    assert exact.completed is True
    assert exact.completion_meaning == "bounded_project_activity_completed"
    assert exact.history[0].snapshot_id == "snapshot-retirement-plan-01"
    assert "master" not in exact.completion_meaning
    assert repository.values[0].source_digest == exact.source_digest


def test_exact_duplicate_replay_is_idempotent_and_supersession_is_ordered() -> None:
    first = completion()
    second = completion(2, supersedes=first.submission_id)
    view = service((second, first, first)).open_project_completion(request())

    assert [item.occurrence for item in view.history] == [1, 2]
    assert view.history[1].supersedes_submission_id == first.submission_id


def test_valid_contract_identifier_boundaries_do_not_require_fixture_lengths() -> None:
    compact = replace(
        completion(),
        event_id="e",
        evidence_id="v",
        submission_id="s",
        snapshot_id="x",
        brief_id="b",
        placement_id="p",
        milestone_ids=("m",),
    )
    view = service((compact,)).open_project_completion(request())
    assert view.completed is True
    assert view.history[0].event_id == "e"


@pytest.mark.parametrize(
    "invalid",
    [
        replace(completion(), learner_id="22222222-2222-4222-8222-222222222222"),
        replace(completion(), event_version="2.0.0"),
        replace(completion(), snapshot_digest="not-a-digest"),
        replace(completion(), milestone_ids=("duplicate", "duplicate")),
    ],
)
def test_inconsistent_project_source_fails_before_projection(
    invalid: SourceProjectCompletion,
) -> None:
    repository = Repository()
    with pytest.raises(LearnerModelError) as captured:
        service((invalid,), repository).open_project_completion(request())
    assert captured.value.code is LearnerModelErrorCode.INCONSISTENT_EVIDENCE
    assert repository.values == []


def test_changed_same_event_and_storage_failure_are_bounded() -> None:
    repository = Repository()
    with pytest.raises(LearnerModelError) as collision:
        service(
            (completion(), replace(completion(), snapshot_digest="9" * 64)),
            repository,
        ).open_project_completion(request())
    assert collision.value.code is LearnerModelErrorCode.INCONSISTENT_EVIDENCE
    assert repository.values == []

    with pytest.raises(LearnerModelError) as unavailable:
        service((completion(),), Repository(fail=True)).open_project_completion(
            request()
        )
    assert unavailable.value.code is LearnerModelErrorCode.UNAVAILABLE
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

    mapped = AssessmentCompletionEvidenceSource(Assessment()).list_for_project(
        learner_id=LEARNER_ID,
        project_id=PROJECT_ID,
    )

    assert mapped[0].event_id == safe_event.event_id
    assert mapped[0].request_fingerprint == validation.accepted.request_fingerprint
    assert mapped[0].milestone_ids == (
        "identify-assumptions",
        "compare-scenarios",
    )
