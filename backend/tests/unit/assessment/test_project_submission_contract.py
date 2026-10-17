from __future__ import annotations

import copy
import json
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.assessment.adapters.project_submission_contract import (
    ContractProjectSubmissionAdapter,
)
from financial_ai_academy.modules.assessment.domain.project_submission import (
    AcceptedProjectSubmission,
    ProjectCompletionEvidence,
    ProjectEvidenceMetadata,
)
from financial_ai_academy.modules.assessment.ports.project_submission import (
    ProjectSubmissionContractFailure,
)


ROOT = Path(__file__).resolve().parents[4]
SCHEMAS = ROOT / "contracts/learning/assessment/project/v1"
CORPUS = ROOT / "contracts/compatibility/assessment-project/v1"


def _document(name: str) -> dict[str, object]:
    return json.loads((CORPUS / f"approved/{name}.json").read_text(encoding="utf-8"))


def _adapter() -> ContractProjectSubmissionAdapter:
    return ContractProjectSubmissionAdapter(SCHEMAS)


def _accepted() -> tuple[ContractProjectSubmissionAdapter, AcceptedProjectSubmission]:
    adapter = _adapter()
    candidate = adapter.parse_candidate(
        json.dumps(_document("snapshot-candidate"), ensure_ascii=False).encode()
    )
    submission = adapter.parse_submission(
        json.dumps(_document("submission"), ensure_ascii=False).encode()
    )
    result = adapter.validate(candidate, submission)
    assert result.accepted is not None
    return adapter, result.accepted


def test_domain_values_are_immutable() -> None:
    _, accepted = _accepted()
    with pytest.raises(FrozenInstanceError):
        accepted.candidate.project.project_id = "changed"  # type: ignore[misc]


def test_independent_origin_cannot_be_parsed_as_learning_evidence() -> None:
    document = _document("snapshot-candidate")
    document["origin"] = {"origin_type": "independent"}
    with pytest.raises(ProjectSubmissionContractFailure) as captured:
        _adapter().parse_candidate(json.dumps(document).encode())
    assert captured.value.code == "assessment.project.schema_invalid"
    assert captured.value.reference == "origin"


@pytest.mark.parametrize(
    "boundary",
    json.loads(
        (CORPUS / "cases/boundaries.json").read_text(encoding="utf-8")
    ),
    ids=lambda boundary: boundary["id"],
)
def test_candidate_accepts_every_supported_milestone_count(
    boundary: dict[str, object],
) -> None:
    milestone_count = int(boundary["milestone_count"])
    document = _document("snapshot-candidate")
    template = copy.deepcopy(document["milestones"][0])  # type: ignore[index]
    document["milestones"] = []
    for index in range(milestone_count):
        milestone = copy.deepcopy(template)
        milestone["milestone_id"] = f"milestone-{index + 1:02d}"
        milestone["sequence"] = index + 1
        milestone["title"] = f"Milestone {index + 1} – café"
        document["milestones"].append(milestone)  # type: ignore[union-attr]
    candidate = _adapter().parse_candidate(
        json.dumps(document, ensure_ascii=False).encode()
    )
    assert len(candidate.milestones) == milestone_count


def test_candidate_preserves_unicode_without_ascii_escape_assumptions() -> None:
    document = _document("snapshot-candidate")
    vector = json.loads(
        (CORPUS / "vectors/non-ascii-candidate.json").read_text(encoding="utf-8")
    )
    document["milestones"][1]["title"] = vector["value"]  # type: ignore[index]
    encoded = json.dumps(document, ensure_ascii=False).encode("utf-8")
    assert bytes.fromhex(vector["utf8_hex"]) in encoded
    candidate = _adapter().parse_candidate(encoded)
    assert candidate.milestones[1].title == vector["value"]


def test_candidate_requires_exact_brief_order_and_unique_resources() -> None:
    document = _document("snapshot-candidate")
    document["milestones"][1]["sequence"] = 1  # type: ignore[index]
    with pytest.raises(ProjectSubmissionContractFailure) as captured:
        _adapter().parse_candidate(json.dumps(document).encode())
    assert captured.value.code == "assessment.project.invalid_candidate"
    assert captured.value.reference == "milestones.sequence"

    document = _document("snapshot-candidate")
    document["resources"].append(copy.deepcopy(document["resources"][0]))  # type: ignore[union-attr,index]
    with pytest.raises(ProjectSubmissionContractFailure) as captured:
        _adapter().parse_candidate(json.dumps(document).encode())
    assert captured.value.code == "assessment.project.invalid_candidate"
    assert captured.value.reference == "resources"


def test_changed_evidence_changes_fingerprint_without_affecting_object_order() -> None:
    adapter, accepted = _accepted()
    changed_document = _document("submission")
    changed_document["submission_id"] = "submission-retirement-02"
    changed = adapter.parse_submission(json.dumps(changed_document).encode())
    result = adapter.validate(accepted.candidate, changed)
    assert result.status == "accepted"
    assert result.request_fingerprint != accepted.request_fingerprint


def test_validation_reports_safe_ordered_issues_without_echoing_payloads() -> None:
    adapter, accepted = _accepted()
    document = _document("submission")
    document["milestone_evidence"][0]["milestone_id"] = "not-in-brief"  # type: ignore[index]
    document["milestone_evidence"][1]["resources"][0]["resource_version"] = 99  # type: ignore[index]
    submission = adapter.parse_submission(json.dumps(document).encode())
    result = adapter.validate(accepted.candidate, submission)
    assert [issue.code for issue in result.issues] == [
        "assessment.project.unknown_milestone",
        "assessment.project.stale_resource",
        "assessment.project.missing_milestone",
    ]
    serialized = json.dumps(adapter.project_validation(result))
    assert "cccccccccccccccc" not in serialized
    assert "C:/" not in serialized


def _history_pair() -> tuple[
    ContractProjectSubmissionAdapter,
    ProjectCompletionEvidence,
    ProjectCompletionEvidence,
]:
    adapter, accepted = _accepted()
    first = adapter.project_evidence(
        accepted,
        ProjectEvidenceMetadata(
            evidence_id="evidence-retirement-01",
            learner_id="local-learner",
            occurrence=1,
            accepted_sequence=41,
            submitted_at=datetime(2026, 10, 17, 3, 30, tzinfo=timezone.utc),
        ),
    )
    second_submission = replace(
        accepted.submission, submission_id="submission-retirement-02"
    )
    second_accepted = AcceptedProjectSubmission(
        accepted.candidate,
        second_submission,
        adapter.submission_fingerprint(accepted.candidate, second_submission),
    )
    second = adapter.project_evidence(
        second_accepted,
        ProjectEvidenceMetadata(
            evidence_id="evidence-retirement-02",
            learner_id="local-learner",
            occurrence=2,
            accepted_sequence=42,
            submitted_at=datetime(2026, 10, 17, 4, 0, tzinfo=timezone.utc),
            supersedes_submission_id="submission-retirement-01",
        ),
    )
    return adapter, first, second


def test_server_metadata_is_bounded_and_history_is_append_only() -> None:
    adapter, first, second = _history_pair()
    history = adapter.project_history((second, first))
    assert [item.occurrence for item in history.items] == [1, 2]
    document = adapter.to_history_document(history)
    assert document["items"][1]["supersedes_submission_id"] == (
        "submission-retirement-01"
    )
    assert "learner_id" not in json.dumps(document)


@pytest.mark.parametrize(
    "case",
    json.loads(
        (CORPUS / "cases/history-cross-record-denials.json").read_text(
            encoding="utf-8"
        )
    ),
    ids=lambda case: case["id"],
)
def test_history_rejects_cross_record_identity_and_order_drift(
    case: dict[str, object],
) -> None:
    adapter, first, second = _history_pair()
    mutation = case["mutation"]
    value = case["value"]
    if mutation == "submission_id":
        submission = replace(second.accepted.submission, submission_id=str(value))
        accepted = replace(
            second.accepted,
            submission=submission,
            request_fingerprint=adapter.submission_fingerprint(
                second.accepted.candidate, submission
            ),
        )
        changed = replace(second, accepted=accepted)
    elif mutation == "submitted_at":
        changed = replace(
            second,
            submitted_at=datetime.fromisoformat(str(value).replace("Z", "+00:00")),
        )
    else:
        changed = replace(second, **{str(mutation): value})
    with pytest.raises(ProjectSubmissionContractFailure) as captured:
        adapter.project_history((first, changed))
    assert captured.value.code == "assessment.project.invalid_history"
    assert captured.value.reference == case["reference"]


def test_server_metadata_rejects_naive_time() -> None:
    adapter, accepted = _accepted()
    with pytest.raises(ProjectSubmissionContractFailure) as captured:
        adapter.project_evidence(
            accepted,
            ProjectEvidenceMetadata(
                evidence_id="evidence-retirement-01",
                learner_id="local-learner",
                occurrence=1,
                accepted_sequence=1,
                submitted_at=datetime(2026, 10, 17, 3, 30),
            ),
        )
    assert captured.value.code == "assessment.project.invalid_server_metadata"
    assert captured.value.reference == "submitted_at"


def test_server_metadata_rejects_broken_first_supersession() -> None:
    adapter, accepted = _accepted()
    with pytest.raises(ProjectSubmissionContractFailure) as captured:
        adapter.project_evidence(
            accepted,
            ProjectEvidenceMetadata(
                evidence_id="evidence-retirement-01",
                learner_id="local-learner",
                occurrence=1,
                accepted_sequence=1,
                submitted_at=datetime(2026, 10, 17, 3, 30, tzinfo=timezone.utc),
                supersedes_submission_id="earlier",
            ),
        )
    assert captured.value.code == "assessment.project.invalid_server_metadata"
    assert captured.value.reference == "supersedes_submission_id"


def test_evidence_rejects_a_forged_fingerprint() -> None:
    adapter, accepted = _accepted()
    forged = replace(accepted, request_fingerprint="9" * 64)
    with pytest.raises(ProjectSubmissionContractFailure) as captured:
        adapter.project_evidence(
            forged,
            ProjectEvidenceMetadata(
                evidence_id="evidence-retirement-01",
                learner_id="local-learner",
                occurrence=1,
                accepted_sequence=1,
                submitted_at=datetime(2026, 10, 17, 3, 30, tzinfo=timezone.utc),
            ),
        )
    assert captured.value.code == "assessment.project.inconsistent_evidence"
