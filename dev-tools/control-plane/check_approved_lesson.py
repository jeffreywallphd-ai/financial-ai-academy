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


def copy_tracked_candidate(source_root: Path, target_root: Path) -> None:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=source_root,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("Unable to enumerate the exact tracked candidate.")
    for raw_path in completed.stdout.split(b"\0"):
        if not raw_path:
            continue
        value = os.fsdecode(raw_path).replace("\\", "/")
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError("Git returned an unsafe tracked candidate path.")
        if relative.parts[:3] == ("apps", "web", "dist"):
            continue
        source = source_root / relative
        target = target_root / relative
        if source.is_symlink() or not source.is_file():
            raise RuntimeError(f"Unsupported tracked candidate path: {value}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def link_web_dependencies(source_root: Path, target_root: Path) -> None:
    source = source_root / "apps" / "web" / "node_modules"
    target = target_root / "apps" / "web" / "node_modules"
    if not source.is_dir():
        raise RuntimeError(
            "The prepared web dependencies are absent; run repository setup first."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        target.symlink_to(source, target_is_directory=True)
    except OSError as error:
        if os.name != "nt":
            raise RuntimeError("Unable to link prepared web dependencies.") from error
        completed = subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(target), str(source)],
            check=False,
            capture_output=True,
        )
        if completed.returncode != 0:
            raise RuntimeError("Unable to link prepared web dependencies.") from error


def prepare_candidate_snapshot(source_root: Path, target_root: Path) -> None:
    target_root.mkdir(parents=True, exist_ok=False)
    copy_tracked_candidate(source_root, target_root)
    link_web_dependencies(source_root, target_root)


def run_build_in_snapshot(
    runtime: WebRuntime,
    *,
    root: Path,
    command_runner: Callable[..., None] = run_checked,
    snapshot_preparer: Callable[[Path, Path], None] = prepare_candidate_snapshot,
) -> None:
    with tempfile.TemporaryDirectory(prefix="faa-affected-web-") as directory:
        snapshot = Path(directory) / "candidate"
        snapshot_preparer(root, snapshot)
        command_runner(
            npm_command(runtime, snapshot, "run", "build"),
            root=snapshot,
        )
        if not (snapshot / "apps" / "web" / "dist" / "index.html").is_file():
            raise RuntimeError("The isolated web build did not produce dist/index.html.")


def run_live_in_snapshot(
    runtime: WebRuntime,
    *,
    root: Path,
    command_runner: Callable[..., None] = run_checked,
    snapshot_preparer: Callable[[Path, Path], None] = prepare_candidate_snapshot,
) -> None:
    with tempfile.TemporaryDirectory(prefix="faa-affected-web-") as directory:
        snapshot = Path(directory) / "candidate"
        snapshot_preparer(root, snapshot)
        command_runner(
            npm_command(runtime, snapshot, "run", "build"),
            root=snapshot,
        )
        if not (snapshot / "apps" / "web" / "dist" / "index.html").is_file():
            raise RuntimeError("The isolated web build did not produce dist/index.html.")
        command_runner(
            (
                sys.executable,
                str(snapshot / "tests" / "e2e" / "approved-lesson" / "run.py"),
            ),
            root=snapshot,
        )


def execute(
    mode: str,
    *,
    root: Path = REPOSITORY,
    environment: Mapping[str, str] = os.environ,
    command_runner: Callable[..., None] = run_checked,
    version_reader: Callable[..., str] = capture,
    snapshot_preparer: Callable[[Path, Path], None] = prepare_candidate_snapshot,
) -> None:
    runtime = resolve_runtime(environment)
    require_versions(runtime, root=root, version_reader=version_reader)
    commands = {
        "typecheck": npm_command(runtime, root, "run", "typecheck"),
        "lint": npm_command(runtime, root, "run", "lint"),
        "unit": npm_command(runtime, root, "test", "--", "--run"),
        "generated": npm_command(
            runtime, root, "run", "generate:api", "--", "--check"
        ),
        "browser": npm_command(
            runtime,
            root,
            "run",
            "test:browser",
            "--",
            *MOCKED_BROWSER_SUITES,
        ),
        "roadmap": npm_command(
            runtime,
            root,
            "exec",
            "--",
            "playwright",
            "test",
            "--config",
            "tests/browser/roadmap-review.config.ts",
            "apps/web/tests/browser/roadmap-review",
        ),
    }
    if mode == "build":
        run_build_in_snapshot(
            runtime,
            root=root,
            command_runner=command_runner,
            snapshot_preparer=snapshot_preparer,
        )
        return
    if mode == "live":
        run_live_in_snapshot(
            runtime,
            root=root,
            command_runner=command_runner,
            snapshot_preparer=snapshot_preparer,
        )
        return
    if mode == "local-scripts":
        for script in ("dev.mjs", "setup-dev.mjs"):
            command_runner(
                (runtime.node, "--check", str(root / "deployments" / "local" / script)),
                root=root,
            )
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
        choices=(
            "typecheck",
            "lint",
            "unit",
            "build",
            "generated",
            "browser",
            "roadmap",
            "local-scripts",
            "live",
        ),
        required=True,
    )
    args = parser.parse_args()
    execute(args.mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
