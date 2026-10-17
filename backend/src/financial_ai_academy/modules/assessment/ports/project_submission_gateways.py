"""Public-operation gateway for exact Project learning-submission facts."""

from __future__ import annotations

from typing import Protocol

from ..domain.project_submission import ProjectSnapshotCandidate


class ProjectSubmissionSourceFailure(RuntimeError):
    def __init__(self, code: str, reference: str) -> None:
        self.code = code
        self.reference = reference[:120]
        super().__init__(f"{code}: {self.reference}")


class ProjectSubmissionSourcePort(Protocol):
    def resolve(
        self, *, learner_id: str, project_id: str, snapshot_id: str
    ) -> ProjectSnapshotCandidate: ...
