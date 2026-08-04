#!/usr/bin/env python3
"""Recommend the next planning skill from compatible artifact metadata."""

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


def choose(items: list[dict[str, str]]) -> dict[str, str] | None:
    return sorted(items, key=lambda item: (item.get("id", "ZZZ"), item["path"]))[0] if items else None


def result(skill: str, action: str, item: dict[str, str] | None, reason: str, approval: str) -> dict[str, str]:
    return {
        "skill": skill,
        "action": action,
        "subject": item.get("id", "none") if item else "none",
        "path": item.get("path", "") if item else "",
        "reason": reason,
        "approval_required": approval,
        "mode": "advice-only",
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: recommend_next.py <planning-root>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"ERROR: planning root not found: {root}", file=sys.stderr)
        return 2
    artifacts: list[dict[str, str]] = []
    for path in root.rglob("*.md"):
        relative = path.relative_to(root).parts
        if "skills" in relative or "templates" in relative or path.name == "README.md":
            continue
        data = metadata(path)
        if data.get("kind") in {"capability", "decision-request", "vertical-slice", "work-packet"}:
            artifacts.append(data)
    capabilities = [a for a in artifacts if a.get("kind") == "capability"]
    decisions = [a for a in artifacts if a.get("kind") == "decision-request"]
    slices = [a for a in artifacts if a.get("kind") == "vertical-slice"]
    packets = [a for a in artifacts if a.get("kind") == "work-packet"]

    item = choose([a for a in slices if a.get("planning_status") == "verifying"])
    if item:
        output = result("verify-and-close-slice", "verify evidence and request completion acceptance", item, "A slice is verifying.", "completion")
    else:
        item = choose([a for a in packets + slices if a.get("planning_status") == "active"])
        if item:
            output = result("implement-vertical-slice", "finish authorized active work", item, "Approved work is already active.", "already-required")
        else:
            item = choose([a for a in artifacts if a.get("planning_status") == "decision-blocked"] + [a for a in decisions if a.get("planning_status") != "complete"])
            if item:
                output = result("review-decision-gates", "resolve or route the blocking decision", item, "A decision gate blocks progress.", "decision")
            else:
                item = choose([a for a in capabilities if a.get("planning_status") in {"captured", "shaping"} or a.get("capability_approval") == "changes-requested"])
                if item:
                    output = result("shape-capability", "finish capability shaping", item, "A capability is not ready for approval.", "capability")
                else:
                    item = choose([a for a in capabilities if a.get("capability_approval") == "pending"])
                    if item:
                        output = result("approve-planned-work", "review capability framing", item, "A shaped capability awaits a human decision.", "capability")
                    else:
                        approved_capabilities = [a for a in capabilities if a.get("capability_approval") == "approved"]
                        without_slice = [a for a in approved_capabilities if not any(s.get("parent") == a.get("id") for s in slices)]
                        item = choose(without_slice)
                        if item:
                            output = result("select-vertical-slice", "select the next vertical slice", item, "An approved capability has no slice.", "selection")
                        else:
                            item = choose([a for a in slices if a.get("planning_status") in {"captured", "shaping"} or a.get("selection_approval") == "changes-requested"])
                            if item:
                                output = result("select-vertical-slice", "finish vertical-slice selection", item, "Slice selection is incomplete.", "selection")
                            else:
                                item = choose([a for a in slices if a.get("selection_approval") == "pending"])
                                if item:
                                    output = result("approve-planned-work", "review vertical-slice selection", item, "A slice awaits selection approval.", "selection")
                                else:
                                    approved_slices = [a for a in slices if a.get("selection_approval") == "approved" and a.get("planning_status") not in {"complete", "superseded"}]
                                    without_packet = [a for a in approved_slices if not any(p.get("parent") == a.get("id") for p in packets)]
                                    item = choose(without_packet)
                                    if item:
                                        output = result("author-agent-work-packet", "author implementation work packets", item, "An approved slice has no packets.", "planning")
                                    else:
                                        item = choose([a for a in packets if a.get("planning_status") in {"captured", "shaping"} or a.get("planning_approval") == "changes-requested"])
                                        if item:
                                            output = result("author-agent-work-packet", "finish work-packet planning", item, "A packet is not plan-ready.", "planning")
                                        else:
                                            item = choose([a for a in packets if a.get("planning_approval") == "pending"])
                                            if item:
                                                output = result("approve-planned-work", "review packet planning", item, "A packet awaits planning approval.", "planning")
                                            else:
                                                item = choose([a for a in packets if a.get("planning_approval") == "approved" and a.get("implementation_approval") != "approved" and a.get("planning_status") == "ready"])
                                                if item:
                                                    output = result("approve-planned-work", "consider implementation activation", item, "A plan-ready packet lacks separate implementation approval.", "implementation")
                                                else:
                                                    item = choose([a for a in packets if a.get("planning_status") == "ready" and a.get("planning_approval") == "approved" and a.get("implementation_approval") == "approved"])
                                                    if item:
                                                        output = result("implement-vertical-slice", "request or begin authorized implementation", item, "A packet is fully approved and ready.", "current-explicit-implementation-request")
                                                    else:
                                                        output = result("shape-capability", "shape the first or next capability", None, "No actionable planning artifact was found.", "capability")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
