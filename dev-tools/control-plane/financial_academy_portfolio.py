"""Financial AI Academy adapter for project-neutral portfolio graphs."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PLANNING_TOOLS = HERE.parent / "planning"
if str(PLANNING_TOOLS) not in sys.path:
    sys.path.insert(0, str(PLANNING_TOOLS))

from approval_store import load_store  # noqa: E402
from cap_package import require_current_package  # noqa: E402
from planning_model import as_list, as_text, load_artifacts  # noqa: E402

from contracts import ControlError, success
from file_leases import FileLeaseStore
from portfolio import analyze
from portfolio_allocation import allocate
from portfolio_conflicts import analyze_compatibility
from portfolio_ordering import plan
from store import confined_path


CATALOG_PATH = "docs/product/capability-catalog.md"
KIND_MAP = {"capability": "capability", "vertical-slice": "slice", "work-packet": "work"}
COMPATIBILITY_BRANCH_SENTINELS = frozenset({"legacy-unrecorded"})


def current_branch(root: Path) -> str | None:
    completed = subprocess.run(["git", "branch", "--show-current"], cwd=root, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")
    branch = completed.stdout.strip() if completed.returncode == 0 else ""
    return branch or None


def projected_claim_branch(claim: dict[str, Any]) -> str | None:
    """Return genuine branch evidence, excluding lifecycle compatibility markers."""

    branch = str(claim.get("branch", "")).strip()
    if not branch or branch in COMPATIBILITY_BRANCH_SENTINELS:
        return None
    return branch


def _slug(value: str) -> str:
    return "-".join(re.findall(r"[a-z0-9]+", value.lower()))


def catalog_nodes(root: Path) -> list[dict[str, Any]]:
    path = root / CATALOG_PATH
    nodes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 2 or cells[0] in {"Capability", "---"} or set(cells[0]) <= {"-", ":"}:
            continue
        title = cells[0]
        candidate_id = f"CAND-{_slug(title)}"
        if candidate_id in seen:
            raise ValueError(f"Duplicate capability catalog key: {candidate_id}")
        seen.add(candidate_id)
        nodes.append({"id": candidate_id, "kind": "candidate", "status": "candidate", "title": title, "source": CATALOG_PATH, "parent": None, "dependencies": [], "manifest": [], "manifest_declared": False, "decision_gates": [], "governed": False})
    return nodes


def planning_nodes(root: Path) -> list[dict[str, Any]]:
    checkout_branch = current_branch(root)
    work_facts: dict[str, dict[str, Any]] = {}
    state_path = root / ".local-codex/control-plane/state.json"
    if state_path.is_file():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            state = {}
        for work_id, value in state.get("work_items", {}).items() if isinstance(state, dict) and isinstance(state.get("work_items"), dict) else []:
            if not isinstance(value, dict):
                continue
            claim = value.get("claim") if isinstance(value.get("claim"), dict) else {}
            branch = projected_claim_branch(claim)
            work_facts[str(work_id)] = {"active_claim": value.get("state") == "active", "branches": [branch] if branch else []}
    nodes: list[dict[str, Any]] = []
    for artifact in load_artifacts(root):
        kind = KIND_MAP.get(artifact.kind)
        if kind is None:
            continue
        metadata = artifact.metadata
        write_scope = as_list(metadata.get("write_scope"))
        generated = as_list(metadata.get("generated_artifacts"))
        contracts = sorted({path for path in [*write_scope, *generated] if path.replace("\\", "/").startswith("contracts/")})
        facts = work_facts.get(artifact.identifier, {})
        branches = list(facts.get("branches", []))
        if not branches and checkout_branch and artifact.status in {"active", "verifying"}:
            branches = [checkout_branch]
        nodes.append({
            "id": artifact.identifier,
            "kind": kind,
            "status": artifact.status,
            "title": artifact.path.stem,
            "source": artifact.relative_path,
            "parent": as_text(metadata.get("parent")) or None,
            "dependencies": [{"target": item, "type": "hard"} for item in as_list(metadata.get("depends_on"))],
            "manifest": as_list(metadata.get("slice_ids")) if kind == "capability" else [],
            "manifest_declared": kind == "capability" and "slice_ids" in metadata,
            "decision_gates": as_list(metadata.get("decision_gates")),
            "superseded_by": as_text(metadata.get("superseded_by")) or None,
            "governed": True,
            "write_scope": write_scope,
            "generated_artifacts": generated,
            "contracts": contracts,
            "exclusive_resources": as_list(metadata.get("exclusive_resources")),
            "parallel_safe_with": as_list(metadata.get("parallel_safe_with")),
            "branches": branches,
            "active_claim": bool(facts.get("active_claim", artifact.status == "active" and kind == "work")),
            "scope_complete": kind == "work" and "write_scope" in metadata and "generated_artifacts" in metadata,
        })
    by_id = {str(node["id"]): node for node in nodes}
    for node in nodes:
        if node["kind"] != "slice":
            continue
        descendants = [item for item in nodes if item["kind"] == "work" and item.get("parent") == node["id"]]
        for field in ("write_scope", "generated_artifacts", "contracts", "exclusive_resources", "branches"):
            node[field] = sorted({*node.get(field, []), *(value for item in descendants for value in item.get(field, []))})
        node["active_claim"] = any(item.get("active_claim") for item in descendants)
        node["scope_complete"] = bool(descendants) and all(item.get("scope_complete") for item in descendants)
    for node in nodes:
        if node["kind"] != "capability":
            continue
        descendants = [item for item in nodes if item["kind"] == "slice" and item.get("parent") == node["id"]]
        for field in ("write_scope", "generated_artifacts", "contracts", "exclusive_resources", "branches"):
            node[field] = sorted({*node.get(field, []), *(value for item in descendants for value in item.get(field, []))})
        node["active_claim"] = any(item.get("active_claim") for item in descendants)
        manifest = node.get("manifest", [])
        node["scope_complete"] = bool(node.get("manifest_declared")) and all(child in by_id for child in manifest) and all(by_id[child].get("scope_complete") for child in manifest if child in by_id)
    return nodes


def project(root: Path) -> dict[str, Any]:
    return analyze([*catalog_nodes(root), *planning_nodes(root)])


def result(root: Path) -> dict[str, Any]:
    graph = project(root)
    response = success("portfolio.graph-projected", f"Projected {graph['node_count']} portfolio node(s) with state {graph['state']}.", data={"graph": graph})
    if graph["state"] == "invalid":
        response["outcome"] = "not-ready"
        response["remediation"] = ["Resolve the blocking portfolio graph issues reported in data.graph.issues."]
    return response


def current_capability_authority(root: Path) -> set[str]:
    store, _ = load_store(root, required=False)
    current: set[str] = set()
    for artifact in load_artifacts(root):
        if artifact.kind != "capability":
            continue
        try:
            require_current_package(store, artifact)
        except Exception:
            continue
        current.add(artifact.identifier)
    return current


def plan_result(root: Path, *, level: str, priority: list[str] | None = None) -> dict[str, Any]:
    portfolio_plan = plan(
        project(root),
        level=level,
        authority_current=current_capability_authority(root),
        explicit_priority=priority or [],
        accepted_sequence=[],
    )
    return success(
        "portfolio.plan-projected",
        f"Projected {len(portfolio_plan['ready'])} ready {level} item(s).",
        data={"plan": portfolio_plan},
    )


def compatibility_result(root: Path, *, level: str, ids: list[str] | None = None) -> dict[str, Any]:
    compatibility = analyze_compatibility(project(root), level=level, candidate_ids=ids)
    return success(
        "portfolio.compatibility-projected",
        f"Evaluated {len(compatibility['pairs'])} {level} pair(s).",
        data={"compatibility": compatibility},
    )


def _previous_plan(root: Path, value: Path | None) -> dict[str, Any] | None:
    if value is None:
        return None
    if value.is_absolute() or not value.as_posix().startswith(".local-codex/"):
        raise ControlError("allocation.previous-not-local", "Previous allocation input must use an ignored repository-relative path.", {"path": value.as_posix()}, ["Place the prior JSON output under .local-codex/ and retry."])
    path = confined_path(root, value.as_posix())
    try:
        previous = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ControlError("allocation.previous-invalid", "The previous allocation input is unreadable or invalid JSON.", {"path": value.as_posix()}, ["Supply a valid portfolio-allocation-v1 JSON object."]) from error
    if not isinstance(previous, dict):
        raise ControlError("allocation.previous-invalid", "The previous allocation input must be a JSON object.", {"path": value.as_posix()}, ["Supply a valid portfolio-allocation-v1 JSON object."])
    data = previous.get("data")
    if isinstance(data, dict) and isinstance(data.get("allocation"), dict):
        previous = data["allocation"]
    return previous


def allocation_result(root: Path, *, level: str, priority: list[str] | None = None, previous_plan: Path | None = None) -> dict[str, Any]:
    edit_status = FileLeaseStore(root).status()
    coordination = dict(edit_status["data"])
    coordination["revision"] = edit_status.get("state_revision", 0)
    allocation = allocate(
        project(root),
        level=level,
        authority_current=current_capability_authority(root),
        explicit_priority=priority or [],
        accepted_sequence=[],
        coordination=coordination,
        previous=_previous_plan(root, previous_plan),
    )
    return success(
        "portfolio.allocation-projected",
        f"Projected {len(allocation['lanes'])} proposed or active {level} lane(s).",
        data={"allocation": allocation},
    )
