from __future__ import annotations

from dataclasses import fields, replace
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.curriculum.public import (
    CurriculumActivityKind,
    CurriculumBranch,
    CurriculumBranchKind,
    CurriculumGraph,
    CurriculumGraphError,
    CurriculumGraphErrorCode,
    CurriculumRelationship,
    CurriculumRelationshipKind,
    curriculum_graph_digest,
    curriculum_graph_from_mapping,
    validate_curriculum_graph,
)


REPOSITORY = Path(__file__).resolve().parents[4]
APPROVED = (
    REPOSITORY
    / "contracts/compatibility/curriculum-graph/v1/approved/graph.json"
)


def approved_graph() -> CurriculumGraph:
    return curriculum_graph_from_mapping(
        json.loads(APPROVED.read_text(encoding="utf-8"))
    )


def approved_mapping() -> dict[str, object]:
    return json.loads(APPROVED.read_text(encoding="utf-8"))


def with_current_digest(graph: CurriculumGraph) -> CurriculumGraph:
    return replace(graph, graph_digest=curriculum_graph_digest(graph))


def test_public_graph_has_no_provider_storage_or_learner_state() -> None:
    prohibited = {
        "provider_payload",
        "storage_key",
        "database_row",
        "eligibility",
        "mastery",
        "recommendation_score",
        "learner_id",
    }
    assert {field.name for field in fields(CurriculumGraph)}.isdisjoint(prohibited)


def test_domain_rejects_activity_prerequisite_cycle_before_digest() -> None:
    graph = approved_graph()
    reverse = CurriculumRelationship(
        relationship_id="relationship-check-before-lesson",
        kind=CurriculumRelationshipKind.ACTIVITY_PREREQUISITE,
        source_id="activity-risk-return-check",
        target_id="activity-risk-return-lesson",
    )
    changed = with_current_digest(
        replace(graph, relationships=(*graph.relationships, reverse))
    )
    with pytest.raises(CurriculumGraphError) as captured:
        validate_curriculum_graph(changed)
    assert captured.value.code is CurriculumGraphErrorCode.PREREQUISITE_CYCLE


def test_domain_rejects_activity_and_reference_kind_mismatch() -> None:
    graph = approved_graph()
    lesson = graph.activities[0]
    changed_activity = replace(
        lesson,
        kind=CurriculumActivityKind.ASSESSMENT,
    )
    changed = with_current_digest(
        replace(graph, activities=(changed_activity, *graph.activities[1:]))
    )
    with pytest.raises(CurriculumGraphError) as captured:
        validate_curriculum_graph(changed)
    assert (
        captured.value.code
        is CurriculumGraphErrorCode.REFERENCE_KIND_MISMATCH
    )


def test_domain_rejects_stale_graph_digest() -> None:
    graph = approved_graph()
    with pytest.raises(CurriculumGraphError) as captured:
        validate_curriculum_graph(replace(graph, summary=graph.summary + " Changed."))
    assert captured.value.code is CurriculumGraphErrorCode.GRAPH_DIGEST_MISMATCH


def test_mapping_converter_rejects_unknown_client_owned_fields() -> None:
    value = approved_mapping()
    value["eligibility"] = "eligible"
    with pytest.raises(CurriculumGraphError) as captured:
        curriculum_graph_from_mapping(value)
    assert captured.value.code is CurriculumGraphErrorCode.INVALID_RECORD


def test_direct_public_graph_rejects_unknown_relationship_kind_boundedly() -> None:
    graph = approved_graph()
    malformed = replace(graph.relationships[0], kind="unknown")
    changed = replace(
        graph,
        relationships=(malformed, *graph.relationships[1:]),
    )
    with pytest.raises(CurriculumGraphError) as captured:
        validate_curriculum_graph(changed)
    assert captured.value.code is CurriculumGraphErrorCode.INVALID_RECORD


def test_valid_optional_branch_and_partial_order_do_not_force_linear_path() -> None:
    graph = approved_graph()
    flexible = with_current_digest(
        replace(
            graph,
            objectives=tuple(reversed(graph.objectives)),
            activities=tuple(reversed(graph.activities)),
            branches=(
                *graph.branches,
                CurriculumBranch(
                    branch_id="branch-reference",
                    title="Reference material",
                    kind=CurriculumBranchKind.OPTIONAL,
                    activity_ids=("activity-terms-glossary",),
                ),
                CurriculumBranch(
                    branch_id="branch-reference-alternate",
                    title="Alternate reference path",
                    kind=CurriculumBranchKind.OPTIONAL,
                    activity_ids=("activity-terms-glossary",),
                ),
                CurriculumBranch(
                    branch_id="branch-core-alternate",
                    title="Alternate required context",
                    kind=CurriculumBranchKind.REQUIRED,
                    activity_ids=("activity-risk-return-lesson",),
                ),
            ),
            presentation_order=None,
        )
    )
    assert validate_curriculum_graph(flexible) is flexible
