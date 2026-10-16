"""Transport-neutral Project contract boundary."""

from __future__ import annotations

from typing import Mapping, Protocol

from ..domain.project import LearningProjectBrief, ProjectCreateIntent, ProjectShell
from ..domain.workspace import (
    ProjectEvidenceExport,
    ProjectSnapshot,
    ProjectSnapshotCloseIntent,
    ProjectWorkspace,
    WorkspaceMutationIntent,
)


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
    def canonical_digest(self, value: Mapping[str, object]) -> str: ...

    def parse_brief(self, value: bytes) -> LearningProjectBrief: ...

    def parse_intent(
        self,
        value: bytes,
        *,
        approved_brief: LearningProjectBrief | None = None,
    ) -> ProjectCreateIntent: ...

    def parse_shell(self, value: bytes) -> ProjectShell: ...

    def parse_workspace(self, value: bytes) -> ProjectWorkspace: ...

    def parse_workspace_mutation_intent(
        self, value: bytes
    ) -> WorkspaceMutationIntent: ...

    def parse_snapshot_close_intent(
        self, value: bytes
    ) -> ProjectSnapshotCloseIntent: ...

    def parse_snapshot(self, value: bytes) -> ProjectSnapshot: ...

    def parse_evidence_export(self, value: bytes) -> ProjectEvidenceExport: ...

    def brief_document(self, value: LearningProjectBrief) -> dict[str, object]: ...

    def intent_document(self, value: ProjectCreateIntent) -> dict[str, object]: ...

    def shell_document(self, value: ProjectShell) -> dict[str, object]: ...

    def workspace_document(self, value: ProjectWorkspace) -> dict[str, object]: ...

    def workspace_mutation_intent_document(
        self, value: WorkspaceMutationIntent
    ) -> dict[str, object]: ...

    def snapshot_close_intent_document(
        self, value: ProjectSnapshotCloseIntent
    ) -> dict[str, object]: ...

    def snapshot_document(self, value: ProjectSnapshot) -> dict[str, object]: ...

    def evidence_export_document(
        self, value: ProjectEvidenceExport
    ) -> dict[str, object]: ...
