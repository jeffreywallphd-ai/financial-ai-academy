from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.adaptation.application.service import (
    AdaptationService,
    OpenActivityLaunchRequest,
)
from financial_ai_academy.modules.adaptation.public import (
    ActivityLaunchError,
    ActivityLaunchErrorCode,
    CompletionState,
)
from financial_ai_academy.modules.adaptation.ports.navigation_sources import (
    LessonCompletionObservation,
)
from financial_ai_academy.modules.curriculum.public import (
    CurriculumRelationship,
    CurriculumRelationshipKind,
    curriculum_graph_digest,
    curriculum_graph_from_mapping,
)


ROOT = Path(__file__).resolve().parents[4]
GRAPH_PATH = ROOT / "contracts/compatibility/curriculum-graph/v1/approved/graph.json"
LEARNER_ID = "90a46e7e-8cbe-4f63-ab1b-8aa01ef95aa6"
NOW = datetime(2026, 10, 16, 1, 0, tzinfo=timezone.utc)


def graph():
    return curriculum_graph_from_mapping(
        json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    )


class CurriculumSource:
    def __init__(self, value=None) -> None:
        self.graph_calls = 0
        self.value = value or graph()
        self.lesson_availability: dict[str, bool] = {}

    def open_graph(self, _request):
        self.graph_calls += 1
        return self.value

    def lesson_is_available(self, reference) -> bool:
        return self.lesson_availability.get(reference.placement_id, True)

    def assessment_is_available(self, _reference) -> bool:
        return True


class CompletionSource:
    def __init__(self) -> None:
        self.observations: dict[str, LessonCompletionObservation] = {}
        self.calls = 0

    def observe_lesson_completion(
        self, *, learner_id, placement_id, fallback_digest
    ) -> LessonCompletionObservation:
        assert learner_id == LEARNER_ID
        self.calls += 1
        return self.observations.get(
            placement_id,
            LessonCompletionObservation(
                CompletionState.INCOMPLETE,
                fallback_digest,
            ),
        )


class Clock:
    def now(self):
        return NOW


def request(
    activity_id: str = "activity-risk-return-lesson",
) -> OpenActivityLaunchRequest:
    return OpenActivityLaunchRequest(
        learner_id=LEARNER_ID,
        curriculum_id="investing-foundations",
        curriculum_version="1.0.0",
        activity_id=activity_id,
    )


def graph_with_locked_optional_lesson():
    original = graph()
    candidate = replace(
        original,
        relationships=original.relationships
        + (
            CurriculumRelationship(
                relationship_id="relationship-lesson-before-diversification",
                kind=CurriculumRelationshipKind.ACTIVITY_PREREQUISITE,
                source_id="activity-risk-return-lesson",
                target_id="activity-diversification-reading",
            ),
        ),
        graph_digest="0" * 64,
    )
    return replace(candidate, graph_digest=curriculum_graph_digest(candidate))


def test_launch_uses_one_fresh_exact_graph_and_projection() -> None:
    curriculum = CurriculumSource()
    completion = CompletionSource()

    result = AdaptationService(
        curriculum, completion, Clock()
    ).open_activity_launch(request())

    assert curriculum.graph_calls == 1
    assert completion.calls == 3
    assert result.activity_id == "activity-risk-return-lesson"
    assert result.placement_id == "intro-risk-return-primary"
    assert result.destination == "/learn/placements/intro-risk-return-primary"
    assert result.evaluated_at == NOW
    assert not hasattr(result, "learner_id")


def test_completed_lesson_resolves_for_review_without_new_evidence() -> None:
    curriculum = CurriculumSource()
    completion = CompletionSource()
    completion.observations["intro-risk-return-primary"] = (
        LessonCompletionObservation(CompletionState.COMPLETED, "a" * 64)
    )

    result = AdaptationService(
        curriculum, completion, Clock()
    ).open_activity_launch(request())

    assert result.destination == "/learn/placements/intro-risk-return-primary"
    assert completion.calls == 3


@pytest.mark.parametrize(
    ("activity_id", "expected"),
    [
        ("activity-risk-return-check", ActivityLaunchErrorCode.UNSUPPORTED_ACTIVITY),
        ("activity-not-present", ActivityLaunchErrorCode.ACTIVITY_NOT_FOUND),
    ],
)
def test_current_policy_denials_remain_bounded(
    activity_id: str,
    expected: ActivityLaunchErrorCode,
) -> None:
    with pytest.raises(ActivityLaunchError) as captured:
        AdaptationService(
            CurriculumSource(), CompletionSource(), Clock()
        ).open_activity_launch(request(activity_id))

    assert captured.value.code is expected
    assert "destination" not in captured.value.as_dict()
    assert LEARNER_ID not in str(captured.value)


def test_new_graph_prerequisite_is_rechecked_before_launch() -> None:
    with pytest.raises(ActivityLaunchError) as captured:
        AdaptationService(
            CurriculumSource(graph_with_locked_optional_lesson()),
            CompletionSource(),
            Clock(),
        ).open_activity_launch(request("activity-diversification-reading"))

    assert captured.value.code is ActivityLaunchErrorCode.ACTIVITY_LOCKED


def test_current_source_unavailability_cannot_return_a_stale_launch() -> None:
    curriculum = CurriculumSource()
    curriculum.lesson_availability["intro-risk-return-primary"] = False

    with pytest.raises(ActivityLaunchError) as captured:
        AdaptationService(
            curriculum, CompletionSource(), Clock()
        ).open_activity_launch(request())

    assert captured.value.code is ActivityLaunchErrorCode.ACTIVITY_UNAVAILABLE
    assert curriculum.graph_calls == 1
