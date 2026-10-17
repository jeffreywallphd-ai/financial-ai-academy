"""Learner-model system capability ports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class ClockPort(Protocol):
    def now(self) -> datetime: ...


class IdentifierPort(Protocol):
    def new(self) -> str: ...


@dataclass(frozen=True, slots=True)
class PreferenceSeed:
    profile_id: str
    created_at: datetime


class PreferenceSeedPort(Protocol):
    def for_learner(self, learner_id: str) -> PreferenceSeed: ...
