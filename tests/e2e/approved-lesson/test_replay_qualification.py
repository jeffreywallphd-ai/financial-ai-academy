from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest


RUNNER_PATH = Path(__file__).with_name("run.py")
SPEC = importlib.util.spec_from_file_location(
    "approved_lesson_qualification_runner",
    RUNNER_PATH,
)
assert SPEC is not None and SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


def graph() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "curriculum_id": runner.CURRICULUM_ID,
        "curriculum_version": runner.CURRICULUM_VERSION,
        "graph_digest": "a" * 64,
        "activities": [
            {
                "activity_id": runner.LESSON_ACTIVITY_ID,
                "reference": {
                    "reference_kind": "lesson_placement",
                    "placement_id": "intro-risk-return-primary",
                    "package_id": "intro-risk-return",
                    "package_version": "1.1.0",
                    "package_digest": "b" * 64,
                },
            }
        ],
    }


def navigation(
    *,
    evaluated_at: str = "2026-10-16T12:00:00Z",
    projection_digest: str = "c" * 64,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "curriculum_id": runner.CURRICULUM_ID,
        "curriculum_version": runner.CURRICULUM_VERSION,
        "graph_digest": "a" * 64,
        "policy_id": "deterministic-prerequisite-baseline",
        "policy_version": "1.0.0",
        "evaluated_at": evaluated_at,
        "source_set_digest": "d" * 64,
        "projection_digest": projection_digest,
        "activity_states": [
            {
                "activity_id": runner.LESSON_ACTIVITY_ID,
                "completion": "completed",
                "eligibility": "eligible",
                "requirement": "required",
                "availability": "available",
                "reasons": [
                    {
                        "code": "activity_completed",
                        "explanation": "This activity is recorded as finished.",
                        "references": [runner.LESSON_ACTIVITY_ID],
                    },
                    {
                        "code": "required_activity",
                        "explanation": "This activity is part of the required path.",
                        "references": [runner.LESSON_ACTIVITY_ID],
                    },
                ],
            }
        ],
    }


def launch() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "curriculum_id": runner.CURRICULUM_ID,
        "curriculum_version": runner.CURRICULUM_VERSION,
        "graph_digest": "a" * 64,
        "activity_id": runner.LESSON_ACTIVITY_ID,
        "navigation_projection_digest": "e" * 64,
        "evaluated_at": "2026-10-16T12:00:01Z",
        "placement_id": "intro-risk-return-primary",
        "package_id": "intro-risk-return",
        "package_version": "1.1.0",
        "package_digest": "b" * 64,
        "destination": "/learn/placements/intro-risk-return-primary",
    }


def observation(
    *,
    evaluated_at: str = "2026-10-16T12:00:00Z",
    projection_digest: str = "c" * 64,
) -> dict[str, Any]:
    return runner.headless_observation_semantics(
        graph=graph(),
        navigation=navigation(
            evaluated_at=evaluated_at,
            projection_digest=projection_digest,
        ),
        launch=launch(),
    )


def test_restart_command_reuses_state_without_reseeding() -> None:
    seeded = runner.application_command(
        postgres_dsn="postgresql://isolated",
        data_root=Path("isolated-data"),
        port=8123,
        seed_fixture=True,
    )
    restarted = runner.application_command(
        postgres_dsn="postgresql://isolated",
        data_root=Path("isolated-data"),
        port=8123,
        seed_fixture=False,
    )

    assert "--seed-approved-fixture" in seeded
    assert "--seed-discovery-query-fixtures" in seeded
    assert "--seed-approved-fixture" not in restarted
    assert "--seed-discovery-query-fixtures" not in restarted
    assert seeded[seeded.index("--data-root") + 1] == restarted[
        restarted.index("--data-root") + 1
    ]


def test_stable_semantics_ignore_observation_time_and_derived_digest() -> None:
    first = observation()
    replayed = observation(
        evaluated_at="2026-10-16T12:05:00Z",
        projection_digest="f" * 64,
    )

    assert first == replayed


def test_headless_observation_rejects_graph_owned_launch_drift() -> None:
    changed = launch()
    changed["destination"] = "/learn/placements/unrelated"

    with pytest.raises(
        RuntimeError,
        match="launch does not match graph-owned facts",
    ):
        runner.headless_observation_semantics(
            graph=graph(),
            navigation=navigation(),
            launch=changed,
        )


def test_headless_client_uses_only_public_session_and_learning_apis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []
    documents = {
        "/api/v1/session/single-profile": {"expires_at": "later"},
        (
            "/api/v1/curriculum/graphs/investing-foundations"
            "/versions/1.0.0"
        ): graph(),
        (
            "/api/v1/adaptation/curricula/investing-foundations"
            "/versions/1.0.0/navigation-state"
        ): navigation(),
        (
            "/api/v1/adaptation/curricula/investing-foundations"
            "/versions/1.0.0/activities/activity-risk-return-lesson/launch"
        ): launch(),
    }

    def request_json(
        _opener: object,
        *,
        origin: str,
        path: str,
        method: str = "GET",
        payload: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        assert origin == "http://127.0.0.1:8123"
        calls.append((method, path, payload))
        return documents[path]

    monkeypatch.setattr(runner, "_request_json", request_json)
    result = runner.observe_headless_navigation("http://127.0.0.1:8123")

    assert result == observation()
    assert calls == [
        (
            "POST",
            "/api/v1/session/single-profile",
            {"limitation_acknowledged": True},
        ),
        (
            "GET",
            (
                "/api/v1/curriculum/graphs/investing-foundations"
                "/versions/1.0.0"
            ),
            None,
        ),
        (
            "GET",
            (
                "/api/v1/adaptation/curricula/investing-foundations"
                "/versions/1.0.0/navigation-state"
            ),
            None,
        ),
        (
            "GET",
            (
                "/api/v1/adaptation/curricula/investing-foundations"
                "/versions/1.0.0/activities/"
                "activity-risk-return-lesson/launch"
            ),
            None,
        ),
    ]


class _RowResult:
    def __init__(self, row: tuple[int, int, int, int]) -> None:
        self._row = row

    def fetchone(self) -> tuple[int, int, int, int]:
        return self._row


class _FakeConnection:
    def __init__(
        self,
        rows: list[tuple[int, int, int, int]],
    ) -> None:
        self._rows = iter(rows)
        self.statements: list[str] = []

    def __enter__(self) -> _FakeConnection:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, statement: str) -> _RowResult:
        normalized = " ".join(statement.split())
        self.statements.append(normalized)
        if normalized.startswith("SELECT"):
            return _RowResult(next(self._rows))
        return _RowResult((0, 0, 0, 0))


def test_reset_deletes_only_rebuildable_learner_model_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection = _FakeConnection([(1, 1, 3, 1), (1, 1, 0, 0)])
    monkeypatch.setattr(
        runner.psycopg,
        "connect",
        lambda _dsn: connection,
    )

    before, after = runner.reset_rebuildable_completion_state(
        "postgresql://isolated"
    )

    assert before == {
        "assessment_evidence": 1,
        "assessment_events": 1,
        "learner_projections": 3,
        "learner_history": 1,
    }
    assert after == {
        "assessment_evidence": 1,
        "assessment_events": 1,
        "learner_projections": 0,
        "learner_history": 0,
    }
    assert connection.statements[1:3] == list(
        runner.REBUILDABLE_COMPLETION_RESET
    )
    assert all(
        "assessment." not in statement
        and "curriculum." not in statement
        for statement in connection.statements[1:3]
    )


def test_replay_accepts_rebuilt_subset_but_preserves_source_and_semantics() -> None:
    runner.assert_replay_result(
        before_observation=observation(),
        after_observation=observation(
            evaluated_at="2026-10-16T12:05:00Z",
            projection_digest="f" * 64,
        ),
        before_reset={
            "assessment_evidence": 1,
            "assessment_events": 1,
            "learner_projections": 3,
            "learner_history": 1,
        },
        after_reset={
            "assessment_evidence": 1,
            "assessment_events": 1,
            "learner_projections": 0,
            "learner_history": 0,
        },
        after_rebuild={
            "assessment_evidence": 1,
            "assessment_events": 1,
            "learner_projections": 2,
            "learner_history": 1,
        },
    )


def test_replay_rejects_source_mutation() -> None:
    with pytest.raises(RuntimeError, match="Assessment evidence changed"):
        runner.assert_replay_result(
            before_observation=observation(),
            after_observation=observation(),
            before_reset={
                "assessment_evidence": 1,
                "assessment_events": 1,
                "learner_projections": 3,
                "learner_history": 1,
            },
            after_reset={
                "assessment_evidence": 1,
                "assessment_events": 1,
                "learner_projections": 0,
                "learner_history": 0,
            },
            after_rebuild={
                "assessment_evidence": 2,
                "assessment_events": 2,
                "learner_projections": 2,
                "learner_history": 1,
            },
        )


class _FakeProcess:
    def __init__(self, *, times_out: bool) -> None:
        self.times_out = times_out
        self.terminated = False
        self.killed = False
        self.waits: list[int] = []

    def poll(self) -> None:
        return None

    def terminate(self) -> None:
        self.terminated = True

    def wait(self, *, timeout: int) -> None:
        self.waits.append(timeout)
        if self.times_out and len(self.waits) == 1:
            raise runner.subprocess.TimeoutExpired("qualification", timeout)

    def kill(self) -> None:
        self.killed = True


def test_stop_application_bounds_graceful_and_forced_cleanup() -> None:
    graceful = _FakeProcess(times_out=False)
    forced = _FakeProcess(times_out=True)

    runner.stop_application(graceful)
    runner.stop_application(forced)

    assert graceful.terminated is True
    assert graceful.killed is False
    assert graceful.waits == [10]
    assert forced.terminated is True
    assert forced.killed is True
    assert forced.waits == [10, 5]


def test_start_application_stops_a_process_that_never_becomes_ready(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    process = _FakeProcess(times_out=False)
    monkeypatch.setattr(
        runner.subprocess,
        "Popen",
        lambda *_args, **_kwargs: process,
    )

    def fail_readiness(_url: str, _process: object) -> None:
        raise RuntimeError("bounded readiness failure")

    monkeypatch.setattr(runner, "wait_for_http", fail_readiness)

    with pytest.raises(RuntimeError, match="bounded readiness failure"):
        runner.start_application(
            postgres_dsn="postgresql://isolated",
            data_root=tmp_path / "application-data",
            port=8123,
            application_log=tmp_path / "application.log",
            seed_fixture=False,
        )

    assert process.terminated is True
    assert process.killed is False
    assert process.waits == [10]
