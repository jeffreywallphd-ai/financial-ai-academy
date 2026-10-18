"""Tracked affected-check catalog for Financial AI Academy."""

from __future__ import annotations

import hashlib
from pathlib import Path

from verification import (
    CURRENT_PYTHON_ARGUMENT,
    CheckCatalog,
    CheckDefinition,
    control_plane_file_argument,
)


def catalog() -> CheckCatalog:
    python = CURRENT_PYTHON_ARGUMENT
    wrapper = Path(__file__).resolve().with_name("check_approved_lesson.py")
    wrapper_digest = "sha256:" + hashlib.sha256(wrapper.read_bytes()).hexdigest()
    presentation_wrapper = Path(__file__).resolve().with_name(
        "check_presentation_preferences.py"
    )
    presentation_wrapper_digest = (
        "sha256:" + hashlib.sha256(presentation_wrapper.read_bytes()).hexdigest()
    )
    assistance_wrapper = Path(__file__).resolve().with_name(
        "check_assistance_preferences.py"
    )
    assistance_wrapper_digest = (
        "sha256:" + hashlib.sha256(assistance_wrapper.read_bytes()).hexdigest()
    )
    platform_help_wrapper = Path(__file__).resolve().with_name(
        "check_platform_help.py"
    )
    platform_help_wrapper_digest = (
        "sha256:" + hashlib.sha256(platform_help_wrapper.read_bytes()).hexdigest()
    )
    web_check = (
        python,
        control_plane_file_argument("check_approved_lesson.py", wrapper_digest),
        "--self-sha256",
        wrapper_digest,
        "--root",
        ".",
    )
    presentation_browser_check = (
        python,
        control_plane_file_argument(
            "check_presentation_preferences.py", presentation_wrapper_digest
        ),
        "--self-sha256",
        presentation_wrapper_digest,
        "--root",
        ".",
        "--mode",
        "presentation-browser",
    )
    assistance_browser_check = (
        python,
        control_plane_file_argument(
            "check_assistance_preferences.py", assistance_wrapper_digest
        ),
        "--self-sha256",
        assistance_wrapper_digest,
        "--root",
        ".",
        "--mode",
        "assistance-browser",
    )
    platform_help_browser_check = (
        python,
        control_plane_file_argument(
            "check_platform_help.py", platform_help_wrapper_digest
        ),
        "--self-sha256",
        platform_help_wrapper_digest,
        "--root",
        ".",
        "--mode",
        "platform-help-browser",
    )
    web_source_paths = (
        "apps/web/src/**",
        "apps/web/tests/unit/**",
        "apps/web/tests/component/**",
        "apps/web/tests/contract/**",
        "apps/web/vite.config.ts",
        "apps/web/package.json",
        "apps/web/package-lock.json",
    )
    web_build_paths = (
        "apps/web/index.html",
        "apps/web/tsconfig.json",
        "apps/web/vite.config.ts",
        "apps/web/package.json",
        "apps/web/package-lock.json",
        "apps/web/src/**",
    )
    generated_client_paths = (
        "apps/web/scripts/generate-api-client.mjs",
        "apps/web/src/generated/api-client/**",
        "backend/src/financial_ai_academy/hosts/api/**",
        "contracts/api/openapi.json",
    )
    mocked_browser_paths = (
        "apps/web/tests/browser/curriculum-graph/**",
        "apps/web/tests/browser/learning-catalog/**",
        "apps/web/tests/browser/lesson-reading/**",
        "apps/web/tests/browser/support/**",
        "apps/web/tests/browser/playwright.config.ts",
    )
    presentation_browser_paths = (
        "apps/web/src/features/presentation-preferences/**",
        "apps/web/src/platform/presentation/**",
        "apps/web/src/design-system/tokens.css",
        "apps/web/src/styles/presentation-preferences.css",
        "apps/web/tests/browser/presentation-preferences/**",
    )
    assistance_browser_paths = (
        "apps/web/src/features/assistance-preferences/**",
        "apps/web/src/platform/reminders/**",
        "apps/web/src/styles/assistance-preferences.css",
        "apps/web/tests/browser/assistance-preferences/**",
    )
    platform_help_browser_paths = (
        "apps/web/src/features/platform-help/**",
        "apps/web/src/styles/platform-help.css",
        "apps/web/tests/browser/platform-help/**",
    )
    project_browser_paths = (
        "apps/web/src/features/project-workspace/**",
        "apps/web/src/styles/project-workspace.css",
        "apps/web/tests/browser/project-workspace/**",
    )
    project_browser_check_paths = (
        *project_browser_paths,
        "dev-tools/control-plane/check_approved_lesson.py",
        "dev-tools/control-plane/financial_academy_checks.py",
    )
    approved_browser_paths = (
        "apps/web/tests/browser/approved-lesson/**",
        "apps/web/tests/browser/approved-lesson.config.ts",
    )
    roadmap_browser_paths = (
        "apps/web/tests/browser/roadmap-review/**",
        "apps/web/tests/browser/roadmap-review.config.ts",
    )
    roadmap_source_paths = (
        "dev-tools/roadmap-review-site/src/**",
        "dev-tools/roadmap-review-site/tsconfig.json",
    )
    roadmap_document_paths = (
        "dev-tools/roadmap-review-site/README.md",
    )
    roadmap_server_paths = (
        "dev-tools/roadmap-review-site/index.html",
        "dev-tools/roadmap-review-site/server.py",
        "dev-tools/roadmap-review-site/styles.css",
        "dev-tools/roadmap-review-site/test_server.py",
    )
    roadmap_unit_paths = (
        *roadmap_source_paths,
        "dev-tools/roadmap-review-site/tests/**",
    )
    roadmap_behavior_paths = (
        *roadmap_source_paths,
        *roadmap_server_paths[:3],
    )
    roadmap_qualification_paths = (
        *roadmap_behavior_paths,
        "dev-tools/roadmap-review-site/test_server.py",
        "dev-tools/roadmap-review-site/test_qualification.py",
        "dev-tools/roadmap-review-site/tests/**",
        *roadmap_browser_paths,
    )
    live_runtime_paths = (
        "tests/e2e/approved-lesson/**",
        "deployments/local/serve.py",
    )
    local_script_paths = (
        "deployments/local/dev.mjs",
        "deployments/local/setup-dev.mjs",
    )
    local_composition_paths = (
        "deployments/local/compose.qualify.yml",
        *local_script_paths,
        *live_runtime_paths,
    )
    learner_language_tool_paths = (
        "dev-tools/learner-language/check_learner_language.py",
        "dev-tools/learner-language/rules.json",
        "dev-tools/learner-language/test_learner_language.py",
    )
    learner_language_owned_paths = (
        "apps/web/src/app/*.tsx",
        "apps/web/src/app/**/*.tsx",
        "apps/web/src/components/*.tsx",
        "apps/web/src/components/**/*.tsx",
        "apps/web/src/features/*.tsx",
        "apps/web/src/features/**/*.tsx",
    )
    documentation_paths = (
        "apps/web/README.md",
        "deployments/local/README.md",
        "dev-tools/control-plane/README.md",
        "dev-tools/learner-language/README.md",
        *roadmap_document_paths,
    )
    return CheckCatalog(
        "financial-ai-academy-v8",
        (
            CheckDefinition("control-plane:unit", (python, "dev-tools/control-plane/test_control_plane.py"), ("dev-tools/control-plane/**",), "medium", 10, description="Reusable control-plane lifecycle and adapter tests"),
            CheckDefinition("control-plane:review", (python, "dev-tools/control-plane/test_review.py"), ("dev-tools/control-plane/review.py", "dev-tools/control-plane/test_review.py"), "medium", 11, description="Technical review, corrected-descendant, and review-ledger behavior"),
            CheckDefinition("control-plane:verification", (python, "dev-tools/control-plane/test_verification.py"), ("dev-tools/control-plane/verification.py", "dev-tools/control-plane/financial_academy_checks.py", "dev-tools/control-plane/check_approved_lesson.py", "dev-tools/control-plane/check_presentation_preferences.py", "dev-tools/control-plane/check_assistance_preferences.py", "dev-tools/control-plane/check_platform_help.py", "dev-tools/control-plane/test_verification.py"), "medium", 12, description="Affected-selection, repository-check, and receipt behavior"),
            CheckDefinition("planning:tools", (python, "dev-tools/planning/test_planning_tools.py"), ("dev-tools/planning/**", "docs/planning/**"), "medium", 20, description="Planning-tool behavior"),
            CheckDefinition("planning:integrity", (python, "dev-tools/planning/check_planning.py"), ("dev-tools/planning/**", "docs/planning/**"), "low", 30, description="Planning artifact integrity"),
            CheckDefinition("documentation:integrity", (python, "dev-tools/documentation/check_docs.py"), ("docs/**", "AGENTS.md", *documentation_paths), "low", 40, description="Documentation and context integrity"),
            CheckDefinition("learner-language:unit", (python, "dev-tools/learner-language/test_learner_language.py"), learner_language_tool_paths, "low", 41, description="Learner-language checker, configuration, and anti-rigidity behavior"),
            CheckDefinition("learner-language:full", (python, "dev-tools/learner-language/check_learner_language.py", "--all"), learner_language_tool_paths[:2], "low", 42, description="Controlled full-scope qualification after checker or rule changes"),
            CheckDefinition("learner-language:changed", (python, "dev-tools/learner-language/check_learner_language.py", "--base-ref", "{base_revision}"), learner_language_owned_paths, "low", 43, description="Candidate-bound changed learner-facing copy"),
            CheckDefinition("roadmap-review:qualification", (python, "dev-tools/roadmap-review-site/test_qualification.py"), roadmap_qualification_paths, "medium", 45, description="Roadmap review projection and site contract"),
            CheckDefinition("roadmap-review:server", (*web_check, "--mode", "roadmap-server"), roadmap_server_paths, "medium", 46, description="Roadmap review read-only server behavior"),
            CheckDefinition("roadmap-review:typecheck", (*web_check, "--mode", "roadmap-typecheck"), roadmap_source_paths, "medium", 47, description="Roadmap review TypeScript boundary"),
            CheckDefinition("roadmap-review:unit", (*web_check, "--mode", "roadmap-unit"), roadmap_unit_paths, "medium", 48, description="Roadmap review DOM and view-model behavior"),
            CheckDefinition("architecture:integrity", (python, "dev-tools/architecture/check_architecture.py"), ("backend/**", "contracts/**", "docs/architecture/**"), "high", 50, description="Architecture boundary checks"),
            CheckDefinition("local:architecture", (python, "tests/architecture/test_approved_lesson_boundaries.py"), local_composition_paths, "medium", 51, description="Local composition and approved-lesson boundary checks"),
            CheckDefinition("web:typecheck", (*web_check, "--mode", "typecheck"), (*web_source_paths, *mocked_browser_paths, *presentation_browser_paths, *assistance_browser_paths, *platform_help_browser_paths, *project_browser_paths, *approved_browser_paths, *roadmap_browser_paths, "apps/web/tsconfig.json"), "medium", 52, description="Web TypeScript boundary"),
            CheckDefinition("web:lint", (*web_check, "--mode", "lint"), (*web_source_paths, *mocked_browser_paths, *presentation_browser_paths, *assistance_browser_paths, *platform_help_browser_paths, *project_browser_paths, *approved_browser_paths, *roadmap_browser_paths), "medium", 54, description="Web source and test lint"),
            CheckDefinition("web:unit", (*web_check, "--mode", "unit"), (*web_source_paths, "apps/web/scripts/generate-api-client.mjs"), "medium", 56, description="Web unit, component, and contract behavior"),
            CheckDefinition("web:browser", (*web_check, "--mode", "browser"), mocked_browser_paths, "medium", 58, timeout_seconds=120, description="Mocked Chromium application behavior"),
            CheckDefinition("presentation:browser", presentation_browser_check, (*presentation_browser_paths, "dev-tools/control-plane/check_presentation_preferences.py"), "medium", 58, timeout_seconds=120, description="Focused presentation-preferences Chromium behavior"),
            CheckDefinition("assistance:browser", assistance_browser_check, (*assistance_browser_paths, "dev-tools/control-plane/check_assistance_preferences.py"), "medium", 58, timeout_seconds=120, description="Focused assistance-preferences Chromium behavior"),
            CheckDefinition("platform-help:browser", platform_help_browser_check, (*platform_help_browser_paths, "dev-tools/control-plane/check_platform_help.py"), "medium", 58, timeout_seconds=120, description="Focused platform-help Chromium behavior"),
            CheckDefinition("project:browser", (*web_check, "--mode", "project-browser"), project_browser_check_paths, "medium", 59, timeout_seconds=120, description="Focused Project Chromium behavior"),
            CheckDefinition("design:integrity", (python, "dev-tools/design/check_design_system.py"), ("apps/web/src/design-system/**", "docs/design/**"), "medium", 60, description="Design-system integrity"),
            CheckDefinition("web:build", (*web_check, "--mode", "build"), web_build_paths, "medium", 62, description="Static web production build"),
            CheckDefinition("web:generated-client", (*web_check, "--mode", "generated"), generated_client_paths, "high", 64, description="Reviewed OpenAPI generated-client reproduction"),
            CheckDefinition("roadmap-review:browser", (*web_check, "--mode", "roadmap"), (*roadmap_behavior_paths, *roadmap_browser_paths), "medium", 66, timeout_seconds=120, description="Roadmap review Chromium behavior"),
            CheckDefinition("local:node-syntax", (*web_check, "--mode", "local-scripts"), local_script_paths, "medium", 68, description="Local Node runner syntax"),
            CheckDefinition("approved-lesson:live", (*web_check, "--mode", "live"), (*approved_browser_paths, *live_runtime_paths, "dev-tools/control-plane/check_approved_lesson.py"), "high", 70, timeout_seconds=300, description="Live PostgreSQL, Python, static browser, and pinned Chromium qualification"),
            CheckDefinition("agent:readiness", (python, "dev-tools/agent/check_ready.py"), ("dev-tools/agent/**", ".github/workflows/**", "docs/planning/skills/**"), "high", 90, timeout_seconds=180, description="Shared agent-support readiness suite"),
        ),
    )
