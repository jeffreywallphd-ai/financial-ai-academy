#!/usr/bin/env python3
"""Policy, operator projection, report privacy, parity, and anti-rigidity tests."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
AGENT = HERE.parent / "agent"
for path in (HERE, AGENT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_ready import output_summary, write_report as write_readiness_report  # noqa: E402
from contracts import ControlError  # noqa: E402
from operator_status import OperatorStatusService, project_status  # noqa: E402
from policy import Fact, Rule, evaluate_policy, write_report  # noqa: E402


RULES = (
    Rule("fixture.local-evidence", "error", "local", "repair only local evidence", lambda value: value is True),
    Rule("fixture.public-invariant", "error", "public", "repair only the public invariant", lambda value: value is True),
)


class CountingSource:
    def __init__(self, snapshots: list[dict[str, Any]]) -> None:
        self.values = snapshots
        self.calls = 0

    def snapshots(self) -> list[dict[str, Any]]:
        self.calls += 1
        return copy.deepcopy(self.values)


class PolicyTests(unittest.TestCase):
    def test_local_and_ci_share_rule_inventory_and_semantics(self) -> None:
        facts = {"local": Fact(True, True, 1), "public": Fact(True, False, 1)}
        local = evaluate_policy(RULES, facts, profile="local")
        ci = evaluate_policy(RULES, facts, profile="ci")
        self.assertEqual(
            [(item["rule_id"], item["disposition"]) for item in local["rules"]],
            [(item["rule_id"], item["disposition"]) for item in ci["rules"]],
        )

    def test_unavailable_ignored_evidence_is_explicit_and_does_not_fail_public_ci(self) -> None:
        report = evaluate_policy(
            RULES,
            {"local": Fact(False, reason="ignored in CI"), "public": Fact(True, True, 1)},
            profile="ci",
        )
        self.assertEqual("ready", report["status"])
        self.assertEqual("not-evaluated", report["rules"][0]["disposition"])
        self.assertEqual("passed", report["rules"][1]["disposition"])

    def test_failure_has_one_narrow_remediation_and_no_raw_evidence(self) -> None:
        secret = "reviewer@example.invalid raw command output C:\\private\\repo"
        report = evaluate_policy(
            RULES,
            {"local": Fact(True, True, 1), "public": Fact(True, {"secret": secret}, 1, "")},
            profile="local",
        )
        encoded = json.dumps(report)
        self.assertEqual("failed", report["status"])
        self.assertNotIn(secret, encoded)
        failure = [item for item in report["rules"] if item["disposition"] == "failed"]
        self.assertEqual(["repair only the public invariant"], [item["remediation"] for item in failure])

    def test_report_output_is_atomic_and_confined(self) -> None:
        with tempfile.TemporaryDirectory(prefix="policy-report-") as directory:
            root = Path(directory)
            report = evaluate_policy(RULES, {"local": Fact(True, True), "public": Fact(True, True)}, profile="local")
            path = write_report(root, "artifacts/control-plane/policy.json", report)
            self.assertEqual("control-policy-report-v1", json.loads(path.read_text(encoding="utf-8"))["schema_version"])
            with self.assertRaises(ControlError) as outside:
                write_report(root, "docs/policy.json", report)
            self.assertEqual("policy.report-path-not-confined", outside.exception.code)

    def test_readiness_machine_report_uses_digests_not_raw_output_or_commands(self) -> None:
        with tempfile.TemporaryDirectory(prefix="readiness-report-") as directory:
            root = Path(directory)
            raw = "secret command output C:\\private\\repo"
            report = {
                "schema_version": "agent-readiness-report-v1",
                "checks": [{"check_id": "fixture", "stdout": output_summary(raw), "stderr": output_summary("")}],
            }
            path = write_readiness_report(root, "artifacts/control-plane/readiness.json", report)
            encoded = path.read_text(encoding="utf-8")
            self.assertNotIn(raw, encoded)
            self.assertIn("sha256", encoded)
            with self.assertRaises(ValueError):
                write_readiness_report(root, "../readiness.json", report)


class OperatorStatusTests(unittest.TestCase):
    def test_status_is_one_read_only_call_and_needs_no_approval_or_check_suite(self) -> None:
        source = CountingSource([{"work_id": "WORK-1", "public_status": "ready"}])
        before = copy.deepcopy(source.values)
        result = OperatorStatusService(source).status()
        self.assertEqual(1, source.calls)
        self.assertEqual(before, source.values)
        self.assertEqual("claim the packet", result["data"]["projection"]["work_items"][0]["next_action"])
        self.assertNotIn("approval", json.dumps(result).lower())
        self.assertNotIn("full suite", json.dumps(result).lower())

    def test_tracked_terminal_state_supersedes_stale_optional_local_state(self) -> None:
        projection = project_status(
            [{"work_id": "WRK-1", "public_status": "complete", "operational_state": "released", "diagnostics": []}]
        )
        item = projection["work_items"][0]
        self.assertEqual("none", item["next_action"])
        self.assertIn("tracked terminal status supersedes stale optional local state", item["diagnostics"])

    def test_projection_minimizes_review_data(self) -> None:
        projection = project_status(
            [
                {
                    "work_id": "WRK-1",
                    "public_status": "verifying",
                    "operational_state": "submitted",
                    "review_round_count": 1,
                    "latest_review_status": "changes-requested",
                    "open_finding_ids": ["R01-F001"],
                    "open_blocking_finding_ids": ["R01-F001"],
                }
            ]
        )
        encoded = json.dumps(projection)
        self.assertIn("R01-F001", encoded)
        self.assertNotIn("reviewer_label", encoded)
        self.assertNotIn("notes", encoded)
        self.assertNotIn("evidence", encoded)
        self.assertEqual("correct named findings and submit a strict descendant", projection["work_items"][0]["next_action"])


if __name__ == "__main__":
    unittest.main()
