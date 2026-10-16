#!/usr/bin/env python3
"""Affected-check, receipt, failure, freshness, and anti-rigidity tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from contracts import ControlError  # noqa: E402
from check_approved_lesson import WebRuntime, execute as execute_web_check  # noqa: E402
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
        self.assertEqual(
            [
                "control-plane:unit",
                "control-plane:verification",
                "planning:tools",
                "planning:integrity",
                "documentation:integrity",
            ],
            [item["check_id"] for item in first["selected"]],
        )

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

    def test_repository_path_classes_select_precise_behavior_checks(self) -> None:
        cases = {
            "apps/web/index.html": ["web:build"],
            "apps/web/tsconfig.json": ["web:typecheck", "web:build"],
            "apps/web/scripts/generate-api-client.mjs": [
                "web:unit",
                "web:generated-client",
            ],
            "apps/web/src/generated/api-client/index.ts": [
                "web:typecheck",
                "web:lint",
                "web:unit",
                "web:build",
                "web:generated-client",
            ],
            "contracts/api/openapi.json": [
                "architecture:integrity",
                "web:generated-client",
            ],
            "apps/web/tests/browser/lesson-reading/example.spec.ts": [
                "web:typecheck",
                "web:lint",
                "web:browser",
            ],
            "apps/web/tests/browser/approved-lesson/example.e2e.ts": [
                "web:typecheck",
                "web:lint",
                "approved-lesson:live",
            ],
            "apps/web/tests/browser/roadmap-review/example.spec.ts": [
                "roadmap-review:qualification",
                "web:typecheck",
                "web:lint",
                "roadmap-review:browser",
            ],
            "apps/web/tests/browser/roadmap-review.config.ts": [
                "roadmap-review:qualification",
                "web:typecheck",
                "web:lint",
                "roadmap-review:browser",
            ],
            "apps/web/README.md": ["documentation:integrity"],
            "deployments/local/README.md": ["documentation:integrity"],
            "deployments/local/serve.py": [
                "local:architecture",
                "approved-lesson:live",
            ],
            "deployments/local/dev.mjs": [
                "local:architecture",
                "local:node-syntax",
            ],
            "deployments/local/compose.qualify.yml": ["local:architecture"],
            "tests/e2e/approved-lesson/run.py": [
                "local:architecture",
                "approved-lesson:live",
            ],
            "dev-tools/control-plane/check_approved_lesson.py": [
                "control-plane:unit",
                "control-plane:verification",
                "approved-lesson:live",
            ],
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                plan = select_checks(repository_catalog(), "a" * 40, [path])
                self.assertEqual(expected, [item["check_id"] for item in plan["selected"]])
                self.assertNotIn(
                    "agent:readiness",
                    [item["check_id"] for item in plan["selected"]],
                )

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


class RepositoryWebCheckTests(unittest.TestCase):
    runtime = WebRuntime(node="node", npm=("npm",))

    @staticmethod
    def versions(command: tuple[str, ...], *, root: Path) -> str:
        del root
        return "v24.14.0" if command[0] == "node" else "10.8.2"

    @staticmethod
    def prepare_snapshot(source: Path, target: Path) -> None:
        del source
        (target / "apps" / "web").mkdir(parents=True)

    def run_isolated_live(self, root: Path, *, fail: bool = False) -> int:
        calls = 0

        def runner(command: tuple[str, ...], *, root: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 1:
                dist = root / "apps" / "web" / "dist"
                dist.mkdir(parents=True)
                (dist / "index.html").write_text("isolated-index", encoding="utf-8")
            elif fail:
                raise RuntimeError("synthetic live failure")

        with mock.patch(
            "check_approved_lesson.resolve_runtime", return_value=self.runtime
        ):
            if fail:
                with self.assertRaisesRegex(RuntimeError, "synthetic live failure"):
                    execute_web_check(
                        "live",
                        root=root,
                        command_runner=runner,
                        version_reader=self.versions,
                        snapshot_preparer=self.prepare_snapshot,
                    )
            else:
                execute_web_check(
                    "live",
                    root=root,
                    command_runner=runner,
                    version_reader=self.versions,
                    snapshot_preparer=self.prepare_snapshot,
                )
        return calls

    def test_build_check_never_mutates_worktree_build(self) -> None:
        with tempfile.TemporaryDirectory(prefix="web-check-build-") as directory:
            root = Path(directory)
            dist = root / "apps" / "web" / "dist"
            dist.mkdir(parents=True)
            (dist / "index.html").write_text("worktree-index", encoding="utf-8")

            def runner(command: tuple[str, ...], *, root: Path) -> None:
                self.assertIn("build", command)
                isolated = root / "apps" / "web" / "dist"
                isolated.mkdir(parents=True)
                (isolated / "index.html").write_text(
                    "isolated-index", encoding="utf-8"
                )

            with mock.patch(
                "check_approved_lesson.resolve_runtime", return_value=self.runtime
            ):
                execute_web_check(
                    "build",
                    root=root,
                    command_runner=runner,
                    version_reader=self.versions,
                    snapshot_preparer=self.prepare_snapshot,
                )
            self.assertEqual(
                "worktree-index", dist.joinpath("index.html").read_text(encoding="utf-8")
            )

    def test_live_check_never_mutates_existing_or_missing_worktree_build(self) -> None:
        for build_exists in (False, True):
            for fail in (False, True):
                with self.subTest(build_exists=build_exists, fail=fail):
                    with tempfile.TemporaryDirectory(prefix="web-check-isolated-") as directory:
                        root = Path(directory)
                        dist = root / "apps" / "web" / "dist"
                        if build_exists:
                            dist.mkdir(parents=True)
                            (dist / "index.html").write_text("old-index", encoding="utf-8")
                            (dist / "old.js").write_text("old-asset", encoding="utf-8")
                        calls = self.run_isolated_live(root, fail=fail)
                        self.assertEqual(2, calls)
                        if build_exists:
                            self.assertEqual("old-index", (dist / "index.html").read_text(encoding="utf-8"))
                            self.assertEqual("old-asset", (dist / "old.js").read_text(encoding="utf-8"))
                        else:
                            self.assertFalse(dist.exists())

    def test_live_check_leaves_unexpected_and_concurrent_build_paths_untouched(self) -> None:
        with tempfile.TemporaryDirectory(prefix="web-check-unexpected-") as directory:
            root = Path(directory)
            dist = root / "apps" / "web" / "dist"
            dist.parent.mkdir(parents=True)
            dist.write_text("unexpected-file", encoding="utf-8")
            self.run_isolated_live(root)
            self.assertTrue(dist.is_file())
            self.assertEqual("unexpected-file", dist.read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory(prefix="web-check-concurrent-") as directory:
            root = Path(directory)
            dist = root / "apps" / "web" / "dist"
            dist.mkdir(parents=True)
            (dist / "before.js").write_text("before", encoding="utf-8")

            def concurrent_snapshot(source: Path, target: Path) -> None:
                self.prepare_snapshot(source, target)
                (dist / "during.js").write_text("during", encoding="utf-8")

            with mock.patch(
                "check_approved_lesson.resolve_runtime", return_value=self.runtime
            ):
                def runner(command: tuple[str, ...], *, root: Path) -> None:
                    if "build" in command:
                        isolated = root / "apps" / "web" / "dist"
                        isolated.mkdir(parents=True)
                        (isolated / "index.html").write_text("isolated", encoding="utf-8")

                execute_web_check(
                    "live",
                    root=root,
                    command_runner=runner,
                    version_reader=self.versions,
                    snapshot_preparer=concurrent_snapshot,
                )
            self.assertEqual("before", (dist / "before.js").read_text(encoding="utf-8"))
            self.assertEqual("during", (dist / "during.js").read_text(encoding="utf-8"))

    def test_live_check_does_not_follow_worktree_build_symlink(self) -> None:
        with tempfile.TemporaryDirectory(prefix="web-check-symlink-") as directory:
            root = Path(directory)
            target = root / "outside-build"
            target.mkdir()
            (target / "sentinel.txt").write_text("outside", encoding="utf-8")
            dist = root / "apps" / "web" / "dist"
            dist.parent.mkdir(parents=True)
            try:
                dist.symlink_to(target, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"directory symlinks are unavailable: {error}")
            self.run_isolated_live(root)
            self.assertTrue(dist.is_symlink())
            self.assertEqual("outside", (target / "sentinel.txt").read_text(encoding="utf-8"))

    @unittest.skipUnless(os.name == "nt", "directory junctions are Windows-specific")
    def test_live_check_does_not_follow_worktree_build_junction(self) -> None:
        with tempfile.TemporaryDirectory(prefix="web-check-junction-root-") as root_dir:
            with tempfile.TemporaryDirectory(prefix="web-check-junction-target-") as target_dir:
                root = Path(root_dir)
                target = Path(target_dir)
                (target / "sentinel.txt").write_text("outside", encoding="utf-8")
                dist = root / "apps" / "web" / "dist"
                dist.parent.mkdir(parents=True)
                completed = subprocess.run(
                    ["cmd.exe", "/d", "/c", "mklink", "/J", str(dist), str(target)],
                    check=False,
                    capture_output=True,
                )
                if completed.returncode != 0:
                    self.skipTest("directory junctions are unavailable")
                self.run_isolated_live(root)
                self.assertTrue(os.path.isjunction(dist))
                self.assertEqual(
                    "outside",
                    (target / "sentinel.txt").read_text(encoding="utf-8"),
                )


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
