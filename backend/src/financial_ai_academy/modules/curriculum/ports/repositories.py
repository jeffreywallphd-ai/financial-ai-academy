"""Persistence contract owned by Curriculum."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from ..public import (
    AssessmentPlacement,
    CurriculumGraph,
    LearningOpportunityRecord,
    LessonOpportunityClassification,
    LessonPlacement,
)


class PlacementConflict(RuntimeError):
    pass


class OpportunityConflict(RuntimeError):
    pass


class CurriculumGraphConflict(RuntimeError):
    pass


class CurriculumRepositoryPort(Protocol):
    def get(self, placement_id: str) -> LessonPlacement | None: ...

    def save_if_absent(
        self, placement: LessonPlacement
    ) -> tuple[LessonPlacement, bool]: ...

    def get_assessment(
        self, placement_id: str
    ) -> AssessmentPlacement | None: ...

    def save_assessment_if_absent(
        self, placement: AssessmentPlacement
    ) -> tuple[AssessmentPlacement, bool]: ...

    def get_graph_exact(
        self,
        curriculum_id: str,
        curriculum_version: str,
    ) -> CurriculumGraph | None: ...

    def save_graph_if_absent(
        self,
        graph: CurriculumGraph,
    ) -> tuple[CurriculumGraph, bool]: ...

    def get_opportunity_classification(
        self, opportunity_id: str
    ) -> LessonOpportunityClassification | None: ...

    def save_opportunity_classification_if_absent(
        self, classification: LessonOpportunityClassification
    ) -> tuple[LessonOpportunityClassification, bool]: ...

    def list_opportunity_classifications(
        self,
    ) -> tuple[LessonOpportunityClassification, ...]: ...

    def replace_discovery_projection(
        self,
        generation: str,
        projected_at: datetime,
        records: tuple[LearningOpportunityRecord, ...],
    ) -> None: ...

    def read_discovery_projection(
        self,
    ) -> tuple[
        str,
        datetime,
        tuple[LearningOpportunityRecord, ...],
    ] | None: ...
