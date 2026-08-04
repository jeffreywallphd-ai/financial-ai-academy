#!/usr/bin/env python3
"""Check structural readiness for vertical-slice completion acceptance."""

from __future__ import annotations

import re
import sys
from pathlib import Path


TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


def metadata(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
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


def section_body(text: str, heading: str) -> str:
    marker = heading + "\n"
    if marker not in text:
        return ""
    tail = text.split(marker, 1)[1]
    return tail.split("\n## ", 1)[0].strip()


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: check_completion_gate.py <SLI markdown> <WRK markdown> [<WRK markdown> ...]", file=sys.stderr)
        return 2
    paths = [Path(value) for value in sys.argv[1:]]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        print("ERROR: missing files: " + ", ".join(missing), file=sys.stderr)
        return 2
    slice_path, *packet_paths = paths
    slice_text = slice_path.read_text(encoding="utf-8")
    slice_data = metadata(slice_path)
    slice_id = slice_data.get("id", str(slice_path))
    errors: list[str] = []
    if slice_data.get("kind") != "vertical-slice":
        errors.append("first artifact must be a vertical-slice")
    if slice_data.get("planning_status") != "verifying":
        errors.append(f"{slice_id}: status must be verifying before acceptance")
    if slice_data.get("selection_approval") != "approved":
        errors.append(f"{slice_id}: selection approval is missing")
    if slice_data.get("completion_approval") not in {"pending", "changes-requested"}:
        errors.append(f"{slice_id}: completion approval must still await a human decision")
    evidence = section_body(slice_text, "## Documentation Impact and Completion Evidence")
    if len(evidence) < 80:
        errors.append(f"{slice_id}: completion evidence section is incomplete")
    for path in packet_paths:
        data = metadata(path)
        label = data.get("id", str(path))
        if data.get("kind") != "work-packet":
            errors.append(f"{label}: kind must be work-packet")
        if data.get("parent") != slice_data.get("id"):
            errors.append(f"{label}: parent does not match {slice_id}")
        if data.get("planning_status") != "complete":
            errors.append(f"{label}: packet must be complete")
        if data.get("planning_approval") != "approved" or data.get("implementation_approval") != "approved":
            errors.append(f"{label}: required approvals are missing")
        for field in ("base_revision", "claim_id", "claimed_by"):
            if data.get(field) in {None, "", "null", "unassigned"}:
                errors.append(f"{label}: completion requires retained {field}")
        if not TIMESTAMP_RE.match(data.get("claimed_at", "")):
            errors.append(f"{label}: completion requires retained claimed_at")
    if errors:
        print("Completion gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Completion structure passed: {slice_id} with {len(packet_paths)} packet(s)")
    print("Exact test results and explicit human completion acceptance remain required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
