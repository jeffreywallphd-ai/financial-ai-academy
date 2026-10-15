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


def list_value(value: str | None) -> list[str]:
    text = (value or "").strip()
    if not text or text == "[]":
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return []
    return [str(item) for item in parsed] if isinstance(parsed, list) else []


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
        output = result("verify-and-close-slice", "verify evidence and close the slice", item, "A slice is verifying.", "none")
    elif (item := choose([a for a in packets + slices if a.get("planning_status") == "active"])):
        output = result("implement-vertical-slice", "finish CAP-authorized active work", item, "CAP-authorized work is active.", "none")
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
        if a.get("planning_status") not in {"complete", "superseded"}
        and decision(ledger, a.get("id", ""), "capability") != "approved"
    ])):
        output = result("approve-planned-work", "review the complete CAP planning package", item, "A shaped CAP package lacks its one local human approval.", "capability")
    else:
        approved_capabilities = [
            a for a in capabilities
            if decision(ledger, a.get("id", ""), "capability") == "approved"
        ]
        capability = choose([
            a for a in approved_capabilities
            if a.get("planning_status") not in {"complete", "superseded"}
        ])
        manifest = list_value(capability.get("slice_ids")) if capability else []
        next_slice_id = next(
            (
                identifier for identifier in manifest
                if identifier not in by_id
                or by_id[identifier].get("planning_status") not in {"complete", "superseded"}
            ),
            "",
        )
        next_slice = by_id.get(next_slice_id)
        if capability and next_slice is None:
            output = result("select-vertical-slice", "refine the next manifest slice", capability, f"{next_slice_id} is next in the approved CAP manifest.", "none")
        elif next_slice and next_slice.get("planning_status") in {"captured", "shaping", "ready"}:
            slice_packets = [p for p in packets if p.get("parent") == next_slice_id]
            shaping_packet = choose([p for p in slice_packets if p.get("planning_status") in {"captured", "shaping"}])
            ready_packet = choose([p for p in slice_packets if p.get("planning_status") == "ready"])
            if shaping_packet:
                output = result("author-agent-work-packet", "finish just-in-time packet planning", shaping_packet, "The next packet needs deterministic refinement.", "none")
            elif ready_packet:
                output = result("implement-vertical-slice", "claim and implement the next packet", next_slice, "The next packet is ready under current CAP authority.", "none", [ready_packet])
            else:
                output = result("author-agent-work-packet", "author the next work packet just in time", next_slice, "The next manifest slice has no executable packet yet.", "none")
        elif capability and not next_slice_id:
            output = result("verify-and-close-slice", "verify cumulative CAP completion", capability, "Every manifest slice is complete.", "none")
        else:
            output = result("shape-capability", "shape the first or next capability", None, "No actionable planning artifact was found.", "capability")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
