"""Identity persistence port."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from ..domain.models import IdentityBinding, SessionRecord


class IdentityModeMismatch(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class SingleProfileCandidate:
    installation_id: str
    binding_id: str
    actor_id: str
    learner_id: str
    created_at: datetime


class IdentityRepositoryPort(Protocol):
    def ensure_single_profile(
        self, candidate: SingleProfileCandidate
    ) -> IdentityBinding: ...

    def revoke_binding_sessions(
        self, binding_id: str, revoked_at: datetime
    ) -> None: ...

    def create_session(self, session: SessionRecord) -> None: ...

    def resolve_active_session(
        self,
        token_hash: str,
        now: datetime,
        idle_cutoff: datetime,
    ) -> SessionRecord | None: ...

    def revoke_session(self, token_hash: str, revoked_at: datetime) -> None: ...

    def health(self) -> bool: ...
