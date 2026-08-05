#!/usr/bin/env python3
"""Validate a public vertical-slice artifact contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path


KEYS = {
    "id", "kind", "planning_status", "authority", "owner", "updated",
    "parent", "depends_on", "decision_gates",
}
HEADINGS = {
    "# Vertical Slice:", "## Outcome and User Scenario",
    "## Scope Boundaries", "### In Scope", "### Out of Scope",
    "## Canonical Context and Decisions", "## Candidate Evaluation",
    "## Selection Rationale", "## Boundary Path",
    "## Contracts, Data, and Provenance", "## Acceptance Scenarios",
    "## Agent Work Packets", "## Verification and Qualification",
    "## Rollback and Migration", "## Stop Conditions",
    "## Documentation Impact and Completion Evidence", "## Planning History",
}
STATUSES = {
    "captured", "shaping", "decision-blocked", "ready", "active",
    "verifying", "complete", "superseded",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def metadata(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0] != "---":
        return {}
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}
    result: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line and not line.startswith((" ", "-")):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_vertical_slice.py <SLI markdown>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    data = metadata(text)
    errors = [f"missing metadata: {key}" for key in sorted(KEYS - data.keys())]
    if not data:
        errors.append("missing YAML-style frontmatter")
    if not data.get("id", "").startswith("SLI-") or data.get("id") == "SLI-0000":
        errors.append("id must be a non-placeholder SLI-* identifier")
    if data.get("kind") != "vertical-slice":
        errors.append("kind must be vertical-slice")
    if not data.get("parent", "").startswith("CAP-") or data.get("parent") == "CAP-0000":
        errors.append("parent must be a non-placeholder CAP-* identifier")
    if data.get("planning_status") not in STATUSES:
        errors.append("invalid planning_status")
    if not DATE_RE.match(data.get("updated", "")):
        errors.append("updated must be YYYY-MM-DD")
    if data.get("planning_status") == "decision-blocked" and data.get("decision_gates") == "[]":
        errors.append("decision-blocked requires at least one decision gate")
    if any(key.endswith(("_approval", "_approved_by", "_approved_at")) for key in data):
        errors.append("approval metadata must remain in the ignored local ledger")
    for heading in HEADINGS:
        if heading not in text:
            errors.append(f"missing heading: {heading}")
    if "Short Observable Increment" in text or "YYYY-MM-DD" in text:
        errors.append("artifact contains template placeholders")
    if errors:
        print("Vertical-slice validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Vertical-slice validation passed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
