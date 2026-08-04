#!/usr/bin/env python3
"""Check slice and packet metadata before implementation starts."""

from __future__ import annotations

import re
import sys
from pathlib import Path


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


def metadata(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
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


def approved(data: dict[str, str], prefix: str, label: str, errors: list[str]) -> None:
    if data.get(f"{prefix}_approval") != "approved":
        errors.append(f"{label}: {prefix}_approval is not approved")
    if data.get(f"{prefix}_approved_by") in {None, "", "null", "unassigned"}:
        errors.append(f"{label}: missing {prefix}_approved_by")
    if not DATE_RE.match(data.get(f"{prefix}_approved_at", "")):
        errors.append(f"{label}: invalid {prefix}_approved_at")


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: check_implementation_gate.py <SLI markdown> <WRK markdown> [<WRK markdown> ...]", file=sys.stderr)
        return 2
    paths = [Path(value) for value in sys.argv[1:]]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        print("ERROR: missing files: " + ", ".join(missing), file=sys.stderr)
        return 2
    slice_path, *packet_paths = paths
    slice_data = metadata(slice_path)
    errors: list[str] = []
    if slice_data.get("kind") != "vertical-slice":
        errors.append("first artifact must be a vertical-slice")
    if slice_data.get("planning_status") == "decision-blocked":
        errors.append("slice is decision-blocked")
    approved(slice_data, "selection", slice_data.get("id", str(slice_path)), errors)
    slice_id = slice_data.get("id")
    seen: set[str] = set()
    for path in packet_paths:
        data = metadata(path)
        label = data.get("id", str(path))
        if data.get("kind") != "work-packet":
            errors.append(f"{label}: kind must be work-packet")
        if data.get("parent") != slice_id:
            errors.append(f"{label}: parent does not match {slice_id}")
        if data.get("planning_status") not in {"ready", "active"}:
            errors.append(f"{label}: status must be ready or active")
        if data.get("planning_status") == "decision-blocked":
            errors.append(f"{label}: packet is decision-blocked")
        approved(data, "planning", label, errors)
        approved(data, "implementation", label, errors)
        if data.get("implementation_authority") in {None, "", "null"}:
            errors.append(f"{label}: missing implementation_authority")
        if data.get("write_scope") in {None, "", "[]"}:
            errors.append(f"{label}: missing write_scope")
        if data.get("planning_status") == "active":
            for field in ("base_revision", "claim_id", "claimed_by"):
                if data.get(field) in {None, "", "null", "unassigned"}:
                    errors.append(f"{label}: active packet missing {field}")
            if not TIMESTAMP_RE.match(data.get("claimed_at", "")):
                errors.append(f"{label}: active packet has invalid claimed_at")
        packet_id = data.get("id")
        if packet_id in seen:
            errors.append(f"duplicate packet: {packet_id}")
        if packet_id:
            seen.add(packet_id)
        text = path.read_text(encoding="utf-8")
        if "AGENTS.md" not in text or "docs/README.md" not in text:
            errors.append(f"{label}: Required Context must name AGENTS.md and docs/README.md")
    if errors:
        print("Implementation gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Implementation gate passed: {slice_id} with {len(packet_paths)} packet(s)")
    print("A current explicit user instruction is still required; this script cannot verify conversation authority.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
