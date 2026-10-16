"""Transport-neutral boundary for private practice definitions."""

from __future__ import annotations

from typing import Protocol

from ..domain.practice import (
    PracticeDefinition,
    PracticePresentation,
    PracticePresentationContext,
)


class PracticeDefinitionFailure(ValueError):
    def __init__(self, code: str, reference: str) -> None:
        super().__init__("Practice definition was rejected.")
        self.code = code
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )


class PracticeDefinitionPort(Protocol):
    def parse(self, value: bytes) -> PracticeDefinition: ...

    def project(
        self,
        definition: PracticeDefinition,
        context: PracticePresentationContext,
    ) -> PracticePresentation: ...
