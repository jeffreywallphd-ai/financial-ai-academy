#!/usr/bin/env python3
"""Validate a recorded human approval without modifying its artifact."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PREFIXES = {
    "capability": "capability",
    "decision": "decision",
    "selection": "selection",
    "planning": "planning",
    "implementation": "implementation",
    "completion": "completion",
}
DECISIONS = {"approved", "changes-requested", "rejected"}
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--stage", choices=sorted(PREFIXES), required=True)
    args = parser.parse_args()
    if not args.artifact.is_file():
        parser.error(f"file not found: {args.artifact}")
    text = args.artifact.read_text(encoding="utf-8")
    data = metadata(text)
    prefix = PREFIXES[args.stage]
    decision = data.get(f"{prefix}_approval")
    errors: list[str] = []
    if decision not in DECISIONS:
        errors.append(f"{prefix}_approval must record approved, changes-requested, or rejected")
    if data.get(f"{prefix}_approved_by") in {None, "", "null", "unassigned"}:
        errors.append(f"{prefix}_approved_by must identify the human approver")
    if not DATE_RE.match(data.get(f"{prefix}_approved_at", "")):
        errors.append(f"{prefix}_approved_at must be YYYY-MM-DD")
    if args.stage == "implementation" and data.get("implementation_authority") in {None, "", "null"}:
        errors.append("implementation_authority must identify scoped authority")
    if "## Approval History" not in text:
        errors.append("artifact must contain an Approval History section")
    if errors:
        print("Approval validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Approval validation passed: {args.stage} on {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
