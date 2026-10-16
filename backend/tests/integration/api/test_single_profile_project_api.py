from __future__ import annotations

import asyncio
import base64
import hashlib
import os
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient

from financial_ai_academy.bootstrap.composition import build_application_services
from financial_ai_academy.bootstrap.settings import SingleProfileApplicationSettings
from financial_ai_academy.hosts.api.app import ApiServices, create_app
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
from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    LearnerContext,
)
from financial_ai_academy.modules.project.domain.project import (
    LearningProjectOrigin,
    ProjectShell,
)
from financial_ai_academy.modules.project.public import (
    CreateProjectRequest,
    IndependentProjectOrigin,
    LearningProjectStartOption,
    ListLearningProjectStartOptionsRequest,
    ListProjectsRequest,
    OpenProjectRequest,
    ProjectError,
    ProjectErrorCode,
    ResolveLearningProjectStartOptionRequest,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)


ORIGIN = "http://127.0.0.1:8000"
COOKIE = "financial_ai_academy_session"
NOW = datetime(2026, 10, 16, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[4]
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
PROJECT_FIXTURE = (
    ROOT
    / "contracts/compatibility/lesson-package/v1/approved"
    / "intro-risk-return-project"
)


def project_curriculum_graph(
    *, package_id: str, package_version: str, package_digest: str
) -> CurriculumGraph:
    activity_id = "activity-risk-return-project"
    graph = CurriculumGraph(
        schema_version="1.0.0",
        curriculum_id="financial-foundations",
        curriculum_version="1.0.0",
        title="Financial foundations",
        summary="A bounded path from an approved lesson to an applied Project.",
        publication_state="approved",
        published_at=NOW,
        source_references=(f"content:{package_id}@{package_version}",),
        objectives=(
            CurriculumObjective(
                "objective-apply-risk-return",
                "Apply risk and return ideas",
                "Use the lesson concepts in an educational comparison.",
            ),
        ),
        competencies=(
            CurriculumCompetency(
                "competency-apply-risk-return",
                "Risk and return application",
                "Apply evidence without making a recommendation.",
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


class Identity:
    def resolve_session(self, cookie_value: str | None) -> LearnerContext:
        if cookie_value not in {"session-a", "session-b", "read-only"}:
            raise IdentityError(
                IdentityErrorCode.UNAUTHORIZED,
                "A valid learner session is required.",
            )
        permissions = (
            ("project.read",)
            if cookie_value == "read-only"
            else ("project.create", "project.read", "project.write")
        )
        learner = "learner-b" if cookie_value == "session-b" else "learner-a"
        return LearnerContext(
            actor_id=f"actor-{learner}",
            learner_id=learner,
            session_id=f"id-{cookie_value}",
            authenticated_at=NOW,
            expires_at=NOW + timedelta(hours=1),
            authentication_method="single_profile",
            permissions=permissions,
        )

    def health(self) -> bool:
        return True


class Projects:
    def __init__(self) -> None:
        self.rows: dict[str, ProjectShell] = {}

    def create_project(self, request: CreateProjectRequest) -> ProjectShell:
        existing = next(
            (
                shell
                for shell in self.rows.values()
                if shell.learner_id == request.learner_id
                and shell.title == request.intent.title
            ),
            None,
        )
        if existing:
            return existing
        project_id = f"project-{len(self.rows) + 1}"
        shell = ProjectShell(
            "1.0.0",
            project_id,
            request.learner_id,
            request.intent.title,
            request.intent.charter,
            request.intent.origin,
            "active",
            1,
            NOW,
            NOW,
        )
        self.rows[project_id] = shell
        return shell

    def list_projects(
        self, request: ListProjectsRequest
    ) -> tuple[ProjectShell, ...]:
        return tuple(
            shell
            for shell in self.rows.values()
            if shell.learner_id == request.learner_id
        )

    def open_project(self, request: OpenProjectRequest) -> ProjectShell:
        shell = self.rows.get(request.project_id)
        if shell is None or shell.learner_id != request.learner_id:
            raise ProjectError(
                ProjectErrorCode.NOT_FOUND,
                "Project was not found.",
                reference=request.project_id,
            )
        return shell

    def resolve_learning_project_start_option(
        self, request: ResolveLearningProjectStartOptionRequest
    ) -> LearningProjectStartOption:
        if request.placement_id != "risk-return-project-primary":
            raise ProjectError(
                ProjectErrorCode.INVALID_REQUEST,
                "The learning Project source is not current.",
                reference=request.placement_id,
            )
        origin = LearningProjectOrigin(
            "1.0.0",
            "intro-risk-return-project",
            "1.0.0",
            "a" * 64,
            "risk-return-project",
            "1.0.0",
            "b" * 64,
            "financial-foundations",
            "1.0.0",
            "c" * 64,
            request.placement_id,
            "1.0.0",
            "d" * 64,
            "Compare investment choices",
            "Practice a structured educational comparison.",
        )
        return LearningProjectStartOption(
            title=origin.brief_title,
            purpose=origin.brief_purpose,
            origin=origin,
        )

    def list_learning_project_start_options(
        self, _request: ListLearningProjectStartOptionsRequest
    ) -> tuple[LearningProjectStartOption, ...]:
        return (
            self.resolve_learning_project_start_option(
                ResolveLearningProjectStartOptionRequest(
                    "risk-return-project-primary"
                )
            ),
        )


def client() -> TestClient:
    policy = SingleProfileRequestPolicy(
        SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin=ORIGIN,
            allowed_hosts=("127.0.0.1:8000", "testserver"),
            secure_cookie=False,
        )
    )
    app = create_app(
        ApiServices(
            identity=Identity(),  # type: ignore[arg-type]
            curriculum=object(),  # type: ignore[arg-type]
            request_policy=policy,
            project=Projects(),
        )
    )
    return TestClient(
        app,
        base_url=ORIGIN,
        backend_options={"loop_factory": asyncio.SelectorEventLoop},
    )


def headers() -> dict[str, str]:
    return {"Origin": ORIGIN, "Sec-Fetch-Site": "same-origin"}


def independent_payload() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "idempotency_key": "project-create-1",
        "title": "Compare evidence",
        "charter": "Compare valid educational sources without making a recommendation.",
        "origin": {"origin_type": "independent"},
    }


def test_authenticated_http_create_list_and_read_share_one_public_api() -> None:
    subject = client()
    subject.cookies.set(COOKIE, "session-a")

    created = subject.post(
        "/api/v1/projects", headers=headers(), json=independent_payload()
    )
    listed = subject.get("/api/v1/projects")
    opened = subject.get(f"/api/v1/projects/{created.json()['project_id']}")

    assert created.status_code == listed.status_code == opened.status_code == 200
    assert listed.json()["records"] == [created.json()]
    assert opened.json() == created.json()
    assert created.json()["learner_id"] == "learner-a"
    assert {"idempotency_key", "request_fingerprint", "storage"}.isdisjoint(
        created.json()
    )


def test_client_selected_learner_and_missing_create_permission_fail_closed() -> None:
    subject = client()
    subject.cookies.set(COOKIE, "session-a")
    selected = {**independent_payload(), "learner_id": "learner-b"}
    rejected = subject.post(
        "/api/v1/projects", headers=headers(), json=selected
    )
    subject.cookies.set(COOKIE, "read-only")
    forbidden = subject.post(
        "/api/v1/projects", headers=headers(), json=independent_payload()
    )

    assert rejected.status_code == 400
    assert forbidden.status_code == 403


def test_cross_learner_guessed_project_is_bounded_not_found() -> None:
    subject = client()
    subject.cookies.set(COOKIE, "session-a")
    created = subject.post(
        "/api/v1/projects", headers=headers(), json=independent_payload()
    )
    subject.cookies.set(COOKIE, "session-b")

    response = subject.get(f"/api/v1/projects/{created.json()['project_id']}")

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_state_change_requires_same_origin_but_headless_gets_do_not() -> None:
    subject = client()
    subject.cookies.set(COOKIE, "session-a")
    denied = subject.post("/api/v1/projects", json=independent_payload())
    allowed = subject.get("/api/v1/projects")

    assert denied.status_code == 403
    assert allowed.status_code == 200


def test_headless_start_option_is_protected_and_contains_no_storage_facts() -> None:
    subject = client()
    denied = subject.get(
        "/api/v1/projects/start-options/risk-return-project-primary"
    )
    subject.cookies.set(COOKIE, "session-a")
    response = subject.get(
        "/api/v1/projects/start-options/risk-return-project-primary"
    )
    listed = subject.get("/api/v1/projects/start-options")

    assert denied.status_code == 401
    assert response.status_code == 200
    assert listed.status_code == 200
    assert listed.json()["records"] == [response.json()]
    assert response.json()["title"] == "Compare investment choices"
    assert response.json()["origin"]["placement_id"] == (
        "risk-return-project-primary"
    )
    assert {"storage", "path", "object_key"}.isdisjoint(response.json())


@pytest.mark.postgres
@pytest.mark.skipif(
    POSTGRES_DSN is None,
    reason="FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN is not configured",
)
def test_composed_api_creates_independent_and_exact_learning_projects(
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
    graph = project_curriculum_graph(
        package_id=accepted.package_id,
        package_version=accepted.package_version,
        package_digest=accepted.package_digest,
    )
    services.curriculum.publish_curriculum_graph(
        PublishCurriculumGraphRequest(graph)
    )
    placement = services.curriculum.create_project_brief_placement(
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
            brief_digest=(
                "1f234681a4b9262dd49e01c82c8c6a12f6a64d13845bea6140708a7d16f061ff"
            ),
            project_brief_schema_version="1.0.0",
        )
    )
    app = create_app(
        ApiServices(
            identity=services.identity,
            curriculum=services.curriculum,
            request_policy=services.request_policy,
            assessment=services.assessment,
            learner_model=services.learner_model,
            adaptation=services.adaptation,
            audit=services.audit,
            project=services.project,
        )
    )
    with TestClient(
        app,
        base_url=ORIGIN,
        backend_options={"loop_factory": asyncio.SelectorEventLoop},
    ) as subject:
        bootstrapped = subject.post(
            "/api/v1/session/single-profile",
            headers=headers(),
            json={"limitation_acknowledged": True},
        )
        assert bootstrapped.status_code == 201
        independent = subject.post(
            "/api/v1/projects",
            headers=headers(),
            json=independent_payload(),
        )
        project_id = independent.json()["project_id"]
        workspace = subject.get(
            f"/api/v1/projects/{project_id}/workspace"
        )
        note = subject.post(
            f"/api/v1/projects/{project_id}/workspace/mutations",
            headers=headers(),
            json={
                "schema_version": "1.0.0",
                "idempotency_key": "api-note-1",
                "expected_workspace_revision": 1,
                "mutation": {
                    "operation": "add_note",
                    "title": "Question",
                    "body": "Compare the educational evidence.",
                },
            },
        )
        artifact_content = b"scenario,value\nbase,1\n"
        artifact = subject.post(
            f"/api/v1/projects/{project_id}/artifacts",
            headers=headers(),
            json={
                "intent": {
                    "schema_version": "1.0.0",
                    "idempotency_key": "api-artifact-1",
                    "expected_workspace_revision": 2,
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
                                "source_title": "API scenario",
                            },
                            "assumptions": [],
                        },
                    },
                },
                "content_base64": base64.b64encode(
                    artifact_content
                ).decode("ascii"),
            },
        )
        artifact_record = artifact.json()["artifacts"][0]
        download = subject.get(
            f"/api/v1/projects/{project_id}/artifacts/"
            f"{artifact_record['artifact_id']}/versions/1"
        )
        snapshot = subject.post(
            f"/api/v1/projects/{project_id}/snapshots",
            headers=headers(),
            json={
                "schema_version": "1.0.0",
                "idempotency_key": "api-snapshot-1",
                "expected_project_revision": 1,
                "expected_workspace_revision": 3,
            },
        )
        assert snapshot.status_code == 200, snapshot.text
        export = subject.get(
            f"/api/v1/projects/{project_id}/snapshots/"
            f"{snapshot.json()['snapshot_id']}/export"
        )
        start_option = subject.get(
            "/api/v1/projects/start-options/risk-return-project-primary"
        )
        start_options = subject.get("/api/v1/projects/start-options")
        learning_payload = {
            "schema_version": "1.0.0",
            "idempotency_key": "learning-project-1",
            "title": "My learning Project",
            "charter": "Apply the approved brief without making a recommendation.",
            "origin": start_option.json()["origin"],
        }
        learning = subject.post(
            "/api/v1/projects", headers=headers(), json=learning_payload
        )
        listed = subject.get("/api/v1/projects")

    assert start_option.status_code == 200
    assert start_options.status_code == 200
    assert start_options.json()["records"] == [start_option.json()]
    assert independent.status_code == learning.status_code == 200
    assert workspace.status_code == note.status_code == artifact.status_code == 200
    assert download.status_code == snapshot.status_code == export.status_code == 200
    assert download.content == artifact_content
    assert download.headers["content-disposition"].startswith("attachment")
    assert download.headers["x-content-type-options"] == "nosniff"
    assert download.headers["x-artifact-media-type"] == "text/csv"
    assert export.json()["files"][0]["content_base64"] == base64.b64encode(
        artifact_content
    ).decode("ascii")
    assert [record["title"] for record in listed.json()["records"]] == [
        "Compare evidence",
        "My learning Project",
    ]
    assert learning.json()["origin"]["placement_digest"] == (
        placement.placement_digest
    )
    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute(
            "SELECT count(*) FROM project.project_shells"
        ).fetchone() == (2,)
        assert connection.execute(
            "SELECT count(*) FROM assessment.attempts"
        ).fetchone() == (0,)
