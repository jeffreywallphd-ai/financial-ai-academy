"""Transport-neutral Project contract boundary."""

from __future__ import annotations

from typing import Protocol

from ..domain.project import LearningProjectBrief, ProjectCreateIntent, ProjectShell


class ProjectContractFailure(ValueError):
    """Bounded learner-safe contract failure."""

    def __init__(self, code: str, reference: str) -> None:
        super().__init__("Project contract input was rejected.")
        self.code = code
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )


class ProjectContractPort(Protocol):
    def parse_brief(self, value: bytes) -> LearningProjectBrief: ...

    def parse_intent(
        self,
        value: bytes,
        *,
        approved_brief: LearningProjectBrief | None = None,
    ) -> ProjectCreateIntent: ...

    def parse_shell(self, value: bytes) -> ProjectShell: ...

    def brief_document(self, value: LearningProjectBrief) -> dict[str, object]: ...

    def intent_document(self, value: ProjectCreateIntent) -> dict[str, object]: ...

    def shell_document(self, value: ProjectShell) -> dict[str, object]: ...
