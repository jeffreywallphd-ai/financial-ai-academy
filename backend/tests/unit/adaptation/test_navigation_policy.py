from __future__ import annotations

import copy
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.adaptation.public import (
    ActivitySourceFact,
    ActivitySourceState,
    CompletionState,
    EligibilityState,
    EvaluateNavigationStateRequest,
    NavigationReasonCode,
    NavigationStateError,
    NavigationStateErrorCode,
    RequirementState,
    evaluate_navigation_state,
    navigation_state_payload,
)
from financial_ai_academy.modules.curriculum.public import (
    CurriculumBranch,
    CurriculumBranchKind,
    CurriculumRelationship,
    CurriculumRelationshipKind,
    curriculum_graph_digest,
    curriculum_graph_from_mapping,
)


REPOSITORY = Path(__file__).resolve().parents[4]
GRAPH_PATH = (
    REPOSITORY
    / "contracts/compatibility/curriculum-graph/v1/approved/graph.json"
)
SOURCE_PATH = (
    REPOSITORY
    / "contracts/compatibility/adaptation-navigation/v1/approved/source-facts.json"
)


def _graph():
    return curriculum_graph_from_mapping(
        json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    )


def _facts() -> tuple[ActivitySourceFact, ...]:
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    return tuple(
        ActivitySourceFact(
            item["activity_id"],
            ActivitySourceState(item["activity_source_state"]),
            CompletionState(item["completion_state"]),
            item["source_digest"],
        )
        for item in source["activity_facts"]
    )


def _request(*, graph=None, facts=None, evaluated_at=None):
    return EvaluateNavigationStateRequest(
        graph=graph or _graph(),
        activity_facts=facts or _facts(),
        evaluated_at=evaluated_at
        or datetime(2026, 10, 16, tzinfo=timezone.utc),
    )


def _state(projection, activity_id: str):
    return next(
        item for item in projection.activity_states if item.activity_id == activity_id
    )


def _with_fact(
    facts: tuple[ActivitySourceFact, ...],
    activity_id: str,
    **changes,
) -> tuple[ActivitySourceFact, ...]:
    return tuple(
        replace(fact, **changes) if fact.activity_id == activity_id else fact
        for fact in facts
    )


def _redigest(graph, **changes):
    candidate = replace(graph, graph_digest="0" * 64, **changes)
    return replace(candidate, graph_digest=curriculum_graph_digest(candidate))


def test_incomplete_prerequisite_locks_then_exact_completion_unlocks() -> None:
    incomplete = _with_fact(
        _facts(),
        "activity-risk-return-lesson",
        completion_state=CompletionState.INCOMPLETE,
    )
    locked = _state(
        evaluate_navigation_state(_request(facts=incomplete)),
        "activity-risk-return-check",
    )
    assert locked.eligibility is EligibilityState.LOCKED
    assert [reason.code for reason in locked.reasons] == [
        NavigationReasonCode.REQUIRED_ACTIVITY,
        NavigationReasonCode.PREREQUISITE_INCOMPLETE,
    ]

    eligible = _state(
        evaluate_navigation_state(_request()),
        "activity-risk-return-check",
    )
    assert eligible.eligibility is EligibilityState.ELIGIBLE
    assert eligible.reasons[-1].code is (
        NavigationReasonCode.PREREQUISITE_SATISFIED
    )


def test_optional_requirement_is_independent_of_other_state_dimensions() -> None:
    activity_id = "activity-diversification-reading"
    base = _facts()
    eligible = _state(
        evaluate_navigation_state(_request(facts=base)),
        activity_id,
    )
    complete = _state(
        evaluate_navigation_state(
            _request(
                facts=_with_fact(
                    base,
                    activity_id,
                    completion_state=CompletionState.COMPLETED,
                )
            )
        ),
        activity_id,
    )
    unavailable = _state(
        evaluate_navigation_state(
            _request(
                facts=_with_fact(
                    base,
                    activity_id,
                    activity_source_state=ActivitySourceState.UNAVAILABLE,
                )
            )
        ),
        activity_id,
    )
    assert eligible.requirement is RequirementState.OPTIONAL
    assert complete.requirement is RequirementState.OPTIONAL
    assert unavailable.requirement is RequirementState.OPTIONAL
    assert eligible.eligibility is EligibilityState.ELIGIBLE
    assert complete.completion is CompletionState.COMPLETED
    assert unavailable.eligibility is EligibilityState.UNAVAILABLE


def test_flexible_graph_shapes_preserve_graph_order_without_hint_dependency() -> None:
    graph = _graph()
    activities = tuple(reversed(graph.activities))
    branches = graph.branches + (
        CurriculumBranch(
            branch_id="branch-explore-alternate",
            title="Alternate exploration",
            kind=CurriculumBranchKind.OPTIONAL,
            activity_ids=("activity-diversification-reading",),
        ),
    )
    flexible = _redigest(
        graph,
        activities=activities,
        branches=branches,
        presentation_order=None,
    )
    projection = evaluate_navigation_state(
        _request(graph=flexible, facts=tuple(reversed(_facts())))
    )
    assert [state.activity_id for state in projection.activity_states] == [
        activity.activity_id for activity in activities
    ]
    assert _state(
        projection, "activity-diversification-reading"
    ).requirement is RequirementState.OPTIONAL
    assert _state(
        projection, "activity-terms-glossary"
    ).requirement is RequirementState.UNASSIGNED


def test_multiple_prerequisites_emit_one_reason_per_edge_in_graph_order() -> None:
    graph = _graph()
    extra = CurriculumRelationship(
        relationship_id="relationship-glossary-before-check",
        kind=CurriculumRelationshipKind.ACTIVITY_PREREQUISITE,
        source_id="activity-terms-glossary",
        target_id="activity-risk-return-check",
    )
    graph = _redigest(graph, relationships=graph.relationships + (extra,))
    state = _state(
        evaluate_navigation_state(_request(graph=graph)),
        "activity-risk-return-check",
    )
    assert state.eligibility is EligibilityState.LOCKED
    assert [reason.code for reason in state.reasons] == [
        NavigationReasonCode.REQUIRED_ACTIVITY,
        NavigationReasonCode.PREREQUISITE_INCOMPLETE,
    ]
    assert state.reasons[-1].references == (
        "activity-risk-return-check",
        "activity-terms-glossary",
        "relationship-glossary-before-check",
    )


def test_unavailable_prerequisite_and_completion_sources_fail_closed() -> None:
    unavailable_prerequisite = _with_fact(
        _facts(),
        "activity-risk-return-lesson",
        completion_state=CompletionState.UNAVAILABLE,
    )
    prerequisite = _state(
        evaluate_navigation_state(_request(facts=unavailable_prerequisite)),
        "activity-risk-return-check",
    )
    assert prerequisite.eligibility is EligibilityState.LOCKED
    assert prerequisite.reasons[-1].code is (
        NavigationReasonCode.PREREQUISITE_UNAVAILABLE
    )

    own = _state(
        evaluate_navigation_state(_request(facts=unavailable_prerequisite)),
        "activity-risk-return-lesson",
    )
    assert own.eligibility is EligibilityState.UNAVAILABLE
    assert own.reasons[-1].code is (
        NavigationReasonCode.COMPLETION_SOURCE_UNAVAILABLE
    )


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "unknown", "bad"])
def test_source_fact_closure_is_exact_and_bounded(mutation: str) -> None:
    facts = list(_facts())
    if mutation == "missing":
        facts.pop()
    elif mutation == "duplicate":
        facts[-1] = facts[0]
    elif mutation == "unknown":
        facts[-1] = replace(facts[-1], activity_id="activity-unknown")
    else:
        facts[-1] = replace(facts[-1], source_digest="not-a-digest")
    with pytest.raises(NavigationStateError) as captured:
        evaluate_navigation_state(_request(facts=tuple(facts)))
    assert captured.value.code is NavigationStateErrorCode.INVALID_SOURCE_FACTS
    assert len(captured.value.reference) <= 120


def test_invalid_graph_and_time_are_adaptation_bounded_errors() -> None:
    with pytest.raises(NavigationStateError) as graph_failure:
        evaluate_navigation_state(
            _request(graph=replace(_graph(), graph_digest="f" * 64))
        )
    assert graph_failure.value.code is NavigationStateErrorCode.INVALID_GRAPH

    with pytest.raises(NavigationStateError) as time_failure:
        evaluate_navigation_state(
            _request(evaluated_at=datetime(2026, 10, 16))
        )
    assert time_failure.value.code is NavigationStateErrorCode.INVALID_CONTEXT


def test_exact_input_replay_is_byte_and_digest_stable() -> None:
    first = evaluate_navigation_state(_request())
    second = evaluate_navigation_state(_request(facts=tuple(reversed(_facts()))))
    assert navigation_state_payload(first) == navigation_state_payload(second)
    assert first.source_set_digest == second.source_set_digest
    assert first.projection_digest == second.projection_digest
    assert "mastery" not in json.dumps(navigation_state_payload(first))
    assert "recommendation" not in json.dumps(navigation_state_payload(first))
