from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).parents[3] / "backend" / "src"))
from financial_ai_academy.modules.personal_workspace.adapters.workspace_contract import (
    ContractPersonalWorkspaceAdapter,
)
from financial_ai_academy.modules.personal_workspace.domain.workspace import (
    CreateBookmarkMutation,
    CreateCollectionMutation,
    RemoveCollectionMutation,
    RemoveRecordMutation,
    RenameCollectionMutation,
    SetCollectionMembersMutation,
    UpdateNoteMutation,
    WorkspaceMutationIntent,
    WorkspaceQuery,
)
from financial_ai_academy.modules.personal_workspace.ports.workspace_contract import (
    PersonalWorkspaceContractFailure,
)


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


def personal_workspace_capture() -> dict[str, Any]:
    project_capture = project_workspace_capture()
    project = project_capture["project"]
    current_project_workspace = project_capture["current_workspace"]
    project_snapshot = project_capture["snapshot"]
    project_snapshot_material = project_snapshot["snapshot"]
    project_artifact = current_project_workspace["artifacts"][0]
    provenance = {
        "published_by": "Financial AI Academy",
        "published_at": "2026-10-17T10:00:00Z",
        "content_reviewed_on": "2026-10-17",
        "educational_use_notice": "Educational content only.",
    }
    target = {
        "reference_kind": "placed_lesson",
        "owner_module": "curriculum",
        "placement_id": "intro-risk-return-primary",
        "package_id": "intro-risk-return",
        "package_version": "1.1.0",
        "package_digest": "a" * 64,
        "title": "Understanding Risk and Return",
        "destination": "/learn/placements/intro-risk-return-primary",
        "target_status": "available",
        "provenance": provenance,
        "validated_at": "2026-10-17T12:00:00Z",
    }
    bookmark = {
        "record_kind": "bookmark",
        "record_id": "bookmark-one",
        "label": "Review risk and return Σ",
        "target": target,
        "archived": False,
        "created_at": "2026-10-17T12:02:00Z",
        "updated_at": "2026-10-17T12:03:00Z",
    }
    note = {
        "record_kind": "note",
        "record_id": "note-one",
        "title": "Café risk and return notes",
        "body": (
            "Uncertainty and potential reward are related, but neither "
            "promises an outcome."
        ),
        "target": target,
        "archived": False,
        "created_at": "2026-10-17T12:01:00Z",
        "updated_at": "2026-10-17T12:07:00Z",
    }
    project_common = {
        "owner_module": "project",
        "project_id": project["project_id"],
        "title": project["title"],
        "lifecycle": project["lifecycle"],
        "project_revision": project["revision"],
        "workspace_revision": current_project_workspace["workspace_revision"],
        "target_status": "available",
        "validated_at": "2026-10-17T12:08:00Z",
    }
    project_note = {
        "record_kind": "note",
        "record_id": "note-project",
        "title": "Project workspace reminders",
        "body": "Keep this Project source connected without copying its working files.",
        "target": project_common
        | {
            "reference_kind": "project_workspace",
            "destination": f"/projects/{project['project_id']}#workspace",
        },
        "archived": False,
        "created_at": "2026-10-17T12:08:00Z",
        "updated_at": "2026-10-17T12:08:00Z",
    }
    snapshot_bookmark = {
        "record_kind": "bookmark",
        "record_id": "bookmark-snapshot",
        "label": "Fixed Project checkpoint",
        "target": project_common
        | {
            "reference_kind": "project_snapshot",
            "project_revision": project_snapshot_material["project_revision"],
            "workspace_revision": project_snapshot_material["workspace_revision"],
            "snapshot_id": project_snapshot["snapshot_id"],
            "snapshot_digest": project_snapshot["snapshot_digest"],
            "closed_at": project_snapshot["closed_at"],
            "destination": (
                f"/projects/{project['project_id']}#snapshot-"
                f"{project_snapshot['snapshot_id']}"
            ),
        },
        "archived": False,
        "created_at": "2026-10-17T12:09:00Z",
        "updated_at": "2026-10-17T12:09:00Z",
    }
    artifact_bookmark = {
        "record_kind": "bookmark",
        "record_id": "bookmark-artifact",
        "label": "Project dataset record",
        "target": project_common
        | {
            "reference_kind": "project_artifact",
            "artifact_id": project_artifact["artifact_id"],
            "artifact_version": project_artifact["artifact_version"],
            "artifact_kind": project_artifact["artifact_kind"],
            "logical_path": project_artifact["logical_path"],
            "media_type": project_artifact["media_type"],
            "inspection_mode": project_artifact["inspection_mode"],
            "byte_count": project_artifact["byte_count"],
            "content_digest": project_artifact["content_digest"],
            "created_at": project_artifact["created_at"],
            "destination": (
                f"/projects/{project['project_id']}#artifact-"
                f"{project_artifact['artifact_id']}"
                f"-v{project_artifact['artifact_version']}"
            ),
        },
        "archived": False,
        "created_at": "2026-10-17T12:10:00Z",
        "updated_at": "2026-10-17T12:10:00Z",
    }
    workspace = {
        "schema_version": "1.0.0",
        "workspace_id": "workspace-one",
        "learner_id": "single-profile-learner",
        "revision": 12,
        "records": [bookmark, note, project_note, snapshot_bookmark, artifact_bookmark],
        "collections": [
            {
                "collection_id": "collection-one",
                "title": "Foundations İ",
                "member_record_ids": [
                    "bookmark-one",
                    "note-one",
                    "note-project",
                    "bookmark-snapshot",
                    "bookmark-artifact",
                ],
                "created_at": "2026-10-17T12:04:00Z",
                "updated_at": "2026-10-17T12:05:00Z",
            }
        ],
        "created_at": "2026-10-17T12:00:00Z",
        "updated_at": "2026-10-17T12:10:00Z",
        "workspace_digest": "b" * 64,
    }
    query_request = {
        "schema_version": "1.0.0",
        "text": "σ",
        "record_kinds": ["bookmark"],
        "owner_modules": ["curriculum"],
        "reference_kinds": ["placed_lesson"],
        "target_statuses": ["available"],
        "archived": False,
        "collection_id": "collection-one",
        "sort": "title_asc",
        "limit": 50,
    }
    refresh_workspace = json.loads(json.dumps(workspace))
    refresh_workspace["revision"] = 10
    refresh_workspace["workspace_digest"] = "c" * 64
    return {
        "workspace": workspace,
        "export": {
            "schema_version": "1.0.0",
            "workspace_digest": workspace["workspace_digest"],
            "generated_at": "2026-10-17T12:11:00Z",
            "workspace": json.loads(json.dumps(workspace)),
        },
        "exact_replay_request": {
            "schema_version": "1.0.0",
            "idempotency_key": "11111111-1111-4111-8111-111111111111",
            "expected_revision": 11,
            "mutation": {
                "operation": "restore_record",
                "record_id": "note-one",
            },
        },
        "query_request": query_request,
        "query_result": {
            "schema_version": "1.0.0",
            "workspace_revision": 9,
            "query_digest": runner.personal_workspace_query_digest(query_request),
            "applied_query": json.loads(json.dumps(query_request)),
            "records": [json.loads(json.dumps(bookmark))],
            "next_cursor": None,
        },
        "refresh_request": {
            "schema_version": "1.0.0",
            "idempotency_key": "99999999-9999-4999-8999-999999999999",
            "expected_revision": 9,
            "mutation": {
                "operation": "refresh_reference",
                "record_id": "note-project",
            },
        },
        "refresh_workspace": refresh_workspace,
        "expected": {
            "note_title": note["title"],
            "note_body": note["body"],
            "bookmark_label": bookmark["label"],
            "collection_title": "Foundations İ",
            "placement_id": "intro-risk-return-primary",
            "project_id": project["project_id"],
            "project_title": project["title"],
            "project_lifecycle": project["lifecycle"],
            "project_revision": project["revision"],
            "project_workspace_revision": current_project_workspace[
                "workspace_revision"
            ],
            "project_note_title": project_note["title"],
            "project_note_body": project_note["body"],
            "snapshot_id": project_snapshot["snapshot_id"],
            "snapshot_label": snapshot_bookmark["label"],
            "snapshot_digest": project_snapshot["snapshot_digest"],
            "snapshot_project_revision": project_snapshot_material[
                "project_revision"
            ],
            "snapshot_workspace_revision": project_snapshot_material[
                "workspace_revision"
            ],
            "snapshot_closed_at": project_snapshot["closed_at"],
            "artifact_id": project_artifact["artifact_id"],
            "artifact_version": project_artifact["artifact_version"],
            "artifact_label": artifact_bookmark["label"],
            "artifact_project_revision": project["revision"],
            "artifact_workspace_revision": current_project_workspace[
                "workspace_revision"
            ],
            "artifact_kind": project_artifact["artifact_kind"],
            "artifact_logical_path": project_artifact["logical_path"],
            "artifact_media_type": project_artifact["media_type"],
            "artifact_inspection_mode": project_artifact["inspection_mode"],
            "artifact_digest": project_artifact["content_digest"],
            "artifact_byte_count": project_artifact["byte_count"],
            "artifact_created_at": project_artifact["created_at"],
        },
    }


def correlated_personal_workspace_storage() -> dict[str, Any]:
    capture = personal_workspace_capture()
    workspace = capture["workspace"]
    mutation_rows = [
        {
            "workspace_id": workspace["workspace_id"],
            "idempotency_key": f"prior-key-{revision}",
            "accepted_workspace": {
                "workspace_id": workspace["workspace_id"],
                "revision": revision,
            },
            "accepted_revision": revision,
        }
        for revision in range(2, workspace["revision"])
    ]
    mutation_rows.append(
        {
            "workspace_id": workspace["workspace_id"],
            "idempotency_key": capture["exact_replay_request"]["idempotency_key"],
            "accepted_workspace": json.loads(json.dumps(workspace)),
            "accepted_revision": workspace["revision"],
        }
    )
    return {
        "personal_workspaces": 1,
        "personal_mutations": workspace["revision"] - 1,
        "content_packages": 1,
        "curriculum_placements": 3,
        "curriculum_discovery_records": 3,
        "assessment_attempts": 1,
        "assessment_practice_attempts": 1,
        "assessment_project_submissions": 2,
        "learner_lesson_projections": 1,
        "learner_practice_projections": 1,
        "learner_project_projections": 1,
        "project_shells": 2,
        "target_state": {
            schema: {
                "table_count": index + 1,
                "row_count": (index + 1) * 3,
                "sha256": hashlib.sha256(schema.encode("utf-8")).hexdigest(),
            }
            for index, schema in enumerate(runner.PERSONAL_WORKSPACE_TARGET_SCHEMAS)
        },
        "workspace_rows": [
            {
                "workspace_id": workspace["workspace_id"],
                "revision": workspace["revision"],
                "workspace": json.loads(json.dumps(workspace)),
            }
        ],
        "mutation_rows": mutation_rows,
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


def test_personal_workspace_capture_is_closed_correlated_and_private(
    tmp_path: Path,
) -> None:
    capture = personal_workspace_capture()
    project_capture = project_workspace_capture()
    path = tmp_path / "personal-workspace-capture.json"
    path.write_text(json.dumps(capture), encoding="utf-8")
    assert runner.load_personal_workspace_capture(
        path,
        data_root=tmp_path,
        project_capture=project_capture,
    ) == capture

    leaked = json.loads(json.dumps(capture))
    leaked["credential"] = "private"
    path.write_text(json.dumps(leaked), encoding="utf-8")
    with pytest.raises(RuntimeError, match="invalid shape"):
        runner.load_personal_workspace_capture(
            path, data_root=tmp_path, project_capture=project_capture
        )

    expanded = json.loads(json.dumps(capture))
    expanded["workspace"]["private_detail"] = "hidden"
    path.write_text(json.dumps(expanded), encoding="utf-8")
    with pytest.raises(RuntimeError, match="closed public contract"):
        runner.load_personal_workspace_capture(
            path, data_root=tmp_path, project_capture=project_capture
        )

    dangling = json.loads(json.dumps(capture))
    dangling["workspace"]["collections"][0]["member_record_ids"].append(
        "missing-record"
    )
    path.write_text(json.dumps(dangling), encoding="utf-8")
    with pytest.raises(RuntimeError, match="collection is invalid"):
        runner.load_personal_workspace_capture(
            path, data_root=tmp_path, project_capture=project_capture
        )

    copied_bytes = json.loads(json.dumps(capture))
    copied_bytes["workspace"]["records"][-1]["target"]["content_base64"] = (
        "c2NlbmFyaW8sdmFsdWU="
    )
    path.write_text(json.dumps(copied_bytes), encoding="utf-8")
    with pytest.raises(RuntimeError, match="closed public contract"):
        runner.load_personal_workspace_capture(
            path, data_root=tmp_path, project_capture=project_capture
        )

    changed_digest = personal_workspace_capture()
    changed_digest["query_result"]["query_digest"] = "f" * 64
    path.write_text(json.dumps(changed_digest), encoding="utf-8")
    with pytest.raises(RuntimeError, match="query result correlation"):
        runner.load_personal_workspace_capture(
            path, data_root=tmp_path, project_capture=project_capture
        )

    changed_query = personal_workspace_capture()
    changed_query["query_result"]["applied_query"]["text"] = "different"
    path.write_text(json.dumps(changed_query), encoding="utf-8")
    with pytest.raises(RuntimeError, match="changed requested meaning"):
        runner.load_personal_workspace_capture(
            path, data_root=tmp_path, project_capture=project_capture
        )

    unowned_query_record = personal_workspace_capture()
    unowned_query_record["query_result"]["records"][0]["record_id"] = "other-record"
    path.write_text(json.dumps(unowned_query_record), encoding="utf-8")
    with pytest.raises(RuntimeError, match="unowned or changed record"):
        runner.load_personal_workspace_capture(
            path, data_root=tmp_path, project_capture=project_capture
        )

    widened_refresh = personal_workspace_capture()
    widened_refresh["refresh_request"]["mutation"]["owner_module"] = "project"
    path.write_text(json.dumps(widened_refresh), encoding="utf-8")
    with pytest.raises(RuntimeError, match="refresh mutation.*closed public contract"):
        runner.load_personal_workspace_capture(
            path, data_root=tmp_path, project_capture=project_capture
        )

    mismatched_refresh = personal_workspace_capture()
    mismatched_refresh["refresh_workspace"]["revision"] = 11
    path.write_text(json.dumps(mismatched_refresh), encoding="utf-8")
    with pytest.raises(RuntimeError, match="refresh revision is uncorrelated"):
        runner.load_personal_workspace_capture(
            path, data_root=tmp_path, project_capture=project_capture
        )

    mismatched_project = json.loads(json.dumps(capture))
    mismatched_project["workspace"]["records"][-2]["target"]["project_id"] = (
        "project.other"
    )
    mismatched_project["workspace"]["records"][-2]["target"]["destination"] = (
        "/projects/project.other#snapshot-snapshot-one"
    )
    mismatched_project["export"]["workspace"] = json.loads(
        json.dumps(mismatched_project["workspace"])
    )
    path.write_text(json.dumps(mismatched_project), encoding="utf-8")
    with pytest.raises(RuntimeError, match="browser-observed meaning"):
        runner.load_personal_workspace_capture(
            path, data_root=tmp_path, project_capture=project_capture
        )


@pytest.mark.parametrize(
    ("record_index", "field", "changed_value"),
    (
        (2, "workspace_revision", 999),
        (3, "closed_at", "2026-10-16T16:04:01Z"),
        (4, "logical_path", "different-but-safe.csv"),
    ),
)
def test_personal_workspace_capture_binds_each_project_reference_class(
    tmp_path: Path,
    record_index: int,
    field: str,
    changed_value: object,
) -> None:
    capture = personal_workspace_capture()
    capture["workspace"]["records"][record_index]["target"][field] = changed_value
    capture["export"]["workspace"] = json.loads(json.dumps(capture["workspace"]))
    path = tmp_path / "personal-workspace-capture.json"
    path.write_text(json.dumps(capture), encoding="utf-8")

    with pytest.raises(RuntimeError, match="uncorrelated|browser-observed meaning"):
        runner.load_personal_workspace_capture(
            path,
            data_root=tmp_path,
            project_capture=project_workspace_capture(),
        )


def test_personal_workspace_capture_binds_browser_expectations_to_project(
    tmp_path: Path,
) -> None:
    capture = personal_workspace_capture()
    capture["expected"]["artifact_kind"] = "code"
    path = tmp_path / "personal-workspace-capture.json"
    path.write_text(json.dumps(capture), encoding="utf-8")

    with pytest.raises(RuntimeError, match="expectations changed Project meaning"):
        runner.load_personal_workspace_capture(
            path,
            data_root=tmp_path,
            project_capture=project_workspace_capture(),
        )


@pytest.mark.parametrize(
    "logical_path",
    (
        "Re\u0301sume\u0301-data.csv",
        " report.csv",
        "folder./report.csv",
        "folder/control\u001f.csv",
        "folder/bad?.csv",
        "CON.txt",
    ),
)
def test_personal_workspace_reference_rejects_noncanonical_project_paths(
    logical_path: str,
) -> None:
    target = personal_workspace_capture()["workspace"]["records"][4]["target"]
    target["logical_path"] = logical_path
    with pytest.raises(RuntimeError, match="inert-file reference is invalid"):
        runner._stable_personal_workspace_reference(target)


def test_personal_workspace_reference_accepts_varied_nfc_project_path() -> None:
    target = personal_workspace_capture()["workspace"]["records"][4]["target"]
    target["logical_path"] = "Données/Στοιχεία.csv"
    assert runner._stable_personal_workspace_reference(target) == target


@pytest.mark.parametrize(
    ("record_index", "time_field"),
    ((3, "closed_at"), (4, "created_at")),
)
def test_personal_workspace_reference_rejects_future_project_material(
    record_index: int,
    time_field: str,
) -> None:
    target = personal_workspace_capture()["workspace"]["records"][record_index][
        "target"
    ]
    target[time_field] = "2026-10-17T12:08:01Z"
    with pytest.raises(RuntimeError, match="reference is invalid"):
        runner._stable_personal_workspace_reference(target)


def test_headless_personal_workspace_uses_public_api_and_bounded_conflicts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    capture = personal_workspace_capture()
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
        if path == "/api/v1/personal-workspace/query":
            return capture["query_result"] | {
                "workspace_revision": capture["workspace"]["revision"]
            }
        if path == "/api/v1/personal-workspace/export":
            return capture["export"]
        if (
            path == "/api/v1/personal-workspace/mutations"
            and payload == capture["refresh_request"]
        ):
            return capture["refresh_workspace"]
        return capture["workspace"]

    denials = iter(("immutable_conflict", "stale_revision", "source_unavailable"))
    denial_messages = {
        "immutable_conflict": "The request key already names different saved work.",
        "stale_revision": (
            "The saved workspace changed. Refresh it before trying again."
        ),
        "source_unavailable": "The learning item is not available to save.",
    }

    def request_status(
        _opener: object,
        *,
        origin: str,
        path: str,
        method: str,
        payload: dict[str, object],
    ) -> tuple[int, dict[str, Any]]:
        assert origin == "http://127.0.0.1:8123"
        assert path == "/api/v1/personal-workspace/mutations"
        assert method == "POST"
        code = next(denials)
        calls.append((method, path, payload))
        return 409, {
            "error_version": "1.0",
            "code": code,
            "message": denial_messages[code],
            "correlation_id": "22222222-2222-4222-8222-222222222222",
        }

    monkeypatch.setattr(runner, "_request_json", request_json)
    monkeypatch.setattr(runner, "_request_json_status", request_status)

    assert runner.observe_headless_personal_workspace(
        origin="http://127.0.0.1:8123",
        capture=capture,
    ) == capture["workspace"]
    assert [method for method, _path, _payload in calls] == [
        "POST",
        "GET",
        "GET",
        "POST",
        "POST",
        "POST",
        "POST",
        "POST",
        "POST",
        "GET",
    ]
    assert calls[2][1] == "/api/v1/personal-workspace/export"
    assert calls[3][1:] == (
        "/api/v1/personal-workspace/query",
        capture["query_request"],
    )
    assert calls[4][2] == capture["refresh_request"]
    assert calls[5][2] == capture["exact_replay_request"]
    assert calls[6][2]["idempotency_key"] == capture["exact_replay_request"][
        "idempotency_key"
    ]
    assert calls[6][2]["mutation"]["operation"] == "archive_record"
    assert calls[7][2]["idempotency_key"] != capture["exact_replay_request"][
        "idempotency_key"
    ]
    assert calls[8][2]["mutation"]["selector"] == {
        "reference_kind": "project_workspace",
        "project_id": "project.missing-qualification",
    }


def test_personal_workspace_query_evidence_is_canonical_and_shape_flexible() -> None:
    capture = personal_workspace_capture()
    query = capture["query_request"]
    equivalent = {
        **query,
        "text": "  Σ\u0085",
        "cursor": "opaque_page_2",
    }
    assert runner.personal_workspace_query_digest(equivalent) == capture[
        "query_result"
    ]["query_digest"]

    continued = json.loads(json.dumps(capture["query_result"]))
    continued["applied_query"] = runner.stable_personal_workspace_query(equivalent)
    continued["next_cursor"] = "opaque_page_3"
    assert runner.stable_personal_workspace_query_result(
        continued,
        requested=equivalent,
        workspace=capture["workspace"],
    )["next_cursor"] == "opaque_page_3"

    changed = {**query, "owner_modules": ["project"]}
    assert runner.personal_workspace_query_digest(changed) != capture["query_result"][
        "query_digest"
    ]


def test_personal_workspace_evidence_normalizes_equivalent_utc_precision() -> None:
    workspace = personal_workspace_capture()["workspace"]
    workspace["updated_at"] = "2026-10-17T12:10:00.123450Z"
    workspace["records"][0]["created_at"] = "2026-10-17T12:00:00.120000Z"
    workspace["records"][0]["target"]["validated_at"] = (
        "2026-10-17T12:00:00.000010Z"
    )

    normalized = runner.stable_personal_workspace(workspace)

    assert normalized["updated_at"] == "2026-10-17T12:10:00.12345Z"
    assert normalized["records"][0]["created_at"] == "2026-10-17T12:00:00.12Z"
    assert (
        normalized["records"][0]["target"]["validated_at"]
        == "2026-10-17T12:00:00.00001Z"
    )


def test_personal_workspace_export_is_closed_correlated_and_chronological() -> None:
    capture = personal_workspace_capture()
    normalized = runner.stable_personal_workspace_export(
        capture["export"],
        expected_workspace=capture["workspace"],
    )
    assert normalized == capture["export"]

    future = json.loads(json.dumps(capture["export"]))
    future["generated_at"] = "2026-10-17T12:12:00.123450Z"
    assert runner.stable_personal_workspace_export(
        future,
        expected_workspace=capture["workspace"],
    )["generated_at"] == "2026-10-17T12:12:00.12345Z"


@pytest.mark.parametrize(
    "mutate",
    (
        lambda document: document.update({"private_storage": "not-allowed"}),
        lambda document: document.update({"workspace_digest": "f" * 64}),
        lambda document: document.update({"generated_at": "2026-10-17T12:09:59Z"}),
        lambda document: document["workspace"].update({"revision": 99}),
    ),
)
def test_personal_workspace_export_rejects_widened_or_changed_meaning(mutate) -> None:
    capture = personal_workspace_capture()
    document = json.loads(json.dumps(capture["export"]))
    mutate(document)
    with pytest.raises(RuntimeError, match="Personal workspace export"):
        runner.stable_personal_workspace_export(
            document,
            expected_workspace=capture["workspace"],
        )


def test_personal_workspace_denials_reject_actual_sensitive_values() -> None:
    capture = personal_workspace_capture()
    snapshot_target = capture["workspace"]["records"][3]["target"]
    artifact_target = capture["workspace"]["records"][4]["target"]
    sensitive_values = (
        capture["workspace"]["learner_id"],
        capture["workspace"]["workspace_id"],
        capture["workspace"]["records"][0]["record_id"],
        capture["expected"]["note_body"],
        capture["exact_replay_request"]["idempotency_key"],
        "personal_workspace.mutations",
        snapshot_target["project_id"],
        snapshot_target["title"],
        snapshot_target["snapshot_id"],
        snapshot_target["snapshot_digest"],
        artifact_target["artifact_id"],
        artifact_target["logical_path"],
        artifact_target["content_digest"],
    )
    for leaked_value in sensitive_values:
        with pytest.raises(RuntimeError, match="disclosed private details"):
            runner._assert_safe_personal_workspace_denial(
                409,
                {
                    "error_version": "1.0",
                    "code": "immutable_conflict",
                    "message": f"Unable to apply {leaked_value}",
                    "correlation_id": "22222222-2222-4222-8222-222222222222",
                },
                expected_code="immutable_conflict",
                capture=capture,
            )
    guessed_project_id = "project.guessed-private"
    with pytest.raises(RuntimeError, match="disclosed private details"):
        runner._assert_safe_personal_workspace_denial(
            409,
            {
                "error_version": "1.0",
                "code": "source_unavailable",
                "message": f"Project {guessed_project_id} is unavailable.",
                "correlation_id": "22222222-2222-4222-8222-222222222222",
            },
            expected_code="source_unavailable",
            capture=capture,
            additional_sensitive_values=(guessed_project_id,),
        )
    with pytest.raises(RuntimeError, match="changed public meaning"):
        runner._assert_safe_personal_workspace_denial(
            409,
            {
                "error_version": "1.0",
                "code": "source_unavailable",
                "message": "That Project does not exist.",
                "correlation_id": "22222222-2222-4222-8222-222222222222",
            },
            expected_code="source_unavailable",
            capture=capture,
        )
    with pytest.raises(RuntimeError, match="correlation is invalid"):
        runner._assert_safe_personal_workspace_denial(
            409,
            {
                "error_version": "1.0",
                "code": "immutable_conflict",
                "message": "The saved request could not be applied.",
                "correlation_id": "not-a-correlation",
            },
            expected_code="immutable_conflict",
            capture=capture,
        )


def test_personal_workspace_restart_preserves_exact_state_and_target_facts() -> None:
    capture = personal_workspace_capture()
    after = correlated_personal_workspace_storage()
    before_target = after | {
        "personal_workspaces": 0,
        "personal_mutations": 0,
        "workspace_rows": [],
        "mutation_rows": [],
    }
    runner.assert_personal_workspace_storage(after, capture=capture)
    runner.assert_personal_workspace_target_state_unchanged(
        before_storage=before_target,
        after_storage=after,
    )
    runner.assert_personal_workspace_restart_result(
        before_observation=personal_workspace_capture()["workspace"],
        after_observation=personal_workspace_capture()["workspace"],
        before_storage=after,
        after_storage=dict(after),
        capture=capture,
    )
    changed_target = json.loads(json.dumps(after))
    changed_target["target_state"]["project"]["sha256"] = "f" * 64
    with pytest.raises(RuntimeError, match="target or learning evidence"):
        runner.assert_personal_workspace_target_state_unchanged(
            before_storage=after,
            after_storage=changed_target,
        )
    changed_history = json.loads(json.dumps(after))
    changed_history["mutation_rows"][0]["idempotency_key"] = "changed-same-count"
    with pytest.raises(RuntimeError, match="changed during restart"):
        runner.assert_personal_workspace_restart_result(
            before_observation=personal_workspace_capture()["workspace"],
            after_observation=personal_workspace_capture()["workspace"],
            before_storage=after,
            after_storage=changed_history,
            capture=capture,
        )


def test_personal_workspace_qualification_accepts_safe_record_count_and_order_variation() -> None:
    capture = personal_workspace_capture()
    base = capture["workspace"]
    contract = ContractPersonalWorkspaceAdapter(
        Path(__file__).parents[3]
        / "contracts"
        / "learning"
        / "personal-workspace"
        / "v1",
        cursor_signing_key=b"qualification-only-cursor-key-32b",
    )

    def canonical_workspace(document: dict[str, Any]):
        candidate = json.loads(json.dumps(document))
        material = json.loads(json.dumps(candidate))
        material.pop("workspace_digest")
        candidate["workspace_digest"] = contract.canonical_digest(material)
        parsed = contract.parse_workspace(
            json.dumps(
                candidate,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        return parsed, contract.workspace_document(parsed)

    smaller = json.loads(json.dumps(base))
    smaller["records"] = smaller["records"][:2]
    smaller_ids = {record["record_id"] for record in smaller["records"]}
    smaller["collections"][0]["member_record_ids"] = [
        record_id
        for record_id in smaller["collections"][0]["member_record_ids"]
        if record_id in smaller_ids
    ]

    larger = json.loads(json.dumps(base))
    extra = json.loads(json.dumps(larger["records"][0]))
    extra["record_id"] = "bookmark-extra"
    extra["label"] = "Another safe saved lesson Σ"
    larger["records"].append(extra)
    larger["collections"][0]["member_record_ids"].append(extra["record_id"])

    reordered = json.loads(json.dumps(larger))
    reordered["records"] = list(reversed(reordered["records"]))

    for workspace in (smaller, larger, reordered):
        parsed_workspace, canonical_document = canonical_workspace(workspace)
        normalized = runner.stable_personal_workspace(canonical_document)
        assert {record["record_id"] for record in normalized["records"]} == {
            record["record_id"] for record in workspace["records"]
        }
        assert set(normalized["collections"][0]["member_record_ids"]).issubset(
            {record["record_id"] for record in normalized["records"]}
        )
        query_request = json.loads(json.dumps(capture["query_request"]))
        query_request["limit"] = 1
        parsed_query = contract.parse_workspace_query(
            json.dumps(query_request, ensure_ascii=False).encode("utf-8")
        )
        result = contract.workspace_query_result_document(
            contract.query_workspace(parsed_workspace, parsed_query)
        )
        qualified = runner.stable_personal_workspace_query_result(
            result,
            requested=query_request,
            workspace=normalized,
        )
        assert len(qualified["records"]) == 1
        matching_records = [
            record
            for record in normalized["records"]
            if record["record_kind"] == "bookmark"
            and record["target"]["owner_module"] == "curriculum"
            and "σ" in (record.get("label") or "").casefold()
        ]
        assert (qualified["next_cursor"] is not None) == (
            len(matching_records) > 1
        )
        if qualified["next_cursor"] is not None:
            continued_request = {
                **query_request,
                "cursor": qualified["next_cursor"],
            }
            continued_query = contract.parse_workspace_query(
                json.dumps(continued_request, ensure_ascii=False).encode("utf-8")
            )
            continued_result = contract.workspace_query_result_document(
                contract.query_workspace(parsed_workspace, continued_query)
            )
            continued = runner.stable_personal_workspace_query_result(
                continued_result,
                requested=continued_request,
                workspace=normalized,
            )
            assert len(continued["records"]) == 1
            assert continued["next_cursor"] is None


def test_personal_workspace_storage_requires_exact_row_correlation() -> None:
    capture = personal_workspace_capture()
    correlated = correlated_personal_workspace_storage()

    wrong_aggregate = json.loads(json.dumps(correlated))
    wrong_aggregate["workspace_rows"][0]["workspace_id"] = "other-workspace"
    with pytest.raises(RuntimeError, match="aggregate is uncorrelated"):
        runner.assert_personal_workspace_storage(
            wrong_aggregate,
            capture=capture,
        )

    wrong_history = json.loads(json.dumps(correlated))
    wrong_history["mutation_rows"][0]["workspace_id"] = "other-workspace"
    with pytest.raises(RuntimeError, match="history is uncorrelated"):
        runner.assert_personal_workspace_storage(
            wrong_history,
            capture=capture,
        )

    wrong_replay = json.loads(json.dumps(correlated))
    wrong_replay["mutation_rows"][-1]["accepted_workspace"]["workspace_digest"] = (
        "c" * 64
    )
    with pytest.raises(RuntimeError, match="replay evidence is uncorrelated"):
        runner.assert_personal_workspace_storage(
            wrong_replay,
            capture=capture,
        )


def test_capacity_refusal_keeps_query_export_removal_and_unrelated_work_available() -> None:
    root = Path(__file__).parents[3]
    fixture_path = (
        root
        / "contracts"
        / "compatibility"
        / "personal-workspace"
        / "v1"
        / "valid-populated-workspace.json"
    )
    adapter = ContractPersonalWorkspaceAdapter(
        root / "contracts" / "learning" / "personal-workspace" / "v1",
        cursor_signing_key=b"qualification-only-cursor-key-32b",
    )

    def parse(document: dict[str, Any]):
        candidate = deepcopy(document)
        material = deepcopy(candidate)
        material.pop("workspace_digest", None)
        candidate["workspace_digest"] = adapter.canonical_digest(material)
        return adapter.parse_workspace(
            json.dumps(candidate, ensure_ascii=False).encode("utf-8")
        )

    def intent(revision: int, key: str, mutation: object) -> WorkspaceMutationIntent:
        return WorkspaceMutationIntent(
            schema_version="1.0.0",
            idempotency_key=key,
            expected_revision=revision,
            mutation=mutation,  # type: ignore[arg-type]
        )

    base = json.loads(fixture_path.read_text(encoding="utf-8"))
    at = lambda minute: datetime(2026, 10, 17, 13, minute, tzinfo=timezone.utc)

    record_document = deepcopy(base)
    bookmark_template = deepcopy(record_document["records"][1])
    record_document["records"] = []
    record_document["collections"] = []
    for index in range(199):
        record = deepcopy(bookmark_template)
        record["record_id"] = f"bookmark.{index:03d}"
        record["label"] = None if index % 3 == 0 else f"Saved {index}"
        record_document["records"].append(record)
    record_workspace = parse(record_document)
    target = record_workspace.records[0].target
    record_full = adapter.apply_mutation(
        record_workspace,
        intent(
            record_workspace.revision,
            "capacity.record.accept",
            CreateBookmarkMutation(target, "Two hundred"),
        ),
        occurred_at=at(0),
        issued_id="bookmark.199",
    )
    with pytest.raises(PersonalWorkspaceContractFailure) as record_failure:
        adapter.apply_mutation(
            record_full,
            intent(
                record_full.revision,
                "capacity.record.refuse",
                CreateBookmarkMutation(target, "Too many"),
            ),
            occurred_at=at(1),
            issued_id="bookmark.200",
        )
    assert record_failure.value.code == "personal_workspace.contract.record_limit"
    assert adapter.query_workspace(record_full, WorkspaceQuery(limit=5)).records
    assert adapter.export_workspace(record_full, generated_at=at(1)).workspace == record_full
    record_reduced = adapter.apply_mutation(
        record_full,
        intent(
            record_full.revision,
            "capacity.record.remove",
            RemoveRecordMutation("bookmark.000"),
        ),
        occurred_at=at(2),
    )
    record_continued = adapter.apply_mutation(
        record_reduced,
        intent(
            record_reduced.revision,
            "capacity.record.unrelated",
            CreateCollectionMutation("Continue learning"),
        ),
        occurred_at=at(3),
        issued_id="collection.after-record-limit",
    )
    assert len(record_continued.records) == 199
    assert record_continued.collections[0].title == "Continue learning"

    collection_document = deepcopy(base)
    collection_template = deepcopy(collection_document["collections"][0])
    collection_document["collections"] = []
    for index in range(49):
        collection = deepcopy(collection_template)
        collection["collection_id"] = f"collection.{index:03d}"
        collection["title"] = f"Collection {index}"
        collection["member_record_ids"] = []
        collection_document["collections"].append(collection)
    collection_workspace = parse(collection_document)
    collection_full = adapter.apply_mutation(
        collection_workspace,
        intent(
            collection_workspace.revision,
            "capacity.collection.accept",
            CreateCollectionMutation("Fiftieth"),
        ),
        occurred_at=at(4),
        issued_id="collection.049",
    )
    with pytest.raises(PersonalWorkspaceContractFailure) as collection_failure:
        adapter.apply_mutation(
            collection_full,
            intent(
                collection_full.revision,
                "capacity.collection.refuse",
                CreateCollectionMutation("Too many"),
            ),
            occurred_at=at(5),
            issued_id="collection.050",
        )
    assert collection_failure.value.code == (
        "personal_workspace.contract.collection_limit"
    )
    assert adapter.query_workspace(collection_full, WorkspaceQuery(limit=2)).records
    assert (
        adapter.export_workspace(collection_full, generated_at=at(5)).workspace
        == collection_full
    )
    collection_reduced = adapter.apply_mutation(
        collection_full,
        intent(
            collection_full.revision,
            "capacity.collection.remove",
            RemoveCollectionMutation("collection.000"),
        ),
        occurred_at=at(6),
    )
    collection_continued = adapter.apply_mutation(
        collection_reduced,
        intent(
            collection_reduced.revision,
            "capacity.collection.unrelated",
            UpdateNoteMutation("note.one", "Still available", "Continue safely."),
        ),
        occurred_at=at(7),
    )
    assert len(collection_continued.collections) == 49
    assert collection_continued.records[0].title == "Still available"

    member_document = deepcopy(base)
    member_document["records"] = []
    for index in range(101):
        record = deepcopy(bookmark_template)
        record["record_id"] = f"bookmark.{index:03d}"
        member_document["records"].append(record)
    member_document["collections"][0]["member_record_ids"] = []
    member_workspace = parse(member_document)
    first_hundred = tuple(f"bookmark.{index:03d}" for index in range(100))
    member_full = adapter.apply_mutation(
        member_workspace,
        intent(
            member_workspace.revision,
            "capacity.members.accept",
            SetCollectionMembersMutation(
                "collection.foundations",
                first_hundred,
            ),
        ),
        occurred_at=at(8),
    )
    with pytest.raises(PersonalWorkspaceContractFailure) as member_failure:
        adapter.apply_mutation(
            member_full,
            intent(
                member_full.revision,
                "capacity.members.refuse",
                SetCollectionMembersMutation(
                    "collection.foundations",
                    first_hundred + ("bookmark.100",),
                ),
            ),
            occurred_at=at(9),
        )
    assert member_failure.value.code == (
        "personal_workspace.contract.collection_member_limit"
    )
    assert adapter.query_workspace(member_full, WorkspaceQuery(limit=3)).records
    assert adapter.export_workspace(member_full, generated_at=at(9)).workspace == member_full
    member_reduced = adapter.apply_mutation(
        member_full,
        intent(
            member_full.revision,
            "capacity.members.remove",
            RemoveRecordMutation("bookmark.000"),
        ),
        occurred_at=at(10),
    )
    member_continued = adapter.apply_mutation(
        member_reduced,
        intent(
            member_reduced.revision,
            "capacity.members.unrelated",
            RenameCollectionMutation("collection.foundations", "Review safely"),
        ),
        occurred_at=at(11),
    )
    assert len(member_continued.collections[0].member_record_ids) == 99
    assert member_continued.collections[0].title == "Review safely"


def test_recovery_restore_refuses_populated_target_before_process(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    bounded = tmp_path / "bounded"
    owned = bounded / "run"
    owned.mkdir(parents=True)
    backup = owned / "source.dump"
    backup.write_bytes(b"bounded-backup")
    invoked = False

    def run_process(*_args, **_kwargs):
        nonlocal invoked
        invoked = True
        raise AssertionError("restore process must not start")

    monkeypatch.setattr(runner, "ARTIFACT_ROOT", bounded)
    monkeypatch.setattr(runner, "application_table_count", lambda _dsn: 1)
    monkeypatch.setattr(runner.subprocess, "run", run_process)
    with pytest.raises(RuntimeError, match="populated; restore was refused"):
        runner.restore_logical_backup(
            container_name=f"{runner.RECOVERY_CONTAINER_PREFIX}test",
            postgres_dsn="postgresql://isolated-target",
            source=backup,
            owned_root=owned,
        )
    assert invoked is False


def test_recovery_restore_streams_only_to_empty_owned_target(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    bounded = tmp_path / "bounded"
    owned = bounded / "run"
    owned.mkdir(parents=True)
    backup = owned / "source.dump"
    backup.write_bytes(b"bounded-backup")
    observed: dict[str, Any] = {}

    class Completed:
        returncode = 0

    def run_process(command, **kwargs):
        observed["command"] = command
        observed["content"] = kwargs["stdin"].read()
        assert kwargs["stdout"] is runner.subprocess.DEVNULL
        assert kwargs["stderr"] is runner.subprocess.DEVNULL
        return Completed()

    monkeypatch.setattr(runner, "ARTIFACT_ROOT", bounded)
    monkeypatch.setattr(runner, "application_table_count", lambda _dsn: 0)
    monkeypatch.setattr(runner.subprocess, "run", run_process)
    runner.restore_logical_backup(
        container_name=f"{runner.RECOVERY_CONTAINER_PREFIX}test",
        postgres_dsn="postgresql://isolated-target",
        source=backup,
        owned_root=owned,
    )
    assert observed["content"] == b"bounded-backup"
    assert observed["command"][0:4] == [
        "docker",
        "exec",
        "--interactive",
        f"{runner.RECOVERY_CONTAINER_PREFIX}test",
    ]
    assert "--exit-on-error" in observed["command"]


def test_recovery_restore_refuses_outside_root_and_symlink_before_process(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    bounded = tmp_path / "bounded"
    owned = bounded / "run"
    owned.mkdir(parents=True)
    outside = tmp_path / "outside.dump"
    outside.write_bytes(b"outside")
    invoked = False

    def run_process(*_args, **_kwargs):
        nonlocal invoked
        invoked = True
        raise AssertionError("restore process must not start")

    monkeypatch.setattr(runner, "ARTIFACT_ROOT", bounded)
    monkeypatch.setattr(runner, "application_table_count", lambda _dsn: 0)
    monkeypatch.setattr(runner.subprocess, "run", run_process)
    with pytest.raises(RuntimeError, match="escaped its runner-owned root"):
        runner.restore_logical_backup(
            container_name=f"{runner.RECOVERY_CONTAINER_PREFIX}test",
            postgres_dsn="postgresql://isolated-target",
            source=outside,
            owned_root=owned,
        )

    linked = owned / "linked.dump"
    linked.write_bytes(b"linked")
    original_is_symlink = Path.is_symlink
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda path: path == linked or original_is_symlink(path),
    )
    with pytest.raises(RuntimeError, match="escaped its runner-owned root"):
        runner.restore_logical_backup(
            container_name=f"{runner.RECOVERY_CONTAINER_PREFIX}test",
            postgres_dsn="postgresql://isolated-target",
            source=linked,
            owned_root=owned,
        )
    assert invoked is False


def test_recovery_subprocess_failures_are_bounded_and_capture_is_removed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    bounded = tmp_path / "bounded"
    owned = bounded / "run"
    owned.mkdir(parents=True)
    capture = owned / "capture.dump"

    class Failed:
        returncode = 1

    monkeypatch.setattr(runner, "ARTIFACT_ROOT", bounded)
    monkeypatch.setattr(runner.subprocess, "run", lambda *_args, **_kwargs: Failed())
    with pytest.raises(RuntimeError, match="logical database capture failed"):
        runner.create_logical_backup(
            f"{runner.CONTAINER_PREFIX}source",
            capture,
        )
    assert not capture.exists()

    source = owned / "recovery-source.dump"
    source.write_bytes(b"bounded-backup")
    monkeypatch.setattr(runner, "application_table_count", lambda _dsn: 0)
    with pytest.raises(RuntimeError, match="logical database restore failed") as failure:
        runner.restore_logical_backup(
            container_name=f"{runner.RECOVERY_CONTAINER_PREFIX}target",
            postgres_dsn="postgresql://isolated-target",
            source=source,
            owned_root=owned,
        )
    assert "postgresql://" not in str(failure.value)
    assert str(source) not in str(failure.value)


def test_recovery_report_is_ordered_correlated_and_redacted() -> None:
    valid = {
        "backup_byte_count": 512,
        "backup_sha256": "a" * 64,
        "database_catalog_and_data_sha256": "b" * 64,
        "database_schema_count": 9,
        "data_file_count": 2,
        "data_sha256": "c" * 64,
        "empty_target_restored": True,
        "fresh_session_public_api": True,
        "old_session_denied": True,
        "phases": list(runner.RECOVERY_PHASES),
        "populated_target_refused": True,
        "qualified": True,
        "restored_sessions_revoked": 1,
        "source_unchanged": True,
    }
    assert runner.stable_recovery_report(valid) == valid

    reordered = deepcopy(valid)
    reordered["phases"][2:4] = reversed(reordered["phases"][2:4])
    with pytest.raises(RuntimeError, match="phase order"):
        runner.stable_recovery_report(reordered)

    uncorrelated = deepcopy(valid)
    uncorrelated["database_catalog_and_data_sha256"] = "not-a-digest"
    with pytest.raises(RuntimeError, match="invalid evidence"):
        runner.stable_recovery_report(uncorrelated)

    leaked = deepcopy(valid)
    leaked["postgres_dsn"] = "postgresql://private"
    with pytest.raises(RuntimeError, match="invalid shape"):
        runner.stable_recovery_report(leaked)


def test_restored_session_revocation_requires_active_session_and_old_token_denial(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Result:
        def __init__(self, row: tuple[int] | None) -> None:
            self._row = row

        def fetchone(self) -> tuple[int] | None:
            return self._row

    class Connection:
        def __init__(self, rows: list[tuple[int] | None]) -> None:
            self._rows = iter(rows)

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def execute(self, _query: str) -> Result:
            if "UPDATE" in _query:
                return Result(None)
            return Result(next(self._rows))

    monkeypatch.setattr(
        runner.psycopg,
        "connect",
        lambda _dsn: Connection([(0,), (0,)]),
    )
    with pytest.raises(RuntimeError, match="could not be proven"):
        runner.revoke_restored_sessions("postgresql://isolated-target")

    denial = {
        "error_version": "1.0",
        "code": "unauthorized",
        "message": "A valid learner session is required.",
        "correlation_id": "11111111-1111-4111-8111-111111111111",
    }
    monkeypatch.setattr(
        runner,
        "_request_json_read_status",
        lambda *_args, **_kwargs: (401, denial),
    )
    runner.assert_restored_session_denied(opener=object(), origin="http://127.0.0.1")

    leaked = deepcopy(denial)
    leaked["message"] = "A valid learner session is required. workspace_id"
    monkeypatch.setattr(
        runner,
        "_request_json_read_status",
        lambda *_args, **_kwargs: (401, leaked),
    )
    with pytest.raises(RuntimeError, match="not denied safely"):
        runner.assert_restored_session_denied(
            opener=object(),
            origin="http://127.0.0.1",
        )


def test_recovery_data_root_copy_preserves_unicode_bytes_and_order_independence(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    bounded = tmp_path / "bounded"
    source = bounded / "source"
    target = bounded / "target"
    (source / "nested").mkdir(parents=True)
    (source / "Σ.txt").write_text("Café", encoding="utf-8")
    (source / "nested" / "data.bin").write_bytes(b"\x00\x01\xff")
    monkeypatch.setattr(runner, "ARTIFACT_ROOT", bounded)

    copied = runner.copy_bounded_data_root(source, target)

    assert copied == runner.bounded_file_tree_fingerprint(source)
    assert copied == runner.bounded_file_tree_fingerprint(target)
    assert copied["file_count"] == 2
    assert copied["byte_count"] == len("Café".encode("utf-8")) + 3


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


def test_cleanup_removes_recovery_target_before_source_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        runner,
        "stop_application",
        lambda _target: calls.append("application"),
    )
    monkeypatch.setattr(
        runner,
        "remove_container",
        lambda target: calls.append(str(target)),
    )
    monkeypatch.setattr(
        runner,
        "remove_data_root",
        lambda _target: calls.append("temporary data"),
    )

    failures = runner.cleanup_qualification(
        application=object(),
        container_name=f"{runner.CONTAINER_PREFIX}source",
        recovery_container_name=f"{runner.RECOVERY_CONTAINER_PREFIX}target",
        data_root=Path("bounded-data"),
    )

    assert failures == ()
    assert calls == [
        "application",
        f"{runner.RECOVERY_CONTAINER_PREFIX}target",
        f"{runner.CONTAINER_PREFIX}source",
        "temporary data",
    ]


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


def learner_preference_profile(
    revision: int = 5,
    *,
    interest_label: str = "Index funds Σ",
) -> dict[str, Any]:
    document: dict[str, Any] = {
        "schema_version": "1.0.0",
        "profile_id": "preference.qualification",
        "learner_id": "11111111-1111-4111-8111-111111111111",
        "revision": revision,
        "goals": [
            {
                "goal_id": "goal.qualification",
                "title": "Compare risk Café",
                "detail": "Keep assumptions visible.",
                "archived": False,
                "created_at": "2026-10-17T18:00:00Z",
                "updated_at": "2026-10-17T18:00:01Z",
            }
        ],
        "experience": [
            {
                "experience_id": "experience.qualification",
                "subject": "Portfolio comparison",
                "level": "new",
                "detail": None,
                "created_at": "2026-10-17T18:00:01Z",
                "updated_at": "2026-10-17T18:00:01Z",
            }
        ],
        "interests": [
            {
                "interest_id": "interest.qualification",
                "label": interest_label,
                "created_at": "2026-10-17T18:00:02Z",
                "updated_at": "2026-10-17T18:00:02Z",
            }
        ],
        "created_at": "2026-10-17T18:00:00Z",
        "updated_at": "2026-10-17T18:00:02Z",
    }
    document["profile_digest"] = runner._canonical_sha256(document)
    return document


def learner_preference_history(
    profile: dict[str, Any],
) -> dict[str, Any]:
    operations = (
        ("reset_profile", "profile", profile["profile_id"]),
        ("create_goal", "goal", "goal.qualification"),
        ("create_experience", "experience", "experience.qualification"),
        ("create_interest", "interest", "interest.qualification"),
    )
    changes = [
        {
            "schema_version": "1.0.0",
            "revision": revision,
            "operation": operation,
            "object_kind": kind,
            "object_id": object_id,
            "occurred_at": f"2026-10-17T18:00:0{revision - 1}Z",
            "resulting_profile_digest": (
                profile["profile_digest"] if revision == profile["revision"] else "a" * 64
            ),
        }
        for revision, (operation, kind, object_id) in zip(
            range(2, profile["revision"] + 1),
            operations,
            strict=True,
        )
    ]
    return {
        "schema_version": "1.0.0",
        "profile_id": profile["profile_id"],
        "current_revision": profile["revision"],
        "changes": changes,
    }


def learner_preference_capture() -> dict[str, Any]:
    profile = learner_preference_profile()
    history = learner_preference_history(profile)
    exact_request = {
        "schema_version": "1.0.0",
        "idempotency_key": "11111111-1111-4111-8111-111111111114",
        "expected_revision": 4,
        "mutation": {"operation": "create_interest", "label": "Index funds Σ"},
    }
    race_revision = profile["revision"]
    return {
        "schema_version": "1.0.0",
        "profile": profile,
        "history": history,
        "export": {
            "schema_version": "1.0.0",
            "purpose": "A portable copy of the learning preferences you entered.",
            "limitations": ["These statements are not evidence of competency."],
            "exported_at": "2026-10-17T18:00:05Z",
            "profile": profile,
            "history": history,
        },
        "exact_replay_request": exact_request,
        "exact_replay_response": profile,
        "races": {
            "same_key_same_payload": {
                "requests": [
                    {
                        "schema_version": "1.0.0",
                        "idempotency_key": "11111111-1111-4111-8111-111111111115",
                        "expected_revision": race_revision,
                        "mutation": {"operation": "create_interest", "label": "Replay race"},
                    }
                    for _ in range(2)
                ],
                "expected": ["accepted", "accepted"],
            },
            "same_key_changed_payload": {
                "requests": [
                    {
                        "schema_version": "1.0.0",
                        "idempotency_key": "11111111-1111-4111-8111-111111111116",
                        "expected_revision": race_revision + 1,
                        "mutation": {"operation": "create_interest", "label": label},
                    }
                    for label in ("Conflict A", "Conflict B")
                ],
                "expected": ["accepted", "conflict"],
            },
            "different_key_same_revision": {
                "requests": [
                    {
                        "schema_version": "1.0.0",
                        "idempotency_key": key,
                        "expected_revision": race_revision + 2,
                        "mutation": {"operation": "create_interest", "label": label},
                    }
                    for key, label in (
                        ("11111111-1111-4111-8111-111111111117", "Stale A"),
                        ("11111111-1111-4111-8111-111111111118", "Stale B"),
                    )
                ],
                "expected": ["accepted", "stale"],
            },
        },
        "expected": {
            "final_goal": "Compare risk Café",
            "final_experience": "Portfolio comparison",
            "final_interest": "Index funds Σ",
            "reset_recorded": True,
            "populated_export_profile_revision": 1,
        },
    }


def test_learner_preference_race_clients_share_one_issued_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bootstrap_calls: list[str] = []

    class FakeOpener:
        def __init__(self, processor: object) -> None:
            self.cookies = processor.cookiejar

    def build_opener(processor: object) -> FakeOpener:
        return FakeOpener(processor)

    def bootstrap(opener: FakeOpener, *, origin: str, path: str, **_kwargs):
        bootstrap_calls.append(f"{origin}{path}")
        opener.cookies.set_cookie(
            runner.http.cookiejar.Cookie(
                version=0,
                name="financial_ai_academy_session",
                value="a" * 43,
                port=None,
                port_specified=False,
                domain="127.0.0.1",
                domain_specified=False,
                domain_initial_dot=False,
                path="/",
                path_specified=True,
                secure=False,
                expires=None,
                discard=True,
                comment=None,
                comment_url=None,
                rest={},
                rfc2109=False,
            )
        )
        return {"status": "ready"}

    monkeypatch.setattr(runner.urllib.request, "build_opener", build_opener)
    monkeypatch.setattr(runner, "_request_json", bootstrap)

    clients = runner.open_learner_preference_sessions(
        "http://127.0.0.1:8123",
        2,
    )

    assert bootstrap_calls == [
        "http://127.0.0.1:8123/api/v1/session/single-profile"
    ]
    assert clients[0] is not clients[1]
    assert clients[0].cookies is not clients[1].cookies
    assert [cookie.value for cookie in clients[0].cookies] == ["a" * 43]
    assert [cookie.value for cookie in clients[1].cookies] == ["a" * 43]


def test_learner_preference_capture_is_closed_correlated_and_private(
    tmp_path: Path,
) -> None:
    capture = learner_preference_capture()
    path = tmp_path / "learner-preferences-capture.json"
    path.write_text(json.dumps(capture), encoding="utf-8")
    assert runner.load_learner_preference_capture(path, data_root=tmp_path) == capture

    changed = deepcopy(capture)
    changed["profile"]["extra"] = True
    path.write_text(json.dumps(changed), encoding="utf-8")
    with pytest.raises(RuntimeError, match="open or incomplete"):
        runner.load_learner_preference_capture(path, data_root=tmp_path)

    leaked = deepcopy(capture)
    leaked["expected"]["token"] = "private"
    path.write_text(json.dumps(leaked), encoding="utf-8")
    with pytest.raises(RuntimeError, match="private authority"):
        runner.load_learner_preference_capture(path, data_root=tmp_path)

    extra_expected = deepcopy(capture)
    extra_expected["expected"]["extra"] = True
    path.write_text(json.dumps(extra_expected), encoding="utf-8")
    with pytest.raises(RuntimeError, match="expected summary"):
        runner.load_learner_preference_capture(path, data_root=tmp_path)

    wrong_goal = deepcopy(capture)
    wrong_goal["expected"]["final_goal"] = "A goal that is not in the profile"
    path.write_text(json.dumps(wrong_goal), encoding="utf-8")
    with pytest.raises(RuntimeError, match="expected summary"):
        runner.load_learner_preference_capture(path, data_root=tmp_path)

    missing_reset = deepcopy(capture)
    missing_reset["expected"]["reset_recorded"] = False
    path.write_text(json.dumps(missing_reset), encoding="utf-8")
    with pytest.raises(RuntimeError, match="expected summary"):
        runner.load_learner_preference_capture(path, data_root=tmp_path)

    wrong_populated_revision = deepcopy(capture)
    wrong_populated_revision["expected"]["populated_export_profile_revision"] = 2
    path.write_text(json.dumps(wrong_populated_revision), encoding="utf-8")
    with pytest.raises(RuntimeError, match="expected summary"):
        runner.load_learner_preference_capture(path, data_root=tmp_path)

    bad_digest = deepcopy(capture)
    bad_digest["profile"]["profile_digest"] = "0" * 64
    path.write_text(json.dumps(bad_digest), encoding="utf-8")
    with pytest.raises(RuntimeError, match="digest"):
        runner.load_learner_preference_capture(path, data_root=tmp_path)


def test_learner_preference_profile_accepts_variable_wording_count_and_order() -> None:
    profile = learner_preference_profile()
    duplicate = deepcopy(profile["goals"][0])
    duplicate["goal_id"] = "goal.duplicate"
    profile["goals"].insert(0, duplicate)
    profile["profile_digest"] = runner._canonical_sha256(
        {key: value for key, value in profile.items() if key != "profile_digest"}
    )
    assert runner.stable_learner_preference_profile(profile) == profile

    changed_order = deepcopy(profile)
    changed_order["goals"].reverse()
    changed_order["profile_digest"] = runner._canonical_sha256(
        {key: value for key, value in changed_order.items() if key != "profile_digest"}
    )
    assert runner.stable_learner_preference_profile(changed_order) == changed_order


def _race_storage(profile: dict[str, Any], *, changes: int, mutations: int) -> dict[str, Any]:
    return {
        "profiles": [[
            profile["profile_id"],
            profile["learner_id"],
            profile["revision"],
            profile,
            profile["profile_digest"],
        ]],
        "changes": [["change", index] for index in range(changes)],
        "mutations": [["mutation", index] for index in range(mutations)],
    }


def test_learner_preference_race_matrix_requires_one_durable_change() -> None:
    before_profile = learner_preference_profile()
    accepted = learner_preference_profile(6, interest_label="Race replay result")
    before = _race_storage(before_profile, changes=4, mutations=4)
    after = _race_storage(accepted, changes=5, mutations=5)
    requests = learner_preference_capture()["races"]["same_key_same_payload"]["requests"]
    assert runner.assert_learner_preference_race_outcomes(
        name="same_key_same_payload",
        requests=requests,
        results=[(200, accepted), (200, deepcopy(accepted))],
        before_storage=before,
        after_storage=after,
    ) == accepted

    conflict_requests = learner_preference_capture()["races"]["same_key_changed_payload"]["requests"]
    denial = {
        "error_version": "1.0",
        "code": "immutable_conflict",
        "message": "The request key already names a different learning preference change.",
        "correlation_id": "22222222-2222-4222-8222-222222222222",
    }
    assert runner.assert_learner_preference_race_outcomes(
        name="same_key_changed_payload",
        requests=conflict_requests,
        results=[(200, accepted), (409, denial)],
        before_storage=before,
        after_storage=after,
    ) == accepted
    stale_denial = {**denial, "code": "stale_revision"}
    assert runner.assert_learner_preference_race_outcomes(
        name="same_key_changed_payload",
        requests=conflict_requests,
        results=[(200, accepted), (409, stale_denial)],
        before_storage=before,
        after_storage=after,
    ) == accepted

    duplicate = deepcopy(after)
    duplicate["changes"].append(["change", 5])
    with pytest.raises(RuntimeError, match="row count"):
        runner.assert_learner_preference_race_outcomes(
            name="same_key_same_payload",
            requests=requests,
            results=[(200, accepted), (200, accepted)],
            before_storage=before,
            after_storage=duplicate,
        )


def test_learner_preference_restart_requires_exact_profile_history_and_rows() -> None:
    capture = learner_preference_capture()
    profile = capture["profile"]
    history = capture["history"]
    accepted_profiles = [learner_preference_profile(revision) for revision in (2, 3, 4, 5)]
    storage = {
        "profiles": [[
            profile["profile_id"],
            profile["learner_id"],
            profile["revision"],
            profile,
            profile["profile_digest"],
        ]],
        "changes": [
            [
                profile["learner_id"],
                change["revision"],
                change,
                change["resulting_profile_digest"],
            ]
            for change in history["changes"]
        ],
        "mutations": [
            [
                profile["learner_id"],
                f"mutation.{index}",
                accepted_profile["revision"],
                accepted_profile,
            ]
            for index, accepted_profile in enumerate(accepted_profiles, start=2)
        ],
    }
    runner.assert_learner_preference_storage(storage, profile=profile, history=history)
    changed = deepcopy(storage)
    changed["profiles"][0][2] += 1
    with pytest.raises(RuntimeError, match="stored profile"):
        runner.assert_learner_preference_storage(changed, profile=profile, history=history)


def presentation_preference_profile(
    revision: int = 5,
    *,
    text_size: str = "default",
    text_spacing: str = "default",
    reading_width: str = "standard",
    motion: str = "system",
) -> dict[str, Any]:
    updated_minute, updated_second = divmod(revision, 60)
    document: dict[str, Any] = {
        "schema_version": "1.0.0",
        "profile_id": "presentation.qualification",
        "learner_id": "11111111-1111-4111-8111-111111111111",
        "revision": revision,
        "text_size": text_size,
        "text_spacing": text_spacing,
        "reading_width": reading_width,
        "motion": motion,
        "created_at": "2026-10-17T18:00:00Z",
        "updated_at": (
            f"2026-10-17T18:{updated_minute:02d}:{updated_second:02d}Z"
        ),
    }
    document["profile_digest"] = runner._canonical_sha256(document)
    return document


def presentation_preference_history(profile: dict[str, Any]) -> dict[str, Any]:
    changes = [
        {
            "schema_version": "1.0.0",
            "revision": revision,
            "operation": "reset_profile" if revision == profile["revision"] else "replace_preferences",
            "object_kind": "profile",
            "object_id": None,
            "occurred_at": (
                f"2026-10-17T18:{revision // 60:02d}:{revision % 60:02d}Z"
            ),
            "resulting_profile_digest": (
                profile["profile_digest"]
                if revision == profile["revision"]
                else presentation_preference_profile(revision)["profile_digest"]
            ),
        }
        for revision in range(
            max(2, profile["revision"] - 99), profile["revision"] + 1
        )
    ]
    return {
        "schema_version": "1.0.0",
        "profile_id": profile["profile_id"],
        "current_revision": profile["revision"],
        "changes": changes,
    }


def presentation_preference_capture() -> dict[str, Any]:
    profile = presentation_preference_profile()
    history = presentation_preference_history(profile)
    combinations = [
        {
            "text_size": text_size,
            "text_spacing": text_spacing,
            "reading_width": reading_width,
            "motion": motion,
        }
        for text_size in ("default", "larger")
        for text_spacing in ("default", "increased")
        for reading_width in ("standard", "focused")
        for motion in ("system", "reduce")
    ]
    exact_request = {
        "schema_version": "1.0.0",
        "idempotency_key": "11111111-1111-4111-8111-111111111124",
        "expected_revision": 4,
        "mutation": {"operation": "reset_profile"},
    }

    def replace(key: str, revision: int, settings: dict[str, str]) -> dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "idempotency_key": key,
            "expected_revision": revision,
            "mutation": {"operation": "replace_preferences", **settings},
        }

    primary = combinations[-1]
    return {
        "schema_version": "1.0.0",
        "profile": profile,
        "history": history,
        "export": {
            "schema_version": "1.0.0",
            "purpose": "A portable copy of explicit display choices.",
            "limitations": ["These choices are not medical or competency evidence."],
            "exported_at": "2026-10-17T18:00:06Z",
            "profile": profile,
            "history": history,
        },
        "exact_replay_request": exact_request,
        "exact_replay_response": profile,
        "races": {
            "same_key_same_payload": {
                "requests": [
                    replace("11111111-1111-4111-8111-111111111125", 5, primary)
                    for _ in range(2)
                ],
                "expected": ["accepted", "accepted"],
            },
            "same_key_changed_payload": {
                "requests": [
                    replace(
                        "11111111-1111-4111-8111-111111111126",
                        6,
                        {**primary, "text_size": text_size},
                    )
                    for text_size in ("default", "larger")
                ],
                "expected": ["accepted", "conflict"],
            },
            "different_key_same_revision": {
                "requests": [
                    replace(key, 7, {**primary, "reading_width": reading_width})
                    for key, reading_width in (
                        ("11111111-1111-4111-8111-111111111127", "standard"),
                        ("11111111-1111-4111-8111-111111111128", "focused"),
                    )
                ],
                "expected": ["accepted", "stale"],
            },
        },
        "expected": {
            "all_combinations": combinations,
            "populated_export_profile_revision": 4,
            "reset_recorded": True,
            "theme_after_reset": "dark",
        },
    }


def test_presentation_preference_capture_is_closed_complete_and_private(
    tmp_path: Path,
) -> None:
    capture = presentation_preference_capture()
    path = tmp_path / "presentation-preferences-capture.json"
    path.write_text(json.dumps(capture), encoding="utf-8")
    assert runner.load_presentation_preference_capture(path, data_root=tmp_path) == capture

    leaked = deepcopy(capture)
    leaked["expected"]["diagnosis"] = "private"
    path.write_text(json.dumps(leaked), encoding="utf-8")
    with pytest.raises(RuntimeError, match="private authority"):
        runner.load_presentation_preference_capture(path, data_root=tmp_path)

    missing_combination = deepcopy(capture)
    missing_combination["expected"]["all_combinations"].pop()
    path.write_text(json.dumps(missing_combination), encoding="utf-8")
    with pytest.raises(RuntimeError, match="expected summary"):
        runner.load_presentation_preference_capture(path, data_root=tmp_path)

    wrong_theme = deepcopy(capture)
    wrong_theme["expected"]["theme_after_reset"] = "system"
    path.write_text(json.dumps(wrong_theme), encoding="utf-8")
    with pytest.raises(RuntimeError, match="expected summary"):
        runner.load_presentation_preference_capture(path, data_root=tmp_path)

    bad_digest = deepcopy(capture)
    bad_digest["profile"]["profile_digest"] = "0" * 64
    path.write_text(json.dumps(bad_digest), encoding="utf-8")
    with pytest.raises(RuntimeError, match="digest"):
        runner.load_presentation_preference_capture(path, data_root=tmp_path)


def test_presentation_preference_profile_accepts_every_closed_combination() -> None:
    for settings in presentation_preference_capture()["expected"]["all_combinations"]:
        profile = presentation_preference_profile(**settings)
        assert runner.stable_presentation_preference_profile(profile) == profile


def _presentation_race_storage(
    profile: dict[str, Any],
    *,
    changes: int,
    mutations: int,
) -> dict[str, Any]:
    return {
        "profiles": [[
            profile["profile_id"],
            profile["learner_id"],
            profile["revision"],
            profile,
            profile["profile_digest"],
        ]],
        "changes": [["change", index] for index in range(changes)],
        "mutations": [["mutation", index] for index in range(mutations)],
    }


def test_presentation_preference_race_requires_one_durable_change() -> None:
    before_profile = presentation_preference_profile()
    accepted = presentation_preference_profile(
        6,
        text_size="larger",
        text_spacing="increased",
        reading_width="focused",
        motion="reduce",
    )
    before = _presentation_race_storage(before_profile, changes=4, mutations=4)
    after = _presentation_race_storage(accepted, changes=5, mutations=5)
    capture = presentation_preference_capture()
    requests = capture["races"]["same_key_same_payload"]["requests"]
    assert runner.assert_presentation_preference_race_outcomes(
        name="same_key_same_payload",
        requests=requests,
        results=[(200, accepted), (200, deepcopy(accepted))],
        before_storage=before,
        after_storage=after,
    ) == accepted

    denial = {
        "error_version": "1.0",
        "code": "immutable_conflict",
        "message": "The request key already names a different display change.",
        "correlation_id": "22222222-2222-4222-8222-222222222222",
    }
    conflict_requests = capture["races"]["same_key_changed_payload"]["requests"]
    assert runner.assert_presentation_preference_race_outcomes(
        name="same_key_changed_payload",
        requests=conflict_requests,
        results=[(200, accepted), (409, denial)],
        before_storage=before,
        after_storage=after,
    ) == accepted
    stale_denial = {**denial, "code": "stale_revision"}
    assert runner.assert_presentation_preference_race_outcomes(
        name="same_key_changed_payload",
        requests=conflict_requests,
        results=[(200, accepted), (409, stale_denial)],
        before_storage=before,
        after_storage=after,
    ) == accepted

    duplicate = deepcopy(after)
    duplicate["mutations"].append(["mutation", 5])
    with pytest.raises(RuntimeError, match="row count"):
        runner.assert_presentation_preference_race_outcomes(
            name="same_key_same_payload",
            requests=requests,
            results=[(200, accepted), (200, accepted)],
            before_storage=before,
            after_storage=duplicate,
        )


def test_presentation_preference_restart_requires_exact_rows() -> None:
    capture = presentation_preference_capture()
    profile = capture["profile"]
    history = capture["history"]
    accepted_profiles = [presentation_preference_profile(revision) for revision in range(2, 6)]
    storage = {
        "profiles": [[
            profile["profile_id"],
            profile["learner_id"],
            profile["revision"],
            profile,
            profile["profile_digest"],
        ]],
        "changes": [
            [profile["learner_id"], change["revision"], change, change["resulting_profile_digest"]]
            for change in history["changes"]
        ],
        "mutations": [
            [
                profile["learner_id"],
                (
                    capture["exact_replay_request"]["idempotency_key"]
                    if accepted["revision"] == profile["revision"]
                    else f"presentation.{index}"
                ),
                accepted["revision"],
                accepted,
            ]
            for index, accepted in enumerate(accepted_profiles, start=2)
        ],
    }
    runner.assert_presentation_preference_storage(
        storage,
        profile=profile,
        history=history,
        exact_replay_request=capture["exact_replay_request"],
        exact_replay_response=capture["exact_replay_response"],
    )
    changed = deepcopy(storage)
    changed["profiles"][0][2] += 1
    with pytest.raises(RuntimeError, match="stored profile"):
        runner.assert_presentation_preference_storage(changed, profile=profile, history=history)

    duplicate_revision = deepcopy(storage)
    duplicate_revision["mutations"][0][2] = 3
    duplicate_revision["mutations"][0][3] = deepcopy(
        duplicate_revision["mutations"][1][3]
    )
    with pytest.raises(RuntimeError, match="revision or key coverage"):
        runner.assert_presentation_preference_storage(
            duplicate_revision,
            profile=profile,
            history=history,
        )

    mismatched_history = deepcopy(storage)
    mismatched_history["changes"][0][2]["resulting_profile_digest"] = "b" * 64
    mismatched_history["changes"][0][3] = "b" * 64
    mismatched_history_document = deepcopy(history)
    mismatched_history_document["changes"][0]["resulting_profile_digest"] = "b" * 64
    with pytest.raises(RuntimeError, match="replay storage"):
        runner.assert_presentation_preference_storage(
            mismatched_history,
            profile=profile,
            history=mismatched_history_document,
        )

    duplicate_key = deepcopy(storage)
    duplicate_key["mutations"][1][1] = duplicate_key["mutations"][0][1]
    with pytest.raises(RuntimeError, match="revision or key coverage"):
        runner.assert_presentation_preference_storage(
            duplicate_key,
            profile=profile,
            history=history,
        )

    invalid_key = deepcopy(storage)
    invalid_key["mutations"][0][1] = "not valid/for replay"
    with pytest.raises(RuntimeError, match="revision or key coverage"):
        runner.assert_presentation_preference_storage(
            invalid_key,
            profile=profile,
            history=history,
        )

    missing_exact_replay = deepcopy(storage)
    missing_exact_replay["mutations"][-1][1] = "presentation.final"
    with pytest.raises(RuntimeError, match="exact replay row"):
        runner.assert_presentation_preference_storage(
            missing_exact_replay,
            profile=profile,
            history=history,
            exact_replay_request=capture["exact_replay_request"],
            exact_replay_response=capture["exact_replay_response"],
        )


@pytest.mark.parametrize(
    ("revision", "first_retained_revision"),
    ((101, 2), (102, 3)),
)
def test_presentation_preference_storage_accepts_bounded_history_window(
    revision: int,
    first_retained_revision: int,
) -> None:
    profile = presentation_preference_profile(revision)
    history = presentation_preference_history(profile)
    accepted_profiles = [
        presentation_preference_profile(accepted_revision)
        for accepted_revision in range(2, revision + 1)
    ]
    storage = {
        "profiles": [[
            profile["profile_id"],
            profile["learner_id"],
            profile["revision"],
            profile,
            profile["profile_digest"],
        ]],
        "changes": [
            [
                profile["learner_id"],
                change["revision"],
                change,
                change["resulting_profile_digest"],
            ]
            for change in history["changes"]
        ],
        "mutations": [
            [
                profile["learner_id"],
                f"presentation.boundary.{accepted['revision']}",
                accepted["revision"],
                accepted,
            ]
            for accepted in accepted_profiles
        ],
    }

    assert history["changes"][0]["revision"] == first_retained_revision
    assert len(history["changes"]) == 100
    runner.assert_presentation_preference_storage(
        storage,
        profile=profile,
        history=history,
    )
