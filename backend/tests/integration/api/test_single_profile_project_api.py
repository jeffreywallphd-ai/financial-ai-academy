from __future__ import annotations

import asyncio
import os
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
    CreateProjectBriefPlacementRequest,
)
from financial_ai_academy.modules.curriculum.public import CurriculumOperations
from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    LearnerContext,
)
from financial_ai_academy.modules.project.domain.project import ProjectShell
from financial_ai_academy.modules.project.public import (
    CreateProjectRequest,
    IndependentProjectOrigin,
    ListProjectsRequest,
    OpenProjectRequest,
    ProjectError,
    ProjectErrorCode,
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
            else ("project.create", "project.read")
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
    placement = services.curriculum.create_project_brief_placement(
        CreateProjectBriefPlacementRequest(
            placement_id="risk-return-project-primary",
            placement_version="1.0.0",
            curriculum_id="financial-foundations",
            curriculum_version="1.0.0",
            curriculum_digest="c" * 64,
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
        learning_payload = {
            "schema_version": "1.0.0",
            "idempotency_key": "learning-project-1",
            "title": "My learning Project",
            "charter": "Apply the approved brief without making a recommendation.",
            "origin": {
                "origin_type": "learning",
                "project_brief_schema_version": "1.0.0",
                "package_id": accepted.package_id,
                "package_version": accepted.package_version,
                "package_digest": accepted.package_digest,
                "brief_id": "risk-return-project",
                "brief_version": "1.0.0",
                "brief_digest": (
                    "1f234681a4b9262dd49e01c82c8c6a12f6a64d13845bea6140708a7d16f061ff"
                ),
                "curriculum_id": placement.curriculum_id,
                "curriculum_version": placement.curriculum_version,
                "curriculum_digest": placement.curriculum_digest,
                "placement_id": placement.placement_id,
                "placement_version": placement.placement_version,
                "placement_digest": placement.placement_digest,
                "brief_title": "Compare investment choices",
                "brief_purpose": (
                    "Practice a structured, educational comparison without making a recommendation."
                ),
            },
        }
        learning = subject.post(
            "/api/v1/projects", headers=headers(), json=learning_payload
        )
        listed = subject.get("/api/v1/projects")

    assert independent.status_code == learning.status_code == 200
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
