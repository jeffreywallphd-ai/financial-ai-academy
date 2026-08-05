#!/usr/bin/env python3
"""Validate the portable decision-request artifact contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path


KEYS = {
    "id", "kind", "planning_status", "authority", "owner", "updated",
    "depends_on", "decision_gates", "decision_record",
}
HEADINGS = {
    "# Decision Request:", "## Decision Needed", "## Why Now",
    "## Current Authority and Constraints", "## Options",
    "## Recommendation", "## Evidence Required", "## Required Authority",
    "## Decision Record and Promotion", "## Dependent Planning Updates",
    "## Planning History",
}
STATUSES = {
    "captured", "shaping", "decision-blocked", "ready", "active",
    "verifying", "complete", "superseded",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0] != "---":
        return {}
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}
    data: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line and not line.startswith((" ", "-")):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_decision_request.py <DEC markdown>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    data = frontmatter(text)
    errors = [f"missing metadata: {key}" for key in sorted(KEYS - data.keys())]
    if not data:
        errors.append("missing YAML-style frontmatter")
    if not data.get("id", "").startswith("DEC-") or data.get("id") == "DEC-0000":
        errors.append("id must be a non-placeholder DEC-* identifier")
    if data.get("kind") != "decision-request":
        errors.append("kind must be decision-request")
    if data.get("planning_status") not in STATUSES:
        errors.append("invalid planning_status")
    if not DATE_RE.match(data.get("updated", "")):
        errors.append("updated must be YYYY-MM-DD")
    if any(key.endswith(("_approval", "_approved_by", "_approved_at")) for key in data):
        errors.append("approval metadata must remain in the ignored local ledger")
    if data.get("planning_status") == "complete":
        if data.get("decision_record") in {"", "null"}:
            errors.append("complete decision request requires canonical decision_record")
    for heading in HEADINGS:
        if heading not in text:
            errors.append(f"missing heading: {heading}")
    if "Short Question" in text or "YYYY-MM-DD" in text:
        errors.append("artifact contains template placeholders")
    if errors:
        print("Decision-request validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Decision-request validation passed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
