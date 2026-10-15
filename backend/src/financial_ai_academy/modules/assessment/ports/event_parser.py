"""Versioned completion-event parsing boundary."""

from __future__ import annotations

from typing import Mapping, Protocol

from ..public import KnowledgeCheckCompletionEvent


class EventParsingFailure(ValueError):
    def __init__(self, code: str, reference: str) -> None:
        super().__init__("Assessment completion event was rejected.")
        self.code = code
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )


class AssessmentEventParserPort(Protocol):
    def parse(
        self, value: Mapping[str, object]
    ) -> KnowledgeCheckCompletionEvent: ...
