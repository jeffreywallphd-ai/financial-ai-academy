#!/usr/bin/env python3
"""Focused tests for reusable hierarchy-aware allocation and replanning."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from contracts import ControlError  # noqa: E402
from financial_academy_portfolio import planning_nodes, projected_claim_branch  # noqa: E402
from portfolio import analyze  # noqa: E402
from portfolio_allocation import allocate  # noqa: E402


def work_graph(*, third_incomplete: bool = False, dependency: bool = False) -> dict:
    reciprocal = ["TASK-A", "TASK-B", "TASK-C"]
    nodes = [
        {"id": "PROGRAM-X", "kind": "capability", "status": "ready", "manifest": ["INCREMENT-X"], "manifest_declared": True, "dependencies": [], "decision_gates": [], "scope_complete": True},
        {"id": "INCREMENT-X", "kind": "slice", "status": "active", "parent": "PROGRAM-X", "dependencies": [], "decision_gates": [], "scope_complete": True},
        {"id": "TASK-A", "kind": "work", "status": "ready", "parent": "INCREMENT-X", "dependencies": [], "decision_gates": [], "write_scope": ["alpha/a.py"], "generated_artifacts": [], "parallel_safe_with": reciprocal, "scope_complete": True},
        {"id": "TASK-B", "kind": "work", "status": "ready", "parent": "INCREMENT-X", "dependencies": [{"target": "TASK-A", "type": "hard"}] if dependency else [], "decision_gates": [], "write_scope": ["beta/b.py"], "generated_artifacts": [], "parallel_safe_with": reciprocal, "scope_complete": True},
        {"id": "TASK-C", "kind": "work", "status": "ready", "parent": "INCREMENT-X", "dependencies": [], "decision_gates": [], "write_scope": [] if third_incomplete else ["gamma/c.py"], "generated_artifacts": [], "parallel_safe_with": reciprocal, "scope_complete": not third_incomplete},
    ]
    return analyze(nodes)


class PortfolioAllocationTests(unittest.TestCase):
    def test_compatibility_branch_marker_is_not_projected_as_git_evidence(self) -> None:
        self.assertIsNone(projected_claim_branch({"branch": "legacy-unrecorded"}))
        self.assertIsNone(projected_claim_branch({"branch": ""}))
        self.assertEqual(
            "codex/cap-0004",
            projected_claim_branch({"branch": "codex/cap-0004"}),
        )

    def test_planning_nodes_fall_back_from_compatibility_marker_and_roll_up_branches(self) -> None:
        def artifact(identifier: str, kind: str, status: str, metadata: dict) -> SimpleNamespace:
            return SimpleNamespace(
                identifier=identifier,
                kind=kind,
                status=status,
                metadata=metadata,
                path=Path(f"{identifier}.md"),
                relative_path=f"docs/planning/{identifier}.md",
            )

        artifacts = [
            artifact("PROGRAM-X", "capability", "active", {"slice_ids": ["INCREMENT-X"]}),
            artifact("INCREMENT-X", "vertical-slice", "active", {"parent": "PROGRAM-X"}),
            artifact(
                "TASK-HISTORICAL",
                "work-packet",
                "complete",
                {"parent": "INCREMENT-X", "write_scope": ["history.txt"], "generated_artifacts": []},
            ),
            artifact(
                "TASK-ACTIVE",
                "work-packet",
                "active",
                {"parent": "INCREMENT-X", "write_scope": ["active.txt"], "generated_artifacts": []},
            ),
        ]
        with tempfile.TemporaryDirectory(prefix="portfolio-branch-projection-") as directory:
            root = Path(directory)
            state_path = root / ".local-codex/control-plane/state.json"
            state_path.parent.mkdir(parents=True)

            def project(active_branch: str) -> dict[str, dict]:
                state_path.write_text(
                    json.dumps(
                        {
                            "work_items": {
                                "TASK-HISTORICAL": {
                                    "state": "submitted",
                                    "claim": {"branch": "legacy-unrecorded"},
                                },
                                "TASK-ACTIVE": {
                                    "state": "active",
                                    "claim": {"branch": active_branch},
                                },
                            }
                        }
                    ),
                    encoding="utf-8",
                )
                with (
                    patch("financial_academy_portfolio.load_artifacts", return_value=artifacts),
                    patch("financial_academy_portfolio.current_branch", return_value="codex/current"),
                ):
                    return {node["id"]: node for node in planning_nodes(root)}

            compatibility = project("legacy-unrecorded")
            self.assertEqual([], compatibility["TASK-HISTORICAL"]["branches"])
            self.assertEqual(["codex/current"], compatibility["TASK-ACTIVE"]["branches"])
            self.assertEqual(["codex/current"], compatibility["INCREMENT-X"]["branches"])
            self.assertEqual(["codex/current"], compatibility["PROGRAM-X"]["branches"])

            genuine = project("codex/recorded")
            self.assertEqual(["codex/recorded"], genuine["TASK-ACTIVE"]["branches"])
            self.assertEqual(["codex/current", "codex/recorded"], genuine["INCREMENT-X"]["branches"])
            self.assertEqual(["codex/current", "codex/recorded"], genuine["PROGRAM-X"]["branches"])

    def test_generic_vocabulary_honors_priority_and_groups_compatible_work(self) -> None:
        result = allocate(work_graph(), level="work", authority_current=["PROGRAM-X"], explicit_priority=["TASK-B", "TASK-A", "TASK-C"])
        self.assertEqual(["TASK-B", "TASK-A", "TASK-C"], [item["unit_id"] for item in result["lanes"]])
        self.assertEqual([["TASK-B", "TASK-A", "TASK-C"]], result["parallel_groups"])
        self.assertTrue(result["constraints"]["single_hierarchy_level"])
        self.assertFalse(result["constraints"]["creates_agents"])
        self.assertTrue(all(item["unit_kind"] == "work" for item in result["lanes"]))

    def test_dependency_blocks_only_dependent_work(self) -> None:
        result = allocate(work_graph(dependency=True), level="work", authority_current=["PROGRAM-X"])
        lane_ids = [item["unit_id"] for item in result["lanes"]]
        self.assertIn("TASK-A", lane_ids)
        self.assertNotIn("TASK-B", lane_ids)
        blocked = {item["id"]: item for item in result["blocked"]}
        self.assertEqual(["dependency.incomplete"], blocked["TASK-B"]["reasons"])

    def test_unknown_scope_isolates_only_affected_lane(self) -> None:
        result = allocate(work_graph(third_incomplete=True), level="work", authority_current=["PROGRAM-X"])
        self.assertIn(["TASK-A", "TASK-B"], result["parallel_groups"])
        self.assertIn(["TASK-C"], result["parallel_groups"])
        unknown = [item for item in result["unresolved_pairs"] if item["decision"] == "unknown"]
        self.assertEqual(2, len(unknown))
        self.assertTrue(all("evidence.scope-incomplete" in item["reason_codes"] for item in unknown))

    def test_container_reports_active_descendants_branch_and_coordination_without_duplication(self) -> None:
        graph = analyze([
            {"id": "PROGRAM-X", "kind": "capability", "status": "active", "manifest": ["INCREMENT-X"], "manifest_declared": True, "dependencies": [], "decision_gates": [], "branches": ["codex/program-x"], "scope_complete": True},
            {"id": "INCREMENT-X", "kind": "slice", "status": "active", "parent": "PROGRAM-X", "dependencies": [], "decision_gates": [], "scope_complete": True},
            {"id": "TASK-A", "kind": "work", "status": "active", "parent": "INCREMENT-X", "dependencies": [], "decision_gates": [], "write_scope": ["alpha/a.py"], "generated_artifacts": [], "active_claim": True, "scope_complete": True},
        ])
        coordination = {"revision": 3, "intents": [{"unit_id": "TASK-A", "work_id": "TASK-A", "paths": ["alpha/next.py"]}], "leases": [{"unit_id": "TASK-A", "work_id": "TASK-A", "paths": ["alpha/a.py"], "state": "live"}]}
        result = allocate(graph, level="capability", authority_current=["PROGRAM-X"], coordination=coordination)
        self.assertEqual(["PROGRAM-X"], [item["unit_id"] for item in result["lanes"]])
        lane = result["lanes"][0]
        self.assertEqual(["INCREMENT-X", "TASK-A"], lane["active_descendants"])
        self.assertEqual("codex", lane["branch_state"])
        self.assertEqual(["alpha/a.py"], lane["coordination"]["live_lease_paths"])
        self.assertEqual(3, result["coordination_revision"])

    def test_replan_preserves_previous_digest_and_explains_live_fact_change(self) -> None:
        first = allocate(work_graph(), level="work", authority_current=["PROGRAM-X"], explicit_priority=["TASK-A", "TASK-B", "TASK-C"])
        coordination = {"revision": 2, "intents": [], "leases": [{"unit_id": "TASK-A", "work_id": "TASK-A", "paths": ["alpha/a.py"], "state": "live"}]}
        second = allocate(work_graph(), level="work", authority_current=["PROGRAM-X"], explicit_priority=["TASK-B", "TASK-A", "TASK-C"], coordination=coordination, previous=first)
        self.assertNotEqual(first["plan_digest"], second["plan_digest"])
        self.assertEqual(first["plan_digest"], second["replan"]["previous_plan_digest"])
        self.assertTrue(second["replan"]["changed"])
        task_change = next(item for item in second["replan"]["changes"] if item.get("unit_id") == "TASK-A")
        self.assertIn("coordination", task_change["fields"])

    def test_invalid_level_graph_and_previous_plan_are_refused(self) -> None:
        with self.assertRaises(ControlError) as level:
            allocate(work_graph(), level="everything", authority_current=["PROGRAM-X"])
        self.assertEqual("allocation.level-invalid", level.exception.code)
        with self.assertRaises(ControlError) as previous:
            allocate(work_graph(), level="work", authority_current=["PROGRAM-X"], previous={"schema_version": "old"})
        self.assertEqual("allocation.previous-incompatible", previous.exception.code)

    def test_repository_cli_is_read_only(self) -> None:
        before_register = (ROOT / "docs/planning/register.md").read_bytes()
        before_lease_state = (ROOT / ".local-codex/control-plane/file-leases.json").read_bytes() if (ROOT / ".local-codex/control-plane/file-leases.json").is_file() else None
        completed = subprocess.run(
            [sys.executable, str(HERE / "control_plane.py"), "--json", "portfolio-allocate", "--level", "slice", "--priority", "SLI-0013"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        result = json.loads(completed.stdout)["data"]["allocation"]
        self.assertEqual("portfolio-allocation-v1", result["schema_version"])
        self.assertFalse(result["constraints"]["grants_authority"])
        self.assertEqual(before_register, (ROOT / "docs/planning/register.md").read_bytes())
        after_lease_state = (ROOT / ".local-codex/control-plane/file-leases.json").read_bytes() if (ROOT / ".local-codex/control-plane/file-leases.json").is_file() else None
        self.assertEqual(before_lease_state, after_lease_state)


if __name__ == "__main__":
    unittest.main()
