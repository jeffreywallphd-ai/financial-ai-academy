"""Project-neutral hierarchy-aware allocation and deterministic replanning."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable

from contracts import ControlError
from portfolio_conflicts import analyze_compatibility
from portfolio_ordering import LEVEL_KIND, plan


SCHEMA_VERSION = "portfolio-allocation-v1"


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _descendant(candidate: str, ancestor: str, by_id: dict[str, dict[str, Any]]) -> bool:
    seen: set[str] = set()
    current = by_id.get(candidate)
    while current and str(current.get("id")) not in seen:
        current_id = str(current.get("id"))
        seen.add(current_id)
        parent = current.get("parent")
        if not parent:
            return False
        if str(parent) == ancestor:
            return True
        current = by_id.get(str(parent))
    return False


def _coordination_for(unit_id: str, by_id: dict[str, dict[str, Any]], coordination: dict[str, Any]) -> dict[str, Any]:
    intent_paths: set[str] = set()
    live_paths: set[str] = set()
    expired_paths: set[str] = set()

    def belongs(record: dict[str, Any]) -> bool:
        direct = str(record.get("unit_id", ""))
        work = str(record.get("work_id", ""))
        return direct == unit_id or work == unit_id or _descendant(work, unit_id, by_id)

    for item in coordination.get("intents", []) if isinstance(coordination.get("intents"), list) else []:
        if isinstance(item, dict) and belongs(item):
            intent_paths.update(str(path) for path in item.get("paths", []) if str(path))
    for item in coordination.get("leases", []) if isinstance(coordination.get("leases"), list) else []:
        if not isinstance(item, dict) or not belongs(item):
            continue
        target = live_paths if item.get("state") == "live" else expired_paths
        target.update(str(path) for path in item.get("paths", []) if str(path))
    return {
        "intent_count": len(intent_paths),
        "intent_paths": sorted(intent_paths),
        "live_lease_count": len(live_paths),
        "live_lease_paths": sorted(live_paths),
        "expired_lease_count": len(expired_paths),
        "expired_lease_paths": sorted(expired_paths),
    }


def _groups(ordered_ids: list[str], compatibility: dict[str, Any]) -> tuple[list[list[str]], list[dict[str, Any]]]:
    decisions = {(str(item["left"]), str(item["right"])): str(item["decision"]) for item in compatibility.get("pairs", [])}
    groups: list[list[str]] = []
    for node_id in ordered_ids:
        for group in groups:
            if all(decisions.get(tuple(sorted((node_id, member)))) == "compatible" for member in group):
                group.append(node_id)
                break
        else:
            groups.append([node_id])
    unresolved: list[dict[str, Any]] = []
    for item in compatibility.get("pairs", []):
        if item.get("decision") != "compatible":
            unresolved.append({
                "left": item.get("left"),
                "right": item.get("right"),
                "decision": item.get("decision"),
                "reason_codes": sorted({str(reason.get("code")) for reason in item.get("reasons", [])}),
                "remediation": item.get("remediation"),
            })
    return groups, sorted(unresolved, key=lambda item: (str(item["left"]), str(item["right"])))


def _changes(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    if previous is None:
        return {"previous_plan_digest": None, "changed": False, "changes": []}
    if previous.get("schema_version") != SCHEMA_VERSION:
        raise ControlError("allocation.previous-incompatible", "The previous allocation uses an incompatible contract.", {"schema_version": previous.get("schema_version")}, ["Supply a portfolio-allocation-v1 result or omit the comparison."])
    if previous.get("level") != current.get("level"):
        raise ControlError("allocation.previous-level-mismatch", "The previous allocation uses a different hierarchy level.", {"previous_level": previous.get("level"), "current_level": current.get("level")}, ["Compare plans produced for the same explicit level."])
    before = {str(item.get("unit_id")): item for item in previous.get("lanes", []) if isinstance(item, dict)}
    after = {str(item.get("unit_id")): item for item in current.get("lanes", []) if isinstance(item, dict)}
    changes: list[dict[str, Any]] = []
    for unit_id in sorted(set(after) - set(before)):
        changes.append({"type": "lane-added", "unit_id": unit_id})
    for unit_id in sorted(set(before) - set(after)):
        changes.append({"type": "lane-removed", "unit_id": unit_id})
    compared_fields = ("allocation_state", "lifecycle_status", "branches", "active_descendants", "coordination", "rationale")
    for unit_id in sorted(set(before) & set(after)):
        fields = [field for field in compared_fields if before[unit_id].get(field) != after[unit_id].get(field)]
        if fields:
            changes.append({"type": "lane-changed", "unit_id": unit_id, "fields": fields})
    for field in ("parallel_groups", "unresolved_pairs"):
        if previous.get(field) != current.get(field):
            changes.append({"type": f"{field.replace('_', '-')}-changed"})
    previous_digest = str(previous.get("plan_digest") or _digest({key: value for key, value in previous.items() if key not in {"plan_digest", "replan"}}))
    return {"previous_plan_digest": previous_digest, "changed": bool(changes), "changes": changes}


def allocate(
    graph: dict[str, Any],
    *,
    level: str,
    authority_current: Iterable[str] = (),
    explicit_priority: Iterable[str] = (),
    accepted_sequence: Iterable[str] = (),
    coordination: dict[str, Any] | None = None,
    previous: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose a proposal from stable graph, order, conflict, and edit facts."""

    if level not in LEVEL_KIND:
        raise ControlError("allocation.level-invalid", "Allocation requires capability, slice, or work granularity.", {"level": level}, ["Choose capability, slice, or work."])
    if graph.get("schema_version") != "portfolio-graph-v1":
        raise ControlError("allocation.graph-incompatible", "The allocation input graph is incompatible.", {"schema_version": graph.get("schema_version")}, ["Regenerate the portfolio graph with a compatible adapter."])
    authority_values = sorted({str(item) for item in authority_current})
    priority_values = [str(item) for item in explicit_priority]
    sequence_values = [str(item) for item in accepted_sequence]
    coordination = coordination or {"revision": 0, "leases": [], "intents": []}
    by_id = {str(item.get("id")): dict(item) for item in graph.get("nodes", [])}
    ordered = plan(graph, level=level, authority_current=authority_values, explicit_priority=priority_values, accepted_sequence=sequence_values)
    ready_ids = {str(item["id"]) for item in ordered["ready"]}
    proposed_ready = [item for item in ordered["proposed_order"] if item in ready_ids]
    active_descendants_by_unit = {
        unit_id: sorted(
            candidate
            for candidate, item in by_id.items()
            if _descendant(candidate, unit_id, by_id)
            and (item.get("active_claim") or item.get("status") in {"active", "verifying"})
        )
        for unit_id, node in by_id.items()
        if node.get("kind") == LEVEL_KIND[level]
    }
    proposal_position = {unit_id: index for index, unit_id in enumerate(proposed_ready)}
    direct_in_progress = [str(item) for item in ordered["in_progress"]]
    direct_in_progress_set = set(direct_in_progress)
    promoted = sorted(
        (
            unit_id
            for unit_id, descendants in active_descendants_by_unit.items()
            if descendants
            and by_id[unit_id].get("status") == "ready"
            and unit_id not in direct_in_progress_set
        ),
        key=lambda unit_id: (
            0 if unit_id in proposal_position else 1,
            proposal_position.get(unit_id, unit_id),
        ),
    )
    in_progress_ids = {*direct_in_progress, *promoted}
    candidate_ids = [
        *direct_in_progress,
        *promoted,
        *(unit_id for unit_id in proposed_ready if unit_id not in in_progress_ids),
    ]
    compatibility = analyze_compatibility(graph, level=level, candidate_ids=candidate_ids)
    parallel_groups, unresolved = _groups(candidate_ids, compatibility)
    lanes: list[dict[str, Any]] = []
    for position, unit_id in enumerate(candidate_ids):
        node = by_id[unit_id]
        active_descendants = active_descendants_by_unit.get(unit_id, [])
        branches = sorted({str(value) for value in node.get("branches", []) if str(value)})
        branch_state = "unrecorded" if not branches else ("codex" if all(value.startswith("codex/") for value in branches) else "non-codex")
        if unit_id in direct_in_progress_set:
            rationale = ["lifecycle.in-progress"]
        elif unit_id in in_progress_ids:
            rationale = ["lifecycle.descendant-in-progress"]
        else:
            rationale = ["authority.current", "dependencies.satisfied", "lifecycle.ready"]
        lane = {
            "lane_id": f"lane-{position + 1:03d}",
            "unit_id": unit_id,
            "unit_kind": node.get("kind"),
            "allocation_state": "in-progress" if unit_id in in_progress_ids else "proposed",
            "lifecycle_status": node.get("status"),
            "branches": branches,
            "branch_state": branch_state,
            "active_descendants": active_descendants,
            "coordination": _coordination_for(unit_id, by_id, coordination),
            "rationale": rationale,
        }
        lane["lane_digest"] = _digest(lane)
        lanes.append(lane)
    input_snapshot = {
        "graph": graph,
        "level": level,
        "authority_current": authority_values,
        "explicit_priority": priority_values,
        "accepted_sequence": sequence_values,
        "coordination": coordination,
    }
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "level": level,
        "input_digest": _digest(input_snapshot),
        "lanes": lanes,
        "parallel_groups": parallel_groups,
        "unresolved_pairs": unresolved,
        "blocked": ordered["blocked"],
        "unresolved_ties": ordered["unresolved_ties"],
        "coordination_revision": coordination.get("revision", 0),
        "constraints": {
            "creates_agents": False,
            "grants_authority": False,
            "mutates_branches": False,
            "acquires_file_leases": False,
            "single_hierarchy_level": True,
        },
    }
    result["plan_digest"] = _digest(result)
    result["replan"] = _changes(previous, result)
    return result
