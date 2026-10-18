#!/usr/bin/env python3
"""Affected-check, receipt, failure, freshness, and anti-rigidity tests."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEST_TEMP_ROOT = ROOT / ".local-codex" / "t"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import verification as verification_module  # noqa: E402
from contracts import ControlError  # noqa: E402
from check_approved_lesson import (  # noqa: E402
    WebRuntime,
    child_environment,
    copy_tracked_candidate,
    execute as execute_web_check,
    execute_bound_check,
    file_digest,
    resolve_runtime,
)
from check_presentation_preferences import (  # noqa: E402
    execute as execute_presentation_check,
)
from check_assistance_preferences import (  # noqa: E402
    execute as execute_assistance_check,
)
from financial_academy_checks import catalog as repository_catalog  # noqa: E402
from store import StateStore, atomic_write, canonical_bytes  # noqa: E402
from verification import (  # noqa: E402
    BASE_REVISION_ARGUMENT,
    CURRENT_PYTHON_ARGUMENT,
    CheckCatalog,
    CheckDefinition,
    ReceiptStore,
    VerificationService,
    environment_fingerprint,
    execute_plan,
    control_plane_file_argument,
    materialize_arguments,
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

    def test_learner_language_selection_is_owned_and_does_not_escalate(self) -> None:
        plan = select_checks(
            repository_catalog(),
            "a" * 40,
            ["apps/web/src/features/lesson-reading/LessonBody.tsx"],
        )
        selected = {item["check_id"] for item in plan["selected"]}
        self.assertIn("learner-language:changed", selected)
        self.assertNotIn("agent:readiness", selected)

        checker = select_checks(
            repository_catalog(),
            "a" * 40,
            ["dev-tools/learner-language/rules.json"],
        )
        self.assertEqual(
            ["learner-language:unit", "learner-language:full"],
            [item["check_id"] for item in checker["selected"]],
        )

        tests = select_checks(
            repository_catalog(),
            "a" * 40,
            ["dev-tools/learner-language/test_learner_language.py"],
        )
        self.assertEqual(
            ["learner-language:unit"],
            [item["check_id"] for item in tests["selected"]],
        )

    def test_non_copy_paths_do_not_select_learner_language(self) -> None:
        paths = (
            "apps/web/src/styles/lesson.css",
            "apps/web/src/generated/api-client/Page.tsx",
            "apps/web/tests/component/lesson.test.tsx",
            "dev-tools/learner-language/README.md",
            "docs/design/style-guide.md",
            "dev-tools/control-plane/engine.py",
        )
        for path in paths:
            with self.subTest(path=path):
                plan = select_checks(repository_catalog(), "a" * 40, [path])
                selected = {item["check_id"] for item in plan["selected"]}
                self.assertNotIn("learner-language:changed", selected)
                self.assertNotIn("learner-language:unit", selected)
                self.assertNotIn("learner-language:full", selected)
                self.assertNotIn("agent:readiness", selected)

    def test_candidate_bound_language_check_inspects_clean_committed_diff(self) -> None:
        TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        cases = {
            "blocking": ("export const Page = () => <h1>Topic slug</h1>;\n", 1),
            "advisory": ("export const Page = () => <p>UTILIZE this learning path.</p>;\n", 0),
            "whitespace": ("export const Page = () =>   <h1>Learning path</h1>;\n", 0),
        }
        for name, (changed_source, expected_exit) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory(
                prefix="candidate-language-", dir=TEST_TEMP_ROOT
            ) as directory:
                root = Path(directory)
                (root / "docs").mkdir()
                tool = root / "dev-tools" / "learner-language"
                tool.mkdir(parents=True)
                shutil.copy2(ROOT / "dev-tools/learner-language/rules.json", tool / "rules.json")
                page = root / "apps" / "web" / "src" / "components" / "StatusPanel.tsx"
                page.parent.mkdir(parents=True)
                page.write_text(
                    "export const Page = () => <h1>Learning path</h1>;\n",
                    encoding="utf-8",
                )
                for arguments in (
                    ("init", "-q"),
                    ("config", "user.name", "Candidate Language Tests"),
                    ("config", "user.email", "tests@example.invalid"),
                    ("add", "."),
                    ("commit", "-q", "-m", "baseline"),
                ):
                    subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)
                base = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=root,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                page.write_text(changed_source, encoding="utf-8")
                subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
                subprocess.run(
                    ["git", "commit", "-q", "-m", name],
                    cwd=root,
                    check=True,
                    capture_output=True,
                )
                candidate = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=root,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                catalog = CheckCatalog(
                    "candidate-language-v1",
                    (
                        CheckDefinition(
                            "learner-language:changed",
                            (
                                sys.executable,
                                str(ROOT / "dev-tools/learner-language/check_learner_language.py"),
                                "--root",
                                ".",
                                "--base-ref",
                                BASE_REVISION_ARGUMENT,
                            ),
                            ("apps/web/src/components/*.tsx",),
                            "low",
                            1,
                        ),
                    ),
                )
                plan = select_checks(
                    catalog,
                    candidate,
                    ["apps/web/src/components/StatusPanel.tsx"],
                    base_revision=base,
                )
                attempt = execute_plan(root, catalog, plan)[0]
                self.assertEqual(expected_exit, attempt["exit_code"])
                self.assertEqual(base, attempt["argv"][-1])

    def test_bound_check_refuses_missing_or_nonexact_base_revision(self) -> None:
        catalog = CheckCatalog(
            "bound-argument-v1",
            (
                CheckDefinition(
                    "bound:fixture",
                    (sys.executable, "-c", "print('not reached')", BASE_REVISION_ARGUMENT),
                    ("docs/**",),
                    "low",
                    1,
                ),
            ),
        )
        for base_revision in (None, "HEAD", "abc123"):
            with self.subTest(base_revision=base_revision):
                plan = select_checks(
                    catalog,
                    "a" * 40,
                    ["docs/README.md"],
                    base_revision=base_revision,
                )
                with self.assertRaises(ControlError) as refused:
                    execute_plan(ROOT, catalog, plan)
                self.assertEqual(
                    "verification.base-revision-required",
                    refused.exception.code,
                )

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
            "apps/web/tests/browser/presentation-preferences/example.spec.ts": [
                "web:typecheck",
                "web:lint",
                "presentation:browser",
            ],
            "apps/web/src/features/presentation-preferences/PresentationPreferencesPage.tsx": [
                "learner-language:changed",
                "web:typecheck",
                "web:lint",
                "web:unit",
                "presentation:browser",
                "web:build",
            ],
            "apps/web/tests/browser/assistance-preferences/example.spec.ts": [
                "web:typecheck",
                "web:lint",
                "assistance:browser",
            ],
            "apps/web/src/features/assistance-preferences/AssistancePreferencesPage.tsx": [
                "learner-language:changed",
                "web:typecheck",
                "web:lint",
                "web:unit",
                "assistance:browser",
                "web:build",
            ],
            "apps/web/tests/browser/project-workspace/example.spec.ts": [
                "web:typecheck",
                "web:lint",
                "project:browser",
            ],
            "apps/web/src/features/project-workspace/ProjectCreatePage.tsx": [
                "learner-language:changed",
                "web:typecheck",
                "web:lint",
                "web:unit",
                "project:browser",
                "web:build",
            ],
            "apps/web/src/styles/project-workspace.css": [
                "web:typecheck",
                "web:lint",
                "web:unit",
                "project:browser",
                "web:build",
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
            "dev-tools/roadmap-review-site/src/app.ts": [
                "roadmap-review:qualification",
                "roadmap-review:typecheck",
                "roadmap-review:unit",
                "roadmap-review:browser",
            ],
            "dev-tools/roadmap-review-site/index.html": [
                "roadmap-review:qualification",
                "roadmap-review:server",
                "roadmap-review:browser",
            ],
            "dev-tools/roadmap-review-site/server.py": [
                "roadmap-review:qualification",
                "roadmap-review:server",
                "roadmap-review:browser",
            ],
            "dev-tools/roadmap-review-site/styles.css": [
                "roadmap-review:qualification",
                "roadmap-review:server",
                "roadmap-review:browser",
            ],
            "dev-tools/roadmap-review-site/tests/app.test.ts": [
                "roadmap-review:qualification",
                "roadmap-review:unit",
            ],
            "dev-tools/roadmap-review-site/test_server.py": [
                "roadmap-review:qualification",
                "roadmap-review:server",
            ],
            "dev-tools/roadmap-review-site/test_qualification.py": [
                "roadmap-review:qualification",
            ],
            "dev-tools/roadmap-review-site/tsconfig.json": [
                "roadmap-review:qualification",
                "roadmap-review:typecheck",
                "roadmap-review:unit",
                "roadmap-review:browser",
            ],
            "dev-tools/roadmap-review-site/README.md": [
                "documentation:integrity",
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
            "dev-tools/control-plane/review.py": [
                "control-plane:unit",
                "control-plane:review",
            ],
            "dev-tools/control-plane/test_review.py": [
                "control-plane:unit",
                "control-plane:review",
            ],
            "dev-tools/control-plane/check_approved_lesson.py": [
                "control-plane:unit",
                "control-plane:verification",
                "project:browser",
                "approved-lesson:live",
            ],
            "dev-tools/control-plane/check_presentation_preferences.py": [
                "control-plane:unit",
                "control-plane:verification",
                "presentation:browser",
            ],
            "dev-tools/control-plane/check_assistance_preferences.py": [
                "control-plane:unit",
                "control-plane:verification",
                "assistance:browser",
            ],
            "dev-tools/control-plane/financial_academy_checks.py": [
                "control-plane:unit",
                "control-plane:verification",
                "project:browser",
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

    def test_roadmap_server_check_uses_prepared_runtime_wrapper(self) -> None:
        definition = next(
            check
            for check in repository_catalog().checks
            if check.check_id == "roadmap-review:server"
        )
        self.assertEqual(CURRENT_PYTHON_ARGUMENT, definition.argv[0])
        self.assertEqual(
            control_plane_file_argument(
                "check_approved_lesson.py",
                file_digest(HERE / "check_approved_lesson.py"),
            ),
            definition.argv[1],
        )
        self.assertEqual("--self-sha256", definition.argv[2])
        self.assertEqual(file_digest(HERE / "check_approved_lesson.py"), definition.argv[3])
        self.assertEqual(("--root", ".", "--mode", "roadmap-server"), definition.argv[4:])

    def test_repository_catalog_runs_current_wrapper_against_candidate_root(self) -> None:
        definition = repository_catalog().by_id("project:browser")
        command = materialize_arguments(
            definition,
            select_checks(
                repository_catalog(),
                "a" * 40,
                ["apps/web/src/features/project-workspace/model.ts"],
            ),
        )

        self.assertEqual(sys.executable, command[0])
        self.assertEqual(
            (HERE / "check_approved_lesson.py").resolve(), Path(command[1]).resolve()
        )
        self.assertEqual("--self-sha256", command[2])
        self.assertEqual(file_digest(Path(command[1])), command[3])
        self.assertEqual(("--root", ".", "--mode", "project-browser"), command[4:])
        self.assertNotIn(str(HERE.resolve()), json.dumps(definition.contract()))

    def test_logical_control_file_refuses_path_escape(self) -> None:
        with self.assertRaises(ValueError):
            control_plane_file_argument(
                "../check_approved_lesson.py", "sha256:" + "a" * 64
            )

        malformed = CheckDefinition(
            "malformed:fixture",
            (
                CURRENT_PYTHON_ARGUMENT,
                "{control_plane_file:../escape.py@sha256:" + "a" * 64 + "}",
            ),
            ("docs/**",),
            "low",
            1,
        )
        with self.assertRaises(ControlError) as refused:
            materialize_arguments(malformed, {"base_revision": None})
        self.assertEqual("verification.control-file-invalid", refused.exception.code)

    def test_unclassified_path_refuses_instead_of_arbitrary_or_full_fallback(self) -> None:
        with self.assertRaises(ControlError) as refused:
            select_checks(repository_catalog(), "a" * 40, ["unknown/new-boundary.xyz"])
        self.assertEqual("verification.unclassified-impact", refused.exception.code)
        self.assertIn("do not execute an arbitrary command", refused.exception.remediation[0])


class ExecutionAndReceiptTests(unittest.TestCase):
    @staticmethod
    def bound_fixture(wrapper: Path) -> tuple[CheckCatalog, dict[str, Any]]:
        expected = file_digest(wrapper)
        catalog = CheckCatalog(
            "bound-control-file-v1",
            (
                CheckDefinition(
                    "docs:fixture",
                    (
                        CURRENT_PYTHON_ARGUMENT,
                        control_plane_file_argument(wrapper.name, expected),
                    ),
                    ("docs/**",),
                    "low",
                    1,
                ),
            ),
        )
        return catalog, select_checks(catalog, "a" * 40, ["docs/README.md"])

    def test_executor_authenticates_control_file_before_launch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="control-file-before-") as directory:
            root = Path(directory)
            wrapper = root / "wrapper.py"
            wrapper.write_text("# expected\n", encoding="utf-8")
            catalog, plan = self.bound_fixture(wrapper)
            wrapper.write_text("# changed\n", encoding="utf-8")
            with mock.patch.object(verification_module, "CONTROL_PLANE_ROOT", root):
                with mock.patch("verification.subprocess.run") as process:
                    with self.assertRaises(ControlError) as refused:
                        execute_plan(root, catalog, plan)
                    self.assertEqual(
                        "verification.control-file-digest-mismatch",
                        refused.exception.code,
                    )
                    process.assert_not_called()

    def test_executor_reauthenticates_after_completion_failure_and_timeout(self) -> None:
        for outcome in ("completed", "failed", "timeout"):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory(
                prefix=f"control-file-{outcome}-"
            ) as directory:
                root = Path(directory)
                wrapper = root / "wrapper.py"
                wrapper.write_text("# expected\n", encoding="utf-8")
                catalog, plan = self.bound_fixture(wrapper)

                def run(*arguments: object, **options: object) -> subprocess.CompletedProcess[bytes]:
                    del arguments, options
                    wrapper.write_text("# changed\n", encoding="utf-8")
                    if outcome == "timeout":
                        raise subprocess.TimeoutExpired(("wrapper",), 1)
                    return subprocess.CompletedProcess(
                        ("wrapper",), 0 if outcome == "completed" else 7, b"", b""
                    )

                with mock.patch.object(verification_module, "CONTROL_PLANE_ROOT", root):
                    with mock.patch("verification.subprocess.run", side_effect=run):
                        with self.assertRaises(ControlError) as refused:
                            execute_plan(root, catalog, plan)
                        self.assertEqual(
                            "verification.control-file-digest-mismatch",
                            refused.exception.code,
                        )

    def test_executor_records_authenticated_control_file_identity(self) -> None:
        with tempfile.TemporaryDirectory(prefix="control-file-receipt-") as directory:
            root = Path(directory)
            wrapper = root / "wrapper.py"
            wrapper.write_text("# expected\n", encoding="utf-8")
            catalog, plan = self.bound_fixture(wrapper)
            completed = subprocess.CompletedProcess(("wrapper",), 0, b"", b"")
            with mock.patch.object(verification_module, "CONTROL_PLANE_ROOT", root):
                with mock.patch("verification.subprocess.run", return_value=completed):
                    attempt = execute_plan(root, catalog, plan)[0]
            binding = attempt["control_file_bindings"][0]
            self.assertEqual(file_digest(wrapper), binding["expected_digest"])
            self.assertEqual(binding["expected_digest"], binding["observed_before"])
            self.assertEqual(binding["expected_digest"], binding["observed_after"])
            self.assertEqual(attempt["argv"][1], binding["resolved_path"])
            receipt = {"candidate": "a" * 40, "plan": plan, "attempts": [attempt]}
            self.assertEqual([], validate_receipt(receipt, catalog))
            binding["observed_after"] = "sha256:" + "0" * 64
            self.assertIn(
                "control-file binding evidence is invalid",
                validate_receipt(receipt, catalog),
            )

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
            second_path = store.append("WORK-1", {**base, "recorded_at": "2026-10-15T12:00:00Z"})
            first = store.load(first_path)
            second = store.load(second_path)
            self.assertIsNone(first["prior_receipt_digest"])
            self.assertEqual(first["receipt_digest"], second["prior_receipt_digest"])
            self.assertEqual(second_path, store.latest_path("WORK-1", "a" * 40))
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
    def mark_repository(root: Path) -> None:
        (root / "apps" / "web" / "tests" / "browser").mkdir(
            parents=True, exist_ok=True
        )
        (root / "apps" / "web" / "package.json").write_text(
            '{"name":"candidate"}\n', encoding="utf-8"
        )
        (root / "apps" / "web" / "tests" / "browser" / "playwright.config.ts").write_text(
            "export default {};\n", encoding="utf-8"
        )

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

    def test_project_browser_check_runs_only_the_project_suite(self) -> None:
        commands: list[tuple[str, ...]] = []

        def runner(command: tuple[str, ...], *, root: Path) -> None:
            del root
            commands.append(command)

        with tempfile.TemporaryDirectory(prefix="project-browser-check-") as directory:
            with mock.patch(
                "check_approved_lesson.resolve_runtime", return_value=self.runtime
            ):
                execute_web_check(
                    "project-browser",
                    root=Path(directory),
                    command_runner=runner,
                    version_reader=self.versions,
                )

        self.assertEqual(1, len(commands))
        self.assertIn("apps/web/tests/browser/project-workspace", commands[0])
        self.assertNotIn("apps/web/tests/browser/lesson-reading", commands[0])

    def test_presentation_browser_check_runs_only_its_focused_suite(self) -> None:
        commands: list[tuple[str, ...]] = []

        def runner(command: tuple[str, ...], *, root: Path) -> None:
            del root
            commands.append(command)

        with tempfile.TemporaryDirectory(prefix="presentation-browser-check-") as directory:
            with mock.patch(
                "check_presentation_preferences.resolve_runtime",
                return_value=self.runtime,
            ):
                execute_presentation_check(
                    "presentation-browser",
                    root=Path(directory),
                    command_runner=runner,
                    version_reader=self.versions,
                )

        self.assertEqual(1, len(commands))
        self.assertIn(
            "apps/web/tests/browser/presentation-preferences",
            commands[0],
        )
        self.assertNotIn("apps/web/tests/browser/lesson-reading", commands[0])

    def test_assistance_browser_check_runs_only_its_focused_suite(self) -> None:
        commands: list[tuple[str, ...]] = []

        def runner(command: tuple[str, ...], *, root: Path) -> None:
            del root
            commands.append(command)

        with tempfile.TemporaryDirectory(prefix="assistance-browser-check-") as directory:
            with mock.patch(
                "check_assistance_preferences.resolve_runtime",
                return_value=self.runtime,
            ):
                execute_assistance_check(
                    "assistance-browser",
                    root=Path(directory),
                    command_runner=runner,
                    version_reader=self.versions,
                )

        self.assertEqual(1, len(commands))
        self.assertIn(
            "apps/web/tests/browser/assistance-preferences",
            commands[0],
        )
        self.assertNotIn("apps/web/tests/browser/lesson-reading", commands[0])

    def test_bound_current_wrapper_runs_new_mode_against_distinct_candidate_root(self) -> None:
        commands: list[tuple[tuple[str, ...], Path]] = []
        with tempfile.TemporaryDirectory(prefix="two-root-candidate-") as directory:
            candidate = Path(directory)
            self.mark_repository(candidate)
            obsolete = candidate / "dev-tools" / "control-plane"
            obsolete.mkdir(parents=True)
            obsolete.joinpath("check_approved_lesson.py").write_text(
                "# historical wrapper without project-browser\n", encoding="utf-8"
            )

            def runner(command: tuple[str, ...], *, root: Path) -> None:
                commands.append((command, root))

            with mock.patch(
                "check_approved_lesson.resolve_runtime", return_value=self.runtime
            ):
                execute_bound_check(
                    "project-browser",
                    root=candidate,
                    expected_wrapper_digest=file_digest(
                        HERE / "check_approved_lesson.py"
                    ),
                    command_runner=runner,
                    version_reader=self.versions,
                )

        self.assertEqual(1, len(commands))
        self.assertEqual(candidate.resolve(), commands[0][1])
        self.assertIn("apps/web/tests/browser/project-workspace", commands[0][0])

    def test_bound_wrapper_refuses_invalid_root_before_runtime_resolution(self) -> None:
        with tempfile.TemporaryDirectory(prefix="invalid-candidate-") as directory:
            with mock.patch("check_approved_lesson.resolve_runtime") as resolver:
                with self.assertRaisesRegex(RuntimeError, "not a compatible"):
                    execute_bound_check(
                        "project-browser",
                        root=Path(directory),
                        expected_wrapper_digest=file_digest(
                            HERE / "check_approved_lesson.py"
                        ),
                    )
                resolver.assert_not_called()

    def test_bound_wrapper_refuses_bytes_changed_during_execution(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mutating-wrapper-") as directory:
            root = Path(directory)
            candidate = root / "candidate"
            wrapper = root / "check_approved_lesson.py"
            candidate.mkdir()
            self.mark_repository(candidate)
            wrapper.write_text("# trusted bytes\n", encoding="utf-8")
            expected = file_digest(wrapper)

            def mutate(mode: str, *, root: Path, **options: object) -> None:
                del mode, root, options
                wrapper.write_text("# changed bytes\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "digest does not match"):
                execute_bound_check(
                    "project-browser",
                    root=candidate,
                    expected_wrapper_digest=expected,
                    wrapper=wrapper,
                    executor=mutate,
                )

    def test_explicit_runtime_is_available_to_child_processes(self) -> None:
        runtime = WebRuntime(
            node=r"C:\prepared-node\node.exe",
            npm=(r"C:\prepared-node\node.exe", r"C:\prepared-npm\npm-cli.js"),
            python=r"C:\prepared-python\python.exe",
        )
        source = {"Path": r"C:\Windows\System32", "UNCHANGED": "true"}
        child = child_environment(runtime, source)
        self.assertEqual(source, {"Path": r"C:\Windows\System32", "UNCHANGED": "true"})
        self.assertEqual(r"C:\prepared-python\python.exe", child["PYTHON"])
        self.assertTrue(child["Path"].startswith(r"C:\prepared-node" + os.pathsep))
        self.assertEqual("true", child["UNCHANGED"])

    def test_runtime_prefers_explicit_python_over_prepared_environment(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prepared-python-") as directory:
            root = Path(directory)
            prepared = root / "backend" / ".venv" / (
                "Scripts/python.exe" if os.name == "nt" else "bin/python"
            )
            prepared.parent.mkdir(parents=True)
            prepared.write_bytes(b"prepared")
            explicit = root / "explicit-python"
            explicit.write_bytes(b"explicit")
            runtime = resolve_runtime(
                {
                    "FINANCIAL_AI_ACADEMY_NODE_EXECUTABLE": "node",
                    "FINANCIAL_AI_ACADEMY_NPM_CLI": "npm-cli.js",
                    "FINANCIAL_AI_ACADEMY_PYTHON_EXECUTABLE": str(explicit),
                },
                root=root,
            )
            self.assertEqual(os.path.abspath(explicit), runtime.python)

    def test_runtime_prefers_prepared_backend_python_then_falls_back(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prepared-python-") as directory:
            root = Path(directory)
            prepared = root / "backend" / ".venv" / (
                "Scripts/python.exe" if os.name == "nt" else "bin/python"
            )
            prepared.parent.mkdir(parents=True)
            prepared.write_bytes(b"prepared")
            environment = {
                "FINANCIAL_AI_ACADEMY_NODE_EXECUTABLE": "node",
                "FINANCIAL_AI_ACADEMY_NPM_CLI": "npm-cli.js",
            }
            self.assertEqual(
                os.path.abspath(prepared),
                resolve_runtime(environment, root=root).python,
            )
            prepared.unlink()
            self.assertEqual(
                sys.executable,
                resolve_runtime(environment, root=root).python,
            )

    @unittest.skipIf(os.name == "nt", "POSIX virtual environments use symlinks")
    def test_posix_venv_symlink_remains_the_exported_and_invoked_path(self) -> None:
        commands: list[tuple[str, ...]] = []

        def runner(command: tuple[str, ...], *, root: Path) -> None:
            commands.append(command)
            if len(commands) == 1:
                dist = root / "apps" / "web" / "dist"
                dist.mkdir(parents=True)
                (dist / "index.html").write_text("isolated", encoding="utf-8")

        with tempfile.TemporaryDirectory(prefix="posix-venv-python-") as directory:
            root = Path(directory)
            base = root / "base-python"
            base.write_bytes(b"base")
            prepared = root / "backend" / ".venv" / "bin" / "python"
            prepared.parent.mkdir(parents=True)
            prepared.symlink_to(base)
            runtime = resolve_runtime(
                {
                    "FINANCIAL_AI_ACADEMY_NODE_EXECUTABLE": "node",
                    "FINANCIAL_AI_ACADEMY_NPM_CLI": "npm-cli.js",
                },
                root=root,
            )
            expected = os.path.abspath(prepared)
            self.assertTrue(prepared.is_symlink())
            self.assertEqual(expected, runtime.python)
            self.assertEqual(expected, child_environment(runtime, {})["PYTHON"])
            with mock.patch(
                "check_approved_lesson.resolve_runtime", return_value=runtime
            ):
                execute_web_check(
                    "live",
                    root=root,
                    command_runner=runner,
                    version_reader=self.versions,
                    snapshot_preparer=self.prepare_snapshot,
                )
        self.assertEqual(expected, commands[1][0])

    def test_live_check_invokes_runner_with_resolved_python(self) -> None:
        commands: list[tuple[str, ...]] = []

        def runner(command: tuple[str, ...], *, root: Path) -> None:
            commands.append(command)
            if len(commands) == 1:
                dist = root / "apps" / "web" / "dist"
                dist.mkdir(parents=True)
                (dist / "index.html").write_text("isolated", encoding="utf-8")

        runtime = WebRuntime(
            node="node",
            npm=("npm",),
            python="prepared-python",
        )
        with tempfile.TemporaryDirectory(prefix="web-check-python-") as directory:
            with mock.patch(
                "check_approved_lesson.resolve_runtime", return_value=runtime
            ):
                execute_web_check(
                    "live",
                    root=Path(directory),
                    command_runner=runner,
                    version_reader=self.versions,
                    snapshot_preparer=self.prepare_snapshot,
                )
        self.assertEqual(2, len(commands))
        self.assertEqual("prepared-python", commands[1][0])

    def test_candidate_snapshot_exports_commit_bytes_and_omits_tracked_build(self) -> None:
        with tempfile.TemporaryDirectory(prefix="candidate-export-") as directory:
            source = Path(directory) / "source"
            target = Path(directory) / "target"
            source.mkdir()
            subprocess.run(["git", "init", "--quiet"], cwd=source, check=True)
            subprocess.run(
                ["git", "config", "user.email", "snapshot@example.invalid"],
                cwd=source,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Snapshot Test"],
                cwd=source,
                check=True,
            )
            tracked = source / "candidate.txt"
            tracked.write_text("committed", encoding="utf-8")
            dist = source / "apps" / "web" / "dist"
            dist.mkdir(parents=True)
            dist.joinpath("index.html").write_text("tracked-build", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=source, check=True)
            subprocess.run(
                ["git", "commit", "--quiet", "-m", "fixture"],
                cwd=source,
                check=True,
            )
            tracked.write_text("mutable-worktree", encoding="utf-8")
            target.mkdir()
            copy_tracked_candidate(source, target)
            self.assertEqual(
                "committed", target.joinpath("candidate.txt").read_text(encoding="utf-8")
            )
            self.assertFalse(target.joinpath("apps", "web", "dist").exists())

    def test_roadmap_check_uses_isolated_dynamic_port(self) -> None:
        with tempfile.TemporaryDirectory(prefix="roadmap-check-") as directory:
            root = Path(directory)
            config = (
                root
                / "apps"
                / "web"
                / "tests"
                / "browser"
                / "roadmap-review.config.ts"
            )
            config.parent.mkdir(parents=True)
            original = "origin 8765; command 8765; readiness 8765"
            config.write_text(original, encoding="utf-8")

            def prepare_snapshot(source: Path, target: Path) -> None:
                target_config = target / config.relative_to(source)
                target_config.parent.mkdir(parents=True)
                target_config.write_text(
                    config.read_text(encoding="utf-8"), encoding="utf-8"
                )

            def runner(command: tuple[str, ...], *, root: Path) -> None:
                self.assertIn(
                    "apps/web/tests/browser/roadmap-review.config.ts", command
                )
                isolated = root / config.relative_to(Path(directory))
                rendered = isolated.read_text(encoding="utf-8")
                self.assertNotIn("8765", rendered)
                self.assertEqual(3, rendered.count("45999"))

            with mock.patch(
                "check_approved_lesson.resolve_runtime", return_value=self.runtime
            ):
                execute_web_check(
                    "roadmap",
                    root=root,
                    command_runner=runner,
                    version_reader=self.versions,
                    snapshot_preparer=prepare_snapshot,
                    port_selector=lambda: 45999,
                )
            self.assertEqual(original, config.read_text(encoding="utf-8"))

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
            "submission": {
                "base_revision": "0" * 40,
                "candidate": "a" * 40,
                "changed_paths": ["docs/README.md"],
            },
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
