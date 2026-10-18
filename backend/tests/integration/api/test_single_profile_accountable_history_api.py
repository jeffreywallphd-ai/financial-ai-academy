from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.hosts.api.generate_openapi import generate_bytes
from financial_ai_academy.modules.audit.adapters import lineage_view_from_mapping
from financial_ai_academy.modules.audit.domain import (
    AccountableHistoryPurpose,
    accountable_history_payload,
    build_portable_evidence,
    compose_accountable_history,
    portable_evidence_payload,
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
DOCUMENT_SCHEMA = ROOT / "contracts/accountable-history/v1/document.schema.json"
EXPORT_SCHEMA = ROOT / "contracts/accountable-history/v1/export.schema.json"
OPENAPI = ROOT / "contracts/api/openapi.json"
ORIGIN = "http://127.0.0.1:8000"
COOKIE_NAME = "financial_ai_academy_session"
COOKIE = "a" * 43
LEARNER_ID = "11111111-1111-4111-8111-111111111111"


def _lineage(name: str):
    return lineage_view_from_mapping(
        json.loads((APPROVED / name).read_text(encoding="utf-8"))
    )


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
        self.lesson = _lineage("incomplete-lineage-view.json")
        self.completion = _lineage("lineage-view.json")
        self.calls: list[tuple[str, object]] = []
        self.error: AuditError | None = None

    def _record(self, operation: str, request: object, value):
        self.calls.append((operation, request))
        if self.error is not None:
            raise self.error
        return value

    def read_published_lesson_accountable_history(
        self, request: ReadPublishedLessonLineageRequest
    ):
        return self._record(
            "read-lesson",
            request,
            compose_accountable_history(
                self.lesson, AccountableHistoryPurpose.LEARNER_REVIEW
            ),
        )

    def read_knowledge_check_completion_accountable_history(
        self, request: ReadKnowledgeCheckCompletionLineageRequest
    ):
        return self._record(
            "read-completion",
            request,
            compose_accountable_history(
                self.completion, AccountableHistoryPurpose.LEARNER_REVIEW
            ),
        )

    def export_published_lesson_accountable_history(
        self, request: ReadPublishedLessonLineageRequest
    ):
        return self._record(
            "export-lesson", request, build_portable_evidence(self.lesson)
        )

    def export_knowledge_check_completion_accountable_history(
        self, request: ReadKnowledgeCheckCompletionLineageRequest
    ):
        return self._record(
            "export-completion", request, build_portable_evidence(self.completion)
        )


def _client(
    permissions: tuple[str, ...] = (
        "audit.history.export",
        "audit.history.read",
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


def test_two_roots_use_server_selected_purpose_and_exact_contracts() -> None:
    http, audit = _client()

    lesson = http.post(
        "/api/v1/audit/accountable-history", json=_lesson_request()
    )
    completion = http.post(
        "/api/v1/audit/accountable-history", json=_completion_request()
    )
    exported = http.post(
        "/api/v1/audit/accountable-history/export", json=_completion_request()
    )

    assert [lesson.status_code, completion.status_code, exported.status_code] == [
        200,
        200,
        200,
    ]
    assert lesson.json() == accountable_history_payload(
        compose_accountable_history(
            audit.lesson, AccountableHistoryPurpose.LEARNER_REVIEW
        )
    )
    assert exported.json() == portable_evidence_payload(
        build_portable_evidence(audit.completion)
    )
    assert audit.calls[1][1] == ReadKnowledgeCheckCompletionLineageRequest(
        LEARNER_ID, "intro-risk-return", "evidence-check-1", 1
    )
    document_validator = Draft202012Validator(
        json.loads(DOCUMENT_SCHEMA.read_text(encoding="utf-8")),
        format_checker=FormatChecker(),
    )
    document_schema = json.loads(DOCUMENT_SCHEMA.read_text(encoding="utf-8"))
    registry = Registry().with_resource(
        str(document_schema["$id"]), Resource.from_contents(document_schema)
    )
    export_validator = Draft202012Validator(
        json.loads(EXPORT_SCHEMA.read_text(encoding="utf-8")),
        format_checker=FormatChecker(),
        registry=registry,
    )
    assert list(document_validator.iter_errors(lesson.json())) == []
    assert list(document_validator.iter_errors(completion.json())) == []
    assert list(export_validator.iter_errors(exported.json())) == []
    serialized = lesson.text + completion.text + exported.text
    assert LEARNER_ID not in serialized
    for private in (
        "lesson_body",
        "answer",
        "score",
        "feedback",
        "locator",
        "provider",
        "storage_path",
        "permission",
    ):
        assert private not in serialized


def test_inspection_and_export_permissions_are_separate_before_audit_access() -> None:
    inspect, inspect_audit = _client(
        ("audit.history.read", "curriculum.lesson.read")
    )
    export, export_audit = _client(
        ("audit.history.export", "curriculum.lesson.read")
    )
    missing_lesson, missing_lesson_audit = _client(("audit.history.read",))
    unauthenticated, unauthenticated_audit = _client(authenticated=False)

    assert inspect.post(
        "/api/v1/audit/accountable-history", json=_lesson_request()
    ).status_code == 200
    assert inspect.post(
        "/api/v1/audit/accountable-history/export", json=_lesson_request()
    ).status_code == 403
    assert export.post(
        "/api/v1/audit/accountable-history/export", json=_lesson_request()
    ).status_code == 200
    assert export.post(
        "/api/v1/audit/accountable-history", json=_lesson_request()
    ).status_code == 403
    assert missing_lesson.post(
        "/api/v1/audit/accountable-history", json=_lesson_request()
    ).status_code == 403
    assert unauthenticated.post(
        "/api/v1/audit/accountable-history", json=_lesson_request()
    ).status_code == 401

    assert [name for name, _request in inspect_audit.calls] == ["read-lesson"]
    assert [name for name, _request in export_audit.calls] == ["export-lesson"]
    assert missing_lesson_audit.calls == []
    assert unauthenticated_audit.calls == []


def test_closed_request_rejects_client_authority_and_query_input() -> None:
    http, audit = _client()

    responses = [
        http.post(
            "/api/v1/audit/accountable-history",
            json={**_lesson_request(), "purpose": "portable_evidence"},
        ),
        http.post(
            "/api/v1/audit/accountable-history/export",
            json={**_completion_request(), "learner_id": LEARNER_ID},
        ),
        http.post(
            "/api/v1/audit/accountable-history",
            json={**_completion_request(), "occurrence": True},
        ),
        http.post(
            "/api/v1/audit/accountable-history?latest=true",
            json=_lesson_request(),
        ),
    ]

    assert [response.status_code for response in responses] == [400, 400, 400, 400]
    assert audit.calls == []
    assert LEARNER_ID not in responses[1].text
    assert "latest" not in responses[3].text


def test_unavailable_and_unconfigured_audit_are_bounded() -> None:
    http, audit = _client()
    audit.error = AuditError(
        AuditErrorCode.UNAVAILABLE,
        "Source and history is temporarily unavailable.",
        reference="published_lesson",
    )
    unavailable = http.post(
        "/api/v1/audit/accountable-history", json=_lesson_request()
    )
    unconfigured, _audit = _client(configured=False)
    absent = unconfigured.post(
        "/api/v1/audit/accountable-history/export", json=_lesson_request()
    )

    assert unavailable.status_code == 503
    assert unavailable.json()["code"] == "unavailable"
    assert absent.status_code == 503
    assert absent.json()["code"] == "unavailable"


def test_openapi_contains_two_cookie_protected_headless_operations() -> None:
    generated = json.loads(generate_bytes())
    read = generated["paths"]["/api/v1/audit/accountable-history"]["post"]
    export = generated["paths"]["/api/v1/audit/accountable-history/export"][
        "post"
    ]

    assert read["operationId"] == "readAccountableHistory"
    assert export["operationId"] == "exportAccountableHistory"
    assert read["security"] == export["security"] == [
        {"OpaqueSessionCookie": []}
    ]
    assert "422" not in read["responses"]
    assert "422" not in export["responses"]
    assert OPENAPI.read_bytes() == generate_bytes()


def test_openapi_preserves_frozen_history_identity_and_time_constraints() -> None:
    generated = json.loads(generate_bytes())
    document_schema = {
        "$ref": "#/components/schemas/AccountableHistoryResponseModel",
        "components": generated["components"],
    }
    document_validator = Draft202012Validator(
        document_schema,
        format_checker=FormatChecker(),
    )
    valid = accountable_history_payload(
        compose_accountable_history(
            _lineage("lineage-view.json"),
            AccountableHistoryPurpose.LEARNER_REVIEW,
        )
    )
    assert list(document_validator.iter_errors(valid)) == []

    wrong_owner = json.loads(json.dumps(valid))
    wrong_owner["entries"][0]["owner_module"] = "audit"
    owner_errors = list(document_validator.iter_errors(wrong_owner))
    assert owner_errors

    missing_offset = json.loads(json.dumps(valid))
    missing_offset["entries"][0]["recorded_at"] = "2026-08-05T12:00:00"
    time_errors = list(document_validator.iter_errors(missing_offset))
    assert time_errors

    export_schema = {
        "$ref": "#/components/schemas/PortableEvidenceExportResponseModel",
        "components": generated["components"],
    }
    export_validator = Draft202012Validator(
        export_schema,
        format_checker=FormatChecker(),
    )
    valid_export = portable_evidence_payload(
        build_portable_evidence(_lineage("lineage-view.json"))
    )
    assert list(export_validator.iter_errors(valid_export)) == []

    numeric_offset_export = json.loads(json.dumps(valid_export))
    numeric_offset_export["exported_at"] = (
        numeric_offset_export["exported_at"].removesuffix("Z") + "+00:00"
    )
    export_time_errors = list(
        export_validator.iter_errors(numeric_offset_export)
    )
    assert export_time_errors
