"""Learner-model system adapters."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4, uuid5

from ..ports.system import PreferenceSeed, PresentationPreferenceSeed


_PREFERENCE_NAMESPACE = UUID("372c8e50-c9e8-47f1-941a-c467ff5df948")
_PRESENTATION_PREFERENCE_NAMESPACE = UUID("305d4e9d-9dd0-4132-bf02-00bcb50a337d")
_LOGICAL_INCEPTION = datetime(2000, 1, 1, tzinfo=timezone.utc)


class UtcClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class UuidGenerator:
    def new(self) -> str:
        return str(uuid4())


class StablePreferenceSeed:
    """Project an unmaterialized preference profile without a read write."""

    def for_learner(self, learner_id: str) -> PreferenceSeed:
        return PreferenceSeed(
            profile_id=f"profile.{uuid5(_PREFERENCE_NAMESPACE, learner_id)}",
            created_at=_LOGICAL_INCEPTION,
        )


class StablePresentationPreferenceSeed:
    """Project an unmaterialized presentation profile without a read write."""

    def for_learner(self, learner_id: str) -> PresentationPreferenceSeed:
        return PresentationPreferenceSeed(
            profile_id=(
                "presentation."
                f"{uuid5(_PRESENTATION_PREFERENCE_NAMESPACE, learner_id)}"
            ),
            created_at=_LOGICAL_INCEPTION,
        )
