#!/usr/bin/env python3
"""Run the focused assistance-preferences Chromium check."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Callable, Mapping, Sequence

from check_approved_lesson import (
    REPOSITORY,
    WebRuntime,
    capture,
    child_environment,
    execute_bound_check,
    npm_command,
    require_versions,
    resolve_runtime,
    run_checked,
)


WRAPPER = Path(__file__).resolve()
ASSISTANCE_BROWSER_SUITE = "apps/web/tests/browser/assistance-preferences"


def execute(
    mode: str,
    *,
    root: Path = REPOSITORY,
    environment: Mapping[str, str] = os.environ,
    command_runner: Callable[..., None] = run_checked,
    version_reader: Callable[..., str] = capture,
) -> None:
    if mode != "assistance-browser":
        raise ValueError(f"Unsupported assistance check mode: {mode}")
    runtime: WebRuntime = resolve_runtime(environment, root=root)
    require_versions(runtime, root=root, version_reader=version_reader)
    command: Sequence[str] = npm_command(
        runtime,
        root,
        "run",
        "test:browser",
        "--",
        ASSISTANCE_BROWSER_SUITE,
    )
    if command_runner is run_checked:
        run_checked(
            command,
            root=root,
            environment=child_environment(runtime, environment),
        )
        return
    command_runner(command, root=root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-sha256")
    parser.add_argument("--root", default=str(REPOSITORY))
    parser.add_argument(
        "--mode",
        choices=("assistance-browser",),
        required=True,
    )
    args = parser.parse_args()
    execute_bound_check(
        args.mode,
        root=Path(args.root),
        expected_wrapper_digest=args.self_sha256,
        wrapper=WRAPPER,
        executor=execute,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
