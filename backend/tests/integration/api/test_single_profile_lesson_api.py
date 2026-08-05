from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient

from financial_ai_academy.bootstrap.composition import (
    ApplicationServices,
    build_application_services,
)
from financial_ai_academy.bootstrap.settings import (
    SingleProfileApplicationSettings,
)
from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.hosts.api.generate_openapi import generate_bytes
from financial_ai_academy.modules.content.public import (
    AdmitLessonPackageRequest,
)
from financial_ai_academy.modules.curriculum.public import (
    CreateLessonPlacementRequest,
    LessonReadingResult,
    OpenPlacedLessonRequest,
)
from financial_ai_academy.modules.identity.public import (
    IssuedSession,
    LearnerContext,
    SingleProfileBootstrapRequest,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)


REPOSITORY = Path(__file__).resolve().parents[4]
APPROVED = (
    REPOSITORY
    / "contracts/compatibility/lesson-package/v1/approved/intro-risk-return"
)
SCHEMAS = REPOSITORY / "contracts/learning/lesson-package/v1"
MIGRATIONS = REPOSITORY / "backend/migrations"
OPENAPI = REPOSITORY / "contracts/api/openapi.json"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
ORIGIN = "http://127.0.0.1:8000"
COOKIE_NAME = "financial_ai_academy_session"

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(
        POSTGRES_DSN is None,
        reason="FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN is not configured",
    ),
]


def _drop_test_schemas() -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as connection:
        connection.execute("DROP SCHEMA IF EXISTS identity CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS curriculum CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS content CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS platform CASCADE")


@pytest.fixture(scope="module", autouse=True)
def migrated_database() -> object:
    assert POSTGRES_DSN is not None
    _drop_test_schemas()
    root_runner = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS)
    identity_runner = PostgresMigrationRunner(
        POSTGRES_DSN, MIGRATIONS / "identity"
    )
    root_statuses = root_runner.apply_all()
    assert [status.migration_id for status in root_statuses] == [
        "0001_content_lesson_package_versions",
        "0002_curriculum_lesson_placements",
    ]
    statuses = identity_runner.apply_all()
    assert [status.migration_id for status in statuses] == [
        "0001_content_lesson_package_versions",
        "0002_curriculum_lesson_placements",
        "identity_0001_single_profile_sessions",
    ]
    assert identity_runner.apply_all() == statuses
    yield
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            (
                MIGRATIONS
                / "identity/identity_0001_single_profile_sessions.down.sql"
            ).read_text(encoding="utf-8")
        )
        connection.execute(
            """
            DELETE FROM platform.schema_migrations
            WHERE migration_id = 'identity_0001_single_profile_sessions'
            """
        )
    root_runner.rollback_all()
    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute(
            "SELECT to_regnamespace('identity')"
        ).fetchone() == (None,)


@pytest.fixture(autouse=True)
def empty_slice_tables(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                identity.sessions,
                identity.bindings,
                identity.installations,
                curriculum.lesson_placements,
                content.lesson_package_versions
            CASCADE
            """
        )


def _settings(object_root: Path) -> SingleProfileApplicationSettings:
    assert POSTGRES_DSN is not None
    return SingleProfileApplicationSettings(
        postgres_dsn=POSTGRES_DSN,
        object_storage_root=object_root,
        lesson_schema_dir=SCHEMAS,
        migrations_dir=MIGRATIONS,
        security=SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin=ORIGIN,
            allowed_hosts=("127.0.0.1:8000",),
            secure_cookie=False,
        ),
    )


def _build_seeded_client(
    object_root: Path,
) -> tuple[TestClient, ApplicationServices, str]:
    services = build_application_services(_settings(object_root))
    accepted = services.content.admit_lesson_package(
        AdmitLessonPackageRequest(APPROVED)
    )
    services.curriculum.create_lesson_placement(
        CreateLessonPlacementRequest(
            placement_id="intro-risk-return-primary",
            package_id=accepted.package_id,
            package_version=accepted.package_version,
            package_digest=accepted.package_digest,
        )
    )
    app = create_app(
        ApiServices(
            identity=services.identity,
            curriculum=services.curriculum,
            request_policy=services.request_policy,
        )
    )
    return (
        TestClient(app, base_url=ORIGIN),
        services,
        accepted.package_digest,
    )


def _bootstrap(client: TestClient) -> object:
    return client.post(
        "/api/v1/session/single-profile",
        headers={"Origin": ORIGIN, "Sec-Fetch-Site": "same-origin"},
        json={"limitation_acknowledged": True},
    )


def test_bootstrap_and_exact_lesson_read_use_protected_server_context(
    tmp_path: Path,
) -> None:
    assert POSTGRES_DSN is not None
    client, _services, digest = _build_seeded_client(tmp_path / "objects")

    bootstrap = _bootstrap(client)
    lesson = client.get(
        "/api/v1/curriculum/placements/intro-risk-return-primary/lesson"
    )

    assert bootstrap.status_code == 201
    assert bootstrap.json()["authentication_method"] == "single_profile"
    cookie_header = bootstrap.headers["set-cookie"].casefold()
    assert f"{COOKIE_NAME}=" in cookie_header
    assert "httponly" in cookie_header
    assert "samesite=strict" in cookie_header
    assert "path=/" in cookie_header
    assert "secure" not in cookie_header
    assert lesson.status_code == 200
    body = lesson.json()
    assert body["placement_id"] == "intro-risk-return-primary"
    assert body["package_id"] == "intro-risk-return"
    assert body["package_version"] == "1.0.0"
    assert body["package_digest"] == digest
    assert body["title"] == "Understanding Risk and Return"
    assert len(body["body"]) == 5
    assert {"actor_id", "learner_id", "session_id"}.isdisjoint(body)
    raw_cookie = client.cookies.get(COOKIE_NAME)
    assert raw_cookie is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        persisted = connection.execute(
            "SELECT token_hash FROM identity.sessions"
        ).fetchone()
    assert persisted is not None
    assert len(persisted[0]) == 64
    assert raw_cookie not in persisted[0]


def test_missing_tampered_expired_and_revoked_context_fail_closed(
    tmp_path: Path,
) -> None:
    assert POSTGRES_DSN is not None
    client, services, _digest = _build_seeded_client(tmp_path / "objects")

    missing = client.get(
        "/api/v1/curriculum/placements/intro-risk-return-primary/lesson"
    )
    assert missing.status_code == 401
    assert missing.json()["code"] == "unauthorized"

    issued = _bootstrap(client)
    assert issued.status_code == 201
    valid_cookie = client.cookies.get(COOKIE_NAME)
    assert valid_cookie is not None
    with TestClient(client.app, base_url=ORIGIN) as tampered_client:
        tampered_client.cookies.set(COOKIE_NAME, "z" * 43)
        tampered = tampered_client.get(
            "/api/v1/curriculum/placements/"
            "intro-risk-return-primary/lesson"
        )
    assert tampered.status_code == 401
    assert "z" * 43 not in tampered.text

    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            UPDATE identity.sessions
            SET absolute_expires_at =
                authenticated_at + interval '1 microsecond'
            """
        )
    expired = client.get(
        "/api/v1/curriculum/placements/intro-risk-return-primary/lesson"
    )
    assert expired.status_code == 401

    replacement = _bootstrap(client)
    assert replacement.status_code == 201
    replacement_cookie = client.cookies.get(COOKIE_NAME)
    services.identity.revoke_session(replacement_cookie)
    revoked = client.get(
        "/api/v1/curriculum/placements/intro-risk-return-primary/lesson"
    )
    assert revoked.status_code == 401


def test_client_selected_identity_and_unsafe_boundary_are_rejected(
    tmp_path: Path,
) -> None:
    client, _services, _digest = _build_seeded_client(tmp_path / "objects")

    selected_header = client.post(
        "/api/v1/session/single-profile",
        headers={
            "Origin": ORIGIN,
            "X-Learner-ID": "client-selected",
        },
        json={"limitation_acknowledged": True},
    )
    selected_body = client.post(
        "/api/v1/session/single-profile",
        headers={"Origin": ORIGIN},
        json={
            "limitation_acknowledged": True,
            "actor_id": "client-selected",
        },
    )
    unsafe_host = client.get("/health", headers={"Host": "attacker.invalid"})
    unsafe_origin = client.post(
        "/api/v1/session/single-profile",
        headers={"Origin": "http://attacker.invalid"},
        json={"limitation_acknowledged": True},
    )

    assert selected_header.status_code == 403
    assert selected_body.status_code == 400
    assert selected_body.json()["code"] == "invalid_request"
    assert "client-selected" not in selected_body.text
    assert unsafe_host.status_code == 403
    assert unsafe_origin.status_code == 403


def test_missing_exact_placement_never_substitutes_latest(
    tmp_path: Path,
) -> None:
    client, _services, _digest = _build_seeded_client(tmp_path / "objects")
    assert _bootstrap(client).status_code == 201

    missing = client.get(
        "/api/v1/curriculum/placements/not-a-real-placement/lesson"
    )

    assert missing.status_code == 404
    assert missing.json()["code"] == "not_found"
    assert "intro-risk-return" not in missing.text


class _ResolvedIdentity:
    def bootstrap_single_profile(
        self, request: SingleProfileBootstrapRequest
    ) -> IssuedSession:
        raise NotImplementedError

    def resolve_session(self, cookie_value: str | None) -> LearnerContext:
        return LearnerContext(
            actor_id="opaque-actor",
            learner_id="opaque-learner",
            session_id="opaque-session",
            authenticated_at=datetime(2026, 8, 5, tzinfo=timezone.utc),
            expires_at=datetime(2026, 8, 6, tzinfo=timezone.utc),
            authentication_method="single_profile",
            permissions=("curriculum.lesson.read",),
        )

    def revoke_session(self, cookie_value: str | None) -> None:
        return None

    def health(self) -> bool:
        return True


class _SentinelCurriculum:
    def create_lesson_placement(
        self, request: CreateLessonPlacementRequest
    ) -> object:
        raise NotImplementedError

    def open_placed_lesson(
        self, request: OpenPlacedLessonRequest
    ) -> LessonReadingResult:
        raise RuntimeError(
            "PRIVATE-SENTINEL C:\\private\\lesson secret-cookie-value"
        )


def test_unexpected_failures_are_redacted_and_correlatable() -> None:
    policy = SingleProfileRequestPolicy(
        SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin=ORIGIN,
            allowed_hosts=("127.0.0.1:8000",),
            secure_cookie=False,
        )
    )
    app = create_app(
        ApiServices(
            identity=_ResolvedIdentity(),
            curriculum=_SentinelCurriculum(),  # type: ignore[arg-type]
            request_policy=policy,
        )
    )
    client = TestClient(app, base_url=ORIGIN)
    client.cookies.set(COOKIE_NAME, "a" * 43)

    response = client.get(
        "/api/v1/curriculum/placements/intro-risk-return-primary/lesson"
    )

    assert response.status_code == 500
    assert response.json()["code"] == "internal_error"
    assert len(response.json()["correlation_id"]) == 36
    assert "PRIVATE-SENTINEL" not in response.text
    assert "private" not in response.text.casefold()
    assert "secret-cookie-value" not in response.text


def test_openapi_snapshot_is_stable_closed_and_cookie_secured() -> None:
    first = generate_bytes()
    second = generate_bytes()
    assert first == second == OPENAPI.read_bytes()
    schema = json.loads(first)
    lesson = schema["paths"][
        "/api/v1/curriculum/placements/{placement_id}/lesson"
    ]["get"]
    assert schema["openapi"] == "3.1.0"
    assert schema["x-contract-version"] == "1.0"
    assert lesson["security"] == [{"OpaqueSessionCookie": []}]
    assert schema["components"]["securitySchemes"][
        "OpaqueSessionCookie"
    ] == {
        "description": (
            "Opaque server-side session cookie. The value is never an "
            "identity selector and is not readable by browser scripts."
        ),
        "in": "cookie",
        "name": COOKIE_NAME,
        "type": "apiKey",
    }
    lesson_model = schema["components"]["schemas"][
        "LessonReadingResponseModel"
    ]
    assert lesson_model["additionalProperties"] is False
    assert "actor_id" not in first.decode("utf-8")
