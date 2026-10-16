#!/usr/bin/env python3
"""Focused dynamic roadmap review contract and adapter tests."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from contracts import ControlError  # noqa: E402
from financial_academy_roadmap_review import projection  # noqa: E402
from financial_academy_portfolio import allocation_result  # noqa: E402
from roadmap_review import build_projection, safe_document, validate_catalog  # noqa: E402


REPO = HERE.parents[1]


def catalog() -> dict:
    return {
        "schema_version": "capability-catalog-v1",
        "capabilities": [
            {"key": "learn", "order": 1, "title": "Learn", "description": "Learn safely.", "planning_id": "PROGRAM-1"},
            {"key": "practice", "order": 2, "title": "Practice", "description": "Practice safely.", "planning_id": None},
        ],
    }


def nodes() -> list[dict]:
    return [
        {"id": "PROGRAM-1", "kind": "capability", "status": "ready", "title": "Program one", "source": "plans/program-1.md", "parent": None, "dependencies": [], "manifest": ["INCREMENT-1", "INCREMENT-2"], "decision_gates": []},
        {"id": "PROGRAM-INTERNAL", "kind": "capability", "status": "complete", "title": "Internal", "source": "plans/internal.md", "parent": None, "dependencies": [], "manifest": ["INCREMENT-INTERNAL"], "decision_gates": []},
        {"id": "INCREMENT-1", "kind": "slice", "status": "active", "title": "Increment", "source": "plans/increment-1.md", "parent": "PROGRAM-1", "dependencies": [], "manifest": [], "decision_gates": []},
        {"id": "TASK-1", "kind": "work", "status": "complete", "title": "Task", "source": "plans/task-1.md", "parent": "INCREMENT-1", "dependencies": [], "manifest": [], "decision_gates": []},
        {"id": "INCREMENT-INTERNAL", "kind": "slice", "status": "complete", "title": "Internal increment", "source": "plans/increment-internal.md", "parent": "PROGRAM-INTERNAL", "dependencies": [], "manifest": [], "decision_gates": []},
        {"id": "TASK-INTERNAL", "kind": "work", "status": "complete", "title": "Internal task", "source": "plans/task-internal.md", "parent": "INCREMENT-INTERNAL", "dependencies": [], "manifest": [], "decision_gates": []},
    ]


def allocation(*, ids: list[str] | None = None, groups: list[list[str]] | None = None) -> dict:
    ordered = ids or ["PROGRAM-1"]
    return {
        "schema_version": "portfolio-allocation-v1",
        "level": "capability",
        "lanes": [
            {
                "unit_id": unit_id,
                "allocation_state": "proposed",
                "lifecycle_status": "ready",
                "branches": ["codex/private-local-branch"],
                "coordination": {"live_lease_paths": ["private/path"]},
            }
            for unit_id in ordered
        ],
        "parallel_groups": groups or [[unit_id] for unit_id in ordered],
        "unresolved_pairs": [],
    }


def project(*, document_suffix: str = "") -> dict:
    graph = {"schema_version": "portfolio-graph-v1", "issues": []}
    ordering = {"schema_version": "portfolio-plan-v1", "proposed_order": ["PROGRAM-1"]}
    compatibility = {"schema_version": "portfolio-compatibility-v1", "parallel_safe_sets": []}
    documents = {
        item["id"]: {"source": item["source"], "text": f"# {item['title']}\n\nSafe text{document_suffix}"}
        for item in nodes()
    }
    return build_projection(
        catalog=catalog(),
        planning_nodes=nodes(),
        documents=documents,
        graph=graph,
        ordering=ordering,
        compatibility=compatibility,
        allocation=allocation(),
        expected_catalog_count=2,
    )


class RoadmapReviewTests(unittest.TestCase):
    def test_generic_projection_keeps_unplanned_and_missing_children_visible(self) -> None:
        result = project()
        self.assertEqual(result["schema_version"], "roadmap-review-v1")
        self.assertEqual([item["key"] for item in result["candidates"]], ["learn", "practice"])
        self.assertTrue(result["candidates"][0]["planned"])
        self.assertFalse(result["candidates"][1]["planned"])
        slices = result["candidates"][0]["slices"]
        self.assertEqual(slices[0]["work"][0]["id"], "TASK-1")
        self.assertFalse(slices[1]["refined"])
        self.assertEqual([item["id"] for item in result["internal_capabilities"]], ["PROGRAM-INTERNAL"])
        self.assertEqual(result["internal_capabilities"][0]["slices"][0]["id"], "INCREMENT-INTERNAL")
        self.assertEqual(result["internal_capabilities"][0]["slices"][0]["work"][0]["id"], "TASK-INTERNAL")
        self.assertEqual(result["diagnostics"][0]["code"], "roadmap.slice-not-refined")

    def test_catalog_rejects_duplicate_mapping_and_noncontiguous_order(self) -> None:
        duplicate = catalog()
        duplicate["capabilities"][1]["planning_id"] = "PROGRAM-1"
        with self.assertRaises(ControlError) as caught:
            validate_catalog(duplicate, expected_count=2)
        self.assertEqual(caught.exception.code, "roadmap.catalog-duplicate")

        unordered = catalog()
        unordered["capabilities"][1]["order"] = 4
        with self.assertRaises(ControlError) as caught:
            validate_catalog(unordered, expected_count=2)
        self.assertEqual(caught.exception.code, "roadmap.catalog-order-invalid")

    def test_projection_rejects_unknown_formal_mapping(self) -> None:
        value = catalog()
        value["capabilities"][0]["planning_id"] = "PROGRAM-MISSING"
        with self.assertRaises(ControlError) as caught:
            build_projection(
                catalog=value,
                planning_nodes=nodes(),
                documents={},
                graph={"issues": []},
                ordering={},
                compatibility={},
                allocation=allocation(),
                expected_catalog_count=2,
            )
        self.assertEqual(caught.exception.code, "roadmap.catalog-mapping-missing")

    def test_document_is_inert_and_source_is_confined(self) -> None:
        document = safe_document(
            "# Plan\n\n<script>alert('x')</script>\n\n- [link](javascript:alert(1))",
            source="plans/plan.md",
        )
        rendered = json.dumps(document)
        self.assertIn("<script>", rendered)
        self.assertNotIn("type\": \"html", rendered)
        with self.assertRaises(ControlError) as caught:
            safe_document("# Plan", source="../secret.txt")
        self.assertEqual(caught.exception.code, "roadmap.source-invalid")

    def test_source_fingerprint_changes_with_plan_content(self) -> None:
        self.assertNotEqual(project()["source_fingerprint"], project(document_suffix=" changed")["source_fingerprint"])

    def test_source_fingerprint_changes_with_lifecycle_state(self) -> None:
        changed = nodes()
        changed[0]["status"] = "active"
        documents = {
            item["id"]: {"source": item["source"], "text": f"# {item['title']}\n\nSafe text"}
            for item in changed
        }
        result = build_projection(
            catalog=catalog(),
            planning_nodes=changed,
            documents=documents,
            graph={"issues": []},
            ordering={"proposed_order": ["PROGRAM-1"]},
            compatibility={"parallel_safe_sets": []},
            allocation=allocation(),
            expected_catalog_count=2,
        )
        self.assertNotEqual(project()["source_fingerprint"], result["source_fingerprint"])
        self.assertEqual(result["candidates"][0]["capability"]["status"], "active")

    def test_empty_generic_catalog_is_valid_and_expected_count_drift_fails(self) -> None:
        result = build_projection(
            catalog={"schema_version": "capability-catalog-v1", "capabilities": []},
            planning_nodes=[],
            documents={},
            graph={"issues": []},
            ordering={"proposed_order": []},
            compatibility={"parallel_safe_sets": []},
            allocation={
                "schema_version": "portfolio-allocation-v1",
                "level": "capability",
                "lanes": [],
                "parallel_groups": [],
                "unresolved_pairs": [],
            },
            expected_catalog_count=0,
        )
        self.assertEqual(result["catalog_count"], 0)
        self.assertEqual(result["candidates"], [])
        with self.assertRaises(ControlError) as caught:
            validate_catalog(catalog(), expected_count=3)
        self.assertEqual(caught.exception.code, "roadmap.catalog-count")

    def test_generic_core_has_no_repository_vocabulary_dependency(self) -> None:
        source = (HERE / "roadmap_review.py").read_text(encoding="utf-8")
        self.assertNotIn("Financial AI Academy", source)
        self.assertNotIn("CAP-", source)
        self.assertNotIn("SLI-", source)
        self.assertNotIn("WRK-", source)

    def test_current_allocation_preserves_parallel_groups_without_locking_future_order(self) -> None:
        result = build_projection(
            catalog=catalog(),
            planning_nodes=nodes(),
            documents={},
            graph={"issues": []},
            ordering={"proposed_order": ["PROGRAM-1", "PROGRAM-INTERNAL"]},
            compatibility={"parallel_safe_sets": [["PROGRAM-1", "PROGRAM-INTERNAL"]]},
            allocation=allocation(
                ids=["PROGRAM-1", "PROGRAM-INTERNAL"],
                groups=[["PROGRAM-1", "PROGRAM-INTERNAL"]],
            ),
            expected_catalog_count=2,
        )
        current = result["current_allocation"]
        self.assertEqual(
            [lane["unit_id"] for lane in current["lanes"]],
            ["PROGRAM-1", "PROGRAM-INTERNAL"],
        )
        self.assertEqual(current["parallel_groups"], [["PROGRAM-1", "PROGRAM-INTERNAL"]])
        self.assertFalse(current["constraints"]["future_order_is_global_lock"])
        serialized = json.dumps(current)
        self.assertNotIn('"branches":', serialized)
        self.assertNotIn('"coordination":', serialized)

        advisory = copy.deepcopy(result)
        advisory["ordering"]["proposed_order"].append("PROGRAM-FUTURE")
        self.assertNotIn(
            "PROGRAM-FUTURE",
            [lane["unit_id"] for lane in advisory["current_allocation"]["lanes"]],
        )

    def test_current_allocation_rejects_groups_that_do_not_partition_lanes(self) -> None:
        with self.assertRaises(ControlError) as caught:
            build_projection(
                catalog=catalog(),
                planning_nodes=nodes(),
                documents={},
                graph={"issues": []},
                ordering={"proposed_order": ["PROGRAM-1"]},
                compatibility={"parallel_safe_sets": []},
                allocation=allocation(ids=["PROGRAM-1"], groups=[["PROGRAM-INTERNAL"]]),
                expected_catalog_count=2,
            )
        self.assertEqual(caught.exception.code, "roadmap.allocation-group-invalid")

    def test_current_repository_projects_exact_catalog_and_explicit_mappings(self) -> None:
        result = projection(REPO)
        self.assertEqual(result["catalog_count"], 26)
        self.assertEqual(len({item["key"] for item in result["candidates"]}), 26)
        mapped = {item["planning_id"] for item in result["candidates"] if item["planning_id"]}
        expected_mapped = {
            "CAP-0001",
            "CAP-0004",
            "CAP-0005",
            "CAP-0006",
            "CAP-0007",
            *(f"CAP-{number:04d}" for number in range(9, 30)),
        }
        self.assertEqual(mapped, expected_mapped)
        internal = {item["id"] for item in result["internal_capabilities"]}
        self.assertTrue({"CAP-0002", "CAP-0003", "CAP-0008"}.issubset(internal))
        for capability in result["internal_capabilities"]:
            self.assertEqual(capability["manifest"], [item["id"] for item in capability["slices"]])
        cap_eight = next(item for item in result["internal_capabilities"] if item["id"] == "CAP-0008")
        slice_six = next(item for item in cap_eight["slices"] if item["id"] == "SLI-0036")
        self.assertEqual([item["id"] for item in slice_six["work"]], ["WRK-0026"])
        serialized = json.dumps(result)
        self.assertNotIn('"actor_label":', serialized)
        self.assertNotIn('"reviewer_label":', serialized)
        self.assertNotIn(str(REPO), serialized)

    def test_current_repository_execution_order_matches_default_allocator(self) -> None:
        result = projection(REPO)
        expected = allocation_result(REPO, level="capability")["data"]["allocation"]
        self.assertEqual(
            [lane["unit_id"] for lane in result["current_allocation"]["lanes"]],
            [lane["unit_id"] for lane in expected["lanes"]],
        )
        self.assertEqual(result["current_allocation"]["parallel_groups"], expected["parallel_groups"])
        blocked_ids = {item["id"] for item in result["ordering"]["blocked"]}
        current_ids = {lane["unit_id"] for lane in result["current_allocation"]["lanes"]}
        self.assertTrue(blocked_ids.isdisjoint(current_ids))

    def test_cli_is_one_read_only_projection_command(self) -> None:
        before = (REPO / "docs/product/capability-catalog.json").read_bytes()
        completed = subprocess.run(
            [sys.executable, str(HERE / "control_plane.py"), "--root", str(REPO), "--json", "roadmap-review"],
            cwd=REPO,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        value = json.loads(completed.stdout)
        self.assertEqual(value["code"], "roadmap.review-projected")
        self.assertEqual(value["data"]["review"]["catalog_count"], 26)
        self.assertEqual((REPO / "docs/product/capability-catalog.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
