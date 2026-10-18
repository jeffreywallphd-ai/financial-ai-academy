"""Financial AI Academy adapter for the dynamic roadmap review contract."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PLANNING_TOOLS = HERE.parent / "planning"
if str(PLANNING_TOOLS) not in sys.path:
    sys.path.insert(0, str(PLANNING_TOOLS))

from planning_model import as_list, as_text, load_artifacts  # noqa: E402

from contracts import ControlError, success
from financial_academy_portfolio import (
    current_capability_authority,
    planning_nodes,
    project,
)
from portfolio_conflicts import analyze_compatibility
from portfolio_allocation import allocate
from portfolio_ordering import plan
from roadmap_review import build_projection


CATALOG_PATH = "docs/product/capability-catalog.json"
EXPECTED_PRODUCT_CAPABILITIES = 26


def _next_after_current(
    graph: dict[str, Any],
    *,
    allocation: dict[str, Any],
    authority_current: set[str],
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Project the next dependency-ready lane after the current allocation."""

    current_ids = [
        str(lane.get("unit_id", ""))
        for lane in allocation.get("lanes", [])
        if isinstance(lane, dict) and str(lane.get("unit_id", ""))
    ]
    resolved_decisions = {
        str(decision.get("id", ""))
        for decision in decisions
        if decision.get("status") == "complete" and decision.get("decision_record")
    }
    simulated = copy.deepcopy(graph)
    nodes_by_id = {
        str(node.get("id", "")): node
        for node in simulated.get("nodes", [])
        if isinstance(node, dict)
    }
    for current_id in current_ids:
        if current_id in nodes_by_id:
            nodes_by_id[current_id]["status"] = "complete"
    for node in nodes_by_id.values():
        node["decision_gates"] = [
            decision_id
            for decision_id in node.get("decision_gates", [])
            if decision_id not in resolved_decisions
        ]

    future = plan(
        simulated,
        level="capability",
        authority_current=authority_current,
        explicit_priority=[],
        accepted_sequence=[],
    )
    ready_ids = {str(item["id"]) for item in future["ready"]}
    ordered_ids = [
        node_id
        for node_id in future["proposed_order"]
        if node_id in ready_ids and node_id not in current_ids
    ]
    unresolved_ties = []
    for tie in future["unresolved_ties"]:
        ready_tie = [node_id for node_id in tie if node_id in ordered_ids]
        if len(ready_tie) > 1:
            unresolved_ties.append(ready_tie)
    return {
        "assumed_complete": current_ids,
        "lanes": [
            {
                "unit_id": node_id,
                "lifecycle_status": str(nodes_by_id[node_id].get("status", "unknown")),
                "dependencies": [
                    str(dependency.get("target", ""))
                    for dependency in nodes_by_id[node_id].get("dependencies", [])
                    if dependency.get("type") == "hard" and dependency.get("target")
                ],
            }
            for node_id in ordered_ids
        ],
        "unresolved_ties": unresolved_ties,
        "constraints": {
            "grants_authority": False,
            "stable_id_order_is_authority": False,
            "assumes_current_lanes_complete": True,
        },
    }


def _decision_title(text: str, fallback: str) -> str:
    prefix = "# Decision Request:"
    for line in text.splitlines():
        if line.startswith(prefix):
            title = line.removeprefix(prefix).strip()
            return title or fallback
    return fallback


def _repository_reference(root: Path, source: Path, value: str | None) -> str | None:
    if not value:
        return None
    path_value, marker, fragment = value.partition("#")
    root_candidate = (root / path_value).resolve()
    candidate = root_candidate if root_candidate.is_file() else (source.parent / path_value).resolve()
    try:
        confined = candidate.relative_to(root.resolve()).as_posix()
        return f"{confined}{marker}{fragment}"
    except ValueError:
        # The project-neutral projector will reject this unconfined path.
        return value


def _decision_nodes(root: Path, artifacts: list[Any]) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    for artifact in artifacts:
        if artifact.kind != "decision-request":
            continue
        text = artifact.path.read_text(encoding="utf-8")
        decisions.append(
            {
                "id": artifact.identifier,
                "status": artifact.status,
                "title": _decision_title(text, artifact.path.stem),
                "source": artifact.relative_path,
                "dependencies": [
                    {"target": item, "type": "hard"}
                    for item in as_list(artifact.metadata.get("depends_on"))
                ],
                "decision_record": _repository_reference(
                    root,
                    artifact.path,
                    as_text(artifact.metadata.get("decision_record")),
                ),
            }
        )
    return decisions


def _load_catalog(root: Path) -> dict[str, Any]:
    path = root / CATALOG_PATH
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ControlError(
            "roadmap.catalog-unreadable",
            "The machine-readable product capability catalog is unavailable or invalid.",
            {"source": CATALOG_PATH},
            ["Correct docs/product/capability-catalog.json and rerun documentation validation."],
        ) from error
    if not isinstance(value, dict):
        raise ControlError(
            "roadmap.catalog-unreadable",
            "The machine-readable product capability catalog must be a JSON object.",
            {"source": CATALOG_PATH},
            ["Use the capability-catalog-v1 object contract."],
        )
    return value


def projection(root: Path) -> dict[str, Any]:
    graph = project(root)
    nodes = planning_nodes(root)
    artifacts = load_artifacts(root)
    decisions = _decision_nodes(root, artifacts)
    authority_current = current_capability_authority(root)
    ordering = plan(
        graph,
        level="capability",
        authority_current=authority_current,
        explicit_priority=[],
        accepted_sequence=[],
    )
    compatibility = analyze_compatibility(graph, level="capability")
    allocation = allocate(
        graph,
        level="capability",
        authority_current=authority_current,
        explicit_priority=[],
        accepted_sequence=[],
    )
    ordering["next_after_current"] = _next_after_current(
        graph,
        allocation=allocation,
        authority_current=authority_current,
        decisions=decisions,
    )
    documents = {
        artifact.identifier: {
            "source": artifact.relative_path,
            "text": artifact.path.read_text(encoding="utf-8"),
        }
        for artifact in artifacts
        if artifact.kind in {"capability", "vertical-slice", "work-packet", "decision-request"}
    }
    return build_projection(
        catalog=_load_catalog(root),
        planning_nodes=nodes,
        documents=documents,
        graph=graph,
        ordering=ordering,
        compatibility=compatibility,
        allocation=allocation,
        decisions=decisions,
        expected_catalog_count=EXPECTED_PRODUCT_CAPABILITIES,
    )


def result(root: Path) -> dict[str, Any]:
    review = projection(root)
    return success(
        "roadmap.review-projected",
        f"Projected {review['catalog_count']} product capability candidate(s) for review.",
        data={"review": review},
    )
