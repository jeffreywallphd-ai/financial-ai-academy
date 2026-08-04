#!/usr/bin/env python3
"""Verify the repository's minimal, read-only agent-readiness CI wiring."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/agent-readiness.yml"
REQUIRED = (
    "name: Agent readiness",
    "pull_request:",
    "push:",
    "      - main",
    "contents: read",
    "timeout-minutes: 10",
    "uses: actions/checkout@v7",
    "fetch-depth: 0",
    "persist-credentials: false",
    "uses: actions/setup-python@v7",
    'python-version: "3.13"',
    "run: python dev-tools/agent/check_ready.py --profile ci --base-ref",
    "run: python dev-tools/agent/check_ready.py --profile ci\n",
)
PROHIBITED = (
    "pull_request_target:",
    "workflow_run:",
    "contents: write",
    "write-all",
    "secrets: inherit",
)


def main() -> int:
    if not WORKFLOW.is_file():
        print(f"CI workflow check failed: missing {WORKFLOW.relative_to(ROOT)}")
        return 1
    text = WORKFLOW.read_text(encoding="utf-8")
    errors = [f"missing required token: {token}" for token in REQUIRED if token not in text]
    errors.extend(f"prohibited token: {token}" for token in PROHIBITED if token in text)
    if errors:
        print("CI workflow check failed:")
        for issue in errors:
            print(f"- {issue}")
        return 1
    print("CI workflow check passed: read-only triggers and deterministic readiness commands verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
