#!/usr/bin/env python3
"""Affected-check, receipt, failure, freshness, and anti-rigidity tests."""

from __future__ import annotations

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
from financial_academy_checks import catalog as repository_catalog  # noqa: E402
from store import StateStore, atomic_write, canonical_bytes  # noqa: E402
from verification import (  # noqa: E402
    CheckCatalog,
    CheckDefinition,
    ReceiptStore,
    VerificationService,
    environment_fingerprint,
    execute_plan,
    select_checks,
    validate_receipt,
)


class JsonProjection:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = root / "work.json"
        if not self.path.exists():
            self.path.write_text('{"status":"verifying"}\n', encoding="utf-8")

    @property
    def relative_path(self) -> str:
        return "work.json"

    def content_sha256(self) -> str:
        import hashlib

        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def matches(self, updates: dict[str, Any]) -> bool:
        current = json.loads(self.path.read_text(encoding="utf-8"))
        return all(current.get(key) == value for key, value in updates.items())

    def apply(self, updates: dict[str, Any], expected_sha256: str) -> None:
        current = json.loads(self.path.read_text(encoding="utf-8"))
        current.update(updates)
        self.path.write_bytes(canonical_bytes(current))


class FixtureProject:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.public = JsonProjection(root)

    def projection(self, work_id: str) -> JsonProjection:
        return self.public

    @staticmethod
    def require_delivery_authority(work_id: str) -> dict[str, Any]:
        return {"approval_stages_checked": ["fixture"], "allowed_paths": ["docs"], "canonical_inputs": []}


class FixtureCandidate:
    def __init__(self) -> None:
        self.stable = True

    @staticmethod
    def current_identity() -> dict[str, str]:
        return {"repository": "fixture", "branch": "codex/fixture", "head": "a" * 40}

    def stable_identity(self, candidate: str) -> dict[str, str]:
        if not self.stable:
            raise ControlError("git.dirty-worktree", "fixture drift", {}, ["restore"])
        return {**self.current_identity(), "candidate": candidate}

    @staticmethod
    def is_strict_descendant(ancestor: str, descendant: str) -> bool:
        return ancestor != descendant

    @staticmethod
    def submission(**kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class DriftingCandidate(FixtureCandidate):
    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    def stable_identity(self, candidate: str) -> dict[str, str]:
        self.calls += 1
        if self.calls > 1:
            raise ControlError("git.dirty-worktree", "fixture drift", {}, ["restore"])
        return super().stable_identity(candidate)


def fixture_catalog(*, failing: bool = False, timeout: bool = False) -> CheckCatalog:
    if timeout:
        argv = (sys.executable, "-c", "import time; time.sleep(2)")
        timeout_seconds = 1
    elif failing:
        argv = (sys.executable, "-c", "import sys; print(bytes.fromhex('73656e736974697665206f7574707574').decode()); sys.exit(7)")
        timeout_seconds = 30
    else:
        argv = (sys.executable, "-c", "print('synthetic output')")
        timeout_seconds = 30
    return CheckCatalog(
        "fixture-v1",
        (
            CheckDefinition("docs:fixture", argv, ("docs/**",), "low", 10, timeout_seconds=timeout_seconds),
            CheckDefinition("full:fixture", (sys.executable, "-c", "print('full')"), ("shared/**",), "high", 90),
        ),
    )


class SelectionTests(unittest.TestCase):
    def test_selection_is_deterministic_and_ordered(self) -> None:
        catalog = repository_catalog()
        paths = ["docs/planning/register.md", "dev-tools/control-plane/verification.py"]
        first = select_checks(catalog, "a" * 40, paths)
        second = select_checks(catalog, "a" * 40, list(reversed(paths)))
        self.assertEqual(first, second)
        self.assertEqual(["control-plane:unit", "planning:tools", "planning:integrity", "documentation:integrity"], [item["check_id"] for item in first["selected"]])

    def test_docs_and_control_changes_do_not_select_full_readiness(self) -> None:
        catalog = repository_catalog()
        docs = select_checks(catalog, "a" * 40, ["docs/product/example.md"])
        control = select_checks(catalog, "a" * 40, ["dev-tools/control-plane/engine.py"])
        self.assertEqual(["documentation:integrity"], [item["check_id"] for item in docs["selected"]])
        self.assertEqual(["control-plane:unit"], [item["check_id"] for item in control["selected"]])
        for plan in (docs, control):
            self.assertNotIn("agent:readiness", [item["check_id"] for item in plan["selected"]])
            self.assertIn("agent:readiness", [item["check_id"] for item in plan["deferred"]])

    def test_shared_agent_change_has_concrete_full_readiness_reason(self) -> None:
        plan = select_checks(repository_catalog(), "a" * 40, ["dev-tools/agent/check_ready.py"])
        selected = {item["check_id"]: item for item in plan["selected"]}
        self.assertEqual("high", plan["risk"])
        self.assertEqual(["dev-tools/agent/check_ready.py"], selected["agent:readiness"]["matched_paths"])
        self.assertEqual("affected path matched tracked rule", selected["agent:readiness"]["reason"])

    def test_unclassified_path_refuses_instead_of_arbitrary_or_full_fallback(self) -> None:
        with self.assertRaises(ControlError) as refused:
            select_checks(repository_catalog(), "a" * 40, ["unknown/new-boundary.xyz"])
        self.assertEqual("verification.unclassified-impact", refused.exception.code)
        self.assertIn("do not execute an arbitrary command", refused.exception.remediation[0])


class ExecutionAndReceiptTests(unittest.TestCase):
    def test_executor_records_digests_not_raw_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="verification-exec-") as directory:
            catalog = fixture_catalog(failing=True)
            plan = select_checks(catalog, "a" * 40, ["docs/README.md"])
            attempts = execute_plan(Path(directory), catalog, plan)
            self.assertEqual(7, attempts[0]["exit_code"])
            rendered = json.dumps(attempts)
            self.assertNotIn("sensitive output", rendered)
            self.assertGreater(attempts[0]["stdout_bytes"], 0)

    def test_timeout_is_preserved_as_nonqualifying_attempt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="verification-timeout-") as directory:
            catalog = fixture_catalog(timeout=True)
            plan = select_checks(catalog, "a" * 40, ["docs/README.md"])
            attempts = execute_plan(Path(directory), catalog, plan)
            self.assertTrue(attempts[0]["timed_out"])
            receipt = {"candidate": "a" * 40, "plan": plan, "attempts": attempts}
            self.assertIn("one or more selected checks failed or timed out", validate_receipt(receipt, catalog))

    def test_append_only_receipts_chain_and_validate_digest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="verification-receipt-") as directory:
            root = Path(directory)
            store = ReceiptStore(root)
            catalog = fixture_catalog()
            plan = select_checks(catalog, "a" * 40, ["docs/README.md"])
            base = {
                "schema_version": "verification-receipt-v1",
                "candidate": "a" * 40,
                "plan": plan,
                "attempts": [{"check_id": "docs:fixture", "exit_code": 0, "timed_out": False}],
                "recorded_at": "2026-10-15T12:00:00Z",
            }
            first_path = store.append("WORK-1", base)
            second_path = store.append("WORK-1", {**base, "recorded_at": "2026-10-15T12:00:01Z"})
            first = store.load(first_path)
            second = store.load(second_path)
            self.assertIsNone(first["prior_receipt_digest"])
            self.assertEqual(first["receipt_digest"], second["prior_receipt_digest"])
            self.assertEqual([], validate_receipt(second, catalog, current_candidate="a" * 40))
            second["candidate"] = "b" * 40
            self.assertIn("receipt candidate does not match plan", validate_receipt(second, catalog))

    def test_environment_fingerprint_disables_optimistic_reuse(self) -> None:
        fingerprint = environment_fingerprint()
        self.assertFalse(fingerprint["reuse_eligible"])
        self.assertIn("not authenticated", fingerprint["reuse_reason"])


class VerificationServiceTests(unittest.TestCase):
    def prepare(self, root: Path, catalog: CheckCatalog, candidate: FixtureCandidate | None = None) -> VerificationService:
        project = FixtureProject(root)
        state = StateStore(root, project.projection)
        envelope = state.empty()
        envelope["revision"] = 2
        envelope["work_items"]["WORK-1"] = {
            "work_id": "WORK-1",
            "revision": 2,
            "state": "submitted",
            "claim": {"base_revision": "0" * 40},
            "submission": {"candidate": "a" * 40, "changed_paths": ["docs/README.md"]},
            "history": [],
        }
        atomic_write(state.state_path, canonical_bytes(envelope))
        return VerificationService(root, project, state, catalog, candidate or FixtureCandidate())

    def test_fresh_success_and_failure_both_append_truthful_receipts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="verification-service-") as directory:
            root = Path(directory)
            success_service = self.prepare(root, fixture_catalog())
            plan_result = success_service.plan("WORK-1")
            self.assertEqual(["docs:fixture"], [item["check_id"] for item in plan_result["data"]["plan"]["selected"]])
            success_result = success_service.verify("WORK-1")
            self.assertTrue(success_result["data"]["qualifying"])
            failed_service = VerificationService(root, success_service.project, success_service.state, fixture_catalog(failing=True), FixtureCandidate())
            failed_result = failed_service.verify("WORK-1")
            self.assertEqual("not-qualified", failed_result["outcome"])
            self.assertFalse(failed_result["data"]["qualifying"])
            receipts = list((root / ".local-codex/control-plane/receipts/WORK-1" / ("a" * 40)).glob("*.json"))
            self.assertEqual(2, len(receipts))

    def test_candidate_drift_during_run_is_retained_as_nonqualifying_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="verification-drift-") as directory:
            root = Path(directory)
            service = self.prepare(root, fixture_catalog(), DriftingCandidate())
            result = service.verify("WORK-1")
            self.assertEqual("not-qualified", result["outcome"])
            self.assertIn("git.dirty-worktree", result["data"]["errors"])
            receipt = json.loads((root / result["data"]["receipt_path"]).read_bytes())
            self.assertFalse(receipt["candidate_stability"]["post_run_stable"])
            self.assertEqual("control-provenance-v1", receipt["provenance"]["schema_version"])
            self.assertRegex(receipt["provenance"]["capability_digest"], r"^sha256:[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
