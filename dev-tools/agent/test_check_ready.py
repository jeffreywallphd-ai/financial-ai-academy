#!/usr/bin/env python3
"""Focused tests for the fixed agent-readiness command catalog."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from check_ready import checks  # noqa: E402


class ReadinessCatalogTests(unittest.TestCase):
    root = Path("C:/readiness-catalog-fixture")

    @staticmethod
    def by_name(root: Path, *, profile: str, base_ref: str | None) -> dict[str, tuple[str, ...]]:
        return {item.name: item.arguments for item in checks(root, profile, base_ref)}

    def test_changed_scope_is_default_and_never_expands_to_full_scope(self) -> None:
        commands = self.by_name(self.root, profile="local", base_ref=None)
        self.assertEqual(
            (sys.executable, "dev-tools/learner-language/check_learner_language.py"),
            commands["learner-language quality"],
        )
        self.assertNotIn("--all", commands["learner-language quality"])

    def test_base_ref_is_forwarded_exactly_in_local_and_ci_profiles(self) -> None:
        base_ref = "a" * 40
        for profile in ("local", "ci"):
            with self.subTest(profile=profile):
                commands = self.by_name(self.root, profile=profile, base_ref=base_ref)
                self.assertEqual(
                    (sys.executable, "dev-tools/learner-language/check_learner_language.py", "--base-ref", base_ref),
                    commands["learner-language quality"],
                )
                self.assertEqual(
                    (sys.executable, "dev-tools/planning/check_planning.py", "--base-ref", base_ref),
                    commands["planning integrity"],
                )
                self.assertNotIn("--all", commands["learner-language quality"])

    def test_readiness_behavior_test_is_fixed_and_non_recursive(self) -> None:
        commands = self.by_name(self.root, profile="ci", base_ref=None)
        self.assertEqual(
            (sys.executable, "dev-tools/agent/test_check_ready.py"),
            commands["agent-readiness behavior"],
        )
        self.assertNotIn("dev-tools/agent/check_ready.py", commands["agent-readiness behavior"])

    def test_guidance_quality_is_a_fixed_fast_readiness_check(self) -> None:
        commands = self.by_name(self.root, profile="ci", base_ref=None)
        self.assertEqual(
            (sys.executable, "dev-tools/guidance/check_guidance_quality.py"),
            commands["guidance quality"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
