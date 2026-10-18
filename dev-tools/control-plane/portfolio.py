"""Project-neutral portfolio hierarchy and dependency graph contracts."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


SCHEMA_VERSION = "portfolio-graph-v1"
KINDS = {"candidate", "capability", "slice", "work"}
PARENT_KIND = {"slice": "capability", "work": "slice"}


def _texts(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({str(item).strip() for item in value if str(item).strip()})


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _issue(
    code: str,
    node_id: str,
    message: str,
    *,
    blocking: bool,
    related: str | None = None,
    remediation: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "blocking": blocking,
        "code": code,
        "message": message,
        "node_id": node_id,
        "remediation": remediation,
    }
    if related:
        result["related_id"] = related
    return result


def _normalized_node(raw: dict[str, Any]) -> dict[str, Any]:
    node_id = str(raw.get("id", "")).strip()
    kind = str(raw.get("kind", "")).strip()
    dependencies: list[dict[str, str]] = []
    raw_dependencies = raw.get("dependencies", [])
    for item in raw_dependencies if isinstance(raw_dependencies, list) else []:
        if isinstance(item, str):
            target, edge_type = item.strip(), "hard"
        elif isinstance(item, dict):
            target = str(item.get("target", "")).strip()
            edge_type = str(item.get("type", "hard")).strip() or "hard"
        else:
            continue
        if target:
            dependencies.append({"target": target, "type": edge_type})
    dependencies.sort(key=lambda item: (item["target"], item["type"]))
    decision_gates = _texts(raw.get("decision_gates"))
    raw_unresolved = raw.get("unresolved_decision_gates")
    unresolved_decision_gates = (
        decision_gates
        if raw_unresolved is None
        else _texts(raw_unresolved)
    )
    return {
        "id": node_id,
        "kind": kind,
        "status": str(raw.get("status", "unknown")).strip() or "unknown",
        "title": str(raw.get("title", node_id)).strip() or node_id,
        "source": str(raw.get("source", "")).replace("\\", "/").strip(),
        "parent": _optional_text(raw.get("parent")),
        "dependencies": dependencies,
        "manifest": _texts(raw.get("manifest")),
        "manifest_declared": bool(raw.get("manifest_declared", "manifest" in raw)),
        "decision_gates": decision_gates,
        "unresolved_decision_gates": unresolved_decision_gates,
        "superseded_by": _optional_text(raw.get("superseded_by")),
        "governed": bool(raw.get("governed", kind != "candidate")),
        "write_scope": _texts(raw.get("write_scope")),
        "generated_artifacts": _texts(raw.get("generated_artifacts")),
        "contracts": _texts(raw.get("contracts")),
        "exclusive_resources": _texts(raw.get("exclusive_resources")),
        "parallel_safe_with": _texts(raw.get("parallel_safe_with")),
        "branches": _texts(raw.get("branches")),
        "active_claim": bool(raw.get("active_claim", False)),
        "scope_complete": bool(raw.get("scope_complete", False)),
    }


def _strong_components(ids: list[str], adjacency: dict[str, list[str]]) -> list[list[str]]:
    index = 0
    indexes: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def visit(node_id: str) -> None:
        nonlocal index
        indexes[node_id] = lowlinks[node_id] = index
        index += 1
        stack.append(node_id)
        on_stack.add(node_id)
        for target in adjacency.get(node_id, []):
            if target not in indexes:
                visit(target)
                lowlinks[node_id] = min(lowlinks[node_id], lowlinks[target])
            elif target in on_stack:
                lowlinks[node_id] = min(lowlinks[node_id], indexes[target])
        if lowlinks[node_id] == indexes[node_id]:
            component: list[str] = []
            while stack:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node_id:
                    break
            components.append(sorted(component))

    for node_id in ids:
        if node_id not in indexes:
            visit(node_id)
    return sorted(components, key=lambda item: item[0])


def _topological_order(ids: list[str], adjacency: dict[str, list[str]]) -> list[str]:
    dependents: dict[str, list[str]] = defaultdict(list)
    indegree = {node_id: 0 for node_id in ids}
    for source in ids:
        for dependency in adjacency.get(source, []):
            dependents[dependency].append(source)
            indegree[source] += 1
    ready = sorted(node_id for node_id, count in indegree.items() if count == 0)
    ordered: list[str] = []
    while ready:
        node_id = ready.pop(0)
        ordered.append(node_id)
        for dependent in sorted(dependents.get(node_id, [])):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
                ready.sort()
    return ordered if len(ordered) == len(ids) else []


def analyze(nodes: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Validate and project a stable hierarchy/dependency graph."""

    normalized = [_normalized_node(dict(item)) for item in nodes]
    normalized.sort(key=lambda item: (item["id"], item["kind"], item["source"]))
    issues: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    for node in normalized:
        node_id = node["id"]
        if not node_id:
            issues.append(_issue("node.id-missing", "<missing>", "A portfolio node has no identifier.", blocking=True, remediation="Provide one stable project-owned identifier."))
            continue
        if node["kind"] not in KINDS:
            issues.append(_issue("node.kind-invalid", node_id, "A portfolio node has an unsupported kind.", blocking=True, remediation="Map the source to candidate, capability, slice, or work."))
        if node_id in by_id:
            issues.append(_issue("node.duplicate", node_id, "The portfolio contains the same identifier more than once.", blocking=True, remediation="Remove or rename the duplicate source binding."))
            continue
        by_id[node_id] = node

    adjacency: dict[str, list[str]] = {node_id: [] for node_id in sorted(by_id)}
    edges: list[dict[str, str]] = []
    for node_id, node in sorted(by_id.items()):
        expected_parent_kind = PARENT_KIND.get(node["kind"])
        parent_id = node["parent"]
        if expected_parent_kind:
            parent = by_id.get(str(parent_id)) if parent_id else None
            if parent is None:
                issues.append(_issue("hierarchy.parent-missing", node_id, "A governed child has no existing parent.", blocking=True, related=str(parent_id) if parent_id else None, remediation="Restore the parent artifact or correct the child binding."))
            elif parent["kind"] != expected_parent_kind:
                issues.append(_issue("hierarchy.parent-kind", node_id, "The parent has the wrong hierarchy kind.", blocking=True, related=str(parent_id), remediation=f"Bind this {node['kind']} to a {expected_parent_kind}."))
        elif parent_id:
            issues.append(_issue("hierarchy.parent-unexpected", node_id, "This node kind cannot have a governed parent.", blocking=True, related=str(parent_id), remediation="Remove the invalid parent binding."))

        for dependency in node["dependencies"]:
            target = dependency["target"]
            edges.append({"source": node_id, "target": target, "type": dependency["type"]})
            if target == node_id:
                issues.append(_issue("dependency.self", node_id, "A node depends on itself.", blocking=True, related=target, remediation="Remove the self-dependency."))
                adjacency[node_id].append(target)
                continue
            target_node = by_id.get(target)
            if target_node is None:
                issues.append(_issue("dependency.missing", node_id, "A dependency target is missing.", blocking=True, related=target, remediation="Restore the target or remove the stale dependency."))
                continue
            adjacency[node_id].append(target)
            if target_node["status"] == "superseded" or target_node["superseded_by"]:
                issues.append(_issue("dependency.superseded", node_id, "A dependency targets superseded work.", blocking=True, related=target, remediation="Depend on the accepted successor or remove the stale edge."))

    for node_id, node in sorted(by_id.items()):
        if node["kind"] != "capability" or not node["manifest_declared"]:
            continue
        for child_id in node["manifest"]:
            child = by_id.get(child_id)
            if child is None:
                issues.append(_issue("manifest.expected-child-missing", node_id, "A declared slice has not yet been refined into an artifact.", blocking=False, related=child_id, remediation="Refine the slice just in time before it starts."))
            elif child["kind"] != "slice" or child["parent"] != node_id:
                issues.append(_issue("manifest.child-mismatch", node_id, "A declared slice is bound to the wrong kind or parent.", blocking=True, related=child_id, remediation="Correct the slice parent or CAP manifest."))
    for node_id, node in sorted(by_id.items()):
        if node["kind"] != "slice" or not node["parent"]:
            continue
        parent = by_id.get(str(node["parent"]))
        if parent and parent["kind"] == "capability" and parent["manifest_declared"] and node_id not in parent["manifest"]:
            issues.append(_issue("manifest.unlisted-child", node_id, "A slice is absent from its parent CAP manifest.", blocking=True, related=str(node["parent"]), remediation="Return the CAP to shaping or remove the stale slice binding."))

    ids = sorted(by_id)
    components = _strong_components(ids, adjacency)
    cyclic = [component for component in components if len(component) > 1 or (len(component) == 1 and component[0] in adjacency.get(component[0], []))]
    for component in cyclic:
        issues.append(_issue("dependency.cycle", component[0], "The dependency graph contains a cycle.", blocking=True, related=",".join(component), remediation="Remove or redirect at least one dependency edge in the cycle."))

    issues.sort(key=lambda item: (item["code"], item["node_id"], item.get("related_id", "")))
    public_nodes = [by_id[node_id] for node_id in ids]
    state = "invalid" if any(item["blocking"] for item in issues) else ("partial" if issues else "valid")
    return {
        "schema_version": SCHEMA_VERSION,
        "state": state,
        "node_count": len(public_nodes),
        "edge_count": len(edges),
        "nodes": public_nodes,
        "edges": sorted(edges, key=lambda item: (item["source"], item["target"], item["type"])),
        "topological_order": [] if cyclic else _topological_order(ids, adjacency),
        "issues": issues,
    }
