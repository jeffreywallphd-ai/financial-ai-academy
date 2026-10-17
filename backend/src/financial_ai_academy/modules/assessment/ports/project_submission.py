"""Port for the transport-neutral Project submission contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping, Protocol, Sequence

from ..domain.project_submission import (
    AcceptedProjectSubmission,
    ProjectCompletionEvent,
    ProjectCompletionEvidence,
    ProjectEvidenceMetadata,
    ProjectHistory,
    ProjectSnapshotCandidate,
    ProjectSubmission,
    ProjectValidationResult,
)


class ProjectSubmissionContractFailure(ValueError):
    """Bounded failure raised for invalid contract documents or metadata."""

    def __init__(self, code: str, reference: str) -> None:
        self.code = code
        self.reference = reference[:120]
        super().__init__(f"{code}: {self.reference}")


class ProjectSubmissionContract(Protocol):
    def parse_candidate(self, value: bytes) -> ProjectSnapshotCandidate: ...

    def parse_submission(self, value: bytes) -> ProjectSubmission: ...

    def validate(
        self,
        candidate: ProjectSnapshotCandidate,
        submission: ProjectSubmission,
    ) -> ProjectValidationResult: ...

    def project_validation(
        self, result: ProjectValidationResult
    ) -> Mapping[str, Any]: ...

    def project_evidence(
        self,
        accepted: AcceptedProjectSubmission,
        metadata: ProjectEvidenceMetadata,
    ) -> ProjectCompletionEvidence: ...

    def project_event(
        self,
        evidence: ProjectCompletionEvidence,
        *,
        event_id: str,
        occurred_at: datetime,
    ) -> ProjectCompletionEvent: ...

    def parse_event(
        self,
        document: Mapping[str, Any],
        evidence: ProjectCompletionEvidence,
    ) -> ProjectCompletionEvent: ...

    def project_history(
        self, evidence: Sequence[ProjectCompletionEvidence]
    ) -> ProjectHistory: ...
