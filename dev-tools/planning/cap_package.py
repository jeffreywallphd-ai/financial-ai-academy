#!/usr/bin/env python3
"""Create and validate the stable binding for one CAP planning package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from planning_model import Artifact, as_list, as_text, load_artifacts


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


def _section(text: str, heading: str) -> str:
    marker = heading + "\n"
    if marker not in text:
        return ""
    tail = text.split(marker, 1)[1]
    return tail.split("\n## ", 1)[0].strip()


def package_snapshot(capability: Artifact) -> dict[str, object]:
    """Return the semantic fields covered by a CAP planning approval."""

    metadata = capability.metadata
    if as_text(metadata.get("approval_model")) != MODEL:
        raise ValueError(f"{capability.identifier}: approval_model must be {MODEL}")
    slice_ids = as_list(metadata.get("slice_ids"))
    if not slice_ids:
        raise ValueError(f"{capability.identifier}: slice_ids must enumerate every planned slice")
    if len(slice_ids) != len(set(slice_ids)) or any(
        not item.startswith("SLI-") for item in slice_ids
    ):
        raise ValueError(f"{capability.identifier}: slice_ids must be unique SLI-* identifiers")
    text = capability.path.read_text(encoding="utf-8")
    sections = {
        heading: _section(text, heading)
        for heading in GOVERNED_SECTIONS
        if _section(text, heading)
    }
    required = {
        "## Outcome",
        "## Decision Gates and Constraints",
        "## Proposed Vertical Slices",
        "## Capability Acceptance",
        "## Risks and Non-Goals",
    }
    missing = sorted(required - set(sections))
    if missing:
        raise ValueError(
            f"{capability.identifier}: missing governed section(s): " + ", ".join(missing)
        )
    slices_body = sections["## Proposed Vertical Slices"]
    absent = [item for item in slice_ids if item not in slices_body]
    if absent:
        raise ValueError(
            f"{capability.identifier}: slice manifest entries missing from Proposed Vertical Slices: "
            + ", ".join(absent)
        )
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
    rendered = json.dumps(
        package_snapshot(capability), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(rendered).hexdigest()


def find_capability(root: Path, identifier: str) -> Artifact:
    matches = [
        item for item in load_artifacts(root)
        if item.kind == "capability" and item.identifier == identifier
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one capability artifact for {identifier}")
    return matches[0]


def approval_fields(root: Path, identifier: str) -> dict[str, object]:
    capability = find_capability(root, identifier)
    snapshot = package_snapshot(capability)
    return {
        "approval_model": MODEL,
        "package_digest": package_digest(capability),
        "slice_ids": snapshot["slice_ids"],
    }


def require_current_package(
    store: dict[str, object], capability: Artifact
) -> dict[str, object]:
    from approval_store import ApprovalStoreError, require_decision

    record = require_decision(store, capability.identifier, "capability")
    if as_text(capability.metadata.get("approval_model")) != MODEL:
        return record
    if record.get("approval_model") != MODEL:
        raise ApprovalStoreError(
            f"{capability.identifier}: latest approval predates the CAP package model"
        )
    expected_slices = package_snapshot(capability)["slice_ids"]
    if record.get("slice_ids") != expected_slices:
        raise ApprovalStoreError(
            f"{capability.identifier}: approved slice manifest is no longer current"
        )
    if record.get("package_digest") != package_digest(capability):
        raise ApprovalStoreError(
            f"{capability.identifier}: governed CAP content changed; renew CAP approval"
        )
    return record
