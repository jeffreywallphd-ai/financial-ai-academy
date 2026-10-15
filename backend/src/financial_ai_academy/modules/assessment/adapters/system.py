"""Production UTC clock and UUID generator."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


class UtcClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class UuidGenerator:
    def new(self) -> str:
        return str(uuid4())

