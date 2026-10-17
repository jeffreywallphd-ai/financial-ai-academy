from __future__ import annotations

import asyncio
import base64
import copy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import os
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient

from financial_ai_academy.bootstrap.composition import build_application_services
from financial_ai_academy.bootstrap.settings import SingleProfileApplicationSettings
from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.hosts.api.generate_openapi import generate_bytes
from financial_ai_academy.modules.identity.public import LearnerContext
from financial_ai_academy.modules.content.public import AdmitLessonPackageRequest
from financial_ai_academy.modules.curriculum.public import (
    CreateLessonPlacementRequest,
    CreateProjectBriefPlacementRequest,
    CurriculumActivity,
    CurriculumActivityKind,
    CurriculumBranch,
    CurriculumBranchKind,
    CurriculumCompetency,
    CurriculumGraph,
    CurriculumObjective,
    CurriculumPresentationOrder,
    CurriculumRelationship,
    CurriculumRelationshipKind,
    LessonActivityReference,
    PublishCurriculumGraphRequest,
    curriculum_graph_digest,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileSecuritySettings,
)


ORIGIN = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parents[4]
OPENAPI = ROOT / "contracts/api/openapi.json"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
PROJECT_FIXTURE = (
    ROOT
    / "contracts/compatibility/lesson-package/v1/approved"
    / "intro-risk-return-project"
)
BRIEF_DIGEST = (
    "1f234681a4b9262dd49e01c82c8c6a12f6a64d13845bea6140708a7d16f061ff"
)


def _headers() -> dict[str, str]:
    return {"Origin": ORIGIN, "Sec-Fetch-Site": "same-origin"}


class _FixedIdentity:
    def __init__(
        self, learner_id: str, permissions: tuple[str, ...]
    ) -> None:
        self._learner_id = learner_id
        self._permissions = permissions

    def resolve_session(self, cookie_value: str | None) -> LearnerContext:
        assert cookie_value == "fixed-session"
        authenticated_at = datetime(2026, 10, 17, tzinfo=timezone.utc)
        return LearnerContext(
            actor_id=f"actor-{self._learner_id}",
            learner_id=self._learner_id,
            session_id="fixed-session",
            authenticated_at=authenticated_at,
            expires_at=authenticated_at + timedelta(hours=1),
            authentication_method="single_profile",
            permissions=self._permissions,
        )

    def health(self) -> bool:
        return True


def _graph(
    *, package_id: str, package_version: str, package_digest: str
) -> CurriculumGraph:
    activity_id = "activity-risk-return-project"
    graph = CurriculumGraph(
        schema_version="1.0.0",
        curriculum_id="financial-foundations-project-submission",
        curriculum_version="1.0.0",
        title="Financial foundations Project submission",
        summary="A bounded path from reviewed material to Project evidence.",
        publication_state="approved",
        published_at=datetime(2026, 10, 17, tzinfo=timezone.utc),
        source_references=(f"content:{package_id}@{package_version}",),
        objectives=(
            CurriculumObjective(
                "objective-apply-risk-return",
                "Apply risk and return ideas",
                "Use consistent criteria in an educational comparison.",
            ),
        ),
        competencies=(
            CurriculumCompetency(
                "competency-apply-risk-return",
                "Risk and return application",
                "Apply evidence without making an investment recommendation.",
            ),
        ),
        activities=(
            CurriculumActivity(
                activity_id,
                "Start the risk and return Project",
                CurriculumActivityKind.LESSON,
                LessonActivityReference(
                    "risk-return-project-source",
                    package_id,
                    package_version,
                    package_digest,
                ),
            ),
        ),
        branches=(
            CurriculumBranch(
                "branch-applied-project",
                "Applied Project",
                CurriculumBranchKind.REQUIRED,
                (activity_id,),
            ),
        ),
        relationships=(
            CurriculumRelationship(
                "relationship-project-objective",
                CurriculumRelationshipKind.OBJECTIVE_COMPETENCY,
                "objective-apply-risk-return",
                "competency-apply-risk-return",
            ),
            CurriculumRelationship(
                "relationship-project-develops",
                CurriculumRelationshipKind.ACTIVITY_DEVELOPS_COMPETENCY,
                activity_id,
                "competency-apply-risk-return",
            ),
        ),
        graph_digest="0" * 64,
        presentation_order=CurriculumPresentationOrder(
            objective_ids=("objective-apply-risk-return",),
            competency_ids=("competency-apply-risk-return",),
            activity_ids=(activity_id,),
            branch_ids=("branch-applied-project",),
        ),
    )
    return replace(graph, graph_digest=curriculum_graph_digest(graph))


def _submission(
    candidate: dict[str, object], submission_id: str
) -> dict[str, object]:
    project = candidate["project"]
    origin = candidate["origin"]
    milestones = candidate["milestones"]
    resources = candidate["resources"]
    assert isinstance(project, dict)
    assert isinstance(origin, dict)
    assert isinstance(milestones, list)
    assert isinstance(resources, list) and resources
    source = {
        key: (
            project
            if key in {"project_id", "snapshot_id", "snapshot_digest"}
            else origin
        )[key]
        for key in (
            "project_id",
            "snapshot_id",
            "snapshot_digest",
            "brief_id",
            "brief_version",
            "brief_digest",
            "placement_id",
            "placement_version",
            "placement_digest",
        )
    }
    return {
        "schema_version": "1.0.0",
        "submission_id": submission_id,
        "source": source,
        "policy_id": candidate["policy_id"],
        "policy_version": candidate["policy_version"],
        "milestone_evidence": [
            {
                "milestone_id": milestone["milestone_id"],
                "resources": (
                    resources
                    if index == 0
                    else [resources[index % len(resources)]]
                ),
            }
            for index, milestone in enumerate(milestones)
        ],
    }


def test_project_submission_openapi_snapshot_is_current() -> None:
    assert OPENAPI.read_bytes() == generate_bytes()


@pytest.mark.postgres
@pytest.mark.skipif(
    POSTGRES_DSN is None,
    reason="FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN is not configured",
)
def test_headless_project_submission_refusal_replay_and_history(
    tmp_path: Path,
) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as connection:
        for schema in (
            "project",
            "identity",
            "audit",
            "learner_model",
            "assessment",
            "curriculum",
            "content",
            "platform",
        ):
            connection.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
    settings = SingleProfileApplicationSettings(
        postgres_dsn=POSTGRES_DSN,
        object_storage_root=tmp_path / "objects",
        lesson_schema_dir=ROOT / "contracts/learning/lesson-package/v1",
        migrations_dir=ROOT / "backend/migrations",
        security=SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin=ORIGIN,
            allowed_hosts=("127.0.0.1:8000", "testserver"),
            secure_cookie=False,
        ),
    )
    services = build_application_services(settings, apply_migrations=True)
    accepted = services.content.admit_lesson_package(
        AdmitLessonPackageRequest(PROJECT_FIXTURE)
    )
    services.curriculum.create_lesson_placement(
        CreateLessonPlacementRequest(
            placement_id="risk-return-project-source",
            package_id=accepted.package_id,
            package_version=accepted.package_version,
            package_digest=accepted.package_digest,
        )
    )
    graph = _graph(
        package_id=accepted.package_id,
        package_version=accepted.package_version,
        package_digest=accepted.package_digest,
    )
    services.curriculum.publish_curriculum_graph(PublishCurriculumGraphRequest(graph))
    services.curriculum.create_project_brief_placement(
        CreateProjectBriefPlacementRequest(
            placement_id="risk-return-project-primary",
            placement_version="1.0.0",
            curriculum_id=graph.curriculum_id,
            curriculum_version=graph.curriculum_version,
            curriculum_digest=graph.graph_digest,
            activity_id="activity-risk-return-project",
            package_id=accepted.package_id,
            package_version=accepted.package_version,
            package_digest=accepted.package_digest,
            brief_id="risk-return-project",
            brief_version="1.0.0",
            brief_digest=BRIEF_DIGEST,
            project_brief_schema_version="1.0.0",
        )
    )
    api_services = ApiServices(
        identity=services.identity,
        curriculum=services.curriculum,
        request_policy=services.request_policy,
        assessment=services.assessment,
        learner_model=services.learner_model,
        adaptation=services.adaptation,
        audit=services.audit,
        project=services.project,
    )
    app = create_app(api_services)
    with TestClient(
        app,
        base_url=ORIGIN,
        backend_options={"loop_factory": asyncio.SelectorEventLoop},
    ) as subject:
        unauthorized = subject.get(
            "/api/v1/projects/project-guess/submissions"
        )
        bootstrapped = subject.post(
            "/api/v1/session/single-profile",
            headers=_headers(),
            json={"limitation_acknowledged": True},
        )
        option = subject.get(
            "/api/v1/projects/start-options/risk-return-project-primary"
        ).json()
        created = subject.post(
            "/api/v1/projects",
            headers=_headers(),
            json={
                "schema_version": "1.0.0",
                "idempotency_key": "submission-project",
                "title": "Evidence comparison",
                "charter": "Compare educational evidence without advice.",
                "origin": option["origin"],
            },
        )
        project_id = created.json()["project_id"]
        workspace = subject.post(
            f"/api/v1/projects/{project_id}/workspace/mutations",
            headers=_headers(),
            json={
                "schema_version": "1.0.0",
                "idempotency_key": "submission-note",
                "expected_workspace_revision": 1,
                "mutation": {
                    "operation": "add_note",
                    "title": "Résumé of comparison limits",
                    "body": "Evidence for both milestones; no recommendation.",
                },
            },
        )
        reference = subject.post(
            f"/api/v1/projects/{project_id}/workspace/mutations",
            headers=_headers(),
            json={
                "schema_version": "1.0.0",
                "idempotency_key": "submission-source",
                "expected_workspace_revision": workspace.json()[
                    "workspace_revision"
                ],
                "mutation": {
                    "operation": "add_reference",
                    "title": "Reviewed educational source",
                    "url": "https://example.edu/evidence",
                    "source_name": "Example University",
                    "source_version": "2026.10",
                    "source_digest": "d" * 64,
                },
            },
        )
        artifact_content = b"scenario,value\nbase,1\n"
        artifact = subject.post(
            f"/api/v1/projects/{project_id}/artifacts",
            headers=_headers(),
            json={
                "intent": {
                    "schema_version": "1.0.0",
                    "idempotency_key": "submission-artifact",
                    "expected_workspace_revision": reference.json()[
                        "workspace_revision"
                    ],
                    "mutation": {
                        "operation": "add_artifact",
                        "artifact": {
                            "artifact_kind": "dataset",
                            "logical_path": "data/scenario.csv",
                            "media_type": "text/csv",
                            "inspection_mode": "plain_text",
                            "byte_count": len(artifact_content),
                            "content_digest": hashlib.sha256(
                                artifact_content
                            ).hexdigest(),
                            "provenance": {
                                "source_type": "learner_created",
                                "source_title": "Submission scenario",
                            },
                            "assumptions": [],
                        },
                    },
                },
                "content_base64": base64.b64encode(artifact_content).decode(
                    "ascii"
                ),
            },
        )
        snapshot = subject.post(
            f"/api/v1/projects/{project_id}/snapshots",
            headers=_headers(),
            json={
                "schema_version": "1.0.0",
                "idempotency_key": "submission-snapshot",
                "expected_project_revision": 1,
                "expected_workspace_revision": artifact.json()[
                    "workspace_revision"
                ],
            },
        )
        snapshot_id = snapshot.json()["snapshot_id"]
        candidate_response = subject.get(
            f"/api/v1/projects/{project_id}/snapshots/{snapshot_id}/submission-candidate"
        )
        candidate = candidate_response.json()
        empty_completion = subject.get(
            f"/api/v1/projects/{project_id}/completion"
        )
        valid = _submission(candidate, "project-submission-1")
        refused_document = {
            **valid,
            "submission_id": "project-submission-refused",
            "milestone_evidence": valid["milestone_evidence"][:-1],
        }
        refused = subject.post(
            f"/api/v1/projects/{project_id}/snapshots/{snapshot_id}/submissions",
            headers=_headers(),
            json=refused_document,
        )
        selected_learner = subject.post(
            f"/api/v1/projects/{project_id}/snapshots/{snapshot_id}/submissions",
            headers=_headers(),
            json={**valid, "learner_id": "another-learner"},
        )
        query_denied = subject.get(
            f"/api/v1/projects/{project_id}/submissions?learner_id=another-learner"
        )
        mismatch = subject.post(
            f"/api/v1/projects/{project_id}/snapshots/another-snapshot/submissions",
            headers=_headers(),
            json=valid,
        )
        invalid_selectors = []
        for suffix, selector in (
            ("naive", {"resource_as_of": "2026-10-17T04:00:00"}),
            ("missing", {}),
            (
                "both",
                {
                    "resource_version": "1.0.0",
                    "resource_as_of": "2026-10-17T04:00:00Z",
                },
            ),
        ):
            invalid = copy.deepcopy(valid)
            invalid["submission_id"] = f"invalid-selector-{suffix}"
            invalid["milestone_evidence"][0]["resources"] = [
                {
                    "resource_kind": "domain_resource",
                    "resource_id": "domain-example",
                    "record_digest": "e" * 64,
                    "owner_reference_digest": "f" * 64,
                    **selector,
                }
            ]
            invalid_selectors.append(
                subject.post(
                    f"/api/v1/projects/{project_id}/snapshots/"
                    f"{snapshot_id}/submissions",
                    headers=_headers(),
                    json=invalid,
                )
            )
        with psycopg.connect(POSTGRES_DSN) as connection:
            pre_accept_submission_rows = connection.execute(
                "SELECT count(*) FROM assessment.project_submissions"
            ).fetchone()
        accepted_response = subject.post(
            f"/api/v1/projects/{project_id}/snapshots/{snapshot_id}/submissions",
            headers=_headers(),
            json=valid,
        )
        replay = subject.post(
            f"/api/v1/projects/{project_id}/snapshots/{snapshot_id}/submissions",
            headers=_headers(),
            json=valid,
        )
        exact = subject.get(
            f"/api/v1/projects/{project_id}/submissions/project-submission-1"
        )
        history = subject.get(f"/api/v1/projects/{project_id}/submissions")
        completion = subject.get(f"/api/v1/projects/{project_id}/completion")
        completion_query_denied = subject.get(
            f"/api/v1/projects/{project_id}/completion?learner_id=another-learner"
        )

        independent = subject.post(
            "/api/v1/projects",
            headers=_headers(),
            json={
                "schema_version": "1.0.0",
                "idempotency_key": "independent-submission-project",
                "title": "Independent evidence",
                "charter": "Keep this Project outside a learning placement.",
                "origin": {"origin_type": "independent"},
            },
        )
        independent_id = independent.json()["project_id"]
        independent_workspace = subject.post(
            f"/api/v1/projects/{independent_id}/workspace/mutations",
            headers=_headers(),
            json={
                "schema_version": "1.0.0",
                "idempotency_key": "independent-note",
                "expected_workspace_revision": 1,
                "mutation": {
                    "operation": "add_note",
                    "title": "Independent note",
                    "body": "This is not learning evidence.",
                },
            },
        )
        independent_snapshot = subject.post(
            f"/api/v1/projects/{independent_id}/snapshots",
            headers=_headers(),
            json={
                "schema_version": "1.0.0",
                "idempotency_key": "independent-snapshot",
                "expected_project_revision": 1,
                "expected_workspace_revision": independent_workspace.json()[
                    "workspace_revision"
                ],
            },
        )
        independent_denied = subject.get(
            f"/api/v1/projects/{independent_id}/snapshots/"
            f"{independent_snapshot.json()['snapshot_id']}/submission-candidate"
        )

        cookie_name = services.request_policy.settings.cookie_name
        with TestClient(
            create_app(
                replace(
                    api_services,
                    identity=_FixedIdentity(
                        created.json()["learner_id"], ("project.read",)
                    ),
                )
            ),
            base_url=ORIGIN,
            backend_options={"loop_factory": asyncio.SelectorEventLoop},
        ) as read_only:
            read_only.cookies.set(cookie_name, "fixed-session")
            readable = read_only.get(
                f"/api/v1/projects/{project_id}/submissions/project-submission-1"
            )
            readable_completion = read_only.get(
                f"/api/v1/projects/{project_id}/completion"
            )
            forbidden_submit = read_only.post(
                f"/api/v1/projects/{project_id}/snapshots/"
                f"{snapshot_id}/submissions",
                headers=_headers(),
                json=valid,
            )

        with TestClient(
            create_app(
                replace(
                    api_services,
                    identity=_FixedIdentity(
                        "22222222-2222-4222-8222-222222222222",
                        ("project.read", "project.write"),
                    ),
                )
            ),
            base_url=ORIGIN,
            backend_options={"loop_factory": asyncio.SelectorEventLoop},
        ) as another_learner:
            another_learner.cookies.set(cookie_name, "fixed-session")
            cross_learner_candidate = another_learner.get(
                f"/api/v1/projects/{project_id}/snapshots/"
                f"{snapshot_id}/submission-candidate"
            )
            cross_learner_exact = another_learner.get(
                f"/api/v1/projects/{project_id}/submissions/"
                "project-submission-1"
            )
            cross_learner_history = another_learner.get(
                f"/api/v1/projects/{project_id}/submissions"
            )
            cross_learner_completion = another_learner.get(
                f"/api/v1/projects/{project_id}/completion"
            )
            cross_learner_submit = another_learner.post(
                f"/api/v1/projects/{project_id}/snapshots/"
                f"{snapshot_id}/submissions",
                headers=_headers(),
                json=valid,
            )

    assert bootstrapped.status_code == 201
    assert unauthorized.status_code == 401
    assert candidate_response.status_code == 200, candidate_response.text
    assert empty_completion.status_code == 200, empty_completion.text
    assert empty_completion.json()["completed"] is False
    assert empty_completion.json()["completion_meaning"] == "not_completed"
    assert empty_completion.json()["history"] == []
    assert reference.status_code == artifact.status_code == 200
    assert candidate["milestones"][0]["title"]
    assert candidate["resources"][0]["resource_kind"] == "note"
    assert {resource["resource_kind"] for resource in candidate["resources"]} == {
        "note",
        "source",
        "artifact",
    }
    assert {"body", "path", "object_key", "content"}.isdisjoint(
        candidate["resources"][0]
    )
    assert refused.status_code == 200, refused.text
    assert refused.json()["validation"]["status"] == "refused"
    assert refused.json()["validation"]["issues"][0]["code"] == (
        "assessment.project.missing_milestone"
    )
    assert refused.json()["evidence"] is None
    assert selected_learner.status_code == 400
    assert query_denied.status_code == 400
    assert mismatch.status_code == 409
    assert [response.status_code for response in invalid_selectors] == [
        400,
        400,
        400,
    ]
    assert all(
        response.json()["code"] == "invalid_request"
        for response in invalid_selectors
    )
    assert pre_accept_submission_rows == (0,)
    assert accepted_response.status_code == replay.status_code == 200
    assert accepted_response.json() == replay.json()
    assert accepted_response.json()["validation"]["status"] == "accepted"
    assert exact.json() == accepted_response.json()["evidence"]
    assert history.status_code == exact.status_code == 200
    assert completion.status_code == 200, completion.text
    assert completion_query_denied.status_code == 400
    assert completion.json()["project_id"] == project_id
    assert completion.json()["completed"] is True
    assert completion.json()["completion_meaning"] == (
        "bounded_project_activity_completed"
    )
    assert completion.json()["history"] == [
        {
            "event_id": completion.json()["history"][0]["event_id"],
            "evidence_id": exact.json()["evidence_id"],
            "submission_id": exact.json()["submission_id"],
            "snapshot_id": exact.json()["snapshot_id"],
            "snapshot_digest": exact.json()["snapshot_digest"],
            "brief_id": exact.json()["brief_id"],
            "brief_version": exact.json()["brief_version"],
            "brief_digest": exact.json()["brief_digest"],
            "placement_id": exact.json()["placement_id"],
            "placement_version": exact.json()["placement_version"],
            "placement_digest": exact.json()["placement_digest"],
            "policy_id": exact.json()["policy_id"],
            "policy_version": exact.json()["policy_version"],
            "milestone_ids": exact.json()["milestone_ids"],
            "request_fingerprint": exact.json()["request_fingerprint"],
            "occurrence": exact.json()["occurrence"],
            "accepted_sequence": exact.json()["accepted_sequence"],
            "submitted_at": exact.json()["submitted_at"],
            "occurred_at": completion.json()["history"][0]["occurred_at"],
        }
    ]
    assert "learner_id" not in completion.text
    assert history.json()["items"] == [
        {
            key: value
            for key, value in exact.json().items()
            if key
            in {
                "evidence_id",
                "submission_id",
                "snapshot_id",
                "snapshot_digest",
                "request_fingerprint",
                "occurrence",
                "submitted_at",
            }
        }
    ]
    assert "learner_id" not in history.text
    assert independent_denied.status_code == 404
    assert readable.status_code == 200
    assert readable_completion.status_code == 200
    assert forbidden_submit.status_code == 403
    assert cross_learner_candidate.status_code == 404
    assert cross_learner_exact.status_code == 404
    assert cross_learner_history.status_code == 404
    assert cross_learner_completion.status_code == 404
    assert cross_learner_submit.status_code == 404
    assert all(
        response.json()["code"] == "not_found"
        for response in (
            cross_learner_candidate,
            cross_learner_exact,
            cross_learner_history,
            cross_learner_completion,
            cross_learner_submit,
        )
    )
    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute(
            "SELECT count(*) FROM assessment.project_submissions"
        ).fetchone() == (1,)
        assert connection.execute(
            "SELECT count(*) FROM assessment.project_outbox "
            "WHERE event_type = 'assessment.project.completed'"
        ).fetchone() == (1,)
        assert connection.execute(
            "SELECT count(*) FROM audit.project_completion_records"
        ).fetchone() == (1,)
        assert connection.execute(
            "SELECT count(*) FROM learner_model.project_completion_history"
        ).fetchone() == (1,)
