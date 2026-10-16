#!/usr/bin/env python3
"""Run repository-owned web checks through the prepared Node/npm runtime."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence


REPOSITORY = Path(__file__).resolve().parents[2]
REQUIRED_NODE_MAJOR = 24
REQUIRED_NPM = "10.8.2"
MOCKED_BROWSER_SUITES = (
    "apps/web/tests/browser/curriculum-graph",
    "apps/web/tests/browser/learning-catalog",
    "apps/web/tests/browser/lesson-reading",
)


@dataclass(frozen=True, slots=True)
class WebRuntime:
    node: str
    npm: tuple[str, ...]


def resolve_runtime(environment: Mapping[str, str]) -> WebRuntime:
    node = environment.get("FINANCIAL_AI_ACADEMY_NODE_EXECUTABLE")
    npm_cli = environment.get("FINANCIAL_AI_ACADEMY_NPM_CLI")
    if bool(node) != bool(npm_cli):
        raise RuntimeError(
            "Set both FINANCIAL_AI_ACADEMY_NODE_EXECUTABLE and "
            "FINANCIAL_AI_ACADEMY_NPM_CLI, or neither."
        )
    if node and npm_cli:
        return WebRuntime(node=node, npm=(node, npm_cli))
    discovered_node = shutil.which("node")
    discovered_npm = shutil.which("npm")
    if not discovered_node or not discovered_npm:
        raise RuntimeError(
            "Node and npm are unavailable; run the repository development setup first."
        )
    return WebRuntime(node=discovered_node, npm=(discovered_npm,))


def capture(command: Sequence[str], *, root: Path) -> str:
    completed = subprocess.run(
        list(command),
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Runtime probe failed with exit code {completed.returncode}.")
    return completed.stdout.strip()


def require_versions(
    runtime: WebRuntime,
    *,
    root: Path,
    version_reader: Callable[..., str] = capture,
) -> None:
    node_version = version_reader((runtime.node, "--version"), root=root)
    npm_version = version_reader((*runtime.npm, "--version"), root=root)
    if not node_version.startswith(f"v{REQUIRED_NODE_MAJOR}."):
        raise RuntimeError(
            f"Node {REQUIRED_NODE_MAJOR} is required; received {node_version or 'no version'}."
        )
    if npm_version != REQUIRED_NPM:
        raise RuntimeError(
            f"npm {REQUIRED_NPM} is required; received {npm_version or 'no version'}."
        )


def run_checked(command: Sequence[str], *, root: Path) -> None:
    completed = subprocess.run(list(command), cwd=root, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Affected check failed with exit code {completed.returncode}."
        )


def npm_command(runtime: WebRuntime, root: Path, *arguments: str) -> tuple[str, ...]:
    return (
        *runtime.npm,
        "--prefix",
        str(root / "apps" / "web"),
        *arguments,
    )


def run_live_with_restored_build(
    runtime: WebRuntime,
    *,
    root: Path,
    command_runner: Callable[..., None] = run_checked,
) -> None:
    dist = root / "apps" / "web" / "dist"
    if dist.is_symlink() or (dist.exists() and not dist.is_dir()):
        raise RuntimeError("Refusing to replace an unexpected web build path.")
    with tempfile.TemporaryDirectory(prefix="faa-affected-web-") as directory:
        backup = Path(directory) / "dist"
        existed = dist.is_dir()
        if existed:
            shutil.copytree(dist, backup)
        try:
            command_runner(
                npm_command(runtime, root, "run", "build"),
                root=root,
            )
            if not (dist / "index.html").is_file():
                raise RuntimeError("The web build did not produce dist/index.html.")
            command_runner(
                (
                    sys.executable,
                    str(root / "tests" / "e2e" / "approved-lesson" / "run.py"),
                ),
                root=root,
            )
        finally:
            if dist.exists():
                shutil.rmtree(dist)
            if existed:
                shutil.copytree(backup, dist)


def execute(
    mode: str,
    *,
    root: Path = REPOSITORY,
    environment: Mapping[str, str] = os.environ,
    command_runner: Callable[..., None] = run_checked,
    version_reader: Callable[..., str] = capture,
) -> None:
    runtime = resolve_runtime(environment)
    require_versions(runtime, root=root, version_reader=version_reader)
    commands = {
        "typecheck": npm_command(runtime, root, "run", "typecheck"),
        "lint": npm_command(runtime, root, "run", "lint"),
        "unit": npm_command(runtime, root, "test", "--", "--run"),
        "browser": npm_command(
            runtime,
            root,
            "run",
            "test:browser",
            "--",
            *MOCKED_BROWSER_SUITES,
        ),
    }
    if mode == "live":
        run_live_with_restored_build(runtime, root=root, command_runner=command_runner)
        return
    try:
        command = commands[mode]
    except KeyError as error:
        raise ValueError(f"Unsupported web check mode: {mode}") from error
    command_runner(command, root=root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("typecheck", "lint", "unit", "browser", "live"),
        required=True,
    )
    args = parser.parse_args()
    execute(args.mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
