from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.modules.audit.public import (
    AuditError,
    AuditErrorCode,
    AuditReconciliationReceipt,
    ReconcileLessonCompletionAuditRequest,
)
from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    LearnerContext,
)
from financial_ai_academy.modules.learner_model.public import (
    LearnerModelError,
    LearnerModelErrorCode,
    LessonCompletionHistoryEntry,
    LessonCompletionView,
    OpenLessonCompletionRequest,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)


ORIGIN = "http://127.0.0.1:8000"
COOKIE = "a" * 43
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)
DIGEST = "a" * 64
DEFINITION_DIGEST = "b" * 64
SOURCE_DIGEST = "c" * 64


class Identity:
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
            authenticated_at=NOW,
            expires_at=datetime(2026, 10, 16, tzinfo=timezone.utc),
            authentication_method="single_profile",
            permissions=("curriculum.lesson.read",),
        )

    def health(self) -> bool:
        return True


class Curriculum:
    pass


class Audit:
    def __init__(self, order: list[str]) -> None:
        self.order = order
        self.request: ReconcileLessonCompletionAuditRequest | None = None
        self.error: AuditError | None = None

    def reconcile_lesson_completion(
        self, request: ReconcileLessonCompletionAuditRequest
    ) -> AuditReconciliationReceipt:
        self.order.append("audit")
        self.request = request
        if self.error is not None:
            raise self.error
        return AuditReconciliationReceipt(
            request.placement_id, 1, SOURCE_DIGEST
        )


class LearnerModel:
    def __init__(self, order: list[str], *, empty: bool = False) -> None:
        self.order = order
        self.empty = empty
        self.request: OpenLessonCompletionRequest | None = None
        self.error: LearnerModelError | None = None

    def open_lesson_completion(
        self, request: OpenLessonCompletionRequest
    ) -> LessonCompletionView:
        self.order.append("learner_model")
        self.request = request
        if self.error is not None:
            raise self.error
        history = () if self.empty else (_history(),)
        return LessonCompletionView(
            placement_id=request.placement_id,
            completed=not self.empty,
            completion_meaning=(
                "not_completed"
                if self.empty
                else "bounded_knowledge_check_completed"
            ),
            source_digest=SOURCE_DIGEST,
            rebuilt_at=NOW,
            history=history,
        )


def _history() -> LessonCompletionHistoryEntry:
    return LessonCompletionHistoryEntry(
        event_id="44444444-4444-4444-8444-444444444444",
        attempt_id="55555555-5555-4555-8555-555555555555",
        evidence_id="66666666-6666-4666-8666-666666666666",
        package_id="intro-risk-return",
        package_version="1.1.0",
        package_digest=DIGEST,
        assessment_id="risk-return-check-1",
        assessment_version="1.0.0",
        definition_digest=DEFINITION_DIGEST,
        item_id="risk-return-tradeoff",
        item_version="1.0.0",
        scoring_policy_id="single-select-exact-match",
        scoring_policy_version="1.0.0",
        score=1,
        max_score=1,
        completed_at=NOW,
    )


def _client(
    *, empty: bool = False, configured: bool = True
) -> tuple[TestClient, Audit, LearnerModel, list[str]]:
    order: list[str] = []
    audit = Audit(order)
    learner_model = LearnerModel(order, empty=empty)
    policy = SingleProfileRequestPolicy(
        SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin=ORIGIN,
            allowed_hosts=("127.0.0.1:8000",),
            secure_cookie=False,
        )
    )
    client = TestClient(
        create_app(
            ApiServices(
                identity=Identity(),  # type: ignore[arg-type]
                curriculum=Curriculum(),  # type: ignore[arg-type]
                request_policy=policy,
                learner_model=learner_model if configured else None,
                audit=audit if configured else None,
            )
        ),
        base_url=ORIGIN,
    )
    client.cookies.set("financial_ai_academy_session", COOKIE)
    return client, audit, learner_model, order


def test_completion_history_is_server_bound_and_audit_first() -> None:
    client, audit, learner_model, order = _client()
    response = client.get(
        "/api/v1/curriculum/placements/intro-risk-return/completion"
    )
    assert response.status_code == 200
    body = response.json()
    assert order == ["audit", "learner_model"]
    assert audit.request is not None and audit.request.learner_id == LEARNER_ID
    assert learner_model.request is not None
    assert body["completed"] is True
    assert body["history"][0]["package_version"] == "1.1.0"
    assert body["history"][0]["score"] == 1
    assert "learner_id" not in response.text
    assert "master" not in response.text.casefold()


def test_empty_history_is_explicit() -> None:
    client, _audit, _learner_model, _order = _client(empty=True)
    response = client.get(
        "/api/v1/curriculum/placements/intro-risk-return/completion"
    )
    assert response.status_code == 200
    assert response.json()["completed"] is False
    assert response.json()["completion_meaning"] == "not_completed"
    assert response.json()["history"] == []


def test_missing_or_client_selected_identity_never_reaches_consumers() -> None:
    client, audit, learner_model, order = _client()
    client.cookies.clear()
    missing = client.get(
        "/api/v1/curriculum/placements/intro-risk-return/completion"
    )
    client.cookies.set("financial_ai_academy_session", COOKIE)
    selected = client.get(
        "/api/v1/curriculum/placements/intro-risk-return/completion",
        headers={"X-Learner-ID": "client-selected"},
    )
    assert missing.status_code == 401
    assert selected.status_code == 403
    assert order == []
    assert audit.request is None
    assert learner_model.request is None


def test_audit_and_projection_failures_are_ordered_and_bounded() -> None:
    client, audit, learner_model, order = _client()
    audit.error = AuditError(
        AuditErrorCode.CONFLICT,
        "An Audit event identity conflicts with retained evidence.",
    )
    conflict = client.get(
        "/api/v1/curriculum/placements/intro-risk-return/completion"
    )
    assert conflict.status_code == 409
    assert order == ["audit"]

    client, _audit, learner_model, order = _client()
    learner_model.error = LearnerModelError(
        LearnerModelErrorCode.UNAVAILABLE,
        "The completion view is temporarily unavailable.",
    )
    unavailable = client.get(
        "/api/v1/curriculum/placements/intro-risk-return/completion"
    )
    assert unavailable.status_code == 503
    assert order == ["audit", "learner_model"]


def test_unconfigured_consumers_fail_closed() -> None:
    client, _audit, _learner_model, _order = _client(configured=False)
    response = client.get(
        "/api/v1/curriculum/placements/intro-risk-return/completion"
    )
    assert response.status_code == 503
    assert response.json()["code"] == "unavailable"
