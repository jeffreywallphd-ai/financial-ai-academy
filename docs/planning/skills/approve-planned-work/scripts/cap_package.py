#!/usr/bin/env python3
"""Create and validate the stable binding for one CAP planning package."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

MODEL = "cap-package-v1"
GOVERNED_SECTIONS = (
    "## Outcome",
    "## Scope",
    "## In Scope",
    "## Out of Scope",
    "## Decision Gates and Constraints",
    "## Proposed Vertical Slices",
    "## Capability Acceptance",
    "## Risks and Non-Goals",
)


def as_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [as_text(item) for item in value if as_text(item)]
    text = as_text(value)
    if not text or text == "[]":
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return []
        return [as_text(item) for item in parsed if as_text(item)] if isinstance(parsed, list) else []
    return [text]


@dataclass(frozen=True)
class Artifact:
    path: Path
    metadata: dict[str, object]

    @property
    def identifier(self) -> str:
        return as_text(self.metadata.get("id"))

    @property
    def kind(self) -> str:
        return as_text(self.metadata.get("kind"))


def _frontmatter(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return {}
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}
    data: dict[str, object] = {}
    for line in lines[1:end]:
        if ":" not in line or line.startswith((" ", "-", "#")):
            continue
        key, value = line.split(":", 1)
        raw = value.strip()
        if raw in {"null", "~"}:
            data[key.strip()] = None
        elif raw.startswith("["):
            try:
                data[key.strip()] = json.loads(raw)
            except json.JSONDecodeError:
                data[key.strip()] = raw
        else:
            data[key.strip()] = raw.strip("\"'")
    return data


def load_artifacts(root: Path) -> list[Artifact]:
    location = root / "docs/planning/capabilities"
    return [Artifact(path, _frontmatter(path)) for path in sorted(location.glob("CAP-*.md"))]


def _section(text: str, heading: str) -> str:
    marker = heading + "\n"
    if marker not in text:
        return ""
    tail = text.split(marker, 1)[1]
    return tail.split("\n## ", 1)[0].strip()


def package_snapshot(capability: Artifact) -> dict[str, object]:
    metadata = capability.metadata
    if as_text(metadata.get("approval_model")) != MODEL:
        raise ValueError(f"{capability.identifier}: approval_model must be {MODEL}")
    slice_ids = as_list(metadata.get("slice_ids"))
    if not slice_ids:
        raise ValueError(f"{capability.identifier}: slice_ids must enumerate every planned slice")
    if len(slice_ids) != len(set(slice_ids)) or any(not item.startswith("SLI-") for item in slice_ids):
        raise ValueError(f"{capability.identifier}: slice_ids must be unique SLI-* identifiers")
    text = capability.path.read_text(encoding="utf-8")
    sections = {heading: _section(text, heading) for heading in GOVERNED_SECTIONS if _section(text, heading)}
    required = {"## Outcome", "## Decision Gates and Constraints", "## Proposed Vertical Slices", "## Capability Acceptance", "## Risks and Non-Goals"}
    missing = sorted(required - set(sections))
    if missing:
        raise ValueError(f"{capability.identifier}: missing governed section(s): " + ", ".join(missing))
    absent = [item for item in slice_ids if item not in sections["## Proposed Vertical Slices"]]
    if absent:
        raise ValueError(f"{capability.identifier}: slice manifest entries missing from Proposed Vertical Slices: " + ", ".join(absent))
    return {
        "model": MODEL,
        "subject": capability.identifier,
        "parent": metadata.get("parent"),
        "depends_on": as_list(metadata.get("depends_on")),
        "decision_gates": as_list(metadata.get("decision_gates")),
        "slice_ids": slice_ids,
        "sections": sections,
    }


def package_digest(capability: Artifact) -> str:
    rendered = json.dumps(package_snapshot(capability), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(rendered).hexdigest()


def find_capability(root: Path, identifier: str) -> Artifact:
    matches = [item for item in load_artifacts(root) if item.kind == "capability" and item.identifier == identifier]
    if len(matches) != 1:
        raise ValueError(f"expected one capability artifact for {identifier}")
    return matches[0]


def approval_fields(root: Path, identifier: str) -> dict[str, object]:
    capability = find_capability(root, identifier)
    snapshot = package_snapshot(capability)
    return {"approval_model": MODEL, "package_digest": package_digest(capability), "slice_ids": snapshot["slice_ids"]}
