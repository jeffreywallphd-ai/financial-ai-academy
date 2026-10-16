"""Transport-neutral boundary for whole-practice submission and scoring."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from ..domain.practice import (
    PracticeDefinition,
    PracticePresentationContext,
    PracticeSubmissionCandidate,
)


class PracticeSubmissionFailure(ValueError):
    def __init__(self, code: str, reference: str) -> None:
        super().__init__("Practice submission was rejected.")
        self.code = code
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )


class PracticeSubmissionPort(Protocol):
    def parse_and_score(
        self,
        value: bytes,
        definition: PracticeDefinition,
        context: PracticePresentationContext,
        *,
        learner_id: str,
        attempt_id: str,
        evidence_id: str,
        event_id: str,
        submitted_at: datetime,
    ) -> PracticeSubmissionCandidate: ...
