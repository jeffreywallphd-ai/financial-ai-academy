#!/usr/bin/env python3
"""Focused tests for conflict-aware parallel-safe portfolio sets."""

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
from portfolio_conflicts import analyze_compatibility  # noqa: E402


def cap(identifier: str, *, depends: list[str] | None = None, scope: list[str] | None = None, generated: list[str] | None = None, complete: bool = True, resource: list[str] | None = None) -> dict:
    return {"id": identifier, "kind": "capability", "status": "ready", "dependencies": [{"target": item, "type": "hard"} for item in (depends or [])], "manifest": [], "manifest_declared": True, "decision_gates": [], "write_scope": scope or [], "generated_artifacts": generated or [], "contracts": [item for item in (scope or []) if item.startswith("contracts/")], "exclusive_resources": resource or [], "scope_complete": complete}


def work(identifier: str, parent: str, *, scope: list[str], safe: list[str]) -> dict:
    return {"id": identifier, "kind": "work", "status": "ready", "parent": parent, "dependencies": [], "decision_gates": [], "write_scope": scope, "generated_artifacts": [], "parallel_safe_with": safe, "scope_complete": True}


class PortfolioConflictTests(unittest.TestCase):
    def test_dependency_and_scope_collisions_are_incompatible(self) -> None:
        graph = analyze([cap("CAP-A", scope=["src/a"]), cap("CAP-B", depends=["CAP-A"], scope=["src/b"]), cap("CAP-C", scope=["SRC/shared/file.py"]), cap("CAP-D", scope=["src/shared"])])
        result = analyze_compatibility(graph, level="capability")
        decisions = {(item["left"], item["right"]): item for item in result["pairs"]}
        self.assertEqual("incompatible", decisions[("CAP-A", "CAP-B")]["decision"])
        self.assertEqual("incompatible", decisions[("CAP-C", "CAP-D")]["decision"])
        self.assertIn("scope.write-overlap", {reason["code"] for reason in decisions[("CAP-C", "CAP-D")]["reasons"]})

    def test_generated_contract_resource_and_branch_collisions_are_categorical(self) -> None:
        left = cap("CAP-A", scope=["contracts/public/a.json"], generated=["generated/client"], resource=["exclusive-db"])
        right = cap("CAP-B", scope=["generated/client/file.ts", "contracts/public"], resource=["exclusive-db"])
        left.update({"active_claim": True, "branches": ["codex/shared"]})
        right.update({"active_claim": True, "branches": ["codex/shared"]})
        pair = analyze_compatibility(analyze([left, right]), level="capability")["pairs"][0]
        codes = {reason["code"] for reason in pair["reasons"]}
        self.assertTrue({"scope.write-generated-overlap", "contract.overlap", "resource.exclusive-overlap", "branch.active-overlap"} <= codes)

    def test_unknown_scope_is_not_fabricated_safe_or_global_conflict(self) -> None:
        result = analyze_compatibility(analyze([cap("CAP-A", complete=False), cap("CAP-B", scope=["src/b"])]), level="capability")
        pair = result["pairs"][0]
        self.assertEqual("unknown", pair["decision"])
        self.assertEqual(0, result["incompatible_pair_count"])
        self.assertEqual([], result["parallel_safe_sets"])
        self.assertIn("Refine only", pair["remediation"])

    def test_disjoint_caps_form_safe_set_and_every_pair_is_compatible(self) -> None:
        graph = analyze([cap("CAP-A", scope=["src/a"]), cap("CAP-B", scope=["src/b"]), cap("CAP-C", scope=["src/c"])])
        result = analyze_compatibility(graph, level="capability")
        self.assertEqual([["CAP-A", "CAP-B", "CAP-C"]], result["parallel_safe_sets"])
        self.assertTrue(all(item["decision"] == "compatible" for item in result["pairs"]))

    def test_work_requires_reciprocal_parallel_declarations(self) -> None:
        base = {"id": "CAP-1", "kind": "capability", "status": "ready", "manifest": ["SLI-1"], "manifest_declared": True, "dependencies": [], "decision_gates": [], "scope_complete": True}
        slice_node = {"id": "SLI-1", "kind": "slice", "status": "active", "parent": "CAP-1", "dependencies": [], "decision_gates": [], "scope_complete": True}
        missing = analyze_compatibility(analyze([base, slice_node, work("WRK-A", "SLI-1", scope=["src/a"], safe=[]), work("WRK-B", "SLI-1", scope=["src/b"], safe=[])]), level="work")
        self.assertEqual("unknown", missing["pairs"][0]["decision"])
        reciprocal = analyze_compatibility(analyze([base, slice_node, work("WRK-A", "SLI-1", scope=["src/a"], safe=["WRK-B"]), work("WRK-B", "SLI-1", scope=["src/b"], safe=["WRK-A"])]), level="work")
        self.assertEqual("compatible", reciprocal["pairs"][0]["decision"])

    def test_repository_projection_marks_fully_refined_cap_scope_complete(self) -> None:
        graph = project(ROOT)
        cap3 = next(item for item in graph["nodes"] if item["id"] == "CAP-0003")
        self.assertTrue(cap3["scope_complete"])
        self.assertEqual(6, len(cap3["manifest"]))
        self.assertIn("dev-tools/control-plane/portfolio.py", cap3["write_scope"])

    def test_cli_is_read_only_and_privacy_minimal(self) -> None:
        before = (ROOT / "docs/planning/register.md").read_bytes()
        completed = subprocess.run([sys.executable, str(HERE / "control_plane.py"), "--json", "portfolio-compatibility", "--level", "capability"], cwd=ROOT, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(0, completed.returncode, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual("portfolio-compatibility-v1", result["data"]["compatibility"]["schema_version"])
        self.assertNotIn("claimed_by", completed.stdout)
        self.assertEqual(before, (ROOT / "docs/planning/register.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
