"""Run the isolated approved-lesson cross-system qualification."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import hashlib
import http.cookiejar
import json
import os
import re
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
from uuid import UUID, uuid4

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
PRACTICE_PLACEMENT_ID = "intro-risk-return-practice"
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
PRACTICE_OPEN_STORAGE_COUNTS = """
    SELECT
        (SELECT count(*) FROM assessment.attempts),
        (SELECT count(*) FROM assessment.responses),
        (SELECT count(*) FROM assessment.scores),
        (SELECT count(*) FROM assessment.completion_evidence),
        (SELECT count(*) FROM assessment.outbox),
        (SELECT count(*)
           FROM learner_model.lesson_completion_projections),
        (SELECT count(*)
           FROM learner_model.lesson_completion_history)
"""
PRACTICE_SUBMISSION_STORAGE = """
    SELECT
        (SELECT count(*) FROM assessment.practice_attempts),
        (SELECT count(*) FROM assessment.practice_responses),
        (SELECT count(*) FROM assessment.practice_scores),
        (SELECT count(*) FROM assessment.practice_completion_evidence),
        (SELECT count(*) FROM assessment.practice_outbox),
        COALESCE((SELECT min(submission_id::text)
                    FROM assessment.practice_attempts), ''),
        COALESCE((SELECT min(attempt_id::text)
                    FROM assessment.practice_attempts), ''),
        COALESCE((SELECT min(evidence_id::text)
                    FROM assessment.practice_completion_evidence), '')
"""
PRIVATE_PRACTICE_FIELDS = frozenset(
    {
        "answer",
        "correct_option_id",
        "correct_option_ids",
        "feedback",
        "scoring_policy",
    }
)
SUPPORTED_PRACTICE_ITEM_TYPES = frozenset(
    {"single_select", "multiple_select", "numeric_entry"}
)
PRACTICE_SUBMISSION_ROOT_KEYS = frozenset(
    {
        "schema_version",
        "submission_id",
        "placement_id",
        "package_id",
        "package_version",
        "package_digest",
        "definition_digest",
        "practice_id",
        "practice_version",
        "attempt_policy_id",
        "attempt_policy_version",
        "responses",
    }
)
PRACTICE_RESULT_ROOT_KEYS = frozenset(
    {
        "schema_version",
        "attempt_id",
        "evidence_id",
        "submission_id",
        "placement_id",
        "package_id",
        "package_version",
        "package_digest",
        "definition_digest",
        "practice_id",
        "practice_version",
        "attempt_policy_id",
        "attempt_policy_version",
        "score",
        "max_score",
        "outcome",
        "review_reference_ids",
        "item_results",
        "submitted_at",
    }
)
PRACTICE_RESPONSE_COMMON_KEYS = frozenset(
    {
        "item_id",
        "item_version",
        "item_type",
        "scoring_policy_id",
        "scoring_policy_version",
    }
)
PRACTICE_RESULT_COMMON_KEYS = PRACTICE_RESPONSE_COMMON_KEYS | frozenset(
    {"score", "max_score", "correct", "feedback"}
)
PRACTICE_SCOPE_KEYS = frozenset(
    {
        "schema_version",
        "placement_id",
        "package_id",
        "package_version",
        "package_digest",
        "definition_digest",
        "practice_id",
        "practice_version",
        "attempt_policy_id",
        "attempt_policy_version",
    }
)
PRACTICE_DRAFT_SAVE_ROOT_KEYS = PRACTICE_SCOPE_KEYS | frozenset(
    {"expected_revision", "responses"}
)
PRACTICE_DRAFT_ROOT_KEYS = PRACTICE_SCOPE_KEYS | frozenset(
    {"responses", "revision", "saved_at", "response_fingerprint"}
)
PRACTICE_RETRY_ROOT_KEYS = PRACTICE_SCOPE_KEYS | frozenset(
    {
        "attempts_used",
        "max_attempts",
        "attempts_remaining",
        "can_retry",
        "state",
    }
)
PRACTICE_HISTORY_ROOT_KEYS = PRACTICE_SCOPE_KEYS | frozenset(
    {"source_digest", "attempts"}
)
PRACTICE_HISTORY_ATTEMPT_KEYS = frozenset(
    {
        "attempt_order",
        "event_id",
        "attempt_id",
        "evidence_id",
        "submission_id",
        "score",
        "max_score",
        "outcome",
        "item_summaries",
        "completed_at",
    }
)
PRACTICE_HISTORY_ITEM_KEYS = PRACTICE_RESPONSE_COMMON_KEYS | frozenset(
    {"score", "max_score", "correct", "review_reference_ids"}
)
PRACTICE_PROGRESS_ROOT_KEYS = frozenset(
    {
        "schema_version",
        "placement_id",
        "draft",
        "retry_state",
        "history",
        "review_targets",
    }
)
PRACTICE_REVIEW_TARGET_COMMON_KEYS = frozenset(
    {
        "schema_version",
        "practice_placement_id",
        "resource_id",
        "resource_version",
        "resource_digest",
        "resource_title",
        "state",
    }
)
PRACTICE_REVIEW_DESTINATION_KEYS = frozenset(
    {"placement_id", "package_id", "package_version", "package_digest"}
)
PRIVATE_PRACTICE_RESULT_FIELDS = frozenset(
    {
        "answer",
        "correct_option_id",
        "correct_option_ids",
        "evaluator",
        "learner_id",
        "request_fingerprint",
        "scoring_policy",
    }
)
UTC_TIMESTAMP = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?Z$"
)


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


def _request_json_status(
    opener: urllib.request.OpenerDirector,
    *,
    origin: str,
    path: str,
    method: str,
    payload: dict[str, object],
) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(
        f"{origin}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": origin,
            "Sec-Fetch-Site": "same-origin",
        },
        method=method,
    )
    try:
        response = opener.open(request, timeout=10)
    except urllib.error.HTTPError as error:
        status = error.code
        raw = error.read()
    else:
        with response:
            status = response.status
            raw = response.read()
    document = json.loads(raw.decode("utf-8"))
    if not isinstance(document, dict):
        raise RuntimeError(
            f"Headless API request returned a non-object: {method} {path}."
        )
    return status, document


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


def _nested_mapping_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for nested in value.values():
            keys.update(_nested_mapping_keys(nested))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for nested in value:
            keys.update(_nested_mapping_keys(nested))
        return keys
    return set()


def stable_practice_semantics(practice: dict[str, Any]) -> dict[str, Any]:
    required = (
        "schema_version",
        "placement_id",
        "package_id",
        "package_version",
        "package_digest",
        "practice_id",
        "practice_version",
        "definition_digest",
        "title",
        "purpose",
        "instructions",
        "attempt_policy",
        "source_references",
        "review_references",
        "items",
    )
    missing = [key for key in required if key not in practice]
    if missing:
        raise RuntimeError(
            "Practice response is missing stable fields: "
            + ", ".join(sorted(missing))
            + "."
        )
    if practice["placement_id"] != PRACTICE_PLACEMENT_ID:
        raise RuntimeError("Headless practice does not match the exact placement.")
    items = practice["items"]
    if not isinstance(items, list) or not 1 <= len(items) <= 20:
        raise RuntimeError("Headless practice has an invalid item collection.")
    unsupported = [
        item.get("item_type") if isinstance(item, dict) else None
        for item in items
        if not isinstance(item, dict)
        or item.get("item_type") not in SUPPORTED_PRACTICE_ITEM_TYPES
    ]
    if unsupported:
        raise RuntimeError(
            "Headless practice contains unsupported item types: "
            + ", ".join(str(item_type) for item_type in unsupported)
            + "."
        )
    leaked = PRIVATE_PRACTICE_FIELDS & _nested_mapping_keys(practice)
    if leaked:
        raise RuntimeError(
            "Headless practice exposed private fields: "
            + ", ".join(sorted(leaked))
            + "."
        )
    return {key: copy.deepcopy(practice[key]) for key in required}


def assert_practice_fixture_coverage(practice: dict[str, Any]) -> None:
    observed = {
        item["item_type"]
        for item in practice["items"]
        if isinstance(item, dict) and "item_type" in item
    }
    missing = SUPPORTED_PRACTICE_ITEM_TYPES - observed
    if missing:
        raise RuntimeError(
            "Qualification practice does not cover supported item types: "
            + ", ".join(sorted(missing))
            + "."
        )


def observe_headless_practice(origin: str) -> dict[str, Any]:
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
    practice_path = (
        f"/api/v1/curriculum/placements/{PRACTICE_PLACEMENT_ID}/practice"
    )
    first = stable_practice_semantics(
        _request_json(opener, origin=origin, path=practice_path)
    )
    repeated = stable_practice_semantics(
        _request_json(opener, origin=origin, path=practice_path)
    )
    if repeated != first:
        raise RuntimeError("Repeated headless practice reads changed meaning.")
    assert_practice_fixture_coverage(first)
    return first


def practice_open_storage_counts(postgres_dsn: str) -> dict[str, int]:
    with psycopg.connect(postgres_dsn) as connection:
        row = connection.execute(PRACTICE_OPEN_STORAGE_COUNTS).fetchone()
    if row is None:
        raise RuntimeError("Practice storage counts are unavailable.")
    labels = (
        "assessment_attempts",
        "assessment_responses",
        "assessment_scores",
        "assessment_completion_evidence",
        "assessment_events",
        "learner_projections",
        "learner_history",
    )
    return dict(zip(labels, (int(value) for value in row), strict=True))


def observe_side_effect_free_practice(
    *,
    origin: str,
    postgres_dsn: str,
) -> dict[str, Any]:
    before = practice_open_storage_counts(postgres_dsn)
    observation = observe_headless_practice(origin)
    after = practice_open_storage_counts(postgres_dsn)
    if after != before:
        raise RuntimeError("Practice opening created learner evidence or state.")
    return observation


def assert_practice_restart_result(
    *,
    before_restart: dict[str, Any],
    after_restart: dict[str, Any],
) -> None:
    if after_restart != before_restart:
        raise RuntimeError("Practice presentation changed after normal restart.")


def _exact_keys(
    value: dict[str, Any],
    expected: frozenset[str],
    label: str,
) -> None:
    if set(value) != expected:
        raise RuntimeError(f"{label} does not match the closed public contract.")


def _practice_response_keys(item_type: str) -> frozenset[str]:
    if item_type == "single_select":
        return PRACTICE_RESPONSE_COMMON_KEYS | {"selected_option_id"}
    if item_type == "multiple_select":
        return PRACTICE_RESPONSE_COMMON_KEYS | {"selected_option_ids"}
    if item_type == "numeric_entry":
        return PRACTICE_RESPONSE_COMMON_KEYS | {"entered_value"}
    raise RuntimeError("Practice submission contains an unsupported response type.")


def _canonical_practice_responses(
    responses: object,
    *,
    label: str,
) -> tuple[tuple[str, str], ...]:
    if not isinstance(responses, list) or len(responses) > 20:
        raise RuntimeError(f"{label} has an invalid response collection.")
    item_ids: set[str] = set()
    canonical: list[tuple[str, str]] = []
    for response in responses:
        if not isinstance(response, dict):
            raise RuntimeError(f"{label} response is not an object.")
        item_type = response.get("item_type")
        if not isinstance(item_type, str):
            raise RuntimeError(f"{label} response type is missing.")
        _exact_keys(response, _practice_response_keys(item_type), f"{label} response")
        item_id = response.get("item_id")
        if not isinstance(item_id, str) or item_id in item_ids:
            raise RuntimeError(f"{label} item IDs are invalid or duplicated.")
        item_ids.add(item_id)
        normalized = copy.deepcopy(response)
        if item_type == "multiple_select":
            selected = normalized["selected_option_ids"]
            if (
                not isinstance(selected, list)
                or not selected
                or len(selected) != len(set(selected))
            ):
                raise RuntimeError(f"{label} selection set is invalid.")
            normalized["selected_option_ids"] = sorted(selected)
        canonical.append(
            (
                item_id,
                json.dumps(normalized, sort_keys=True, separators=(",", ":")),
            )
        )
    return tuple(sorted(canonical))


def _canonical_utc(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not UTC_TIMESTAMP.fullmatch(value):
        raise RuntimeError(f"{label} is not canonical UTC.")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise RuntimeError(f"{label} is not a real date.") from None
    return value


def _assert_same_practice_scope(
    document: dict[str, Any],
    expected: dict[str, Any],
    *,
    label: str,
) -> None:
    for key in PRACTICE_SCOPE_KEYS:
        if document.get(key) != expected.get(key):
            raise RuntimeError(f"{label} changed the practice {key}.")


def stable_practice_draft_save(document: dict[str, Any]) -> dict[str, Any]:
    _exact_keys(document, PRACTICE_DRAFT_SAVE_ROOT_KEYS, "Practice draft save")
    if document["placement_id"] != PRACTICE_PLACEMENT_ID:
        raise RuntimeError("Practice draft save does not match the exact placement.")
    expected_revision = document["expected_revision"]
    if type(expected_revision) is not int or expected_revision < 0:
        raise RuntimeError("Practice draft save has an invalid expected revision.")
    _canonical_practice_responses(document["responses"], label="Practice draft save")
    return copy.deepcopy(document)


def stable_practice_draft(
    document: dict[str, Any],
    *,
    save: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _exact_keys(document, PRACTICE_DRAFT_ROOT_KEYS, "Practice draft")
    if document["placement_id"] != PRACTICE_PLACEMENT_ID:
        raise RuntimeError("Practice draft does not match the exact placement.")
    revision = document["revision"]
    if type(revision) is not int or revision < 1:
        raise RuntimeError("Practice draft has an invalid revision.")
    fingerprint = document["response_fingerprint"]
    if not isinstance(fingerprint, str) or not re.fullmatch(r"[a-f0-9]{64}", fingerprint):
        raise RuntimeError("Practice draft has an invalid response fingerprint.")
    _canonical_utc(document["saved_at"], label="Practice draft timestamp")
    canonical = _canonical_practice_responses(
        document["responses"], label="Practice draft"
    )
    if save is not None:
        stable_save = stable_practice_draft_save(save)
        _assert_same_practice_scope(document, stable_save, label="Practice draft")
        if canonical != _canonical_practice_responses(
            stable_save["responses"], label="Practice draft save"
        ):
            raise RuntimeError("Practice draft changed the saved responses.")
        if revision < max(1, stable_save["expected_revision"]):
            raise RuntimeError("Practice draft revision precedes the requested state.")
    return copy.deepcopy(document)


def stable_practice_progress(
    document: dict[str, Any],
    *,
    expected_submission: dict[str, Any] | None = None,
    expected_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _exact_keys(document, PRACTICE_PROGRESS_ROOT_KEYS, "Practice progress")
    if document["schema_version"] != "1.0.0":
        raise RuntimeError("Practice progress schema version changed.")
    if document["placement_id"] != PRACTICE_PLACEMENT_ID:
        raise RuntimeError("Practice progress does not match the exact placement.")
    leaked = PRIVATE_PRACTICE_RESULT_FIELDS & _nested_mapping_keys(document)
    if leaked:
        raise RuntimeError("Practice progress exposed private fields.")

    retry = document["retry_state"]
    history = document["history"]
    targets = document["review_targets"]
    if not isinstance(retry, dict) or not isinstance(history, dict):
        raise RuntimeError("Practice progress state is not an object.")
    if not isinstance(targets, list) or len(targets) > 8:
        raise RuntimeError("Practice progress review targets are invalid.")
    _exact_keys(retry, PRACTICE_RETRY_ROOT_KEYS, "Practice retry state")
    _exact_keys(history, PRACTICE_HISTORY_ROOT_KEYS, "Practice history")
    _assert_same_practice_scope(history, retry, label="Practice history")
    if retry["placement_id"] != PRACTICE_PLACEMENT_ID:
        raise RuntimeError("Practice retry state does not match the placement.")

    for key in ("attempts_used", "max_attempts", "attempts_remaining"):
        if type(retry[key]) is not int:
            raise RuntimeError("Practice retry counts are not integers.")
    used = retry["attempts_used"]
    maximum = retry["max_attempts"]
    remaining = retry["attempts_remaining"]
    if not (0 <= used <= maximum <= 10) or remaining != maximum - used:
        raise RuntimeError("Practice retry counts are incoherent.")
    can_retry = remaining > 0
    if retry["can_retry"] is not can_retry or retry["state"] != (
        "available" if can_retry else "exhausted"
    ):
        raise RuntimeError("Practice retry eligibility is incoherent.")

    attempts = history["attempts"]
    if not isinstance(attempts, list) or len(attempts) != used:
        raise RuntimeError("Practice history does not match attempts used.")
    if not isinstance(history["source_digest"], str) or not re.fullmatch(
        r"[a-f0-9]{64}", history["source_digest"]
    ):
        raise RuntimeError("Practice history source digest is invalid.")
    latest_incorrect_references: list[str] = []
    for index, attempt in enumerate(attempts, start=1):
        if not isinstance(attempt, dict):
            raise RuntimeError("Practice history attempt is not an object.")
        _exact_keys(attempt, PRACTICE_HISTORY_ATTEMPT_KEYS, "Practice history attempt")
        if attempt["attempt_order"] != index:
            raise RuntimeError("Practice history attempt order is not gap-free.")
        for key in ("event_id", "attempt_id", "evidence_id", "submission_id"):
            try:
                UUID(str(attempt[key]))
            except (TypeError, ValueError, AttributeError):
                raise RuntimeError(f"Practice history has an invalid {key}.") from None
        _canonical_utc(attempt["completed_at"], label="Practice history timestamp")
        summaries = attempt["item_summaries"]
        if not isinstance(summaries, list) or not 1 <= len(summaries) <= 20:
            raise RuntimeError("Practice history item summaries are invalid.")
        item_ids: set[str] = set()
        score = 0
        max_score = 0
        incorrect_references: list[str] = []
        for summary in summaries:
            if not isinstance(summary, dict):
                raise RuntimeError("Practice history item summary is not an object.")
            _exact_keys(summary, PRACTICE_HISTORY_ITEM_KEYS, "Practice history item")
            item_id = summary.get("item_id")
            item_type = summary.get("item_type")
            if (
                not isinstance(item_id, str)
                or item_id in item_ids
                or item_type not in SUPPORTED_PRACTICE_ITEM_TYPES
            ):
                raise RuntimeError("Practice history item identity is invalid.")
            item_ids.add(item_id)
            if type(summary["score"]) is not int or summary["max_score"] != 1:
                raise RuntimeError("Practice history item score is invalid.")
            if summary["correct"] is not (summary["score"] == summary["max_score"]):
                raise RuntimeError("Practice history item correctness is incoherent.")
            references = summary["review_reference_ids"]
            if (
                not isinstance(references, list)
                or len(references) > 8
                or len(references) != len(set(references))
            ):
                raise RuntimeError("Practice history review references are invalid.")
            score += summary["score"]
            max_score += summary["max_score"]
            if not summary["correct"]:
                for reference in references:
                    if reference not in incorrect_references:
                        incorrect_references.append(reference)
        if attempt["score"] != score or attempt["max_score"] != max_score:
            raise RuntimeError("Practice history totals do not match item summaries.")
        if attempt["outcome"] != (
            "all_correct" if score == max_score else "review_needed"
        ):
            raise RuntimeError("Practice history outcome is incoherent.")
        latest_incorrect_references = incorrect_references

    resource_ids: list[str] = []
    for target in targets:
        if not isinstance(target, dict):
            raise RuntimeError("Practice review target is not an object.")
        state = target.get("state")
        expected_keys = PRACTICE_REVIEW_TARGET_COMMON_KEYS | (
            {"destination"} if state == "available" else {"unavailable_reason"}
        )
        _exact_keys(target, frozenset(expected_keys), "Practice review target")
        if target["practice_placement_id"] != PRACTICE_PLACEMENT_ID:
            raise RuntimeError("Practice review target changed the placement.")
        resource_id = target["resource_id"]
        if not isinstance(resource_id, str) or resource_id in resource_ids:
            raise RuntimeError("Practice review target identity is invalid.")
        resource_ids.append(resource_id)
        if state == "available":
            destination = target["destination"]
            if not isinstance(destination, dict):
                raise RuntimeError("Practice review destination is not an object.")
            destination_keys = frozenset(destination)
            if destination_keys not in {
                PRACTICE_REVIEW_DESTINATION_KEYS,
                PRACTICE_REVIEW_DESTINATION_KEYS | {"section_id"},
            }:
                raise RuntimeError("Practice review destination is not closed.")
            if (
                "section_id" in destination
                and destination["section_id"] is not None
                and not isinstance(destination["section_id"], str)
            ):
                raise RuntimeError("Practice review section is invalid.")
        elif state != "unavailable":
            raise RuntimeError("Practice review target state is invalid.")
    if resource_ids != latest_incorrect_references:
        raise RuntimeError("Practice review targets do not match latest incorrect evidence.")

    draft = document["draft"]
    if draft is not None:
        if not isinstance(draft, dict):
            raise RuntimeError("Practice progress draft is not an object.")
        stable_practice_draft(draft)
        _assert_same_practice_scope(draft, retry, label="Practice progress draft")

    if expected_submission is not None or expected_result is not None:
        if expected_submission is None or expected_result is None:
            raise RuntimeError("Practice progress correlation requires request and result.")
        stable_submission = stable_practice_submission(expected_submission)
        stable_result = stable_practice_submission_result(
            expected_result, stable_submission
        )
        if draft is not None:
            raise RuntimeError("Accepted practice submission did not clear its draft.")
        if len(attempts) != 1:
            raise RuntimeError("Captured practice progress does not contain one attempt.")
        attempt = attempts[0]
        for key in ("attempt_id", "evidence_id", "submission_id", "score", "max_score", "outcome"):
            if attempt[key] != stable_result[key]:
                raise RuntimeError(f"Practice history changed the result {key}.")
        result_items = {
            item["item_id"]: item for item in stable_result["item_results"]
        }
        for item in attempt["item_summaries"]:
            source = result_items.get(item["item_id"])
            if source is None:
                raise RuntimeError("Practice history contains an unknown result item.")
            for key in PRACTICE_HISTORY_ITEM_KEYS - {"review_reference_ids"}:
                if item[key] != source[key]:
                    raise RuntimeError("Practice history changed result item evidence.")
            expected_references = [] if source["correct"] else source["feedback"][
                "review_reference_ids"
            ]
            if item["review_reference_ids"] != expected_references:
                raise RuntimeError("Practice history changed review evidence.")
    return copy.deepcopy(document)


def stable_practice_submission(document: dict[str, Any]) -> dict[str, Any]:
    _exact_keys(document, PRACTICE_SUBMISSION_ROOT_KEYS, "Practice submission")
    if document["placement_id"] != PRACTICE_PLACEMENT_ID:
        raise RuntimeError("Practice submission does not match the exact placement.")
    try:
        UUID(str(document["submission_id"]))
    except (TypeError, ValueError, AttributeError):
        raise RuntimeError("Practice submission has an invalid public ID.") from None
    responses = document["responses"]
    if not isinstance(responses, list) or not 1 <= len(responses) <= 20:
        raise RuntimeError("Practice submission has an invalid response collection.")
    item_ids: set[str] = set()
    for response in responses:
        if not isinstance(response, dict):
            raise RuntimeError("Practice submission response is not an object.")
        item_type = response.get("item_type")
        if not isinstance(item_type, str):
            raise RuntimeError("Practice submission response type is missing.")
        _exact_keys(
            response,
            _practice_response_keys(item_type),
            "Practice submission response",
        )
        item_id = response.get("item_id")
        if not isinstance(item_id, str) or item_id in item_ids:
            raise RuntimeError("Practice submission item IDs are invalid or duplicated.")
        item_ids.add(item_id)
        if item_type == "multiple_select":
            selected = response["selected_option_ids"]
            if (
                not isinstance(selected, list)
                or not selected
                or len(selected) != len(set(selected))
            ):
                raise RuntimeError("Practice submission selection set is invalid.")
    return copy.deepcopy(document)


def stable_practice_submission_result(
    document: dict[str, Any],
    submission: dict[str, Any],
) -> dict[str, Any]:
    _exact_keys(document, PRACTICE_RESULT_ROOT_KEYS, "Practice result")
    leaked = PRIVATE_PRACTICE_RESULT_FIELDS & _nested_mapping_keys(document)
    if leaked:
        raise RuntimeError(
            "Practice result exposed private fields: "
            + ", ".join(sorted(leaked))
            + "."
        )
    for identifier in ("attempt_id", "evidence_id", "submission_id"):
        try:
            UUID(str(document[identifier]))
        except (TypeError, ValueError, AttributeError):
            raise RuntimeError(f"Practice result has an invalid {identifier}.") from None
    timestamp = document["submitted_at"]
    if not isinstance(timestamp, str) or not UTC_TIMESTAMP.fullmatch(timestamp):
        raise RuntimeError("Practice result timestamp is not canonical UTC.")
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        raise RuntimeError("Practice result timestamp is not a real date.") from None
    for selector in (
        "submission_id",
        "placement_id",
        "package_id",
        "package_version",
        "package_digest",
        "definition_digest",
        "practice_id",
        "practice_version",
        "attempt_policy_id",
        "attempt_policy_version",
    ):
        if document[selector] != submission[selector]:
            raise RuntimeError(f"Practice result changed the submitted {selector}.")
    submitted = {
        str(response["item_id"]): response for response in submission["responses"]
    }
    item_results = document["item_results"]
    if not isinstance(item_results, list) or len(item_results) != len(submitted):
        raise RuntimeError("Practice result does not close every submitted item.")
    result_ids: set[str] = set()
    score = 0
    maximum = 0
    for result in item_results:
        if not isinstance(result, dict):
            raise RuntimeError("Practice item result is not an object.")
        item_type = result.get("item_type")
        if not isinstance(item_type, str):
            raise RuntimeError("Practice item result type is missing.")
        _exact_keys(
            result,
            PRACTICE_RESULT_COMMON_KEYS
            | (_practice_response_keys(item_type) - PRACTICE_RESPONSE_COMMON_KEYS),
            "Practice item result",
        )
        item_id = result.get("item_id")
        if not isinstance(item_id, str) or item_id in result_ids:
            raise RuntimeError("Practice result item IDs are invalid or duplicated.")
        result_ids.add(item_id)
        original = submitted.get(item_id)
        if original is None:
            raise RuntimeError("Practice result contains an unknown item.")
        for key in _practice_response_keys(item_type):
            if result[key] != original[key]:
                raise RuntimeError("Practice result changed a submitted response.")
        feedback = result["feedback"]
        if not isinstance(feedback, dict):
            raise RuntimeError("Practice result feedback is not an object.")
        _exact_keys(
            feedback,
            frozenset({"feedback_id", "text", "review_reference_ids"}),
            "Practice result feedback",
        )
        if type(result["score"]) is not int or type(result["max_score"]) is not int:
            raise RuntimeError("Practice item scores are not integers.")
        score += result["score"]
        maximum += result["max_score"]
    if result_ids != set(submitted):
        raise RuntimeError("Practice result omitted a submitted item.")
    if document["score"] != score or document["max_score"] != maximum:
        raise RuntimeError("Practice result totals do not match item results.")
    expected_outcome = "all_correct" if score == maximum else "review_needed"
    if document["outcome"] != expected_outcome:
        raise RuntimeError("Practice result outcome does not match its score.")
    return copy.deepcopy(document)


def load_practice_submission_capture(
    path: Path,
    *,
    data_root: Path,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("The bounded practice submission capture is absent.")
    resolved = path.resolve()
    if resolved.parent != data_root.resolve() or resolved.stat().st_size > 262_144:
        raise RuntimeError("Practice submission capture escaped its bounded root.")
    capture = json.loads(resolved.read_text(encoding="utf-8"))
    expected_capture_keys = {
        "draft_request",
        "draft_result",
        "request",
        "result",
        "progress",
    }
    if not isinstance(capture, dict) or set(capture) != expected_capture_keys:
        raise RuntimeError("Practice submission capture has an invalid shape.")
    draft_request = capture["draft_request"]
    draft_result = capture["draft_result"]
    request = capture["request"]
    result = capture["result"]
    progress = capture["progress"]
    if not all(
        isinstance(document, dict)
        for document in (draft_request, draft_result, request, result, progress)
    ):
        raise RuntimeError("Practice submission capture documents must be objects.")
    stable_draft_request = stable_practice_draft_save(draft_request)
    stable_draft_result = stable_practice_draft(
        draft_result,
        save=stable_draft_request,
    )
    stable_request = stable_practice_submission(request)
    stable_result = stable_practice_submission_result(result, stable_request)
    stable_progress = stable_practice_progress(
        progress,
        expected_submission=stable_request,
        expected_result=stable_result,
    )
    return (
        stable_draft_request,
        stable_draft_result,
        stable_request,
        stable_result,
        stable_progress,
    )


def _conflicting_practice_submission(
    submission: dict[str, Any],
) -> dict[str, Any]:
    changed = copy.deepcopy(submission)
    for response in changed["responses"]:
        if response["item_type"] == "single_select":
            response["selected_option_id"] = (
                "guarantee"
                if response["selected_option_id"] != "guarantee"
                else "uncertainty"
            )
            return changed
    raise RuntimeError("Qualification needs one single-select response.")


def _assert_safe_practice_denial(
    status: int,
    document: dict[str, Any],
    *,
    expected_status: int,
    expected_code: str,
) -> None:
    if status != expected_status or document.get("code") != expected_code:
        raise RuntimeError(
            f"Practice denial changed: expected {expected_status} {expected_code}."
        )
    leaked = PRIVATE_PRACTICE_RESULT_FIELDS & _nested_mapping_keys(document)
    if leaked:
        raise RuntimeError("Practice denial exposed private fields.")


def observe_headless_practice_submission(
    *,
    origin: str,
    submission: dict[str, Any],
    expected_result: dict[str, Any],
) -> dict[str, Any]:
    request = stable_practice_submission(submission)
    expected = stable_practice_submission_result(expected_result, request)
    submission_path = (
        f"/api/v1/curriculum/placements/{PRACTICE_PLACEMENT_ID}"
        "/practice/submissions"
    )
    unauthenticated = urllib.request.build_opener()
    status, denial = _request_json_status(
        unauthenticated,
        origin=origin,
        path=submission_path,
        method="POST",
        payload=request,
    )
    _assert_safe_practice_denial(
        status,
        denial,
        expected_status=401,
        expected_code="unauthorized",
    )

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
    replay = stable_practice_submission_result(
        _request_json(
            opener,
            origin=origin,
            path=submission_path,
            method="POST",
            payload=request,
        ),
        request,
    )
    if replay != expected:
        raise RuntimeError("Headless exact replay changed the saved result.")

    status, denial = _request_json_status(
        opener,
        origin=origin,
        path=submission_path,
        method="POST",
        payload=_conflicting_practice_submission(request),
    )
    _assert_safe_practice_denial(
        status,
        denial,
        expected_status=409,
        expected_code="conflict",
    )
    return replay


def _supported_practice_opener(origin: str) -> object:
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
    return opener


def read_headless_practice_progress(origin: str) -> dict[str, Any]:
    opener = _supported_practice_opener(origin)
    progress_path = (
        f"/api/v1/curriculum/placements/{PRACTICE_PLACEMENT_ID}"
        "/practice/progress"
    )
    return stable_practice_progress(
        _request_json(opener, origin=origin, path=progress_path)
    )


def replay_headless_practice_draft(
    *,
    origin: str,
    save: dict[str, Any],
) -> dict[str, Any]:
    opener = _supported_practice_opener(origin)
    draft_path = (
        f"/api/v1/curriculum/placements/{PRACTICE_PLACEMENT_ID}"
        "/practice/draft"
    )
    stable_save = stable_practice_draft_save(save)
    return stable_practice_draft(
        _request_json(
            opener,
            origin=origin,
            path=draft_path,
            method="PUT",
            payload=stable_save,
        ),
        save=stable_save,
    )


def observe_headless_practice_progress(
    *,
    origin: str,
    expected_progress: dict[str, Any],
    draft_save: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    expected = stable_practice_progress(expected_progress)
    stable_save = stable_practice_draft_save(draft_save)
    opener = _supported_practice_opener(origin)
    progress_path = (
        f"/api/v1/curriculum/placements/{PRACTICE_PLACEMENT_ID}"
        "/practice/progress"
    )
    draft_path = (
        f"/api/v1/curriculum/placements/{PRACTICE_PLACEMENT_ID}"
        "/practice/draft"
    )
    first = stable_practice_progress(
        _request_json(opener, origin=origin, path=progress_path)
    )
    if first != expected:
        raise RuntimeError("Headless progress changed browser-observed meaning.")

    saved = stable_practice_draft(
        _request_json(
            opener,
            origin=origin,
            path=draft_path,
            method="PUT",
            payload=stable_save,
        ),
        save=stable_save,
    )
    replayed = stable_practice_draft(
        _request_json(
            opener,
            origin=origin,
            path=draft_path,
            method="PUT",
            payload=stable_save,
        ),
        save=stable_save,
    )
    if replayed != saved:
        raise RuntimeError("Exact practice draft replay changed saved meaning.")

    conflict = copy.deepcopy(stable_save)
    changed = False
    for response in conflict["responses"]:
        if response["item_type"] == "single_select":
            response["selected_option_id"] = (
                "guarantee"
                if response["selected_option_id"] != "guarantee"
                else "uncertainty"
            )
            changed = True
            break
    if not changed:
        raise RuntimeError("Qualification draft needs one single-select response.")
    status, denial = _request_json_status(
        opener,
        origin=origin,
        path=draft_path,
        method="PUT",
        payload=conflict,
    )
    _assert_safe_practice_denial(
        status,
        denial,
        expected_status=409,
        expected_code="conflict",
    )

    after = stable_practice_progress(
        _request_json(opener, origin=origin, path=progress_path)
    )
    if after["draft"] != saved:
        raise RuntimeError("Stale practice save changed the retained draft.")
    for key in ("retry_state", "history", "review_targets"):
        if after[key] != expected[key]:
            raise RuntimeError(f"Practice draft save changed public {key}.")
    return saved, after


def practice_submission_storage_snapshot(
    postgres_dsn: str,
) -> dict[str, int | str]:
    with psycopg.connect(postgres_dsn) as connection:
        row = connection.execute(PRACTICE_SUBMISSION_STORAGE).fetchone()
    if row is None or len(row) != 8:
        raise RuntimeError("Practice submission storage snapshot is unavailable.")
    labels = (
        "attempts",
        "responses",
        "scores",
        "completion_evidence",
        "outbox_events",
    )
    snapshot: dict[str, int | str] = {
        label: int(row[index]) for index, label in enumerate(labels)
    }
    snapshot.update(
        {
            "submission_id": str(row[5]),
            "attempt_id": str(row[6]),
            "evidence_id": str(row[7]),
        }
    )
    return snapshot


def assert_practice_submission_storage(
    snapshot: dict[str, int | str],
    *,
    submission: dict[str, Any],
    result: dict[str, Any],
) -> None:
    expected = {
        "attempts": 1,
        "responses": len(submission["responses"]),
        "scores": len(submission["responses"]),
        "completion_evidence": 1,
        "outbox_events": 1,
        "submission_id": submission["submission_id"],
        "attempt_id": result["attempt_id"],
        "evidence_id": result["evidence_id"],
    }
    if snapshot != expected:
        raise RuntimeError("Practice submission evidence is incomplete or uncorrelated.")


def assert_practice_submission_restart_result(
    *,
    before_result: dict[str, Any],
    after_result: dict[str, Any],
    before_storage: dict[str, int | str],
    after_storage: dict[str, int | str],
) -> None:
    if after_result != before_result:
        raise RuntimeError("Practice result changed after normal restart.")
    if after_storage != before_storage:
        raise RuntimeError("Practice evidence changed after replay or restart.")


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
    practice_capture = data_root / "practice-submission-capture.json"
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

        practice_before_restart = observe_side_effect_free_practice(
            origin=origin,
            postgres_dsn=postgres_dsn,
        )

        environment = os.environ.copy()
        environment["FINANCIAL_AI_ACADEMY_E2E_BASE_URL"] = origin
        environment["FINANCIAL_AI_ACADEMY_PRACTICE_CAPTURE"] = str(
            practice_capture
        )
        run_checked(npm_e2e_command(), env=environment)

        (
            practice_draft_save,
            _browser_practice_draft,
            practice_submission,
            practice_result,
            browser_practice_progress,
        ) = load_practice_submission_capture(
            practice_capture,
            data_root=data_root,
        )
        practice_storage_before_restart = practice_submission_storage_snapshot(
            postgres_dsn
        )
        assert_practice_submission_storage(
            practice_storage_before_restart,
            submission=practice_submission,
            result=practice_result,
        )
        headless_practice_result = observe_headless_practice_submission(
            origin=origin,
            submission=practice_submission,
            expected_result=practice_result,
        )
        practice_storage_after_replay = practice_submission_storage_snapshot(
            postgres_dsn
        )
        if practice_storage_after_replay != practice_storage_before_restart:
            raise RuntimeError("Practice replay or refusal appended duplicate evidence.")
        (
            headless_practice_draft,
            practice_progress_before_restart,
        ) = observe_headless_practice_progress(
            origin=origin,
            expected_progress=browser_practice_progress,
            draft_save=practice_draft_save,
        )

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
        practice_after_restart = observe_side_effect_free_practice(
            origin=origin,
            postgres_dsn=postgres_dsn,
        )
        assert_practice_restart_result(
            before_restart=practice_before_restart,
            after_restart=practice_after_restart,
        )
        practice_progress_after_restart = read_headless_practice_progress(origin)
        if practice_progress_after_restart != practice_progress_before_restart:
            raise RuntimeError("Practice progress changed after normal restart.")
        replayed_draft_after_restart = replay_headless_practice_draft(
            origin=origin,
            save=practice_draft_save,
        )
        if replayed_draft_after_restart != headless_practice_draft:
            raise RuntimeError("Practice draft replay changed after normal restart.")
        practice_result_after_restart = observe_headless_practice_submission(
            origin=origin,
            submission=practice_submission,
            expected_result=practice_result,
        )
        progress_after_submission_replay = read_headless_practice_progress(origin)
        if progress_after_submission_replay != practice_progress_before_restart:
            raise RuntimeError(
                "Exact submission replay changed retained practice progress."
            )
        practice_storage_after_restart = practice_submission_storage_snapshot(
            postgres_dsn
        )
        assert_practice_submission_restart_result(
            before_result=headless_practice_result,
            after_result=practice_result_after_restart,
            before_storage=practice_storage_before_restart,
            after_storage=practice_storage_after_restart,
        )
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
            "fixture": (
                "intro-risk-return@1.1.0 with "
                "risk-return-check-1@1.0.0 and "
                "intro-risk-return@2.0.0 with "
                "risk-return-practice@1.0.0"
            ),
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
            "practice_opening": (
                "the exact three-shape answer-safe presentation qualified "
                "through repeated non-browser public API reads and the "
                "generated browser client with storage-count invariance "
                "and normal-restart stability"
            ),
            "practice_submission": {
                "atomic_evidence": True,
                "browser_generated_client": True,
                "confidential_denials": True,
                "draft_exact_replay": True,
                "draft_resume_after_restart": True,
                "draft_stale_write_refused": True,
                "exact_headless_replay": True,
                "history_and_review_targets": True,
                "normal_restart_without_reseeding": True,
                "public_api_shared": True,
                "retry_state_server_owned": True,
                "three_response_types": True,
            },
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
