from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
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


def practice() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "placement_id": runner.PRACTICE_PLACEMENT_ID,
        "package_id": "intro-risk-return",
        "package_version": "2.0.0",
        "package_digest": "a" * 64,
        "practice_id": "risk-return-practice",
        "practice_version": "1.0.0",
        "definition_digest": "b" * 64,
        "title": "Practice risk and return basics",
        "purpose": "Review three educational examples.",
        "instructions": "Answer every item.",
        "attempt_policy": {
            "policy_id": "formative-retry",
            "policy_version": "1.0.0",
            "max_attempts": 3,
            "resume_allowed": True,
            "history_visible": True,
        },
        "source_references": [],
        "review_references": [],
        "items": [
            {"item_id": "one", "item_type": "single_select"},
            {"item_id": "many", "item_type": "multiple_select"},
            {"item_id": "number", "item_type": "numeric_entry"},
        ],
    }


def practice_submission() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "submission_id": "22222222-2222-4222-8222-222222222222",
        "placement_id": runner.PRACTICE_PLACEMENT_ID,
        "package_id": "intro-risk-return",
        "package_version": "2.0.0",
        "package_digest": "a" * 64,
        "definition_digest": "b" * 64,
        "practice_id": "risk-return-practice",
        "practice_version": "1.0.0",
        "attempt_policy_id": "formative-retry",
        "attempt_policy_version": "1.0.0",
        "responses": [
            {
                "item_id": "one",
                "item_version": "1.0.0",
                "item_type": "single_select",
                "scoring_policy_id": "single-select-exact-match",
                "scoring_policy_version": "1.0.0",
                "selected_option_id": "uncertainty",
            },
            {
                "item_id": "many",
                "item_version": "1.0.0",
                "item_type": "multiple_select",
                "scoring_policy_id": "multiple-select-exact-set",
                "scoring_policy_version": "1.0.0",
                "selected_option_ids": ["more-issuers", "same-copy"],
            },
            {
                "item_id": "number",
                "item_version": "1.0.0",
                "item_type": "numeric_entry",
                "scoring_policy_id": "numeric-exact-or-inclusive-range",
                "scoring_policy_version": "1.0.0",
                "entered_value": "105.00",
            },
        ],
    }


def practice_result() -> dict[str, Any]:
    submission = practice_submission()
    return {
        "schema_version": "1.0.0",
        "attempt_id": "33333333-3333-4333-8333-333333333333",
        "evidence_id": "44444444-4444-4444-8444-444444444444",
        **{
            key: submission[key]
            for key in (
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
            )
        },
        "score": 2,
        "max_score": 3,
        "outcome": "review_needed",
        "review_reference_ids": ["risk-return-review"],
        "item_results": [
            {
                **submission["responses"][0],
                "score": 1,
                "max_score": 1,
                "correct": True,
                "feedback": {
                    "feedback_id": "risk-correct",
                    "text": "Correct.",
                    "review_reference_ids": ["risk-return-review"],
                },
            },
            {
                **submission["responses"][1],
                "score": 0,
                "max_score": 1,
                "correct": False,
                "feedback": {
                    "feedback_id": "diversification-review",
                    "text": "Review this example.",
                    "review_reference_ids": ["risk-return-review"],
                },
            },
            {
                **submission["responses"][2],
                "score": 1,
                "max_score": 1,
                "correct": True,
                "feedback": {
                    "feedback_id": "growth-correct",
                    "text": "Correct.",
                    "review_reference_ids": ["risk-return-review"],
                },
            },
        ],
        "submitted_at": "2026-10-16T16:00:00.123456Z",
    }


def practice_draft_save() -> dict[str, Any]:
    submission = practice_submission()
    return {
        key: submission[key]
        for key in (
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
        )
    } | {
        "expected_revision": 0,
        "responses": [submission["responses"][0], submission["responses"][2]],
    }


def practice_draft() -> dict[str, Any]:
    save = practice_draft_save()
    return {
        key: save[key]
        for key in runner.PRACTICE_SCOPE_KEYS
    } | {
        "responses": save["responses"],
        "revision": 1,
        "saved_at": "2026-10-16T15:59:00Z",
        "response_fingerprint": "d" * 64,
    }


def practice_progress(*, draft: dict[str, Any] | None = None) -> dict[str, Any]:
    submission = practice_submission()
    result = practice_result()
    scope = {
        key: submission[key]
        for key in runner.PRACTICE_SCOPE_KEYS
    }
    return {
        "schema_version": "1.0.0",
        "placement_id": runner.PRACTICE_PLACEMENT_ID,
        "draft": draft,
        "retry_state": {
            **scope,
            "attempts_used": 1,
            "max_attempts": 3,
            "attempts_remaining": 2,
            "can_retry": True,
            "state": "available",
        },
        "history": {
            **scope,
            "source_digest": "e" * 64,
            "attempts": [
                {
                    "attempt_order": 1,
                    "event_id": "55555555-5555-4555-8555-555555555555",
                    "attempt_id": result["attempt_id"],
                    "evidence_id": result["evidence_id"],
                    "submission_id": result["submission_id"],
                    "score": result["score"],
                    "max_score": result["max_score"],
                    "outcome": result["outcome"],
                    "item_summaries": [
                        {
                            **{
                                key: item[key]
                                for key in (
                                    runner.PRACTICE_HISTORY_ITEM_KEYS
                                    - {"review_reference_ids"}
                                )
                            },
                            "review_reference_ids": (
                                []
                                if item["correct"]
                                else item["feedback"]["review_reference_ids"]
                            ),
                        }
                        for item in result["item_results"]
                    ],
                    "completed_at": result["submitted_at"],
                }
            ],
        },
        "review_targets": [
            {
                "schema_version": "1.0.0",
                "practice_placement_id": runner.PRACTICE_PLACEMENT_ID,
                "resource_id": "risk-return-review",
                "resource_version": "1.0.0",
                "resource_digest": "c" * 64,
                "resource_title": "Review risk and return",
                "state": "available",
                "destination": {
                    "placement_id": "intro-risk-return-primary",
                    "package_id": "intro-risk-return",
                    "package_version": "1.1.0",
                    "package_digest": "f" * 64,
                },
            }
        ],
    }


def project_workspace_capture() -> dict[str, Any]:
    content = b"scenario,value\nbase,1\n"
    digest = hashlib.sha256(content).hexdigest()
    project = {
        "schema_version": "1.0.0",
        "project_id": "project-qualification",
        "learner_id": "single-profile-learner",
        "title": "Unicode evidence Project",
        "charter": "Preserve exact educational evidence.",
        "origin": {"origin_type": "independent"},
        "lifecycle": "active",
        "revision": 1,
        "created_at": "2026-10-16T16:00:00Z",
        "updated_at": "2026-10-16T16:00:00Z",
    }
    note = {
        "note_id": "note-one",
        "note_version": 1,
        "title": "Café Σίσυφος Straße İ",
        "body": "Compare the exact educational evidence.",
        "created_at": "2026-10-16T16:01:00Z",
        "updated_at": "2026-10-16T16:01:00Z",
    }
    reference = {
        "reference_id": "reference-one",
        "reference_version": 1,
        "title": "Reviewed learning source",
        "url": "https://example.com/learning/evidence",
        "source_name": "Example education publisher",
        "created_at": "2026-10-16T16:02:00Z",
        "updated_at": "2026-10-16T16:02:00Z",
    }
    artifact = {
        "artifact_id": "artifact-one",
        "artifact_version": 1,
        "artifact_kind": "dataset",
        "logical_path": "Résumé-Σ-data.csv",
        "media_type": "text/csv",
        "inspection_mode": "plain_text",
        "byte_count": len(content),
        "content_digest": digest,
        "provenance": {
            "source_type": "learner_created",
            "source_title": "Browser qualification dataset",
        },
        "assumptions": [],
        "created_at": "2026-10-16T16:03:00Z",
    }
    workspace_at_snapshot = {
        "schema_version": "1.0.0",
        "project_id": project["project_id"],
        "learner_id": project["learner_id"],
        "workspace_revision": 4,
        "notes": [note],
        "references": [reference],
        "artifacts": [artifact],
        "domain_links": [],
        "created_at": "2026-10-16T16:00:00Z",
        "updated_at": "2026-10-16T16:03:00Z",
    }
    snapshot = {
        "schema_version": "1.0.0",
        "snapshot_id": "snapshot-one",
        "snapshot_digest": "a" * 64,
        "snapshot": {
            "project_id": project["project_id"],
            "learner_id": project["learner_id"],
            "project_revision": 1,
            "project_shell_digest": "b" * 64,
            "workspace_revision": 4,
            "workspace_created_at": workspace_at_snapshot["created_at"],
            "workspace_updated_at": workspace_at_snapshot["updated_at"],
            "notes": [
                {
                    "record_id": note["note_id"],
                    "record_version": 1,
                    "record_digest": "c" * 64,
                }
            ],
            "references": [
                {
                    "record_id": reference["reference_id"],
                    "record_version": 1,
                    "record_digest": "d" * 64,
                }
            ],
            "artifacts": [
                {
                    "artifact_id": artifact["artifact_id"],
                    "artifact_version": 1,
                    "manifest_digest": "e" * 64,
                    "content_digest": digest,
                    "byte_count": len(content),
                }
            ],
            "domain_links": [],
        },
        "closed_at": "2026-10-16T16:04:00Z",
    }
    current_workspace = json.loads(json.dumps(workspace_at_snapshot))
    current_workspace["workspace_revision"] = 5
    current_workspace["updated_at"] = "2026-10-16T16:05:00Z"
    current_workspace["notes"].append(
        {
            "note_id": "note-two",
            "note_version": 1,
            "title": "Work after the checkpoint",
            "body": "The fixed checkpoint remains unchanged.",
            "created_at": "2026-10-16T16:05:00Z",
            "updated_at": "2026-10-16T16:05:00Z",
        }
    )
    export_bundle = {
        "manifest": {
            "schema_version": "1.0.0",
            "export_id": "export-one",
            "export_digest": "f" * 64,
            "generated_at": snapshot["closed_at"],
            "export": {
                "format": "project-evidence-manifest-v1",
                "project_id": project["project_id"],
                "snapshot_id": snapshot["snapshot_id"],
                "snapshot_digest": snapshot["snapshot_digest"],
                "snapshot_record": snapshot,
                "workspace_record": workspace_at_snapshot,
                "artifact_files": [
                    {
                        "artifact_id": artifact["artifact_id"],
                        "artifact_version": 1,
                        "logical_path": artifact["logical_path"],
                        "content_digest": digest,
                        "byte_count": len(content),
                    }
                ],
                "excluded_artifacts": [],
            },
        },
        "files": [
            {
                "artifact_id": artifact["artifact_id"],
                "artifact_version": 1,
                "logical_path": artifact["logical_path"],
                "content_base64": base64.b64encode(content).decode("ascii"),
            }
        ],
    }
    learning_state = {
        "navigation": navigation(),
        "practice_progress": practice_progress(),
    }
    return {
        "project": project,
        "workspace_at_snapshot": workspace_at_snapshot,
        "current_workspace": current_workspace,
        "snapshot": snapshot,
        "export_bundle": export_bundle,
        "artifact_sha256": digest,
        "learning_state_before": learning_state,
        "learning_state_after": json.loads(json.dumps(learning_state)),
    }


def project_learning_capture() -> dict[str, Any]:
    project_id = "project-learning-qualification"
    origin = {
        "package_id": "package-project-learning",
        "package_version": "1.0.0",
        "package_digest": "1" * 64,
        "brief_id": "brief-compare-choices",
        "brief_version": "1.0.0",
        "brief_digest": "2" * 64,
        "curriculum_id": "investing-foundations",
        "curriculum_version": "1.0.0",
        "curriculum_digest": "3" * 64,
        "placement_id": "placement-compare-choices",
        "placement_version": "1.0.0",
        "placement_digest": "4" * 64,
    }
    milestones = [
        {
            "milestone_id": "compare-evidence",
            "milestone_version": "1.0.0",
            "sequence": 1,
            "title": "Compare the evidence",
        },
        {
            "milestone_id": "explain-limits",
            "milestone_version": "1.0.0",
            "sequence": 2,
            "title": "Explain the limits",
        },
    ]
    artifact_digest = "d" * 64
    resources = [
        {
            "resource_kind": "note",
            "resource_id": "note-purpose",
            "resource_version": 1,
            "record_digest": "5" * 64,
        },
        {
            "resource_kind": "note",
            "resource_id": "note-comparison",
            "resource_version": 1,
            "record_digest": "6" * 64,
        },
        {
            "resource_kind": "source",
            "resource_id": "source-reviewed",
            "resource_version": 1,
            "record_digest": "7" * 64,
        },
        {
            "resource_kind": "artifact",
            "resource_id": "artifact-evidence",
            "resource_version": 1,
            "record_digest": "8" * 64,
            "content_digest": artifact_digest,
            "byte_count": 96,
        },
    ]
    later_note = {
        "resource_kind": "note",
        "resource_id": "note-later-work",
        "resource_version": 1,
        "record_digest": "9" * 64,
    }
    snapshots = [
        {
            "snapshot_id": "snapshot-learning-one",
            "snapshot_digest": "a" * 64,
            "workspace_revision": 5,
            "closed_at": "2026-10-17T05:00:00Z",
        },
        {
            "snapshot_id": "snapshot-learning-two",
            "snapshot_digest": "b" * 64,
            "workspace_revision": 7,
            "closed_at": "2026-10-17T05:10:00Z",
        },
    ]

    def candidate(index: int) -> dict[str, Any]:
        snapshot = snapshots[index]
        return {
            "schema_version": "1.0.0",
            "project": {
                "project_id": project_id,
                "project_revision": 1,
                "project_shell_digest": "c" * 64,
                **snapshot,
            },
            "origin": origin,
            "policy_id": "assessment-project-closure",
            "policy_version": "1.0.0",
            "milestones": milestones,
            "resources": resources + ([later_note] if index else []),
        }

    candidates = [candidate(0), candidate(1)]

    def intent(index: int) -> dict[str, Any]:
        snapshot = snapshots[index]
        return {
            "schema_version": "1.0.0",
            "submission_id": f"submission-learning-{index + 1}",
            "source": {
                "project_id": project_id,
                "snapshot_id": snapshot["snapshot_id"],
                "snapshot_digest": snapshot["snapshot_digest"],
                **{
                    key: origin[key]
                    for key in (
                        "brief_id",
                        "brief_version",
                        "brief_digest",
                        "placement_id",
                        "placement_version",
                        "placement_digest",
                    )
                },
            },
            "policy_id": "assessment-project-closure",
            "policy_version": "1.0.0",
            "milestone_evidence": [
                {"milestone_id": milestones[0]["milestone_id"], "resources": [resources[0]]},
                {
                    "milestone_id": milestones[1]["milestone_id"],
                    "resources": [candidates[index]["resources"][-1]],
                },
            ],
        }

    intents = [intent(0), intent(1)]

    def evidence(index: int) -> dict[str, Any]:
        submission = intents[index]
        source = submission["source"]
        record = {
            "schema_version": "1.0.0",
            "evidence_id": f"evidence-learning-{index + 1}",
            "submission_id": submission["submission_id"],
            "project_id": project_id,
            "snapshot_id": source["snapshot_id"],
            "snapshot_digest": source["snapshot_digest"],
            **{
                key: source[key]
                for key in (
                    "brief_id",
                    "brief_version",
                    "brief_digest",
                    "placement_id",
                    "placement_version",
                    "placement_digest",
                )
            },
            "policy_id": "assessment-project-closure",
            "policy_version": "1.0.0",
            "milestone_evidence": submission["milestone_evidence"],
            "milestone_ids": [item["milestone_id"] for item in milestones],
            "request_fingerprint": ("e" if index == 0 else "f") * 64,
            "occurrence": index + 1,
            "accepted_sequence": 41 + index,
            "submitted_at": f"2026-10-17T05:{index + 1:02d}:00Z",
        }
        if index:
            record["supersedes_submission_id"] = intents[0]["submission_id"]
        return record

    evidence_records = [evidence(0), evidence(1)]
    outcomes = [
        {
            "validation": {
                "schema_version": "1.0.0",
                "status": "accepted",
                "request_fingerprint": record["request_fingerprint"],
                "issues": [],
            },
            "evidence": record,
        }
        for record in evidence_records
    ]
    history_items = [
        {
            key: record[key]
            for key in (
                "evidence_id",
                "submission_id",
                "snapshot_id",
                "snapshot_digest",
                "request_fingerprint",
                "occurrence",
                "submitted_at",
            )
        }
        | (
            {"supersedes_submission_id": record["supersedes_submission_id"]}
            if "supersedes_submission_id" in record
            else {}
        )
        for record in evidence_records
    ]
    completion_history = [
        {
            "event_id": f"event-learning-{index + 1}",
            **record,
            "occurred_at": f"2026-10-17T05:{index + 3:02d}:00Z",
        }
        for index, record in enumerate(evidence_records)
    ]
    return {
        "project": {
            "schema_version": "1.0.0",
            "project_id": project_id,
            "title": "Compare investment choices",
            "revision": 1,
            "origin": {"origin_type": "learning", **origin},
        },
        "independent_project_id": "project-independent-qualification",
        "artifact_sha256": artifact_digest,
        "snapshots": snapshots,
        "candidates": candidates,
        "submission_intents": intents,
        "outcomes": outcomes,
        "exact_replay": outcomes[0],
        "changed_retry_denial": {
            "status": 409,
            "document": {"error_version": "1.0", "code": "conflict"},
        },
        "history": {
            "schema_version": "1.0.0",
            "project_id": project_id,
            "items": history_items,
        },
        "completion": {
            "projection_version": "1.0.0",
            "project_id": project_id,
            "completed": True,
            "completion_meaning": "bounded_project_activity_completed",
            "source_digest": "0" * 64,
            "rebuilt_at": "2026-10-17T05:20:00Z",
            "history": completion_history,
        },
        "evidence": evidence_records,
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


def test_practice_semantics_preserve_closed_public_shape() -> None:
    assert runner.stable_practice_semantics(practice()) == practice()

    leaked = practice()
    leaked["items"][0]["correct_option_id"] = "private-answer"
    with pytest.raises(RuntimeError, match="exposed private fields"):
        runner.stable_practice_semantics(leaked)

    reordered = practice()
    reordered["items"].reverse()
    reordered["items"].append(
        {"item_id": "another-choice", "item_type": "single_select"}
    )
    assert runner.stable_practice_semantics(reordered) == reordered

    unknown_shape = practice()
    unknown_shape["items"][0]["item_type"] = "free_text"
    with pytest.raises(RuntimeError, match="unsupported item types"):
        runner.stable_practice_semantics(unknown_shape)


def test_practice_fixture_coverage_requires_each_supported_shape() -> None:
    runner.assert_practice_fixture_coverage(practice())

    missing_numeric = practice()
    missing_numeric["items"].pop()
    with pytest.raises(RuntimeError, match="does not cover supported item types"):
        runner.assert_practice_fixture_coverage(missing_numeric)


def test_headless_practice_uses_session_and_repeated_public_gets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []

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
        if path == "/api/v1/session/single-profile":
            return {"expires_at": "later"}
        return practice()

    monkeypatch.setattr(runner, "_request_json", request_json)

    assert runner.observe_headless_practice("http://127.0.0.1:8123") == practice()
    practice_path = (
        "/api/v1/curriculum/placements/intro-risk-return-practice/practice"
    )
    assert calls == [
        (
            "POST",
            "/api/v1/session/single-profile",
            {"limitation_acknowledged": True},
        ),
        ("GET", practice_path, None),
        ("GET", practice_path, None),
    ]


def test_side_effect_free_practice_requires_storage_count_invariance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    counts = {
        "assessment_attempts": 1,
        "assessment_responses": 1,
        "assessment_scores": 1,
        "assessment_completion_evidence": 1,
        "assessment_events": 1,
        "learner_projections": 1,
        "learner_history": 1,
    }
    snapshots = iter((counts, counts.copy()))
    monkeypatch.setattr(
        runner,
        "practice_open_storage_counts",
        lambda _dsn: next(snapshots),
    )
    monkeypatch.setattr(runner, "observe_headless_practice", lambda _origin: practice())

    assert runner.observe_side_effect_free_practice(
        origin="http://127.0.0.1:8123",
        postgres_dsn="postgresql://isolated",
    ) == practice()

    changed = counts | {"assessment_attempts": 2}
    snapshots = iter((counts, changed))
    with pytest.raises(RuntimeError, match="created learner evidence or state"):
        runner.observe_side_effect_free_practice(
            origin="http://127.0.0.1:8123",
            postgres_dsn="postgresql://isolated",
        )


def test_practice_restart_requires_exact_stable_public_meaning() -> None:
    runner.assert_practice_restart_result(
        before_restart=practice(),
        after_restart=practice(),
    )
    changed = practice()
    changed["package_version"] = "2.0.1"
    with pytest.raises(RuntimeError, match="changed after normal restart"):
        runner.assert_practice_restart_result(
            before_restart=practice(),
            after_restart=changed,
        )


def test_practice_submission_capture_is_closed_correlated_and_confined(
    tmp_path: Path,
) -> None:
    valid_capture = {
        "draft_request": practice_draft_save(),
        "draft_result": practice_draft(),
        "request": practice_submission(),
        "result": practice_result(),
        "progress": practice_progress(),
    }
    capture = tmp_path / "practice-submission-capture.json"
    capture.write_text(json.dumps(valid_capture), encoding="utf-8")
    draft_request, draft_result, request, result, progress = (
        runner.load_practice_submission_capture(
            capture,
            data_root=tmp_path,
            expected_practice=practice(),
        )
    )
    assert draft_request == practice_draft_save()
    assert draft_result == practice_draft()
    assert request == practice_submission()
    assert result == practice_result()
    assert progress == practice_progress()

    reordered = json.loads(json.dumps(valid_capture))
    reordered["draft_request"]["responses"].reverse()
    reordered["draft_result"]["responses"].reverse()
    reordered["request"]["responses"].reverse()
    reordered["result"]["item_results"].reverse()
    capture.write_text(json.dumps(reordered), encoding="utf-8")
    runner.load_practice_submission_capture(
        capture,
        data_root=tmp_path,
        expected_practice=practice(),
    )

    leaked = practice_result()
    leaked["learner_id"] = "private-learner"
    changed_capture = valid_capture | {"result": leaked}
    capture.write_text(
        json.dumps(changed_capture),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="closed public contract"):
        runner.load_practice_submission_capture(
            capture,
            data_root=tmp_path,
            expected_practice=practice(),
        )

    changed = practice_result()
    changed["package_version"] = "2.0.1"
    changed_capture = valid_capture | {"result": changed}
    capture.write_text(
        json.dumps(changed_capture),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="changed the submitted"):
        runner.load_practice_submission_capture(
            capture,
            data_root=tmp_path,
            expected_practice=practice(),
        )

    outside = tmp_path.parent / "outside-practice-capture.json"
    outside.write_text(
        json.dumps(valid_capture),
        encoding="utf-8",
    )
    try:
        with pytest.raises(RuntimeError, match="escaped its bounded root"):
            runner.load_practice_submission_capture(
                outside,
                data_root=tmp_path,
                expected_practice=practice(),
            )
    finally:
        outside.unlink()


def test_project_workspace_capture_is_correlated_confined_and_private(
    tmp_path: Path,
) -> None:
    valid = project_workspace_capture()
    capture = tmp_path / "project-workspace-capture.json"
    capture.write_text(json.dumps(valid), encoding="utf-8")
    assert runner.load_project_workspace_capture(
        capture,
        data_root=tmp_path,
    ) == valid

    leaked = json.loads(json.dumps(valid))
    leaked["project"]["object_key"] = "private/storage/path"
    capture.write_text(json.dumps(leaked), encoding="utf-8")
    with pytest.raises(RuntimeError, match="private runtime data"):
        runner.load_project_workspace_capture(capture, data_root=tmp_path)

    changed_learning = json.loads(json.dumps(valid))
    changed_learning["learning_state_after"]["navigation"][
        "projection_digest"
    ] = "0" * 64
    capture.write_text(json.dumps(changed_learning), encoding="utf-8")
    with pytest.raises(RuntimeError, match="changed learning state"):
        runner.load_project_workspace_capture(capture, data_root=tmp_path)

    changed_artifact = json.loads(json.dumps(valid))
    changed_artifact["export_bundle"]["files"][0]["content_base64"] = (
        base64.b64encode(b"changed").decode("ascii")
    )
    capture.write_text(json.dumps(changed_artifact), encoding="utf-8")
    with pytest.raises(RuntimeError, match="changed artifact meaning"):
        runner.load_project_workspace_capture(capture, data_root=tmp_path)

    outside = tmp_path.parent / "outside-project-workspace-capture.json"
    outside.write_text(json.dumps(valid), encoding="utf-8")
    try:
        with pytest.raises(RuntimeError, match="escaped its bounded root"):
            runner.load_project_workspace_capture(outside, data_root=tmp_path)
    finally:
        outside.unlink()


def test_project_learning_capture_is_correlated_confined_and_private(
    tmp_path: Path,
) -> None:
    valid = project_learning_capture()
    capture = tmp_path / "project-learning-capture.json"
    capture.write_text(json.dumps(valid), encoding="utf-8")
    assert runner.load_project_learning_capture(capture, data_root=tmp_path) == valid

    leaked = json.loads(json.dumps(valid))
    leaked["evidence"][0]["learner_id"] = "private-learner"
    capture.write_text(json.dumps(leaked), encoding="utf-8")
    with pytest.raises(RuntimeError, match="private runtime data"):
        runner.load_project_learning_capture(capture, data_root=tmp_path)

    changed_source = json.loads(json.dumps(valid))
    changed_source["submission_intents"][0]["source"]["snapshot_id"] = (
        "snapshot-unrelated"
    )
    capture.write_text(json.dumps(changed_source), encoding="utf-8")
    with pytest.raises(RuntimeError, match="changed submission meaning"):
        runner.load_project_learning_capture(capture, data_root=tmp_path)

    malformed_candidate = json.loads(json.dumps(valid))
    malformed_candidate["candidates"][0]["project"] = []
    capture.write_text(json.dumps(malformed_candidate), encoding="utf-8")
    with pytest.raises(RuntimeError, match="changed submission meaning"):
        runner.load_project_learning_capture(capture, data_root=tmp_path)

    broken_supersession = json.loads(json.dumps(valid))
    broken_supersession["evidence"][1]["supersedes_submission_id"] = (
        "submission-unrelated"
    )
    broken_supersession["outcomes"][1]["evidence"] = broken_supersession[
        "evidence"
    ][1]
    capture.write_text(json.dumps(broken_supersession), encoding="utf-8")
    with pytest.raises(RuntimeError, match="lost immutable supersession"):
        runner.load_project_learning_capture(capture, data_root=tmp_path)

    changed_completion = json.loads(json.dumps(valid))
    changed_completion["completion"]["history"][1]["submission_id"] = (
        "submission-unrelated"
    )
    capture.write_text(json.dumps(changed_completion), encoding="utf-8")
    with pytest.raises(RuntimeError, match="uncorrelated"):
        runner.load_project_learning_capture(capture, data_root=tmp_path)


def test_headless_project_learning_uses_public_routes_and_exact_replays(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    capture = project_learning_capture()
    project_id = capture["project"]["project_id"]
    api = f"/api/v1/projects/{project_id}"
    calls: list[tuple[str, str, dict[str, object] | None]] = []

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
        if path == "/api/v1/session/single-profile":
            return {"expires_at": "later"}
        if path == api:
            return capture["project"] | {"learner_id": "single-profile-learner"}
        for index, snapshot in enumerate(capture["snapshots"]):
            if path == (
                f"{api}/snapshots/{snapshot['snapshot_id']}/submission-candidate"
            ):
                return capture["candidates"][index]
            if path == f"{api}/snapshots/{snapshot['snapshot_id']}/submissions":
                assert method == "POST"
                assert payload == capture["submission_intents"][index]
                result = json.loads(json.dumps(capture["outcomes"][index]))
                result["evidence"]["learner_id"] = "single-profile-learner"
                return result
        if path == f"{api}/submissions":
            return capture["history"]
        if path == f"{api}/completion":
            return capture["completion"] | {"rebuilt_at": "2026-10-17T05:30:00Z"}
        for index, record in enumerate(capture["evidence"]):
            if path == f"{api}/submissions/{record['submission_id']}":
                return record | {"learner_id": "single-profile-learner"}
        raise AssertionError(f"Unexpected request: {method} {path}")

    monkeypatch.setattr(runner, "_request_json", request_json)
    monkeypatch.setattr(
        runner,
        "_request_json_read_status",
        lambda *_args, **_kwargs: (
            404,
            {"error_version": "1.0", "code": "not_found"},
        ),
    )

    observed = runner.observe_headless_project_learning(
        origin="http://127.0.0.1:8123",
        capture=capture,
    )
    assert observed["project"] == capture["project"]
    assert observed["exact_replays"] == capture["outcomes"]
    assert observed["independent_denial"] == {
        "status": 404,
        "code": "not_found",
    }
    assert calls[0] == (
        "POST",
        "/api/v1/session/single-profile",
        {"limitation_acknowledged": True},
    )
    assert [method for method, _path, _payload in calls].count("POST") == 3


def test_project_learning_storage_and_restart_require_exact_correlation() -> None:
    capture = project_learning_capture()
    evidence = capture["evidence"]
    sources = capture["completion"]["history"]
    storage = {
        "submissions": [
            [
                item["evidence_id"],
                item["submission_id"],
                item["snapshot_id"],
                item["request_fingerprint"],
                item["occurrence"],
                item["accepted_sequence"],
                item.get("supersedes_submission_id"),
            ]
            for item in evidence
        ],
        "events": [
            [source["event_id"], item["evidence_id"]]
            for source, item in zip(sources, evidence, strict=True)
        ],
        "projections": [[True, 2, capture["completion"]["source_digest"]]],
        "history": [
            [
                source["event_id"],
                item["evidence_id"],
                item["submission_id"],
                item["snapshot_id"],
                item["request_fingerprint"],
                item["occurrence"],
                item["accepted_sequence"],
                item.get("supersedes_submission_id"),
            ]
            for source, item in zip(sources, evidence, strict=True)
        ],
        "audit": [
            [
                source["event_id"],
                item["evidence_id"],
                item["submission_id"],
                item["snapshot_id"],
                item["occurrence"],
                item.get("supersedes_submission_id"),
                "a" * 64,
            ]
            for source, item in zip(sources, evidence, strict=True)
        ],
    }
    runner.assert_project_learning_storage(storage, capture=capture)
    runner.assert_project_learning_restart_result(
        before_observation={"project": capture["project"]},
        after_observation={"project": json.loads(json.dumps(capture["project"]))},
        before_storage=storage,
        after_storage=json.loads(json.dumps(storage)),
    )

    duplicate = json.loads(json.dumps(storage))
    duplicate["events"].append(duplicate["events"][0])
    with pytest.raises(RuntimeError, match="counts are incomplete"):
        runner.assert_project_learning_storage(duplicate, capture=capture)

    changed_projection = json.loads(json.dumps(storage))
    changed_projection["projections"][0][2] = "f" * 64
    with pytest.raises(RuntimeError, match="projection is uncorrelated"):
        runner.assert_project_learning_storage(changed_projection, capture=capture)

    with pytest.raises(RuntimeError, match="changed after normal restart"):
        runner.assert_project_learning_restart_result(
            before_observation={"project": capture["project"]},
            after_observation={"project": {"project_id": "changed"}},
            before_storage=storage,
            after_storage=storage,
        )


def test_headless_project_workspace_uses_only_public_api_and_exact_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    capture = project_workspace_capture()
    project = capture["project"]
    workspace = capture["current_workspace"]
    snapshot = capture["snapshot"]
    export_bundle = capture["export_bundle"]
    project_id = project["project_id"]
    snapshot_id = snapshot["snapshot_id"]
    calls: list[tuple[str, str]] = []

    def request_json(
        _opener: object,
        *,
        origin: str,
        path: str,
        method: str = "GET",
        payload: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        assert origin == "http://127.0.0.1:8123"
        calls.append((method, path))
        if path == "/api/v1/session/single-profile":
            assert method == "POST"
            assert payload == {"limitation_acknowledged": True}
            return {"expires_at": "later"}
        documents = {
            "/api/v1/projects": {"records": [project]},
            f"/api/v1/projects/{project_id}": project,
            f"/api/v1/projects/{project_id}/workspace": workspace,
            f"/api/v1/projects/{project_id}/snapshots": {
                "records": [snapshot]
            },
            f"/api/v1/projects/{project_id}/snapshots/{snapshot_id}": snapshot,
            (
                f"/api/v1/projects/{project_id}/snapshots/"
                f"{snapshot_id}/export"
            ): export_bundle,
        }
        return json.loads(json.dumps(documents[path]))

    artifact = workspace["artifacts"][0]

    def request_bytes(
        _opener: object,
        *,
        origin: str,
        path: str,
    ) -> bytes:
        assert origin == "http://127.0.0.1:8123"
        assert path == (
            f"/api/v1/projects/{project_id}/artifacts/"
            f"{artifact['artifact_id']}/versions/{artifact['artifact_version']}"
        )
        return base64.b64decode(export_bundle["files"][0]["content_base64"])

    monkeypatch.setattr(runner, "_request_json", request_json)
    monkeypatch.setattr(runner, "_request_bytes", request_bytes)
    observed = runner.observe_headless_project_workspace(
        origin="http://127.0.0.1:8123",
        capture=capture,
    )

    assert observed["project"] == project
    assert observed["workspace"] == workspace
    assert observed["snapshot"] == snapshot
    assert observed["export_bundle"] == runner.stable_project_export_bundle(
        export_bundle
    )
    assert observed["artifact_sha256"] == capture["artifact_sha256"]
    assert calls[0] == ("POST", "/api/v1/session/single-profile")
    assert all(method == "GET" for method, _path in calls[1:])


def test_project_restart_requires_exact_evidence_and_storage() -> None:
    observation = {
        "project": {"project_id": "project-qualification"},
        "artifact_sha256": "a" * 64,
    }
    storage = {key: 1 for key in runner.PROJECT_LEARNING_STORAGE_KEYS} | {
        "project_shells": 1,
        "project_workspaces": 1,
        "project_mutations": 4,
        "project_artifacts": 1,
        "project_snapshots": 1,
    }
    runner.assert_project_storage(storage)
    runner.assert_project_learning_state_unchanged(
        before_storage=dict(storage),
        after_storage=dict(storage),
    )
    runner.assert_project_restart_result(
        before_observation=observation,
        after_observation=json.loads(json.dumps(observation)),
        before_storage=storage,
        after_storage=dict(storage),
    )
    with pytest.raises(RuntimeError, match="incomplete or uncorrelated"):
        runner.assert_project_storage(storage | {"project_mutations": 3})
    with pytest.raises(RuntimeError, match="changed after normal restart"):
        runner.assert_project_restart_result(
            before_observation=observation,
            after_observation=observation | {"artifact_sha256": "b" * 64},
            before_storage=storage,
            after_storage=storage,
        )
    with pytest.raises(RuntimeError, match="storage changed"):
        runner.assert_project_restart_result(
            before_observation=observation,
            after_observation=observation,
            before_storage=storage,
            after_storage=storage | {"project_snapshots": 2},
        )
    with pytest.raises(RuntimeError, match="created Assessment or Learner-model"):
        runner.assert_project_learning_state_unchanged(
            before_storage=storage,
            after_storage=storage | {"assessment_attempts": 2},
        )
    with pytest.raises(RuntimeError, match="storage evidence is incomplete"):
        runner.assert_project_learning_state_unchanged(
            before_storage=storage,
            after_storage={
                key: value
                for key, value in storage.items()
                if key != "learner_completion_history"
            },
        )


def test_headless_submission_uses_only_public_session_and_post(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    success_calls: list[tuple[str, str, dict[str, object] | None]] = []
    denial_calls: list[tuple[str, dict[str, object]]] = []

    def request_json(
        _opener: object,
        *,
        origin: str,
        path: str,
        method: str = "GET",
        payload: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        assert origin == "http://127.0.0.1:8123"
        success_calls.append((method, path, payload))
        if path == "/api/v1/session/single-profile":
            return {"expires_at": "later"}
        return practice_result()

    statuses = iter(
        (
            (
                401,
                {
                    "error_version": "1.0",
                    "code": "unauthorized",
                    "message": "Session required.",
                    "correlation_id": "11111111-1111-4111-8111-111111111111",
                },
            ),
            (
                409,
                {
                    "error_version": "1.0",
                    "code": "conflict",
                    "message": "Request changed.",
                    "correlation_id": "11111111-1111-4111-8111-111111111111",
                },
            ),
        )
    )

    def request_status(
        _opener: object,
        *,
        origin: str,
        path: str,
        method: str,
        payload: dict[str, object],
    ) -> tuple[int, dict[str, Any]]:
        assert origin == "http://127.0.0.1:8123"
        assert method == "POST"
        denial_calls.append((path, payload))
        return next(statuses)

    monkeypatch.setattr(runner, "_request_json", request_json)
    monkeypatch.setattr(runner, "_request_json_status", request_status)

    assert runner.observe_headless_practice_submission(
        origin="http://127.0.0.1:8123",
        submission=practice_submission(),
        expected_result=practice_result(),
    ) == practice_result()
    submission_path = (
        "/api/v1/curriculum/placements/intro-risk-return-practice"
        "/practice/submissions"
    )
    assert success_calls == [
        (
            "POST",
            "/api/v1/session/single-profile",
            {"limitation_acknowledged": True},
        ),
        ("POST", submission_path, practice_submission()),
    ]
    assert [path for path, _payload in denial_calls] == [submission_path] * 2
    assert denial_calls[0][1] == practice_submission()
    assert denial_calls[1][1]["submission_id"] == practice_submission()[
        "submission_id"
    ]
    assert denial_calls[1][1] != practice_submission()


def test_progress_is_closed_coherent_and_order_tolerant() -> None:
    assert runner.stable_practice_progress(
        practice_progress(),
        expected_submission=practice_submission(),
        expected_result=practice_result(),
        expected_practice=practice(),
    ) == practice_progress()

    reordered = practice_draft()
    reordered["responses"].reverse()
    save = practice_draft_save()
    save["responses"].reverse()
    assert runner.stable_practice_draft(reordered, save=save) == reordered

    incoherent = practice_progress()
    incoherent["retry_state"]["attempts_remaining"] = 1
    with pytest.raises(RuntimeError, match="retry counts are incoherent"):
        runner.stable_practice_progress(incoherent)

    leaked = practice_progress()
    leaked["history"]["attempts"][0]["item_summaries"][0][
        "selected_option_id"
    ] = "private-response"
    with pytest.raises(RuntimeError, match="closed public contract"):
        runner.stable_practice_progress(leaked)

    mismatched_scope = practice_progress()
    mismatched_scope["retry_state"]["package_version"] = "9.9.9"
    mismatched_scope["history"]["package_version"] = "9.9.9"
    with pytest.raises(RuntimeError, match="changed the practice package_version"):
        runner.stable_practice_progress(
            mismatched_scope,
            expected_submission=practice_submission(),
            expected_result=practice_result(),
        )

    mismatched_limit = practice_progress()
    mismatched_limit["retry_state"]["max_attempts"] = 10
    mismatched_limit["retry_state"]["attempts_remaining"] = 9
    with pytest.raises(RuntimeError, match="immutable presentation"):
        runner.stable_practice_progress(
            mismatched_limit,
            expected_practice=practice(),
        )


def test_practice_denial_is_closed_and_rejects_private_values() -> None:
    safe = {
        "error_version": "1.0",
        "code": "conflict",
        "message": "Saved practice progress changed in another session.",
        "correlation_id": "11111111-1111-4111-8111-111111111111",
    }
    runner._assert_safe_practice_denial(
        409,
        safe,
        expected_status=409,
        expected_code="conflict",
    )
    benign_wording = safe | {
        "message": "Your answer was not saved. Authorization is required."
    }
    runner._assert_safe_practice_denial(
        409,
        benign_wording,
        expected_status=409,
        expected_code="conflict",
    )

    leaked = safe | {
        "message": (
            "learner_id=private selected_option_id=answer "
            "from assessment.practice_drafts"
        )
    }
    with pytest.raises(RuntimeError, match="private or diagnostic"):
        runner._assert_safe_practice_denial(
            409,
            leaked,
            expected_status=409,
            expected_code="conflict",
        )

    expanded = safe | {"diagnostic": "private.storage.detail"}
    with pytest.raises(RuntimeError, match="closed public contract"):
        runner._assert_safe_practice_denial(
            409,
            expanded,
            expected_status=409,
            expected_code="conflict",
        )


def test_headless_progress_uses_shared_public_api_and_preserves_stale_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []
    saved = practice_draft()
    progress_documents = iter(
        (practice_progress(), practice_progress(draft=saved))
    )
    draft_documents = iter((saved, saved))

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
        if path == "/api/v1/session/single-profile":
            return {"expires_at": "later"}
        if path.endswith("/progress"):
            return next(progress_documents)
        return next(draft_documents)

    denial_calls: list[dict[str, object]] = []

    def request_status(
        _opener: object,
        *,
        origin: str,
        path: str,
        method: str,
        payload: dict[str, object],
    ) -> tuple[int, dict[str, Any]]:
        assert origin == "http://127.0.0.1:8123"
        assert path.endswith("/draft")
        assert method == "PUT"
        denial_calls.append(payload)
        return 409, {
            "error_version": "1.0",
            "code": "conflict",
            "message": "Revision changed.",
            "correlation_id": "11111111-1111-4111-8111-111111111111",
        }

    monkeypatch.setattr(runner, "_request_json", request_json)
    monkeypatch.setattr(runner, "_request_json_status", request_status)

    observed_draft, observed_progress = runner.observe_headless_practice_progress(
        origin="http://127.0.0.1:8123",
        expected_progress=practice_progress(),
        draft_save=practice_draft_save(),
    )

    assert observed_draft == saved
    assert observed_progress == practice_progress(draft=saved)
    assert [method for method, _path, _payload in calls] == [
        "POST",
        "GET",
        "PUT",
        "PUT",
        "GET",
    ]
    assert calls[2][2] == practice_draft_save()
    assert calls[3][2] == practice_draft_save()
    assert len(denial_calls) == 1
    assert denial_calls[0]["expected_revision"] == 0
    assert denial_calls[0] != practice_draft_save()


def test_practice_submission_restart_preserves_result_and_evidence() -> None:
    snapshot = {
        "attempts": 1,
        "responses": 3,
        "scores": 3,
        "completion_evidence": 1,
        "outbox_events": 1,
        "submission_id": practice_submission()["submission_id"],
        "attempt_id": practice_result()["attempt_id"],
        "evidence_id": practice_result()["evidence_id"],
    }
    runner.assert_practice_submission_storage(
        snapshot,
        submission=practice_submission(),
        result=practice_result(),
    )
    runner.assert_practice_submission_restart_result(
        before_result=practice_result(),
        after_result=practice_result(),
        before_storage=snapshot,
        after_storage=snapshot.copy(),
    )
    changed = snapshot | {"responses": 4}
    with pytest.raises(RuntimeError, match="evidence changed"):
        runner.assert_practice_submission_restart_result(
            before_result=practice_result(),
            after_result=practice_result(),
            before_storage=snapshot,
            after_storage=changed,
        )


class _RowResult:
    def __init__(self, row: tuple[int, ...]) -> None:
        self._row = row

    def fetchone(self) -> tuple[int, ...]:
        return self._row


class _FakeConnection:
    def __init__(
        self,
        rows: list[tuple[int, ...]],
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


@pytest.mark.parametrize(
    "failed_stage",
    ["application", "database container", "temporary data"],
)
def test_cleanup_attempts_every_exact_stage_after_each_injected_failure(
    monkeypatch: pytest.MonkeyPatch,
    failed_stage: str,
) -> None:
    calls: list[str] = []

    def stage(label: str):
        def cleanup(_target: object) -> None:
            calls.append(label)
            if label == failed_stage:
                raise RuntimeError("private cleanup detail")

        return cleanup

    monkeypatch.setattr(runner, "stop_application", stage("application"))
    monkeypatch.setattr(
        runner,
        "remove_container",
        stage("database container"),
    )
    monkeypatch.setattr(
        runner,
        "remove_data_root",
        stage("temporary data"),
    )

    failures = runner.cleanup_qualification(
        application=object(),
        container_name="faa-wrk0005-postgres-test",
        data_root=Path("bounded-data"),
    )

    assert calls == ["application", "database container", "temporary data"]
    assert failures == (f"{failed_stage} (RuntimeError)",)
    assert "private cleanup detail" not in failures[0]


def test_cleanup_diagnostics_preserve_the_primary_failure() -> None:
    primary = ValueError("primary qualification failure")

    with pytest.raises(ValueError, match="primary qualification failure") as captured:
        runner.finish_after_cleanup(
            primary,
            ("application (TimeoutExpired)", "temporary data (PermissionError)"),
        )

    assert captured.value is primary
    assert captured.value.__notes__ == [
        "Qualification cleanup also failed for: application "
        "(TimeoutExpired), temporary data (PermissionError)."
    ]


def test_cleanup_failure_without_primary_error_remains_bounded() -> None:
    with pytest.raises(RuntimeError) as captured:
        runner.finish_after_cleanup(
            None,
            ("database container (RuntimeError)",),
        )

    assert str(captured.value) == (
        "Qualification cleanup failed for: database container (RuntimeError)."
    )
