from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi.testclient import TestClient

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    AssessmentErrorCode,
    KnowledgeCheckFeedback,
    KnowledgeCheckOption,
    KnowledgeCheckPresentation,
    KnowledgeCheckResult,
    OpenPlacedKnowledgeCheckRequest,
    SubmitPlacedKnowledgeCheckRequest,
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


ORIGIN = "http://127.0.0.1:8000"
COOKIE = "a" * 43
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
SUBMISSION_ID = "22222222-2222-4222-8222-222222222222"
DIGEST = "a" * 64
DEFINITION_DIGEST = "b" * 64


class _Identity:
    def resolve_session(self, cookie_value: str | None) -> LearnerContext:
        if cookie_value != COOKIE:
            raise IdentityError(
                IdentityErrorCode.UNAUTHORIZED,
                "A valid learner session is required.",
            )
        return LearnerContext(
            actor_id="33333333-3333-4333-8333-333333333333",
            learner_id=LEARNER_ID,
            session_id="44444444-4444-4444-8444-444444444444",
            authenticated_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
            expires_at=datetime(2026, 10, 16, tzinfo=timezone.utc),
            authentication_method="single_profile",
            permissions=("curriculum.lesson.read",),
        )

    def bootstrap_single_profile(self, request: object) -> object:
        raise NotImplementedError

    def revoke_session(self, cookie_value: str | None) -> None:
        return None

    def health(self) -> bool:
        return True


class _Curriculum:
    def open_placed_lesson(self, request: object) -> object:
        raise NotImplementedError


class _Assessment:
    def __init__(self) -> None:
        self.submission: SubmitPlacedKnowledgeCheckRequest | None = None
        self.error: AssessmentError | None = None

    def open_placed_knowledge_check(
        self, request: OpenPlacedKnowledgeCheckRequest
    ) -> KnowledgeCheckPresentation:
        assert request.placement_id == "intro-risk-return-check"
        return _presentation()

    def submit_placed_knowledge_check(
        self, request: SubmitPlacedKnowledgeCheckRequest
    ) -> KnowledgeCheckResult:
        if self.error is not None:
            raise self.error
        self.submission = request
        return KnowledgeCheckResult(
            attempt_id="55555555-5555-4555-8555-555555555555",
            evidence_id="66666666-6666-4666-8666-666666666666",
            learner_id=request.learner_id,
            submission_id=request.submission_id,
            placement_id=request.placement_id,
            package_id=request.package_id,
            package_version=request.package_version,
            package_digest=request.package_digest,
            assessment_id=request.assessment_id,
            assessment_version=request.assessment_version,
            definition_digest=request.definition_digest,
            item_id=request.item_id,
            item_version=request.item_version,
            scoring_policy_id=request.scoring_policy_id,
            scoring_policy_version=request.scoring_policy_version,
            selected_option_id=request.selected_option_id,
            score=1,
            max_score=1,
            correct=True,
            feedback=KnowledgeCheckFeedback(
                "risk-return-correct",
                "Correct. Higher potential return generally comes with higher uncertainty.",
            ),
            submitted_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
        )


def _presentation() -> KnowledgeCheckPresentation:
    return KnowledgeCheckPresentation(
        placement_id="intro-risk-return-check",
        package_id="intro-risk-return",
        package_version="1.1.0",
        package_digest=DIGEST,
        assessment_id="risk-return-check-1",
        assessment_version="1.0.0",
        definition_digest=DEFINITION_DIGEST,
        item_type="single_select",
        item_id="risk-return-question-1",
        item_version="1.0.0",
        scoring_policy_id="single-select-exact-match",
        scoring_policy_version="1.0.0",
        prompt="Which statement best describes the relationship between risk and return?",
        options=(
            KnowledgeCheckOption(
                "higher-potential-higher-uncertainty",
                "Higher potential return generally comes with higher uncertainty.",
            ),
            KnowledgeCheckOption(
                "higher-risk-guarantees-return",
                "Taking more risk guarantees a higher return.",
            ),
        ),
    )


def _request_body() -> dict[str, object]:
    value = _presentation()
    return {
        "schema_version": "1.0.0",
        "submission_id": SUBMISSION_ID,
        "placement_id": value.placement_id,
        "package_id": value.package_id,
        "package_version": value.package_version,
        "package_digest": value.package_digest,
        "assessment_id": value.assessment_id,
        "assessment_version": value.assessment_version,
        "definition_digest": value.definition_digest,
        "item_id": value.item_id,
        "item_version": value.item_version,
        "scoring_policy_id": value.scoring_policy_id,
        "scoring_policy_version": value.scoring_policy_version,
        "selected_option_id": "higher-potential-higher-uncertainty",
    }


def _client(assessment: _Assessment | None = None) -> tuple[TestClient, _Assessment]:
    service = assessment or _Assessment()
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
                identity=_Identity(),  # type: ignore[arg-type]
                curriculum=_Curriculum(),  # type: ignore[arg-type]
                request_policy=policy,
                assessment=service,
            )
        ),
        base_url=ORIGIN,
    )
    client.cookies.set("financial_ai_academy_session", COOKIE)
    return client, service


def test_presentation_exposes_safe_choices_without_answer_key() -> None:
    client, _service = _client()

    response = client.get(
        "/api/v1/curriculum/placements/intro-risk-return-check/knowledge-check"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["assessment_id"] == "risk-return-check-1"
    assert len(body["options"]) == 2
    assert "correct" not in response.text.casefold()
    assert "learner_id" not in response.text


def test_submission_uses_server_learner_and_returns_bounded_result() -> None:
    client, service = _client()

    response = client.post(
        "/api/v1/curriculum/placements/intro-risk-return-check/knowledge-check/submissions",
        headers={"Origin": ORIGIN, "Sec-Fetch-Site": "same-origin"},
        json=_request_body(),
    )

    assert response.status_code == 200
    assert service.submission is not None
    assert service.submission.learner_id == LEARNER_ID
    assert UUID(response.json()["attempt_id"])
    assert response.json()["score"] == 1
    assert "learner_id" not in response.text


def test_missing_context_and_client_selected_identity_fail_before_submission() -> None:
    client, service = _client()
    client.cookies.clear()
    missing = client.post(
        "/api/v1/curriculum/placements/intro-risk-return-check/knowledge-check/submissions",
        headers={"Origin": ORIGIN},
        json=_request_body(),
    )
    client.cookies.set("financial_ai_academy_session", COOKIE)
    selected = _request_body()
    selected["learner_id"] = "client-selected"
    extra = client.post(
        "/api/v1/curriculum/placements/intro-risk-return-check/knowledge-check/submissions",
        headers={"Origin": ORIGIN},
        json=selected,
    )

    assert missing.status_code == 401
    assert extra.status_code == 400
    assert service.submission is None
    assert "client-selected" not in extra.text


def test_conflict_is_stable_and_unconfigured_service_fails_closed() -> None:
    assessment = _Assessment()
    assessment.error = AssessmentError(
        AssessmentErrorCode.CONFLICT,
        "The submission identity was already used for different input.",
    )
    client, _service = _client(assessment)
    conflict = client.post(
        "/api/v1/curriculum/placements/intro-risk-return-check/knowledge-check/submissions",
        headers={"Origin": ORIGIN},
        json=_request_body(),
    )

    policy = SingleProfileRequestPolicy(
        SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin=ORIGIN,
            allowed_hosts=("127.0.0.1:8000",),
            secure_cookie=False,
        )
    )
    no_service = TestClient(
        create_app(
            ApiServices(
                identity=_Identity(),  # type: ignore[arg-type]
                curriculum=_Curriculum(),  # type: ignore[arg-type]
                request_policy=policy,
            )
        ),
        base_url=ORIGIN,
    )
    no_service.cookies.set("financial_ai_academy_session", COOKIE)
    absent = no_service.get(
        "/api/v1/curriculum/placements/intro-risk-return-check/knowledge-check"
    )

    assert conflict.status_code == 409
    assert conflict.json()["code"] == "conflict"
    assert absent.status_code == 503
    assert absent.json()["code"] == "unavailable"
