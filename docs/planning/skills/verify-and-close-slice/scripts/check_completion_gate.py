#!/usr/bin/env python3
"""Check structural readiness for deterministic vertical-slice completion."""

from __future__ import annotations

import re
import json
import sys
from pathlib import Path

from cap_package import find as find_capability, items as cap_items, metadata as cap_metadata, require_current


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


def repository_root(path: Path) -> Path:
    current = path.resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() and (candidate / "docs").is_dir():
            return candidate
    raise ValueError("unable to locate repository root")


def load_ledger(root: Path) -> dict[str, object]:
    path = root / ".local-codex/approvals/ledger.json"
    if not path.is_file():
        raise ValueError(f"local approval ledger not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("records"), list):
        raise ValueError("local approval ledger is invalid")
    return data


def latest(ledger: dict[str, object], subject: str, stage: str) -> dict[str, object] | None:
    records = [
        item for item in ledger["records"]
        if isinstance(item, dict)
        and item.get("subject") == subject
        and item.get("stage") == stage
    ]
    return records[-1] if records else None


def require_approved(
    ledger: dict[str, object], subject: str, stage: str, errors: list[str]
) -> None:
    record = latest(ledger, subject, stage)
    if not record or record.get("decision") != "approved":
        errors.append(f"{subject}: missing approved local {stage} decision")


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
    try:
        ledger = load_ledger(repository_root(slice_path))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Completion gate failed: {error}", file=sys.stderr)
        return 1
    if slice_data.get("kind") != "vertical-slice":
        errors.append("first artifact must be a vertical-slice")
    if slice_data.get("planning_status") != "verifying":
        errors.append(f"{slice_id}: status must be verifying before completion")
    capability_id = slice_data.get("parent", "")
    try:
        capability_path = find_capability(repository_root(slice_path), capability_id)
        capability_data = cap_metadata(capability_path)
        require_current(ledger, capability_path)
        if capability_data.get("approval_model") and slice_id not in cap_items(
            capability_data.get("slice_ids")
        ):
            errors.append(f"{slice_id}: not present in approved {capability_id} slice manifest")
    except ValueError as error:
        errors.append(str(error))
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
    print("Exact test results remain required; no lower-level completion approval exists.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
