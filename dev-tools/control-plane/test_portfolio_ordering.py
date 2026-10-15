#!/usr/bin/env python3
"""Focused tests for hierarchy-aware readiness and ordering."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from contracts import ControlError  # noqa: E402
from financial_academy_portfolio import current_capability_authority, project  # noqa: E402
from portfolio import analyze  # noqa: E402
from portfolio_ordering import plan  # noqa: E402


def graph_nodes() -> list[dict]:
    return [
        {"id": "CAP-1", "kind": "capability", "status": "ready", "manifest": ["SLI-1", "SLI-2"], "manifest_declared": True, "dependencies": [], "decision_gates": []},
        {"id": "CAP-2", "kind": "capability", "status": "ready", "manifest": [], "manifest_declared": True, "dependencies": [], "decision_gates": []},
        {"id": "SLI-1", "kind": "slice", "status": "complete", "parent": "CAP-1", "dependencies": [], "decision_gates": []},
        {"id": "SLI-2", "kind": "slice", "status": "ready", "parent": "CAP-1", "dependencies": [{"target": "SLI-1", "type": "hard"}], "decision_gates": []},
        {"id": "WRK-1", "kind": "work", "status": "complete", "parent": "SLI-1", "dependencies": [], "decision_gates": []},
        {"id": "WRK-2", "kind": "work", "status": "ready", "parent": "SLI-2", "dependencies": [{"target": "WRK-1", "type": "hard"}], "decision_gates": []},
    ]


class PortfolioOrderingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = analyze(graph_nodes())

    def test_capability_tie_is_visible_and_priority_is_explicit(self) -> None:
        tied = plan(self.graph, level="capability", authority_current=["CAP-1", "CAP-2"])
        self.assertEqual([["CAP-1", "CAP-2"]], tied["unresolved_ties"])
        self.assertFalse(tied["constraints"]["stable_id_order_is_authority"])
        prioritized = plan(self.graph, level="capability", authority_current=["CAP-1", "CAP-2"], explicit_priority=["CAP-2", "CAP-1"])
        self.assertEqual(["CAP-2", "CAP-1"], prioritized["proposed_order"])
        self.assertEqual([], prioritized["unresolved_ties"])

    def test_slice_and_work_readiness_preserve_parent_authority(self) -> None:
        slices = plan(self.graph, level="slice", authority_current=["CAP-1"])
        self.assertEqual(["SLI-2"], [item["id"] for item in slices["ready"]])
        self.assertEqual(["SLI-1"], slices["completed"])
        work = plan(self.graph, level="work", authority_current=["CAP-1"])
        self.assertEqual(["WRK-2"], [item["id"] for item in work["ready"]])

    def test_missing_authority_is_bounded_and_contains_no_ledger_data(self) -> None:
        result = plan(self.graph, level="capability", authority_current=[])
        self.assertEqual([], result["ready"])
        self.assertTrue(all(item["reasons"] == ["authority.cap-package-not-current"] for item in result["blocked"]))
        encoded = json.dumps(result).lower()
        self.assertNotIn("actor_label", encoded)
        self.assertNotIn("decided_at", encoded)

    def test_incomplete_dependency_orders_future_work_but_not_ready_set(self) -> None:
        graph = analyze([
            {"id": "CAP-1", "kind": "capability", "status": "ready", "manifest": ["SLI-A", "SLI-B"], "manifest_declared": True, "dependencies": [], "decision_gates": []},
            {"id": "SLI-A", "kind": "slice", "status": "ready", "parent": "CAP-1", "dependencies": [], "decision_gates": []},
            {"id": "SLI-B", "kind": "slice", "status": "ready", "parent": "CAP-1", "dependencies": [{"target": "SLI-A", "type": "hard"}], "decision_gates": []},
        ])
        result = plan(graph, level="slice", authority_current=["CAP-1"])
        self.assertEqual(["SLI-A"], [item["id"] for item in result["ready"]])
        self.assertEqual(["SLI-A", "SLI-B"], result["proposed_order"])
        blocked = {item["id"]: item for item in result["blocked"]}
        self.assertEqual(["dependency.incomplete"], blocked["SLI-B"]["reasons"])

    def test_invalid_or_out_of_level_priority_is_refused(self) -> None:
        with self.assertRaises(ControlError) as duplicate:
            plan(self.graph, level="capability", authority_current=["CAP-1"], explicit_priority=["CAP-1", "CAP-1"])
        self.assertEqual("portfolio.explicit_priority-invalid", duplicate.exception.code)
        with self.assertRaises(ControlError) as outside:
            plan(self.graph, level="capability", authority_current=["CAP-1"], explicit_priority=["SLI-1"])
        self.assertEqual("portfolio.explicit_priority-outside-level", outside.exception.code)

    def test_repository_authority_adapter_exposes_only_current_cap_ids(self) -> None:
        current = current_capability_authority(ROOT)
        self.assertIn("CAP-0003", current)
        graph = project(ROOT)
        result = plan(graph, level="slice", authority_current=current)
        by_id = {item["id"]: item for item in graph["nodes"]}
        self.assertTrue(result["in_progress"])
        self.assertTrue(all(by_id[item]["parent"] in current for item in result["in_progress"]))

    def test_cli_plan_is_read_only(self) -> None:
        before = (ROOT / "docs/planning/register.md").read_bytes()
        completed = subprocess.run(
            [sys.executable, str(HERE / "control_plane.py"), "--json", "portfolio-plan", "--level", "capability", "--priority", "CAP-0003"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual("portfolio-plan-v1", result["data"]["plan"]["schema_version"])
        self.assertEqual(before, (ROOT / "docs/planning/register.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
