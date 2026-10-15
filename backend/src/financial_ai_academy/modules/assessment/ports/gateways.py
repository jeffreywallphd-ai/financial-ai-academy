"""Public-only gateway contracts owned by Assessment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class PlacedAssessmentReference:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    assessment_id: str
    assessment_version: str
    definition_digest: str
    item_id: str
    item_version: str
    scoring_policy_id: str
    scoring_policy_version: str


@dataclass(frozen=True, slots=True)
class DefinitionDocument:
    package_id: str
    package_version: str
    package_digest: str
    assessment_id: str
    schema_version: str
    file_digest: str
    value: bytes


class CurriculumAssessmentGatewayPort(Protocol):
    def resolve(self, placement_id: str) -> PlacedAssessmentReference: ...


class ContentDefinitionGatewayPort(Protocol):
    def get_exact(
        self, reference: PlacedAssessmentReference
    ) -> DefinitionDocument: ...

