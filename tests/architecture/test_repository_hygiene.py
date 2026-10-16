from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]


def run_git(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=REPOSITORY,
        check=False,
        capture_output=True,
        text=True,
    )


class RepositoryHygieneTests(unittest.TestCase):
    def test_nested_node_modules_are_ignored(self) -> None:
        result = run_git(
            "check-ignore",
            "--quiet",
            "--no-index",
            "apps/web/node_modules/.repository-hygiene-probe",
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_installed_dependencies_are_not_tracked(self) -> None:
        result = run_git("ls-files", "--", ":(glob)**/node_modules/**")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
