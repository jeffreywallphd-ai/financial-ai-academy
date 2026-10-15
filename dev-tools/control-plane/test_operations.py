#!/usr/bin/env python3
"""Packet-start, correction, maintenance, anti-rigidity, and anti-bypass tests."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from contracts import ControlError  # noqa: E402
from operations import CorrectionRouteService, MaintenanceService, PacketStartService  # noqa: E402


class FixtureProject:
    def __init__(self, risk: str = "low") -> None:
        self.context = {
            "claim_id": "WRK-1:claim",
            "canonical_input_digest": "sha256:" + "1" * 64,
            "acceptance_ids": ["SLI-1:A001", "WRK-1:A001"],
            "acceptance_digest": "sha256:" + "2" * 64,
            "scope_digest": "sha256:" + "3" * 64,
            "risk": risk,
            "risk_reason": "fixture impact",
        }

    def start_context(self, work_id: str) -> dict[str, Any]:
        return copy.deepcopy(self.context)

    @staticmethod
    def correction_context(work_id: str) -> dict[str, Any]:
        return {"parent_slice": "SLI-1", "allowed_paths": ["docs", "src/exact.py"]}


class StartAndCorrectionTests(unittest.TestCase):
    def test_low_risk_start_is_short_idempotent_and_has_no_approval_or_full_suite(self) -> None:
        with tempfile.TemporaryDirectory(prefix="start-low-") as directory:
            service = PacketStartService(Path(directory), FixtureProject())
            first = service.start("WRK-1")
            second = service.start("WRK-1")
            route = first["data"]["manifest"]["route"]["required_evidence"]
            self.assertEqual(["affected-verification", "independent-technical-review"], route)
            self.assertFalse(second["data"]["created"])
            encoded = json.dumps(first).lower()
            self.assertNotIn("approval", encoded)
            self.assertNotIn("full", encoded)
            self.assertEqual(first["data"]["manifest"]["manifest_digest"], second["data"]["manifest"]["manifest_digest"])

    def test_high_risk_adds_only_explicit_aggregate_readiness(self) -> None:
        with tempfile.TemporaryDirectory(prefix="start-high-") as directory:
            route = PacketStartService(Path(directory), FixtureProject("high")).start("WRK-1")["data"]["manifest"]["route"]
            self.assertEqual(["affected-verification", "aggregate-readiness", "independent-technical-review"], route["required_evidence"])
            self.assertEqual("fixture impact", route["reason"])

    def test_start_refuses_drift_with_one_replan_action(self) -> None:
        with tempfile.TemporaryDirectory(prefix="start-drift-") as directory:
            project = FixtureProject()
            service = PacketStartService(Path(directory), project)
            service.start("WRK-1")
            project.context["acceptance_digest"] = "sha256:" + "9" * 64
            with self.assertRaises(ControlError) as drift:
                service.start("WRK-1")
            self.assertEqual("start.planning-drift", drift.exception.code)
            self.assertEqual(1, len(drift.exception.remediation))

    def test_completed_correction_route_is_bounded_idempotent_and_preserves_target(self) -> None:
        with tempfile.TemporaryDirectory(prefix="correction-") as directory:
            root = Path(directory)
            marker = root / "tracked.md"
            marker.write_text("complete\n", encoding="utf-8")
            service = CorrectionRouteService(root, FixtureProject())
            first = service.plan("WRK-1", paths=["docs/guide.md"], reason_code="regression.fixed")
            second = service.plan("WRK-1", paths=["docs/guide.md"], reason_code="regression.fixed")
            self.assertTrue(first["data"]["created"])
            self.assertFalse(second["data"]["created"])
            self.assertEqual("complete\n", marker.read_text(encoding="utf-8"))
            encoded = json.dumps(first).lower()
            self.assertNotIn("approval", encoded)
            self.assertEqual("author-bounded-descendant-wrk", first["data"]["route"]["route"][0])

    def test_correction_scope_escape_and_traversal_are_narrowly_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="correction-deny-") as directory:
            service = CorrectionRouteService(Path(directory), FixtureProject())
            with self.assertRaises(ControlError) as escape:
                service.plan("WRK-1", paths=["outside/file.py"], reason_code="scope.escape")
            self.assertEqual("correction.scope-escape", escape.exception.code)
            self.assertEqual(1, len(escape.exception.remediation))
            with self.assertRaises(ControlError) as traversal:
                service.plan("WRK-1", paths=["../docs/file.md"], reason_code="path.escape")
            self.assertEqual("correction.path-invalid", traversal.exception.code)


class MaintenanceTests(unittest.TestCase):
    def service(self, root: Path, health: list[bool], calls: list[str]) -> MaintenanceService:
        def validate() -> dict[str, Any]:
            calls.append("validate")
            health[0] = True
            return {"state_revision": 2, "work_item_count": 1}

        return MaintenanceService(root, {"validate-local-state": validate}, lambda: health[0])

    def test_allowlisted_maintenance_blocks_mutation_and_preserves_event_history(self) -> None:
        with tempfile.TemporaryDirectory(prefix="maintenance-") as directory:
            root = Path(directory)
            calls: list[str] = []
            health = [False]
            service = self.service(root, health, calls)
            started = service.start(defect_code="state.malformed", allowed_action_ids=["validate-local-state"])
            with self.assertRaises(ControlError) as blocked:
                service.guard_mutation("submit")
            self.assertEqual("maintenance.blocks-mutation", blocked.exception.code)
            action = service.execute("validate-local-state")
            finished = service.finish()
            self.assertEqual(["validate"], calls)
            self.assertEqual("maintenance.action-succeeded", action["code"])
            self.assertEqual("closed", finished["data"]["session"]["status"])
            events = sorted((root / ".local-codex/control-plane/maintenance" / started["data"]["session"]["session_id"]).glob("event-*.json"))
            self.assertEqual(3, len(events))
            self.assertEqual([1, 2, 3], [json.loads(path.read_text(encoding="utf-8"))["sequence"] for path in events])
            service.guard_mutation("submit")

    def test_unknown_action_concurrent_session_and_early_exit_are_denied(self) -> None:
        with tempfile.TemporaryDirectory(prefix="maintenance-deny-") as directory:
            service = self.service(Path(directory), [False], [])
            with self.assertRaises(ControlError) as unknown:
                service.start(defect_code="state.malformed", allowed_action_ids=["run-shell"])
            self.assertEqual("maintenance.action-not-allowed", unknown.exception.code)
            service.start(defect_code="state.malformed", allowed_action_ids=["validate-local-state"])
            with self.assertRaises(ControlError) as concurrent:
                service.start(defect_code="state.malformed", allowed_action_ids=["validate-local-state"])
            self.assertEqual("maintenance.already-active", concurrent.exception.code)
            with self.assertRaises(ControlError) as early:
                service.finish()
            self.assertEqual("maintenance.no-success", early.exception.code)

    def test_failed_action_is_audited_and_cannot_exit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="maintenance-fail-") as directory:
            root = Path(directory)

            def fail() -> dict[str, Any]:
                raise ControlError("state.still-broken", "still broken", {}, ["inspect one state record"])

            service = MaintenanceService(root, {"validate-local-state": fail}, lambda: False)
            service.start(defect_code="state.malformed", allowed_action_ids=["validate-local-state"])
            with self.assertRaises(ControlError):
                service.execute("validate-local-state")
            status = service.status()["data"]["session"]
            self.assertEqual(2, status["event_count"])
            self.assertEqual([], status["successful_action_ids"])
            with self.assertRaises(ControlError):
                service.finish()


if __name__ == "__main__":
    unittest.main()
