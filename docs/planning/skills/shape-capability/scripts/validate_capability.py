#!/usr/bin/env python3
"""Validate the portable capability-planning artifact contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_KEYS = {
    "id", "kind", "planning_status", "authority", "owner", "updated",
    "depends_on", "decision_gates", "capability_approval",
    "capability_approved_by", "capability_approved_at",
}
REQUIRED_HEADINGS = {
    "# Capability:", "## Outcome", "## Users and Value", "## In Scope",
    "## Out of Scope", "## Canonical Context",
    "## Decision Gates and Constraints", "## Proposed Vertical Slices",
    "## Capability Acceptance", "## Risks and Non-Goals",
    "## Documentation Impact", "## Approval History",
}
STATUSES = {
    "captured", "shaping", "decision-blocked", "ready", "active",
    "verifying", "complete", "superseded",
}
APPROVALS = {"pending", "approved", "changes-requested", "rejected"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse(path: Path) -> tuple[dict[str, str], str, list[str]]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0] != "---" or "---" not in lines[1:]:
        return {}, text, ["missing YAML-style frontmatter"]
    end = lines[1:].index("---") + 1
    data: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line and not line.startswith((" ", "-")):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data, text, errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_capability.py <CAP markdown>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2
    data, text, errors = parse(path)
    errors.extend(f"missing metadata: {key}" for key in sorted(REQUIRED_KEYS - data.keys()))
    if not data.get("id", "").startswith("CAP-") or data.get("id") == "CAP-0000":
        errors.append("id must be a non-placeholder CAP-* identifier")
    if data.get("kind") != "capability":
        errors.append("kind must be capability")
    if data.get("planning_status") not in STATUSES:
        errors.append("invalid planning_status")
    if data.get("capability_approval") not in APPROVALS:
        errors.append("invalid capability_approval")
    if not DATE_RE.match(data.get("updated", "")):
        errors.append("updated must be YYYY-MM-DD")
    if data.get("planning_status") == "decision-blocked" and data.get("decision_gates") == "[]":
        errors.append("decision-blocked requires at least one decision gate")
    if data.get("planning_status") == "ready" and data.get("capability_approval") != "approved":
        errors.append("ready requires capability_approval: approved")
    if data.get("capability_approval") == "approved":
        if data.get("capability_approved_by") in {"", "null", "unassigned"}:
            errors.append("approved capability requires capability_approved_by")
        if not DATE_RE.match(data.get("capability_approved_at", "")):
            errors.append("approved capability requires capability_approved_at YYYY-MM-DD")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing heading: {heading}")
    if "Short Outcome Name" in text or "YYYY-MM-DD" in text:
        errors.append("artifact contains template placeholders")
    if errors:
        print("Capability validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Capability validation passed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
