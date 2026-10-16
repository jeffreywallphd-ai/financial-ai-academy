from __future__ import annotations

from dataclasses import replace
from datetime import datetime
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.adaptation.public import (
    ActivityLaunchError,
    ActivityLaunchErrorCode,
    ActivityNavigationState,
    ActivitySourceFact,
    ActivitySourceState,
    CompletionState,
    EligibilityState,
    EvaluateNavigationStateRequest,
    NavigationReason,
    NavigationReasonCode,
    NavigationStateProjection,
    RequirementState,
    ResolveActivityLaunchRequest,
    activity_launch_payload,
    evaluate_navigation_state,
    navigation_projection_digest,
    resolve_activity_launch,
)
from financial_ai_academy.modules.curriculum.public import (
    curriculum_graph_digest,
    curriculum_graph_from_mapping,
)


ROOT = Path(__file__).resolve().parents[4]
GRAPH_PATH = ROOT / "contracts/compatibility/curriculum-graph/v1/approved/graph.json"
NAVIGATION_PATH = ROOT / "contracts/compatibility/adaptation-navigation/v1/approved/navigation-state.json"
SOURCE_PATH = ROOT / "contracts/compatibility/adaptation-navigation/v1/approved/source-facts.json"
LAUNCH_PATH = ROOT / "contracts/compatibility/adaptation-activity-launch/v1/approved/launch.json"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _graph():
    return curriculum_graph_from_mapping(_json(GRAPH_PATH))


def _projection() -> NavigationStateProjection:
    value = _json(NAVIGATION_PATH)
    return NavigationStateProjection(
        schema_version=value["schema_version"],
        curriculum_id=value["curriculum_id"],
        curriculum_version=value["curriculum_version"],
        graph_digest=value["graph_digest"],
        policy_id=value["policy_id"],
        policy_version=value["policy_version"],
        evaluated_at=datetime.fromisoformat(value["evaluated_at"].replace("Z", "+00:00")),
        source_set_digest=value["source_set_digest"],
        activity_states=tuple(
            ActivityNavigationState(
                activity_id=item["activity_id"],
                completion=CompletionState(item["completion"]),
                eligibility=EligibilityState(item["eligibility"]),
                requirement=RequirementState(item["requirement"]),
                availability=ActivitySourceState(item["availability"]),
                reasons=tuple(
                    NavigationReason(
                        code=NavigationReasonCode(reason["code"]),
                        explanation=reason["explanation"],
                        references=tuple(reason["references"]),
                    )
                    for reason in item["reasons"]
                ),
            )
            for item in value["activity_states"]
        ),
        projection_digest=value["projection_digest"],
    )


def _facts() -> tuple[ActivitySourceFact, ...]:
    return tuple(
        ActivitySourceFact(
            activity_id=item["activity_id"],
            activity_source_state=ActivitySourceState(item["activity_source_state"]),
            completion_state=CompletionState(item["completion_state"]),
            source_digest=item["source_digest"],
        )
        for item in _json(SOURCE_PATH)["activity_facts"]
    )


def _request(
    activity_id: str = "activity-risk-return-lesson",
    *,
    graph=None,
    projection=None,
) -> ResolveActivityLaunchRequest:
    return ResolveActivityLaunchRequest(
        graph=graph or _graph(),
        navigation_state=projection or _projection(),
        activity_id=activity_id,
    )


def _state_change(projection: NavigationStateProjection, activity_id: str, **changes) -> NavigationStateProjection:
    states = tuple(
        replace(state, **changes) if state.activity_id == activity_id else state
        for state in projection.activity_states
    )
    candidate = replace(projection, activity_states=states, projection_digest="0" * 64)
    return replace(candidate, projection_digest=navigation_projection_digest(candidate))


def test_approved_completed_lesson_resolves_exact_contract_for_review() -> None:
    request = _request()
    before_graph = request.graph
    before_projection = request.navigation_state
    first = activity_launch_payload(resolve_activity_launch(request))
    second = activity_launch_payload(resolve_activity_launch(request))

    assert first == _json(LAUNCH_PATH)
    assert second == first
    assert request.graph is before_graph
    assert request.navigation_state is before_projection
    assert set(first) == {
        "schema_version",
        "curriculum_id",
        "curriculum_version",
        "graph_digest",
        "activity_id",
        "navigation_projection_digest",
        "evaluated_at",
        "placement_id",
        "package_id",
        "package_version",
        "package_digest",
        "destination",
    }


@pytest.mark.parametrize(
    "activity_id",
    ["activity-diversification-reading", "activity-terms-glossary"],
)
def test_optional_and_unbranched_eligible_lessons_need_no_special_case(activity_id: str) -> None:
    result = resolve_activity_launch(_request(activity_id))
    reference = next(
        item.reference for item in _graph().activities if item.activity_id == activity_id
    )
    assert result.placement_id == reference.placement_id
    assert result.destination == f"/learn/placements/{reference.placement_id}"


def test_locked_activity_is_denied_without_destination() -> None:
    projection = _state_change(
        _projection(),
        "activity-risk-return-lesson",
        eligibility=EligibilityState.LOCKED,
    )
    with pytest.raises(ActivityLaunchError) as captured:
        resolve_activity_launch(_request(projection=projection))
    assert captured.value.code is ActivityLaunchErrorCode.ACTIVITY_LOCKED
    assert "destination" not in captured.value.as_dict()


@pytest.mark.parametrize(
    "changes",
    [
        {"availability": ActivitySourceState.UNAVAILABLE},
        {"completion": CompletionState.UNAVAILABLE},
        {"eligibility": EligibilityState.UNAVAILABLE},
    ],
)
def test_unavailable_dimensions_fail_closed(changes: dict) -> None:
    projection = _state_change(
        _projection(),
        "activity-risk-return-lesson",
        **changes,
    )
    with pytest.raises(ActivityLaunchError) as captured:
        resolve_activity_launch(_request(projection=projection))
    assert captured.value.code is ActivityLaunchErrorCode.ACTIVITY_UNAVAILABLE


def test_assessment_activity_is_explicitly_unsupported() -> None:
    with pytest.raises(ActivityLaunchError) as captured:
        resolve_activity_launch(_request("activity-risk-return-check"))
    assert captured.value.code is ActivityLaunchErrorCode.UNSUPPORTED_ACTIVITY


@pytest.mark.parametrize(
    "activity_id,expected",
    [
        ("activity-unknown", ActivityLaunchErrorCode.ACTIVITY_NOT_FOUND),
        ("unsafe/activity", ActivityLaunchErrorCode.INVALID_CONTEXT),
        ("private\nactivity", ActivityLaunchErrorCode.INVALID_CONTEXT),
    ],
)
def test_unknown_and_malformed_activity_ids_are_bounded(activity_id: str, expected: ActivityLaunchErrorCode) -> None:
    with pytest.raises(ActivityLaunchError) as captured:
        resolve_activity_launch(_request(activity_id))
    assert captured.value.code is expected
    assert len(captured.value.reference) <= 120
    assert "\n" not in captured.value.reference


@pytest.mark.parametrize("mutation", ["curriculum", "order", "digest", "time"])
def test_mismatched_or_tampered_navigation_context_fails_closed(mutation: str) -> None:
    projection = _projection()
    if mutation == "curriculum":
        projection = replace(projection, curriculum_version="2.0.0")
    elif mutation == "order":
        projection = replace(
            projection,
            activity_states=tuple(reversed(projection.activity_states)),
        )
    elif mutation == "digest":
        projection = replace(projection, projection_digest="f" * 64)
    else:
        projection = replace(projection, evaluated_at=datetime(2026, 10, 16))
    with pytest.raises(ActivityLaunchError) as captured:
        resolve_activity_launch(_request(projection=projection))
    assert captured.value.code is ActivityLaunchErrorCode.INVALID_CONTEXT


def test_reordered_graph_and_projection_remain_exact_without_shape_assumptions() -> None:
    graph = _graph()
    candidate = replace(
        graph,
        activities=tuple(reversed(graph.activities)),
        graph_digest="0" * 64,
    )
    graph = replace(candidate, graph_digest=curriculum_graph_digest(candidate))
    navigation = evaluate_navigation_state(
        EvaluateNavigationStateRequest(
            graph=graph,
            activity_facts=tuple(reversed(_facts())),
            evaluated_at=_projection().evaluated_at,
        )
    )
    lesson_ids = [
        item.activity_id for item in graph.activities if item.kind.value == "lesson"
    ]
    assert [
        resolve_activity_launch(
            _request(activity_id, graph=graph, projection=navigation)
        ).activity_id
        for activity_id in lesson_ids
    ] == lesson_ids


def test_error_payload_never_exposes_context_or_destination() -> None:
    with pytest.raises(ActivityLaunchError) as captured:
        resolve_activity_launch(_request("private\nactivity"))
    payload = captured.value.as_dict()
    rendered = json.dumps(payload)
    assert set(payload) == {"code", "message", "reference"}
    assert "destination" not in rendered
    assert "learner" not in rendered
    assert "Traceback" not in rendered
