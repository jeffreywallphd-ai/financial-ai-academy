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


def record(
    root: Path,
    subject: str,
    stage: str,
    *,
    authority: str = "test-authority",
    scope: str | None = None,
) -> None:
    args: list[str] = [
        "--root", str(root), "record",
        "--subject", subject,
        "--stage", stage,
        "--decision", "approved",
        "--actor-label", "test authority",
        "--decided-at", TODAY,
        "--authority", authority,
        "--confirm-human-decision",
    ]
    if scope:
        args.extend(["--scope", scope])
    run(ROOT / "approve-planned-work" / "scripts" / "manage_approval.py", *args)


def record_bundle(
    root: Path,
    subjects: list[str],
    stage: str,
    *,
    bundle_subject: str | None = None,
) -> None:
    args: list[str] = [
        "--root", str(root), "record-bundle",
        "--subjects", *subjects,
        "--stage", stage,
        "--decision", "approved",
        "--actor-label", "test authority",
        "--decided-at", TODAY,
        "--authority", "approved-bundle-task",
        "--confirm-human-decision",
    ]
    if bundle_subject:
        args.extend(["--bundle-subject", bundle_subject])
    if stage == "implementation":
        args.append("--scope-from-artifacts")
    run(ROOT / "approve-planned-work" / "scripts" / "manage_approval.py", *args)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="planning-skills-") as directory:
        temp = Path(directory)
        (temp / ".git").mkdir()
        (temp / "docs").mkdir()
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

        approved_packet_path = write(
            temp / "work-packets" / "WRK-0002-approved.md",
            packet.replace("WRK-0001", "WRK-0002"),
        )
        record(temp, "WRK-0002", "planning")
        run(
            ROOT / "approve-planned-work" / "scripts" / "validate_approval.py",
            approved_packet_path,
            "--stage", "planning",
            "--root", temp,
        )

        active_slice = slice_text.replace("planning_status: shaping", "planning_status: ready")
        active_slice_path = write(temp / "vertical-slices" / "SLI-0002-ready.md", active_slice.replace("SLI-0001", "SLI-0002"))
        active_packet = packet.replace("WRK-0001", "WRK-0003").replace("SLI-0001", "SLI-0002").replace("planning_status: shaping", "planning_status: ready").replace("write_scope: []", 'write_scope: ["modules/learning"]')
        active_packet_path = write(temp / "work-packets" / "WRK-0003-ready.md", active_packet)
        record(temp, "SLI-0002", "selection")
        record(temp, "WRK-0003", "planning")
        record(temp, "WRK-0003", "implementation", authority="approved-task", scope="modules/learning")
        run(ROOT / "implement-vertical-slice" / "scripts" / "check_implementation_gate.py", active_slice_path, active_packet_path)

        record_bundle(temp, ["DEC-0101", "DEC-0102"], "decision", bundle_subject="CAP-0001")
        bundled_slice = active_slice.replace("SLI-0001", "SLI-0100")
        bundled_slice_path = write(
            temp / "docs/planning/vertical-slices/SLI-0100-bundled.md",
            bundled_slice,
        )
        bundled_packet_a = active_packet.replace("WRK-0003", "WRK-0101").replace(
            "SLI-0002", "SLI-0100"
        )
        bundled_packet_b = bundled_packet_a.replace("WRK-0101", "WRK-0102").replace(
            "depends_on: []", 'depends_on: ["WRK-0101"]'
        ).replace(
            'write_scope: ["modules/learning"]',
            'write_scope: ["modules/assessment"]',
        )
        bundled_packet_a_path = write(
            temp / "docs/planning/work-packets/WRK-0101-first.md",
            bundled_packet_a,
        )
        bundled_packet_b_path = write(
            temp / "docs/planning/work-packets/WRK-0102-second.md",
            bundled_packet_b,
        )
        record(temp, "SLI-0100", "selection")
        record_bundle(
            temp,
            ["WRK-0101", "WRK-0102"],
            "planning",
            bundle_subject="SLI-0100",
        )
        record_bundle(
            temp,
            ["WRK-0101", "WRK-0102"],
            "implementation",
            bundle_subject="SLI-0100",
        )
        run(
            ROOT / "implement-vertical-slice" / "scripts" / "check_implementation_gate.py",
            bundled_slice_path,
            bundled_packet_a_path,
            bundled_packet_b_path,
        )
        ledger = json.loads(
            (temp / ".local-codex/approvals/ledger.json").read_text(encoding="utf-8")
        )
        implementation_bundle = [
            item for item in ledger["records"]
            if item.get("stage") == "implementation"
            and item.get("subject") in {"WRK-0101", "WRK-0102"}
        ]
        assert len(implementation_bundle) == 2
        assert len({item["bundle_id"] for item in implementation_bundle}) == 1

        evidence = "Delivered behavior, exact verification commands and results, documentation impact, assumptions, residual risks, and qualification gaps were recorded for acceptance."
        verifying_slice = active_slice.replace("SLI-0001", "SLI-0003").replace("planning_status: ready", "planning_status: verifying").replace("## Documentation Impact and Completion Evidence\n", "## Documentation Impact and Completion Evidence\n\n" + evidence + "\n")
        verifying_slice_path = write(temp / "vertical-slices" / "SLI-0003-verifying.md", verifying_slice)
        complete_packet = active_packet.replace("WRK-0003", "WRK-0004").replace("SLI-0002", "SLI-0003").replace("planning_status: ready", "planning_status: complete").replace("base_revision: null", "base_revision: abc123").replace("claim_id: null", "claim_id: WRK-0004:test").replace("claimed_by: null", "claimed_by: test-agent").replace("claimed_at: null", "claimed_at: 2026-08-04T12:00:00Z")
        complete_packet_path = write(temp / "work-packets" / "WRK-0004-complete.md", complete_packet)
        record(temp, "SLI-0003", "selection")
        record(temp, "WRK-0004", "planning")
        record(temp, "WRK-0004", "implementation", scope="modules/learning")
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
        ready_capability = capability.replace("planning_status: captured", "planning_status: ready")
        write(routing_ready / "capabilities" / capability_path.name, ready_capability)
        write(routing_ready / "vertical-slices" / slice_path.name, active_slice)
        ready_packet = active_packet.replace("SLI-0002", "SLI-0001")
        write(routing_ready / "work-packets" / "WRK-0003-ready.md", ready_packet)
        record(temp, "CAP-0001", "capability")
        record(temp, "SLI-0001", "selection")
        output = run(ROOT / "guide-next-planning-action" / "scripts" / "recommend_next.py", routing_ready)
        if json.loads(output)["skill"] != "implement-vertical-slice":
            raise AssertionError("fully approved ready packet must route to implement-vertical-slice")
    print("Planning skill behavior tests passed: validators, gates, and router verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
