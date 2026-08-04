#!/usr/bin/env python3
"""Exercise planning integrity, reservation, and claim helper behavior."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_planning import run  # noqa: E402
from claim_packet import claim_updates  # noqa: E402
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

| ID | Kind | Title | Planning status | Approval summary | Parent | Dependencies | Decision gates | Owner | Updated |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
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
planning_approval: approved
planning_approved_by: project-owner
planning_approved_at: {TODAY}
implementation_approval: approved
implementation_approved_by: project-owner
implementation_approved_at: {TODAY}
implementation_authority: task-42
---

# Agent Work Packet: Test
"""


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="planning-tools-") as directory:
        root = fixture_root(Path(directory))
        assert run(root) == [], "empty planning scaffold must pass"
        first = reserve(root, "CAP", "agent-a")
        second = reserve(root, "CAP", "agent-b")
        assert first["id"] == "CAP-0001" and second["id"] == "CAP-0002"
        packet = write(root / "docs/planning/work-packets/WRK-0001-test.md", packet_text())
        updates = claim_updates(root, packet, "agent-a", "task-42", "base123")
        assert updates["planning_status"] == "active"
        update_frontmatter(packet, updates)
        claimed = frontmatter_from_path(packet)
        assert claimed["claimed_by"] == "agent-a" and claimed["base_revision"] == "base123"
        competing = write(
            root / "docs/planning/work-packets/WRK-0002-competing.md",
            packet_text("WRK-0002"),
        )
        try:
            claim_updates(root, competing, "agent-b", "task-42", "base456")
        except ValueError as exception:
            assert "overlaps active packet WRK-0001" in str(exception)
        else:
            raise AssertionError("overlapping active write scope must be refused")

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
capability_approval: pending
capability_approved_by: null
capability_approved_at: null
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
