"""Dependency-free structural and anti-rigidity qualification for the review site."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "dev-tools" / "roadmap-review-site"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class RoadmapReviewQualificationTests(unittest.TestCase):
    def test_site_has_no_committed_roadmap_copy_or_generated_pages(self) -> None:
        committed = {
            path.relative_to(SITE).as_posix()
            for path in SITE.rglob("*")
            if path.is_file() and path.suffix.lower() in {".json", ".yaml", ".yml"}
        }
        self.assertEqual(committed, {"tsconfig.json"})
        index = read("dev-tools/roadmap-review-site/index.html")
        self.assertNotIn("CAP-000", index)
        self.assertNotIn("SLI-000", index)
        self.assertNotIn("WRK-000", index)

    def test_generated_and_browser_outputs_are_ignored(self) -> None:
        ignored = read(".gitignore")
        self.assertIn("/.local-codex/", ignored)
        self.assertIn("/artifacts/", ignored)
        server = read("dev-tools/roadmap-review-site/server.py")
        self.assertIn('.local-codex" / "roadmap-review-site', server)
        self.assertNotIn("write_text(", server)

    def test_host_is_fixed_read_only_and_path_confined(self) -> None:
        server = read("dev-tools/roadmap-review-site/server.py")
        self.assertIn('default="127.0.0.1"', server)
        self.assertIn("address.is_loopback", server)
        self.assertIn('do_POST = _deny_mutation', server)
        self.assertIn('do_DELETE = _deny_mutation', server)
        self.assertIn('"/api/roadmap"', server)
        self.assertNotIn("SimpleHTTPRequestHandler", server)
        self.assertNotRegex(server, r"subprocess\.(?:run|Popen)\([^\n]+shell\s*=\s*True")

    def test_accessibility_and_responsive_contract_is_source_visible(self) -> None:
        index = read("dev-tools/roadmap-review-site/index.html")
        for token in ('class="skip-link"', "<header", "<main", "<footer", 'aria-busy="true"'):
            self.assertIn(token, index)
        styles = read("dev-tools/roadmap-review-site/styles.css")
        for token in (":focus-visible", "forced-colors: active", "prefers-reduced-motion: reduce", "max-width: 48rem", "--faa-target-min"):
            self.assertIn(token, styles)
        without_comments = re.sub(r"/\*.*?\*/", "", styles, flags=re.DOTALL)
        self.assertNotRegex(without_comments, r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")

    def test_fixed_readiness_stays_dependency_free(self) -> None:
        readiness = read("dev-tools/agent/check_ready.py")
        self.assertIn("roadmap review projection", readiness)
        self.assertIn("roadmap review site contract", readiness)
        checks = readiness[readiness.index("def checks"):readiness.index("def output_summary")]
        self.assertNotIn("node", checks.lower())
        self.assertNotIn("playwright", checks.lower())
        self.assertNotIn("roadmap-review-site/server.py", checks)

    def test_one_start_command_and_affected_browser_suite_are_documented(self) -> None:
        guide = read("dev-tools/roadmap-review-site/README.md")
        self.assertEqual(guide.count("python dev-tools/roadmap-review-site/server.py"), 1)
        self.assertIn("No data-generation", guide)
        self.assertIn("roadmap-review.config.ts", guide)
        browser = read("apps/web/tests/browser/roadmap-review/roadmap-review.e2e.ts")
        for token in ("AxeBuilder", "26", "forcedColors", "reducedMotion", "SLI-0018", "Roadmap entry not found"):
            self.assertIn(token, browser)


if __name__ == "__main__":
    unittest.main(verbosity=2)
