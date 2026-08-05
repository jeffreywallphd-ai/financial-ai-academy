#!/usr/bin/env python3
"""Recommend the next governed skill using public state and local approvals."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def metadata(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3 or lines[0] != "---":
        return {}
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}
    result: dict[str, str] = {"path": str(path)}
    for line in lines[1:end]:
        if ":" in line and not line.startswith((" ", "-")):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def repository_root(path: Path) -> Path:
    current = path.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() and (candidate / "docs").is_dir():
            return candidate
    raise ValueError("unable to locate repository root")


def load_ledger(root: Path) -> dict[str, object]:
    path = root / ".local-codex/approvals/ledger.json"
    if not path.is_file():
        return {"version": 1, "records": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("records"), list):
        raise ValueError("local approval ledger is invalid")
    return data


def decision(ledger: dict[str, object], subject: str, stage: str) -> str:
    matches = [
        item for item in ledger["records"]
        if isinstance(item, dict)
        and item.get("subject") == subject
        and item.get("stage") == stage
    ]
    return str(matches[-1].get("decision", "")) if matches else ""


def choose(items: list[dict[str, str]]) -> dict[str, str] | None:
    return sorted(items, key=lambda item: (item.get("id", "ZZZ"), item["path"]))[0] if items else None


def result(
    skill: str,
    action: str,
    item: dict[str, str] | None,
    reason: str,
    approval: str,
    members: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    selected = sorted(
        members or ([item] if item else []),
        key=lambda member: (member.get("id", "ZZZ"), member.get("path", "")),
    )
    return {
        "skill": skill,
        "action": action,
        "subject": item.get("id", "none") if item else "none",
        "path": item.get("path", "") if item else "",
        "subjects": [member.get("id", "") for member in selected],
        "paths": [member.get("path", "") for member in selected],
        "reason": reason,
        "approval_required": approval,
        "mode": "advice-only",
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: recommend_next.py <planning-root>", file=sys.stderr)
        return 2
    planning_root = Path(sys.argv[1])
    if not planning_root.is_dir():
        print(f"ERROR: planning root not found: {planning_root}", file=sys.stderr)
        return 2
    try:
        ledger = load_ledger(repository_root(planning_root))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    artifacts: list[dict[str, str]] = []
    for path in planning_root.rglob("*.md"):
        relative = path.relative_to(planning_root).parts
        if "skills" in relative or "templates" in relative or path.name == "README.md":
            continue
        data = metadata(path)
        if data.get("kind") in {"capability", "decision-request", "vertical-slice", "work-packet"}:
            artifacts.append(data)
    capabilities = [a for a in artifacts if a.get("kind") == "capability"]
    decisions = [a for a in artifacts if a.get("kind") == "decision-request"]
    slices = [a for a in artifacts if a.get("kind") == "vertical-slice"]
    packets = [a for a in artifacts if a.get("kind") == "work-packet"]
    by_id = {a.get("id", ""): a for a in artifacts}

    item = choose([a for a in slices if a.get("planning_status") == "verifying"])
    if item:
        output = result("verify-and-close-slice", "verify evidence and request completion acceptance", item, "A slice is verifying.", "completion")
    elif (item := choose([a for a in packets + slices if a.get("planning_status") == "active"])):
        output = result("implement-vertical-slice", "finish authorized active work", item, "Locally authorized work is active.", "already-required")
    elif (unresolved_decisions := [
        a for a in decisions if a.get("planning_status") != "complete"
    ]):
        item = choose(unresolved_decisions)
        output = result(
            "review-decision-gates",
            "review the consolidated blocking decision set",
            item,
            "One or more decision requests block progress.",
            "decision-bundle" if len(unresolved_decisions) > 1 else "decision",
            unresolved_decisions,
        )
    elif (item := choose([
        a for a in artifacts if a.get("planning_status") == "decision-blocked"
    ])):
        output = result(
            "review-decision-gates",
            "identify or route the blocking decision",
            item,
            "An artifact is decision-blocked.",
            "decision",
        )
    elif (item := choose([
        a for a in capabilities
        if a.get("planning_status") in {"captured", "shaping"}
        or decision(ledger, a.get("id", ""), "capability") == "changes-requested"
    ])):
        output = result("shape-capability", "finish capability shaping", item, "A capability is not ready for review.", "capability")
    elif (item := choose([
        a for a in capabilities
        if decision(ledger, a.get("id", ""), "capability") != "approved"
    ])):
        output = result("approve-planned-work", "review capability framing", item, "A shaped capability lacks a local human decision.", "capability")
    else:
        approved_capabilities = [
            a for a in capabilities
            if decision(ledger, a.get("id", ""), "capability") == "approved"
        ]
        item = choose([
            a for a in approved_capabilities
            if not any(s.get("parent") == a.get("id") for s in slices)
        ])
        if item:
            output = result("select-vertical-slice", "select the next vertical slice", item, "A locally approved capability has no slice.", "selection")
        elif (item := choose([
            a for a in slices
            if a.get("planning_status") in {"captured", "shaping"}
            or decision(ledger, a.get("id", ""), "selection") == "changes-requested"
        ])):
            output = result("select-vertical-slice", "finish vertical-slice selection", item, "Slice selection is incomplete.", "selection")
        elif (item := choose([
            a for a in slices
            if decision(ledger, a.get("id", ""), "selection") != "approved"
        ])):
            output = result("approve-planned-work", "review vertical-slice selection", item, "A slice lacks local selection approval.", "selection")
        else:
            approved_slices = [
                a for a in slices
                if decision(ledger, a.get("id", ""), "selection") == "approved"
                and a.get("planning_status") not in {"complete", "superseded"}
            ]
            item = choose([
                a for a in approved_slices
                if not any(p.get("parent") == a.get("id") for p in packets)
            ])
            if item:
                output = result("author-agent-work-packet", "author implementation work packets", item, "A locally selected slice has no packets.", "planning")
            elif (item := choose([
                a for a in packets
                if a.get("planning_status") in {"captured", "shaping"}
                or decision(ledger, a.get("id", ""), "planning") == "changes-requested"
            ])):
                output = result("author-agent-work-packet", "finish work-packet planning", item, "A packet is not plan-ready.", "planning")
            elif (item := choose([
                a for a in packets
                if decision(ledger, a.get("id", ""), "planning") != "approved"
            ])):
                members = [
                    a for a in packets
                    if a.get("parent") == item.get("parent")
                    and decision(ledger, a.get("id", ""), "planning") != "approved"
                ]
                parent = by_id.get(item.get("parent", ""), item)
                output = result(
                    "approve-planned-work",
                    "review the closed slice packet plan",
                    parent,
                    "One or more packets in a slice lack local planning approval.",
                    "planning-bundle" if len(members) > 1 else "planning",
                    members,
                )
            elif (item := choose([
                a for a in packets
                if a.get("planning_status") == "ready"
                and decision(ledger, a.get("id", ""), "implementation") != "approved"
            ])):
                members = [
                    a for a in packets
                    if a.get("parent") == item.get("parent")
                    and a.get("planning_status") == "ready"
                    and decision(ledger, a.get("id", ""), "implementation") != "approved"
                ]
                parent = by_id.get(item.get("parent", ""), item)
                output = result(
                    "approve-planned-work",
                    "consider slice-wide implementation activation",
                    parent,
                    "A closed slice packet set lacks local implementation approval.",
                    "implementation-bundle" if len(members) > 1 else "implementation",
                    members,
                )
            elif (item := choose([
                a for a in packets
                if a.get("planning_status") == "ready"
                and decision(ledger, a.get("id", ""), "implementation") == "approved"
            ])):
                members = [
                    a for a in packets
                    if a.get("parent") == item.get("parent")
                    and a.get("planning_status") == "ready"
                    and decision(ledger, a.get("id", ""), "implementation") == "approved"
                ]
                parent = by_id.get(item.get("parent", ""), item)
                output = result(
                    "implement-vertical-slice",
                    "request or begin serial slice implementation",
                    parent,
                    "A closed slice packet set is locally approved and ready.",
                    "current-explicit-implementation-request",
                    members,
                )
            else:
                output = result("shape-capability", "shape the first or next capability", None, "No actionable planning artifact was found.", "capability")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
