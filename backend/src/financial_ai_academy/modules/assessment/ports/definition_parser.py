"""Private definition parsing boundary."""

from __future__ import annotations

from typing import Protocol

from ..domain.models import AssessmentDefinition


class DefinitionParsingFailure(ValueError):
    def __init__(self, code: str, reference: str) -> None:
        super().__init__("Assessment definition was rejected.")
        self.code = code
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )


class AssessmentDefinitionParserPort(Protocol):
    def parse(self, value: bytes) -> AssessmentDefinition: ...

