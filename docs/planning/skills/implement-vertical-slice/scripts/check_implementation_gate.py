#!/usr/bin/env python3
"""Check CAP authority and public structure before implementation."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from cap_package import find as find_capability, items as cap_items, metadata as cap_metadata, require_current


TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)


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
            result[key.strip()] = value.strip().strip(chr(34))
    return result


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


def approved(
    ledger: dict[str, object], subject: str, stage: str, errors: list[str]
) -> dict[str, object] | None:
    records = [
        item for item in ledger["records"]
        if isinstance(item, dict)
        and item.get("subject") == subject
        and item.get("stage") == stage
    ]
    record = records[-1] if records else None
    if not record or record.get("decision") != "approved":
        errors.append(f"{subject}: missing approved local {stage} decision")
        return None
    return record


def scope_items(value: object) -> list[str]:
    if isinstance(value, list):
        items = value
    else:
        text = "" if value is None else str(value).strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                inner = text[1:-1].strip() if text.endswith("]") else ""
                parsed = (
                    [
                        item.strip().strip(chr(34)).strip(chr(39))
                        for item in inner.split(",")
                    ]
                    if inner
                    else []
                )
            items = parsed if isinstance(parsed, list) else []
        else:
            items = [text]
    normalized = {
        str(item)
        .strip()
        .replace(chr(92), "/")
        .removeprefix("./")
        .removesuffix("/**")
        .rstrip("/")
        for item in items
        if str(item).strip()
    }
    return sorted(item for item in normalized if item)


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "Usage: check_implementation_gate.py "
            "<SLI markdown> <WRK markdown> [<WRK markdown> ...]",
            file=sys.stderr,
        )
        return 2
    paths = [Path(value) for value in sys.argv[1:]]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        print("ERROR: missing files: " + ", ".join(missing), file=sys.stderr)
        return 2
    slice_path, *packet_paths = paths
    slice_data = metadata(slice_path)
    errors: list[str] = []
    try:
        ledger = load_ledger(repository_root(slice_path))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Implementation gate failed: {error}", file=sys.stderr)
        return 1
    if slice_data.get("kind") != "vertical-slice":
        errors.append("first artifact must be a vertical-slice")
    if slice_data.get("planning_status") == "decision-blocked":
        errors.append("slice is decision-blocked")
    slice_id = slice_data.get("id")
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
    seen: set[str] = set()
    packet_data = [(path, metadata(path)) for path in packet_paths]
    packet_ids = {data.get("id", "") for _path, data in packet_data}
    for path, data in packet_data:
        label = data.get("id", str(path))
        if data.get("kind") != "work-packet":
            errors.append(f"{label}: kind must be work-packet")
        if data.get("parent") != slice_id:
            errors.append(f"{label}: parent does not match {slice_id}")
        if data.get("planning_status") not in {"ready", "active"}:
            errors.append(f"{label}: status must be ready or active")
        if data.get("planning_status") == "decision-blocked":
            errors.append(f"{label}: packet is decision-blocked")
        if not scope_items(data.get("write_scope")):
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
        for dependency in scope_items(data.get("depends_on")):
            if dependency in packet_ids and dependency not in seen:
                errors.append(
                    f"{label}: dependency {dependency} must appear earlier "
                    "in the packet order"
                )
        if packet_id:
            seen.add(packet_id)
        text = path.read_text(encoding="utf-8")
        if "AGENTS.md" not in text or "docs/README.md" not in text:
            errors.append(
                f"{label}: Required Context must name AGENTS.md and docs/README.md"
            )
    if errors:
        print("Implementation gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"Implementation gate passed: {slice_id} "
        f"with {len(packet_paths)} packet(s)"
    )
    print("CAP package authority is current; no lower-level approval is required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
