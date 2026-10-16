"""Nondeterministic values supplied to deterministic Project policy."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class ClockPort(Protocol):
    def now(self) -> datetime: ...


class IdentifierPort(Protocol):
    def new(self) -> str: ...
