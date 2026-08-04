#!/usr/bin/env python3
"""Exercise positive compatibility paths across the planning skill scripts."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TODAY = "2026-08-04"


def run(script: Path, *args: Path | str) -> str:
    completed = subprocess.run(
        [sys.executable, str(script), *(str(value) for value in args)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode:
        raise AssertionError(
            f"{script.name} failed ({completed.returncode})\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed.stdout


def asset(skill: str, name: str) -> str:
    return (ROOT / skill / "assets" / name).read_text(encoding="utf-8")


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="planning-skills-") as directory:
        temp = Path(directory)
        capability = asset("shape-capability", "capability-template.md")
        capability = capability.replace("CAP-0000", "CAP-0001").replace("YYYY-MM-DD", TODAY).replace("Short Outcome Name", "Learn Safely")
        capability_path = write(temp / "capabilities" / "CAP-0001-learn-safely.md", capability)
        run(ROOT / "shape-capability" / "scripts" / "validate_capability.py", capability_path)

        decision = asset("review-decision-gates", "decision-request-template.md")
        decision = decision.replace("DEC-0000", "DEC-0001").replace("YYYY-MM-DD", TODAY).replace("Short Question", "Choose Identity Boundary")
        decision_path = write(temp / "decisions" / "DEC-0001-identity.md", decision)
        run(ROOT / "review-decision-gates" / "scripts" / "validate_decision_request.py", decision_path)

        slice_text = asset("select-vertical-slice", "vertical-slice-template.md")
        slice_text = slice_text.replace("SLI-0000", "SLI-0001").replace("CAP-0000", "CAP-0001").replace("YYYY-MM-DD", TODAY).replace("Short Observable Increment", "Complete One Lesson")
        slice_path = write(temp / "vertical-slices" / "SLI-0001-lesson.md", slice_text)
        run(ROOT / "select-vertical-slice" / "scripts" / "validate_vertical_slice.py", slice_path)

        packet = asset("author-agent-work-packet", "work-packet-template.md")
        packet = packet.replace("WRK-0000", "WRK-0001").replace("SLI-0000", "SLI-0001").replace("CAP-0000", "CAP-0001").replace("YYYY-MM-DD", TODAY).replace("Short Objective", "Deliver Lesson Contract")
        packet_path = write(temp / "work-packets" / "WRK-0001-contract.md", packet)
        run(ROOT / "author-agent-work-packet" / "scripts" / "validate_work_packet.py", packet_path)

        approved_packet = packet.replace("planning_approval: pending", "planning_approval: approved").replace("planning_approved_by: null", "planning_approved_by: project-owner").replace("planning_approved_at: null", f"planning_approved_at: {TODAY}")
        approved_packet_path = write(temp / "work-packets" / "WRK-0002-approved.md", approved_packet.replace("WRK-0001", "WRK-0002"))
        run(ROOT / "approve-planned-work" / "scripts" / "validate_approval.py", approved_packet_path, "--stage", "planning")

        active_slice = slice_text.replace("planning_status: shaping", "planning_status: ready").replace("selection_approval: pending", "selection_approval: approved").replace("selection_approved_by: null", "selection_approved_by: project-owner").replace("selection_approved_at: null", f"selection_approved_at: {TODAY}")
        active_slice_path = write(temp / "vertical-slices" / "SLI-0002-ready.md", active_slice.replace("SLI-0001", "SLI-0002"))
        active_packet = approved_packet.replace("WRK-0001", "WRK-0003").replace("SLI-0001", "SLI-0002").replace("planning_status: shaping", "planning_status: ready").replace("write_scope: []", 'write_scope: ["modules/learning"]').replace("implementation_approval: pending", "implementation_approval: approved").replace("implementation_approved_by: null", "implementation_approved_by: project-owner").replace("implementation_approved_at: null", f"implementation_approved_at: {TODAY}").replace("implementation_authority: null", "implementation_authority: approved-task")
        active_packet_path = write(temp / "work-packets" / "WRK-0003-ready.md", active_packet)
        run(ROOT / "implement-vertical-slice" / "scripts" / "check_implementation_gate.py", active_slice_path, active_packet_path)

        evidence = "Delivered behavior, exact verification commands and results, documentation impact, assumptions, residual risks, and qualification gaps were recorded for acceptance."
        verifying_slice = active_slice.replace("SLI-0001", "SLI-0003").replace("planning_status: ready", "planning_status: verifying").replace("## Documentation Impact and Completion Evidence\n", "## Documentation Impact and Completion Evidence\n\n" + evidence + "\n")
        verifying_slice_path = write(temp / "vertical-slices" / "SLI-0003-verifying.md", verifying_slice)
        complete_packet = active_packet.replace("WRK-0003", "WRK-0004").replace("SLI-0002", "SLI-0003").replace("planning_status: ready", "planning_status: complete").replace("base_revision: null", "base_revision: abc123").replace("claim_id: null", "claim_id: WRK-0004:test").replace("claimed_by: null", "claimed_by: test-agent").replace("claimed_at: null", "claimed_at: 2026-08-04T12:00:00Z")
        complete_packet_path = write(temp / "work-packets" / "WRK-0004-complete.md", complete_packet)
        run(ROOT / "verify-and-close-slice" / "scripts" / "check_completion_gate.py", verifying_slice_path, complete_packet_path)

        routing = temp / "routing"
        routing.mkdir()
        output = run(ROOT / "guide-next-planning-action" / "scripts" / "recommend_next.py", routing)
        if json.loads(output)["skill"] != "shape-capability":
            raise AssertionError("empty planning root must route to shape-capability")
        write(routing / "capabilities" / capability_path.name, capability.replace("planning_status: captured", "planning_status: shaping"))
        output = run(ROOT / "guide-next-planning-action" / "scripts" / "recommend_next.py", routing)
        if json.loads(output)["skill"] != "shape-capability":
            raise AssertionError("shaping capability must route to shape-capability")

        routing_ready = temp / "routing-ready"
        ready_capability = capability.replace("planning_status: captured", "planning_status: ready").replace("capability_approval: pending", "capability_approval: approved").replace("capability_approved_by: null", "capability_approved_by: project-owner").replace("capability_approved_at: null", f"capability_approved_at: {TODAY}")
        write(routing_ready / "capabilities" / capability_path.name, ready_capability)
        write(routing_ready / "vertical-slices" / slice_path.name, active_slice)
        ready_packet = active_packet.replace("SLI-0002", "SLI-0001")
        write(routing_ready / "work-packets" / "WRK-0003-ready.md", ready_packet)
        output = run(ROOT / "guide-next-planning-action" / "scripts" / "recommend_next.py", routing_ready)
        if json.loads(output)["skill"] != "implement-vertical-slice":
            raise AssertionError("fully approved ready packet must route to implement-vertical-slice")
    print("Planning skill behavior tests passed: validators, gates, and router verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
