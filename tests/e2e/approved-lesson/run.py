"""Run the isolated approved-lesson cross-system qualification."""

from __future__ import annotations

import argparse
import copy
import hashlib
import http.cookiejar
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
from typing import Any
from uuid import uuid4

import psycopg


REPOSITORY = Path(__file__).resolve().parents[3]
ARTIFACT_ROOT = REPOSITORY / "artifacts" / "tmp"
CONTAINER_PREFIX = "faa-wrk0005-postgres-"
POSTGRES_IMAGE = "postgres:18.4"
POSTGRES_USER = "financial_ai_academy"
POSTGRES_DATABASE = "financial_ai_academy"
POSTGRES_PASSWORD = "qualification-only"
CURRICULUM_ID = "investing-foundations"
CURRICULUM_VERSION = "1.0.0"
LESSON_ACTIVITY_ID = "activity-risk-return-lesson"
REBUILDABLE_COMPLETION_RESET = (
    "DELETE FROM learner_model.lesson_completion_history",
    "DELETE FROM learner_model.lesson_completion_projections",
)
COMPLETION_STORAGE_COUNTS = """
    SELECT
        (SELECT count(*) FROM assessment.completion_evidence),
        (SELECT count(*) FROM assessment.outbox),
        (SELECT count(*)
           FROM learner_model.lesson_completion_projections),
        (SELECT count(*) FROM learner_model.lesson_completion_history)
"""


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


def application_command(
    *,
    postgres_dsn: str,
    data_root: Path,
    port: int,
    seed_fixture: bool,
) -> list[str]:
    command = [
        sys.executable,
        str(REPOSITORY / "deployments" / "local" / "serve.py"),
        "--postgres-dsn",
        postgres_dsn,
        "--data-root",
        str(data_root),
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ]
    if seed_fixture:
        command.extend(
            ["--seed-approved-fixture", "--seed-discovery-query-fixtures"]
        )
    return command


def start_application(
    *,
    postgres_dsn: str,
    data_root: Path,
    port: int,
    application_log: Path,
    seed_fixture: bool,
) -> subprocess.Popen[str]:
    with application_log.open("a", encoding="utf-8") as output:
        process = subprocess.Popen(
            application_command(
                postgres_dsn=postgres_dsn,
                data_root=data_root,
                port=port,
                seed_fixture=seed_fixture,
            ),
            cwd=REPOSITORY,
            stdout=output,
            stderr=subprocess.STDOUT,
            text=True,
        )
    try:
        wait_for_http(f"http://127.0.0.1:{port}/ready", process)
    except Exception:
        stop_application(process)
        raise
    return process


def stop_application(application: subprocess.Popen[str] | None) -> None:
    if application is None or application.poll() is not None:
        return
    application.terminate()
    try:
        application.wait(timeout=10)
    except subprocess.TimeoutExpired:
        application.kill()
        application.wait(timeout=5)


def cleanup_qualification(
    *,
    application: subprocess.Popen[str] | None,
    container_name: str | None,
    data_root: Path | None,
) -> tuple[str, ...]:
    failures: list[str] = []
    steps = (
        ("application", lambda: stop_application(application)),
        ("database container", lambda: remove_container(container_name)),
        ("temporary data", lambda: remove_data_root(data_root)),
    )
    for label, cleanup in steps:
        try:
            cleanup()
        except Exception as error:
            failures.append(f"{label} ({type(error).__name__})")
    return tuple(failures)


def finish_after_cleanup(
    primary_error: BaseException | None,
    cleanup_failures: tuple[str, ...],
) -> None:
    if primary_error is not None:
        if cleanup_failures:
            primary_error.add_note(
                "Qualification cleanup also failed for: "
                + ", ".join(cleanup_failures)
                + "."
            )
        raise primary_error.with_traceback(primary_error.__traceback__)
    if cleanup_failures:
        raise RuntimeError(
            "Qualification cleanup failed for: "
            + ", ".join(cleanup_failures)
            + "."
        )


def _request_json(
    opener: urllib.request.OpenerDirector,
    *,
    origin: str,
    path: str,
    method: str = "GET",
    payload: dict[str, object] | None = None,
) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers.update(
            {
                "Content-Type": "application/json",
                "Origin": origin,
                "Sec-Fetch-Site": "same-origin",
            }
        )
    request = urllib.request.Request(
        f"{origin}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with opener.open(request, timeout=10) as response:
            if not 200 <= response.status < 300:
                raise RuntimeError(
                    f"Headless API request failed: {method} {path} "
                    f"returned {response.status}."
                )
            document = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"Headless API request failed: {method} {path} "
            f"returned {error.code}."
        ) from None
    if not isinstance(document, dict):
        raise RuntimeError(
            f"Headless API request returned a non-object: {method} {path}."
        )
    return document


def stable_navigation_semantics(
    navigation: dict[str, Any],
) -> dict[str, Any]:
    required = (
        "schema_version",
        "curriculum_id",
        "curriculum_version",
        "graph_digest",
        "policy_id",
        "policy_version",
        "source_set_digest",
        "activity_states",
    )
    missing = [key for key in required if key not in navigation]
    if missing:
        raise RuntimeError(
            "Navigation response is missing stable fields: "
            + ", ".join(sorted(missing))
            + "."
        )
    return {key: copy.deepcopy(navigation[key]) for key in required}


def _stable_launch_semantics(launch: dict[str, Any]) -> dict[str, Any]:
    required = (
        "schema_version",
        "curriculum_id",
        "curriculum_version",
        "graph_digest",
        "activity_id",
        "placement_id",
        "package_id",
        "package_version",
        "package_digest",
        "destination",
    )
    missing = [key for key in required if key not in launch]
    if missing:
        raise RuntimeError(
            "Launch response is missing stable fields: "
            + ", ".join(sorted(missing))
            + "."
        )
    return {key: copy.deepcopy(launch[key]) for key in required}


def headless_observation_semantics(
    *,
    graph: dict[str, Any],
    navigation: dict[str, Any],
    launch: dict[str, Any],
    activity_id: str = LESSON_ACTIVITY_ID,
) -> dict[str, Any]:
    graph_identity = {
        "schema_version": graph.get("schema_version"),
        "curriculum_id": graph.get("curriculum_id"),
        "curriculum_version": graph.get("curriculum_version"),
        "graph_digest": graph.get("graph_digest"),
    }
    if graph_identity != {
        "schema_version": "1.0.0",
        "curriculum_id": CURRICULUM_ID,
        "curriculum_version": CURRICULUM_VERSION,
        "graph_digest": graph.get("graph_digest"),
    } or not isinstance(graph_identity["graph_digest"], str):
        raise RuntimeError("Headless graph identity is inconsistent.")

    navigation_semantics = stable_navigation_semantics(navigation)
    if any(
        navigation_semantics[key] != graph_identity[key]
        for key in ("curriculum_id", "curriculum_version", "graph_digest")
    ):
        raise RuntimeError("Headless navigation does not match the exact graph.")

    activities = graph.get("activities")
    if not isinstance(activities, list):
        raise RuntimeError("Headless graph activities are unavailable.")
    matching_activities = [
        item
        for item in activities
        if isinstance(item, dict) and item.get("activity_id") == activity_id
    ]
    if len(matching_activities) != 1:
        raise RuntimeError("Headless launch activity is not uniquely present.")
    reference = matching_activities[0].get("reference")
    if not isinstance(reference, dict):
        raise RuntimeError("Headless launch activity reference is unavailable.")

    states = navigation_semantics["activity_states"]
    if not isinstance(states, list):
        raise RuntimeError("Headless navigation states are unavailable.")
    matching_states = [
        item
        for item in states
        if isinstance(item, dict) and item.get("activity_id") == activity_id
    ]
    if len(matching_states) != 1 or matching_states[0].get("eligibility") != "eligible":
        raise RuntimeError("Headless launch activity is not uniquely eligible.")

    launch_semantics = _stable_launch_semantics(launch)
    expected_launch = {
        "schema_version": "1.0.0",
        "curriculum_id": graph_identity["curriculum_id"],
        "curriculum_version": graph_identity["curriculum_version"],
        "graph_digest": graph_identity["graph_digest"],
        "activity_id": activity_id,
        "placement_id": reference.get("placement_id"),
        "package_id": reference.get("package_id"),
        "package_version": reference.get("package_version"),
        "package_digest": reference.get("package_digest"),
        "destination": f"/learn/placements/{reference.get('placement_id')}",
    }
    if launch_semantics != expected_launch:
        raise RuntimeError("Headless launch does not match graph-owned facts.")

    return {
        "graph": graph_identity,
        "navigation": navigation_semantics,
        "launch": launch_semantics,
    }


def observe_headless_navigation(origin: str) -> dict[str, Any]:
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies)
    )
    _request_json(
        opener,
        origin=origin,
        path="/api/v1/session/single-profile",
        method="POST",
        payload={"limitation_acknowledged": True},
    )
    graph_path = (
        f"/api/v1/curriculum/graphs/{CURRICULUM_ID}"
        f"/versions/{CURRICULUM_VERSION}"
    )
    navigation_path = (
        f"/api/v1/adaptation/curricula/{CURRICULUM_ID}"
        f"/versions/{CURRICULUM_VERSION}/navigation-state"
    )
    launch_path = (
        f"/api/v1/adaptation/curricula/{CURRICULUM_ID}"
        f"/versions/{CURRICULUM_VERSION}/activities/"
        f"{LESSON_ACTIVITY_ID}/launch"
    )
    return headless_observation_semantics(
        graph=_request_json(opener, origin=origin, path=graph_path),
        navigation=_request_json(
            opener,
            origin=origin,
            path=navigation_path,
        ),
        launch=_request_json(opener, origin=origin, path=launch_path),
    )


def _storage_counts(connection: psycopg.Connection[Any]) -> dict[str, int]:
    row = connection.execute(COMPLETION_STORAGE_COUNTS).fetchone()
    if row is None or len(row) != 4:
        raise RuntimeError("Completion storage counts are unavailable.")
    return {
        "assessment_evidence": int(row[0]),
        "assessment_events": int(row[1]),
        "learner_projections": int(row[2]),
        "learner_history": int(row[3]),
    }


def completion_storage_counts(postgres_dsn: str) -> dict[str, int]:
    with psycopg.connect(postgres_dsn) as connection:
        return _storage_counts(connection)


def reset_rebuildable_completion_state(
    postgres_dsn: str,
) -> tuple[dict[str, int], dict[str, int]]:
    with psycopg.connect(postgres_dsn) as connection:
        before = _storage_counts(connection)
        for statement in REBUILDABLE_COMPLETION_RESET:
            connection.execute(statement)
        after = _storage_counts(connection)
    if (
        after["assessment_evidence"] != before["assessment_evidence"]
        or after["assessment_events"] != before["assessment_events"]
        or after["learner_projections"] != 0
        or after["learner_history"] != 0
    ):
        raise RuntimeError("Derived completion reset exceeded its bounded scope.")
    return before, after


def assert_replay_result(
    *,
    before_observation: dict[str, Any],
    after_observation: dict[str, Any],
    before_reset: dict[str, int],
    after_reset: dict[str, int],
    after_rebuild: dict[str, int],
) -> None:
    if before_observation != after_observation:
        raise RuntimeError("Navigation semantics changed after projection replay.")
    if before_reset["assessment_evidence"] < 1 or before_reset[
        "assessment_events"
    ] < 1:
        raise RuntimeError("Replay qualification requires retained Assessment evidence.")
    if before_reset["learner_projections"] < 1 or before_reset[
        "learner_history"
    ] < 1:
        raise RuntimeError("Replay qualification requires an initial projection.")
    if after_reset["learner_projections"] != 0 or after_reset[
        "learner_history"
    ] != 0:
        raise RuntimeError("Derived completion rows were not fully reset.")
    if (
        after_rebuild["assessment_evidence"]
        != before_reset["assessment_evidence"]
        or after_rebuild["assessment_events"]
        != before_reset["assessment_events"]
    ):
        raise RuntimeError("Assessment evidence changed during projection replay.")
    if after_rebuild["learner_projections"] < 1 or after_rebuild[
        "learner_history"
    ] < 1:
        raise RuntimeError("Learner-model projection replay did not rebuild state.")


def npm_e2e_command() -> list[str]:
    node = os.environ.get("FINANCIAL_AI_ACADEMY_NODE_EXECUTABLE")
    npm_cli = os.environ.get("FINANCIAL_AI_ACADEMY_NPM_CLI")
    if bool(node) != bool(npm_cli):
        raise RuntimeError(
            "Set both FINANCIAL_AI_ACADEMY_NODE_EXECUTABLE and "
            "FINANCIAL_AI_ACADEMY_NPM_CLI, or neither."
        )
    npm_executable = shutil.which("npm")
    if not node and npm_executable is None:
        raise RuntimeError(
            "npm is not available on PATH; alternatively set both "
            "FINANCIAL_AI_ACADEMY_NODE_EXECUTABLE and "
            "FINANCIAL_AI_ACADEMY_NPM_CLI."
        )
    prefix = [npm_executable] if not node else [node, npm_cli]
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
    primary_error: BaseException | None = None

    try:
        if external_dsn:
            postgres_dsn = external_dsn
            postgres_topology = "externally managed isolated PostgreSQL"
        else:
            container_name, postgres_dsn = start_postgres()
            postgres_topology = f"{POSTGRES_IMAGE} isolated container"

        application = start_application(
            postgres_dsn=postgres_dsn,
            data_root=data_root / "application-data",
            port=port,
            application_log=application_log,
            seed_fixture=True,
        )

        environment = os.environ.copy()
        environment["FINANCIAL_AI_ACADEMY_E2E_BASE_URL"] = origin
        run_checked(npm_e2e_command(), env=environment)

        before_observation = observe_headless_navigation(origin)
        stop_application(application)
        application = None
        before_reset, after_reset = reset_rebuildable_completion_state(
            postgres_dsn
        )
        application = start_application(
            postgres_dsn=postgres_dsn,
            data_root=data_root / "application-data",
            port=port,
            application_log=application_log,
            seed_fixture=False,
        )
        after_observation = observe_headless_navigation(origin)
        after_rebuild = completion_storage_counts(postgres_dsn)
        assert_replay_result(
            before_observation=before_observation,
            after_observation=after_observation,
            before_reset=before_reset,
            after_reset=after_reset,
            after_rebuild=after_rebuild,
        )

        report = {
            "browser": "Playwright pinned Chromium",
            "catalog": (
                "three deterministic lesson opportunities registered and "
                "projected through public Curriculum operations, then "
                "qualified through catalog, detail, ordered comparison, "
                "and exact lesson routes"
            ),
            "database": postgres_topology,
            "filesystem": "isolated temporary data root",
            "fixture": "intro-risk-return@1.1.0 with risk-return-check-1@1.0.0",
            "curriculum_graph": (
                "investing-foundations@1.0.0 and @1.1.0 published through "
                "public Curriculum operations and qualified through exact "
                "API, list, map, provenance, denial, coexistence, and "
                "missing-version paths"
            ),
            "activity_launch": (
                "protected exact-version API and generated browser client "
                "qualified for start, review, exact lesson destination, "
                "return context, bounded denial, and current-position display"
            ),
            "navigation_state": (
                "deterministic-prerequisite-baseline@1.0.0 qualified "
                "through the protected exact-version API, same-context "
                "lesson-completion transition, complete graph-ordered "
                "activity closure, list/map parity, bounded assessment "
                "unavailability, selector denial, provenance digests, and "
                "exact-source completion reuse without changed-placement "
                "inheritance"
            ),
            "http_origin": origin,
            "production_application_process": Path(sys.executable).name,
            "projection_replay": {
                "assessment_source_preserved": True,
                "headless_public_api": True,
                "learner_history_rows": after_rebuild["learner_history"],
                "learner_projection_rows": after_rebuild[
                    "learner_projections"
                ],
                "normal_restart_without_reseeding": True,
                "stable_navigation_semantics": True,
            },
            "query_corpus": (
                "one available exact lesson plus planned and unavailable "
                "synthetic classifications"
            ),
            "static_index_sha256": hashlib.sha256(
                web_index.read_bytes()
            ).hexdigest(),
            "static_serving": "same-origin Python application",
        }
        print(json.dumps(report, indent=2, sort_keys=True))
    except BaseException as error:
        primary_error = error
        try:
            if application_log.is_file():
                diagnostics = application_log.read_text(
                    encoding="utf-8", errors="replace"
                )
                if external_dsn:
                    diagnostics = diagnostics.replace(
                        external_dsn,
                        "<redacted-dsn>",
                    )
                print(diagnostics[-4000:], file=sys.stderr)
        except Exception as diagnostic_error:
            error.add_note(
                "Qualification diagnostic collection also failed "
                f"({type(diagnostic_error).__name__})."
            )
    cleanup_failures = cleanup_qualification(
        application=application,
        container_name=container_name,
        data_root=data_root,
    )
    finish_after_cleanup(primary_error, cleanup_failures)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
