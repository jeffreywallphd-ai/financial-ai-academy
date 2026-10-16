"""Transport-neutral practice progress contract boundary."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from ..domain.practice import (
    PracticeCompletionEvent,
    PracticeDefinition,
    PracticeDraft,
    PracticeDraftSave,
    PracticePresentationContext,
    PracticeRetryState,
)


class PracticeProgressFailure(ValueError):
    def __init__(self, code: str, reference: str) -> None:
        super().__init__("Practice progress was rejected.")
        self.code = code
        self.reference = reference


class PracticeProgressContractPort(Protocol):
    def parse_draft_save(
        self,
        value: bytes,
        definition: PracticeDefinition,
        context: PracticePresentationContext,
    ) -> PracticeDraftSave: ...

    def parse_completion_event(
        self, value: Mapping[str, Any]
    ) -> PracticeCompletionEvent: ...

    def draft_document(self, draft: PracticeDraft) -> dict[str, Any]: ...

    def retry_state_document(
        self, state: PracticeRetryState
    ) -> dict[str, Any]: ...
