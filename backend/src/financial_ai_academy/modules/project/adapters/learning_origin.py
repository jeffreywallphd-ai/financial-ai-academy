"""Adapters from Project ports to public Content and Curriculum operations."""

from __future__ import annotations

from financial_ai_academy.modules.content.public import (
    ContentOperations,
    GetPublishedProjectBriefRequest,
)
from financial_ai_academy.modules.curriculum.public import (
    CurriculumOperations,
    ProjectBriefPlacement,
    ResolveProjectBriefPlacementRequest,
)

from ..domain.project import LearningProjectBrief, LearningProjectOrigin
from ..ports.project_contract import ProjectContractPort


class PublicContentProjectBriefGateway:
    def __init__(
        self,
        content: ContentOperations,
        contract: ProjectContractPort,
    ) -> None:
        self._content = content
        self._contract = contract

    def resolve(self, origin: LearningProjectOrigin) -> LearningProjectBrief:
        published = self._content.get_published_project_brief(
            GetPublishedProjectBriefRequest(
                package_id=origin.package_id,
                package_version=origin.package_version,
                package_digest=origin.package_digest,
                brief_id=origin.brief_id,
            )
        )
        return self._contract.parse_brief(published.value)


class PublicCurriculumProjectPlacementGateway:
    def __init__(self, curriculum: CurriculumOperations) -> None:
        self._curriculum = curriculum

    def resolve(self, placement_id: str) -> ProjectBriefPlacement:
        return self._curriculum.resolve_project_brief_placement(
            ResolveProjectBriefPlacementRequest(placement_id=placement_id)
        )
