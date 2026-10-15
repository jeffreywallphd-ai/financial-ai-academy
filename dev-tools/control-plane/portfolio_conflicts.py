"""Project-neutral pairwise compatibility and parallel-safe grouping."""

from __future__ import annotations

from itertools import combinations
from typing import Any, Iterable

from contracts import ControlError


SCHEMA_VERSION = "portfolio-compatibility-v1"
LEVEL_KIND = {"capability": "capability", "slice": "slice", "work": "work"}
ACTIVE_STATUSES = {"ready", "active", "verifying"}


def _path(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/").casefold()


def _overlap(left: Iterable[str], right: Iterable[str]) -> list[tuple[str, str]]:
    overlaps: list[tuple[str, str]] = []
    for first_raw in sorted(set(left)):
        first = _path(first_raw)
        for second_raw in sorted(set(right)):
            second = _path(second_raw)
            if not first or not second:
                continue
            if first == second or first.startswith(second + "/") or second.startswith(first + "/"):
                overlaps.append((first_raw, second_raw))
    return overlaps


def _reachable(source: str, target: str, adjacency: dict[str, list[str]]) -> bool:
    pending = list(adjacency.get(source, []))
    seen: set[str] = set()
    while pending:
        current = pending.pop()
        if current == target:
            return True
        if current in seen:
            continue
        seen.add(current)
        pending.extend(adjacency.get(current, []))
    return False


def _pair(left: dict[str, Any], right: dict[str, Any], adjacency: dict[str, list[str]], level: str) -> dict[str, Any]:
    left_id, right_id = str(left["id"]), str(right["id"])
    reasons: list[dict[str, Any]] = []
    if _reachable(left_id, right_id, adjacency) or _reachable(right_id, left_id, adjacency):
        reasons.append({"code": "dependency.path", "evidence": [left_id, right_id]})

    path_checks = (
        ("scope.write-overlap", left.get("write_scope", []), right.get("write_scope", [])),
        ("scope.write-generated-overlap", left.get("write_scope", []), right.get("generated_artifacts", [])),
        ("scope.write-generated-overlap", left.get("generated_artifacts", []), right.get("write_scope", [])),
        ("scope.generated-overlap", left.get("generated_artifacts", []), right.get("generated_artifacts", [])),
        ("contract.overlap", left.get("contracts", []), right.get("contracts", [])),
    )
    for code, left_paths, right_paths in path_checks:
        matches = _overlap(left_paths, right_paths)
        if matches:
            reasons.append({"code": code, "evidence": [list(item) for item in matches]})

    shared_resources = sorted(set(left.get("exclusive_resources", [])) & set(right.get("exclusive_resources", [])))
    if shared_resources:
        reasons.append({"code": "resource.exclusive-overlap", "evidence": shared_resources})
    shared_branches = sorted(set(left.get("branches", [])) & set(right.get("branches", [])))
    if shared_branches and left.get("active_claim") and right.get("active_claim"):
        reasons.append({"code": "branch.active-overlap", "evidence": shared_branches})

    if reasons:
        return {"left": left_id, "right": right_id, "decision": "incompatible", "confidence": "high", "reasons": reasons, "remediation": "Sequence the pair or remove the named dependency or exclusive overlap."}

    unknown: list[dict[str, Any]] = []
    if not left.get("scope_complete"):
        unknown.append({"code": "evidence.scope-incomplete", "evidence": [left_id]})
    if not right.get("scope_complete"):
        unknown.append({"code": "evidence.scope-incomplete", "evidence": [right_id]})
    if level == "work":
        reciprocal = right_id in left.get("parallel_safe_with", []) and left_id in right.get("parallel_safe_with", [])
        if not reciprocal:
            unknown.append({"code": "evidence.reciprocal-declaration-missing", "evidence": [left_id, right_id]})
    if unknown:
        return {"left": left_id, "right": right_id, "decision": "unknown", "confidence": "low", "reasons": unknown, "remediation": "Refine only the named scopes or reciprocal packet declarations, then recompute."}
    return {"left": left_id, "right": right_id, "decision": "compatible", "confidence": "high", "reasons": [{"code": "evidence.disjoint", "evidence": [left_id, right_id]}], "remediation": None}


def analyze_compatibility(graph: dict[str, Any], *, level: str, candidate_ids: Iterable[str] | None = None) -> dict[str, Any]:
    if level not in LEVEL_KIND:
        raise ControlError("compatibility.level-invalid", "Compatibility requires capability, slice, or work granularity.", {"level": level}, ["Choose capability, slice, or work."])
    if graph.get("schema_version") != "portfolio-graph-v1":
        raise ControlError("compatibility.graph-incompatible", "The portfolio graph contract is incompatible.", {}, ["Regenerate the graph with a compatible adapter."])
    blocking = [item for item in graph.get("issues", []) if item.get("blocking")]
    if blocking:
        raise ControlError("compatibility.graph-invalid", "Blocking graph issues prevent reliable compatibility analysis.", {"issue_codes": sorted({str(item.get('code')) for item in blocking})}, ["Resolve graph issues first."])
    nodes = {str(item.get("id")): dict(item) for item in graph.get("nodes", [])}
    eligible = sorted(node_id for node_id, node in nodes.items() if node.get("kind") == LEVEL_KIND[level] and node.get("status") in ACTIVE_STATUSES)
    if candidate_ids is not None:
        requested = sorted({str(item) for item in candidate_ids})
        unknown = sorted(set(requested) - set(eligible))
        if unknown:
            raise ControlError("compatibility.candidate-ineligible", "Requested compatibility IDs are absent or not active at this level.", {"ids": unknown}, ["Choose ready, active, or verifying IDs at the requested level."])
        eligible = requested
    adjacency = {node_id: [str(item.get("target")) for item in node.get("dependencies", []) if item.get("type") == "hard"] for node_id, node in nodes.items()}
    pairs = [_pair(nodes[left], nodes[right], adjacency, level) for left, right in combinations(eligible, 2)]
    decisions = {(item["left"], item["right"]): item["decision"] for item in pairs}

    groups: list[list[str]] = []
    for node_id in eligible:
        placed = False
        for group in groups:
            if all(decisions.get(tuple(sorted((node_id, member)))) == "compatible" for member in group):
                group.append(node_id)
                placed = True
                break
        if not placed:
            groups.append([node_id])
    parallel_safe_sets = [group for group in groups if len(group) > 1]
    isolated = [group[0] for group in groups if len(group) == 1]
    return {
        "schema_version": SCHEMA_VERSION,
        "level": level,
        "considered_ids": eligible,
        "pairs": pairs,
        "parallel_safe_sets": parallel_safe_sets,
        "isolated_or_unresolved": isolated,
        "compatible_pair_count": sum(item["decision"] == "compatible" for item in pairs),
        "incompatible_pair_count": sum(item["decision"] == "incompatible" for item in pairs),
        "unknown_pair_count": sum(item["decision"] == "unknown" for item in pairs),
    }
