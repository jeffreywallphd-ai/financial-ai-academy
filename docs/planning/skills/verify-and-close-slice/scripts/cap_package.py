#!/usr/bin/env python3
"""Portable CAP package fingerprint helpers for a standalone planning skill."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


MODEL = "cap-package-v1"
SECTIONS = ("## Outcome", "## Scope", "## In Scope", "## Out of Scope", "## Decision Gates and Constraints", "## Proposed Vertical Slices", "## Capability Acceptance", "## Risks and Non-Goals")


def metadata(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---": return {}
    try: end = lines[1:].index("---") + 1
    except ValueError: return {}
    data: dict[str, object] = {}
    for line in lines[1:end]:
        if ":" not in line or line.startswith((" ", "-", "#")): continue
        key, raw = line.split(":", 1); value = raw.strip()
        if value.startswith("["):
            try: data[key.strip()] = json.loads(value)
            except json.JSONDecodeError: data[key.strip()] = []
        elif value in {"null", "~"}: data[key.strip()] = None
        else: data[key.strip()] = value.strip("\"'")
    return data


def items(value: object) -> list[str]:
    return [str(item).strip() for item in value if str(item).strip()] if isinstance(value, list) else []


def find(root: Path, identifier: str) -> Path:
    matches = sorted((root / "docs/planning/capabilities").glob(identifier + "-*.md"))
    if len(matches) != 1: raise ValueError(f"expected one capability artifact for {identifier}")
    return matches[0]


def snapshot(path: Path) -> dict[str, object]:
    data = metadata(path)
    if data.get("approval_model") != MODEL: return {"model": "legacy", "subject": data.get("id")}
    text = path.read_text(encoding="utf-8"); section_data: dict[str, str] = {}
    for heading in SECTIONS:
        marker = heading + "\n"
        if marker in text:
            body = text.split(marker, 1)[1].split("\n## ", 1)[0].strip()
            if body: section_data[heading] = body
    return {"model": MODEL, "subject": data.get("id"), "parent": data.get("parent"), "depends_on": items(data.get("depends_on")), "decision_gates": items(data.get("decision_gates")), "slice_ids": items(data.get("slice_ids")), "sections": section_data}


def digest(path: Path) -> str:
    payload = json.dumps(snapshot(path), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def require_current(ledger: dict[str, object], path: Path) -> dict[str, object]:
    data = metadata(path)
    records = [item for item in ledger.get("records", []) if isinstance(item, dict) and item.get("subject") == data.get("id") and item.get("stage") == "capability"]
    record = records[-1] if records else None
    if not record or record.get("decision") != "approved": raise ValueError(f"{data.get('id')}: missing approved local capability decision")
    if data.get("approval_model") == MODEL and (record.get("approval_model") != MODEL or record.get("slice_ids") != items(data.get("slice_ids")) or record.get("package_digest") != digest(path)):
        raise ValueError(f"{data.get('id')}: CAP package approval is stale")
    return record
