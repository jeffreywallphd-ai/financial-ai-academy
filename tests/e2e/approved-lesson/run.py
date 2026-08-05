"""Run the isolated approved-lesson cross-system qualification."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid4


REPOSITORY = Path(__file__).resolve().parents[3]
ARTIFACT_ROOT = REPOSITORY / "artifacts" / "tmp"
CONTAINER_PREFIX = "faa-wrk0005-postgres-"
POSTGRES_IMAGE = "postgres:18.4"
POSTGRES_USER = "financial_ai_academy"
POSTGRES_DATABASE = "financial_ai_academy"
POSTGRES_PASSWORD = "qualification-only"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Qualify the approved lesson through PostgreSQL, Python, and Chromium."
    )
    parser.add_argument(
        "--postgres-dsn",
        default=os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN"),
        help=(
            "Use an already isolated PostgreSQL database instead of starting "
            "the pinned local container."
        ),
    )
    return parser.parse_args()


def free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def run_checked(command: list[str], *, env: dict[str, str] | None = None) -> None:
    completed = subprocess.run(
        command,
        cwd=REPOSITORY,
        env=env,
        check=False,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Qualification command failed with exit code {completed.returncode}."
        )


def wait_for_postgres(container_name: str) -> None:
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        result = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                "pg_isready",
                "-U",
                POSTGRES_USER,
                "-d",
                POSTGRES_DATABASE,
            ],
            cwd=REPOSITORY,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode == 0:
            return
        time.sleep(0.25)
    raise RuntimeError("The isolated PostgreSQL container did not become ready.")


def start_postgres() -> tuple[str, str]:
    container_name = CONTAINER_PREFIX + uuid4().hex[:12]
    port = free_loopback_port()
    try:
        run_checked(
            [
                "docker",
                "run",
                "--detach",
                "--name",
                container_name,
                "--publish",
                f"127.0.0.1:{port}:5432",
                "--env",
                f"POSTGRES_DB={POSTGRES_DATABASE}",
                "--env",
                f"POSTGRES_USER={POSTGRES_USER}",
                "--env",
                f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}",
                "--tmpfs",
                "/var/lib/postgresql",
                POSTGRES_IMAGE,
            ]
        )
        wait_for_postgres(container_name)
    except Exception:
        remove_container(container_name)
        raise
    dsn = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@127.0.0.1:{port}/{POSTGRES_DATABASE}"
    )
    return container_name, dsn


def wait_for_http(url: str, process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("The Python application exited before readiness.")
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(0.25)
    raise RuntimeError("The Python application did not become ready.")


def npm_e2e_command() -> list[str]:
    node = os.environ.get("FINANCIAL_AI_ACADEMY_NODE_EXECUTABLE")
    npm_cli = os.environ.get("FINANCIAL_AI_ACADEMY_NPM_CLI")
    if bool(node) != bool(npm_cli):
        raise RuntimeError(
            "Set both FINANCIAL_AI_ACADEMY_NODE_EXECUTABLE and "
            "FINANCIAL_AI_ACADEMY_NPM_CLI, or neither."
        )
    prefix = ["npm"] if not node else [node, npm_cli]
    return [
        *prefix,
        "--prefix",
        str(REPOSITORY / "apps" / "web"),
        "run",
        "test:e2e",
    ]


def remove_container(container_name: str | None) -> None:
    if not container_name:
        return
    if not container_name.startswith(CONTAINER_PREFIX):
        raise RuntimeError("Refusing to remove an unexpected container.")
    inspected = subprocess.run(
        ["docker", "inspect", container_name],
        cwd=REPOSITORY,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if inspected.returncode != 0:
        return
    completed = subprocess.run(
        ["docker", "rm", "--force", "--volumes", container_name],
        cwd=REPOSITORY,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("The isolated PostgreSQL container was not removed.")


def remove_data_root(data_root: Path | None) -> None:
    if data_root is None or not data_root.exists():
        return
    artifact_root = ARTIFACT_ROOT.resolve()
    resolved = data_root.resolve()
    if (
        not resolved.is_relative_to(artifact_root)
        or not resolved.name.startswith("wrk0005-")
    ):
        raise RuntimeError("Refusing to remove an unexpected data root.")
    deadline = time.monotonic() + 5
    while True:
        try:
            shutil.rmtree(resolved)
            return
        except PermissionError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.1)


def main() -> int:
    args = parse_args()
    web_index = REPOSITORY / "apps" / "web" / "dist" / "index.html"
    if not web_index.is_file():
        raise RuntimeError(
            "The reviewed static build is absent; run npm --prefix apps/web run build."
        )

    external_dsn = args.postgres_dsn
    if external_dsn and (
        os.environ.get("FINANCIAL_AI_ACADEMY_E2E_EXTERNAL_DB_ACKNOWLEDGED")
        != "true"
    ):
        raise RuntimeError(
            "External PostgreSQL qualification requires an explicit isolated-database acknowledgement."
        )

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    data_root = Path(tempfile.mkdtemp(prefix="wrk0005-", dir=ARTIFACT_ROOT))
    container_name: str | None = None
    application: subprocess.Popen[str] | None = None
    application_log = data_root / "python-application.log"
    port = free_loopback_port()
    origin = f"http://127.0.0.1:{port}"

    try:
        if external_dsn:
            postgres_dsn = external_dsn
            postgres_topology = "externally managed isolated PostgreSQL"
        else:
            container_name, postgres_dsn = start_postgres()
            postgres_topology = f"{POSTGRES_IMAGE} isolated container"

        command = [
            sys.executable,
            str(REPOSITORY / "deployments" / "local" / "serve.py"),
            "--postgres-dsn",
            postgres_dsn,
            "--data-root",
            str(data_root / "application-data"),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--seed-approved-fixture",
        ]
        with application_log.open("w", encoding="utf-8") as output:
            application = subprocess.Popen(
                command,
                cwd=REPOSITORY,
                stdout=output,
                stderr=subprocess.STDOUT,
                text=True,
            )
        wait_for_http(f"{origin}/ready", application)

        environment = os.environ.copy()
        environment["FINANCIAL_AI_ACADEMY_E2E_BASE_URL"] = origin
        run_checked(npm_e2e_command(), env=environment)

        report = {
            "browser": "Playwright pinned Chromium",
            "database": postgres_topology,
            "filesystem": "isolated temporary data root",
            "fixture": "intro-risk-return@1.0.0",
            "http_origin": origin,
            "production_application_process": Path(sys.executable).name,
            "static_index_sha256": hashlib.sha256(
                web_index.read_bytes()
            ).hexdigest(),
            "static_serving": "same-origin Python application",
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except Exception:
        if application_log.is_file():
            diagnostics = application_log.read_text(
                encoding="utf-8", errors="replace"
            )
            if external_dsn:
                diagnostics = diagnostics.replace(external_dsn, "<redacted-dsn>")
            print(diagnostics[-4000:], file=sys.stderr)
        raise
    finally:
        if application is not None and application.poll() is None:
            application.terminate()
            try:
                application.wait(timeout=10)
            except subprocess.TimeoutExpired:
                application.kill()
                application.wait(timeout=5)
        remove_container(container_name)
        remove_data_root(data_root)


if __name__ == "__main__":
    raise SystemExit(main())
