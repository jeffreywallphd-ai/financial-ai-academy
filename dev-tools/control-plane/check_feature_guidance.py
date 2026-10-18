#!/usr/bin/env python3
"""Run candidate-bound feature-guidance contract and pure-core checks."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Callable, Mapping, Sequence

from check_approved_lesson import (
    REPOSITORY,
    execute_bound_check,
    resolve_python,
    run_checked,
)


WRAPPER = Path(__file__).resolve()
FOCUSED_SUITES = (
    "backend/tests/unit/guidance",
    "backend/tests/contract/platform_help",
    "backend/tests/contract/contextual_help",
    "backend/tests/contract/feature_guidance",
)
COMPILE_TARGETS = (
    "backend/src/financial_ai_academy/modules/guidance",
    "backend/tests/contract/feature_guidance",
    "backend/tests/unit/guidance/test_feature_guidance.py",
)


def _child_environment(
    environment: Mapping[str, str],
    *,
    root: Path,
) -> dict[str, str]:
    child = dict(environment)
    source_root = str(root / "backend" / "src")
    current = child.get("PYTHONPATH", "")
    child["PYTHONPATH"] = source_root + (os.pathsep + current if current else "")
    return child


def execute(
    mode: str,
    *,
    root: Path = REPOSITORY,
    environment: Mapping[str, str] = os.environ,
    command_runner: Callable[..., None] = run_checked,
) -> None:
    if mode != "feature-guidance":
        raise ValueError(f"Unsupported feature-guidance check mode: {mode}")
    python = resolve_python(environment, root=root)
    child = _child_environment(environment, root=root)
    commands: tuple[Sequence[str], ...] = (
        (
            python,
            "-m",
            "pytest",
            *FOCUSED_SUITES,
            "-q",
            "--basetemp=.local-codex/t/feature-guidance-verification",
        ),
        (python, "-m", "compileall", "-q", *COMPILE_TARGETS),
    )
    for command in commands:
        if command_runner is run_checked:
            run_checked(command, root=root, environment=child)
        else:
            command_runner(command, root=root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-sha256")
    parser.add_argument("--root", default=str(REPOSITORY))
    parser.add_argument("--mode", choices=("feature-guidance",), required=True)
    arguments = parser.parse_args()
    execute_bound_check(
        arguments.mode,
        root=Path(arguments.root),
        expected_wrapper_digest=arguments.self_sha256,
        wrapper=WRAPPER,
        executor=execute,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
