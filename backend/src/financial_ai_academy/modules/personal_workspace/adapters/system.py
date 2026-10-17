"""UTC, opaque identity, and stable virtual-empty adapters."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4, uuid5

from ..ports.system import PersonalWorkspaceSeed


_WORKSPACE_NAMESPACE = UUID("7f404763-35f9-47aa-93ac-8508a55cf1ee")
_LOGICAL_INCEPTION = datetime(2000, 1, 1, tzinfo=timezone.utc)


class UtcClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class UuidGenerator:
    def new(self) -> str:
        return str(uuid4())


class StableWorkspaceSeed:
    """Project an unmaterialized learner workspace without a read-side write."""

    def for_learner(self, learner_id: str) -> PersonalWorkspaceSeed:
        return PersonalWorkspaceSeed(
            workspace_id=str(uuid5(_WORKSPACE_NAMESPACE, learner_id)),
            created_at=_LOGICAL_INCEPTION,
        )
