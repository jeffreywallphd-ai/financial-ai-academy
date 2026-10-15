"""Project-neutral readiness and dependency-respecting portfolio ordering."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from contracts import ControlError


SCHEMA_VERSION = "portfolio-plan-v1"
LEVEL_KIND = {"capability": "capability", "slice": "slice", "work": "work"}
COMPLETED = {"complete", "superseded"}
IN_PROGRESS = {"active", "verifying"}


def _validate_sequence(name: str, values: Iterable[str], selected: set[str]) -> list[str]:
    sequence = [str(value).strip() for value in values]
    if any(not value for value in sequence) or len(sequence) != len(set(sequence)):
        raise ControlError(f"portfolio.{name}-invalid", f"The {name.replace('_', ' ')} must contain unique non-empty IDs.", {name: sequence}, ["Provide each selected work ID at most once."])
    unknown = sorted(set(sequence) - selected)
    if unknown:
        raise ControlError(f"portfolio.{name}-outside-level", f"The {name.replace('_', ' ')} names work outside the selected level.", {"unknown_ids": unknown}, ["Choose IDs present at the requested portfolio level."])
    return sequence


def _capability_ancestor(node_id: str, by_id: dict[str, dict[str, Any]]) -> str | None:
    seen: set[str] = set()
    current = by_id.get(node_id)
    while current and current.get("id") not in seen:
        seen.add(str(current.get("id")))
        if current.get("kind") == "capability":
            return str(current.get("id"))
        parent = current.get("parent")
        current = by_id.get(str(parent)) if parent else None
    return None


def plan(
    graph: dict[str, Any],
    *,
    level: str,
    authority_current: Iterable[str] = (),
    explicit_priority: Iterable[str] = (),
    accepted_sequence: Iterable[str] = (),
) -> dict[str, Any]:
    """Return current readiness plus one explainable proposed order."""

    if level not in LEVEL_KIND:
        raise ControlError("portfolio.level-invalid", "Portfolio planning requires capability, slice, or work granularity.", {"level": level}, ["Choose --level capability, slice, or work."])
    if graph.get("schema_version") != "portfolio-graph-v1":
        raise ControlError("portfolio.graph-incompatible", "The portfolio graph contract is incompatible.", {"schema_version": graph.get("schema_version")}, ["Regenerate the graph with a compatible adapter."])
    blocking_graph_issues = [item for item in graph.get("issues", []) if item.get("blocking")]
    if blocking_graph_issues:
        raise ControlError("portfolio.graph-invalid", "Blocking graph issues prevent a trustworthy proposed order.", {"issue_codes": sorted({str(item.get('code')) for item in blocking_graph_issues})}, ["Resolve the reported graph issues before ordering work."])

    nodes = [dict(item) for item in graph.get("nodes", [])]
    by_id = {str(item.get("id")): item for item in nodes}
    selected_nodes = sorted((item for item in nodes if item.get("kind") == LEVEL_KIND[level]), key=lambda item: str(item.get("id")))
    selected_ids = {str(item.get("id")) for item in selected_nodes}
    priority = _validate_sequence("explicit_priority", explicit_priority, selected_ids)
    roadmap = _validate_sequence("accepted_sequence", accepted_sequence, selected_ids)
    authority = {str(item) for item in authority_current}
    priority_rank = {item: index for index, item in enumerate(priority)}
    roadmap_rank = {item: index for index, item in enumerate(roadmap)}

    ready: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    completed: list[str] = []
    in_progress: list[str] = []
    sequence_candidates: set[str] = set()
    hard_blocked: set[str] = set()

    for node in selected_nodes:
        node_id = str(node["id"])
        status = str(node.get("status", "unknown"))
        if status in COMPLETED:
            completed.append(node_id)
            continue
        if status in IN_PROGRESS:
            in_progress.append(node_id)
            continue
        reasons: list[str] = []
        cap_id = _capability_ancestor(node_id, by_id)
        if not cap_id or cap_id not in authority:
            reasons.append("authority.cap-package-not-current")
        if node.get("decision_gates"):
            reasons.append("decision.unresolved")
        if status != "ready":
            reasons.append("lifecycle.not-ready")
        parent_id = node.get("parent")
        if level != "capability":
            parent = by_id.get(str(parent_id)) if parent_id else None
            if parent is None:
                reasons.append("hierarchy.parent-missing")
            elif str(parent.get("status")) not in {"ready", "active", "verifying", "complete"}:
                reasons.append("hierarchy.parent-not-deliverable")
        dependency_ids = [str(item.get("target")) for item in node.get("dependencies", []) if item.get("type") == "hard"]
        incomplete = sorted(target for target in dependency_ids if str(by_id.get(target, {}).get("status")) not in COMPLETED)
        fundamental = [reason for reason in reasons if reason != "dependency.incomplete"]
        if fundamental:
            blocked.append({"id": node_id, "reasons": sorted(set(reasons)), "incomplete_dependencies": incomplete, "remediation": "Resolve the named authority, decision, hierarchy, or lifecycle condition."})
            hard_blocked.add(node_id)
            continue
        sequence_candidates.add(node_id)
        if incomplete:
            blocked.append({"id": node_id, "reasons": ["dependency.incomplete"], "incomplete_dependencies": incomplete, "remediation": "Complete the named dependencies first."})
        else:
            ready.append({"id": node_id, "reasons": ["authority.current", "dependencies.satisfied", "lifecycle.ready"]})

    candidate_dependencies: dict[str, list[str]] = {}
    dependents: dict[str, list[str]] = defaultdict(list)
    indegree = {node_id: 0 for node_id in sequence_candidates}
    for node_id in sorted(sequence_candidates):
        node = by_id[node_id]
        dependencies = sorted({str(item.get("target")) for item in node.get("dependencies", []) if item.get("type") == "hard" and str(item.get("target")) in sequence_candidates})
        candidate_dependencies[node_id] = dependencies
        indegree[node_id] = len(dependencies)
        for dependency in dependencies:
            dependents[dependency].append(node_id)

    def order_key(node_id: str) -> tuple[int, int, int, int, str]:
        return (
            0 if node_id in roadmap_rank else 1,
            roadmap_rank.get(node_id, len(roadmap)),
            0 if node_id in priority_rank else 1,
            priority_rank.get(node_id, len(priority)),
            node_id,
        )

    available = sorted((node_id for node_id, count in indegree.items() if count == 0), key=order_key)
    proposed: list[str] = []
    layers: list[list[str]] = []
    while available:
        current_layer = sorted(available, key=order_key)
        layers.append(current_layer)
        available = []
        for node_id in current_layer:
            proposed.append(node_id)
            for dependent in sorted(dependents.get(node_id, [])):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    available.append(dependent)

    ties: list[list[str]] = []
    for layer in layers:
        unranked = [item for item in layer if item not in priority_rank and item not in roadmap_rank]
        if len(unranked) > 1:
            ties.append(sorted(unranked))

    return {
        "schema_version": SCHEMA_VERSION,
        "level": level,
        "ready": ready,
        "blocked": sorted(blocked, key=lambda item: item["id"]),
        "completed": sorted(completed),
        "in_progress": sorted(in_progress),
        "proposed_order": proposed,
        "unresolved_ties": ties,
        "constraints": {
            "accepted_sequence": roadmap,
            "explicit_priority": priority,
            "stable_id_order_is_authority": False,
        },
        "omitted_hard_blocked": sorted(hard_blocked),
    }
