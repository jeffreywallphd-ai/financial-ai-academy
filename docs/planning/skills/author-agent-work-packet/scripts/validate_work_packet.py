#!/usr/bin/env python3
"""Validate a public work-packet artifact contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path


KEYS = {
    "id", "kind", "planning_status", "authority", "owner", "updated",
    "parent", "capability", "depends_on", "decision_gates",
    "parallel_safe_with", "write_scope", "generated_artifacts",
    "base_revision", "claim_id", "claimed_by", "claimed_at",
}
HEADINGS = {
    "# Agent Work Packet:", "## Objective and Deliverable",
    "## Required Context", "## Decisions and Assumptions", "## In Scope",
    "## Out of Scope", "## Expected File and Boundary Impact",
    "## Contracts and Interfaces", "## Dependencies and Parallel Safety",
    "## Acceptance Scenarios", "## Verification Commands",
    "## Documentation and Evidence Update", "## Stop Conditions",
    "## Required Handoff", "## Planning History",
}
STATUSES = {
    "captured", "shaping", "decision-blocked", "ready", "active",
    "verifying", "complete", "superseded",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


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
        print("Usage: validate_work_packet.py <WRK markdown>", file=sys.stderr)
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
    if not data.get("id", "").startswith("WRK-") or data.get("id") == "WRK-0000":
        errors.append("id must be a non-placeholder WRK-* identifier")
    if data.get("kind") != "work-packet":
        errors.append("kind must be work-packet")
    if not data.get("parent", "").startswith("SLI-") or data.get("parent") == "SLI-0000":
        errors.append("parent must be a non-placeholder SLI-* identifier")
    if not data.get("capability", "").startswith("CAP-") or data.get("capability") == "CAP-0000":
        errors.append("capability must be a non-placeholder CAP-* identifier")
    if data.get("planning_status") not in STATUSES:
        errors.append("invalid planning_status")
    if any(
        key.endswith(("_approval", "_approved_by", "_approved_at"))
        or key == "implementation_authority"
        for key in data
    ):
        errors.append("approval and authority metadata must remain in the ignored local ledger")
    if not DATE_RE.match(data.get("updated", "")):
        errors.append("updated must be YYYY-MM-DD")
    if data.get("planning_status") == "decision-blocked" and data.get("decision_gates") == "[]":
        errors.append("decision-blocked requires at least one decision gate")
    if data.get("planning_status") in {"active", "verifying", "complete"}:
        if data.get("write_scope") == "[]":
            errors.append("active or later requires write_scope")
        for field in ("base_revision", "claim_id", "claimed_by"):
            if data.get(field) in {"", "null", "unassigned"}:
                errors.append(f"active or later requires {field}")
        if not TIMESTAMP_RE.match(data.get("claimed_at", "")):
            errors.append("active or later requires claimed_at as an ISO UTC timestamp")
    for heading in HEADINGS:
        if heading not in text:
            errors.append(f"missing heading: {heading}")
    if "Short Objective" in text or "YYYY-MM-DD" in text:
        errors.append("artifact contains template placeholders")
    if "AGENTS.md" not in text or "docs/README.md" not in text:
        errors.append("Required Context must name AGENTS.md and docs/README.md")
    if errors:
        print("Work-packet validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Work-packet validation passed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
