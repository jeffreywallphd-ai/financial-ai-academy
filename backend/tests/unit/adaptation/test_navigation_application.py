from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.adaptation.application.service import (
    AdaptationService,
    NavigationStateOperationError,
    NavigationStateOperationErrorCode,
    OpenNavigationStateRequest,
)
from financial_ai_academy.modules.adaptation.public import (
    ActivitySourceState,
    CompletionState,
)
from financial_ai_academy.modules.adaptation.ports.navigation_sources import (
    LessonCompletionObservation,
    NavigationSourceError,
    NavigationSourceErrorCode,
)
from financial_ai_academy.modules.curriculum.public import (
    CurriculumBranch,
    CurriculumBranchKind,
    curriculum_graph_digest,
    curriculum_graph_from_mapping,
)


REPOSITORY = Path(__file__).resolve().parents[4]
GRAPH_PATH = (
    REPOSITORY
    / "contracts/compatibility/curriculum-graph/v1/approved/graph.json"
)
LEARNER_ID = "90a46e7e-8cbe-4f63-ab1b-8aa01ef95aa6"
NOW = datetime(2026, 10, 16, 1, 0, tzinfo=timezone.utc)


def graph():
    return curriculum_graph_from_mapping(
        json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    )


class CurriculumSource:
    def __init__(self, value=None) -> None:
        self.value = value or graph()
        self.lesson_availability: dict[str, bool] = {}
        self.assessment_availability: dict[str, bool] = {}
        self.graph_requests = []

    def open_graph(self, request):
        self.graph_requests.append(request)
        if isinstance(self.value, Exception):
            raise self.value
        return self.value

    def lesson_is_available(self, reference) -> bool:
        return self.lesson_availability.get(reference.placement_id, True)

    def assessment_is_available(self, reference) -> bool:
        return self.assessment_availability.get(reference.placement_id, True)


class CompletionSource:
    def __init__(self) -> None:
        self.observations: dict[str, LessonCompletionObservation] = {}
        self.calls: list[tuple[str, str, str]] = []

    def observe_lesson_completion(
        self, *, learner_id, placement_id, fallback_digest
    ) -> LessonCompletionObservation:
        self.calls.append((learner_id, placement_id, fallback_digest))
        return self.observations.get(
            placement_id,
            LessonCompletionObservation(
                CompletionState.INCOMPLETE,
                fallback_digest,
            ),
        )


class Clock:
    def __init__(self, value=NOW) -> None:
        self.value = value

    def now(self):
        return self.value


def request() -> OpenNavigationStateRequest:
    return OpenNavigationStateRequest(
        LEARNER_ID,
        "investing-foundations",
        "1.0.0",
    )


def state(projection, activity_id: str):
    return next(
        item
        for item in projection.activity_states
        if item.activity_id == activity_id
    )


def test_exact_graph_order_and_supported_source_meanings_are_composed() -> None:
    curriculum = CurriculumSource()
    completion = CompletionSource()
    completion.observations["intro-risk-return-primary"] = (
        LessonCompletionObservation(CompletionState.COMPLETED, "a" * 64)
    )
    service = AdaptationService(curriculum, completion, Clock())

    projection = service.open_navigation_state(request())

    assert [item.activity_id for item in projection.activity_states] == [
        item.activity_id for item in graph().activities
    ]
    assert state(
        projection, "activity-risk-return-lesson"
    ).completion is CompletionState.COMPLETED
    assessment = state(projection, "activity-risk-return-check")
    assert assessment.availability is ActivitySourceState.AVAILABLE
    assert assessment.completion is CompletionState.UNAVAILABLE
    assert projection.evaluated_at == NOW
    assert len(completion.calls) == 3
    assert all(call[0] == LEARNER_ID for call in completion.calls)
    assert "learner" not in projection.__dataclass_fields__


@pytest.mark.parametrize(
    ("available", "completion_state"),
    [
        (True, CompletionState.COMPLETED),
        (True, CompletionState.UNAVAILABLE),
        (False, CompletionState.COMPLETED),
        (False, CompletionState.UNAVAILABLE),
    ],
)
def test_source_availability_and_completion_degrade_independently(
    available: bool,
    completion_state: CompletionState,
) -> None:
    curriculum = CurriculumSource()
    curriculum.lesson_availability["intro-risk-return-primary"] = available
    completion = CompletionSource()
    completion.observations["intro-risk-return-primary"] = (
        LessonCompletionObservation(completion_state, "a" * 64)
    )

    result = AdaptationService(
        curriculum, completion, Clock()
    ).open_navigation_state(request())
    lesson = state(result, "activity-risk-return-lesson")

    assert lesson.availability is (
        ActivitySourceState.AVAILABLE
        if available
        else ActivitySourceState.UNAVAILABLE
    )
    assert lesson.completion is completion_state


def test_flexible_graph_order_layout_and_branch_membership_need_no_new_api() -> None:
    original = graph()
    shared = "activity-diversification-reading"
    branches = original.branches + (
        CurriculumBranch(
            branch_id="branch-explore-more",
            title="Explore more",
            kind=CurriculumBranchKind.OPTIONAL,
            activity_ids=(shared,),
        ),
    )
    candidate = replace(
        original,
        activities=tuple(reversed(original.activities)),
        branches=branches,
        presentation_order=None,
        graph_digest="0" * 64,
    )
    flexible = replace(
        candidate,
        graph_digest=curriculum_graph_digest(candidate),
    )

    result = AdaptationService(
        CurriculumSource(flexible), CompletionSource(), Clock()
    ).open_navigation_state(request())

    assert [item.activity_id for item in result.activity_states] == [
        item.activity_id for item in flexible.activities
    ]


def test_graph_failure_and_invalid_context_are_bounded() -> None:
    missing = AdaptationService(
        CurriculumSource(
            NavigationSourceError(NavigationSourceErrorCode.NOT_FOUND)
        ),
        CompletionSource(),
        Clock(),
    )
    with pytest.raises(NavigationStateOperationError) as not_found:
        missing.open_navigation_state(request())
    assert not_found.value.code is NavigationStateOperationErrorCode.NOT_FOUND

    with pytest.raises(NavigationStateOperationError) as invalid:
        AdaptationService(
            CurriculumSource(), CompletionSource(), Clock()
        ).open_navigation_state(replace(request(), learner_id="selected-user"))
    assert invalid.value.code is (
        NavigationStateOperationErrorCode.INVALID_CONTEXT
    )
    assert LEARNER_ID not in str(invalid.value)


def test_cross_version_graph_result_is_rejected_without_partial_state() -> None:
    other_graph = replace(
        graph(),
        curriculum_id="different-curriculum",
    )

    with pytest.raises(NavigationStateOperationError) as captured:
        AdaptationService(
            CurriculumSource(other_graph), CompletionSource(), Clock()
        ).open_navigation_state(request())

    assert captured.value.code is NavigationStateOperationErrorCode.UNAVAILABLE


def test_invalid_clock_or_source_projection_returns_no_partial_result() -> None:
    service = AdaptationService(
        CurriculumSource(),
        CompletionSource(),
        Clock(datetime(2026, 10, 16, 1, 0)),
    )

    with pytest.raises(NavigationStateOperationError) as captured:
        service.open_navigation_state(request())

    assert captured.value.code is NavigationStateOperationErrorCode.UNAVAILABLE
    assert captured.value.safe_message == "Navigation state is currently unavailable."
