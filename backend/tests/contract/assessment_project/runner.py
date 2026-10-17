"""Dependency-light conformance runner for Assessment Project v1."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from financial_ai_academy.modules.assessment.adapters.project_submission_contract import (
    ContractProjectSubmissionAdapter,
)
from financial_ai_academy.modules.assessment.domain.project_submission import (
    ProjectEvidenceMetadata,
)


ROOT = Path(__file__).resolve().parents[4]
SCHEMAS = ROOT / "contracts/learning/assessment/project/v1"
CORPUS = ROOT / "contracts/compatibility/assessment-project/v1"


def load(relative: str) -> dict[str, Any]:
    return json.loads((CORPUS / relative).read_text(encoding="utf-8"))


def approved_chain() -> tuple[ContractProjectSubmissionAdapter, object, ...]:
    adapter = ContractProjectSubmissionAdapter(SCHEMAS)
    candidate = adapter.parse_candidate(
        (CORPUS / "approved/snapshot-candidate.json").read_bytes()
    )
    submission = adapter.parse_submission(
        (CORPUS / "approved/submission.json").read_bytes()
    )
    validation = adapter.validate(candidate, submission)
    if validation.accepted is None:
        raise RuntimeError("Approved Project submission was refused.")
    evidence = adapter.project_evidence(
        validation.accepted,
        ProjectEvidenceMetadata(
            evidence_id="evidence-retirement-01",
            learner_id="local-learner",
            occurrence=1,
            accepted_sequence=41,
            submitted_at=datetime(2026, 10, 17, 3, 30, tzinfo=timezone.utc),
        ),
    )
    event = adapter.project_event(
        evidence,
        event_id="event-retirement-01",
        occurred_at=datetime(2026, 10, 17, 3, 30, 1, tzinfo=timezone.utc),
    )
    history = adapter.project_history((evidence,))
    return adapter, candidate, submission, validation, evidence, event, history


def main() -> int:
    adapter, candidate, submission, validation, evidence, event, history = (
        approved_chain()
    )
    expected = {
        "validation": load("approved/validation-result.json"),
        "evidence": load("approved/evidence.json"),
        "event": load("approved/completion-event.json"),
        "history": load("approved/history.json"),
    }
    actual = {
        "validation": adapter.project_validation(validation),
        "evidence": adapter.to_evidence_document(evidence),
        "event": adapter.to_event_document(event),
        "history": adapter.to_history_document(history),
    }
    if actual != expected:
        raise RuntimeError("Approved Assessment Project projection drifted.")
    print(
        json.dumps(
            {
                "valid": True,
                "milestone_count": len(candidate.milestones),
                "resource_kinds": sorted(
                    {item.resource_kind for item in candidate.resources}
                ),
                "fingerprint": validation.request_fingerprint,
                "submission_id": submission.submission_id,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
