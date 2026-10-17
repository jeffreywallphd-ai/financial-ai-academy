"""Personal-workspace-owned persistence contract."""

from __future__ import annotations

from typing import Protocol

from ..domain.workspace import PersonalWorkspace


class PersonalWorkspaceIdempotencyConflict(RuntimeError):
    pass


class PersonalWorkspaceRevisionConflict(RuntimeError):
    pass


class PersonalWorkspaceRepositoryPort(Protocol):
    def get_workspace(self, learner_id: str) -> PersonalWorkspace | None: ...

    def get_mutation_replay(
        self, learner_id: str, idempotency_key: str
    ) -> tuple[str, PersonalWorkspace] | None: ...

    def save_if_revision(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_revision: int,
        workspace: PersonalWorkspace,
    ) -> PersonalWorkspace: ...
