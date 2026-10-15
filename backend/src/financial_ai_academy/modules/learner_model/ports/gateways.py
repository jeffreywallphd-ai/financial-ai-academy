"""Learner-model evidence-source boundary."""

from __future__ import annotations

from typing import Protocol

from ..domain.models import SourceCompletionEvidence


class CompletionEvidenceSourcePort(Protocol):
    def list_for_lesson(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[SourceCompletionEvidence, ...]: ...
