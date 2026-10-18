from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.hosts.api.generate_openapi import generate_bytes
from financial_ai_academy.modules.audit.adapters.provenance_contract import (
    lineage_view_from_mapping,
)
from financial_ai_academy.modules.audit.domain.provenance import (
    LineageView,
    lineage_view_payload,
)
from financial_ai_academy.modules.audit.public import (
    AuditError,
    AuditErrorCode,
    ReadKnowledgeCheckCompletionLineageRequest,
    ReadPublishedLessonLineageRequest,
)
from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    LearnerContext,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)


ROOT = Path(__file__).resolve().parents[4]
APPROVED = ROOT / "contracts/compatibility/provenance/v1/approved"
LINEAGE_SCHEMA = ROOT / "contracts/provenance/v1/lineage-view.schema.json"
OPENAPI = ROOT / "contracts/api/openapi.json"
ORIGIN = "http://127.0.0.1:8000"
COOKIE_NAME = "financial_ai_academy_session"
COOKIE = "a" * 43
LEARNER_ID = "11111111-1111-4111-8111-111111111111"


def _approved(name: str) -> tuple[dict[str, object], LineageView]:
    document = json.loads((APPROVED / name).read_text(encoding="utf-8"))
    view = lineage_view_from_mapping(document)
    return lineage_view_payload(view), view


class Identity:
    def __init__(self, permissions: tuple[str, ...]) -> None:
        self.permissions = permissions

    def resolve_session(self, cookie_value: str | None) -> LearnerContext:
        if cookie_value != COOKIE:
            raise IdentityError(
                IdentityErrorCode.UNAUTHORIZED,
                "A valid learner session is required.",
            )
        return LearnerContext(
            actor_id="22222222-2222-4222-8222-222222222222",
            learner_id=LEARNER_ID,
            session_id="33333333-3333-4333-8333-333333333333",
            authenticated_at=datetime(2026, 8, 5, tzinfo=timezone.utc),
            expires_at=datetime(2026, 8, 6, tzinfo=timezone.utc),
            authentication_method="single_profile",
            permissions=self.permissions,
        )

    def health(self) -> bool:
        return True


class Audit:
    def __init__(self) -> None:
        self.lesson_document, self.lesson_view = _approved(
            "incomplete-lineage-view.json"
        )
        self.completion_document, self.completion_view = _approved(
            "lineage-view.json"
        )
        self.lesson_calls: list[ReadPublishedLessonLineageRequest] = []
        self.completion_calls: list[
            ReadKnowledgeCheckCompletionLineageRequest
        ] = []
        self.error: AuditError | None = None

    def read_published_lesson_lineage(
        self,
        request: ReadPublishedLessonLineageRequest,
    ) -> LineageView:
        self.lesson_calls.append(request)
        if self.error is not None:
            raise self.error
        return self.lesson_view

    def read_knowledge_check_completion_lineage(
        self,
        request: ReadKnowledgeCheckCompletionLineageRequest,
    ) -> LineageView:
        self.completion_calls.append(request)
        if self.error is not None:
            raise self.error
        return self.completion_view


def _client(
    permissions: tuple[str, ...] = (
        "audit.lineage.read",
        "curriculum.lesson.read",
    ),
    *,
    authenticated: bool = True,
    configured: bool = True,
) -> tuple[TestClient, Audit]:
    audit = Audit()
    policy = SingleProfileRequestPolicy(
        SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin=ORIGIN,
            allowed_hosts=("127.0.0.1:8000",),
            secure_cookie=False,
        )
    )
    http = TestClient(
        create_app(
            ApiServices(
                identity=Identity(permissions),  # type: ignore[arg-type]
                curriculum=object(),  # type: ignore[arg-type]
                request_policy=policy,
                audit=audit if configured else None,
            )
        ),
        base_url=ORIGIN,
    )
    if authenticated:
        http.cookies.set(COOKIE_NAME, COOKIE)
    http.headers["Origin"] = ORIGIN
    return http, audit


def _lesson_request() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "root_kind": "published_lesson",
        "package_id": "leçon-diversification-été",
        "package_version": "1.0.0",
        "package_digest": "8" * 64,
    }


def _completion_request() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "root_kind": "knowledge_check_completion",
        "placement_id": "intro-risk-return",
        "evidence_id": "evidence-check-1",
        "occurrence": 1,
    }


def test_authorized_two_root_requests_preserve_exact_bounded_views() -> None:
    http, audit = _client()

    lesson = http.post(
        "/api/v1/audit/learning-lineage",
        json=_lesson_request(),
    )
    completion = http.post(
        "/api/v1/audit/learning-lineage",
        json=_completion_request(),
    )

    assert lesson.status_code == 200
    assert completion.status_code == 200
    assert lesson.json() == audit.lesson_document
    assert completion.json() == audit.completion_document
    assert audit.lesson_calls == [
        ReadPublishedLessonLineageRequest(
            "leçon-diversification-été",
            "1.0.0",
            "8" * 64,
        )
    ]
    assert audit.completion_calls == [
        ReadKnowledgeCheckCompletionLineageRequest(
            LEARNER_ID,
            "intro-risk-return",
            "evidence-check-1",
            1,
        )
    ]
    validator = Draft202012Validator(
        json.loads(LINEAGE_SCHEMA.read_text(encoding="utf-8")),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(lesson.json())) == []
    assert list(validator.iter_errors(completion.json())) == []
    serialized = lesson.text + completion.text
    assert LEARNER_ID not in serialized
    assert all(
        private not in serialized
        for private in (
            "locator",
            "selected_option",
            "feedback",
            "repository_path",
            "permission",
        )
    )


def test_session_and_both_permissions_are_required_before_audit_access() -> None:
    missing, missing_audit = _client(authenticated=False)
    no_lineage, no_lineage_audit = _client(("curriculum.lesson.read",))
    no_lesson, no_lesson_audit = _client(("audit.lineage.read",))

    missing_response = missing.post(
        "/api/v1/audit/learning-lineage",
        json=_lesson_request(),
    )
    lineage_response = no_lineage.post(
        "/api/v1/audit/learning-lineage",
        json=_lesson_request(),
    )
    lesson_response = no_lesson.post(
        "/api/v1/audit/learning-lineage",
        json=_completion_request(),
    )

    assert missing_response.status_code == 401
    assert lineage_response.status_code == 403
    assert lesson_response.status_code == 403
    for audit in (missing_audit, no_lineage_audit, no_lesson_audit):
        assert audit.lesson_calls == []
        assert audit.completion_calls == []


def test_closed_request_rejects_authority_fields_query_and_wrong_types() -> None:
    http, audit = _client()
    selected = {**_completion_request(), "learner_id": LEARNER_ID}

    extra = http.post("/api/v1/audit/learning-lineage", json=selected)
    boolean = http.post(
        "/api/v1/audit/learning-lineage",
        json={**_completion_request(), "occurrence": True},
    )
    invalid_digest = http.post(
        "/api/v1/audit/learning-lineage",
        json={**_lesson_request(), "package_digest": "A" * 64},
    )
    query = http.post(
        "/api/v1/audit/learning-lineage?latest=true",
        json=_lesson_request(),
    )
    selected_header = http.post(
        "/api/v1/audit/learning-lineage",
        json=_lesson_request(),
        headers={"X-Permission": "audit.lineage.read"},
    )

    assert [
        extra.status_code,
        boolean.status_code,
        invalid_digest.status_code,
        query.status_code,
        selected_header.status_code,
    ] == [400, 400, 400, 400, 403]
    assert audit.lesson_calls == []
    assert audit.completion_calls == []
    assert LEARNER_ID not in extra.text
    assert "latest" not in query.text


def test_unavailable_or_unconfigured_audit_is_bounded() -> None:
    http, audit = _client()
    audit.error = AuditError(
        AuditErrorCode.UNAVAILABLE,
        "Learning lineage is temporarily unavailable.",
        reference="published_lesson",
    )
    unavailable = http.post(
        "/api/v1/audit/learning-lineage",
        json=_lesson_request(),
    )
    unconfigured, _audit = _client(configured=False)
    absent = unconfigured.post(
        "/api/v1/audit/learning-lineage",
        json=_lesson_request(),
    )

    assert unavailable.status_code == 503
    assert unavailable.json()["code"] == "unavailable"
    assert absent.status_code == 503
    assert absent.json()["code"] == "unavailable"


def test_openapi_snapshot_contains_one_cookie_protected_union_operation() -> None:
    generated = json.loads(generate_bytes())
    operation = generated["paths"]["/api/v1/audit/learning-lineage"]["post"]

    assert operation["operationId"] == "readLearningLineage"
    assert operation["security"] == [{"OpaqueSessionCookie": []}]
    assert "422" not in operation["responses"]
    assert OPENAPI.read_bytes() == generate_bytes()
