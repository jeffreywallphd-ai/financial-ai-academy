#!/usr/bin/env python3
"""Deterministic tests for the bounded learner-language checker."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
TEST_TEMP_ROOT = HERE.parents[1] / ".local-codex" / "t"
SPEC = importlib.util.spec_from_file_location("learner_language_check", HERE / "check_learner_language.py")
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


def run(arguments: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(arguments, cwd=root, check=False, capture_output=True, text=True, encoding="utf-8")


class LearnerLanguageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.configuration = CHECK.load_configuration(HERE / "rules.json")

    def inspect(self, source: str, selected: set[int] | None = None):
        lines = source.splitlines()
        return CHECK.inspect_source(
            "apps/web/src/features/example/Example.tsx",
            source,
            selected or set(range(1, len(lines) + 1)),
            self.configuration,
        )

    def test_blocks_only_owned_primary_term_and_names_replacement(self) -> None:
        findings, errors, inspected = self.inspect("export const Page = () => <h1>Approved curriculum graph</h1>;")
        self.assertEqual([], errors)
        blocking = [item for item in findings if item.severity == "blocking"]
        self.assertEqual(1, len(blocking))
        self.assertEqual("primary.curriculum-graph", blocking[0].rule_id)
        self.assertEqual("Learning path", blocking[0].replacement)
        self.assertEqual(1, inspected)

    def test_technical_record_and_code_identifier_are_not_primary_copy(self) -> None:
        source = """const curriculumGraph = value;
return (
  <details>
    <summary>Technical record</summary>
    <dl><dt>Graph relationships</dt><dd>{curriculumGraph}</dd></dl>
  </details>
);"""
        findings, errors, _ = self.inspect(source)
        self.assertEqual([], errors)
        self.assertFalse(any(item.severity == "blocking" for item in findings))

    def test_advisory_language_never_becomes_blocking(self) -> None:
        source = (
            "<p>UTILIZE this deliberately long sentence containing many ordinary words so the contributor "
            "can decide whether it needs revision while the automated check remains advisory and does not "
            "interrupt useful product work when the meaning and interaction are still correct.</p>"
        )
        findings, errors, _ = self.inspect(source)
        self.assertEqual([], errors)
        self.assertTrue(any(item.severity == "advisory" for item in findings))
        self.assertFalse(any(item.severity == "blocking" for item in findings))

    def test_narrow_exception_suppresses_one_rule_but_not_another(self) -> None:
        source = """{/* learner-language: allow primary.curriculum-graph; reason=the lesson teaches graph structure; explained=the paragraph below */}
<p>Curriculum graph</p>
<button>Apply query</button>"""
        findings, errors, _ = self.inspect(source)
        self.assertEqual([], errors)
        self.assertNotIn("primary.curriculum-graph", {item.rule_id for item in findings})
        self.assertIn("primary.apply-query", {item.rule_id for item in findings})

    def test_malformed_or_stale_exception_fails_narrowly(self) -> None:
        malformed = """{/* learner-language: allow missing-rule; reason=needed here; explained=next paragraph */}
<p>Curriculum graph</p>"""
        _, errors, _ = self.inspect(malformed)
        self.assertEqual(1, len(errors))
        self.assertIn("unknown rule", errors[0])

        stale = """{/* learner-language: allow primary.curriculum-graph; reason=needed for this lesson; explained=next paragraph */}
<p>Learning path</p>"""
        _, errors, _ = self.inspect(stale)
        self.assertEqual(1, len(errors))
        self.assertIn("stale", errors[0])

    def test_path_scope_excludes_css_tests_and_generated_source(self) -> None:
        self.assertTrue(CHECK.owned_path("apps/web/src/features/example/Page.tsx", self.configuration))
        self.assertFalse(CHECK.owned_path("apps/web/src/features/example/page.css", self.configuration))
        self.assertFalse(CHECK.owned_path("apps/web/tests/component/example.test.tsx", self.configuration))
        self.assertFalse(CHECK.owned_path("apps/web/src/generated/api-client/Page.tsx", self.configuration))


class LearnerLanguageGitTests(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=TEST_TEMP_ROOT)
        self.root = Path(self.temporary.name)
        (self.root / "docs").mkdir()
        (self.root / "dev-tools/learner-language").mkdir(parents=True)
        (self.root / "apps/web/src/features/example").mkdir(parents=True)
        (self.root / "apps/web/src/styles").mkdir(parents=True)
        (self.root / "dev-tools/learner-language/rules.json").write_text(
            (HERE / "rules.json").read_text(encoding="utf-8"), encoding="utf-8"
        )
        for arguments in (
            ["git", "init", "-q"],
            ["git", "config", "user.name", "Learner Language Tests"],
            ["git", "config", "user.email", "tests@example.invalid"],
        ):
            completed = run(arguments, self.root)
            self.assertEqual(0, completed.returncode, completed.stderr)
        self.page = self.root / "apps/web/src/features/example/Page.tsx"
        self.page.write_text("export const Page = () => <h1>Learning path</h1>;\n", encoding="utf-8")
        (self.root / "apps/web/src/styles/page.css").write_text(".page { display: block; }\n", encoding="utf-8")
        self.commit("baseline")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def commit(self, message: str) -> None:
        added = run(["git", "add", "."], self.root)
        self.assertEqual(0, added.returncode, added.stderr)
        committed = run(["git", "commit", "-q", "-m", message], self.root)
        self.assertEqual(0, committed.returncode, committed.stderr)

    def cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return run(
            [sys.executable, str(HERE / "check_learner_language.py"), "--root", str(self.root), *arguments],
            self.root,
        )

    def test_changed_copy_blocks_and_json_omits_source_payload(self) -> None:
        self.page.write_text("export const Page = () => <h1>Topic slug</h1>;\n", encoding="utf-8")
        completed = self.cli("--json")
        self.assertEqual(1, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual("blocked", report["status"])
        self.assertEqual(1, report["blocking_count"])
        self.assertEqual("changed", report["selection"])
        self.assertNotIn("export const", completed.stdout)

    def test_base_ref_selects_committed_change(self) -> None:
        baseline = run(["git", "rev-parse", "HEAD"], self.root).stdout.strip()
        self.page.write_text("export const Page = () => <button>Apply query</button>;\n", encoding="utf-8")
        self.commit("changed copy")
        completed = self.cli("--base-ref", baseline, "--json")
        self.assertEqual(1, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual("base-ref", report["selection"])
        self.assertEqual("primary.apply-query", report["findings"][0]["rule_id"])

    def test_whitespace_and_css_only_changes_are_nonblocking_and_select_no_copy(self) -> None:
        self.page.write_text("export const Page = () =>   <h1>Learning path</h1>;\n", encoding="utf-8")
        (self.root / "apps/web/src/styles/page.css").write_text(".page { display: grid; }\n", encoding="utf-8")
        completed = self.cli("--json")
        self.assertEqual(0, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(0, report["blocking_count"])
        self.assertEqual(0, report["inspected_regions"])

    def test_untracked_owned_source_is_checked_but_untracked_css_is_not(self) -> None:
        new_page = self.root / "apps/web/src/features/example/NewPage.tsx"
        new_page.write_text("export const NewPage = () => <h2>Open exact lesson</h2>;\n", encoding="utf-8")
        (self.root / "apps/web/src/styles/new.css").write_text(".new { color: inherit; }\n", encoding="utf-8")
        completed = self.cli("--json")
        self.assertEqual(1, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(1, report["selected_files"])
        self.assertEqual("apps/web/src/features/example/NewPage.tsx", report["findings"][0]["path"])

    def test_full_scope_is_stable_and_advisories_do_not_fail(self) -> None:
        self.page.write_text("export const Page = () => <p>UTILIZE this learning path.</p>;\n", encoding="utf-8")
        self.commit("advisory copy")
        first = self.cli("--all", "--json")
        second = self.cli("--all", "--json")
        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        report = json.loads(first.stdout)
        self.assertEqual(0, report["blocking_count"])
        self.assertGreaterEqual(report["advisory_count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
