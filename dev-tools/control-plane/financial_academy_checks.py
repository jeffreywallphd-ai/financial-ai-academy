"""Tracked affected-check catalog for Financial AI Academy."""

from __future__ import annotations

import sys

from verification import CheckCatalog, CheckDefinition


def catalog() -> CheckCatalog:
    python = sys.executable
    web_check = (python, "dev-tools/control-plane/check_approved_lesson.py")
    web_paths = (
        "apps/web/src/**",
        "apps/web/tests/unit/**",
        "apps/web/tests/component/**",
        "apps/web/tests/contract/**",
        "apps/web/vite.config.ts",
        "apps/web/package.json",
        "apps/web/package-lock.json",
    )
    mocked_browser_paths = (
        "apps/web/tests/browser/curriculum-graph/**",
        "apps/web/tests/browser/learning-catalog/**",
        "apps/web/tests/browser/lesson-reading/**",
        "apps/web/tests/browser/support/**",
        "apps/web/tests/browser/playwright.config.ts",
    )
    live_paths = (
        "apps/web/tests/browser/approved-lesson/**",
        "apps/web/tests/browser/approved-lesson.config.ts",
        "tests/e2e/approved-lesson/**",
        "deployments/local/**",
    )
    return CheckCatalog(
        "financial-ai-academy-v2",
        (
            CheckDefinition("control-plane:unit", (python, "dev-tools/control-plane/test_control_plane.py"), ("dev-tools/control-plane/**",), "medium", 10, description="Reusable control-plane lifecycle and adapter tests"),
            CheckDefinition("control-plane:verification", (python, "dev-tools/control-plane/test_verification.py"), ("dev-tools/control-plane/verification.py", "dev-tools/control-plane/financial_academy_checks.py", "dev-tools/control-plane/check_approved_lesson.py", "dev-tools/control-plane/test_verification.py"), "medium", 12, description="Affected-selection, repository-check, and receipt behavior"),
            CheckDefinition("planning:tools", (python, "dev-tools/planning/test_planning_tools.py"), ("dev-tools/planning/**", "docs/planning/**"), "medium", 20, description="Planning-tool behavior"),
            CheckDefinition("planning:integrity", (python, "dev-tools/planning/check_planning.py"), ("dev-tools/planning/**", "docs/planning/**"), "low", 30, description="Planning artifact integrity"),
            CheckDefinition("documentation:integrity", (python, "dev-tools/documentation/check_docs.py"), ("docs/**", "AGENTS.md"), "low", 40, description="Documentation and context integrity"),
            CheckDefinition("architecture:integrity", (python, "dev-tools/architecture/check_architecture.py"), ("backend/**", "contracts/**", "docs/architecture/**"), "high", 50, description="Architecture boundary checks"),
            CheckDefinition("web:typecheck", (*web_check, "--mode", "typecheck"), (*web_paths, *mocked_browser_paths, *live_paths), "medium", 52, description="Web TypeScript boundary"),
            CheckDefinition("web:lint", (*web_check, "--mode", "lint"), (*web_paths, *mocked_browser_paths, *live_paths), "medium", 54, description="Web source and test lint"),
            CheckDefinition("web:unit", (*web_check, "--mode", "unit"), (*web_paths, *mocked_browser_paths, *live_paths), "medium", 56, description="Web unit, component, and contract behavior"),
            CheckDefinition("web:browser", (*web_check, "--mode", "browser"), mocked_browser_paths, "medium", 58, timeout_seconds=120, description="Mocked Chromium application behavior"),
            CheckDefinition("design:integrity", (python, "dev-tools/design/check_design_system.py"), ("apps/web/src/design-system/**", "docs/design/**"), "medium", 60, description="Design-system integrity"),
            CheckDefinition("approved-lesson:live", (*web_check, "--mode", "live"), live_paths, "high", 70, timeout_seconds=240, description="Live PostgreSQL, Python, static browser, and pinned Chromium qualification"),
            CheckDefinition("agent:readiness", (python, "dev-tools/agent/check_ready.py"), ("dev-tools/agent/**", ".github/workflows/**", "docs/planning/skills/**", *live_paths), "high", 90, timeout_seconds=180, description="Shared agent-support readiness suite"),
        ),
    )
