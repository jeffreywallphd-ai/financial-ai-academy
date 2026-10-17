"""Server-owned time and identity ports for Personal workspace."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class PersonalWorkspaceSeed:
    workspace_id: str
    created_at: datetime


class ClockPort(Protocol):
    def now(self) -> datetime: ...


class IdentifierPort(Protocol):
    def new(self) -> str: ...


class WorkspaceSeedPort(Protocol):
    def for_learner(self, learner_id: str) -> PersonalWorkspaceSeed: ...
