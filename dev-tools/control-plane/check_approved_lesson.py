#!/usr/bin/env python3
"""Run repository-owned web checks through the prepared Node/npm runtime."""

from __future__ import annotations

import argparse
import io
import os
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
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


def run_checked(
    command: Sequence[str],
    *,
    root: Path,
    environment: Mapping[str, str] | None = None,
) -> None:
    completed = subprocess.run(
        list(command),
        cwd=root,
        env=None if environment is None else dict(environment),
        check=False,
    )
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


def child_environment(
    runtime: WebRuntime,
    environment: Mapping[str, str],
) -> dict[str, str]:
    child = dict(environment)
    path_name = next(
        (name for name in child if name.casefold() == "path"),
        "PATH",
    )
    resolved_node = Path(shutil.which(runtime.node) or runtime.node).resolve()
    existing_path = child.get(path_name, "")
    child[path_name] = str(resolved_node.parent) + (
        os.pathsep + existing_path if existing_path else ""
    )
    child["PYTHON"] = sys.executable
    return child


def copy_tracked_candidate(source_root: Path, target_root: Path) -> None:
    completed = subprocess.run(
        ["git", "archive", "--format=tar", "HEAD"],
        cwd=source_root,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("Unable to export the exact tracked candidate.")
    with tarfile.open(fileobj=io.BytesIO(completed.stdout), mode="r:") as archive:
        members: list[tarfile.TarInfo] = []
        for member in archive.getmembers():
            relative = PurePosixPath(member.name)
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError("Git returned an unsafe tracked candidate path.")
            if relative.parts[:3] == ("apps", "web", "dist"):
                continue
            if not (member.isfile() or member.isdir()):
                raise RuntimeError(
                    f"Unsupported tracked candidate path: {member.name}"
                )
            members.append(member)
        archive.extractall(target_root, members=members, filter="data")


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


def select_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def run_roadmap_in_snapshot(
    runtime: WebRuntime,
    *,
    root: Path,
    command_runner: Callable[..., None] = run_checked,
    snapshot_preparer: Callable[[Path, Path], None] = prepare_candidate_snapshot,
    port_selector: Callable[[], int] = select_loopback_port,
) -> None:
    with tempfile.TemporaryDirectory(prefix="faa-affected-roadmap-") as directory:
        snapshot = Path(directory) / "candidate"
        snapshot_preparer(root, snapshot)
        config = (
            snapshot
            / "apps"
            / "web"
            / "tests"
            / "browser"
            / "roadmap-review.config.ts"
        )
        source = config.read_text(encoding="utf-8")
        if source.count("8765") != 3:
            raise RuntimeError(
                "The roadmap review config no longer has the expected isolated-port seam."
            )
        config.write_text(
            source.replace("8765", str(port_selector())),
            encoding="utf-8",
        )
        command_runner(
            npm_command(
                runtime,
                snapshot,
                "exec",
                "--",
                "playwright",
                "test",
                "--config",
                "apps/web/tests/browser/roadmap-review.config.ts",
                "apps/web/tests/browser/roadmap-review",
            ),
            root=snapshot,
        )


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
    port_selector: Callable[[], int] = select_loopback_port,
) -> None:
    runtime = resolve_runtime(environment)
    require_versions(runtime, root=root, version_reader=version_reader)
    execution_environment = child_environment(runtime, environment)

    def invoke(command: Sequence[str], *, root: Path) -> None:
        if command_runner is run_checked:
            run_checked(command, root=root, environment=execution_environment)
            return
        command_runner(command, root=root)

    commands = {
        "typecheck": npm_command(runtime, root, "run", "typecheck"),
        "lint": npm_command(runtime, root, "run", "lint"),
        "unit": npm_command(runtime, root, "test", "--", "--run"),
        "generated": npm_command(
            runtime, root, "run", "generate:api", "--", "--check"
        ),
        "roadmap-typecheck": (
            runtime.node,
            str(root / "apps" / "web" / "node_modules" / "typescript" / "bin" / "tsc"),
            "-p",
            str(root / "dev-tools" / "roadmap-review-site" / "tsconfig.json"),
            "--noEmit",
        ),
        "roadmap-unit": (
            runtime.node,
            str(root / "apps" / "web" / "node_modules" / "vitest" / "vitest.mjs"),
            "run",
            "--globals",
            "--environment",
            "jsdom",
            str(root / "dev-tools" / "roadmap-review-site" / "tests"),
        ),
        "browser": npm_command(
            runtime,
            root,
            "run",
            "test:browser",
            "--",
            *MOCKED_BROWSER_SUITES,
        ),
    }
    if mode == "build":
        run_build_in_snapshot(
            runtime,
            root=root,
            command_runner=invoke,
            snapshot_preparer=snapshot_preparer,
        )
        return
    if mode == "live":
        run_live_in_snapshot(
            runtime,
            root=root,
            command_runner=invoke,
            snapshot_preparer=snapshot_preparer,
        )
        return
    if mode == "roadmap":
        run_roadmap_in_snapshot(
            runtime,
            root=root,
            command_runner=invoke,
            snapshot_preparer=snapshot_preparer,
            port_selector=port_selector,
        )
        return
    if mode == "local-scripts":
        for script in ("dev.mjs", "setup-dev.mjs"):
            invoke(
                (runtime.node, "--check", str(root / "deployments" / "local" / script)),
                root=root,
            )
        return
    try:
        command = commands[mode]
    except KeyError as error:
        raise ValueError(f"Unsupported web check mode: {mode}") from error
    invoke(command, root=root)


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
            "roadmap-typecheck",
            "roadmap-unit",
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
