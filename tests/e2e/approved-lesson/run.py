"""Run the isolated approved-lesson cross-system qualification."""

from __future__ import annotations

import argparse
import base64
import copy
from concurrent.futures import ThreadPoolExecutor
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
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import psycopg
from psycopg import sql


REPOSITORY = Path(__file__).resolve().parents[3]
ARTIFACT_ROOT = REPOSITORY / "artifacts" / "tmp"
CONTAINER_PREFIX = "faa-wrk0005-postgres-"
RECOVERY_CONTAINER_PREFIX = "faa-wrk0146-recovery-postgres-"
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
PROJECT_LEARNING_STORAGE_KEYS = (
    "assessment_attempts",
    "assessment_responses",
    "assessment_scores",
    "assessment_completion_evidence",
    "assessment_outbox",
    "practice_attempts",
    "practice_responses",
    "practice_scores",
    "practice_completion_evidence",
    "practice_outbox",
    "learner_completion_projections",
    "learner_completion_history",
    "practice_history_projections",
    "practice_history_attempts",
)
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
PRACTICE_DENIAL_ROOT_KEYS = frozenset(
    {"error_version", "code", "message", "correlation_id"}
)
PRACTICE_DENIAL_PRIVATE_FRAGMENTS = frozenset(
    {
        "assessment.",
        "entered_value",
        "evaluator",
        "learner_id",
        "postgres",
        "practice_attempts",
        "practice_drafts",
        "practice_responses",
        "request_fingerprint",
        "scoring_policy",
        "selected_option_id",
        "sql",
        "stack trace",
        "submission_id",
        "traceback",
    }
)
PLATFORM_HELP_CAPTURE_ROOT_KEYS = frozenset(
    {
        "schema_version",
        "first_page",
        "continued_page",
        "searched_page",
        "approved_search",
        "method_topic",
        "approved_topic",
        "related_topic",
        "limitation_page",
        "limitation_continuation",
        "contexts",
        "context_topics",
        "expected",
    }
)
PLATFORM_HELP_SEARCH_KEYS = frozenset(
    {"schema_version", "corpus_digest", "query", "results", "next_cursor"}
)
PLATFORM_HELP_RESULT_KEYS = frozenset(
    {
        "topic_id",
        "topic_version",
        "topic_kind",
        "title",
        "summary",
        "applicability",
        "publication",
        "source_references",
        "topic_digest",
    }
)
PLATFORM_HELP_TOPIC_KEYS = frozenset(
    {
        "schema_version",
        "topic_id",
        "topic_version",
        "topic_kind",
        "title",
        "summary",
        "keywords",
        "body",
        "applicability",
        "publication",
        "source_references",
        "related_topics",
        "topic_digest",
    }
)
PLATFORM_HELP_PRIVATE_KEYS = frozenset(
    {
        "approval",
        "authoring_path",
        "cookie",
        "credential",
        "learner_id",
        "local_path",
        "permission",
        "prompt",
        "provider_payload",
        "repository_path",
        "reviewer",
        "session_id",
        "storage_locator",
        "token",
    }
)
CONTEXTUAL_HELP_KEYS = (
    "ai-assistance",
    "lesson-publication",
    "practice-result",
    "project-result",
)
CONTEXTUAL_HELP_ROOT_KEYS = frozenset(
    {
        "schema_version",
        "context_key",
        "context_version",
        "feature_label",
        "applicability",
        "help_references",
        "publication",
        "source_references",
        "context_digest",
    }
)
CONTEXTUAL_HELP_REFERENCE_KEYS = frozenset(
    {"topic_id", "topic_version", "purpose", "label"}
)
CONTEXTUAL_HELP_PURPOSES = frozenset(
    {"method", "source", "data_meaning", "ai_boundary", "education_boundary"}
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
PROJECT_CAPTURE_ROOT_KEYS = frozenset(
    {
        "artifact_sha256",
        "current_workspace",
        "export_bundle",
        "learning_state_after",
        "learning_state_before",
        "project",
        "snapshot",
        "workspace_at_snapshot",
    }
)
PRIVATE_PROJECT_CAPTURE_KEYS = frozenset(
    {
        "authorization",
        "cookie",
        "credential",
        "object_key",
        "password",
        "session_cookie",
        "storage_path",
        "token",
    }
)
PERSONAL_WORKSPACE_CAPTURE_ROOT_KEYS = frozenset(
    {
        "exact_replay_request",
        "expected",
        "export",
        "query_request",
        "query_result",
        "refresh_request",
        "refresh_workspace",
        "workspace",
    }
)
PERSONAL_WORKSPACE_ROOT_KEYS = frozenset(
    {
        "schema_version",
        "workspace_id",
        "learner_id",
        "revision",
        "records",
        "collections",
        "created_at",
        "updated_at",
        "workspace_digest",
    }
)
PERSONAL_WORKSPACE_PRIVATE_CAPTURE_KEYS = frozenset(
    {
        "authorization",
        "cookie",
        "credential",
        "database",
        "password",
        "request_fingerprint",
        "session_cookie",
        "storage_path",
        "token",
    }
)
PERSONAL_WORKSPACE_TARGET_SCHEMAS = (
    "assessment",
    "audit",
    "content",
    "curriculum",
    "learner_model",
    "project",
)
LEARNER_PREFERENCE_CAPTURE_ROOT_KEYS = frozenset(
    {
        "schema_version",
        "profile",
        "history",
        "export",
        "exact_replay_request",
        "exact_replay_response",
        "races",
        "expected",
    }
)
LEARNER_PREFERENCE_EXPECTED_KEYS = frozenset(
    {
        "final_goal",
        "final_experience",
        "final_interest",
        "reset_recorded",
        "populated_export_profile_revision",
    }
)
LEARNER_PREFERENCE_PRIVATE_CAPTURE_KEYS = frozenset(
    {
        "authorization",
        "cookie",
        "credential",
        "database",
        "evidence",
        "mastery",
        "password",
        "permission",
        "provider",
        "recommendation",
        "request_fingerprint",
        "session_cookie",
        "storage_path",
        "suitability",
        "token",
    }
)
LEARNER_PREFERENCE_PROFILE_KEYS = frozenset(
    {
        "schema_version",
        "profile_id",
        "learner_id",
        "revision",
        "goals",
        "experience",
        "interests",
        "created_at",
        "updated_at",
        "profile_digest",
    }
)
LEARNER_PREFERENCE_HISTORY_KEYS = frozenset(
    {"schema_version", "profile_id", "current_revision", "changes"}
)
LEARNER_PREFERENCE_EXPORT_KEYS = frozenset(
    {"schema_version", "purpose", "limitations", "exported_at", "profile", "history"}
)
LEARNER_PREFERENCE_REQUEST_KEYS = frozenset(
    {"schema_version", "idempotency_key", "expected_revision", "mutation"}
)
LEARNER_PREFERENCE_DENIAL_KEYS = frozenset(
    {"error_version", "code", "message", "correlation_id"}
)
LEARNER_PREFERENCE_TABLES = frozenset(
    {"preference_profiles", "preference_changes", "preference_mutations"}
)
PRESENTATION_PREFERENCE_CAPTURE_ROOT_KEYS = frozenset(
    {
        "schema_version",
        "profile",
        "history",
        "export",
        "exact_replay_request",
        "exact_replay_response",
        "races",
        "expected",
    }
)
PRESENTATION_PREFERENCE_EXPECTED_KEYS = frozenset(
    {
        "all_combinations",
        "populated_export_profile_revision",
        "reset_recorded",
        "theme_after_reset",
    }
)
PRESENTATION_PREFERENCE_PRIVATE_CAPTURE_KEYS = (
    LEARNER_PREFERENCE_PRIVATE_CAPTURE_KEYS
    | frozenset({"diagnosis", "medical_condition", "assistive_technology"})
)
PRESENTATION_PREFERENCE_PROFILE_KEYS = frozenset(
    {
        "schema_version",
        "profile_id",
        "learner_id",
        "revision",
        "text_size",
        "text_spacing",
        "reading_width",
        "motion",
        "created_at",
        "updated_at",
        "profile_digest",
    }
)
PRESENTATION_PREFERENCE_HISTORY_KEYS = LEARNER_PREFERENCE_HISTORY_KEYS
PRESENTATION_PREFERENCE_EXPORT_KEYS = LEARNER_PREFERENCE_EXPORT_KEYS
PRESENTATION_PREFERENCE_REQUEST_KEYS = LEARNER_PREFERENCE_REQUEST_KEYS
PRESENTATION_PREFERENCE_DENIAL_KEYS = LEARNER_PREFERENCE_DENIAL_KEYS
PRESENTATION_PREFERENCE_TABLES = frozenset(
    {
        "presentation_preference_profiles",
        "presentation_preference_changes",
        "presentation_preference_mutations",
    }
)
ASSISTANCE_PREFERENCE_CAPTURE_ROOT_KEYS = frozenset(
    {
        "schema_version",
        "profile",
        "history",
        "export",
        "exact_replay_request",
        "exact_replay_response",
        "local",
        "races",
        "expected",
    }
)
ASSISTANCE_PREFERENCE_EXPECTED_KEYS = frozenset(
    {
        "first_open_server_revision",
        "local_saved_revision",
        "local_reset_revision",
        "reset_recorded",
    }
)
ASSISTANCE_PREFERENCE_PRIVATE_CAPTURE_KEYS = (
    LEARNER_PREFERENCE_PRIVATE_CAPTURE_KEYS
    | frozenset(
        {
            "destination",
            "email",
            "model",
            "notification",
            "phone",
            "prompt",
            "schedule",
            "subscription",
        }
    )
)
ASSISTANCE_PREFERENCE_PROFILE_KEYS = frozenset(
    {
        "schema_version",
        "profile_id",
        "learner_id",
        "revision",
        "assistance_mode",
        "created_at",
        "updated_at",
        "profile_digest",
    }
)
ASSISTANCE_PREFERENCE_DENIAL_KEYS = LEARNER_PREFERENCE_DENIAL_KEYS
ASSISTANCE_PREFERENCE_TABLES = frozenset(
    {
        "assistance_preference_profiles",
        "assistance_preference_changes",
        "assistance_preference_mutations",
    }
)
PREFERENCE_FAMILY_NAMES = frozenset(
    {"learner", "presentation", "assistance"}
)
PREFERENCE_STORAGE_KEYS = frozenset({"profiles", "changes", "mutations"})
PROJECT_LEARNING_CAPTURE_ROOT_KEYS = frozenset(
    {
        "artifact_sha256",
        "candidates",
        "changed_retry_denial",
        "completion",
        "evidence",
        "exact_replay",
        "history",
        "independent_project_id",
        "outcomes",
        "project",
        "snapshots",
        "submission_intents",
    }
)
PRIVATE_PROJECT_LEARNING_CAPTURE_KEYS = PRIVATE_PROJECT_CAPTURE_KEYS | frozenset(
    {
        "actor_id",
        "learner_id",
        "session_id",
    }
)
UTC_TIMESTAMP = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?Z$"
)
RESERVED_PROJECT_PATH_SEGMENT = re.compile(
    r"^(?:con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?:\..*)?$",
    re.IGNORECASE,
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


def run_replay_qualification() -> None:
    """Prove pure replay invariants before starting the live topology."""

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="approved-replay-", dir=ARTIFACT_ROOT
    ) as directory:
        run_checked(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/e2e/approved-lesson/test_replay_qualification.py",
                "--basetemp",
                str(Path(directory) / "pytest"),
                "-q",
            ]
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


def start_postgres(*, prefix: str = CONTAINER_PREFIX) -> tuple[str, str]:
    if prefix not in {CONTAINER_PREFIX, RECOVERY_CONTAINER_PREFIX}:
        raise RuntimeError("The isolated PostgreSQL container prefix is invalid.")
    container_name = prefix + uuid4().hex[:12]
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
    recovery_container_name: str | None = None,
    data_root: Path | None,
) -> tuple[str, ...]:
    failures: list[str] = []
    steps = [
        ("application", lambda: stop_application(application)),
    ]
    if recovery_container_name is not None:
        steps.append(
            (
                "recovery database container",
                lambda: remove_container(recovery_container_name),
            )
        )
    steps.extend(
        (
            ("database container", lambda: remove_container(container_name)),
            ("temporary data", lambda: remove_data_root(data_root)),
        )
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


def _request_bytes(
    opener: urllib.request.OpenerDirector,
    *,
    origin: str,
    path: str,
) -> bytes:
    request = urllib.request.Request(
        f"{origin}{path}",
        headers={"Accept": "application/octet-stream"},
        method="GET",
    )
    try:
        with opener.open(request, timeout=10) as response:
            if response.status != 200:
                raise RuntimeError(
                    f"Headless API request failed: GET {path} "
                    f"returned {response.status}."
                )
            return response.read()
    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"Headless API request failed: GET {path} returned {error.code}."
        ) from None


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


def _utc_instant(value: object, *, label: str) -> datetime:
    return datetime.fromisoformat(
        _canonical_utc(value, label=label).replace("Z", "+00:00")
    )


def _normalized_utc(value: object, *, label: str) -> str:
    normalized = _utc_instant(value, label=label)
    if normalized.microsecond:
        rendered = normalized.strftime("%Y-%m-%dT%H:%M:%S.%f").rstrip("0")
    else:
        rendered = normalized.strftime("%Y-%m-%dT%H:%M:%S")
    return f"{rendered}Z"


def _canonical_project_logical_path(value: object) -> bool:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 240
        or "\\" in value
        or value.startswith("/")
        or unicodedata.normalize("NFC", value) != value
    ):
        return False
    return all(
        segment
        and segment not in {".", ".."}
        and segment == segment.strip()
        and not segment.endswith(".")
        and not any(
            ord(character) < 32 or character in '<>:"|?*'
            for character in segment
        )
        and RESERVED_PROJECT_PATH_SEGMENT.fullmatch(segment) is None
        for segment in value.split("/")
    )


def _assert_same_practice_scope(
    document: dict[str, Any],
    expected: dict[str, Any],
    *,
    label: str,
) -> None:
    for key in PRACTICE_SCOPE_KEYS:
        if document.get(key) != expected.get(key):
            raise RuntimeError(f"{label} changed the practice {key}.")


def _practice_scope_from_presentation(
    document: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    practice = stable_practice_semantics(document)
    policy = practice["attempt_policy"]
    if not isinstance(policy, dict):
        raise RuntimeError("Practice presentation attempt policy is not an object.")
    required_policy = {
        "policy_id",
        "policy_version",
        "max_attempts",
        "resume_allowed",
        "history_visible",
    }
    if set(policy) != required_policy:
        raise RuntimeError(
            "Practice presentation attempt policy is not the closed public contract."
        )
    maximum = policy["max_attempts"]
    if type(maximum) is not int or not 1 <= maximum <= 10:
        raise RuntimeError("Practice presentation attempt limit is invalid.")
    scope = {
        key: practice[key]
        for key in PRACTICE_SCOPE_KEYS
        if key not in {"attempt_policy_id", "attempt_policy_version"}
    }
    scope["attempt_policy_id"] = policy["policy_id"]
    scope["attempt_policy_version"] = policy["policy_version"]
    return scope, maximum


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
    expected_practice: dict[str, Any] | None = None,
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
    if expected_practice is not None:
        expected_scope, expected_maximum = _practice_scope_from_presentation(
            expected_practice
        )
        _assert_same_practice_scope(
            retry,
            expected_scope,
            label="Practice retry state",
        )
        if maximum != expected_maximum:
            raise RuntimeError(
                "Practice retry limit changed from the immutable presentation."
            )

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
        _assert_same_practice_scope(
            retry,
            stable_submission,
            label="Practice retry state",
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
    expected_practice: dict[str, Any] | None = None,
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
    _assert_same_practice_scope(
        stable_draft_request,
        stable_request,
        label="Practice draft request",
    )
    _assert_same_practice_scope(
        stable_draft_result,
        stable_request,
        label="Practice draft result",
    )
    if expected_practice is not None:
        expected_scope, _expected_maximum = _practice_scope_from_presentation(
            expected_practice
        )
        _assert_same_practice_scope(
            stable_request,
            expected_scope,
            label="Practice submission",
        )
    stable_progress = stable_practice_progress(
        progress,
        expected_submission=stable_request,
        expected_result=stable_result,
        expected_practice=expected_practice,
    )
    return (
        stable_draft_request,
        stable_draft_result,
        stable_request,
        stable_result,
        stable_progress,
    )


def _stable_personal_workspace_reference(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeError("Personal workspace reference is not an object.")
    kind = value.get("reference_kind")
    project_kinds = {
        "project_workspace",
        "project_snapshot",
        "project_artifact",
    }
    if kind in project_kinds:
        project_common = frozenset(
            {
                "reference_kind",
                "owner_module",
                "project_id",
                "title",
                "lifecycle",
                "project_revision",
                "workspace_revision",
                "destination",
                "target_status",
                "validated_at",
            }
        )
        expected_keys = (
            project_common
            if kind == "project_workspace"
            else project_common
            | {
                "snapshot_id",
                "snapshot_digest",
                "closed_at",
            }
            if kind == "project_snapshot"
            else project_common
            | {
                "artifact_id",
                "artifact_version",
                "artifact_kind",
                "logical_path",
                "media_type",
                "inspection_mode",
                "byte_count",
                "content_digest",
                "created_at",
            }
        )
        _exact_keys(value, expected_keys, "Personal workspace Project reference")
        project_id = value.get("project_id")
        if (
            value.get("owner_module") != "project"
            or value.get("lifecycle") != "active"
            or value.get("target_status") != "available"
            or not isinstance(project_id, str)
            or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", project_id)
            or not isinstance(value.get("title"), str)
            or not 1 <= len(value["title"]) <= 240
            or type(value.get("project_revision")) is not int
            or value["project_revision"] < 1
            or type(value.get("workspace_revision")) is not int
            or value["workspace_revision"] < 1
            or not UTC_TIMESTAMP.fullmatch(str(value.get("validated_at", "")))
        ):
            raise RuntimeError("Personal workspace Project authority is invalid.")
        if kind == "project_workspace":
            if value.get("destination") != f"/projects/{project_id}#workspace":
                raise RuntimeError("Personal workspace Project destination is invalid.")
            return copy.deepcopy(value)
        if kind == "project_snapshot":
            snapshot_id = value.get("snapshot_id")
            if (
                not isinstance(snapshot_id, str)
                or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", snapshot_id)
                or not re.fullmatch(r"[a-f0-9]{64}", str(value.get("snapshot_digest", "")))
                or not UTC_TIMESTAMP.fullmatch(str(value.get("closed_at", "")))
                or _utc_instant(
                    value.get("closed_at"), label="Project checkpoint close time"
                )
                > _utc_instant(
                    value.get("validated_at"),
                    label="Project checkpoint validation time",
                )
                or value.get("destination")
                != f"/projects/{project_id}#snapshot-{snapshot_id}"
            ):
                raise RuntimeError("Personal workspace checkpoint reference is invalid.")
            return copy.deepcopy(value)

        artifact_id = value.get("artifact_id")
        logical_path = value.get("logical_path")
        if (
            not isinstance(artifact_id, str)
            or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", artifact_id)
            or type(value.get("artifact_version")) is not int
            or value["artifact_version"] < 1
            or value.get("artifact_kind")
            not in {
                "code",
                "dataset",
                "environment",
                "notebook",
                "reflection",
                "result",
                "supporting_file",
            }
            or not _canonical_project_logical_path(logical_path)
            or value.get("media_type")
            not in {
                "application/json",
                "application/octet-stream",
                "application/pdf",
                "application/x-ipynb+json",
                "text/csv",
                "text/markdown",
                "text/plain",
                "text/x-python",
            }
            or value.get("inspection_mode") not in {"metadata_only", "plain_text"}
            or type(value.get("byte_count")) is not int
            or not 0 <= value["byte_count"] <= 10_485_760
            or not re.fullmatch(r"[a-f0-9]{64}", str(value.get("content_digest", "")))
            or not UTC_TIMESTAMP.fullmatch(str(value.get("created_at", "")))
            or _utc_instant(
                value.get("created_at"), label="Project artifact creation time"
            )
            > _utc_instant(
                value.get("validated_at"),
                label="Project artifact validation time",
            )
            or value.get("destination")
            != (
                f"/projects/{project_id}#artifact-{artifact_id}"
                f"-v{value['artifact_version']}"
            )
        ):
            raise RuntimeError("Personal workspace inert-file reference is invalid.")
        return copy.deepcopy(value)

    common = frozenset(
        {
            "reference_kind",
            "owner_module",
            "placement_id",
            "package_id",
            "package_version",
            "package_digest",
            "title",
            "destination",
            "target_status",
            "provenance",
            "validated_at",
        }
    )
    expected_keys = (
        common | {"opportunity_id", "source_fingerprint"}
        if kind == "learning_opportunity"
        else common
    )
    _exact_keys(value, expected_keys, "Personal workspace reference")
    if kind not in {"learning_opportunity", "placed_lesson"}:
        raise RuntimeError("Personal workspace reference type is unsupported.")
    if value.get("owner_module") != "curriculum" or value.get(
        "target_status"
    ) != "available":
        raise RuntimeError("Personal workspace reference changed source authority.")
    placement_id = value.get("placement_id")
    if (
        not isinstance(placement_id, str)
        or value.get("destination") != f"/learn/placements/{placement_id}"
        or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,63}", placement_id)
    ):
        raise RuntimeError("Personal workspace reference destination is invalid.")
    for key in ("package_digest",):
        if not re.fullmatch(r"[a-f0-9]{64}", str(value.get(key, ""))):
            raise RuntimeError("Personal workspace reference digest is invalid.")
    if kind == "learning_opportunity" and not re.fullmatch(
        r"[a-f0-9]{64}", str(value.get("source_fingerprint", ""))
    ):
        raise RuntimeError("Personal workspace source fingerprint is invalid.")
    if not UTC_TIMESTAMP.fullmatch(str(value.get("validated_at", ""))):
        raise RuntimeError("Personal workspace validation time is invalid.")
    provenance = value.get("provenance")
    if not isinstance(provenance, dict):
        raise RuntimeError("Personal workspace provenance is unavailable.")
    _exact_keys(
        provenance,
        frozenset(
            {
                "published_by",
                "published_at",
                "content_reviewed_on",
                "educational_use_notice",
            }
        ),
        "Personal workspace provenance",
    )
    if not UTC_TIMESTAMP.fullmatch(str(provenance.get("published_at", ""))):
        raise RuntimeError("Personal workspace publication time is invalid.")
    return copy.deepcopy(value)


def stable_personal_workspace(document: dict[str, Any]) -> dict[str, Any]:
    _exact_keys(document, PERSONAL_WORKSPACE_ROOT_KEYS, "Personal workspace")
    if (
        document.get("schema_version") != "1.0.0"
        or type(document.get("revision")) is not int
        or document["revision"] < 1
        or not re.fullmatch(
            r"[a-f0-9]{64}", str(document.get("workspace_digest", ""))
        )
        or not UTC_TIMESTAMP.fullmatch(str(document.get("created_at", "")))
        or not UTC_TIMESTAMP.fullmatch(str(document.get("updated_at", "")))
    ):
        raise RuntimeError("Personal workspace identity or chronology is invalid.")
    records = document.get("records")
    collections = document.get("collections")
    if not isinstance(records, list) or len(records) > 200:
        raise RuntimeError("Personal workspace records are invalid.")
    if not isinstance(collections, list) or len(collections) > 50:
        raise RuntimeError("Personal workspace collections are invalid.")
    record_ids: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            raise RuntimeError("Personal workspace record is not an object.")
        kind = record.get("record_kind")
        common = {
            "record_kind",
            "record_id",
            "target",
            "archived",
            "created_at",
            "updated_at",
        }
        _exact_keys(
            record,
            frozenset(common | ({"title", "body"} if kind == "note" else {"label"})),
            "Personal workspace record",
        )
        if kind not in {"note", "bookmark"} or type(record.get("archived")) is not bool:
            raise RuntimeError("Personal workspace record type is invalid.")
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not re.fullmatch(
            r"[a-z0-9][a-z0-9._-]{0,127}", record_id
        ):
            raise RuntimeError("Personal workspace record ID is invalid.")
        if record_id in record_ids:
            raise RuntimeError("Personal workspace record IDs are duplicated.")
        record_ids.append(record_id)
        if kind == "note" and (
            not isinstance(record.get("title"), str)
            or not 1 <= len(record["title"]) <= 120
            or not isinstance(record.get("body"), str)
            or not 1 <= len(record["body"]) <= 8_000
        ):
            raise RuntimeError("Personal workspace note text is invalid.")
        if kind == "bookmark" and record.get("label") is not None and (
            not isinstance(record.get("label"), str)
            or len(record["label"]) > 120
        ):
            raise RuntimeError("Personal workspace bookmark label is invalid.")
        _stable_personal_workspace_reference(record.get("target"))
    collection_ids: set[str] = set()
    accepted_records = set(record_ids)
    for collection in collections:
        if not isinstance(collection, dict):
            raise RuntimeError("Personal workspace collection is not an object.")
        _exact_keys(
            collection,
            frozenset(
                {
                    "collection_id",
                    "title",
                    "member_record_ids",
                    "created_at",
                    "updated_at",
                }
            ),
            "Personal workspace collection",
        )
        collection_id = collection.get("collection_id")
        members = collection.get("member_record_ids")
        if (
            not isinstance(collection_id, str)
            or collection_id in collection_ids
            or not isinstance(collection.get("title"), str)
            or not 1 <= len(collection["title"]) <= 120
            or not isinstance(members, list)
            or len(members) > 100
            or len(set(members)) != len(members)
            or any(member not in accepted_records for member in members)
        ):
            raise RuntimeError("Personal workspace collection is invalid.")
        collection_ids.add(collection_id)
    timestamp_fields = {
        "closed_at",
        "created_at",
        "published_at",
        "updated_at",
        "validated_at",
    }

    def normalize(value: object, *, field: str = "") -> object:
        if isinstance(value, dict):
            return {
                key: (
                    _normalized_utc(item, label=f"Personal workspace {key}")
                    if key in timestamp_fields
                    else normalize(item, field=key)
                )
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [normalize(item, field=field) for item in value]
        return copy.deepcopy(value)

    normalized = normalize(document)
    if not isinstance(normalized, dict):
        raise RuntimeError("Personal workspace normalization failed.")
    return normalized


def stable_personal_workspace_export(
    document: object,
    *,
    expected_workspace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise RuntimeError("Personal workspace export is not an object.")
    _exact_keys(
        document,
        frozenset(
            {
                "schema_version",
                "workspace_digest",
                "generated_at",
                "workspace",
            }
        ),
        "Personal workspace export",
    )
    workspace_value = document.get("workspace")
    if not isinstance(workspace_value, dict):
        raise RuntimeError("Personal workspace export has no workspace document.")
    workspace = stable_personal_workspace(workspace_value)
    generated_at = _normalized_utc(
        document.get("generated_at"),
        label="Personal workspace export generation time",
    )
    if (
        document.get("schema_version") != "1.0.0"
        or document.get("workspace_digest") != workspace["workspace_digest"]
        or _utc_instant(
            generated_at,
            label="Personal workspace export generation time",
        )
        < _utc_instant(
            workspace["updated_at"],
            label="Personal workspace update time",
        )
    ):
        raise RuntimeError("Personal workspace export correlation is invalid.")
    if expected_workspace is not None and workspace != expected_workspace:
        raise RuntimeError("Personal workspace export changed workspace meaning.")
    return {
        "schema_version": "1.0.0",
        "workspace_digest": workspace["workspace_digest"],
        "generated_at": generated_at,
        "workspace": workspace,
    }


def stable_personal_workspace_query(document: object) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise RuntimeError("Personal workspace query is not an object.")
    allowed = frozenset(
        {
            "schema_version",
            "text",
            "record_kinds",
            "owner_modules",
            "reference_kinds",
            "target_statuses",
            "archived",
            "collection_id",
            "sort",
            "limit",
            "cursor",
        }
    )
    if not set(document).issubset(allowed) or document.get("schema_version") != "1.0.0":
        raise RuntimeError("Personal workspace query has an invalid shape.")
    normalized = copy.deepcopy(document)
    text = normalized.get("text")
    if text is not None:
        if not isinstance(text, str) or not 1 <= len(text) <= 240 or "\x00" in text:
            raise RuntimeError("Personal workspace query text is invalid.")
        text = " ".join(unicodedata.normalize("NFKC", text).casefold().split())
        if not 1 <= len(text) <= 240:
            raise RuntimeError("Personal workspace canonical query text is invalid.")
        normalized["text"] = text
    closed_arrays = {
        "record_kinds": ({"note", "bookmark"}, 2),
        "owner_modules": ({"curriculum", "project"}, 2),
        "reference_kinds": (
            {
                "learning_opportunity",
                "placed_lesson",
                "project_workspace",
                "project_snapshot",
                "project_artifact",
            },
            5,
        ),
        "target_statuses": ({"available", "stale", "unavailable"}, 3),
    }
    for field, (accepted, maximum) in closed_arrays.items():
        values = normalized.get(field)
        if values is None:
            continue
        if (
            not isinstance(values, list)
            or not 1 <= len(values) <= maximum
            or len(values) != len(set(values))
            or any(value not in accepted for value in values)
        ):
            raise RuntimeError(f"Personal workspace query {field} is invalid.")
        normalized[field] = sorted(values)
    if "archived" in normalized and type(normalized["archived"]) is not bool:
        raise RuntimeError("Personal workspace archive query is invalid.")
    collection_id = normalized.get("collection_id")
    if collection_id is not None and (
        not isinstance(collection_id, str)
        or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", collection_id)
    ):
        raise RuntimeError("Personal workspace collection query is invalid.")
    sort = normalized.get("sort", "workspace_order")
    if sort not in {
        "workspace_order",
        "updated_desc",
        "updated_asc",
        "title_asc",
        "source_asc",
    }:
        raise RuntimeError("Personal workspace query order is invalid.")
    limit = normalized.get("limit", 50)
    if type(limit) is not int or not 1 <= limit <= 100:
        raise RuntimeError("Personal workspace query limit is invalid.")
    cursor = normalized.get("cursor")
    if cursor is not None and (
        not isinstance(cursor, str)
        or not re.fullmatch(r"[A-Za-z0-9_-]{1,512}", cursor)
    ):
        raise RuntimeError("Personal workspace query cursor is invalid.")
    normalized["sort"] = sort
    normalized["limit"] = limit
    return normalized


def personal_workspace_query_digest(query: dict[str, Any]) -> str:
    normalized = stable_personal_workspace_query(query)
    material = {
        key: value
        for key, value in normalized.items()
        if key != "cursor"
        and not (key == "sort" and value == "workspace_order")
        and not (key == "limit" and value == 50)
    }
    return hashlib.sha256(
        json.dumps(
            material,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def stable_personal_workspace_query_result(
    document: object,
    *,
    requested: dict[str, Any],
    workspace: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise RuntimeError("Personal workspace query result is not an object.")
    _exact_keys(
        document,
        frozenset(
            {
                "schema_version",
                "workspace_revision",
                "query_digest",
                "applied_query",
                "records",
                "next_cursor",
            }
        ),
        "Personal workspace query result",
    )
    applied = stable_personal_workspace_query(document.get("applied_query"))
    expected_query = stable_personal_workspace_query(requested)
    if applied != expected_query:
        raise RuntimeError("Personal workspace applied query changed requested meaning.")
    if (
        document.get("schema_version") != "1.0.0"
        or type(document.get("workspace_revision")) is not int
        or not 1 <= document["workspace_revision"] <= workspace["revision"]
        or document.get("query_digest") != personal_workspace_query_digest(applied)
    ):
        raise RuntimeError("Personal workspace query result correlation is invalid.")
    records = document.get("records")
    if (
        not isinstance(records, list)
        or len(records) > applied["limit"]
        or len({record.get("record_id") for record in records if isinstance(record, dict)})
        != len(records)
    ):
        raise RuntimeError("Personal workspace query records are invalid.")
    stable_records = stable_personal_workspace(
        {
            "schema_version": "1.0.0",
            "workspace_id": "workspace-query-validation",
            "learner_id": "learner-query-validation",
            "revision": 1,
            "records": records,
            "collections": [],
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "workspace_digest": "0" * 64,
        }
    )["records"]
    workspace_records = {
        record["record_id"]: record for record in workspace["records"]
    }
    if any(workspace_records.get(record["record_id"]) != record for record in stable_records):
        raise RuntimeError("Personal workspace query returned an unowned or changed record.")
    next_cursor = document.get("next_cursor")
    if next_cursor is not None and (
        not stable_records
        or not isinstance(next_cursor, str)
        or not re.fullmatch(r"[A-Za-z0-9_-]{1,512}", next_cursor)
    ):
        raise RuntimeError("Personal workspace query continuation is invalid.")
    return {
        "schema_version": "1.0.0",
        "workspace_revision": document["workspace_revision"],
        "query_digest": document["query_digest"],
        "applied_query": applied,
        "records": copy.deepcopy(stable_records),
        "next_cursor": next_cursor,
    }


def stable_personal_workspace_refresh_request(
    document: object,
    *,
    workspace_revision: int,
) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise RuntimeError("Personal workspace refresh request is not an object.")
    _exact_keys(
        document,
        frozenset({"schema_version", "idempotency_key", "expected_revision", "mutation"}),
        "Personal workspace refresh request",
    )
    mutation = document.get("mutation")
    if not isinstance(mutation, dict):
        raise RuntimeError("Personal workspace refresh mutation is invalid.")
    _exact_keys(
        mutation,
        frozenset({"operation", "record_id"}),
        "Personal workspace refresh mutation",
    )
    try:
        request_id = UUID(str(document.get("idempotency_key")))
    except ValueError as error:
        raise RuntimeError("Personal workspace refresh key is invalid.") from error
    if (
        document.get("schema_version") != "1.0.0"
        or str(request_id) != document.get("idempotency_key")
        or document.get("expected_revision") != workspace_revision
        or mutation.get("operation") != "refresh_reference"
        or not isinstance(mutation.get("record_id"), str)
        or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", mutation["record_id"])
    ):
        raise RuntimeError("Personal workspace refresh request is invalid.")
    return copy.deepcopy(document)


def _project_reference_expectations(
    project_capture: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    project = project_capture.get("project")
    current_workspace = project_capture.get("current_workspace")
    snapshot = project_capture.get("snapshot")
    if not all(
        isinstance(value, dict)
        for value in (project, current_workspace, snapshot)
    ):
        raise RuntimeError("Project correlation evidence is unavailable.")
    snapshot_material = snapshot.get("snapshot")
    artifacts = current_workspace.get("artifacts")
    if (
        not isinstance(snapshot_material, dict)
        or not isinstance(artifacts, list)
        or len(artifacts) != 1
        or not isinstance(artifacts[0], dict)
    ):
        raise RuntimeError("Project correlation evidence is incomplete.")
    artifact = artifacts[0]
    common = {
        "owner_module": "project",
        "project_id": project.get("project_id"),
        "title": project.get("title"),
        "lifecycle": project.get("lifecycle"),
        "target_status": "available",
    }
    workspace_reference = common | {
        "reference_kind": "project_workspace",
        "project_revision": project.get("revision"),
        "workspace_revision": current_workspace.get("workspace_revision"),
        "destination": f"/projects/{project.get('project_id')}#workspace",
    }
    snapshot_reference = common | {
        "reference_kind": "project_snapshot",
        "project_revision": snapshot_material.get("project_revision"),
        "workspace_revision": snapshot_material.get("workspace_revision"),
        "snapshot_id": snapshot.get("snapshot_id"),
        "snapshot_digest": snapshot.get("snapshot_digest"),
        "closed_at": snapshot.get("closed_at"),
        "destination": (
            f"/projects/{project.get('project_id')}#snapshot-"
            f"{snapshot.get('snapshot_id')}"
        ),
    }
    artifact_reference = common | {
        "reference_kind": "project_artifact",
        "project_revision": project.get("revision"),
        "workspace_revision": current_workspace.get("workspace_revision"),
        **{
            key: artifact.get(key)
            for key in (
                "artifact_id",
                "artifact_version",
                "artifact_kind",
                "logical_path",
                "media_type",
                "inspection_mode",
                "byte_count",
                "content_digest",
                "created_at",
            )
        },
        "destination": (
            f"/projects/{project.get('project_id')}#artifact-"
            f"{artifact.get('artifact_id')}-v{artifact.get('artifact_version')}"
        ),
    }
    return {
        "project_workspace": workspace_reference,
        "project_snapshot": snapshot_reference,
        "project_artifact": artifact_reference,
    }


def _matches_reference_expectation(
    actual: dict[str, Any], expected: dict[str, Any]
) -> bool:
    return all(actual.get(key) == value for key, value in expected.items())


def load_personal_workspace_capture(
    path: Path,
    *,
    data_root: Path,
    project_capture: dict[str, Any],
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("The bounded Personal workspace capture is absent.")
    resolved = path.resolve()
    if resolved.parent != data_root.resolve() or resolved.stat().st_size > 524_288:
        raise RuntimeError("Personal workspace capture escaped its bounded root.")
    capture = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(capture, dict) or set(capture) != PERSONAL_WORKSPACE_CAPTURE_ROOT_KEYS:
        raise RuntimeError("Personal workspace capture has an invalid shape.")
    leaked = PERSONAL_WORKSPACE_PRIVATE_CAPTURE_KEYS & _nested_mapping_keys(capture)
    if leaked:
        raise RuntimeError("Personal workspace capture contains private runtime data.")
    workspace = capture.get("workspace")
    replay = capture.get("exact_replay_request")
    query_request = capture.get("query_request")
    query_result = capture.get("query_result")
    refresh_request = capture.get("refresh_request")
    refresh_workspace = capture.get("refresh_workspace")
    export_document = capture.get("export")
    expected = capture.get("expected")
    if not all(
        isinstance(value, dict)
        for value in (
            workspace,
            replay,
            query_request,
            query_result,
            refresh_request,
            refresh_workspace,
            export_document,
            expected,
        )
    ):
        raise RuntimeError("Personal workspace capture documents must be objects.")
    stable = stable_personal_workspace(workspace)
    stable_export = stable_personal_workspace_export(
        export_document,
        expected_workspace=stable,
    )
    stable_query_request = stable_personal_workspace_query(query_request)
    stable_query_result = stable_personal_workspace_query_result(
        query_result,
        requested=stable_query_request,
        workspace=stable,
    )
    stable_refresh_request = stable_personal_workspace_refresh_request(
        refresh_request,
        workspace_revision=stable_query_result["workspace_revision"],
    )
    stable_refresh_workspace = stable_personal_workspace(refresh_workspace)
    if stable_refresh_workspace["revision"] != stable_query_result["workspace_revision"] + 1:
        raise RuntimeError("Personal workspace refresh revision is uncorrelated.")
    refresh_record_id = stable_refresh_request["mutation"]["record_id"]
    refreshed_record = next(
        (
            record
            for record in stable_refresh_workspace["records"]
            if record["record_id"] == refresh_record_id
        ),
        None,
    )
    final_refreshed_record = next(
        (record for record in stable["records"] if record["record_id"] == refresh_record_id),
        None,
    )
    if (
        refreshed_record is None
        or final_refreshed_record != refreshed_record
        or refreshed_record["target"].get("target_status") != "available"
    ):
        raise RuntimeError("Personal workspace refresh result is uncorrelated.")
    project_references = _project_reference_expectations(project_capture)
    _exact_keys(
        replay,
        frozenset({"schema_version", "idempotency_key", "expected_revision", "mutation"}),
        "Personal workspace replay request",
    )
    mutation = replay.get("mutation")
    if (
        replay.get("schema_version") != "1.0.0"
        or not isinstance(replay.get("idempotency_key"), str)
        or type(replay.get("expected_revision")) is not int
        or replay["expected_revision"] != stable["revision"] - 1
        or not isinstance(mutation, dict)
    ):
        raise RuntimeError("Personal workspace replay request is invalid.")
    try:
        UUID(replay["idempotency_key"])
    except ValueError as error:
        raise RuntimeError("Personal workspace replay key is invalid.") from error
    _exact_keys(
        mutation,
        frozenset({"operation", "record_id"}),
        "Personal workspace replay mutation",
    )
    if mutation.get("operation") != "restore_record":
        raise RuntimeError("Personal workspace replay is not the accepted final restore.")
    _exact_keys(
        expected,
        frozenset(
            {
                "note_title",
                "note_body",
                "bookmark_label",
                "collection_title",
                "placement_id",
                "project_id",
                "project_title",
                "project_lifecycle",
                "project_revision",
                "project_workspace_revision",
                "project_note_title",
                "project_note_body",
                "snapshot_id",
                "snapshot_label",
                "snapshot_digest",
                "snapshot_project_revision",
                "snapshot_workspace_revision",
                "snapshot_closed_at",
                "artifact_id",
                "artifact_version",
                "artifact_label",
                "artifact_project_revision",
                "artifact_workspace_revision",
                "artifact_kind",
                "artifact_logical_path",
                "artifact_media_type",
                "artifact_inspection_mode",
                "artifact_digest",
                "artifact_byte_count",
                "artifact_created_at",
            }
        ),
        "Personal workspace capture expectations",
    )
    expected_project_values = {
        "project_id": project_references["project_workspace"]["project_id"],
        "project_title": project_references["project_workspace"]["title"],
        "project_lifecycle": project_references["project_workspace"]["lifecycle"],
        "project_revision": project_references["project_workspace"]["project_revision"],
        "project_workspace_revision": project_references["project_workspace"][
            "workspace_revision"
        ],
        "snapshot_id": project_references["project_snapshot"]["snapshot_id"],
        "snapshot_digest": project_references["project_snapshot"]["snapshot_digest"],
        "snapshot_project_revision": project_references["project_snapshot"][
            "project_revision"
        ],
        "snapshot_workspace_revision": project_references["project_snapshot"][
            "workspace_revision"
        ],
        "snapshot_closed_at": project_references["project_snapshot"]["closed_at"],
        "artifact_id": project_references["project_artifact"]["artifact_id"],
        "artifact_version": project_references["project_artifact"]["artifact_version"],
        "artifact_project_revision": project_references["project_artifact"][
            "project_revision"
        ],
        "artifact_workspace_revision": project_references["project_artifact"][
            "workspace_revision"
        ],
        "artifact_kind": project_references["project_artifact"]["artifact_kind"],
        "artifact_logical_path": project_references["project_artifact"][
            "logical_path"
        ],
        "artifact_media_type": project_references["project_artifact"]["media_type"],
        "artifact_inspection_mode": project_references["project_artifact"][
            "inspection_mode"
        ],
        "artifact_digest": project_references["project_artifact"]["content_digest"],
        "artifact_byte_count": project_references["project_artifact"]["byte_count"],
        "artifact_created_at": project_references["project_artifact"]["created_at"],
    }
    if any(
        expected.get(key) != value
        for key, value in expected_project_values.items()
    ):
        raise RuntimeError("Personal workspace expectations changed Project meaning.")
    notes = [record for record in stable["records"] if record["record_kind"] == "note"]
    bookmarks = [
        record for record in stable["records"] if record["record_kind"] == "bookmark"
    ]
    notes_by_title = {record["title"]: record for record in notes}
    bookmarks_by_label = {record["label"]: record for record in bookmarks}
    curriculum_note = notes_by_title.get(expected.get("note_title"))
    project_note = notes_by_title.get(expected.get("project_note_title"))
    curriculum_bookmark = bookmarks_by_label.get(expected.get("bookmark_label"))
    snapshot_bookmark = bookmarks_by_label.get(expected.get("snapshot_label"))
    artifact_bookmark = bookmarks_by_label.get(expected.get("artifact_label"))
    if (
        len(notes) != 2
        or len(bookmarks) != 3
        or len(stable["collections"]) != 1
        or curriculum_note is None
        or curriculum_note["body"] != expected.get("note_body")
        or curriculum_note["archived"] is not False
        or curriculum_note["target"].get("reference_kind") != "placed_lesson"
        or curriculum_note["target"].get("placement_id")
        != expected.get("placement_id")
        or project_note is None
        or project_note["body"] != expected.get("project_note_body")
        or project_note["target"].get("reference_kind") != "project_workspace"
        or not _matches_reference_expectation(
            project_note["target"], project_references["project_workspace"]
        )
        or stable_refresh_request["mutation"]["record_id"]
        != project_note["record_id"]
        or curriculum_bookmark is None
        or curriculum_bookmark["target"].get("reference_kind") != "placed_lesson"
        or curriculum_bookmark["target"].get("placement_id")
        != expected.get("placement_id")
        or snapshot_bookmark is None
        or snapshot_bookmark["target"].get("reference_kind") != "project_snapshot"
        or not _matches_reference_expectation(
            snapshot_bookmark["target"], project_references["project_snapshot"]
        )
        or artifact_bookmark is None
        or artifact_bookmark["target"].get("reference_kind") != "project_artifact"
        or not _matches_reference_expectation(
            artifact_bookmark["target"], project_references["project_artifact"]
        )
        or stable["collections"][0]["title"] != expected.get("collection_title")
        or set(stable["collections"][0]["member_record_ids"])
        != {record["record_id"] for record in stable["records"]}
        or mutation.get("record_id") != curriculum_note["record_id"]
    ):
        raise RuntimeError("Personal workspace capture changed browser-observed meaning.")
    return {
        "workspace": stable,
        "export": stable_export,
        "exact_replay_request": copy.deepcopy(replay),
        "query_request": stable_query_request,
        "query_result": stable_query_result,
        "refresh_request": stable_refresh_request,
        "refresh_workspace": stable_refresh_workspace,
        "expected": copy.deepcopy(expected),
    }


def _assert_safe_personal_workspace_denial(
    status: int,
    document: dict[str, Any],
    *,
    expected_code: str,
    capture: dict[str, Any],
    additional_sensitive_values: tuple[str, ...] = (),
) -> None:
    if status != 409:
        raise RuntimeError("Personal workspace conflict returned an unexpected status.")
    _exact_keys(
        document,
        frozenset({"error_version", "code", "message", "correlation_id"}),
        "Personal workspace denial",
    )
    if document.get("error_version") != "1.0" or document.get("code") != expected_code:
        raise RuntimeError("Personal workspace conflict changed public meaning.")
    correlation_id = document.get("correlation_id")
    try:
        parsed_correlation = UUID(str(correlation_id))
    except ValueError as error:
        raise RuntimeError("Personal workspace denial correlation is invalid.") from error
    if str(parsed_correlation) != correlation_id:
        raise RuntimeError("Personal workspace denial correlation is invalid.")
    workspace = capture["workspace"]
    replay = capture["exact_replay_request"]
    project_sensitive_keys = {
        "project_id",
        "title",
        "destination",
        "snapshot_id",
        "snapshot_digest",
        "closed_at",
        "artifact_id",
        "logical_path",
        "content_digest",
        "created_at",
    }
    sensitive_values = {
        str(workspace["learner_id"]),
        str(workspace["workspace_id"]),
        str(replay["idempotency_key"]),
        str(replay["mutation"]["record_id"]),
        *(str(record["record_id"]) for record in workspace["records"]),
        *(
            str(value)
            for record in workspace["records"]
            for value in (
                record.get("title"),
                record.get("body"),
                record.get("label"),
            )
            if value
        ),
        *(
            str(value)
            for record in workspace["records"]
            if record.get("target", {}).get("owner_module") == "project"
            for key, value in record["target"].items()
            if key in project_sensitive_keys and isinstance(value, str) and value
        ),
        *(value for value in additional_sensitive_values if value),
    }
    serialized = json.dumps(
        document, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).casefold()
    private_markers = PERSONAL_WORKSPACE_PRIVATE_CAPTURE_KEYS | {
        "personal_workspace",
        "request_fingerprint",
        "storage_path",
    }
    if any(value.casefold() in serialized for value in sensitive_values) or any(
        marker.casefold() in serialized for marker in private_markers
    ):
        raise RuntimeError("Personal workspace denial disclosed private details.")
    canonical_messages = {
        "immutable_conflict": "The request key already names different saved work.",
        "stale_revision": (
            "The saved workspace changed. Refresh it before trying again."
        ),
        "source_unavailable": "The learning item is not available to save.",
    }
    if document.get("message") != canonical_messages.get(expected_code):
        raise RuntimeError("Personal workspace denial changed public meaning.")


def observe_headless_personal_workspace(
    *,
    origin: str,
    capture: dict[str, Any],
) -> dict[str, Any]:
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
    _request_json(
        opener,
        origin=origin,
        path="/api/v1/session/single-profile",
        method="POST",
        payload={"limitation_acknowledged": True},
    )
    expected = capture["workspace"]
    observed = stable_personal_workspace(
        _request_json(opener, origin=origin, path="/api/v1/personal-workspace")
    )
    if observed != expected:
        raise RuntimeError("Headless Personal workspace changed browser-observed meaning.")
    export_observation = stable_personal_workspace_export(
        _request_json(
            opener,
            origin=origin,
            path="/api/v1/personal-workspace/export",
        ),
        expected_workspace=expected,
    )
    browser_export = capture["export"]
    if (
        any(
            export_observation[key] != browser_export[key]
            for key in ("schema_version", "workspace_digest", "workspace")
        )
        or _utc_instant(
            export_observation["generated_at"],
            label="Headless Personal workspace export generation time",
        )
        < _utc_instant(
            browser_export["generated_at"],
            label="Browser Personal workspace export generation time",
        )
    ):
        raise RuntimeError("Headless Personal workspace export changed browser meaning.")
    query_observation = stable_personal_workspace_query_result(
        _request_json(
            opener,
            origin=origin,
            path="/api/v1/personal-workspace/query",
            method="POST",
            payload=capture["query_request"],
        ),
        requested=capture["query_request"],
        workspace=expected,
    )
    browser_query = capture["query_result"]
    if query_observation["workspace_revision"] != expected["revision"] or any(
        query_observation[key] != browser_query[key]
        for key in (
            "schema_version",
            "query_digest",
            "applied_query",
            "records",
            "next_cursor",
        )
    ):
        raise RuntimeError("Headless Personal workspace query changed browser meaning.")
    refresh_replay = stable_personal_workspace(
        _request_json(
            opener,
            origin=origin,
            path="/api/v1/personal-workspace/mutations",
            method="POST",
            payload=capture["refresh_request"],
        )
    )
    if refresh_replay != capture["refresh_workspace"]:
        raise RuntimeError("Headless Personal workspace refresh replay changed meaning.")
    exact_request = capture["exact_replay_request"]
    replayed = stable_personal_workspace(
        _request_json(
            opener,
            origin=origin,
            path="/api/v1/personal-workspace/mutations",
            method="POST",
            payload=exact_request,
        )
    )
    if replayed != expected:
        raise RuntimeError("Headless Personal workspace replay changed accepted meaning.")
    changed = copy.deepcopy(exact_request)
    changed["mutation"]["operation"] = "archive_record"
    changed_status, changed_denial = _request_json_status(
        opener,
        origin=origin,
        path="/api/v1/personal-workspace/mutations",
        method="POST",
        payload=changed,
    )
    _assert_safe_personal_workspace_denial(
        changed_status,
        changed_denial,
        expected_code="immutable_conflict",
        capture=capture,
    )
    stale = copy.deepcopy(changed)
    stale["idempotency_key"] = str(uuid4())
    stale_status, stale_denial = _request_json_status(
        opener,
        origin=origin,
        path="/api/v1/personal-workspace/mutations",
        method="POST",
        payload=stale,
    )
    _assert_safe_personal_workspace_denial(
        stale_status,
        stale_denial,
        expected_code="stale_revision",
        capture=capture,
    )
    missing_target = {
        "schema_version": "1.0.0",
        "idempotency_key": str(uuid4()),
        "expected_revision": expected["revision"],
        "mutation": {
            "operation": "create_bookmark",
            "selector": {
                "reference_kind": "project_workspace",
                "project_id": "project.missing-qualification",
            },
            "label": "Unavailable Project",
        },
    }
    missing_status, missing_denial = _request_json_status(
        opener,
        origin=origin,
        path="/api/v1/personal-workspace/mutations",
        method="POST",
        payload=missing_target,
    )
    _assert_safe_personal_workspace_denial(
        missing_status,
        missing_denial,
        expected_code="source_unavailable",
        capture=capture,
        additional_sensitive_values=(
            str(missing_target["mutation"]["selector"]["project_id"]),
        ),
    )
    after_denial = stable_personal_workspace(
        _request_json(opener, origin=origin, path="/api/v1/personal-workspace")
    )
    if after_denial != expected:
        raise RuntimeError(
            "An unavailable Project changed unrelated Saved Learning records."
        )
    return observed


def open_personal_workspace_session(
    *,
    origin: str,
    expected_workspace: dict[str, Any],
) -> urllib.request.OpenerDirector:
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
    _request_json(
        opener,
        origin=origin,
        path="/api/v1/session/single-profile",
        method="POST",
        payload={"limitation_acknowledged": True},
    )
    observed = stable_personal_workspace(
        _request_json(opener, origin=origin, path="/api/v1/personal-workspace")
    )
    if observed != expected_workspace:
        raise RuntimeError("Recovery session did not observe accepted source state.")
    return opener


def assert_restored_session_denied(
    *,
    opener: urllib.request.OpenerDirector,
    origin: str,
) -> None:
    status, document = _request_json_read_status(
        opener,
        origin=origin,
        path="/api/v1/personal-workspace",
    )
    _exact_keys(
        document,
        frozenset({"error_version", "code", "message", "correlation_id"}),
        "Revoked restored session denial",
    )
    correlation_id = document.get("correlation_id")
    try:
        parsed_correlation = UUID(str(correlation_id))
    except ValueError as error:
        raise RuntimeError("Revoked session denial correlation is invalid.") from error
    serialized = json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).casefold()
    if (
        status != 401
        or document.get("error_version") != "1.0"
        or document.get("code") != "unauthorized"
        or document.get("message") != "A valid learner session is required."
        or str(parsed_correlation) != correlation_id
        or any(
            marker in serialized
            for marker in (
                "session_cookie",
                "session_id",
                "token_hash",
                "workspace_id",
                "learner_id",
                "postgresql",
            )
        )
    ):
        raise RuntimeError("Restored session was not denied safely.")


def load_project_workspace_capture(
    path: Path,
    *,
    data_root: Path,
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("The bounded Project workspace capture is absent.")
    resolved = path.resolve()
    if resolved.parent != data_root.resolve() or resolved.stat().st_size > 1_048_576:
        raise RuntimeError("Project workspace capture escaped its bounded root.")
    capture = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(capture, dict) or set(capture) != PROJECT_CAPTURE_ROOT_KEYS:
        raise RuntimeError("Project workspace capture has an invalid shape.")
    leaked = PRIVATE_PROJECT_CAPTURE_KEYS & _nested_mapping_keys(capture)
    if leaked:
        raise RuntimeError("Project workspace capture contains private runtime data.")

    document_keys = (
        "project",
        "workspace_at_snapshot",
        "current_workspace",
        "snapshot",
        "export_bundle",
        "learning_state_before",
        "learning_state_after",
    )
    if not all(isinstance(capture[key], dict) for key in document_keys):
        raise RuntimeError("Project workspace capture documents must be objects.")
    if capture["learning_state_before"] != capture["learning_state_after"]:
        raise RuntimeError("Project browser work changed learning state.")

    project = capture["project"]
    workspace_at_snapshot = capture["workspace_at_snapshot"]
    current_workspace = capture["current_workspace"]
    snapshot = capture["snapshot"]
    export_bundle = capture["export_bundle"]
    project_id = project.get("project_id")
    if (
        not isinstance(project_id, str)
        or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", project_id)
        or project.get("schema_version") != "1.0.0"
        or project.get("origin") != {"origin_type": "independent"}
    ):
        raise RuntimeError("Project workspace capture has an invalid Project shell.")
    if any(
        workspace.get("project_id") != project_id
        or workspace.get("schema_version") != "1.0.0"
        for workspace in (workspace_at_snapshot, current_workspace)
    ):
        raise RuntimeError("Project workspace capture changed Project identity.")
    snapshot_material = snapshot.get("snapshot")
    if (
        snapshot.get("schema_version") != "1.0.0"
        or not isinstance(snapshot.get("snapshot_id"), str)
        or not isinstance(snapshot.get("snapshot_digest"), str)
        or not isinstance(snapshot_material, dict)
        or snapshot_material.get("project_id") != project_id
        or snapshot_material.get("workspace_revision")
        != workspace_at_snapshot.get("workspace_revision")
    ):
        raise RuntimeError("Project workspace capture has an invalid snapshot.")
    snapshot_revision = workspace_at_snapshot.get("workspace_revision")
    current_revision = current_workspace.get("workspace_revision")
    if (
        type(snapshot_revision) is not int
        or type(current_revision) is not int
        or current_revision <= snapshot_revision
    ):
        raise RuntimeError("Project workspace capture did not preserve later work.")

    artifacts = workspace_at_snapshot.get("artifacts")
    current_artifacts = current_workspace.get("artifacts")
    if (
        not isinstance(artifacts, list)
        or len(artifacts) != 1
        or current_artifacts != artifacts
        or not isinstance(artifacts[0], dict)
    ):
        raise RuntimeError("Project workspace capture has invalid artifact evidence.")
    artifact = artifacts[0]
    artifact_digest = capture.get("artifact_sha256")
    if (
        not isinstance(artifact_digest, str)
        or not re.fullmatch(r"[a-f0-9]{64}", artifact_digest)
        or artifact.get("content_digest") != artifact_digest
        or type(artifact.get("byte_count")) is not int
    ):
        raise RuntimeError("Project workspace capture has an invalid artifact digest.")

    manifest = export_bundle.get("manifest")
    files = export_bundle.get("files")
    if not isinstance(manifest, dict) or not isinstance(files, list) or len(files) != 1:
        raise RuntimeError("Project workspace capture has an invalid evidence export.")
    export_material = manifest.get("export")
    if (
        not isinstance(export_material, dict)
        or export_material.get("project_id") != project_id
        or export_material.get("snapshot_id") != snapshot.get("snapshot_id")
        or export_material.get("snapshot_digest") != snapshot.get("snapshot_digest")
        or export_material.get("snapshot_record") != snapshot
        or export_material.get("workspace_record") != workspace_at_snapshot
    ):
        raise RuntimeError("Project evidence export is not bound to its snapshot.")
    exported_file = files[0]
    if not isinstance(exported_file, dict):
        raise RuntimeError("Project evidence export file is invalid.")
    try:
        exported_bytes = base64.b64decode(
            exported_file.get("content_base64", ""), validate=True
        )
    except (ValueError, TypeError):
        raise RuntimeError("Project evidence export file is not valid base64.") from None
    if (
        exported_file.get("artifact_id") != artifact.get("artifact_id")
        or exported_file.get("artifact_version") != artifact.get("artifact_version")
        or exported_file.get("logical_path") != artifact.get("logical_path")
        or len(exported_bytes) != artifact.get("byte_count")
        or hashlib.sha256(exported_bytes).hexdigest() != artifact_digest
    ):
        raise RuntimeError("Project evidence export file changed artifact meaning.")
    return copy.deepcopy(capture)


def _project_learning_evidence_without_learner(
    document: dict[str, Any],
) -> dict[str, Any]:
    safe = copy.deepcopy(document)
    safe.pop("learner_id", None)
    return safe


def _project_learning_outcome_without_learner(
    document: dict[str, Any],
) -> dict[str, Any]:
    safe = copy.deepcopy(document)
    evidence = safe.get("evidence")
    if isinstance(evidence, dict):
        safe["evidence"] = _project_learning_evidence_without_learner(evidence)
    return safe


def stable_project_learning_completion(
    document: dict[str, Any],
) -> dict[str, Any]:
    required = {
        "projection_version",
        "project_id",
        "completed",
        "completion_meaning",
        "source_digest",
        "rebuilt_at",
        "history",
    }
    if set(document) != required:
        raise RuntimeError("Project completion has an invalid public shape.")
    if (
        document.get("projection_version") != "1.0.0"
        or document.get("completed") is not True
        or document.get("completion_meaning")
        != "bounded_project_activity_completed"
        or not isinstance(document.get("source_digest"), str)
        or not re.fullmatch(r"[a-f0-9]{64}", document["source_digest"])
        or not isinstance(document.get("rebuilt_at"), str)
        or not UTC_TIMESTAMP.fullmatch(document["rebuilt_at"])
        or not isinstance(document.get("history"), list)
        or len(document["history"]) != 2
    ):
        raise RuntimeError("Project completion has invalid retained meaning.")
    return {
        key: copy.deepcopy(value)
        for key, value in document.items()
        if key != "rebuilt_at"
    }


def load_project_learning_capture(
    path: Path,
    *,
    data_root: Path,
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("The bounded Project learning capture is absent.")
    resolved = path.resolve()
    if resolved.parent != data_root.resolve() or resolved.stat().st_size > 2_097_152:
        raise RuntimeError("Project learning capture escaped its bounded root.")
    capture = json.loads(resolved.read_text(encoding="utf-8"))
    if (
        not isinstance(capture, dict)
        or set(capture) != PROJECT_LEARNING_CAPTURE_ROOT_KEYS
    ):
        raise RuntimeError("Project learning capture has an invalid shape.")
    leaked = PRIVATE_PROJECT_LEARNING_CAPTURE_KEYS & _nested_mapping_keys(capture)
    if leaked:
        raise RuntimeError("Project learning capture contains private runtime data.")

    project = capture.get("project")
    project_id = project.get("project_id") if isinstance(project, dict) else None
    origin = project.get("origin") if isinstance(project, dict) else None
    independent_project_id = capture.get("independent_project_id")
    if (
        not isinstance(project_id, str)
        or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", project_id)
        or project.get("schema_version") != "1.0.0"
        or not isinstance(origin, dict)
        or origin.get("origin_type") != "learning"
        or not isinstance(independent_project_id, str)
        or not re.fullmatch(
            r"[a-z0-9][a-z0-9._-]{0,127}", independent_project_id
        )
        or independent_project_id == project_id
    ):
        raise RuntimeError("Project learning capture has invalid Project identity.")

    collections = {
        key: capture.get(key)
        for key in (
            "snapshots",
            "candidates",
            "submission_intents",
            "outcomes",
            "evidence",
        )
    }
    if any(not isinstance(value, list) or len(value) != 2 for value in collections.values()):
        raise RuntimeError("Project learning capture requires two correlated submissions.")
    snapshots = collections["snapshots"]
    candidates = collections["candidates"]
    intents = collections["submission_intents"]
    outcomes = collections["outcomes"]
    evidence_records = collections["evidence"]
    if not all(
        isinstance(item, dict)
        for collection in collections.values()
        for item in collection
    ):
        raise RuntimeError("Project learning capture documents must be objects.")

    for index in range(2):
        snapshot = snapshots[index]
        candidate = candidates[index]
        intent = intents[index]
        outcome = outcomes[index]
        evidence = evidence_records[index]
        candidate_project = candidate.get("project")
        source = intent.get("source")
        validation = outcome.get("validation")
        outcome_evidence = outcome.get("evidence")
        if (
            not isinstance(candidate_project, dict)
            or not isinstance(source, dict)
            or snapshot.get("snapshot_id") != candidate_project.get("snapshot_id")
            or snapshot.get("snapshot_digest")
            != candidate_project.get("snapshot_digest")
            or candidate_project.get("project_id") != project_id
            or source.get("project_id") != project_id
            or source.get("snapshot_id") != snapshot.get("snapshot_id")
            or source.get("snapshot_digest") != snapshot.get("snapshot_digest")
            or intent.get("policy_id") != "assessment-project-closure"
            or intent.get("policy_version") != "1.0.0"
            or not isinstance(intent.get("submission_id"), str)
            or not isinstance(validation, dict)
            or validation.get("status") != "accepted"
            or not isinstance(outcome_evidence, dict)
            or outcome_evidence != evidence
            or evidence.get("project_id") != project_id
            or evidence.get("snapshot_id") != snapshot.get("snapshot_id")
            or evidence.get("snapshot_digest") != snapshot.get("snapshot_digest")
            or evidence.get("submission_id") != intent.get("submission_id")
            or evidence.get("occurrence") != index + 1
            or not isinstance(evidence.get("request_fingerprint"), str)
            or validation.get("request_fingerprint")
            != evidence.get("request_fingerprint")
        ):
            raise RuntimeError("Project learning capture changed submission meaning.")
        milestones = candidate.get("milestones")
        resources = candidate.get("resources")
        mappings = intent.get("milestone_evidence")
        if (
            not isinstance(milestones, list)
            or len(milestones) != 2
            or not isinstance(resources, list)
            or len(resources) < 4 + index
            or not isinstance(mappings, list)
            or len(mappings) != 2
            or [mapping.get("milestone_id") for mapping in mappings]
            != [milestone.get("milestone_id") for milestone in milestones]
            or any(not mapping.get("resources") for mapping in mappings)
        ):
            raise RuntimeError("Project learning capture has incomplete evidence mappings.")

    first_evidence, second_evidence = evidence_records
    if (
        first_evidence.get("supersedes_submission_id") not in (None, "")
        or second_evidence.get("supersedes_submission_id")
        != first_evidence.get("submission_id")
        or snapshots[0].get("snapshot_id") == snapshots[1].get("snapshot_id")
        or snapshots[1].get("workspace_revision", 0)
        <= snapshots[0].get("workspace_revision", 0)
    ):
        raise RuntimeError("Project learning capture lost immutable supersession.")

    exact_replay = capture.get("exact_replay")
    if exact_replay != outcomes[0]:
        raise RuntimeError("Project learning exact replay changed accepted evidence.")
    denial = capture.get("changed_retry_denial")
    if (
        not isinstance(denial, dict)
        or set(denial) != {"status", "document"}
        or denial.get("status") != 409
        or not isinstance(denial.get("document"), dict)
        or denial["document"].get("code") != "conflict"
        or denial["document"].get("error_version") != "1.0"
    ):
        raise RuntimeError("Project learning changed retry was not safely refused.")

    history = capture.get("history")
    completion = capture.get("completion")
    if (
        not isinstance(history, dict)
        or history.get("project_id") != project_id
        or not isinstance(history.get("items"), list)
        or len(history["items"]) != 2
        or [item.get("occurrence") for item in history["items"]] != [1, 2]
        or not isinstance(completion, dict)
        or completion.get("project_id") != project_id
    ):
        raise RuntimeError("Project learning capture has invalid retained history.")
    stable_completion = stable_project_learning_completion(completion)
    if [item.get("submission_id") for item in history["items"]] != [
        evidence.get("submission_id") for evidence in evidence_records
    ] or [item.get("submission_id") for item in stable_completion["history"]] != [
        evidence.get("submission_id") for evidence in evidence_records
    ]:
        raise RuntimeError("Project history and completion sources are uncorrelated.")
    artifact_digest = capture.get("artifact_sha256")
    if (
        not isinstance(artifact_digest, str)
        or not re.fullmatch(r"[a-f0-9]{64}", artifact_digest)
        or not any(
            resource.get("resource_kind") == "artifact"
            and resource.get("content_digest") == artifact_digest
            for candidate in candidates
            for resource in candidate.get("resources", [])
        )
    ):
        raise RuntimeError("Project learning capture lost inert artifact provenance.")
    return copy.deepcopy(capture)


def stable_project_export_bundle(document: dict[str, Any]) -> dict[str, Any]:
    if set(document) != {"files", "manifest"}:
        raise RuntimeError("Project evidence export has an invalid public shape.")
    manifest = document.get("manifest")
    files = document.get("files")
    if (
        not isinstance(manifest, dict)
        or set(manifest)
        != {
            "schema_version",
            "export_id",
            "export_digest",
            "export",
            "generated_at",
        }
        or manifest.get("schema_version") != "1.0.0"
        or not isinstance(manifest.get("export_digest"), str)
        or not isinstance(manifest.get("export"), dict)
        or not isinstance(files, list)
    ):
        raise RuntimeError("Project evidence export has an invalid public shape.")
    return {
        "schema_version": manifest["schema_version"],
        "export_digest": manifest["export_digest"],
        "export": copy.deepcopy(manifest["export"]),
        "files": copy.deepcopy(files),
    }


def observe_headless_project_workspace(
    *,
    origin: str,
    capture: dict[str, Any],
) -> dict[str, Any]:
    expected = copy.deepcopy(capture)
    project = expected["project"]
    current_workspace = expected["current_workspace"]
    snapshot = expected["snapshot"]
    export_bundle = stable_project_export_bundle(expected["export_bundle"])
    project_id = project["project_id"]
    snapshot_id = snapshot["snapshot_id"]
    artifact = current_workspace["artifacts"][0]
    api = f"/api/v1/projects/{project_id}"
    opener = _supported_practice_opener(origin)

    listed = _request_json(opener, origin=origin, path="/api/v1/projects")
    records = listed.get("records")
    if not isinstance(records, list) or project not in records:
        raise RuntimeError("Headless Project list omitted the browser-created Project.")
    observed_project = _request_json(opener, origin=origin, path=api)
    observed_workspace = _request_json(
        opener, origin=origin, path=f"{api}/workspace"
    )
    observed_snapshots = _request_json(
        opener, origin=origin, path=f"{api}/snapshots"
    )
    observed_snapshot = _request_json(
        opener,
        origin=origin,
        path=f"{api}/snapshots/{snapshot_id}",
    )
    observed_export = _request_json(
        opener,
        origin=origin,
        path=f"{api}/snapshots/{snapshot_id}/export",
    )
    artifact_bytes = _request_bytes(
        opener,
        origin=origin,
        path=(
            f"{api}/artifacts/{artifact['artifact_id']}"
            f"/versions/{artifact['artifact_version']}"
        ),
    )
    if observed_project != project:
        raise RuntimeError("Headless Project shell changed browser-observed meaning.")
    if observed_workspace != current_workspace:
        raise RuntimeError("Headless Project workspace changed browser-observed meaning.")
    if observed_snapshots != {"records": [snapshot]}:
        raise RuntimeError("Headless Project snapshot list changed saved evidence.")
    if observed_snapshot != snapshot:
        raise RuntimeError("Headless Project snapshot changed saved evidence.")
    stable_observed_export = stable_project_export_bundle(observed_export)
    if stable_observed_export != export_bundle:
        raise RuntimeError("Headless Project export changed browser-observed evidence.")
    if (
        len(artifact_bytes) != artifact["byte_count"]
        or hashlib.sha256(artifact_bytes).hexdigest()
        != expected["artifact_sha256"]
    ):
        raise RuntimeError("Headless Project artifact download changed exact bytes.")
    return {
        "project": observed_project,
        "workspace": observed_workspace,
        "snapshot": observed_snapshot,
        "export_bundle": stable_observed_export,
        "artifact_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
    }


def _request_json_read_status(
    opener: urllib.request.OpenerDirector,
    *,
    origin: str,
    path: str,
) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(
        f"{origin}{path}",
        headers={"Accept": "application/json"},
        method="GET",
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
        raise RuntimeError(f"Headless API request returned a non-object: GET {path}.")
    return status, document


def _platform_help_digest(value: object, *, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[a-f0-9]{64}", value) is None:
        raise RuntimeError(f"{label} is not a lowercase SHA-256 digest.")
    return value


def _stable_platform_help_publication(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeError("Platform Help publication facts are unavailable.")
    _exact_keys(
        value,
        frozenset({"state", "reviewed_on", "updated_at"}),
        "Platform Help publication",
    )
    if (
        value.get("state") != "approved"
        or not isinstance(value.get("reviewed_on"), str)
        or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value["reviewed_on"]) is None
        or not isinstance(value.get("updated_at"), str)
        or re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})",
            value["updated_at"],
        )
        is None
        or value["reviewed_on"] > value["updated_at"][:10]
    ):
        raise RuntimeError("Platform Help publication facts are inconsistent.")
    return copy.deepcopy(value)


def _stable_platform_help_sources(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not 1 <= len(value) <= 20:
        raise RuntimeError("Platform Help source facts are unavailable.")
    observed: list[dict[str, Any]] = []
    source_keys: set[str] = set()
    for source in value:
        if not isinstance(source, dict):
            raise RuntimeError("Platform Help source fact is not an object.")
        _exact_keys(
            source,
            frozenset(
                {
                    "source_key",
                    "title",
                    "area",
                    "source_version",
                    "content_fingerprint",
                }
            ),
            "Platform Help source fact",
        )
        source_key = source.get("source_key")
        if (
            not isinstance(source_key, str)
            or source_key in source_keys
            or not isinstance(source.get("title"), str)
            or not isinstance(source.get("source_version"), str)
            or source.get("area")
            not in {"product", "domain", "contract", "architecture", "risk", "method"}
        ):
            raise RuntimeError("Platform Help source fact is invalid or duplicated.")
        _platform_help_digest(
            source.get("content_fingerprint"),
            label="Platform Help source fingerprint",
        )
        source_keys.add(source_key)
        observed.append(copy.deepcopy(source))
    return observed


def stable_contextual_help(
    value: dict[str, Any],
    *,
    context_key: str,
    context_version: str = "1.0.0",
) -> dict[str, Any]:
    _exact_keys(value, CONTEXTUAL_HELP_ROOT_KEYS, "Contextual Help document")
    if (
        value.get("schema_version") != "1.0.0"
        or value.get("context_key") != context_key
        or value.get("context_version") != context_version
        or re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,63}", context_key) is None
        or re.fullmatch(
            r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)",
            context_version,
        )
        is None
        or not isinstance(value.get("feature_label"), str)
        or not 1 <= len(value["feature_label"]) <= 160
    ):
        raise RuntimeError("Contextual Help identity is invalid.")

    applicability = value.get("applicability")
    if not isinstance(applicability, list) or not 1 <= len(applicability) <= 20:
        raise RuntimeError("Contextual Help applicability is invalid.")
    scope_keys: set[str] = set()
    for item in applicability:
        if not isinstance(item, dict):
            raise RuntimeError("Contextual Help applicability is not an object.")
        _exact_keys(
            item,
            frozenset({"scope_key", "label"}),
            "Contextual Help applicability",
        )
        scope_key = item.get("scope_key")
        if (
            not isinstance(scope_key, str)
            or re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,63}", scope_key) is None
            or scope_key in scope_keys
            or not isinstance(item.get("label"), str)
            or not 1 <= len(item["label"]) <= 160
        ):
            raise RuntimeError("Contextual Help applicability is invalid or duplicated.")
        scope_keys.add(scope_key)

    references = value.get("help_references")
    if not isinstance(references, list) or not 1 <= len(references) <= 10:
        raise RuntimeError("Contextual Help references are invalid.")
    identities: set[str] = set()
    purposes: set[str] = set()
    for reference in references:
        if not isinstance(reference, dict):
            raise RuntimeError("Contextual Help reference is not an object.")
        _exact_keys(
            reference,
            CONTEXTUAL_HELP_REFERENCE_KEYS,
            "Contextual Help reference",
        )
        topic_id = reference.get("topic_id")
        topic_version = reference.get("topic_version")
        purpose = reference.get("purpose")
        identity = f"{topic_id}@{topic_version}"
        if (
            not isinstance(topic_id, str)
            or re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,63}", topic_id) is None
            or not isinstance(topic_version, str)
            or re.fullmatch(
                r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)",
                topic_version,
            )
            is None
            or purpose not in CONTEXTUAL_HELP_PURPOSES
            or identity in identities
            or purpose in purposes
            or not isinstance(reference.get("label"), str)
            or not 1 <= len(reference["label"]) <= 160
        ):
            raise RuntimeError("Contextual Help reference is invalid or duplicated.")
        identities.add(identity)
        purposes.add(purpose)

    _stable_platform_help_publication(value.get("publication"))
    _stable_platform_help_sources(value.get("source_references"))
    _platform_help_digest(
        value.get("context_digest"), label="Contextual Help context digest"
    )
    return copy.deepcopy(value)


def _stable_platform_help_result(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeError("Platform Help search result is not an object.")
    allowed = PLATFORM_HELP_RESULT_KEYS | {"glossary_term"}
    if not PLATFORM_HELP_RESULT_KEYS.issubset(value) or not set(value).issubset(allowed):
        raise RuntimeError("Platform Help search result is not closed.")
    if (
        not isinstance(value.get("topic_id"), str)
        or re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,63}", value["topic_id"]) is None
        or not isinstance(value.get("topic_version"), str)
        or re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", value["topic_version"])
        is None
        or value.get("topic_kind")
        not in {"glossary", "help", "method", "limitation", "troubleshooting"}
        or not isinstance(value.get("title"), str)
        or not isinstance(value.get("summary"), str)
        or not isinstance(value.get("applicability"), list)
        or not value["applicability"]
    ):
        raise RuntimeError("Platform Help search result identity is invalid.")
    _stable_platform_help_publication(value.get("publication"))
    _stable_platform_help_sources(value.get("source_references"))
    _platform_help_digest(value.get("topic_digest"), label="Platform Help topic digest")
    return copy.deepcopy(value)


def stable_platform_help_search(
    value: dict[str, Any],
    *,
    query: str,
    topic_kind: str | None = None,
) -> dict[str, Any]:
    expected_keys = PLATFORM_HELP_SEARCH_KEYS | ({"topic_kind"} if topic_kind else set())
    _exact_keys(value, frozenset(expected_keys), "Platform Help search page")
    if (
        value.get("schema_version") != "1.0.0"
        or value.get("query") != query
        or value.get("topic_kind") != topic_kind
        or not isinstance(value.get("results"), list)
        or len(value["results"]) > 50
        or (
            value.get("next_cursor") is not None
            and (
                not isinstance(value["next_cursor"], str)
                or re.fullmatch(r"[A-Za-z0-9_-]{1,4096}", value["next_cursor"])
                is None
            )
        )
    ):
        raise RuntimeError("Platform Help search page is invalid.")
    _platform_help_digest(value.get("corpus_digest"), label="Platform Help corpus digest")
    results = [_stable_platform_help_result(item) for item in value["results"]]
    identities = [f"{item['topic_id']}@{item['topic_version']}" for item in results]
    if len(identities) != len(set(identities)):
        raise RuntimeError("Platform Help search page has duplicate exact topics.")
    return copy.deepcopy(value)


def stable_platform_help_topic(
    value: dict[str, Any],
    *,
    topic_id: str,
    topic_version: str,
) -> dict[str, Any]:
    required = PLATFORM_HELP_TOPIC_KEYS
    allowed = required | {"glossary_term"}
    if not required.issubset(value) or not set(value).issubset(allowed):
        raise RuntimeError("Platform Help topic is not closed.")
    if (
        value.get("schema_version") != "1.0.0"
        or value.get("topic_id") != topic_id
        or value.get("topic_version") != topic_version
        or not isinstance(value.get("keywords"), list)
        or not isinstance(value.get("body"), list)
        or not value["body"]
        or not isinstance(value.get("related_topics"), list)
    ):
        raise RuntimeError("Platform Help exact topic identity is inconsistent.")
    _stable_platform_help_result(
        {key: copy.deepcopy(item) for key, item in value.items() if key in PLATFORM_HELP_RESULT_KEYS or key == "glossary_term"}
    )
    allowed_nodes = {"heading", "paragraph", "list", "note", "topic_reference"}
    if any(
        not isinstance(node, dict) or node.get("node_kind") not in allowed_nodes
        for node in value["body"]
    ):
        raise RuntimeError("Platform Help topic contains an unsafe body node.")
    relations: set[str] = set()
    for relation in value["related_topics"]:
        if (
            not isinstance(relation, dict)
            or set(relation) != {"topic_id", "topic_version", "relationship"}
            or relation.get("relationship") not in {"see_also", "prerequisite", "explains"}
        ):
            raise RuntimeError("Platform Help relation is invalid.")
        identity = f"{relation.get('topic_id')}@{relation.get('topic_version')}"
        if identity in relations:
            raise RuntimeError("Platform Help relation is duplicated.")
        relations.add(identity)
    return copy.deepcopy(value)


def load_platform_help_capture(path: Path, *, data_root: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("The bounded Platform Help capture is absent.")
    resolved = path.resolve()
    if resolved.parent != data_root.resolve() or resolved.stat().st_size > 1_048_576:
        raise RuntimeError("Platform Help capture escaped its bounded root.")
    capture = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(capture, dict) or set(capture) != PLATFORM_HELP_CAPTURE_ROOT_KEYS:
        raise RuntimeError("Platform Help capture has an invalid shape.")
    if capture.get("schema_version") != "1.0.0":
        raise RuntimeError("Platform Help capture version is unsupported.")
    pages = {
        "first_page": stable_platform_help_search(capture["first_page"], query=""),
        "continued_page": stable_platform_help_search(capture["continued_page"], query=""),
        "searched_page": stable_platform_help_search(capture["searched_page"], query="methods"),
        "approved_search": stable_platform_help_search(capture["approved_search"], query="approved help"),
        "limitation_page": stable_platform_help_search(
            capture["limitation_page"], query="", topic_kind="limitation"
        ),
        "limitation_continuation": stable_platform_help_search(
            capture["limitation_continuation"], query="", topic_kind="limitation"
        ),
    }
    topics = {
        "method_topic": stable_platform_help_topic(
            capture["method_topic"], topic_id="platform-methods", topic_version="1.0.0"
        ),
        "approved_topic": stable_platform_help_topic(
            capture["approved_topic"], topic_id="approved-help", topic_version="1.0.0"
        ),
        "related_topic": stable_platform_help_topic(
            capture["related_topic"], topic_id="education-not-advice", topic_version="1.0.0"
        ),
    }
    captured_contexts = capture.get("contexts")
    if (
        not isinstance(captured_contexts, dict)
        or set(captured_contexts) != set(CONTEXTUAL_HELP_KEYS)
    ):
        raise RuntimeError("Contextual Help capture does not contain every feature context.")
    contexts = {
        context_key: stable_contextual_help(
            captured_contexts[context_key], context_key=context_key
        )
        for context_key in CONTEXTUAL_HELP_KEYS
    }
    expected_topic_identities = {
        f"{reference['topic_id']}@{reference['topic_version']}"
        for context in contexts.values()
        for reference in context["help_references"]
    }
    captured_context_topics = capture.get("context_topics")
    if (
        not isinstance(captured_context_topics, dict)
        or set(captured_context_topics) != expected_topic_identities
    ):
        raise RuntimeError("Contextual Help capture does not bind every exact topic.")
    context_topics: dict[str, dict[str, Any]] = {}
    for identity in sorted(expected_topic_identities):
        topic_id, topic_version = identity.split("@", maxsplit=1)
        context_topics[identity] = stable_platform_help_topic(
            captured_context_topics[identity],
            topic_id=topic_id,
            topic_version=topic_version,
        )
    corpus_digests = {page["corpus_digest"] for page in pages.values()}
    if len(corpus_digests) != 1:
        raise RuntimeError("Platform Help pages disagree on the corpus digest.")
    first = pages["first_page"]
    continued = pages["continued_page"]
    limitation = pages["limitation_page"]
    limitation_continued = pages["limitation_continuation"]
    if (
        len(first["results"]) != 1
        or not first["next_cursor"]
        or len(continued["results"]) != 1
        or first["results"][0]["topic_id"] == continued["results"][0]["topic_id"]
        or len(limitation["results"]) != 1
        or not limitation["next_cursor"]
        or len(limitation_continued["results"]) != 1
        or limitation["results"][0]["topic_id"]
        == limitation_continued["results"][0]["topic_id"]
    ):
        raise RuntimeError("Platform Help capture does not prove bounded continuation.")
    if [item["topic_id"] for item in pages["approved_search"]["results"]] != [
        "approved-help"
    ] or "platform-methods" not in {
        item["topic_id"] for item in pages["searched_page"]["results"]
    }:
        raise RuntimeError("Platform Help capture does not bind its searches.")
    if not any(
        relation.get("topic_id") == "education-not-advice"
        and relation.get("topic_version") == "1.0.0"
        for relation in topics["approved_topic"]["related_topics"]
    ):
        raise RuntimeError("Platform Help exact relation is absent.")
    for context in contexts.values():
        for reference in context["help_references"]:
            identity = f"{reference['topic_id']}@{reference['topic_version']}"
            if identity not in context_topics:
                raise RuntimeError("Contextual Help exact topic correlation is absent.")
    expected = capture.get("expected")
    if expected != {"external_request_count": 0, "guidance_methods": ["GET"]}:
        raise RuntimeError("Platform Help request containment was not observed.")
    private_keys = PLATFORM_HELP_PRIVATE_KEYS & _nested_mapping_keys(capture)
    if private_keys:
        raise RuntimeError("Platform Help capture contains private fields.")
    return copy.deepcopy(capture)


def _platform_help_path(query: dict[str, object]) -> str:
    encoded = urllib.parse.urlencode(query)
    return f"/api/v1/guidance/platform-help?{encoded}" if encoded else "/api/v1/guidance/platform-help"


def observe_headless_platform_help(
    *,
    origin: str,
    capture: dict[str, Any],
) -> dict[str, Any]:
    unauthenticated = urllib.request.build_opener()
    status, denial = _request_json_read_status(
        unauthenticated,
        origin=origin,
        path="/api/v1/guidance/platform-help?page_size=1",
    )
    _exact_keys(
        denial,
        frozenset({"error_version", "code", "message", "correlation_id"}),
        "Platform Help authorization denial",
    )
    serialized_denial = json.dumps(denial, sort_keys=True).casefold()
    if (
        status != 401
        or denial.get("code") != "unauthorized"
        or any(
            marker in serialized_denial
            for marker in (
                "approved-help",
                "corpus_digest",
                "content_fingerprint",
                "platform-methods",
                "topic_digest",
            )
        )
    ):
        raise RuntimeError("Platform Help authorization denial exposed corpus facts.")

    context_status, context_denial = _request_json_read_status(
        unauthenticated,
        origin=origin,
        path=(
            "/api/v1/guidance/contextual-help/lesson-publication/"
            "versions/1.0.0"
        ),
    )
    _exact_keys(
        context_denial,
        frozenset({"error_version", "code", "message", "correlation_id"}),
        "Contextual Help authorization denial",
    )
    serialized_context_denial = json.dumps(
        context_denial, sort_keys=True
    ).casefold()
    if (
        context_status != 401
        or context_denial.get("code") != "unauthorized"
        or any(
            marker in serialized_context_denial
            for marker in (
                "context_digest",
                "education-not-advice",
                "lesson-publication",
                "source-and-history",
            )
        )
    ):
        raise RuntimeError(
            "Contextual Help authorization denial exposed registry facts."
        )

    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
    _request_json(
        opener,
        origin=origin,
        path="/api/v1/session/single-profile",
        method="POST",
        payload={"limitation_acknowledged": True},
    )
    first = stable_platform_help_search(
        _request_json(
            opener,
            origin=origin,
            path=_platform_help_path({"page_size": 1}),
        ),
        query="",
    )
    continued = stable_platform_help_search(
        _request_json(
            opener,
            origin=origin,
            path=_platform_help_path(
                {"page_size": 1, "cursor": first["next_cursor"]}
            ),
        ),
        query="",
    )
    searched = stable_platform_help_search(
        _request_json(
            opener,
            origin=origin,
            path=_platform_help_path({"query": "methods", "page_size": 20}),
        ),
        query="methods",
    )
    approved_search = stable_platform_help_search(
        _request_json(
            opener,
            origin=origin,
            path=_platform_help_path({"query": "approved help", "page_size": 20}),
        ),
        query="approved help",
    )
    limitation = stable_platform_help_search(
        _request_json(
            opener,
            origin=origin,
            path=_platform_help_path({"topic_kind": "limitation", "page_size": 1}),
        ),
        query="",
        topic_kind="limitation",
    )
    limitation_continued = stable_platform_help_search(
        _request_json(
            opener,
            origin=origin,
            path=_platform_help_path(
                {
                    "topic_kind": "limitation",
                    "page_size": 1,
                    "cursor": limitation["next_cursor"],
                }
            ),
        ),
        query="",
        topic_kind="limitation",
    )
    topics = {
        "method_topic": stable_platform_help_topic(
            _request_json(
                opener,
                origin=origin,
                path="/api/v1/guidance/platform-help/platform-methods/versions/1.0.0",
            ),
            topic_id="platform-methods",
            topic_version="1.0.0",
        ),
        "approved_topic": stable_platform_help_topic(
            _request_json(
                opener,
                origin=origin,
                path="/api/v1/guidance/platform-help/approved-help/versions/1.0.0",
            ),
            topic_id="approved-help",
            topic_version="1.0.0",
        ),
        "related_topic": stable_platform_help_topic(
            _request_json(
                opener,
                origin=origin,
                path="/api/v1/guidance/platform-help/education-not-advice/versions/1.0.0",
            ),
            topic_id="education-not-advice",
            topic_version="1.0.0",
        ),
    }
    contexts = {
        context_key: stable_contextual_help(
            _request_json(
                opener,
                origin=origin,
                path=(
                    f"/api/v1/guidance/contextual-help/{context_key}/"
                    "versions/1.0.0"
                ),
            ),
            context_key=context_key,
        )
        for context_key in CONTEXTUAL_HELP_KEYS
    }
    exact_topic_identities = {
        f"{reference['topic_id']}@{reference['topic_version']}"
        for context in contexts.values()
        for reference in context["help_references"]
    }
    context_topics: dict[str, dict[str, Any]] = {}
    for identity in sorted(exact_topic_identities):
        topic_id, topic_version = identity.split("@", maxsplit=1)
        context_topics[identity] = stable_platform_help_topic(
            _request_json(
                opener,
                origin=origin,
                path=(
                    f"/api/v1/guidance/platform-help/{topic_id}/"
                    f"versions/{topic_version}"
                ),
            ),
            topic_id=topic_id,
            topic_version=topic_version,
        )
    observed = {
        "first_page": first,
        "continued_page": continued,
        "searched_page": searched,
        "approved_search": approved_search,
        **topics,
        "limitation_page": limitation,
        "limitation_continuation": limitation_continued,
        "contexts": contexts,
        "context_topics": context_topics,
    }
    expected = {key: capture[key] for key in observed}
    if observed != expected:
        raise RuntimeError("Headless Platform Help changed browser-observed meaning.")
    return observed


def assert_platform_help_restart_result(
    *,
    before_restart: dict[str, Any],
    after_restart: dict[str, Any],
) -> None:
    if after_restart != before_restart:
        raise RuntimeError("Platform Help changed after normal restart.")


def _project_summary_without_learner(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": document.get("schema_version"),
        "project_id": document.get("project_id"),
        "title": document.get("title"),
        "revision": document.get("revision"),
        "origin": copy.deepcopy(document.get("origin")),
    }


def observe_headless_project_learning(
    *,
    origin: str,
    capture: dict[str, Any],
) -> dict[str, Any]:
    expected = copy.deepcopy(capture)
    project_id = expected["project"]["project_id"]
    api = f"/api/v1/projects/{project_id}"
    opener = _supported_practice_opener(origin)
    project = _request_json(opener, origin=origin, path=api)
    if _project_summary_without_learner(project) != expected["project"]:
        raise RuntimeError("Headless Project learning shell changed browser meaning.")

    candidates = []
    for snapshot in expected["snapshots"]:
        candidates.append(
            _request_json(
                opener,
                origin=origin,
                path=(
                    f"{api}/snapshots/{snapshot['snapshot_id']}"
                    "/submission-candidate"
                ),
            )
        )
    if candidates != expected["candidates"]:
        raise RuntimeError("Headless Project candidates changed browser meaning.")

    history = _request_json(opener, origin=origin, path=f"{api}/submissions")
    completion = _request_json(opener, origin=origin, path=f"{api}/completion")
    evidence = [
        _project_learning_evidence_without_learner(
            _request_json(
                opener,
                origin=origin,
                path=f"{api}/submissions/{record['submission_id']}",
            )
        )
        for record in expected["evidence"]
    ]
    if history != expected["history"] or evidence != expected["evidence"]:
        raise RuntimeError("Headless Project retained evidence changed browser meaning.")
    if stable_project_learning_completion(completion) != (
        stable_project_learning_completion(expected["completion"])
    ):
        raise RuntimeError("Headless Project completion changed browser meaning.")

    replayed = []
    for snapshot, intent, outcome in zip(
        expected["snapshots"],
        expected["submission_intents"],
        expected["outcomes"],
        strict=True,
    ):
        replay = _request_json(
            opener,
            origin=origin,
            path=(
                f"{api}/snapshots/{snapshot['snapshot_id']}/submissions"
            ),
            method="POST",
            payload=intent,
        )
        safe_replay = _project_learning_outcome_without_learner(replay)
        if safe_replay != outcome:
            raise RuntimeError("Headless Project exact replay changed evidence.")
        replayed.append(safe_replay)

    independent_path = (
        f"/api/v1/projects/{expected['independent_project_id']}/completion"
    )
    denial_status, denial = _request_json_read_status(
        opener,
        origin=origin,
        path=independent_path,
    )
    if (
        denial_status != 404
        or denial.get("error_version") != "1.0"
        or denial.get("code") != "not_found"
        or PRIVATE_PROJECT_LEARNING_CAPTURE_KEYS & _nested_mapping_keys(denial)
    ):
        raise RuntimeError("Independent Project gained learning meaning.")

    return {
        "project": _project_summary_without_learner(project),
        "candidates": candidates,
        "history": history,
        "completion": stable_project_learning_completion(completion),
        "evidence": evidence,
        "exact_replays": replayed,
        "independent_denial": {
            "status": denial_status,
            "code": denial.get("code"),
        },
    }


def project_learning_storage_snapshot(
    postgres_dsn: str,
    *,
    project_id: str,
) -> dict[str, Any]:
    with psycopg.connect(postgres_dsn) as connection:
        submissions = connection.execute(
            """
            SELECT evidence_id, submission_id, snapshot_id,
                   request_fingerprint, occurrence, accepted_sequence,
                   supersedes_submission_id
              FROM assessment.project_submissions
             WHERE project_id = %s
             ORDER BY occurrence
            """,
            (project_id,),
        ).fetchall()
        events = connection.execute(
            """
            SELECT event.event_id, event.evidence_id
              FROM assessment.project_outbox AS event
              JOIN assessment.project_submissions AS submission
                ON submission.evidence_id = event.evidence_id
             WHERE submission.project_id = %s
             ORDER BY submission.occurrence
            """,
            (project_id,),
        ).fetchall()
        projections = connection.execute(
            """
            SELECT completed, history_count, source_digest
              FROM learner_model.project_completion_projections
             WHERE project_id = %s
            """,
            (project_id,),
        ).fetchall()
        history = connection.execute(
            """
            SELECT event_id, evidence_id, submission_id, snapshot_id,
                   request_fingerprint, occurrence, accepted_sequence,
                   supersedes_submission_id
              FROM learner_model.project_completion_history
             WHERE project_id = %s
             ORDER BY occurrence
            """,
            (project_id,),
        ).fetchall()
        audit = connection.execute(
            """
            SELECT event_id, evidence_id, submission_id, snapshot_id,
                   occurrence, supersedes_submission_id, integrity_digest
              FROM audit.project_completion_records
             WHERE project_id = %s
             ORDER BY occurrence
            """,
            (project_id,),
        ).fetchall()
    return {
        "submissions": [list(row) for row in submissions],
        "events": [list(row) for row in events],
        "projections": [list(row) for row in projections],
        "history": [list(row) for row in history],
        "audit": [list(row) for row in audit],
    }


def assert_project_learning_storage(
    storage: dict[str, Any],
    *,
    capture: dict[str, Any],
) -> None:
    evidence = capture["evidence"]
    completion_history = capture["completion"]["history"]
    if any(
        not isinstance(storage.get(key), list)
        for key in ("submissions", "events", "projections", "history", "audit")
    ):
        raise RuntimeError("Project learning storage evidence is unavailable.")
    if (
        len(storage["submissions"]) != 2
        or len(storage["events"]) != 2
        or len(storage["projections"]) != 1
        or len(storage["history"]) != 2
        or len(storage["audit"]) != 2
    ):
        raise RuntimeError("Project learning storage counts are incomplete.")
    for index in range(2):
        submission = storage["submissions"][index]
        projected = storage["history"][index]
        audited = storage["audit"][index]
        source = completion_history[index]
        expected = evidence[index]
        if submission[:3] != [
            expected["evidence_id"],
            expected["submission_id"],
            expected["snapshot_id"],
        ] or submission[3:] != [
            expected["request_fingerprint"],
            index + 1,
            expected["accepted_sequence"],
            expected.get("supersedes_submission_id"),
        ]:
            raise RuntimeError("Assessment Project evidence is uncorrelated.")
        if storage["events"][index] != [source["event_id"], expected["evidence_id"]]:
            raise RuntimeError("Assessment Project event is uncorrelated.")
        if projected[:7] != [
            source["event_id"],
            expected["evidence_id"],
            expected["submission_id"],
            expected["snapshot_id"],
            expected["request_fingerprint"],
            index + 1,
            expected["accepted_sequence"],
        ] or projected[7] != expected.get("supersedes_submission_id"):
            raise RuntimeError("Learner-model Project history is uncorrelated.")
        if audited[:6] != [
            source["event_id"],
            expected["evidence_id"],
            expected["submission_id"],
            expected["snapshot_id"],
            index + 1,
            expected.get("supersedes_submission_id"),
        ] or not re.fullmatch(r"[a-f0-9]{64}", str(audited[6])):
            raise RuntimeError("Audit Project reference is uncorrelated.")
    projection = storage["projections"][0]
    if projection != [True, 2, capture["completion"]["source_digest"]]:
        raise RuntimeError("Project completion projection is uncorrelated.")


def assert_project_learning_restart_result(
    *,
    before_observation: dict[str, Any],
    after_observation: dict[str, Any],
    before_storage: dict[str, Any],
    after_storage: dict[str, Any],
) -> None:
    if after_observation != before_observation:
        raise RuntimeError("Project learning evidence changed after normal restart.")
    if after_storage != before_storage:
        raise RuntimeError("Project learning storage changed during restart replay.")


def _schema_state_fingerprint(
    connection: psycopg.Connection[Any],
    *,
    schema: str,
) -> dict[str, Any]:
    tables = [
        str(row[0])
        for row in connection.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """,
            (schema,),
        ).fetchall()
    ]
    digest = hashlib.sha256()
    row_count = 0
    for table in tables:
        digest.update(f"{schema}.{table}\0".encode("utf-8"))
        rows = connection.execute(
            sql.SQL(
                "SELECT to_jsonb(row_value)::text "
                "FROM {}.{} AS row_value "
                "ORDER BY to_jsonb(row_value)::text"
            ).format(sql.Identifier(schema), sql.Identifier(table))
        ).fetchall()
        row_count += len(rows)
        digest.update(f"{len(rows)}\0".encode("ascii"))
        for row in rows:
            digest.update(str(row[0]).encode("utf-8"))
            digest.update(b"\0")
    return {
        "table_count": len(tables),
        "row_count": row_count,
        "sha256": digest.hexdigest(),
    }


def _schema_catalog_fingerprint(
    connection: psycopg.Connection[Any],
    *,
    schema: str,
) -> dict[str, Any]:
    catalog_queries = {
        "columns": """
            SELECT table_name, ordinal_position, column_name, data_type,
                   udt_schema, udt_name, is_nullable,
                   COALESCE(column_default, ''), is_identity,
                   COALESCE(identity_generation, '')
            FROM information_schema.columns
            WHERE table_schema = %s
            ORDER BY table_name, ordinal_position
        """,
        "constraints": """
            SELECT relation.relname, constraint_record.conname,
                   constraint_record.contype,
                   pg_get_constraintdef(constraint_record.oid, true)
            FROM pg_constraint AS constraint_record
            JOIN pg_class AS relation
              ON relation.oid = constraint_record.conrelid
            JOIN pg_namespace AS namespace
              ON namespace.oid = relation.relnamespace
            WHERE namespace.nspname = %s
            ORDER BY relation.relname, constraint_record.conname
        """,
        "indexes": """
            SELECT tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = %s
            ORDER BY tablename, indexname
        """,
        "sequences": """
            SELECT sequencename, data_type, start_value, min_value, max_value,
                   increment_by, cycle
            FROM pg_sequences
            WHERE schemaname = %s
            ORDER BY sequencename
        """,
        "routines": """
            SELECT procedure_record.proname, procedure_record.prokind,
                   pg_get_function_identity_arguments(procedure_record.oid),
                   pg_get_function_result(procedure_record.oid),
                   pg_get_functiondef(procedure_record.oid)
            FROM pg_proc AS procedure_record
            JOIN pg_namespace AS namespace
              ON namespace.oid = procedure_record.pronamespace
            WHERE namespace.nspname = %s
              AND procedure_record.prokind IN ('f', 'p')
            ORDER BY procedure_record.proname,
                     pg_get_function_identity_arguments(procedure_record.oid)
        """,
        "triggers": """
            SELECT relation.relname, trigger_record.tgname,
                   pg_get_triggerdef(trigger_record.oid, true)
            FROM pg_trigger AS trigger_record
            JOIN pg_class AS relation
              ON relation.oid = trigger_record.tgrelid
            JOIN pg_namespace AS namespace
              ON namespace.oid = relation.relnamespace
            WHERE namespace.nspname = %s
              AND NOT trigger_record.tgisinternal
            ORDER BY relation.relname, trigger_record.tgname
        """,
    }
    digest = hashlib.sha256()
    object_counts: dict[str, int] = {}
    for kind, query in catalog_queries.items():
        rows = connection.execute(query, (schema,)).fetchall()
        object_counts[kind] = len(rows)
        digest.update(f"{kind}\0{len(rows)}\0".encode("utf-8"))
        for row in rows:
            canonical = json.dumps(
                list(row),
                ensure_ascii=False,
                separators=(",", ":"),
                default=str,
            )
            digest.update(canonical.encode("utf-8"))
            digest.update(b"\0")
    return {
        "object_counts": object_counts,
        "sha256": digest.hexdigest(),
    }


def application_database_fingerprint(
    postgres_dsn: str,
    *,
    exclude_schemas: frozenset[str] = frozenset(),
) -> dict[str, dict[str, Any]]:
    with psycopg.connect(postgres_dsn) as connection:
        schemas = [
            str(row[0])
            for row in connection.execute(
                """
                SELECT DISTINCT table_schema
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                  AND table_schema NOT IN ('information_schema', 'pg_catalog')
                  AND table_schema NOT LIKE 'pg\\_%' ESCAPE '\\'
                ORDER BY table_schema
                """
            ).fetchall()
            if str(row[0]) not in exclude_schemas
        ]
        return {
            schema: {
                "catalog": _schema_catalog_fingerprint(connection, schema=schema),
                "data": _schema_state_fingerprint(connection, schema=schema),
            }
            for schema in schemas
        }


def database_fingerprint_digest(
    fingerprint: dict[str, dict[str, Any]],
) -> str:
    material = json.dumps(
        fingerprint,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def application_table_count(postgres_dsn: str) -> int:
    with psycopg.connect(postgres_dsn) as connection:
        row = connection.execute(
            """
            SELECT count(*)
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
              AND table_schema NOT IN ('information_schema', 'pg_catalog')
              AND table_schema NOT LIKE 'pg\\_%' ESCAPE '\\'
            """
        ).fetchone()
    if row is None:
        raise RuntimeError("Recovery target table evidence is unavailable.")
    return int(row[0])


def create_logical_backup(container_name: str, destination: Path) -> dict[str, Any]:
    if not container_name.startswith(CONTAINER_PREFIX):
        raise RuntimeError("Recovery capture requires the runner-owned source database.")
    if destination.exists() or destination.is_symlink():
        raise RuntimeError("Recovery capture destination must be new.")
    resolved_parent = destination.parent.resolve()
    if not resolved_parent.is_relative_to(ARTIFACT_ROOT.resolve()):
        raise RuntimeError("Recovery capture destination escaped the bounded root.")
    with destination.open("xb") as output:
        completed = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                "pg_dump",
                "--format=custom",
                "--no-owner",
                "--no-privileges",
                "--username",
                POSTGRES_USER,
                "--dbname",
                POSTGRES_DATABASE,
            ],
            cwd=REPOSITORY,
            stdout=output,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    if completed.returncode != 0 or not destination.is_file():
        destination.unlink(missing_ok=True)
        raise RuntimeError("The controlled logical database capture failed.")
    content = destination.read_bytes()
    if not content:
        destination.unlink(missing_ok=True)
        raise RuntimeError("The controlled logical database capture is empty.")
    return {
        "byte_count": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def restore_logical_backup(
    *,
    container_name: str,
    postgres_dsn: str,
    source: Path,
    owned_root: Path,
) -> None:
    if not container_name.startswith(RECOVERY_CONTAINER_PREFIX):
        raise RuntimeError("Recovery restore requires the runner-owned target database.")
    bounded_root = ARTIFACT_ROOT.resolve()
    owned_resolved = owned_root.resolve()
    if (
        owned_root.is_symlink()
        or not owned_root.is_dir()
        or owned_resolved.parent != bounded_root
        or source.is_symlink()
        or source.resolve().parent != owned_resolved
    ):
        raise RuntimeError("Recovery restore source escaped its runner-owned root.")
    if application_table_count(postgres_dsn) != 0:
        raise RuntimeError("Recovery target is populated; restore was refused.")
    if not source.is_file() or source.stat().st_size == 0:
        raise RuntimeError("Recovery restore source is invalid.")
    with source.open("rb") as input_stream:
        completed = subprocess.run(
            [
                "docker",
                "exec",
                "--interactive",
                container_name,
                "pg_restore",
                "--exit-on-error",
                "--no-owner",
                "--no-privileges",
                "--username",
                POSTGRES_USER,
                "--dbname",
                POSTGRES_DATABASE,
            ],
            cwd=REPOSITORY,
            stdin=input_stream,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError("The controlled logical database restore failed.")


def assert_populated_target_refusal(
    *,
    container_name: str,
    postgres_dsn: str,
    source: Path,
    owned_root: Path,
) -> None:
    with psycopg.connect(postgres_dsn) as connection:
        connection.execute(
            "CREATE TABLE public.qualification_populated_marker (value integer NOT NULL)"
        )
        connection.execute(
            "INSERT INTO public.qualification_populated_marker (value) VALUES (1)"
        )
    try:
        restore_logical_backup(
            container_name=container_name,
            postgres_dsn=postgres_dsn,
            source=source,
            owned_root=owned_root,
        )
    except RuntimeError as error:
        if str(error) != "Recovery target is populated; restore was refused.":
            raise
    else:
        raise RuntimeError("A populated recovery target was not refused.")
    with psycopg.connect(postgres_dsn) as connection:
        marker = connection.execute(
            "SELECT value FROM public.qualification_populated_marker"
        ).fetchone()
        connection.execute("DROP TABLE public.qualification_populated_marker")
    if marker != (1,) or application_table_count(postgres_dsn) != 0:
        raise RuntimeError("Populated-target refusal changed the recovery target.")


def revoke_restored_sessions(postgres_dsn: str) -> int:
    with psycopg.connect(postgres_dsn) as connection:
        before = connection.execute(
            "SELECT count(*) FROM identity.sessions WHERE revoked_at IS NULL"
        ).fetchone()
        connection.execute(
            "UPDATE identity.sessions SET revoked_at = CURRENT_TIMESTAMP "
            "WHERE revoked_at IS NULL"
        )
        after = connection.execute(
            "SELECT count(*) FROM identity.sessions WHERE revoked_at IS NULL"
        ).fetchone()
    if before is None or int(before[0]) < 1 or after != (0,):
        raise RuntimeError("Restored session revocation could not be proven.")
    return int(before[0])


RECOVERY_PHASES = (
    "source_stopped",
    "source_fingerprinted",
    "backup_created",
    "data_copied",
    "source_unchanged_after_capture",
    "populated_target_refused",
    "empty_target_restored",
    "catalog_and_data_matched",
    "restored_sessions_revoked",
    "old_session_denied",
    "fresh_session_verified",
    "source_and_target_unchanged",
)


def assert_recovery_phase_order(phases: list[str]) -> None:
    if tuple(phases) != RECOVERY_PHASES:
        raise RuntimeError("Recovery qualification phase order is invalid.")


def stable_recovery_report(report: dict[str, Any]) -> dict[str, Any]:
    expected_keys = {
        "backup_byte_count",
        "backup_sha256",
        "database_catalog_and_data_sha256",
        "database_schema_count",
        "data_file_count",
        "data_sha256",
        "empty_target_restored",
        "fresh_session_public_api",
        "old_session_denied",
        "phases",
        "populated_target_refused",
        "qualified",
        "restored_sessions_revoked",
        "source_unchanged",
    }
    if set(report) != expected_keys:
        raise RuntimeError("Recovery qualification report has an invalid shape.")
    if (
        not isinstance(report["backup_byte_count"], int)
        or report["backup_byte_count"] < 1
        or not isinstance(report["database_schema_count"], int)
        or report["database_schema_count"] < 1
        or not isinstance(report["data_file_count"], int)
        or report["data_file_count"] < 0
        or not isinstance(report["restored_sessions_revoked"], int)
        or report["restored_sessions_revoked"] < 1
        or any(
            not isinstance(report[key], str)
            or re.fullmatch(r"[a-f0-9]{64}", report[key]) is None
            for key in (
                "backup_sha256",
                "database_catalog_and_data_sha256",
                "data_sha256",
            )
        )
        or any(
            report[key] is not True
            for key in (
                "empty_target_restored",
                "fresh_session_public_api",
                "old_session_denied",
                "populated_target_refused",
                "qualified",
                "source_unchanged",
            )
        )
        or not isinstance(report["phases"], list)
        or any(not isinstance(phase, str) for phase in report["phases"])
    ):
        raise RuntimeError("Recovery qualification report has invalid evidence.")
    assert_recovery_phase_order(report["phases"])
    return copy.deepcopy(report)


def bounded_file_tree_fingerprint(root: Path) -> dict[str, Any]:
    if root.is_symlink() or not root.is_dir():
        raise RuntimeError("Recovery data root is unavailable.")
    digest = hashlib.sha256()
    file_count = 0
    byte_count = 0
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise RuntimeError("Recovery data root contains a symbolic link.")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        content = path.read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(content)).encode("ascii"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
        file_count += 1
        byte_count += len(content)
    return {
        "file_count": file_count,
        "byte_count": byte_count,
        "sha256": digest.hexdigest(),
    }


def copy_bounded_data_root(source: Path, target: Path) -> dict[str, Any]:
    source_resolved = source.resolve()
    target_parent = target.parent.resolve()
    bounded_root = ARTIFACT_ROOT.resolve()
    if (
        not source_resolved.is_relative_to(bounded_root)
        or not target_parent.is_relative_to(bounded_root)
        or target.exists()
        or target.is_symlink()
    ):
        raise RuntimeError("Recovery data-root copy escaped its bounded target.")
    source_fingerprint = bounded_file_tree_fingerprint(source_resolved)
    shutil.copytree(source_resolved, target)
    target_fingerprint = bounded_file_tree_fingerprint(target)
    if target_fingerprint != source_fingerprint:
        raise RuntimeError("Recovery data-root copy changed accepted bytes.")
    return target_fingerprint


def personal_workspace_storage_snapshot(postgres_dsn: str) -> dict[str, Any]:
    query = """
        SELECT
            (SELECT count(*) FROM personal_workspace.workspaces),
            (SELECT count(*) FROM personal_workspace.mutations),
            (SELECT count(*) FROM content.lesson_package_versions),
            (SELECT count(*) FROM curriculum.lesson_placements),
            (SELECT count(*) FROM curriculum.discovery_projection_records),
            (SELECT count(*) FROM assessment.attempts),
            (SELECT count(*) FROM assessment.practice_attempts),
            (SELECT count(*) FROM assessment.project_submissions),
            (SELECT count(*) FROM learner_model.lesson_completion_projections),
            (SELECT count(*) FROM learner_model.practice_history_projections),
            (SELECT count(*) FROM learner_model.project_completion_projections),
            (SELECT count(*) FROM project.project_shells)
    """
    labels = (
        "personal_workspaces",
        "personal_mutations",
        "content_packages",
        "curriculum_placements",
        "curriculum_discovery_records",
        "assessment_attempts",
        "assessment_practice_attempts",
        "assessment_project_submissions",
        "learner_lesson_projections",
        "learner_practice_projections",
        "learner_project_projections",
        "project_shells",
    )
    with psycopg.connect(postgres_dsn) as connection:
        row = connection.execute(query).fetchone()
        workspace_rows = connection.execute(
            """
            SELECT workspace_id, revision, workspace
            FROM personal_workspace.workspaces
            ORDER BY workspace_id
            """
        ).fetchall()
        mutation_rows = connection.execute(
            """
            SELECT workspace_id, idempotency_key,
                   accepted_workspace, accepted_revision
            FROM personal_workspace.mutations
            ORDER BY accepted_revision, idempotency_key
            """
        ).fetchall()
        target_state = {
            schema: _schema_state_fingerprint(connection, schema=schema)
            for schema in PERSONAL_WORKSPACE_TARGET_SCHEMAS
        }
    if row is None or len(row) != len(labels):
        raise RuntimeError("Personal workspace storage snapshot is unavailable.")
    return {
        **{label: int(row[index]) for index, label in enumerate(labels)},
        "workspace_rows": [
            {
                "workspace_id": str(item[0]),
                "revision": int(item[1]),
                "workspace": copy.deepcopy(item[2]),
            }
            for item in workspace_rows
        ],
        "mutation_rows": [
            {
                "workspace_id": str(item[0]),
                "idempotency_key": str(item[1]),
                "accepted_workspace": copy.deepcopy(item[2]),
                "accepted_revision": int(item[3]),
            }
            for item in mutation_rows
        ],
        "target_state": target_state,
    }


def assert_personal_workspace_storage(
    snapshot: dict[str, Any],
    *,
    capture: dict[str, Any],
) -> None:
    expected = capture["workspace"]
    expected_mutations = expected["revision"] - 1
    if snapshot.get("personal_workspaces") != 1 or snapshot.get(
        "personal_mutations"
    ) != expected_mutations:
        raise RuntimeError("Personal workspace storage is incomplete or uncorrelated.")
    workspace_rows = snapshot.get("workspace_rows")
    mutation_rows = snapshot.get("mutation_rows")
    if not isinstance(workspace_rows, list) or len(workspace_rows) != 1:
        raise RuntimeError("Personal workspace storage is incomplete or uncorrelated.")
    if not isinstance(mutation_rows, list) or len(mutation_rows) != expected_mutations:
        raise RuntimeError("Personal workspace mutation storage is uncorrelated.")
    workspace_row = workspace_rows[0]
    if (
        not isinstance(workspace_row, dict)
        or not isinstance(workspace_row.get("workspace"), dict)
        or workspace_row.get("workspace_id") != expected["workspace_id"]
        or workspace_row.get("revision") != expected["revision"]
    ):
        raise RuntimeError("Personal workspace aggregate is uncorrelated.")
    stored_workspace = stable_personal_workspace(workspace_row["workspace"])
    if stored_workspace != expected:
        changed_fields = sorted(
            key
            for key in PERSONAL_WORKSPACE_ROOT_KEYS
            if stored_workspace.get(key) != expected.get(key)
        )
        if "records" in changed_fields:
            stored_records = stored_workspace.get("records", [])
            expected_records = expected.get("records", [])
            if len(stored_records) != len(expected_records):
                changed_fields.append("records.count")
            elif [record.get("record_id") for record in stored_records] != [
                record.get("record_id") for record in expected_records
            ]:
                changed_fields.append("records.order_or_membership")
            else:
                for index, (stored_record, expected_record) in enumerate(
                    zip(stored_records, expected_records, strict=True)
                ):
                    changed_fields.extend(
                        f"records.{index}.{key}"
                        for key in sorted(set(stored_record) | set(expected_record))
                        if stored_record.get(key) != expected_record.get(key)
                    )
        if "collections" in changed_fields:
            stored_collections = stored_workspace.get("collections", [])
            expected_collections = expected.get("collections", [])
            collection_fields: list[str] = []
            if len(stored_collections) != len(expected_collections):
                collection_fields.append("count")
            else:
                for index, (stored, observed) in enumerate(
                    zip(stored_collections, expected_collections, strict=True)
                ):
                    collection_fields.extend(
                        f"{index}.{key}"
                        for key in (
                            "collection_id",
                            "title",
                            "member_record_ids",
                            "created_at",
                            "updated_at",
                        )
                        if stored.get(key) != observed.get(key)
                    )
            changed_fields.extend(
                f"collections.{field}" for field in collection_fields
            )
        raise RuntimeError(
            "Personal workspace stored document differs from the public response "
            f"for fields: {', '.join(changed_fields)}."
        )
    if any(
        not isinstance(row, dict)
        or row.get("workspace_id") != expected["workspace_id"]
        or not isinstance(row.get("accepted_workspace"), dict)
        or row["accepted_workspace"].get("workspace_id") != expected["workspace_id"]
        or row["accepted_workspace"].get("revision") != row.get("accepted_revision")
        for row in mutation_rows
    ):
        raise RuntimeError("Personal workspace mutation history is uncorrelated.")
    replay_key = capture["exact_replay_request"]["idempotency_key"]
    replay_rows = [
        row
        for row in mutation_rows
        if isinstance(row, dict) and row.get("idempotency_key") == replay_key
    ]
    if (
        len(replay_rows) != 1
        or not isinstance(replay_rows[0].get("accepted_workspace"), dict)
        or replay_rows[0].get("accepted_revision") != expected["revision"]
        or stable_personal_workspace(replay_rows[0].get("accepted_workspace"))
        != expected
    ):
        raise RuntimeError("Personal workspace replay evidence is uncorrelated.")


def assert_personal_workspace_target_state_unchanged(
    *,
    before_storage: dict[str, Any],
    after_storage: dict[str, Any],
) -> None:
    before_state = before_storage.get("target_state")
    after_state = after_storage.get("target_state")
    if (
        not isinstance(before_state, dict)
        or set(before_state) != set(PERSONAL_WORKSPACE_TARGET_SCHEMAS)
        or not isinstance(after_state, dict)
        or after_state != before_state
    ):
        raise RuntimeError(
            "Personal workspace journey changed target or learning evidence state."
        )


def assert_personal_workspace_restart_result(
    *,
    before_observation: dict[str, Any],
    after_observation: dict[str, Any],
    before_storage: dict[str, Any],
    after_storage: dict[str, Any],
    capture: dict[str, Any],
) -> None:
    if after_observation != before_observation:
        raise RuntimeError("Personal workspace changed after normal restart.")
    assert_personal_workspace_storage(after_storage, capture=capture)
    personal_keys = (
        "personal_workspaces",
        "personal_mutations",
        "workspace_rows",
        "mutation_rows",
    )
    if any(
        after_storage.get(key) != before_storage.get(key)
        for key in personal_keys
    ):
        raise RuntimeError("Personal workspace storage changed during restart replay.")


def project_storage_snapshot(
    postgres_dsn: str,
    *,
    project_id: str,
) -> dict[str, int]:
    query = """
        SELECT
            (SELECT count(*) FROM project.project_shells
              WHERE project_id = %s),
            (SELECT count(*) FROM project.project_workspaces
              WHERE project_id = %s),
            (SELECT count(*) FROM project.project_workspace_mutations
              WHERE project_id = %s),
            (SELECT count(*) FROM project.project_artifact_objects
              WHERE project_id = %s),
            (SELECT count(*) FROM project.project_snapshots
              WHERE project_id = %s),
            (SELECT count(*) FROM assessment.attempts),
            (SELECT count(*) FROM assessment.responses),
            (SELECT count(*) FROM assessment.scores),
            (SELECT count(*) FROM assessment.completion_evidence),
            (SELECT count(*) FROM assessment.outbox),
            (SELECT count(*) FROM assessment.practice_attempts),
            (SELECT count(*) FROM assessment.practice_responses),
            (SELECT count(*) FROM assessment.practice_scores),
            (SELECT count(*) FROM assessment.practice_completion_evidence),
            (SELECT count(*) FROM assessment.practice_outbox),
            (SELECT count(*) FROM learner_model.lesson_completion_projections),
            (SELECT count(*) FROM learner_model.lesson_completion_history),
            (SELECT count(*) FROM learner_model.practice_history_projections),
            (SELECT count(*) FROM learner_model.practice_history_attempts)
    """
    with psycopg.connect(postgres_dsn) as connection:
        row = connection.execute(query, (project_id,) * 5).fetchone()
    labels = (
        "project_shells",
        "project_workspaces",
        "project_mutations",
        "project_artifacts",
        "project_snapshots",
        "assessment_attempts",
        "assessment_responses",
        "assessment_scores",
        "assessment_completion_evidence",
        "assessment_outbox",
        "practice_attempts",
        "practice_responses",
        "practice_scores",
        "practice_completion_evidence",
        "practice_outbox",
        "learner_completion_projections",
        "learner_completion_history",
        "practice_history_projections",
        "practice_history_attempts",
    )
    if row is None or len(row) != len(labels):
        raise RuntimeError("Project storage snapshot is unavailable.")
    return {label: int(row[index]) for index, label in enumerate(labels)}


def assert_project_storage(snapshot: dict[str, int]) -> None:
    expected = {
        "project_shells": 1,
        "project_workspaces": 1,
        "project_mutations": 4,
        "project_artifacts": 1,
        "project_snapshots": 1,
    }
    if {key: snapshot.get(key) for key in expected} != expected:
        raise RuntimeError("Project workspace evidence is incomplete or uncorrelated.")


def project_learning_storage(snapshot: dict[str, int]) -> dict[str, int]:
    missing = [key for key in PROJECT_LEARNING_STORAGE_KEYS if key not in snapshot]
    if missing:
        raise RuntimeError("Project learning-state storage evidence is incomplete.")
    return {key: snapshot[key] for key in PROJECT_LEARNING_STORAGE_KEYS}


def assert_project_learning_state_unchanged(
    *,
    before_storage: dict[str, int],
    after_storage: dict[str, int],
) -> None:
    if project_learning_storage(after_storage) != project_learning_storage(
        before_storage
    ):
        raise RuntimeError(
            "Project journey created Assessment or Learner-model state."
        )


def assert_project_restart_result(
    *,
    before_observation: dict[str, Any],
    after_observation: dict[str, Any],
    before_storage: dict[str, int],
    after_storage: dict[str, int],
) -> None:
    if after_observation != before_observation:
        raise RuntimeError("Project workspace evidence changed after normal restart.")
    project_keys = (
        "project_shells",
        "project_workspaces",
        "project_mutations",
        "project_artifacts",
        "project_snapshots",
    )
    if any(after_storage.get(key) != before_storage.get(key) for key in project_keys):
        raise RuntimeError("Project storage changed during restart replay.")


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
    _exact_keys(document, PRACTICE_DENIAL_ROOT_KEYS, "Practice denial")
    if status != expected_status or document.get("code") != expected_code:
        raise RuntimeError(
            f"Practice denial changed: expected {expected_status} {expected_code}."
        )
    if document["error_version"] != "1.0":
        raise RuntimeError("Practice denial error version changed.")
    message = document["message"]
    if not isinstance(message, str) or not 1 <= len(message) <= 240:
        raise RuntimeError("Practice denial message is invalid.")
    try:
        UUID(str(document["correlation_id"]))
    except (TypeError, ValueError, AttributeError):
        raise RuntimeError("Practice denial correlation ID is invalid.") from None
    leaked = PRIVATE_PRACTICE_RESULT_FIELDS & _nested_mapping_keys(document)
    if leaked:
        raise RuntimeError("Practice denial exposed private fields.")
    normalized_message = message.casefold()
    if "\n" in message or any(
        fragment in normalized_message
        for fragment in PRACTICE_DENIAL_PRIVATE_FRAGMENTS
    ):
        raise RuntimeError("Practice denial exposed private or diagnostic detail.")
    private_path = re.compile(
        r"(?:[a-z]:\\|/(?:home|users?|var|tmp)/|\.py\b)",
        re.I,
    )
    if private_path.search(message):
        raise RuntimeError("Practice denial exposed a private path or stack detail.")
    credential_value = re.compile(
        r"\b(?:authorization|bearer|cookie|credential|password|token)\b\s*[:=]",
        re.I,
    )
    sql_detail = re.compile(
        r"\b(?:delete\s+from|insert\s+into|select\s+.+\s+from|update\s+.+\s+set)\b",
        re.I,
    )
    if credential_value.search(message) or sql_detail.search(message):
        raise RuntimeError("Practice denial exposed private or diagnostic detail.")


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


def _canonical_sha256(document: object) -> str:
    return hashlib.sha256(
        json.dumps(
            document,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _preference_identifier(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(
        r"[a-z0-9][a-z0-9._-]{2,63}", value
    ) is not None


def _preference_time(value: object, *, label: str) -> datetime:
    if not isinstance(value, str) or UTC_TIMESTAMP.fullmatch(value) is None:
        raise RuntimeError(f"{label} is not a canonical UTC timestamp.")
    return _utc_instant(value, label=label)


def stable_learner_preference_profile(
    document: dict[str, Any],
) -> dict[str, Any]:
    if set(document) != LEARNER_PREFERENCE_PROFILE_KEYS:
        raise RuntimeError("Learner preference profile has an open or incomplete shape.")
    if (
        document.get("schema_version") != "1.0.0"
        or not _preference_identifier(document.get("profile_id"))
        or not isinstance(document.get("learner_id"), str)
        or not isinstance(document.get("revision"), int)
        or isinstance(document.get("revision"), bool)
        or document["revision"] < 1
        or not isinstance(document.get("profile_digest"), str)
        or re.fullmatch(r"[a-f0-9]{64}", document["profile_digest"]) is None
    ):
        raise RuntimeError("Learner preference profile identity is invalid.")
    try:
        learner_id = UUID(document["learner_id"])
    except ValueError as error:
        raise RuntimeError("Learner preference profile learner identity is invalid.") from error
    if str(learner_id) != document["learner_id"]:
        raise RuntimeError("Learner preference learner identity is not canonical.")
    created_at = _preference_time(
        document.get("created_at"), label="Learner preference created time"
    )
    updated_at = _preference_time(
        document.get("updated_at"), label="Learner preference updated time"
    )
    if updated_at < created_at:
        raise RuntimeError("Learner preference profile chronology is invalid.")

    collections = (
        (
            "goals",
            20,
            frozenset(
                {"goal_id", "title", "detail", "archived", "created_at", "updated_at"}
            ),
            "goal_id",
            "title",
        ),
        (
            "experience",
            20,
            frozenset(
                {"experience_id", "subject", "level", "detail", "created_at", "updated_at"}
            ),
            "experience_id",
            "subject",
        ),
        (
            "interests",
            50,
            frozenset({"interest_id", "label", "created_at", "updated_at"}),
            "interest_id",
            "label",
        ),
    )
    identifiers: list[str] = []
    for name, limit, keys, identifier_key, text_key in collections:
        entries = document.get(name)
        if not isinstance(entries, list) or len(entries) > limit:
            raise RuntimeError(f"Learner preference {name} collection is invalid.")
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != keys:
                raise RuntimeError(f"Learner preference {name} entry is not closed.")
            identifier = entry.get(identifier_key)
            text_value = entry.get(text_key)
            if (
                not _preference_identifier(identifier)
                or not isinstance(text_value, str)
                or text_value.strip() != text_value
                or not text_value
            ):
                raise RuntimeError(f"Learner preference {name} entry is invalid.")
            if name == "goals" and (
                not isinstance(entry.get("archived"), bool)
                or not (
                    entry.get("detail") is None
                    or isinstance(entry.get("detail"), str)
                )
            ):
                raise RuntimeError("Learner preference goal entry is invalid.")
            if name == "experience" and (
                entry.get("level") not in {"new", "some_experience", "experienced"}
                or not (
                    entry.get("detail") is None
                    or isinstance(entry.get("detail"), str)
                )
            ):
                raise RuntimeError("Learner preference experience entry is invalid.")
            entry_created = _preference_time(
                entry.get("created_at"), label=f"Learner preference {name} created time"
            )
            entry_updated = _preference_time(
                entry.get("updated_at"), label=f"Learner preference {name} updated time"
            )
            if not (created_at <= entry_created <= entry_updated <= updated_at):
                raise RuntimeError(f"Learner preference {name} chronology is invalid.")
            identifiers.append(str(identifier))
    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError("Learner preference identifiers are not unique.")
    material = {key: copy.deepcopy(value) for key, value in document.items() if key != "profile_digest"}
    if _canonical_sha256(material) != document["profile_digest"]:
        raise RuntimeError("Learner preference profile digest is invalid.")
    return copy.deepcopy(document)


def stable_learner_preference_history(
    document: dict[str, Any],
    *,
    profile: dict[str, Any],
) -> dict[str, Any]:
    if set(document) != LEARNER_PREFERENCE_HISTORY_KEYS or (
        document.get("schema_version") != "1.0.0"
        or document.get("profile_id") != profile["profile_id"]
        or document.get("current_revision") != profile["revision"]
        or not isinstance(document.get("changes"), list)
        or len(document["changes"]) > 100
    ):
        raise RuntimeError("Learner preference history is invalid.")
    previous_revision = 0
    previous_time: datetime | None = None
    change_keys = frozenset(
        {
            "schema_version",
            "revision",
            "operation",
            "object_kind",
            "object_id",
            "occurred_at",
            "resulting_profile_digest",
        }
    )
    for change in document["changes"]:
        if not isinstance(change, dict) or set(change) != change_keys:
            raise RuntimeError("Learner preference history change is not closed.")
        occurred_at = _preference_time(
            change.get("occurred_at"), label="Learner preference change time"
        )
        revision = change.get("revision")
        if (
            change.get("schema_version") != "1.0.0"
            or not isinstance(revision, int)
            or isinstance(revision, bool)
            or revision <= previous_revision
            or revision > profile["revision"]
            or previous_time is not None
            and occurred_at < previous_time
            or not isinstance(change.get("resulting_profile_digest"), str)
            or re.fullmatch(r"[a-f0-9]{64}", change["resulting_profile_digest"])
            is None
        ):
            raise RuntimeError("Learner preference history correlation is invalid.")
        previous_revision = revision
        previous_time = occurred_at
    latest = document["changes"][-1] if document["changes"] else None
    if latest is not None and (
        latest["revision"] != profile["revision"]
        or latest["resulting_profile_digest"] != profile["profile_digest"]
    ):
        raise RuntimeError("Learner preference history does not end at the current profile.")
    return copy.deepcopy(document)


def stable_learner_preference_export(
    document: dict[str, Any],
    *,
    profile: dict[str, Any],
    history: dict[str, Any],
) -> dict[str, Any]:
    if set(document) != LEARNER_PREFERENCE_EXPORT_KEYS or (
        document.get("schema_version") != "1.0.0"
        or not isinstance(document.get("purpose"), str)
        or not document["purpose"]
        or not isinstance(document.get("limitations"), list)
        or not 1 <= len(document["limitations"]) <= 8
        or not all(isinstance(item, str) and item for item in document["limitations"])
        or document.get("profile") != profile
        or document.get("history") != history
    ):
        raise RuntimeError("Learner preference export is invalid.")
    exported_at = _preference_time(
        document.get("exported_at"), label="Learner preference export time"
    )
    if exported_at < _preference_time(
        profile["updated_at"], label="Learner preference profile update time"
    ):
        raise RuntimeError("Learner preference export chronology is invalid.")
    return copy.deepcopy(document)


def stable_learner_preference_request(
    document: dict[str, Any],
) -> dict[str, Any]:
    if set(document) != LEARNER_PREFERENCE_REQUEST_KEYS or (
        document.get("schema_version") != "1.0.0"
        or not _preference_identifier(document.get("idempotency_key"))
        or not isinstance(document.get("expected_revision"), int)
        or isinstance(document.get("expected_revision"), bool)
        or document["expected_revision"] < 1
        or not isinstance(document.get("mutation"), dict)
    ):
        raise RuntimeError("Learner preference mutation request is invalid.")
    return copy.deepcopy(document)


def load_learner_preference_capture(
    path: Path,
    *,
    data_root: Path,
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("The bounded learner preference capture is absent.")
    resolved = path.resolve()
    if resolved.parent != data_root.resolve() or resolved.stat().st_size > 524_288:
        raise RuntimeError("Learner preference capture escaped its bounded root.")
    capture = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(capture, dict) or set(capture) != LEARNER_PREFERENCE_CAPTURE_ROOT_KEYS:
        raise RuntimeError("Learner preference capture has an invalid shape.")
    leaked = LEARNER_PREFERENCE_PRIVATE_CAPTURE_KEYS & _nested_mapping_keys(capture)
    if leaked:
        raise RuntimeError("Learner preference capture contains private authority data.")
    if capture.get("schema_version") != "1.0.0":
        raise RuntimeError("Learner preference capture version is invalid.")
    if not all(
        isinstance(capture.get(key), dict)
        for key in (
            "profile",
            "history",
            "export",
            "exact_replay_request",
            "exact_replay_response",
            "races",
            "expected",
        )
    ):
        raise RuntimeError("Learner preference capture documents must be objects.")
    profile = stable_learner_preference_profile(capture["profile"])
    history = stable_learner_preference_history(capture["history"], profile=profile)
    stable_learner_preference_export(capture["export"], profile=profile, history=history)
    expected = capture["expected"]
    populated_revision = expected.get("populated_export_profile_revision")
    reset_revisions = {
        change["revision"]
        for change in history["changes"]
        if change["operation"] == "reset_profile"
    }
    if (
        set(expected) != LEARNER_PREFERENCE_EXPECTED_KEYS
        or not isinstance(expected.get("final_goal"), str)
        or expected["final_goal"] not in {goal["title"] for goal in profile["goals"]}
        or not isinstance(expected.get("final_experience"), str)
        or expected["final_experience"]
        not in {entry["subject"] for entry in profile["experience"]}
        or not isinstance(expected.get("final_interest"), str)
        or expected["final_interest"]
        not in {interest["label"] for interest in profile["interests"]}
        or expected.get("reset_recorded") is not True
        or not isinstance(populated_revision, int)
        or isinstance(populated_revision, bool)
        or populated_revision < 1
        or populated_revision >= profile["revision"]
        or populated_revision + 1 not in reset_revisions
    ):
        raise RuntimeError("Learner preference expected summary is not correlated.")
    exact_request = stable_learner_preference_request(capture["exact_replay_request"])
    exact_response = stable_learner_preference_profile(capture["exact_replay_response"])
    if exact_response != profile or exact_request["expected_revision"] + 1 != profile["revision"]:
        raise RuntimeError("Learner preference exact replay is not correlated.")
    races = capture["races"]
    if set(races) != {
        "same_key_same_payload",
        "same_key_changed_payload",
        "different_key_same_revision",
    }:
        raise RuntimeError("Learner preference race matrix is incomplete.")
    expected_classes = {
        "same_key_same_payload": ["accepted", "accepted"],
        "same_key_changed_payload": ["accepted", "conflict"],
        "different_key_same_revision": ["accepted", "stale"],
    }
    for offset, (name, expected_outcomes) in enumerate(expected_classes.items()):
        case = races.get(name)
        if not isinstance(case, dict) or set(case) != {"requests", "expected"}:
            raise RuntimeError("Learner preference race case is not closed.")
        requests = case.get("requests")
        if not isinstance(requests, list) or len(requests) != 2:
            raise RuntimeError("Learner preference race request pair is invalid.")
        stable_requests = [
            stable_learner_preference_request(request)
            if isinstance(request, dict)
            else (_ for _ in ()).throw(RuntimeError("Learner preference race request is invalid."))
            for request in requests
        ]
        if (
            sorted(case.get("expected", [])) != sorted(expected_outcomes)
            or any(
                request["expected_revision"] != profile["revision"] + offset
                or request["mutation"].get("operation") != "create_interest"
                for request in stable_requests
            )
        ):
            raise RuntimeError("Learner preference race expectations are invalid.")
        keys = [request["idempotency_key"] for request in stable_requests]
        mutations = [request["mutation"] for request in stable_requests]
        if name == "same_key_same_payload" and not (
            keys[0] == keys[1] and mutations[0] == mutations[1]
        ):
            raise RuntimeError("Exact replay race does not use the same request.")
        if name == "same_key_changed_payload" and not (
            keys[0] == keys[1] and mutations[0] != mutations[1]
        ):
            raise RuntimeError("Changed-payload race is not immutable-key scoped.")
        if name == "different_key_same_revision" and keys[0] == keys[1]:
            raise RuntimeError("Stale-revision race does not use distinct keys.")
    return copy.deepcopy(capture)


def open_learner_preference_sessions(
    origin: str,
    count: int,
) -> list[urllib.request.OpenerDirector]:
    if count < 1:
        raise ValueError("At least one learner preference session client is required.")
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
    _request_json(
        opener,
        origin=origin,
        path="/api/v1/session/single-profile",
        method="POST",
        payload={"limitation_acknowledged": True},
    )
    issued_cookies = tuple(cookies)
    if not issued_cookies:
        raise RuntimeError("Learner preference session did not issue a cookie.")
    openers: list[urllib.request.OpenerDirector] = []
    for _ in range(count):
        client_cookies = http.cookiejar.CookieJar()
        for cookie in issued_cookies:
            client_cookies.set_cookie(copy.copy(cookie))
        openers.append(
            urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor(client_cookies)
            )
        )
    return openers


def open_learner_preference_session(origin: str) -> urllib.request.OpenerDirector:
    return open_learner_preference_sessions(origin, 1)[0]


def _assert_safe_learner_preference_denial(
    status: int,
    document: dict[str, Any],
    *,
    expected_code: str | tuple[str, ...],
    requests: list[dict[str, Any]],
) -> None:
    expected_codes = (
        frozenset(expected_code) if isinstance(expected_code, tuple) else {expected_code}
    )
    if status != 409 or set(document) != LEARNER_PREFERENCE_DENIAL_KEYS or (
        document.get("error_version") != "1.0"
        or document.get("code") not in expected_codes
    ):
        raise RuntimeError(
            "Learner preference race denial changed public meaning: "
            f"status={status}, code={document.get('code')!r}, "
            f"keys={sorted(document)}."
        )
    try:
        correlation_id = UUID(str(document.get("correlation_id")))
    except ValueError as error:
        raise RuntimeError("Learner preference denial correlation is invalid.") from error
    if str(correlation_id) != document.get("correlation_id"):
        raise RuntimeError("Learner preference denial correlation is not canonical.")
    serialized = json.dumps(document, ensure_ascii=False, sort_keys=True).casefold()
    sensitive_values = {
        str(value).casefold()
        for request in requests
        for value in (
            request.get("idempotency_key"),
            request.get("mutation", {}).get("label"),
        )
        if value
    }
    if any(value in serialized for value in sensitive_values) or any(
        marker in serialized
        for marker in (
            "learner_id",
            "preference_mutations",
            "request_fingerprint",
            "postgres",
            "traceback",
        )
    ):
        raise RuntimeError("Learner preference denial disclosed private details.")


def observe_headless_learner_preferences(
    *,
    origin: str,
    expected_profile: dict[str, Any],
    expected_history: dict[str, Any],
    expected_export: dict[str, Any],
    exact_replay_request: dict[str, Any],
    exact_replay_response: dict[str, Any],
) -> dict[str, Any]:
    opener = open_learner_preference_session(origin)
    profile = stable_learner_preference_profile(
        _request_json(opener, origin=origin, path="/api/v1/learner-preferences")
    )
    history = stable_learner_preference_history(
        _request_json(opener, origin=origin, path="/api/v1/learner-preferences/history"),
        profile=profile,
    )
    export_document = stable_learner_preference_export(
        _request_json(opener, origin=origin, path="/api/v1/learner-preferences/export"),
        profile=profile,
        history=history,
    )
    if profile != expected_profile or history != expected_history or any(
        export_document[key] != expected_export[key]
        for key in LEARNER_PREFERENCE_EXPORT_KEYS - {"exported_at"}
    ):
        raise RuntimeError("Headless learner preferences changed browser-observed meaning.")
    replayed = stable_learner_preference_profile(
        _request_json(
            opener,
            origin=origin,
            path="/api/v1/learner-preferences/mutations",
            method="POST",
            payload=exact_replay_request,
        )
    )
    if replayed != exact_replay_response:
        raise RuntimeError("Headless learner preference replay changed accepted meaning.")
    for suffix in ("?learner_id=someone-else", "/history?limit=1", "/export?private=true"):
        status, denial = _request_json_read_status(
            opener,
            origin=origin,
            path=f"/api/v1/learner-preferences{suffix}",
        )
        if status != 400 or denial.get("code") != "invalid_request":
            raise RuntimeError("Learner preference guessed input was not denied.")
    return {"profile": profile, "history": history, "export": export_document}


def learner_preference_source_fingerprint(postgres_dsn: str) -> dict[str, Any]:
    with psycopg.connect(postgres_dsn) as connection:
        tables = [
            (str(row[0]), str(row[1]))
            for row in connection.execute(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                  AND table_schema NOT IN ('information_schema', 'pg_catalog', 'identity')
                  AND table_schema NOT LIKE 'pg\\_%' ESCAPE '\\'
                ORDER BY table_schema, table_name
                """
            ).fetchall()
            if not (
                str(row[0]) == "learner_model"
                and str(row[1]) in LEARNER_PREFERENCE_TABLES
            )
        ]
        digest = hashlib.sha256()
        row_count = 0
        for schema, table in tables:
            rows = connection.execute(
                sql.SQL(
                    "SELECT to_jsonb(row_value)::text FROM {}.{} AS row_value "
                    "ORDER BY to_jsonb(row_value)::text"
                ).format(sql.Identifier(schema), sql.Identifier(table))
            ).fetchall()
            row_count += len(rows)
            digest.update(f"{schema}.{table}\0{len(rows)}\0".encode("utf-8"))
            for row in rows:
                digest.update(str(row[0]).encode("utf-8"))
                digest.update(b"\0")
    return {"table_count": len(tables), "row_count": row_count, "sha256": digest.hexdigest()}


def learner_preference_storage_snapshot(postgres_dsn: str) -> dict[str, Any]:
    with psycopg.connect(postgres_dsn) as connection:
        profiles = connection.execute(
            """
            SELECT profile_id, learner_id::text, revision, profile, profile_digest
            FROM learner_model.preference_profiles ORDER BY profile_id
            """
        ).fetchall()
        changes = connection.execute(
            """
            SELECT learner_id::text, revision, change, resulting_profile_digest
            FROM learner_model.preference_changes ORDER BY learner_id, revision
            """
        ).fetchall()
        mutations = connection.execute(
            """
            SELECT learner_id::text, idempotency_key, accepted_revision, accepted_profile
            FROM learner_model.preference_mutations
            ORDER BY learner_id, accepted_revision, idempotency_key
            """
        ).fetchall()
    return {
        "profiles": [
            [str(row[0]), str(row[1]), int(row[2]), copy.deepcopy(row[3]), str(row[4])]
            for row in profiles
        ],
        "changes": [
            [str(row[0]), int(row[1]), copy.deepcopy(row[2]), str(row[3])]
            for row in changes
        ],
        "mutations": [
            [str(row[0]), str(row[1]), int(row[2]), copy.deepcopy(row[3])]
            for row in mutations
        ],
    }


def assert_learner_preference_storage(
    snapshot: dict[str, Any],
    *,
    profile: dict[str, Any],
    history: dict[str, Any],
) -> None:
    profiles = snapshot.get("profiles")
    changes = snapshot.get("changes")
    mutations = snapshot.get("mutations")
    expected_mutations = profile["revision"] - 1
    if (
        not isinstance(profiles, list)
        or len(profiles) != 1
        or not isinstance(changes, list)
        or len(changes) != len(history["changes"])
        or not isinstance(mutations, list)
        or len(mutations) != expected_mutations
    ):
        raise RuntimeError("Learner preference storage row counts are uncorrelated.")
    stored = profiles[0]
    if (
        stored[0] != profile["profile_id"]
        or stored[1] != profile["learner_id"]
        or stored[2] != profile["revision"]
        or stable_learner_preference_profile(stored[3]) != profile
        or stored[4] != profile["profile_digest"]
    ):
        raise RuntimeError("Learner preference stored profile is uncorrelated.")
    if [row[2] for row in changes] != history["changes"] or any(
        row[0] != profile["learner_id"]
        or row[1] != row[2]["revision"]
        or row[3] != row[2]["resulting_profile_digest"]
        for row in changes
    ):
        raise RuntimeError("Learner preference stored history is uncorrelated.")
    if any(
        row[0] != profile["learner_id"]
        or row[2] != row[3].get("revision")
        or stable_learner_preference_profile(row[3]) != row[3]
        for row in mutations
    ):
        raise RuntimeError("Learner preference replay storage is uncorrelated.")


def _run_learner_preference_race(
    *,
    origin: str,
    requests: list[dict[str, Any]],
) -> list[tuple[int, dict[str, Any]]]:
    openers = open_learner_preference_sessions(origin, len(requests))
    barrier = threading.Barrier(len(requests))

    def send(
        opener: urllib.request.OpenerDirector,
        request: dict[str, Any],
    ) -> tuple[int, dict[str, Any]]:
        barrier.wait(timeout=10)
        return _request_json_status(
            opener,
            origin=origin,
            path="/api/v1/learner-preferences/mutations",
            method="POST",
            payload=request,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(send, opener, request)
            for opener, request in zip(openers, requests, strict=True)
        ]
        return [future.result(timeout=20) for future in futures]


def assert_learner_preference_race_outcomes(
    *,
    name: str,
    requests: list[dict[str, Any]],
    results: list[tuple[int, dict[str, Any]]],
    before_storage: dict[str, Any],
    after_storage: dict[str, Any],
) -> dict[str, Any]:
    if len(results) != 2:
        raise RuntimeError("Learner preference race returned an invalid outcome count.")
    accepted = [document for status, document in results if status == 200]
    denials = [(status, document) for status, document in results if status != 200]
    expected_accepted = 2 if name == "same_key_same_payload" else 1
    if len(accepted) != expected_accepted:
        observed = [
            f"{status}:{document.get('code', 'accepted')}"
            for status, document in results
        ]
        raise RuntimeError(
            "Learner preference race acceptance matrix is invalid for "
            f"{name}: {observed}."
        )
    stable_accepted = [stable_learner_preference_profile(item) for item in accepted]
    if name == "same_key_same_payload" and stable_accepted[0] != stable_accepted[1]:
        raise RuntimeError("Exact concurrent replays did not converge.")
    if name != "same_key_same_payload":
        if len(denials) != 1:
            raise RuntimeError("Learner preference race denial matrix is invalid.")
        _assert_safe_learner_preference_denial(
            denials[0][0],
            denials[0][1],
            expected_code=(
                ("immutable_conflict", "stale_revision")
                if name == "same_key_changed_payload"
                else "stale_revision"
            ),
            requests=requests,
        )
    for key in ("profiles", "changes", "mutations"):
        before = before_storage.get(key)
        after = after_storage.get(key)
        if not isinstance(before, list) or not isinstance(after, list):
            raise RuntimeError("Learner preference race storage evidence is invalid.")
        expected_delta = 0 if key == "profiles" else 1
        if key == "profiles":
            if len(before) != 1 or len(after) != 1 or after[0][2] != before[0][2] + 1:
                raise RuntimeError("Learner preference race profile revision is invalid.")
        elif len(after) != len(before) + expected_delta:
            raise RuntimeError("Learner preference race appended an invalid row count.")
    current = after_storage["profiles"][0][3]
    if current not in stable_accepted:
        raise RuntimeError("Learner preference race result did not match durable state.")
    return stable_learner_preference_profile(current)


def qualify_learner_preference_races(
    *,
    origin: str,
    postgres_dsn: str,
    capture: dict[str, Any],
) -> dict[str, Any]:
    outcomes: dict[str, list[str]] = {}
    current_profile = capture["profile"]
    for name in (
        "same_key_same_payload",
        "same_key_changed_payload",
        "different_key_same_revision",
    ):
        requests = capture["races"][name]["requests"]
        before = learner_preference_storage_snapshot(postgres_dsn)
        results = _run_learner_preference_race(origin=origin, requests=requests)
        after = learner_preference_storage_snapshot(postgres_dsn)
        current_profile = assert_learner_preference_race_outcomes(
            name=name,
            requests=requests,
            results=results,
            before_storage=before,
            after_storage=after,
        )
        outcomes[name] = [
            "accepted"
            if status == 200
            else "conflict"
            if document.get("code") == "immutable_conflict"
            else "stale"
            for status, document in results
        ]
        expected = sorted(capture["races"][name]["expected"])
        allowed = (
            {("accepted", "conflict"), ("accepted", "stale")}
            if name == "same_key_changed_payload"
            else {tuple(expected)}
        )
        if tuple(sorted(outcomes[name])) not in allowed:
            raise RuntimeError("Learner preference race outcome classes changed.")
    opener = open_learner_preference_session(origin)
    history = stable_learner_preference_history(
        _request_json(opener, origin=origin, path="/api/v1/learner-preferences/history"),
        profile=current_profile,
    )
    export_document = stable_learner_preference_export(
        _request_json(opener, origin=origin, path="/api/v1/learner-preferences/export"),
        profile=current_profile,
        history=history,
    )
    storage = learner_preference_storage_snapshot(postgres_dsn)
    assert_learner_preference_storage(storage, profile=current_profile, history=history)
    return {
        "profile": current_profile,
        "history": history,
        "export": export_document,
        "storage": storage,
        "outcomes": outcomes,
    }


def stable_presentation_settings(document: dict[str, Any]) -> dict[str, str]:
    if set(document) != {"text_size", "text_spacing", "reading_width", "motion"} or (
        document.get("text_size") not in {"default", "larger"}
        or document.get("text_spacing") not in {"default", "increased"}
        or document.get("reading_width") not in {"standard", "focused"}
        or document.get("motion") not in {"system", "reduce"}
    ):
        raise RuntimeError("Presentation preference settings are invalid.")
    return {key: str(document[key]) for key in sorted(document)}


def stable_presentation_preference_profile(
    document: dict[str, Any],
) -> dict[str, Any]:
    if set(document) != PRESENTATION_PREFERENCE_PROFILE_KEYS:
        raise RuntimeError("Presentation preference profile has an open or incomplete shape.")
    if (
        document.get("schema_version") != "1.0.0"
        or not _preference_identifier(document.get("profile_id"))
        or not isinstance(document.get("learner_id"), str)
        or not isinstance(document.get("revision"), int)
        or isinstance(document.get("revision"), bool)
        or document["revision"] < 1
        or not isinstance(document.get("profile_digest"), str)
        or re.fullmatch(r"[a-f0-9]{64}", document["profile_digest"]) is None
    ):
        raise RuntimeError("Presentation preference profile identity is invalid.")
    try:
        learner_id = UUID(document["learner_id"])
    except ValueError as error:
        raise RuntimeError("Presentation preference learner identity is invalid.") from error
    if str(learner_id) != document["learner_id"]:
        raise RuntimeError("Presentation preference learner identity is not canonical.")
    created_at = _preference_time(
        document.get("created_at"), label="Presentation preference created time"
    )
    updated_at = _preference_time(
        document.get("updated_at"), label="Presentation preference updated time"
    )
    if updated_at < created_at:
        raise RuntimeError("Presentation preference profile chronology is invalid.")
    stable_presentation_settings(
        {
            "text_size": document.get("text_size"),
            "text_spacing": document.get("text_spacing"),
            "reading_width": document.get("reading_width"),
            "motion": document.get("motion"),
        }
    )
    material = {
        key: copy.deepcopy(value)
        for key, value in document.items()
        if key != "profile_digest"
    }
    if _canonical_sha256(material) != document["profile_digest"]:
        raise RuntimeError("Presentation preference profile digest is invalid.")
    return copy.deepcopy(document)


def stable_presentation_preference_history(
    document: dict[str, Any],
    *,
    profile: dict[str, Any],
) -> dict[str, Any]:
    if set(document) != PRESENTATION_PREFERENCE_HISTORY_KEYS or (
        document.get("schema_version") != "1.0.0"
        or document.get("profile_id") != profile["profile_id"]
        or document.get("current_revision") != profile["revision"]
        or not isinstance(document.get("changes"), list)
        or len(document["changes"]) > 100
    ):
        raise RuntimeError("Presentation preference history is invalid.")
    change_keys = frozenset(
        {
            "schema_version",
            "revision",
            "operation",
            "object_kind",
            "object_id",
            "occurred_at",
            "resulting_profile_digest",
        }
    )
    previous_revision = 0
    previous_time: datetime | None = None
    for change in document["changes"]:
        if not isinstance(change, dict) or set(change) != change_keys:
            raise RuntimeError("Presentation preference history change is not closed.")
        occurred_at = _preference_time(
            change.get("occurred_at"), label="Presentation preference change time"
        )
        revision = change.get("revision")
        if (
            change.get("schema_version") != "1.0.0"
            or change.get("operation") not in {"replace_preferences", "reset_profile"}
            or change.get("object_kind") != "profile"
            or change.get("object_id") is not None
            or not isinstance(revision, int)
            or isinstance(revision, bool)
            or revision <= previous_revision
            or revision > profile["revision"]
            or previous_time is not None
            and occurred_at < previous_time
            or not isinstance(change.get("resulting_profile_digest"), str)
            or re.fullmatch(r"[a-f0-9]{64}", change["resulting_profile_digest"])
            is None
        ):
            raise RuntimeError("Presentation preference history correlation is invalid.")
        previous_revision = revision
        previous_time = occurred_at
    latest = document["changes"][-1] if document["changes"] else None
    if latest is not None and (
        latest["revision"] != profile["revision"]
        or latest["resulting_profile_digest"] != profile["profile_digest"]
    ):
        raise RuntimeError("Presentation preference history does not end at the profile.")
    return copy.deepcopy(document)


def stable_presentation_preference_export(
    document: dict[str, Any],
    *,
    profile: dict[str, Any],
    history: dict[str, Any],
) -> dict[str, Any]:
    if set(document) != PRESENTATION_PREFERENCE_EXPORT_KEYS or (
        document.get("schema_version") != "1.0.0"
        or not isinstance(document.get("purpose"), str)
        or not document["purpose"]
        or not isinstance(document.get("limitations"), list)
        or not 1 <= len(document["limitations"]) <= 8
        or not all(isinstance(item, str) and item for item in document["limitations"])
        or document.get("profile") != profile
        or document.get("history") != history
    ):
        raise RuntimeError("Presentation preference export is invalid.")
    exported_at = _preference_time(
        document.get("exported_at"), label="Presentation preference export time"
    )
    if exported_at < _preference_time(
        profile["updated_at"], label="Presentation preference profile update time"
    ):
        raise RuntimeError("Presentation preference export chronology is invalid.")
    return copy.deepcopy(document)


def stable_presentation_preference_request(
    document: dict[str, Any],
) -> dict[str, Any]:
    if set(document) != PRESENTATION_PREFERENCE_REQUEST_KEYS or (
        document.get("schema_version") != "1.0.0"
        or not _preference_identifier(document.get("idempotency_key"))
        or not isinstance(document.get("expected_revision"), int)
        or isinstance(document.get("expected_revision"), bool)
        or document["expected_revision"] < 1
        or not isinstance(document.get("mutation"), dict)
    ):
        raise RuntimeError("Presentation preference mutation request is invalid.")
    mutation = document["mutation"]
    if mutation.get("operation") == "reset_profile":
        if set(mutation) != {"operation"}:
            raise RuntimeError("Presentation preference reset request is open.")
    elif mutation.get("operation") == "replace_preferences":
        if set(mutation) != {
            "operation",
            "text_size",
            "text_spacing",
            "reading_width",
            "motion",
        }:
            raise RuntimeError("Presentation preference replacement request is open.")
        stable_presentation_settings(
            {key: mutation[key] for key in mutation if key != "operation"}
        )
    else:
        raise RuntimeError("Presentation preference mutation operation is invalid.")
    return copy.deepcopy(document)


def load_presentation_preference_capture(
    path: Path,
    *,
    data_root: Path,
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("The bounded presentation preference capture is absent.")
    resolved = path.resolve()
    if resolved.parent != data_root.resolve() or resolved.stat().st_size > 524_288:
        raise RuntimeError("Presentation preference capture escaped its bounded root.")
    capture = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(capture, dict) or set(capture) != PRESENTATION_PREFERENCE_CAPTURE_ROOT_KEYS:
        raise RuntimeError("Presentation preference capture has an invalid shape.")
    leaked = PRESENTATION_PREFERENCE_PRIVATE_CAPTURE_KEYS & _nested_mapping_keys(capture)
    if leaked:
        raise RuntimeError("Presentation preference capture contains private authority data.")
    if capture.get("schema_version") != "1.0.0" or not all(
        isinstance(capture.get(key), dict)
        for key in (
            "profile",
            "history",
            "export",
            "exact_replay_request",
            "exact_replay_response",
            "races",
            "expected",
        )
    ):
        raise RuntimeError("Presentation preference capture documents are invalid.")
    profile = stable_presentation_preference_profile(capture["profile"])
    history = stable_presentation_preference_history(capture["history"], profile=profile)
    stable_presentation_preference_export(
        capture["export"], profile=profile, history=history
    )
    exact_request = stable_presentation_preference_request(
        capture["exact_replay_request"]
    )
    exact_response = stable_presentation_preference_profile(
        capture["exact_replay_response"]
    )
    if (
        exact_response != profile
        or exact_request["expected_revision"] + 1 != profile["revision"]
        or exact_request["mutation"] != {"operation": "reset_profile"}
    ):
        raise RuntimeError("Presentation preference exact replay is not correlated.")

    expected = capture["expected"]
    combinations = expected.get("all_combinations")
    expected_combinations = {
        (text_size, text_spacing, reading_width, motion)
        for text_size in ("default", "larger")
        for text_spacing in ("default", "increased")
        for reading_width in ("standard", "focused")
        for motion in ("system", "reduce")
    }
    observed_combinations = set()
    if isinstance(combinations, list):
        for settings in combinations:
            if not isinstance(settings, dict):
                raise RuntimeError("Presentation preference combination is invalid.")
            stable = stable_presentation_settings(settings)
            observed_combinations.add(
                (
                    stable["text_size"],
                    stable["text_spacing"],
                    stable["reading_width"],
                    stable["motion"],
                )
            )
    populated_revision = expected.get("populated_export_profile_revision")
    reset_revisions = {
        change["revision"]
        for change in history["changes"]
        if change["operation"] == "reset_profile"
    }
    if (
        set(expected) != PRESENTATION_PREFERENCE_EXPECTED_KEYS
        or observed_combinations != expected_combinations
        or expected.get("reset_recorded") is not True
        or expected.get("theme_after_reset") != "dark"
        or not isinstance(populated_revision, int)
        or isinstance(populated_revision, bool)
        or populated_revision < 1
        or populated_revision >= profile["revision"]
        or populated_revision + 1 not in reset_revisions
        or stable_presentation_settings(
            {key: profile[key] for key in ("text_size", "text_spacing", "reading_width", "motion")}
        )
        != {
            "motion": "system",
            "reading_width": "standard",
            "text_size": "default",
            "text_spacing": "default",
        }
    ):
        raise RuntimeError("Presentation preference expected summary is not correlated.")

    races = capture["races"]
    expected_classes = {
        "same_key_same_payload": ["accepted", "accepted"],
        "same_key_changed_payload": ["accepted", "conflict"],
        "different_key_same_revision": ["accepted", "stale"],
    }
    if set(races) != set(expected_classes):
        raise RuntimeError("Presentation preference race matrix is incomplete.")
    for offset, (name, expected_outcomes) in enumerate(expected_classes.items()):
        case = races.get(name)
        if not isinstance(case, dict) or set(case) != {"requests", "expected"}:
            raise RuntimeError("Presentation preference race case is not closed.")
        requests = case.get("requests")
        if not isinstance(requests, list) or len(requests) != 2:
            raise RuntimeError("Presentation preference race request pair is invalid.")
        stable_requests = [
            stable_presentation_preference_request(request)
            if isinstance(request, dict)
            else (_ for _ in ()).throw(
                RuntimeError("Presentation preference race request is invalid.")
            )
            for request in requests
        ]
        if (
            sorted(case.get("expected", [])) != sorted(expected_outcomes)
            or any(
                request["expected_revision"] != profile["revision"] + offset
                or request["mutation"].get("operation") != "replace_preferences"
                for request in stable_requests
            )
        ):
            raise RuntimeError("Presentation preference race expectations are invalid.")
        keys = [request["idempotency_key"] for request in stable_requests]
        mutations = [request["mutation"] for request in stable_requests]
        if name == "same_key_same_payload" and not (
            keys[0] == keys[1] and mutations[0] == mutations[1]
        ):
            raise RuntimeError("Presentation exact replay race does not match.")
        if name == "same_key_changed_payload" and not (
            keys[0] == keys[1] and mutations[0] != mutations[1]
        ):
            raise RuntimeError("Presentation conflict race is not key-scoped.")
        if name == "different_key_same_revision" and keys[0] == keys[1]:
            raise RuntimeError("Presentation stale race does not use distinct keys.")
    return copy.deepcopy(capture)


def _assert_safe_presentation_preference_denial(
    status: int,
    document: dict[str, Any],
    *,
    expected_code: str | tuple[str, ...],
    requests: list[dict[str, Any]],
) -> None:
    expected_codes = (
        frozenset(expected_code) if isinstance(expected_code, tuple) else {expected_code}
    )
    if status != 409 or set(document) != PRESENTATION_PREFERENCE_DENIAL_KEYS or (
        document.get("error_version") != "1.0"
        or document.get("code") not in expected_codes
    ):
        raise RuntimeError("Presentation preference denial changed public meaning.")
    try:
        correlation_id = UUID(str(document.get("correlation_id")))
    except ValueError as error:
        raise RuntimeError("Presentation preference denial correlation is invalid.") from error
    if str(correlation_id) != document.get("correlation_id"):
        raise RuntimeError("Presentation preference denial correlation is not canonical.")
    serialized = json.dumps(document, ensure_ascii=False, sort_keys=True).casefold()
    keys = {str(request["idempotency_key"]).casefold() for request in requests}
    if any(key in serialized for key in keys) or any(
        marker in serialized
        for marker in (
            "learner_id",
            "presentation_preference_mutations",
            "request_fingerprint",
            "postgres",
            "traceback",
        )
    ):
        raise RuntimeError("Presentation preference denial disclosed private details.")


def observe_headless_presentation_preferences(
    *,
    origin: str,
    expected_profile: dict[str, Any],
    expected_history: dict[str, Any],
    expected_export: dict[str, Any],
    exact_replay_request: dict[str, Any],
    exact_replay_response: dict[str, Any],
) -> dict[str, Any]:
    opener = open_learner_preference_session(origin)
    profile = stable_presentation_preference_profile(
        _request_json(
            opener, origin=origin, path="/api/v1/learner-presentation-preferences"
        )
    )
    history = stable_presentation_preference_history(
        _request_json(
            opener,
            origin=origin,
            path="/api/v1/learner-presentation-preferences/history",
        ),
        profile=profile,
    )
    export_document = stable_presentation_preference_export(
        _request_json(
            opener,
            origin=origin,
            path="/api/v1/learner-presentation-preferences/export",
        ),
        profile=profile,
        history=history,
    )
    if profile != expected_profile or history != expected_history or any(
        export_document[key] != expected_export[key]
        for key in PRESENTATION_PREFERENCE_EXPORT_KEYS - {"exported_at"}
    ):
        raise RuntimeError("Headless presentation preferences changed browser meaning.")
    replayed = stable_presentation_preference_profile(
        _request_json(
            opener,
            origin=origin,
            path="/api/v1/learner-presentation-preferences/mutations",
            method="POST",
            payload=exact_replay_request,
        )
    )
    if replayed != exact_replay_response:
        raise RuntimeError("Headless presentation replay changed accepted meaning.")
    for suffix in ("?learner_id=someone-else", "/history?limit=1", "/export?private=true"):
        status, denial = _request_json_read_status(
            opener,
            origin=origin,
            path=f"/api/v1/learner-presentation-preferences{suffix}",
        )
        if status != 400 or denial.get("code") != "invalid_request":
            raise RuntimeError("Presentation preference guessed input was not denied.")
    return {"profile": profile, "history": history, "export": export_document}


def presentation_preference_source_fingerprint(postgres_dsn: str) -> dict[str, Any]:
    with psycopg.connect(postgres_dsn) as connection:
        tables = [
            (str(row[0]), str(row[1]))
            for row in connection.execute(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                  AND table_schema NOT IN ('information_schema', 'pg_catalog', 'identity')
                  AND table_schema NOT LIKE 'pg\\_%' ESCAPE '\\'
                ORDER BY table_schema, table_name
                """
            ).fetchall()
            if not (
                str(row[0]) == "learner_model"
                and str(row[1]) in PRESENTATION_PREFERENCE_TABLES
            )
        ]
        digest = hashlib.sha256()
        row_count = 0
        for schema, table in tables:
            rows = connection.execute(
                sql.SQL(
                    "SELECT to_jsonb(row_value)::text FROM {}.{} AS row_value "
                    "ORDER BY to_jsonb(row_value)::text"
                ).format(sql.Identifier(schema), sql.Identifier(table))
            ).fetchall()
            row_count += len(rows)
            digest.update(f"{schema}.{table}\0{len(rows)}\0".encode("utf-8"))
            for row in rows:
                digest.update(str(row[0]).encode("utf-8"))
                digest.update(b"\0")
    return {"table_count": len(tables), "row_count": row_count, "sha256": digest.hexdigest()}


def presentation_preference_storage_snapshot(postgres_dsn: str) -> dict[str, Any]:
    with psycopg.connect(postgres_dsn) as connection:
        profiles = connection.execute(
            """
            SELECT profile_id, learner_id::text, revision, profile, profile_digest
            FROM learner_model.presentation_preference_profiles ORDER BY profile_id
            """
        ).fetchall()
        changes = connection.execute(
            """
            SELECT learner_id::text, revision, change, resulting_profile_digest
            FROM learner_model.presentation_preference_changes ORDER BY learner_id, revision
            """
        ).fetchall()
        mutations = connection.execute(
            """
            SELECT learner_id::text, idempotency_key, accepted_revision, accepted_profile
            FROM learner_model.presentation_preference_mutations
            ORDER BY learner_id, accepted_revision, idempotency_key
            """
        ).fetchall()
    return {
        "profiles": [
            [str(row[0]), str(row[1]), int(row[2]), copy.deepcopy(row[3]), str(row[4])]
            for row in profiles
        ],
        "changes": [
            [str(row[0]), int(row[1]), copy.deepcopy(row[2]), str(row[3])]
            for row in changes
        ],
        "mutations": [
            [str(row[0]), str(row[1]), int(row[2]), copy.deepcopy(row[3])]
            for row in mutations
        ],
    }


def assert_presentation_preference_storage(
    snapshot: dict[str, Any],
    *,
    profile: dict[str, Any],
    history: dict[str, Any],
    exact_replay_request: dict[str, Any] | None = None,
    exact_replay_response: dict[str, Any] | None = None,
) -> None:
    profiles = snapshot.get("profiles")
    changes = snapshot.get("changes")
    mutations = snapshot.get("mutations")
    if (
        not isinstance(profiles, list)
        or len(profiles) != 1
        or not isinstance(changes, list)
        or len(changes) != len(history["changes"])
        or not isinstance(mutations, list)
        or len(mutations) != profile["revision"] - 1
    ):
        raise RuntimeError("Presentation preference storage row counts are uncorrelated.")
    stored = profiles[0]
    if (
        stored[0] != profile["profile_id"]
        or stored[1] != profile["learner_id"]
        or stored[2] != profile["revision"]
        or stable_presentation_preference_profile(stored[3]) != profile
        or stored[4] != profile["profile_digest"]
    ):
        raise RuntimeError("Presentation preference stored profile is uncorrelated.")
    if [row[2] for row in changes] != history["changes"] or any(
        row[0] != profile["learner_id"]
        or row[1] != row[2]["revision"]
        or row[3] != row[2]["resulting_profile_digest"]
        for row in changes
    ):
        raise RuntimeError("Presentation preference stored history is uncorrelated.")
    expected_mutation_revisions = list(range(2, profile["revision"] + 1))
    expected_history_revisions = list(
        range(max(2, profile["revision"] - 99), profile["revision"] + 1)
    )
    history_by_revision = {
        change["revision"]: change for change in history["changes"]
    }
    if (
        [change["revision"] for change in history["changes"]]
        != expected_history_revisions
        or len(history_by_revision) != len(expected_history_revisions)
    ):
        raise RuntimeError("Presentation preference history revision coverage is invalid.")
    mutation_keys = [row[1] for row in mutations]
    if (
        [row[2] for row in mutations] != expected_mutation_revisions
        or len(set(mutation_keys)) != len(mutation_keys)
        or not all(_preference_identifier(key) for key in mutation_keys)
    ):
        raise RuntimeError("Presentation preference replay revision or key coverage is invalid.")
    if any(
        row[0] != profile["learner_id"]
        or row[2] != row[3].get("revision")
        or stable_presentation_preference_profile(row[3]) != row[3]
        or row[2] in history_by_revision
        and row[3]["profile_digest"]
        != history_by_revision[row[2]]["resulting_profile_digest"]
        for row in mutations
    ):
        raise RuntimeError("Presentation preference replay storage is uncorrelated.")
    if (exact_replay_request is None) != (exact_replay_response is None):
        raise RuntimeError("Presentation preference exact replay evidence is incomplete.")
    if exact_replay_request is not None and exact_replay_response is not None:
        replay_request = stable_presentation_preference_request(exact_replay_request)
        replay_response = stable_presentation_preference_profile(exact_replay_response)
        replay_rows = [
            row for row in mutations if row[1] == replay_request["idempotency_key"]
        ]
        if (
            len(replay_rows) != 1
            or replay_rows[0][2] != replay_response["revision"]
            or replay_rows[0][3] != replay_response
        ):
            raise RuntimeError("Presentation preference exact replay row is uncorrelated.")


def _run_presentation_preference_race(
    *,
    origin: str,
    requests: list[dict[str, Any]],
) -> list[tuple[int, dict[str, Any]]]:
    openers = open_learner_preference_sessions(origin, len(requests))
    barrier = threading.Barrier(len(requests))

    def send(
        opener: urllib.request.OpenerDirector,
        request: dict[str, Any],
    ) -> tuple[int, dict[str, Any]]:
        barrier.wait(timeout=10)
        return _request_json_status(
            opener,
            origin=origin,
            path="/api/v1/learner-presentation-preferences/mutations",
            method="POST",
            payload=request,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(send, opener, request)
            for opener, request in zip(openers, requests, strict=True)
        ]
        return [future.result(timeout=20) for future in futures]


def assert_presentation_preference_race_outcomes(
    *,
    name: str,
    requests: list[dict[str, Any]],
    results: list[tuple[int, dict[str, Any]]],
    before_storage: dict[str, Any],
    after_storage: dict[str, Any],
) -> dict[str, Any]:
    accepted = [document for status, document in results if status == 200]
    denials = [(status, document) for status, document in results if status != 200]
    expected_accepted = 2 if name == "same_key_same_payload" else 1
    if len(results) != 2 or len(accepted) != expected_accepted:
        raise RuntimeError("Presentation preference race acceptance matrix is invalid.")
    stable_accepted = [stable_presentation_preference_profile(item) for item in accepted]
    if name == "same_key_same_payload" and stable_accepted[0] != stable_accepted[1]:
        raise RuntimeError("Presentation exact concurrent replays did not converge.")
    if name != "same_key_same_payload":
        if len(denials) != 1:
            raise RuntimeError("Presentation preference race denial matrix is invalid.")
        _assert_safe_presentation_preference_denial(
            denials[0][0],
            denials[0][1],
            expected_code=(
                ("immutable_conflict", "stale_revision")
                if name == "same_key_changed_payload"
                else "stale_revision"
            ),
            requests=requests,
        )
    for key in ("profiles", "changes", "mutations"):
        before = before_storage.get(key)
        after = after_storage.get(key)
        if not isinstance(before, list) or not isinstance(after, list):
            raise RuntimeError("Presentation preference race storage is invalid.")
        if key == "profiles":
            if len(before) != 1 or len(after) != 1 or after[0][2] != before[0][2] + 1:
                raise RuntimeError("Presentation preference race revision is invalid.")
        elif len(after) != len(before) + 1:
            raise RuntimeError("Presentation preference race appended an invalid row count.")
    current = after_storage["profiles"][0][3]
    if current not in stable_accepted:
        raise RuntimeError("Presentation preference race result did not persist.")
    return stable_presentation_preference_profile(current)


def qualify_presentation_preference_races(
    *,
    origin: str,
    postgres_dsn: str,
    capture: dict[str, Any],
) -> dict[str, Any]:
    outcomes: dict[str, list[str]] = {}
    current_profile = capture["profile"]
    for name in (
        "same_key_same_payload",
        "same_key_changed_payload",
        "different_key_same_revision",
    ):
        requests = capture["races"][name]["requests"]
        before = presentation_preference_storage_snapshot(postgres_dsn)
        results = _run_presentation_preference_race(origin=origin, requests=requests)
        after = presentation_preference_storage_snapshot(postgres_dsn)
        current_profile = assert_presentation_preference_race_outcomes(
            name=name,
            requests=requests,
            results=results,
            before_storage=before,
            after_storage=after,
        )
        outcomes[name] = [
            "accepted"
            if status == 200
            else "conflict"
            if document.get("code") == "immutable_conflict"
            else "stale"
            for status, document in results
        ]
        expected = sorted(capture["races"][name]["expected"])
        allowed = (
            {("accepted", "conflict"), ("accepted", "stale")}
            if name == "same_key_changed_payload"
            else {tuple(expected)}
        )
        if tuple(sorted(outcomes[name])) not in allowed:
            raise RuntimeError("Presentation preference race outcome classes changed.")
    opener = open_learner_preference_session(origin)
    history = stable_presentation_preference_history(
        _request_json(
            opener,
            origin=origin,
            path="/api/v1/learner-presentation-preferences/history",
        ),
        profile=current_profile,
    )
    export_document = stable_presentation_preference_export(
        _request_json(
            opener,
            origin=origin,
            path="/api/v1/learner-presentation-preferences/export",
        ),
        profile=current_profile,
        history=history,
    )
    storage = presentation_preference_storage_snapshot(postgres_dsn)
    assert_presentation_preference_storage(
        storage,
        profile=current_profile,
        history=history,
        exact_replay_request=capture["exact_replay_request"],
        exact_replay_response=capture["exact_replay_response"],
    )
    return {
        "profile": current_profile,
        "history": history,
        "export": export_document,
        "storage": storage,
        "outcomes": outcomes,
    }


def stable_assistance_preference_profile(
    document: dict[str, Any],
) -> dict[str, Any]:
    if set(document) != ASSISTANCE_PREFERENCE_PROFILE_KEYS:
        raise RuntimeError("Assistance preference profile has an open or incomplete shape.")
    if (
        document.get("schema_version") != "1.0.0"
        or not _preference_identifier(document.get("profile_id"))
        or not isinstance(document.get("learner_id"), str)
        or not isinstance(document.get("revision"), int)
        or isinstance(document.get("revision"), bool)
        or document["revision"] < 1
        or document.get("assistance_mode") not in {"off", "on_request"}
        or not isinstance(document.get("profile_digest"), str)
        or re.fullmatch(r"[a-f0-9]{64}", document["profile_digest"]) is None
    ):
        raise RuntimeError("Assistance preference profile identity or choice is invalid.")
    try:
        learner_id = UUID(document["learner_id"])
    except ValueError as error:
        raise RuntimeError("Assistance preference learner identity is invalid.") from error
    if str(learner_id) != document["learner_id"]:
        raise RuntimeError("Assistance preference learner identity is not canonical.")
    created_at = _preference_time(
        document.get("created_at"), label="Assistance preference created time"
    )
    updated_at = _preference_time(
        document.get("updated_at"), label="Assistance preference updated time"
    )
    if updated_at < created_at:
        raise RuntimeError("Assistance preference chronology is invalid.")
    material = {
        key: copy.deepcopy(value)
        for key, value in document.items()
        if key != "profile_digest"
    }
    if _canonical_sha256(material) != document["profile_digest"]:
        raise RuntimeError("Assistance preference profile digest is invalid.")
    return copy.deepcopy(document)


def stable_assistance_preference_history(
    document: dict[str, Any],
    *,
    profile: dict[str, Any],
) -> dict[str, Any]:
    stable = stable_presentation_preference_history(document, profile=profile)
    expected_revisions = list(
        range(max(2, profile["revision"] - 99), profile["revision"] + 1)
    )
    if [change["revision"] for change in stable["changes"]] != expected_revisions:
        raise RuntimeError("Assistance preference history coverage is invalid.")
    return stable


def stable_assistance_preference_export(
    document: dict[str, Any],
    *,
    profile: dict[str, Any],
    history: dict[str, Any],
) -> dict[str, Any]:
    return stable_presentation_preference_export(
        document,
        profile=profile,
        history=history,
    )


def stable_assistance_preference_request(
    document: dict[str, Any],
) -> dict[str, Any]:
    if set(document) != PRESENTATION_PREFERENCE_REQUEST_KEYS or (
        document.get("schema_version") != "1.0.0"
        or not _preference_identifier(document.get("idempotency_key"))
        or not isinstance(document.get("expected_revision"), int)
        or isinstance(document.get("expected_revision"), bool)
        or document["expected_revision"] < 1
        or not isinstance(document.get("mutation"), dict)
    ):
        raise RuntimeError("Assistance preference mutation request is invalid.")
    mutation = document["mutation"]
    if mutation.get("operation") == "reset_profile":
        if set(mutation) != {"operation"}:
            raise RuntimeError("Assistance preference reset request is open.")
    elif mutation.get("operation") == "replace_preferences":
        if set(mutation) != {"operation", "assistance_mode"} or mutation.get(
            "assistance_mode"
        ) not in {"off", "on_request"}:
            raise RuntimeError("Assistance preference replacement request is invalid.")
    else:
        raise RuntimeError("Assistance preference mutation operation is invalid.")
    return copy.deepcopy(document)


def stable_local_reminder_envelope(document: dict[str, Any]) -> dict[str, Any]:
    if set(document) != {
        "schema_version",
        "revision",
        "reminder_mode",
        "updated_at",
        "changes",
        "integrity_code",
    }:
        raise RuntimeError("Local reminder envelope is not closed.")
    revision = document.get("revision")
    if (
        document.get("schema_version") != "1.0.0"
        or not isinstance(revision, int)
        or isinstance(revision, bool)
        or revision < 1
        or document.get("reminder_mode") not in {"off", "in_app_when_available"}
        or not isinstance(document.get("changes"), list)
        or len(document["changes"]) > 100
        or not isinstance(document.get("integrity_code"), str)
        or re.fullmatch(r"[a-f0-9]{64}", document["integrity_code"]) is None
    ):
        raise RuntimeError("Local reminder envelope values are invalid.")
    updated_at = _preference_time(
        document.get("updated_at"), label="Local reminder update time"
    )
    first_revision = max(2, revision - 99)
    expected_revisions = list(range(first_revision, revision + 1))
    observed_revisions: list[int] = []
    previous_time: datetime | None = None
    for change in document["changes"]:
        if not isinstance(change, dict) or set(change) != {
            "schema_version",
            "revision",
            "operation",
            "occurred_at",
        }:
            raise RuntimeError("Local reminder change is not closed.")
        occurred_at = _preference_time(
            change.get("occurred_at"), label="Local reminder change time"
        )
        if (
            change.get("schema_version") != "1.0.0"
            or change.get("operation")
            not in {"replace_preference", "reset_preference"}
            or not isinstance(change.get("revision"), int)
            or isinstance(change.get("revision"), bool)
            or occurred_at > updated_at
            or previous_time is not None
            and occurred_at < previous_time
        ):
            raise RuntimeError("Local reminder change is invalid.")
        observed_revisions.append(change["revision"])
        previous_time = occurred_at
    if observed_revisions != expected_revisions:
        raise RuntimeError("Local reminder history coverage is invalid.")
    material = {
        key: copy.deepcopy(value)
        for key, value in document.items()
        if key != "integrity_code"
    }
    if _canonical_sha256(material) != document["integrity_code"]:
        raise RuntimeError("Local reminder integrity code is invalid.")
    return copy.deepcopy(document)


def stable_local_reminder_export(
    document: dict[str, Any],
    *,
    expected_preference: dict[str, Any],
) -> dict[str, Any]:
    if set(document) != {"schema_version", "purpose", "limitations", "preference"} or (
        document.get("schema_version") != "1.0.0"
        or not isinstance(document.get("purpose"), str)
        or not document["purpose"]
        or not isinstance(document.get("limitations"), list)
        or not 1 <= len(document["limitations"]) <= 8
        or not all(isinstance(item, str) and item for item in document["limitations"])
        or document.get("preference") != expected_preference
    ):
        raise RuntimeError("Local reminder export is invalid.")
    stable_local_reminder_envelope(document["preference"])
    if "learner_id" in _nested_mapping_keys(document):
        raise RuntimeError("Local reminder export contains learner identity.")
    return copy.deepcopy(document)


def load_assistance_preference_capture(
    path: Path,
    *,
    data_root: Path,
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("The bounded assistance preference capture is absent.")
    resolved = path.resolve()
    if resolved.parent != data_root.resolve() or resolved.stat().st_size > 524_288:
        raise RuntimeError("Assistance preference capture escaped its bounded root.")
    capture = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(capture, dict) or set(capture) != ASSISTANCE_PREFERENCE_CAPTURE_ROOT_KEYS:
        raise RuntimeError("Assistance preference capture has an invalid shape.")
    leaked = ASSISTANCE_PREFERENCE_PRIVATE_CAPTURE_KEYS & _nested_mapping_keys(capture)
    if leaked:
        raise RuntimeError("Assistance preference capture contains private authority data.")
    if capture.get("schema_version") != "1.0.0" or not all(
        isinstance(capture.get(key), dict)
        for key in (
            "profile",
            "history",
            "export",
            "exact_replay_request",
            "exact_replay_response",
            "local",
            "races",
            "expected",
        )
    ):
        raise RuntimeError("Assistance preference capture documents are invalid.")
    profile = stable_assistance_preference_profile(capture["profile"])
    history = stable_assistance_preference_history(capture["history"], profile=profile)
    stable_assistance_preference_export(
        capture["export"], profile=profile, history=history
    )
    exact_request = stable_assistance_preference_request(
        capture["exact_replay_request"]
    )
    exact_response = stable_assistance_preference_profile(
        capture["exact_replay_response"]
    )
    if (
        exact_response != profile
        or exact_request["expected_revision"] + 1 != profile["revision"]
        or exact_request["mutation"] != {"operation": "reset_profile"}
        or profile["assistance_mode"] != "off"
    ):
        raise RuntimeError("Assistance preference exact replay is not correlated.")

    local = capture["local"]
    if set(local) != {"saved", "export", "reset"}:
        raise RuntimeError("Local reminder capture is not closed.")
    saved_local = stable_local_reminder_envelope(local["saved"])
    reset_local = stable_local_reminder_envelope(local["reset"])
    stable_local_reminder_export(local["export"], expected_preference=saved_local)
    expected = capture["expected"]
    reset_revisions = {
        change["revision"]
        for change in history["changes"]
        if change["operation"] == "reset_profile"
    }
    if (
        set(expected) != ASSISTANCE_PREFERENCE_EXPECTED_KEYS
        or expected.get("first_open_server_revision") != 1
        or expected.get("local_saved_revision") != saved_local["revision"]
        or expected.get("local_reset_revision") != reset_local["revision"]
        or saved_local["reminder_mode"] != "in_app_when_available"
        or reset_local["reminder_mode"] != "off"
        or reset_local["revision"] != saved_local["revision"] + 1
        or expected.get("reset_recorded") is not True
        or profile["revision"] not in reset_revisions
    ):
        raise RuntimeError("Assistance preference expected summary is not correlated.")

    races = capture["races"]
    expected_classes = {
        "same_key_same_payload": ["accepted", "accepted"],
        "same_key_changed_payload": ["accepted", "conflict"],
        "different_key_same_revision": ["accepted", "stale"],
    }
    if set(races) != set(expected_classes):
        raise RuntimeError("Assistance preference race matrix is incomplete.")
    for offset, (name, expected_outcomes) in enumerate(expected_classes.items()):
        case = races.get(name)
        if not isinstance(case, dict) or set(case) != {"requests", "expected"}:
            raise RuntimeError("Assistance preference race case is not closed.")
        requests = case.get("requests")
        if not isinstance(requests, list) or len(requests) != 2:
            raise RuntimeError("Assistance preference race request pair is invalid.")
        stable_requests = [
            stable_assistance_preference_request(request)
            if isinstance(request, dict)
            else (_ for _ in ()).throw(
                RuntimeError("Assistance preference race request is invalid.")
            )
            for request in requests
        ]
        if (
            sorted(case.get("expected", [])) != sorted(expected_outcomes)
            or any(
                request["expected_revision"] != profile["revision"] + offset
                for request in stable_requests
            )
        ):
            raise RuntimeError("Assistance preference race expectations are invalid.")
        keys = [request["idempotency_key"] for request in stable_requests]
        mutations = [request["mutation"] for request in stable_requests]
        if name == "same_key_same_payload" and not (
            keys[0] == keys[1]
            and mutations[0] == mutations[1]
            and mutations[0] == {
                "operation": "replace_preferences",
                "assistance_mode": "on_request",
            }
        ):
            raise RuntimeError("Assistance exact replay race does not match.")
        if name == "same_key_changed_payload" and not (
            keys[0] == keys[1]
            and {
                json.dumps(mutation, sort_keys=True)
                for mutation in mutations
            }
            == {
                json.dumps(
                    {
                        "operation": "replace_preferences",
                        "assistance_mode": "off",
                    },
                    sort_keys=True,
                ),
                json.dumps({"operation": "reset_profile"}, sort_keys=True),
            }
        ):
            raise RuntimeError("Assistance conflict race is not key-scoped.")
        if name == "different_key_same_revision" and not (
            keys[0] != keys[1]
            and mutations[0] == mutations[1]
            and mutations[0] == {
                "operation": "replace_preferences",
                "assistance_mode": "on_request",
            }
        ):
            raise RuntimeError("Assistance stale race is not revision-scoped.")
    return copy.deepcopy(capture)


def observe_headless_assistance_preferences(
    *,
    origin: str,
    expected_profile: dict[str, Any],
    expected_history: dict[str, Any],
    expected_export: dict[str, Any],
    exact_replay_request: dict[str, Any],
    exact_replay_response: dict[str, Any],
) -> dict[str, Any]:
    opener = open_learner_preference_session(origin)
    root = "/api/v1/learner-assistance-preferences"
    profile = stable_assistance_preference_profile(
        _request_json(opener, origin=origin, path=root)
    )
    history = stable_assistance_preference_history(
        _request_json(opener, origin=origin, path=f"{root}/history"),
        profile=profile,
    )
    export_document = stable_assistance_preference_export(
        _request_json(opener, origin=origin, path=f"{root}/export"),
        profile=profile,
        history=history,
    )
    if profile != expected_profile or history != expected_history or any(
        export_document[key] != expected_export[key]
        for key in PRESENTATION_PREFERENCE_EXPORT_KEYS - {"exported_at"}
    ):
        raise RuntimeError("Headless assistance preferences changed browser meaning.")
    replayed = stable_assistance_preference_profile(
        _request_json(
            opener,
            origin=origin,
            path=f"{root}/mutations",
            method="POST",
            payload=exact_replay_request,
        )
    )
    if replayed != exact_replay_response:
        raise RuntimeError("Headless assistance replay changed accepted meaning.")
    for suffix in ("?learner_id=someone-else", "/history?limit=1", "/export?private=true"):
        status, denial = _request_json_read_status(
            opener, origin=origin, path=f"{root}{suffix}"
        )
        if status != 400 or denial.get("code") != "invalid_request":
            raise RuntimeError("Assistance preference guessed input was not denied.")
    return {"profile": profile, "history": history, "export": export_document}


def assistance_preference_source_fingerprint(postgres_dsn: str) -> dict[str, Any]:
    with psycopg.connect(postgres_dsn) as connection:
        tables = [
            (str(row[0]), str(row[1]))
            for row in connection.execute(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                  AND table_schema NOT IN ('information_schema', 'pg_catalog', 'identity')
                  AND table_schema NOT LIKE 'pg\\_%' ESCAPE '\\'
                ORDER BY table_schema, table_name
                """
            ).fetchall()
            if not (
                str(row[0]) == "learner_model"
                and str(row[1]) in ASSISTANCE_PREFERENCE_TABLES
            )
        ]
        digest = hashlib.sha256()
        row_count = 0
        for schema, table in tables:
            rows = connection.execute(
                sql.SQL(
                    "SELECT to_jsonb(row_value)::text FROM {}.{} AS row_value "
                    "ORDER BY to_jsonb(row_value)::text"
                ).format(sql.Identifier(schema), sql.Identifier(table))
            ).fetchall()
            row_count += len(rows)
            digest.update(f"{schema}.{table}\0{len(rows)}\0".encode("utf-8"))
            for row in rows:
                digest.update(str(row[0]).encode("utf-8"))
                digest.update(b"\0")
    return {
        "table_count": len(tables),
        "row_count": row_count,
        "sha256": digest.hexdigest(),
    }


def assistance_preference_storage_snapshot(postgres_dsn: str) -> dict[str, Any]:
    with psycopg.connect(postgres_dsn) as connection:
        profiles = connection.execute(
            """
            SELECT profile_id, learner_id::text, revision, profile, profile_digest
            FROM learner_model.assistance_preference_profiles ORDER BY profile_id
            """
        ).fetchall()
        changes = connection.execute(
            """
            SELECT learner_id::text, revision, change, resulting_profile_digest
            FROM learner_model.assistance_preference_changes ORDER BY learner_id, revision
            """
        ).fetchall()
        mutations = connection.execute(
            """
            SELECT learner_id::text, idempotency_key, accepted_revision, accepted_profile
            FROM learner_model.assistance_preference_mutations
            ORDER BY learner_id, accepted_revision, idempotency_key
            """
        ).fetchall()
    return {
        "profiles": [
            [str(row[0]), str(row[1]), int(row[2]), copy.deepcopy(row[3]), str(row[4])]
            for row in profiles
        ],
        "changes": [
            [str(row[0]), int(row[1]), copy.deepcopy(row[2]), str(row[3])]
            for row in changes
        ],
        "mutations": [
            [str(row[0]), str(row[1]), int(row[2]), copy.deepcopy(row[3])]
            for row in mutations
        ],
    }


def preference_family_storage_snapshot(postgres_dsn: str) -> dict[str, Any]:
    """Return the three existing preference stores without creating an aggregate model."""
    return {
        "learner": learner_preference_storage_snapshot(postgres_dsn),
        "presentation": presentation_preference_storage_snapshot(postgres_dsn),
        "assistance": assistance_preference_storage_snapshot(postgres_dsn),
    }


def _validate_preference_family_snapshot(
    snapshot: dict[str, Any],
    *,
    label: str,
) -> None:
    if set(snapshot) != PREFERENCE_FAMILY_NAMES:
        raise RuntimeError(f"{label} preference-family snapshot is not closed.")
    for family in sorted(PREFERENCE_FAMILY_NAMES):
        storage = snapshot[family]
        if (
            not isinstance(storage, dict)
            or set(storage) != PREFERENCE_STORAGE_KEYS
            or any(not isinstance(storage[key], list) for key in PREFERENCE_STORAGE_KEYS)
        ):
            raise RuntimeError(
                f"{label} {family} preference storage snapshot is invalid."
            )


def assert_preference_family_isolation(
    before: dict[str, Any],
    after: dict[str, Any],
    *,
    changed_family: str,
) -> None:
    """Require one named preference store to change and the other two to stay exact."""
    _validate_preference_family_snapshot(before, label="Before")
    _validate_preference_family_snapshot(after, label="After")
    if changed_family not in PREFERENCE_FAMILY_NAMES:
        raise RuntimeError("Preference-family isolation named an unknown family.")
    if before[changed_family] == after[changed_family]:
        raise RuntimeError(
            f"The {changed_family} preference phase created no durable change."
        )
    leaked = sorted(
        family
        for family in PREFERENCE_FAMILY_NAMES - {changed_family}
        if before[family] != after[family]
    )
    if leaked:
        raise RuntimeError(
            "Preference-family isolation failed; unexpected change in "
            + ", ".join(leaked)
            + "."
        )


def stable_preference_system_report(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Validate cumulative family identity and return non-sensitive report facts."""
    _validate_preference_family_snapshot(snapshot, label="Final")
    learner_ids: set[str] = set()
    profile_ids: set[str] = set()
    for family in sorted(PREFERENCE_FAMILY_NAMES):
        storage = snapshot[family]
        profiles = storage["profiles"]
        if (
            len(profiles) != 1
            or len(profiles[0]) != 5
            or not storage["changes"]
            or not storage["mutations"]
        ):
            raise RuntimeError(
                f"Final {family} preference evidence is incomplete."
            )
        profile_ids.add(str(profiles[0][0]))
        learner_ids.add(str(profiles[0][1]))
    if len(learner_ids) != 1:
        raise RuntimeError(
            "Preference families do not share one authorized learner context."
        )
    if len(profile_ids) != len(PREFERENCE_FAMILY_NAMES):
        raise RuntimeError("Preference families do not retain distinct profile identities.")
    return {
        "browser_local_adapter_count": 2,
        "cross_family_storage_isolation": True,
        "distinct_profile_identities": True,
        "learner_context_count": 1,
        "public_api_family_count": len(PREFERENCE_FAMILY_NAMES),
        "shared_core_semantics": True,
    }


def assert_assistance_preference_storage(
    snapshot: dict[str, Any],
    *,
    profile: dict[str, Any],
    history: dict[str, Any],
    exact_replay_request: dict[str, Any] | None = None,
    exact_replay_response: dict[str, Any] | None = None,
) -> None:
    profiles = snapshot.get("profiles")
    changes = snapshot.get("changes")
    mutations = snapshot.get("mutations")
    if (
        not isinstance(profiles, list)
        or len(profiles) != 1
        or not isinstance(changes, list)
        or len(changes) != len(history["changes"])
        or not isinstance(mutations, list)
        or len(mutations) != profile["revision"] - 1
    ):
        raise RuntimeError("Assistance preference storage row counts are uncorrelated.")
    stored = profiles[0]
    if (
        stored[0] != profile["profile_id"]
        or stored[1] != profile["learner_id"]
        or stored[2] != profile["revision"]
        or stable_assistance_preference_profile(stored[3]) != profile
        or stored[4] != profile["profile_digest"]
    ):
        raise RuntimeError("Assistance preference stored profile is uncorrelated.")
    if [row[2] for row in changes] != history["changes"] or any(
        row[0] != profile["learner_id"]
        or row[1] != row[2]["revision"]
        or row[3] != row[2]["resulting_profile_digest"]
        for row in changes
    ):
        raise RuntimeError("Assistance preference stored history is uncorrelated.")
    expected_mutation_revisions = list(range(2, profile["revision"] + 1))
    history_by_revision = {
        change["revision"]: change for change in history["changes"]
    }
    mutation_keys = [row[1] for row in mutations]
    if (
        [row[2] for row in mutations] != expected_mutation_revisions
        or len(set(mutation_keys)) != len(mutation_keys)
        or not all(_preference_identifier(key) for key in mutation_keys)
        or any(
            row[0] != profile["learner_id"]
            or row[2] != row[3].get("revision")
            or stable_assistance_preference_profile(row[3]) != row[3]
            or row[2] in history_by_revision
            and row[3]["profile_digest"]
            != history_by_revision[row[2]]["resulting_profile_digest"]
            for row in mutations
        )
    ):
        raise RuntimeError("Assistance preference replay storage is uncorrelated.")
    if (exact_replay_request is None) != (exact_replay_response is None):
        raise RuntimeError("Assistance preference exact replay evidence is incomplete.")
    if exact_replay_request is not None and exact_replay_response is not None:
        replay_request = stable_assistance_preference_request(exact_replay_request)
        replay_response = stable_assistance_preference_profile(exact_replay_response)
        replay_rows = [
            row for row in mutations if row[1] == replay_request["idempotency_key"]
        ]
        if (
            len(replay_rows) != 1
            or replay_rows[0][2] != replay_response["revision"]
            or replay_rows[0][3] != replay_response
        ):
            raise RuntimeError("Assistance preference exact replay row is uncorrelated.")


def _assert_safe_assistance_preference_denial(
    status: int,
    document: dict[str, Any],
    *,
    expected_code: str | tuple[str, ...],
    requests: list[dict[str, Any]],
) -> None:
    expected_codes = (
        frozenset(expected_code) if isinstance(expected_code, tuple) else {expected_code}
    )
    if status != 409 or set(document) != ASSISTANCE_PREFERENCE_DENIAL_KEYS or (
        document.get("error_version") != "1.0"
        or document.get("code") not in expected_codes
    ):
        raise RuntimeError(
            "Assistance preference denial changed public meaning: "
            f"status={status}, code={document.get('code')!r}, "
            f"keys={sorted(document)}."
        )
    try:
        correlation_id = UUID(str(document.get("correlation_id")))
    except ValueError as error:
        raise RuntimeError("Assistance preference denial correlation is invalid.") from error
    if str(correlation_id) != document.get("correlation_id"):
        raise RuntimeError("Assistance preference denial correlation is not canonical.")
    serialized = json.dumps(document, ensure_ascii=False, sort_keys=True).casefold()
    keys = {str(request["idempotency_key"]).casefold() for request in requests}
    if any(key in serialized for key in keys) or any(
        marker in serialized
        for marker in (
            "learner_id",
            "assistance_preference_mutations",
            "request_fingerprint",
            "postgres",
            "traceback",
        )
    ):
        raise RuntimeError("Assistance preference denial disclosed private details.")


def _run_assistance_preference_race(
    *,
    origin: str,
    requests: list[dict[str, Any]],
) -> list[tuple[int, dict[str, Any]]]:
    openers = open_learner_preference_sessions(origin, len(requests))
    barrier = threading.Barrier(len(requests))

    def send(
        opener: urllib.request.OpenerDirector,
        request: dict[str, Any],
    ) -> tuple[int, dict[str, Any]]:
        barrier.wait(timeout=10)
        return _request_json_status(
            opener,
            origin=origin,
            path="/api/v1/learner-assistance-preferences/mutations",
            method="POST",
            payload=request,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(send, opener, request)
            for opener, request in zip(openers, requests, strict=True)
        ]
        return [future.result(timeout=20) for future in futures]


def assert_assistance_preference_race_outcomes(
    *,
    name: str,
    requests: list[dict[str, Any]],
    results: list[tuple[int, dict[str, Any]]],
    before_storage: dict[str, Any],
    after_storage: dict[str, Any],
) -> dict[str, Any]:
    accepted = [document for status, document in results if status == 200]
    denials = [(status, document) for status, document in results if status != 200]
    expected_accepted = 2 if name == "same_key_same_payload" else 1
    if len(results) != 2 or len(accepted) != expected_accepted:
        raise RuntimeError("Assistance preference race acceptance matrix is invalid.")
    stable_accepted = [stable_assistance_preference_profile(item) for item in accepted]
    if name == "same_key_same_payload" and stable_accepted[0] != stable_accepted[1]:
        raise RuntimeError("Assistance exact concurrent replays did not converge.")
    if name != "same_key_same_payload":
        if len(denials) != 1:
            raise RuntimeError("Assistance preference race denial matrix is invalid.")
        _assert_safe_assistance_preference_denial(
            denials[0][0],
            denials[0][1],
            expected_code=(
                ("immutable_conflict", "stale_revision")
                if name == "same_key_changed_payload"
                else "stale_revision"
            ),
            requests=requests,
        )
    for key in ("profiles", "changes", "mutations"):
        before = before_storage.get(key)
        after = after_storage.get(key)
        if not isinstance(before, list) or not isinstance(after, list):
            raise RuntimeError("Assistance preference race storage is invalid.")
        if key == "profiles":
            if len(before) != 1 or len(after) != 1 or after[0][2] != before[0][2] + 1:
                raise RuntimeError("Assistance preference race revision is invalid.")
        elif len(after) != len(before) + 1:
            raise RuntimeError("Assistance preference race appended an invalid row count.")
    current = after_storage["profiles"][0][3]
    if current not in stable_accepted:
        raise RuntimeError("Assistance preference race result did not persist.")
    return stable_assistance_preference_profile(current)


def qualify_assistance_preference_races(
    *,
    origin: str,
    postgres_dsn: str,
    capture: dict[str, Any],
) -> dict[str, Any]:
    outcomes: dict[str, list[str]] = {}
    current_profile = capture["profile"]
    for name in (
        "same_key_same_payload",
        "same_key_changed_payload",
        "different_key_same_revision",
    ):
        requests = capture["races"][name]["requests"]
        before = assistance_preference_storage_snapshot(postgres_dsn)
        results = _run_assistance_preference_race(origin=origin, requests=requests)
        after = assistance_preference_storage_snapshot(postgres_dsn)
        current_profile = assert_assistance_preference_race_outcomes(
            name=name,
            requests=requests,
            results=results,
            before_storage=before,
            after_storage=after,
        )
        outcomes[name] = [
            "accepted"
            if status == 200
            else "conflict"
            if document.get("code") == "immutable_conflict"
            else "stale"
            for status, document in results
        ]
        expected = sorted(capture["races"][name]["expected"])
        allowed = (
            {("accepted", "conflict"), ("accepted", "stale")}
            if name == "same_key_changed_payload"
            else {tuple(expected)}
        )
        if tuple(sorted(outcomes[name])) not in allowed:
            raise RuntimeError("Assistance preference race outcome classes changed.")
    opener = open_learner_preference_session(origin)
    root = "/api/v1/learner-assistance-preferences"
    history = stable_assistance_preference_history(
        _request_json(opener, origin=origin, path=f"{root}/history"),
        profile=current_profile,
    )
    export_document = stable_assistance_preference_export(
        _request_json(opener, origin=origin, path=f"{root}/export"),
        profile=current_profile,
        history=history,
    )
    storage = assistance_preference_storage_snapshot(postgres_dsn)
    assert_assistance_preference_storage(
        storage,
        profile=current_profile,
        history=history,
        exact_replay_request=capture["exact_replay_request"],
        exact_replay_response=capture["exact_replay_response"],
    )
    return {
        "profile": current_profile,
        "history": history,
        "export": export_document,
        "storage": storage,
        "outcomes": outcomes,
    }


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


def npm_e2e_command(*test_files: str) -> list[str]:
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
    command = [
        *prefix,
        "--prefix",
        str(REPOSITORY / "apps" / "web"),
        "run",
        "test:e2e",
    ]
    if test_files:
        command.extend(("--", *test_files))
    return command


def remove_container(container_name: str | None) -> None:
    if not container_name:
        return
    if not container_name.startswith(
        (CONTAINER_PREFIX, RECOVERY_CONTAINER_PREFIX)
    ):
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

    run_replay_qualification()

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
    recovery_container_name: str | None = None
    application: subprocess.Popen[str] | None = None
    application_log = data_root / "python-application.log"
    practice_capture = data_root / "practice-submission-capture.json"
    personal_workspace_capture = data_root / "personal-workspace-capture.json"
    project_capture = data_root / "project-workspace-capture.json"
    project_learning_capture = data_root / "project-learning-capture.json"
    learner_preferences_capture = data_root / "learner-preferences-capture.json"
    presentation_preferences_capture = data_root / "presentation-preferences-capture.json"
    assistance_preferences_capture = data_root / "assistance-preferences-capture.json"
    platform_help_capture = data_root / "platform-help-capture.json"
    port = free_loopback_port()
    origin = f"http://127.0.0.1:{port}"
    primary_error: BaseException | None = None
    recovery_report: dict[str, Any] = {
        "qualified": False,
        "reason": "external database lifecycle is not runner-owned",
    }

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
        environment["FINANCIAL_AI_ACADEMY_PERSONAL_WORKSPACE_CAPTURE"] = str(
            personal_workspace_capture
        )
        environment["FINANCIAL_AI_ACADEMY_PROJECT_CAPTURE"] = str(
            project_capture
        )
        environment["FINANCIAL_AI_ACADEMY_PROJECT_LEARNING_CAPTURE"] = str(
            project_learning_capture
        )
        environment["FINANCIAL_AI_ACADEMY_LEARNER_PREFERENCES_CAPTURE"] = str(
            learner_preferences_capture
        )
        environment["FINANCIAL_AI_ACADEMY_PRESENTATION_PREFERENCES_CAPTURE"] = str(
            presentation_preferences_capture
        )
        environment["FINANCIAL_AI_ACADEMY_ASSISTANCE_PREFERENCES_CAPTURE"] = str(
            assistance_preferences_capture
        )
        environment["FINANCIAL_AI_ACADEMY_PLATFORM_HELP_CAPTURE"] = str(
            platform_help_capture
        )
        run_checked(
            npm_e2e_command(
                "approved-lesson.e2e.ts",
                "curriculum-graph.e2e.ts",
                "practice-activity.e2e.ts",
            ),
            env=environment,
        )
        platform_help_source_before = application_database_fingerprint(
            postgres_dsn,
            exclude_schemas=frozenset({"identity"}),
        )
        run_checked(
            npm_e2e_command("platform-help.e2e.ts"),
            env=environment,
        )
        platform_help = load_platform_help_capture(
            platform_help_capture,
            data_root=data_root,
        )
        platform_help_before_restart = observe_headless_platform_help(
            origin=origin,
            capture=platform_help,
        )
        platform_help_source_after = application_database_fingerprint(
            postgres_dsn,
            exclude_schemas=frozenset({"identity"}),
        )
        if platform_help_source_after != platform_help_source_before:
            changed_schemas = sorted(
                schema
                for schema in set(platform_help_source_before)
                | set(platform_help_source_after)
                if platform_help_source_before.get(schema)
                != platform_help_source_after.get(schema)
            )
            raise RuntimeError(
                "Platform Help changed durable application state in schema(s): "
                + ", ".join(changed_schemas)
                + "."
            )
        project_learning_before = project_storage_snapshot(
            postgres_dsn,
            project_id="project-qualification-not-created",
        )
        run_checked(
            npm_e2e_command("project-workspace.e2e.ts"),
            env=environment,
        )
        project_workspace_capture = load_project_workspace_capture(
            project_capture,
            data_root=data_root,
        )
        project_id = project_workspace_capture["project"]["project_id"]
        project_storage_before_restart = project_storage_snapshot(
            postgres_dsn,
            project_id=project_id,
        )
        assert_project_storage(project_storage_before_restart)
        assert_project_learning_state_unchanged(
            before_storage=project_learning_before,
            after_storage=project_storage_before_restart,
        )
        project_before_restart = observe_headless_project_workspace(
            origin=origin,
            capture=project_workspace_capture,
        )
        project_storage_after_headless_read = project_storage_snapshot(
            postgres_dsn,
            project_id=project_id,
        )
        if project_storage_after_headless_read != project_storage_before_restart:
            raise RuntimeError("Headless Project reads changed durable state.")

        personal_storage_before = personal_workspace_storage_snapshot(postgres_dsn)
        if personal_storage_before["personal_workspaces"] != 0 or personal_storage_before[
            "personal_mutations"
        ] != 0:
            raise RuntimeError("Personal workspace qualification did not start empty.")
        run_checked(
            npm_e2e_command("personal-workspace.e2e.ts"),
            env=environment,
        )
        personal_capture = load_personal_workspace_capture(
            personal_workspace_capture,
            data_root=data_root,
            project_capture=project_workspace_capture,
        )
        personal_storage_before_restart = personal_workspace_storage_snapshot(
            postgres_dsn
        )
        assert_personal_workspace_storage(
            personal_storage_before_restart,
            capture=personal_capture,
        )
        assert_personal_workspace_target_state_unchanged(
            before_storage=personal_storage_before,
            after_storage=personal_storage_before_restart,
        )
        personal_before_restart = observe_headless_personal_workspace(
            origin=origin,
            capture=personal_capture,
        )
        personal_storage_after_headless = personal_workspace_storage_snapshot(
            postgres_dsn
        )
        if personal_storage_after_headless != personal_storage_before_restart:
            raise RuntimeError(
                "Headless Personal workspace replay or denial changed durable state."
            )
        if (
            project_storage_snapshot(postgres_dsn, project_id=project_id)
            != project_storage_before_restart
        ):
            raise RuntimeError(
                "Saved Learning changed Project or learning evidence state."
            )

        preference_system_before_learner = preference_family_storage_snapshot(
            postgres_dsn
        )
        learner_source_before = learner_preference_source_fingerprint(postgres_dsn)
        empty_preference_storage = learner_preference_storage_snapshot(postgres_dsn)
        if any(empty_preference_storage.values()):
            raise RuntimeError("Learner preference qualification did not start empty.")
        run_checked(
            npm_e2e_command("learner-preferences.e2e.ts"),
            env=environment,
        )
        learner_capture = load_learner_preference_capture(
            learner_preferences_capture,
            data_root=data_root,
        )
        learner_storage_after_browser = learner_preference_storage_snapshot(
            postgres_dsn
        )
        assert_learner_preference_storage(
            learner_storage_after_browser,
            profile=learner_capture["profile"],
            history=learner_capture["history"],
        )
        learner_browser_headless = observe_headless_learner_preferences(
            origin=origin,
            expected_profile=learner_capture["profile"],
            expected_history=learner_capture["history"],
            expected_export=learner_capture["export"],
            exact_replay_request=learner_capture["exact_replay_request"],
            exact_replay_response=learner_capture["exact_replay_response"],
        )
        if (
            learner_preference_storage_snapshot(postgres_dsn)
            != learner_storage_after_browser
        ):
            raise RuntimeError(
                "Headless learner preference reads or replay changed durable state."
            )
        learner_race_result = qualify_learner_preference_races(
            origin=origin,
            postgres_dsn=postgres_dsn,
            capture=learner_capture,
        )
        if learner_preference_source_fingerprint(postgres_dsn) != learner_source_before:
            raise RuntimeError(
                "Learner preferences changed unrelated application state."
            )
        preference_system_after_learner = preference_family_storage_snapshot(
            postgres_dsn
        )
        assert_preference_family_isolation(
            preference_system_before_learner,
            preference_system_after_learner,
            changed_family="learner",
        )

        presentation_source_before = presentation_preference_source_fingerprint(
            postgres_dsn
        )
        empty_presentation_storage = presentation_preference_storage_snapshot(
            postgres_dsn
        )
        if any(empty_presentation_storage.values()):
            raise RuntimeError(
                "Presentation preference qualification did not start empty."
            )
        run_checked(
            npm_e2e_command("presentation-preferences.e2e.ts"),
            env=environment,
        )
        presentation_capture = load_presentation_preference_capture(
            presentation_preferences_capture,
            data_root=data_root,
        )
        presentation_storage_after_browser = (
            presentation_preference_storage_snapshot(postgres_dsn)
        )
        assert_presentation_preference_storage(
            presentation_storage_after_browser,
            profile=presentation_capture["profile"],
            history=presentation_capture["history"],
            exact_replay_request=presentation_capture["exact_replay_request"],
            exact_replay_response=presentation_capture["exact_replay_response"],
        )
        observe_headless_presentation_preferences(
            origin=origin,
            expected_profile=presentation_capture["profile"],
            expected_history=presentation_capture["history"],
            expected_export=presentation_capture["export"],
            exact_replay_request=presentation_capture["exact_replay_request"],
            exact_replay_response=presentation_capture["exact_replay_response"],
        )
        if (
            presentation_preference_storage_snapshot(postgres_dsn)
            != presentation_storage_after_browser
        ):
            raise RuntimeError(
                "Headless presentation reads or replay changed durable state."
            )
        presentation_race_result = qualify_presentation_preference_races(
            origin=origin,
            postgres_dsn=postgres_dsn,
            capture=presentation_capture,
        )
        if (
            presentation_preference_source_fingerprint(postgres_dsn)
            != presentation_source_before
        ):
            raise RuntimeError(
                "Presentation preferences changed unrelated application state."
            )
        preference_system_after_presentation = preference_family_storage_snapshot(
            postgres_dsn
        )
        assert_preference_family_isolation(
            preference_system_after_learner,
            preference_system_after_presentation,
            changed_family="presentation",
        )

        assistance_source_before = assistance_preference_source_fingerprint(
            postgres_dsn
        )
        empty_assistance_storage = assistance_preference_storage_snapshot(postgres_dsn)
        if any(empty_assistance_storage.values()):
            raise RuntimeError(
                "Assistance preference qualification did not start empty."
            )
        run_checked(
            npm_e2e_command("assistance-preferences.e2e.ts"),
            env=environment,
        )
        assistance_capture = load_assistance_preference_capture(
            assistance_preferences_capture,
            data_root=data_root,
        )
        assistance_storage_after_browser = assistance_preference_storage_snapshot(
            postgres_dsn
        )
        assert_assistance_preference_storage(
            assistance_storage_after_browser,
            profile=assistance_capture["profile"],
            history=assistance_capture["history"],
            exact_replay_request=assistance_capture["exact_replay_request"],
            exact_replay_response=assistance_capture["exact_replay_response"],
        )
        observe_headless_assistance_preferences(
            origin=origin,
            expected_profile=assistance_capture["profile"],
            expected_history=assistance_capture["history"],
            expected_export=assistance_capture["export"],
            exact_replay_request=assistance_capture["exact_replay_request"],
            exact_replay_response=assistance_capture["exact_replay_response"],
        )
        if (
            assistance_preference_storage_snapshot(postgres_dsn)
            != assistance_storage_after_browser
        ):
            raise RuntimeError(
                "Headless assistance reads or replay changed durable state."
            )
        assistance_race_result = qualify_assistance_preference_races(
            origin=origin,
            postgres_dsn=postgres_dsn,
            capture=assistance_capture,
        )
        if (
            assistance_preference_source_fingerprint(postgres_dsn)
            != assistance_source_before
        ):
            raise RuntimeError(
                "Assistance preferences changed unrelated application state."
            )
        preference_system_before_restart = preference_family_storage_snapshot(
            postgres_dsn
        )
        assert_preference_family_isolation(
            preference_system_after_presentation,
            preference_system_before_restart,
            changed_family="assistance",
        )

        (
            practice_draft_save,
            _browser_practice_draft,
            practice_submission,
            practice_result,
            browser_practice_progress,
        ) = load_practice_submission_capture(
            practice_capture,
            data_root=data_root,
            expected_practice=practice_before_restart,
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
        run_checked(
            npm_e2e_command("project-learning-submission.e2e.ts"),
            env=environment,
        )
        project_learning = load_project_learning_capture(
            project_learning_capture,
            data_root=data_root,
        )
        learning_project_id = project_learning["project"]["project_id"]
        project_learning_storage_before_restart = (
            project_learning_storage_snapshot(
                postgres_dsn,
                project_id=learning_project_id,
            )
        )
        assert_project_learning_storage(
            project_learning_storage_before_restart,
            capture=project_learning,
        )
        project_learning_before_restart = observe_headless_project_learning(
            origin=origin,
            capture=project_learning,
        )
        project_learning_storage_after_headless = (
            project_learning_storage_snapshot(
                postgres_dsn,
                project_id=learning_project_id,
            )
        )
        if (
            project_learning_storage_after_headless
            != project_learning_storage_before_restart
        ):
            raise RuntimeError(
                "Headless Project learning replay changed durable evidence."
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
        platform_help_storage_before_restart_observation = (
            application_database_fingerprint(
                postgres_dsn,
                exclude_schemas=frozenset({"identity"}),
            )
        )
        platform_help_after_restart = observe_headless_platform_help(
            origin=origin,
            capture=platform_help,
        )
        assert_platform_help_restart_result(
            before_restart=platform_help_before_restart,
            after_restart=platform_help_after_restart,
        )
        if (
            application_database_fingerprint(
                postgres_dsn,
                exclude_schemas=frozenset({"identity"}),
            )
            != platform_help_storage_before_restart_observation
        ):
            raise RuntimeError("Platform Help restart read changed durable state.")
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
        project_after_restart = observe_headless_project_workspace(
            origin=origin,
            capture=project_workspace_capture,
        )
        project_storage_after_restart = project_storage_snapshot(
            postgres_dsn,
            project_id=project_id,
        )
        assert_project_restart_result(
            before_observation=project_before_restart,
            after_observation=project_after_restart,
            before_storage=project_storage_before_restart,
            after_storage=project_storage_after_restart,
        )
        project_learning_after_restart = observe_headless_project_learning(
            origin=origin,
            capture=project_learning,
        )
        project_learning_storage_after_restart = (
            project_learning_storage_snapshot(
                postgres_dsn,
                project_id=learning_project_id,
            )
        )
        assert_project_learning_storage(
            project_learning_storage_after_restart,
            capture=project_learning,
        )
        assert_project_learning_restart_result(
            before_observation=project_learning_before_restart,
            after_observation=project_learning_after_restart,
            before_storage=project_learning_storage_before_restart,
            after_storage=project_learning_storage_after_restart,
        )
        personal_storage_before_restart_observation = (
            personal_workspace_storage_snapshot(postgres_dsn)
        )
        personal_after_restart = observe_headless_personal_workspace(
            origin=origin,
            capture=personal_capture,
        )
        personal_storage_after_restart = personal_workspace_storage_snapshot(
            postgres_dsn
        )
        assert_personal_workspace_restart_result(
            before_observation=personal_before_restart,
            after_observation=personal_after_restart,
            before_storage=personal_storage_before_restart,
            after_storage=personal_storage_after_restart,
            capture=personal_capture,
        )
        assert_personal_workspace_target_state_unchanged(
            before_storage=personal_storage_before_restart_observation,
            after_storage=personal_storage_after_restart,
        )
        learner_after_restart = observe_headless_learner_preferences(
            origin=origin,
            expected_profile=learner_race_result["profile"],
            expected_history=learner_race_result["history"],
            expected_export=learner_race_result["export"],
            exact_replay_request=learner_capture["exact_replay_request"],
            exact_replay_response=learner_capture["exact_replay_response"],
        )
        learner_storage_after_restart = learner_preference_storage_snapshot(
            postgres_dsn
        )
        assert_learner_preference_storage(
            learner_storage_after_restart,
            profile=learner_after_restart["profile"],
            history=learner_after_restart["history"],
        )
        if learner_storage_after_restart != learner_race_result["storage"]:
            raise RuntimeError(
                "Learner preference storage changed after normal restart."
            )
        presentation_after_restart = observe_headless_presentation_preferences(
            origin=origin,
            expected_profile=presentation_race_result["profile"],
            expected_history=presentation_race_result["history"],
            expected_export=presentation_race_result["export"],
            exact_replay_request=presentation_capture["exact_replay_request"],
            exact_replay_response=presentation_capture["exact_replay_response"],
        )
        presentation_storage_after_restart = (
            presentation_preference_storage_snapshot(postgres_dsn)
        )
        assert_presentation_preference_storage(
            presentation_storage_after_restart,
            profile=presentation_after_restart["profile"],
            history=presentation_after_restart["history"],
            exact_replay_request=presentation_capture["exact_replay_request"],
            exact_replay_response=presentation_capture["exact_replay_response"],
        )
        if presentation_storage_after_restart != presentation_race_result["storage"]:
            raise RuntimeError(
                "Presentation preference storage changed after normal restart."
            )
        assistance_after_restart = observe_headless_assistance_preferences(
            origin=origin,
            expected_profile=assistance_race_result["profile"],
            expected_history=assistance_race_result["history"],
            expected_export=assistance_race_result["export"],
            exact_replay_request=assistance_capture["exact_replay_request"],
            exact_replay_response=assistance_capture["exact_replay_response"],
        )
        assistance_storage_after_restart = assistance_preference_storage_snapshot(
            postgres_dsn
        )
        assert_assistance_preference_storage(
            assistance_storage_after_restart,
            profile=assistance_after_restart["profile"],
            history=assistance_after_restart["history"],
            exact_replay_request=assistance_capture["exact_replay_request"],
            exact_replay_response=assistance_capture["exact_replay_response"],
        )
        if assistance_storage_after_restart != assistance_race_result["storage"]:
            raise RuntimeError(
                "Assistance preference storage changed after normal restart."
            )
        preference_system_after_restart = preference_family_storage_snapshot(
            postgres_dsn
        )
        if preference_system_after_restart != preference_system_before_restart:
            raise RuntimeError(
                "Preference-family storage changed during restart or headless reads."
            )
        preference_system_report = stable_preference_system_report(
            preference_system_after_restart
        )

        if container_name is not None:
            restored_credential_opener = open_personal_workspace_session(
                origin=origin,
                expected_workspace=personal_capture["workspace"],
            )
            recovery_phases: list[str] = []
            stop_application(application)
            application = None
            recovery_phases.append("source_stopped")
            source_application_data = data_root / "application-data"
            recovered_application_data = data_root / "recovery-target-data"
            logical_backup = data_root / "recovery-source.dump"
            source_database_before = application_database_fingerprint(postgres_dsn)
            source_non_identity_before = application_database_fingerprint(
                postgres_dsn,
                exclude_schemas=frozenset({"identity"}),
            )
            source_storage_before_recovery = personal_workspace_storage_snapshot(
                postgres_dsn
            )
            source_files_before = bounded_file_tree_fingerprint(
                source_application_data
            )
            recovery_phases.append("source_fingerprinted")
            backup_evidence = create_logical_backup(container_name, logical_backup)
            recovery_phases.append("backup_created")
            copied_files = copy_bounded_data_root(
                source_application_data,
                recovered_application_data,
            )
            recovery_phases.append("data_copied")
            if (
                application_database_fingerprint(postgres_dsn)
                != source_database_before
                or personal_workspace_storage_snapshot(postgres_dsn)
                != source_storage_before_recovery
                or bounded_file_tree_fingerprint(source_application_data)
                != source_files_before
            ):
                raise RuntimeError("Recovery capture changed the stopped source.")
            recovery_phases.append("source_unchanged_after_capture")

            recovery_container_name, recovery_dsn = start_postgres(
                prefix=RECOVERY_CONTAINER_PREFIX
            )
            assert_populated_target_refusal(
                container_name=recovery_container_name,
                postgres_dsn=recovery_dsn,
                source=logical_backup,
                owned_root=data_root,
            )
            recovery_phases.append("populated_target_refused")
            restore_logical_backup(
                container_name=recovery_container_name,
                postgres_dsn=recovery_dsn,
                source=logical_backup,
                owned_root=data_root,
            )
            recovery_phases.append("empty_target_restored")
            if application_database_fingerprint(recovery_dsn) != source_database_before:
                raise RuntimeError("Recovered database changed accepted source state.")
            recovery_phases.append("catalog_and_data_matched")
            revoked_sessions = revoke_restored_sessions(recovery_dsn)
            recovery_phases.append("restored_sessions_revoked")
            if (
                application_database_fingerprint(
                    recovery_dsn,
                    exclude_schemas=frozenset({"identity"}),
                )
                != source_non_identity_before
            ):
                raise RuntimeError(
                    "Recovery session revocation changed non-identity state."
                )

            application = start_application(
                postgres_dsn=recovery_dsn,
                data_root=recovered_application_data,
                port=port,
                application_log=data_root / "recovery-application.log",
                seed_fixture=False,
            )
            assert_restored_session_denied(
                opener=restored_credential_opener,
                origin=origin,
            )
            recovery_phases.append("old_session_denied")
            restored_personal = observe_headless_personal_workspace(
                origin=origin,
                capture=personal_capture,
            )
            recovery_phases.append("fresh_session_verified")
            restored_storage = personal_workspace_storage_snapshot(recovery_dsn)
            assert_personal_workspace_restart_result(
                before_observation=personal_before_restart,
                after_observation=restored_personal,
                before_storage=personal_storage_before_restart,
                after_storage=restored_storage,
                capture=personal_capture,
            )
            assert_personal_workspace_target_state_unchanged(
                before_storage=source_storage_before_recovery,
                after_storage=restored_storage,
            )
            if (
                application_database_fingerprint(
                    recovery_dsn,
                    exclude_schemas=frozenset({"identity"}),
                )
                != source_non_identity_before
                or application_database_fingerprint(postgres_dsn)
                != source_database_before
                or personal_workspace_storage_snapshot(postgres_dsn)
                != source_storage_before_recovery
                or bounded_file_tree_fingerprint(source_application_data)
                != source_files_before
                or bounded_file_tree_fingerprint(recovered_application_data)
                != copied_files
            ):
                raise RuntimeError(
                    "Recovered public use changed source, target, or copied data state."
                )
            recovery_phases.append("source_and_target_unchanged")
            recovery_report = stable_recovery_report({
                "backup_byte_count": backup_evidence["byte_count"],
                "backup_sha256": backup_evidence["sha256"],
                "database_catalog_and_data_sha256": database_fingerprint_digest(
                    source_database_before
                ),
                "database_schema_count": len(source_database_before),
                "data_file_count": copied_files["file_count"],
                "data_sha256": copied_files["sha256"],
                "empty_target_restored": True,
                "fresh_session_public_api": True,
                "old_session_denied": True,
                "phases": recovery_phases,
                "populated_target_refused": True,
                "qualified": True,
                "restored_sessions_revoked": revoked_sessions,
                "source_unchanged": True,
            })

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
            "personal_workspace": {
                "browser_headless_query_parity": True,
                "browser_headless_export_parity": True,
                "browser_generated_client": True,
                "canonical_query_digest": True,
                "collection_order_preserved": True,
                "confidential_conflicts": True,
                "exact_headless_replay": True,
                "exact_refresh_replay": True,
                "headless_public_api": True,
                "inert_artifact_bytes_excluded": True,
                "mixed_curriculum_and_project_references": True,
                "normal_restart_without_reseeding": True,
                "project_state_unchanged": True,
                "project_workspace_snapshot_artifact_references": True,
                "public_api_shared": True,
                "record_only_refresh": True,
                "source_and_learning_state_unchanged": True,
                "unavailable_project_isolated": True,
                "unicode_evidence_preserved": True,
                "workspace_id": personal_capture["workspace"]["workspace_id"],
            },
            "personal_workspace_recovery": recovery_report,
            "preference_system": preference_system_report,
            "learner_preferences": {
                "browser_generated_client": True,
                "browser_headless_export_parity": True,
                "browser_headless_profile_history_parity": True,
                "complete_learner_control_journey": True,
                "confidential_race_denials": True,
                "different_key_same_revision_race": True,
                "exact_headless_replay": True,
                "normal_restart_without_reseeding": True,
                "profile_id": learner_race_result["profile"]["profile_id"],
                "public_api_shared": True,
                "same_key_changed_payload_race": True,
                "same_key_same_payload_race": True,
                "source_state_unchanged": True,
            },
            "presentation_preferences": {
                "all_sixteen_profiles": True,
                "browser_generated_client": True,
                "browser_headless_export_parity": True,
                "browser_headless_profile_history_parity": True,
                "confidential_race_denials": True,
                "different_key_same_revision_race": True,
                "exact_headless_replay": True,
                "local_theme_excluded": True,
                "normal_restart_without_reseeding": True,
                "profile_id": presentation_race_result["profile"]["profile_id"],
                "protective_browser_precedence": True,
                "public_api_shared": True,
                "same_key_changed_payload_race": True,
                "same_key_same_payload_race": True,
                "source_state_unchanged": True,
            },
            "assistance_preferences": {
                "browser_generated_client": True,
                "browser_headless_export_parity": True,
                "browser_headless_profile_history_parity": True,
                "confidential_race_denials": True,
                "different_key_same_revision_race": True,
                "exact_headless_replay": True,
                "local_reminder_excluded_from_api": True,
                "local_reminder_reload_only": True,
                "no_model_or_notification_execution": True,
                "normal_restart_without_reseeding": True,
                "profile_id": assistance_race_result["profile"]["profile_id"],
                "public_api_shared": True,
                "same_key_changed_payload_race": True,
                "same_key_same_payload_race": True,
                "source_state_unchanged": True,
            },
            "platform_help": {
                "authorization_confidential": True,
                "browser_generated_client": True,
                "browser_headless_parity": True,
                "checked_in_corpus_available": True,
                "context_digests": {
                    context_key: platform_help["contexts"][context_key][
                        "context_digest"
                    ]
                    for context_key in CONTEXTUAL_HELP_KEYS
                },
                "contextual_feature_contexts": list(CONTEXTUAL_HELP_KEYS),
                "contextual_safe_returns": True,
                "corpus_digest": platform_help["first_page"]["corpus_digest"],
                "exact_relation_navigation": True,
                "exact_version_reads": True,
                "no_non_loopback_browser_requests": True,
                "normal_restart_without_reseeding": True,
                "public_api_shared": True,
                "read_only_state_containment": True,
                "source_fingerprints_preserved": True,
                "stable_search_filter_and_cursor": True,
            },
            "project_workspace": {
                "artifact_download_exact": True,
                "browser_generated_client": True,
                "evidence_export_exact": True,
                "headless_public_api": True,
                "learning_state_unchanged": True,
                "normal_restart_without_reseeding": True,
                "persistent_assessment_and_learner_model_state_unchanged": True,
                "project_id": project_id,
                "snapshot_immutable_after_later_work": True,
                "unicode_evidence_preserved": True,
            },
            "project_learning_submission": {
                "assessment_evidence_occurrences": 2,
                "audit_references": 2,
                "browser_generated_client": True,
                "bounded_correction": True,
                "exact_headless_replay": True,
                "headless_public_api": True,
                "independent_project_denied": True,
                "learner_model_history_entries": 2,
                "normal_restart_without_reseeding": True,
                "project_id": learning_project_id,
                "retained_supersession": True,
                "snapshot_evidence_immutable": True,
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
        recovery_container_name=recovery_container_name,
        data_root=data_root,
    )
    finish_after_cleanup(primary_error, cleanup_failures)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
