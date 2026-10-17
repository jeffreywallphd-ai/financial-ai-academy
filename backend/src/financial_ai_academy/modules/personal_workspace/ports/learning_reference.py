"""Public-owner gateway for accepted Personal-workspace references."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from ..domain.workspace import LearningReference
from ..public import LearningReferenceSelector


class PersonalWorkspaceSourceUnavailable(RuntimeError):
    pass


class LearningReferenceGatewayPort(Protocol):
    def resolve(
        self,
        selector: LearningReferenceSelector,
        *,
        learner_id: str,
        validated_at: datetime,
    ) -> LearningReference: ...
