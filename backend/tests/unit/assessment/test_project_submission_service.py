from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import pytest

from financial_ai_academy.modules.assessment.adapters.project_submission_contract import (
    ContractProjectSubmissionAdapter,
)
from financial_ai_academy.modules.assessment.adapters.project_submission_gateways import (
    PublicProjectSubmissionSource,
)
from financial_ai_academy.modules.assessment.application.service import AssessmentService
from financial_ai_academy.modules.content.public import PublishedProjectBrief
from financial_ai_academy.modules.curriculum.public import ProjectBriefPlacement
from financial_ai_academy.modules.project.domain.project import LearningProjectOrigin
from financial_ai_academy.modules.project.domain.workspace import (
    ProjectSnapshot,
    ProjectSnapshotMaterial,
)
from financial_ai_academy.modules.project.public import (
    ProjectLearningSnapshot,
    ProjectLearningSnapshotResource,
)
from financial_ai_academy.modules.assessment.ports.project_submission_gateways import (
    ProjectSubmissionSourceFailure,
)
from financial_ai_academy.modules.assessment.ports.repositories import (
    ProjectSubmissionConflict,
)
from financial_ai_academy.modules.assessment.domain.project_submission import (
    ProjectEvidenceMetadata,
)
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    AssessmentErrorCode,
    OpenProjectSubmissionCandidateRequest,
    ReadProjectCompletionEvidenceRequest,
    ReadProjectCompletionHistoryRequest,
    SubmitProjectSnapshotRequest,
)


ROOT = Path(__file__).resolve().parents[4]
CORPUS = ROOT / "contracts/compatibility/assessment-project/v1/approved"
SCHEMAS = ROOT / "contracts/learning/assessment/project/v1"
PROJECT_SCHEMAS = ROOT / "contracts/learning/project/v1"
LEARNER = "11111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 10, 17, 3, 30, tzinfo=timezone.utc)


class Unused:
    def __getattr__(self, name):
        raise AssertionError(f"Unexpected dependency call: {name}")


class Source:
    def __init__(self, candidate):
        self.candidate = candidate
        self.failure: ProjectSubmissionSourceFailure | None = None

    def resolve(self, *, learner_id, project_id, snapshot_id):
        assert learner_id == LEARNER
        assert project_id == self.candidate.project.project_id
        assert snapshot_id == self.candidate.project.snapshot_id
        if self.failure is not None:
            raise self.failure
        return self.candidate


class Repository:
    def __init__(self, contract):
        self.contract = contract
        self.items = []

    def record_project_submission(self, candidate):
        for item in self.items:
            if (
                item.learner_id == candidate.learner_id
                and item.accepted.submission.submission_id
                == candidate.accepted.submission.submission_id
            ):
                if (
                    item.accepted.request_fingerprint
                    != candidate.accepted.request_fingerprint
                ):
                    raise ProjectSubmissionConflict
                return item, False
        prior = self.items[-1] if self.items else None
        evidence = self.contract.project_evidence(
            candidate.accepted,
            ProjectEvidenceMetadata(
                candidate.evidence_id,
                candidate.learner_id,
                len(self.items) + 1,
                len(self.items) + 1,
                candidate.submitted_at,
                prior.accepted.submission.submission_id if prior else None,
            ),
        )
        self.items.append(evidence)
        return evidence, True

    def list_project_completion_evidence(self, *, learner_id, project_id):
        return tuple(
            item
            for item in self.items
            if item.learner_id == learner_id
            and item.accepted.candidate.project.project_id == project_id
        )


class Clock:
    def now(self):
        return NOW


class Ids:
    def __init__(self):
        self.value = 0

    def new(self):
        self.value += 1
        return str(UUID(int=self.value))


class PublicOperation:
    def __init__(self, value):
        self.value = value
        self.request = None

    def open_learning_snapshot(self, request):
        self.request = request
        return self.value

    def get_published_project_brief(self, request):
        self.request = request
        return self.value

    def resolve_project_brief_placement(self, request):
        self.request = request
        return self.value


def _document(name: str) -> bytes:
    return (CORPUS / f"{name}.json").read_bytes()


def _subject():
    contract = ContractProjectSubmissionAdapter(SCHEMAS)
    candidate = contract.parse_candidate(_document("snapshot-candidate"))
    source = Source(candidate)
    repository = Repository(contract)
    subject = AssessmentService(
        Unused(),
        Unused(),
        Unused(),
        Unused(),
        repository,
        Clock(),
        Ids(),
        project_submission_source=source,
        project_submission_contract=contract,
    )
    return subject, source, repository


def _public_source(*, first_description: str = "Identify the plan assumptions"):
    raw = json.loads(_document("snapshot-candidate"))
    project = raw["project"]
    origin_value = raw["origin"]
    origin = LearningProjectOrigin(
        project_brief_schema_version="1.0.0",
        **origin_value,
        brief_title="Retirement plan",
        brief_purpose="Compare retirement scenarios.",
    )
    snapshot = ProjectSnapshot(
        schema_version="1.0.0",
        snapshot_id=project["snapshot_id"],
        snapshot_digest=project["snapshot_digest"],
        snapshot=ProjectSnapshotMaterial(
            project_id=project["project_id"],
            learner_id=LEARNER,
            project_revision=project["project_revision"],
            project_shell_digest=project["project_shell_digest"],
            workspace_revision=project["workspace_revision"],
            workspace_created_at=NOW,
            workspace_updated_at=NOW,
            notes=(),
            references=(),
            artifacts=(),
            domain_links=(),
        ),
        closed_at=datetime.fromisoformat(project["closed_at"].replace("Z", "+00:00")),
    )
    resources = tuple(
        ProjectLearningSnapshotResource(
            resource_kind=item["resource_kind"],
            resource_id=item["resource_id"],
            resource_version=item.get("resource_version"),
            resource_as_of=None,
            record_digest=item["record_digest"],
            content_digest=item.get("content_digest"),
            byte_count=item.get("byte_count"),
            owner_reference_digest=item.get("owner_reference_digest"),
        )
        for item in raw["resources"]
    )
    brief_document = {
        "schema_version": "1.0.0",
        "brief_digest": origin.brief_digest,
        "brief": {
            "brief_id": origin.brief_id,
            "brief_version": origin.brief_version,
            "title": origin.brief_title,
            "purpose": origin.brief_purpose,
            "milestones": [
                {
                    "milestone_id": "identify-assumptions",
                    "description": first_description,
                },
                {
                    "milestone_id": "compare-scenarios",
                    "description": "Compare two scenarios café",
                },
            ],
            "source_references": [
                {
                    "resource_id": "source-plan-rules",
                    "resource_version": "1.0.0",
                    "resource_digest": "b" * 64,
                    "title": "Plan rules",
                }
            ],
        },
    }
    project_operation = PublicOperation(
        ProjectLearningSnapshot(origin, snapshot, resources)
    )
    content_operation = PublicOperation(
        PublishedProjectBrief(
            package_id=origin.package_id,
            package_version=origin.package_version,
            package_digest=origin.package_digest,
            brief_id=origin.brief_id,
            brief_version=origin.brief_version,
            brief_digest=origin.brief_digest,
            schema_version="1.0.0",
            file_digest="7" * 64,
            value=json.dumps(brief_document).encode(),
        )
    )
    placement_operation = PublicOperation(
        ProjectBriefPlacement(
            placement_id=origin.placement_id,
            placement_version=origin.placement_version,
            placement_digest=origin.placement_digest,
            curriculum_id=origin.curriculum_id,
            curriculum_version=origin.curriculum_version,
            curriculum_digest=origin.curriculum_digest,
            activity_id="activity-retirement-project",
            package_id=origin.package_id,
            package_version=origin.package_version,
            package_digest=origin.package_digest,
            brief_id=origin.brief_id,
            brief_version=origin.brief_version,
            brief_digest=origin.brief_digest,
            project_brief_schema_version="1.0.0",
            created_at=NOW,
        )
    )
    contract = ContractProjectSubmissionAdapter(SCHEMAS)
    source = PublicProjectSubmissionSource(
        project_operation,
        content_operation,
        placement_operation,
        contract,
        PROJECT_SCHEMAS,
    )
    return source, project_operation, content_operation, placement_operation


def test_project_candidate_and_accepted_evidence_share_one_headless_core() -> None:
    subject, _source, repository = _subject()
    candidate = subject.open_project_submission_candidate(
        OpenProjectSubmissionCandidateRequest(
            LEARNER, "project-retirement-plan", "snapshot-retirement-plan-01"
        )
    )

    outcome = subject.submit_project_snapshot(
        SubmitProjectSnapshotRequest(
            LEARNER,
            candidate.project.project_id,
            candidate.project.snapshot_id,
            _document("submission"),
        )
    )
    replay = subject.submit_project_snapshot(
        SubmitProjectSnapshotRequest(
            LEARNER,
            candidate.project.project_id,
            candidate.project.snapshot_id,
            _document("submission"),
        )
    )
    history = subject.read_project_completion_history(
        ReadProjectCompletionHistoryRequest(LEARNER, candidate.project.project_id)
    )
    reopened = subject.read_project_completion_evidence(
        ReadProjectCompletionEvidenceRequest(
            LEARNER,
            candidate.project.project_id,
            outcome.evidence.accepted.submission.submission_id,  # type: ignore[union-attr]
        )
    )

    assert outcome.validation.status == "accepted"
    assert outcome.evidence is not None
    assert replay.evidence == outcome.evidence
    assert len(repository.items) == 1
    assert history.items == (outcome.evidence,)
    assert reopened == outcome.evidence


def test_public_project_source_assembles_exact_versioned_facts() -> None:
    source, project, content, placement = _public_source(
        first_description="A" * 200
    )

    candidate = source.resolve(
        learner_id=LEARNER,
        project_id="project-retirement-plan",
        snapshot_id="snapshot-retirement-plan-01",
    )

    assert candidate.project.snapshot_digest == "2" * 64
    assert candidate.origin.brief_digest == "4" * 64
    assert candidate.milestones[0].title == f"{'A' * 157}..."
    assert len(candidate.resources) == 4
    assert project.request.learner_id == LEARNER
    assert content.request.package_digest == candidate.origin.package_digest
    assert placement.request.placement_id == candidate.origin.placement_id


def test_public_project_source_refuses_stale_placement() -> None:
    source, _project, _content, placement = _public_source()
    placement.value = ProjectBriefPlacement(
        **{
            field: getattr(placement.value, field)
            for field in placement.value.__dataclass_fields__
            if field != "brief_digest"
        },
        brief_digest="9" * 64,
    )

    with pytest.raises(ProjectSubmissionSourceFailure) as captured:
        source.resolve(
            learner_id=LEARNER,
            project_id="project-retirement-plan",
            snapshot_id="snapshot-retirement-plan-01",
        )

    assert captured.value.code == "assessment.project.stale_source"
    assert captured.value.reference == "learning_origin"


def test_project_validation_refusal_has_no_persistence_side_effect() -> None:
    subject, _source, repository = _subject()
    document = json.loads(_document("submission"))
    document["milestone_evidence"] = document["milestone_evidence"][:-1]

    outcome = subject.submit_project_snapshot(
        SubmitProjectSnapshotRequest(
            LEARNER,
            "project-retirement-plan",
            "snapshot-retirement-plan-01",
            json.dumps(document).encode(),
        )
    )

    assert outcome.validation.status == "refused"
    assert outcome.evidence is None
    assert outcome.validation.issues[0].code == "assessment.project.missing_milestone"
    assert repository.items == []


@pytest.mark.parametrize(
    ("source_code", "expected"),
    [
        ("assessment.project.not_found", AssessmentErrorCode.NOT_FOUND),
        ("assessment.project.stale_source", AssessmentErrorCode.STALE_REFERENCE),
        ("assessment.project.invalid_source", AssessmentErrorCode.INVALID_DEFINITION),
        ("assessment.project.source_unavailable", AssessmentErrorCode.UNAVAILABLE),
    ],
)
def test_project_source_failures_remain_bounded(source_code, expected) -> None:
    subject, source, _repository = _subject()
    source.failure = ProjectSubmissionSourceFailure(source_code, "safe-reference")

    with pytest.raises(AssessmentError) as captured:
        subject.open_project_submission_candidate(
            OpenProjectSubmissionCandidateRequest(
                LEARNER,
                "project-retirement-plan",
                "snapshot-retirement-plan-01",
            )
        )

    assert captured.value.code is expected
    assert captured.value.reference == "safe-reference"
    assert "storage" not in captured.value.safe_message.lower()
