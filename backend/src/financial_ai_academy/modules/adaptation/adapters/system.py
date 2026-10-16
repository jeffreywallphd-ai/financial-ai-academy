"""System adapters for Adaptation."""

from datetime import datetime, timezone


class UtcClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
