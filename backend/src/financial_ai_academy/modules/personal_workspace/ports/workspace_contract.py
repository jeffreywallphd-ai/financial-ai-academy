"""Transport-neutral Personal workspace contract boundary."""

from __future__ import annotations

from datetime import datetime
from typing import Mapping, Protocol

from ..domain.workspace import (
    LearningReference,
    PersonalWorkspace,
    WorkspaceExportView,
    WorkspaceMutationIntent,
    WorkspaceQuery,
    WorkspaceQueryResult,
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

    def parse_workspace_export(self, value: bytes) -> WorkspaceExportView: ...

    def parse_mutation_intent(self, value: bytes) -> WorkspaceMutationIntent: ...

    def parse_workspace_query(self, value: bytes) -> WorkspaceQuery: ...

    def parse_workspace_query_result(self, value: bytes) -> WorkspaceQueryResult: ...

    def reference_document(self, value: LearningReference) -> dict[str, object]: ...

    def workspace_document(self, value: PersonalWorkspace) -> dict[str, object]: ...

    def workspace_export_document(
        self, value: WorkspaceExportView
    ) -> dict[str, object]: ...

    def export_workspace(
        self,
        workspace: PersonalWorkspace,
        *,
        generated_at: datetime,
    ) -> WorkspaceExportView: ...

    def mutation_intent_document(
        self, value: WorkspaceMutationIntent
    ) -> dict[str, object]: ...

    def workspace_query_document(self, value: WorkspaceQuery) -> dict[str, object]: ...

    def workspace_query_result_document(
        self, value: WorkspaceQueryResult
    ) -> dict[str, object]: ...

    def query_workspace(
        self,
        workspace: PersonalWorkspace,
        query: WorkspaceQuery,
    ) -> WorkspaceQueryResult: ...

    def apply_reference_refresh(
        self,
        workspace: PersonalWorkspace,
        intent: WorkspaceMutationIntent,
        *,
        occurred_at: datetime,
        resolved_reference: LearningReference | None,
    ) -> PersonalWorkspace: ...

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
