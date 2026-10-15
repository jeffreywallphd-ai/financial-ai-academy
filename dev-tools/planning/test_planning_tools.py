#!/usr/bin/env python3
"""Exercise planning integrity, reservation, and claim helper behavior."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_planning import run  # noqa: E402
from claim_packet import claim_updates, finalize_updates, release_updates  # noqa: E402
from approval_store import empty_store, save_store, store_path  # noqa: E402
from cap_package import approval_fields  # noqa: E402
from planning_model import frontmatter_from_path, update_frontmatter  # noqa: E402
from reserve_id import reserve  # noqa: E402


TODAY = "2026-08-04"


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")
    return path


def fixture_root(path: Path) -> Path:
    (path / ".git").mkdir()
    for folder in (
        "capabilities", "decision-requests", "vertical-slices", "work-packets"
    ):
        (path / "docs/planning" / folder).mkdir(parents=True, exist_ok=True)
    write(
        path / "docs/planning/register.md",
        """
# Planning Register

| ID | Kind | Title | Planning status | Parent | Dependencies | Decision gates | Owner | Updated |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
""",
    )
    return path


def packet_text(identifier: str = "WRK-0001", status: str = "ready") -> str:
    claim = status in {"active", "verifying", "complete"}
    claim_id = f"{identifier}:test" if claim else "null"
    base_revision = "abc123" if claim else "null"
    claimed_by = "test-agent" if claim else "null"
    claimed_at = "2026-08-04T12:00:00Z" if claim else "null"
    return f"""---
id: {identifier}
kind: work-packet
planning_status: {status}
authority: noncanonical
owner: test-agent
updated: {TODAY}
parent: SLI-0001
capability: CAP-0001
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: [\"modules/learning\"]
generated_artifacts: []
base_revision: {base_revision}
claim_id: {claim_id}
claimed_by: {claimed_by}
claimed_at: {claimed_at}
---

# Agent Work Packet: Test
"""


def capability_text() -> str:
    return f"""---
id: CAP-0001
kind: capability
planning_status: ready
authority: noncanonical
owner: unassigned
updated: {TODAY}
parent: null
depends_on: []
decision_gates: []
approval_model: cap-package-v1
slice_ids: [\"SLI-0001\"]
---

# Capability: Test planning control

## Outcome

An agent can claim one bounded packet.

## Decision Gates and Constraints

The work remains repository-local.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies | Material boundary | Status |
| --- | --- | --- | --- | --- |
| SLI-0001 | Claim one packet | none | remote execution | ready |

## Capability Acceptance

Claims are exclusive and recoverable.

## Risks and Non-Goals

Do not coordinate remote workers.
"""


def slice_text() -> str:
    return f"""---
id: SLI-0001
kind: vertical-slice
planning_status: ready
authority: noncanonical
owner: unassigned
updated: {TODAY}
parent: CAP-0001
depends_on: []
decision_gates: []
---

# Vertical Slice: Claim one packet
"""


def prepare_cap(root: Path) -> None:
    write(root / "docs/planning/capabilities/CAP-0001-test.md", capability_text())
    write(root / "docs/planning/vertical-slices/SLI-0001-test.md", slice_text())


def approve_cap(root: Path) -> None:
    store = empty_store()
    record = {
        "subject": "CAP-0001",
        "stage": "capability",
        "decision": "approved",
        "actor_label": "test authority",
        "decided_at": TODAY,
        "authority": "task-42",
        "recorded_at": "2026-08-04T12:00:00Z",
        **approval_fields(root, "CAP-0001"),
    }
    store["records"].append(record)
    save_store(store_path(root), store)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="planning-tools-") as directory:
        root = fixture_root(Path(directory))
        assert run(root) == [], "empty planning scaffold must pass"
        first = reserve(root, "CAP", "agent-a")
        second = reserve(root, "CAP", "agent-b")
        assert first["id"] == "CAP-0001" and second["id"] == "CAP-0002"
        prepare_cap(root)
        approve_cap(root)
        packet = write(root / "docs/planning/work-packets/WRK-0001-test.md", packet_text())
        capability_path = root / "docs/planning/capabilities/CAP-0001-test.md"
        write(
            capability_path,
            capability_text().replace(
                "An agent can claim one bounded packet.",
                "An agent can claim and remotely dispatch one bounded packet.",
            ),
        )
        try:
            claim_updates(root, packet, "agent-a", "base123")
        except ValueError as exception:
            assert "renew CAP approval" in str(exception)
        else:
            raise AssertionError("material CAP drift must invalidate packet claims")
        write(capability_path, capability_text())
        updates = claim_updates(root, packet, "agent-a", "base123")
        assert updates["planning_status"] == "active"
        update_frontmatter(packet, updates)
        claimed = frontmatter_from_path(packet)
        assert claimed["claimed_by"] == "agent-a" and claimed["base_revision"] == "base123"
        competing = write(
            root / "docs/planning/work-packets/WRK-0002-competing.md",
            packet_text("WRK-0002"),
        )
        store_path(root).unlink()
        approve_cap(root)
        try:
            claim_updates(root, competing, "agent-b", "base456")
        except ValueError as exception:
            assert "overlaps active packet WRK-0001" in str(exception)
        else:
            raise AssertionError("overlapping active write scope must be refused")
        update_frontmatter(packet, release_updates(packet, "agent-a", "verifying"))
        update_frontmatter(packet, finalize_updates(packet, "agent-a"))
        assert frontmatter_from_path(packet)["planning_status"] == "complete"

    with tempfile.TemporaryDirectory(prefix="planning-dependencies-") as directory:
        root = fixture_root(Path(directory))
        prepare_cap(root)
        dependency = write(
            root / "docs/planning/work-packets/WRK-0001-dependency.md",
            packet_text("WRK-0001"),
        )
        dependent = write(
            root / "docs/planning/work-packets/WRK-0002-dependent.md",
            packet_text("WRK-0002").replace(
                "depends_on: []", 'depends_on: ["WRK-0001"]'
            ),
        )
        approve_cap(root)
        try:
            claim_updates(root, dependent, "agent-b", "base456")
        except ValueError as exception:
            assert "dependency WRK-0001 must be complete" in str(exception)
        else:
            raise AssertionError("incomplete dependencies must prevent claim")
        assert frontmatter_from_path(dependency)["planning_status"] == "ready"

    with tempfile.TemporaryDirectory(prefix="planning-duplicates-") as directory:
        root = fixture_root(Path(directory))
        capability = f"""---
id: CAP-0001
kind: capability
planning_status: captured
authority: noncanonical
owner: unassigned
updated: {TODAY}
parent: null
depends_on: []
decision_gates: []
---
"""
        write(root / "docs/planning/capabilities/CAP-0001-first.md", capability)
        write(root / "docs/planning/capabilities/CAP-0001-second.md", capability)
        errors = run(root)
        assert any("duplicate id CAP-0001" in issue for issue in errors)
        assert any("register.md: missing CAP-0001" in issue for issue in errors)

    print("Planning tool tests passed: integrity, reservation, collision, and claim paths verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
