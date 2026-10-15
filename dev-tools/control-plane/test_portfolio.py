#!/usr/bin/env python3
"""Focused tests for portfolio hierarchy projection."""

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

from financial_academy_portfolio import project  # noqa: E402
from portfolio import analyze  # noqa: E402


def node(identifier: str, kind: str, *, parent: str | None = None, depends: list[str] | None = None, manifest: list[str] | None = None, status: str = "ready") -> dict:
    return {
        "id": identifier,
        "kind": kind,
        "status": status,
        "title": identifier,
        "source": f"fixtures/{identifier}.md",
        "parent": parent,
        "dependencies": [{"target": item, "type": "hard"} for item in (depends or [])],
        "manifest": manifest or [],
        "decision_gates": [],
    }


class PortfolioCoreTests(unittest.TestCase):
    def test_valid_hierarchy_is_stable_and_topological(self) -> None:
        nodes = [
            node("WRK-2", "work", parent="SLI-1", depends=["WRK-1"]),
            node("CAP-1", "capability", manifest=["SLI-1"]),
            node("WRK-1", "work", parent="SLI-1"),
            node("SLI-1", "slice", parent="CAP-1"),
        ]
        first = analyze(nodes)
        second = analyze(reversed(nodes))
        self.assertEqual(first, second)
        self.assertEqual("valid", first["state"])
        self.assertLess(first["topological_order"].index("WRK-1"), first["topological_order"].index("WRK-2"))

    def test_missing_dependency_cycle_and_superseded_target_are_blocking(self) -> None:
        result = analyze([
            node("CAP-A", "capability", depends=["CAP-B", "CAP-MISSING"]),
            node("CAP-B", "capability", depends=["CAP-A"]),
            node("CAP-OLD", "capability", status="superseded"),
            node("CAP-C", "capability", depends=["CAP-OLD"]),
        ])
        codes = {issue["code"] for issue in result["issues"]}
        self.assertTrue({"dependency.missing", "dependency.cycle", "dependency.superseded"} <= codes)
        self.assertEqual("invalid", result["state"])
        self.assertEqual([], result["topological_order"])

    def test_future_manifest_detail_is_advisory_not_global_lock(self) -> None:
        result = analyze([node("CAP-1", "capability", manifest=["SLI-FUTURE"])])
        self.assertEqual("partial", result["state"])
        self.assertEqual("manifest.expected-child-missing", result["issues"][0]["code"])
        self.assertFalse(result["issues"][0]["blocking"])
        self.assertEqual(["CAP-1"], result["topological_order"])

    def test_invalid_parent_and_unlisted_slice_are_distinct(self) -> None:
        result = analyze([
            node("CAP-1", "capability", manifest=[]),
            node("SLI-1", "slice", parent="CAP-1"),
            node("WRK-1", "work", parent="CAP-1"),
        ])
        codes = {issue["code"] for issue in result["issues"]}
        self.assertIn("manifest.unlisted-child", codes)
        self.assertIn("hierarchy.parent-kind", codes)

    def test_duplicate_and_malformed_nodes_are_reported_without_crash(self) -> None:
        result = analyze([node("CAP-1", "capability"), node("CAP-1", "capability"), node("BAD", "unknown")])
        codes = {issue["code"] for issue in result["issues"]}
        self.assertIn("node.duplicate", codes)
        self.assertIn("node.kind-invalid", codes)


class FinancialAcademyPortfolioTests(unittest.TestCase):
    def test_repository_projection_preserves_authority_separation(self) -> None:
        graph = project(ROOT)
        ids = {item["id"] for item in graph["nodes"]}
        self.assertIn("CAP-0003", ids)
        self.assertIn("SLI-0009", ids)
        self.assertGreaterEqual(len([item for item in graph["nodes"] if item["kind"] == "candidate"]), 26)
        encoded = json.dumps(graph, sort_keys=True).lower()
        for forbidden in ("actor_label", "reviewer", "approved_by", "authority_reference"):
            self.assertNotIn(forbidden, encoded)

    def test_cli_emits_versioned_json_without_mutating_planning(self) -> None:
        before = (ROOT / "docs/planning/register.md").read_bytes()
        completed = subprocess.run(
            [sys.executable, str(HERE / "control_plane.py"), "--json", "portfolio-graph"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual("portfolio.graph-projected", result["code"])
        self.assertEqual("portfolio-graph-v1", result["data"]["graph"]["schema_version"])
        self.assertEqual(before, (ROOT / "docs/planning/register.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
