#!/usr/bin/env python3
"""Cumulative qualification for portfolio planning and edit coordination."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from financial_academy_portfolio import catalog_nodes, project  # noqa: E402
from portfolio_harness import evaluate_corpus, evaluate_scenario  # noqa: E402
from provenance import validates  # noqa: E402


class PortfolioHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.corpus = json.loads((HERE / "evals/portfolio-scenarios.json").read_text(encoding="utf-8"))

    def test_real_core_corpus_passes_hard_safety_and_friction_budgets(self) -> None:
        first = evaluate_corpus(self.corpus)
        second = evaluate_corpus(self.corpus)
        self.assertEqual("passed", first["status"])
        self.assertEqual(7, first["passed_count"])
        self.assertEqual(first, second)
        self.assertGreaterEqual(first["aggregate_metrics"]["parallel_lane_count"], 9)
        encoded = json.dumps(first, sort_keys=True)
        for forbidden in ("nodes", "write_scope", "generated_artifacts", "prompt", "reviewer_label", "actor_label"):
            self.assertNotIn(forbidden, encoded)

    def test_safety_mismatch_cannot_be_offset_by_generous_friction_budget(self) -> None:
        scenario = copy.deepcopy(next(item for item in self.corpus["scenarios"] if item["id"] == "disjoint-work-uses-parallelism"))
        scenario["expected"]["parallel_groups"] = [["TASK-A"], ["TASK-B"], ["TASK-C"]]
        scenario["budgets"] = {"max_blocked_count": 99, "max_isolated_lane_count": 99, "min_parallel_lane_count": 0, "max_unresolved_pair_count": 99}
        result = evaluate_scenario(scenario)
        self.assertEqual("failed", result["status"])
        self.assertIn("safety.parallel-groups-mismatch", result["violations"])

    def test_malformed_and_duplicate_corpora_fail_deterministically(self) -> None:
        malformed = evaluate_corpus({"schema_version": "old", "scenarios": []})
        self.assertEqual("failed", malformed["status"])
        duplicate = copy.deepcopy(self.corpus)
        duplicate["scenarios"][1]["id"] = duplicate["scenarios"][0]["id"]
        report = evaluate_corpus(duplicate)
        self.assertEqual("failed", report["status"])
        self.assertTrue(any("corpus.ids-not-unique-sorted" in item["violations"] for item in report["results"]))


class RepositoryQualificationTests(unittest.TestCase):
    def test_current_catalog_projects_all_26_candidates_beside_governed_work(self) -> None:
        candidates = catalog_nodes(ROOT)
        self.assertEqual(26, len(candidates))
        graph = project(ROOT)
        self.assertEqual(26, sum(item["kind"] == "candidate" and not item["governed"] for item in graph["nodes"]))
        self.assertTrue(any(item["kind"] == "capability" and item["governed"] for item in graph["nodes"]))

    def test_generic_modules_do_not_import_repository_adapter_or_vocabulary_ids(self) -> None:
        for name in ("portfolio.py", "portfolio_ordering.py", "portfolio_conflicts.py", "portfolio_allocation.py", "portfolio_harness.py", "file_leases.py"):
            text = (HERE / name).read_text(encoding="utf-8").lower()
            self.assertNotIn("financial_academy", text, name)
            self.assertNotIn("cap-000", text, name)
            self.assertNotIn("sli-000", text, name)
            self.assertNotIn("wrk-000", text, name)

    def test_allocation_cli_is_payload_minimized_and_provenance_valid(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(HERE / "control_plane.py"), "--json", "portfolio-allocate", "--level", "work", "--priority", "WRK-0022"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(validates(result))
        encoded = json.dumps(result).lower()
        for forbidden in ("prompt", "credential", "reviewer_label", "actor_label", "stdout", "stderr"):
            self.assertNotIn(forbidden, encoded)
        self.assertFalse(result["data"]["allocation"]["constraints"]["creates_agents"])

    def test_evaluator_report_path_is_confined(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(HERE / "evaluate_portfolio.py"), "--report-path", "../escape.json"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(2, completed.returncode)
        self.assertIn("Portfolio evaluation failed", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_fixed_readiness_gate_includes_every_portfolio_boundary(self) -> None:
        readiness = (ROOT / "dev-tools/agent/check_ready.py").read_text(encoding="utf-8")
        for command in (
            "test_portfolio.py",
            "test_portfolio_ordering.py",
            "test_portfolio_conflicts.py",
            "test_file_leases.py",
            "test_portfolio_allocation.py",
            "test_portfolio_qualification.py",
            "evaluate_portfolio.py",
        ):
            self.assertIn(command, readiness)


if __name__ == "__main__":
    unittest.main()
