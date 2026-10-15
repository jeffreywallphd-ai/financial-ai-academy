from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.curriculum.application.service import (
    CurriculumService,
)
from financial_ai_academy.modules.curriculum.ports.repositories import (
    CurriculumGraphConflict,
)
from financial_ai_academy.modules.curriculum.public import (
    AssessmentActivityReference,
    AssessmentPlacement,
    CurriculumGraph,
    CurriculumGraphError,
    CurriculumGraphErrorCode,
    LessonActivityReference,
    LessonPlacement,
    OpenCurriculumGraphRequest,
    PublishCurriculumGraphRequest,
    curriculum_graph_digest,
    curriculum_graph_from_mapping,
)


REPOSITORY = Path(__file__).resolve().parents[4]
APPROVED = (
    REPOSITORY
    / "contracts/compatibility/curriculum-graph/v1/approved/graph.json"
)
NOW = datetime(2026, 10, 15, tzinfo=timezone.utc)


class MemoryGraphRepository:
    def __init__(self, graph: CurriculumGraph | object | None = None) -> None:
        self.graphs: dict[tuple[str, str], CurriculumGraph | object] = {}
        if graph is not None and isinstance(graph, CurriculumGraph):
            self.graphs[(graph.curriculum_id, graph.curriculum_version)] = graph
        self.lessons: dict[str, LessonPlacement] = {}
        self.assessments: dict[str, AssessmentPlacement] = {}
        self.save_calls = 0

    def get(self, placement_id: str) -> LessonPlacement | None:
        return self.lessons.get(placement_id)

    def get_assessment(
        self, placement_id: str
    ) -> AssessmentPlacement | None:
        return self.assessments.get(placement_id)

    def get_graph_exact(
        self, curriculum_id: str, curriculum_version: str
    ) -> CurriculumGraph | None:
        return self.graphs.get((curriculum_id, curriculum_version))  # type: ignore[return-value]

    def save_graph_if_absent(
        self, graph: CurriculumGraph
    ) -> tuple[CurriculumGraph, bool]:
        self.save_calls += 1
        key = (graph.curriculum_id, graph.curriculum_version)
        existing = self.graphs.get(key)
        if existing is None:
            self.graphs[key] = graph
            return graph, True
        if existing != graph:
            raise CurriculumGraphConflict
        return graph, False


class UnusedContentGateway:
    def get_exact(self, *_args: object) -> object:
        raise AssertionError("graph operations must not read Content")


def approved_graph() -> CurriculumGraph:
    return curriculum_graph_from_mapping(
        json.loads(APPROVED.read_text(encoding="utf-8"))
    )


def add_exact_placements(
    repository: MemoryGraphRepository,
    graph: CurriculumGraph,
) -> None:
    for activity in graph.activities:
        reference = activity.reference
        if isinstance(reference, LessonActivityReference):
            repository.lessons[reference.placement_id] = LessonPlacement(
                placement_id=reference.placement_id,
                package_id=reference.package_id,
                package_version=reference.package_version,
                package_digest=reference.package_digest,
                created_at=NOW,
            )
        elif isinstance(reference, AssessmentActivityReference):
            repository.assessments[reference.placement_id] = AssessmentPlacement(
                placement_id=reference.placement_id,
                package_id="supporting-package",
                package_version="1.0.0",
                package_digest="f" * 64,
                assessment_id=reference.assessment_id,
                assessment_version=reference.assessment_version,
                definition_digest=reference.definition_digest,
                item_id="supporting-item",
                item_version="1.0.0",
                scoring_policy_id="single-select-exact-match",
                scoring_policy_version="1.0.0",
                created_at=NOW,
            )


def service_with_placements() -> tuple[CurriculumService, MemoryGraphRepository]:
    graph = approved_graph()
    repository = MemoryGraphRepository()
    add_exact_placements(repository, graph)
    return CurriculumService(repository, UnusedContentGateway()), repository  # type: ignore[arg-type]


def test_publish_and_open_exact_graph_is_idempotent() -> None:
    service, repository = service_with_placements()
    graph = approved_graph()

    first = service.publish_curriculum_graph(PublishCurriculumGraphRequest(graph))
    second = service.publish_curriculum_graph(PublishCurriculumGraphRequest(graph))
    opened = service.open_curriculum_graph(
        OpenCurriculumGraphRequest(graph.curriculum_id, graph.curriculum_version)
    )

    assert first == second == opened == graph
    assert repository.save_calls == 2


def test_publish_rejects_missing_exact_activity_reference_before_save() -> None:
    service, repository = service_with_placements()
    graph = approved_graph()
    repository.lessons.pop("diversification-reading")

    with pytest.raises(CurriculumGraphError) as captured:
        service.publish_curriculum_graph(PublishCurriculumGraphRequest(graph))

    assert captured.value.code is CurriculumGraphErrorCode.STALE_REFERENCE
    assert repository.save_calls == 0


def test_publish_conflict_preserves_original_version() -> None:
    service, repository = service_with_placements()
    graph = approved_graph()
    service.publish_curriculum_graph(PublishCurriculumGraphRequest(graph))
    changed = replace(graph, title="Changed title", graph_digest="0" * 64)
    changed = replace(changed, graph_digest=curriculum_graph_digest(changed))

    with pytest.raises(CurriculumGraphError) as captured:
        service.publish_curriculum_graph(PublishCurriculumGraphRequest(changed))

    assert captured.value.code is CurriculumGraphErrorCode.IMMUTABLE_CONFLICT
    assert repository.graphs[(graph.curriculum_id, "1.0.0")] == graph


def test_open_never_falls_forward_to_another_version() -> None:
    service, repository = service_with_placements()
    graph = approved_graph()
    later = replace(graph, curriculum_version="1.1.0", graph_digest="0" * 64)
    later = replace(later, graph_digest=curriculum_graph_digest(later))
    repository.graphs[(later.curriculum_id, later.curriculum_version)] = later

    with pytest.raises(CurriculumGraphError) as captured:
        service.open_curriculum_graph(
            OpenCurriculumGraphRequest(graph.curriculum_id, "1.0.0")
        )

    assert captured.value.code is CurriculumGraphErrorCode.NOT_FOUND


def test_open_rejects_corrupt_stored_object_boundedly() -> None:
    service, repository = service_with_placements()
    graph = approved_graph()
    repository.graphs[(graph.curriculum_id, graph.curriculum_version)] = object()

    with pytest.raises(CurriculumGraphError) as captured:
        service.open_curriculum_graph(
            OpenCurriculumGraphRequest(graph.curriculum_id, graph.curriculum_version)
        )

    assert captured.value.code is CurriculumGraphErrorCode.UNAVAILABLE


def test_storage_seam_accepts_graph_without_presentation_order() -> None:
    service, repository = service_with_placements()
    graph = approved_graph()
    flexible = replace(graph, presentation_order=None, graph_digest="0" * 64)
    flexible = replace(
        flexible,
        graph_digest=curriculum_graph_digest(flexible),
    )

    stored = service.publish_curriculum_graph(
        PublishCurriculumGraphRequest(flexible)
    )

    assert stored.presentation_order is None
    assert repository.graphs[(graph.curriculum_id, graph.curriculum_version)] == (
        flexible
    )
