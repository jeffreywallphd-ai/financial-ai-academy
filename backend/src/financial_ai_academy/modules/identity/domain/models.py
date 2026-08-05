"""Identity persistence records; provider/session secrets remain private."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentityBinding:
    installation_id: str
    binding_id: str
    actor_id: str
    learner_id: str
    mode: str


@dataclass(frozen=True, slots=True)
class SessionRecord:
    session_id: str
    binding: IdentityBinding
    token_hash: str
    authenticated_at: datetime
    last_seen_at: datetime
    absolute_expires_at: datetime
    revoked_at: datetime | None
