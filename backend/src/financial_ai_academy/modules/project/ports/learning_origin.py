"""Project-owned ports for exact public learning-origin resolution."""

from __future__ import annotations

from typing import Protocol

from financial_ai_academy.modules.curriculum.public import ProjectBriefPlacement

from ..domain.project import LearningProjectBrief, LearningProjectOrigin


class ProjectBriefGatewayPort(Protocol):
    def resolve(self, origin: LearningProjectOrigin) -> LearningProjectBrief: ...


class ProjectPlacementGatewayPort(Protocol):
    def resolve(self, placement_id: str) -> ProjectBriefPlacement: ...

    def list(self) -> tuple[ProjectBriefPlacement, ...]: ...
