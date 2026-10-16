"""Project-owned persistence contract."""

from __future__ import annotations

from typing import Protocol

from ..domain.project import ProjectShell


class ProjectIdempotencyConflict(RuntimeError):
    pass


class ProjectRepositoryPort(Protocol):
    def get_by_idempotency(
        self, learner_id: str, idempotency_key: str
    ) -> tuple[str, ProjectShell] | None: ...

    def create_if_absent(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        shell: ProjectShell,
    ) -> tuple[ProjectShell, bool]: ...

    def get_for_learner(
        self, learner_id: str, project_id: str
    ) -> ProjectShell | None: ...

    def list_for_learner(self, learner_id: str) -> tuple[ProjectShell, ...]: ...
