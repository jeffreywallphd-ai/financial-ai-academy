"""Tracked affected-check catalog for Financial AI Academy."""

from __future__ import annotations

import sys

from verification import CheckCatalog, CheckDefinition


def catalog() -> CheckCatalog:
    python = sys.executable
    return CheckCatalog(
        "financial-ai-academy-v1",
        (
            CheckDefinition("control-plane:unit", (python, "dev-tools/control-plane/test_control_plane.py"), ("dev-tools/control-plane/**",), "medium", 10, description="Reusable control-plane lifecycle and adapter tests"),
            CheckDefinition("planning:tools", (python, "dev-tools/planning/test_planning_tools.py"), ("dev-tools/planning/**", "docs/planning/**"), "medium", 20, description="Planning-tool behavior"),
            CheckDefinition("planning:integrity", (python, "dev-tools/planning/check_planning.py"), ("dev-tools/planning/**", "docs/planning/**"), "low", 30, description="Planning artifact integrity"),
            CheckDefinition("documentation:integrity", (python, "dev-tools/documentation/check_docs.py"), ("docs/**", "AGENTS.md"), "low", 40, description="Documentation and context integrity"),
            CheckDefinition("architecture:integrity", (python, "dev-tools/architecture/check_architecture.py"), ("backend/**", "contracts/**", "docs/architecture/**"), "high", 50, description="Architecture boundary checks"),
            CheckDefinition("design:integrity", (python, "dev-tools/design/check_design_system.py"), ("apps/web/src/design-system/**", "docs/design/**"), "medium", 60, description="Design-system integrity"),
            CheckDefinition("agent:readiness", (python, "dev-tools/agent/check_ready.py"), ("dev-tools/agent/**", ".github/workflows/**", "docs/planning/skills/**"), "high", 90, description="Shared agent-support readiness suite"),
        ),
    )
