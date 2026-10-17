"""Transport-neutral Personal workspace contract boundary."""

from __future__ import annotations

from datetime import datetime
from typing import Mapping, Protocol

from ..domain.workspace import (
    LearningReference,
    PersonalWorkspace,
    WorkspaceMutationIntent,
)


class PersonalWorkspaceContractFailure(ValueError):
    """Bounded learner-safe contract failure."""

    def __init__(self, code: str, reference: str) -> None:
        super().__init__("Personal workspace contract input was rejected.")
        self.code = code
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )


class PersonalWorkspaceContractPort(Protocol):
    def canonical_digest(self, value: Mapping[str, object]) -> str: ...

    def parse_reference(self, value: bytes) -> LearningReference: ...

    def parse_workspace(self, value: bytes) -> PersonalWorkspace: ...

    def parse_mutation_intent(self, value: bytes) -> WorkspaceMutationIntent: ...

    def reference_document(self, value: LearningReference) -> dict[str, object]: ...

    def workspace_document(self, value: PersonalWorkspace) -> dict[str, object]: ...

    def mutation_intent_document(
        self, value: WorkspaceMutationIntent
    ) -> dict[str, object]: ...

    def apply_mutation(
        self,
        workspace: PersonalWorkspace,
        intent: WorkspaceMutationIntent,
        *,
        occurred_at: datetime,
        issued_id: str | None = None,
    ) -> PersonalWorkspace: ...

    def empty_workspace(
        self,
        *,
        workspace_id: str,
        learner_id: str,
        created_at: datetime,
    ) -> PersonalWorkspace: ...
