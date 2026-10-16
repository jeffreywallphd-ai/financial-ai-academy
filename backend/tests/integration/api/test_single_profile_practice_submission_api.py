from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
import pytest

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.hosts.api.generate_openapi import generate_bytes
from financial_ai_academy.modules.assessment.domain.practice import (
    MultipleSelectPracticeResponse,
    NumericEntryPracticeResponse,
    PracticeFeedback,
    PracticeItemOutcome,
    SingleSelectPracticeResponse,
)
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    AssessmentErrorCode,
    PracticeResult,
    SubmitPlacedPracticeRequest,
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


REPOSITORY = Path(__file__).resolve().parents[4]
SUBMISSION_PATH = (
    REPOSITORY
    / "contracts/compatibility/assessment-practice/v1/approved/submission.json"
)
OPENAPI_PATH = REPOSITORY / "contracts/api/openapi.json"
ORIGIN = "http://127.0.0.1:8000"
COOKIE = "a" * 43
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
ATTEMPT_ID = "33333333-3333-4333-8333-333333333333"
EVIDENCE_ID = "44444444-4444-4444-8444-444444444444"
FINGERPRINT = "c" * 64


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
            expires_at=datetime(2026, 10, 17, tzinfo=timezone.utc),
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


def _feedback(identifier: str, text: str) -> PracticeFeedback:
    return PracticeFeedback(
        feedback_id=identifier,
        text=text,
        review_reference_ids=("risk-return-review",),
    )


def _result(*, learner_id: str = LEARNER_ID) -> PracticeResult:
    return PracticeResult(
        schema_version="1.0.0",
        attempt_id=ATTEMPT_ID,
        evidence_id=EVIDENCE_ID,
        learner_id=learner_id,
        submission_id="22222222-2222-4222-8222-222222222222",
        request_fingerprint=FINGERPRINT,
        placement_id="risk-return-practice-placement",
        package_id="intro-risk-return",
        package_version="2.0.0",
        package_digest="a" * 64,
        definition_digest=(
            "82cdc82c402aacdb0070fb19671d896ae22a4c16d338ccbf27f02a51a396d527"
        ),
        practice_id="risk-return-practice",
        practice_version="1.0.0",
        attempt_policy_id="formative-retry",
        attempt_policy_version="1.0.0",
        score=2,
        max_score=3,
        outcome="review_needed",
        review_reference_ids=("risk-return-review",),
        item_results=(
            PracticeItemOutcome(
                response=SingleSelectPracticeResponse(
                    item_id="risk-meaning",
                    item_version="1.0.0",
                    item_type="single_select",
                    scoring_policy_id="single-select-exact-match",
                    scoring_policy_version="1.0.0",
                    selected_option_id="uncertainty",
                ),
                score=1,
                max_score=1,
                correct=True,
                feedback=_feedback(
                    "risk-correct",
                    "Correct. Risk includes uncertainty about future outcomes.",
                ),
            ),
            PracticeItemOutcome(
                response=MultipleSelectPracticeResponse(
                    item_id="diversification-actions",
                    item_version="1.0.0",
                    item_type="multiple_select",
                    scoring_policy_id="multiple-select-exact-set",
                    scoring_policy_version="1.0.0",
                    selected_option_ids=("more-issuers", "same-copy"),
                ),
                score=0,
                max_score=1,
                correct=False,
                feedback=_feedback(
                    "diversification-review",
                    "Review what changes exposure instead of merely "
                    "relabeling one position.",
                ),
            ),
            PracticeItemOutcome(
                response=NumericEntryPracticeResponse(
                    item_id="simple-growth",
                    item_version="1.0.0",
                    item_type="numeric_entry",
                    scoring_policy_id="numeric-exact-or-inclusive-range",
                    scoring_policy_version="1.0.0",
                    entered_value="105.00",
                ),
                score=1,
                max_score=1,
                correct=True,
                feedback=_feedback(
                    "growth-correct",
                    "Correct. Five percent of 100.00 is 5.00.",
                ),
            ),
        ),
        submitted_at=datetime(2026, 10, 16, 15, tzinfo=timezone.utc),
    )


class _Assessment:
    def __init__(self) -> None:
        self.calls = 0
        self.submission: SubmitPlacedPracticeRequest | None = None
        self.error: AssessmentError | None = None
        self.result = _result()

    def submit_placed_practice(
        self, request: SubmitPlacedPracticeRequest
    ) -> PracticeResult:
        self.calls += 1
        self.submission = request
        if self.error is not None:
            raise self.error
        return self.result


def _submission() -> dict[str, object]:
    return json.loads(SUBMISSION_PATH.read_text(encoding="utf-8"))


def _client(
    assessment: _Assessment | None = None,
    *,
    configured: bool = True,
) -> tuple[TestClient, _Assessment]:
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
                assessment=service if configured else None,
            )
        ),
        base_url=ORIGIN,
    )
    client.cookies.set("financial_ai_academy_session", COOKIE)
    return client, service


def _post(client: TestClient, body: dict[str, object] | None = None):
    return client.post(
        "/api/v1/curriculum/placements/"
        "risk-return-practice-placement/practice/submissions",
        headers={"Origin": ORIGIN, "Sec-Fetch-Site": "same-origin"},
        json=body or _submission(),
    )


def test_direct_client_uses_server_learner_and_receives_safe_ordered_result() -> None:
    client, service = _client()

    response = _post(client)

    assert response.status_code == 200
    assert service.calls == 1
    assert service.submission is not None
    assert service.submission.learner_id == LEARNER_ID
    assert service.submission.placement_id == "risk-return-practice-placement"
    assert json.loads(service.submission.submission) == _submission()
    body = response.json()
    assert UUID(body["attempt_id"]) == UUID(ATTEMPT_ID)
    assert UUID(body["evidence_id"]) == UUID(EVIDENCE_ID)
    assert body["score"] == 2
    assert body["max_score"] == 3
    assert body["outcome"] == "review_needed"
    assert [item["item_type"] for item in body["item_results"]] == [
        "single_select",
        "multiple_select",
        "numeric_entry",
    ]
    assert body["item_results"][2]["entered_value"] == "105.00"
    assert "learner_id" not in response.text
    assert "request_fingerprint" not in response.text
    assert FINGERPRINT not in response.text
    for private_name in (
        "correct_option_id",
        "correct_option_ids",
        "answer",
        "evaluator",
    ):
        assert private_name not in response.text


def test_route_mismatch_and_caller_selected_identity_fail_before_service() -> None:
    client, service = _client()
    mismatch = _submission()
    mismatch["placement_id"] = "different-practice-placement"

    stale = _post(client, mismatch)
    selected = _submission()
    selected["learner_id"] = "client-selected"
    extra = _post(client, selected)

    assert stale.status_code == 409
    assert stale.json()["code"] == "stale_reference"
    assert extra.status_code == 400
    assert extra.json()["code"] == "invalid_request"
    assert service.calls == 0
    assert "client-selected" not in extra.text


def test_missing_session_query_input_and_duplicate_selection_fail_closed() -> None:
    client, service = _client()
    client.cookies.clear()
    missing = _post(client)
    client.cookies.set("financial_ai_academy_session", COOKIE)
    query = client.post(
        "/api/v1/curriculum/placements/"
        "risk-return-practice-placement/practice/submissions?learner_id=selected",
        headers={"Origin": ORIGIN, "Sec-Fetch-Site": "same-origin"},
        json=_submission(),
    )
    duplicate = _submission()
    responses = duplicate["responses"]
    assert isinstance(responses, list)
    multiple = next(
        item for item in responses if item["item_type"] == "multiple_select"
    )
    multiple["selected_option_ids"] = ["more-issuers", "more-issuers"]
    invalid = _post(client, duplicate)

    assert missing.status_code == 401
    assert query.status_code == 400
    assert query.json()["code"] == "invalid_submission"
    assert "selected" not in query.text
    assert invalid.status_code == 400
    assert invalid.json()["code"] == "invalid_request"
    assert service.calls == 0


@pytest.mark.parametrize(
    ("code", "expected_status"),
    [
        (AssessmentErrorCode.INVALID_SUBMISSION, 400),
        (AssessmentErrorCode.UNKNOWN_OPTION, 400),
        (AssessmentErrorCode.UNAUTHORIZED_CONTEXT, 401),
        (AssessmentErrorCode.NOT_FOUND, 404),
        (AssessmentErrorCode.UNSUPPORTED_VERSION, 409),
        (AssessmentErrorCode.STALE_REFERENCE, 409),
        (AssessmentErrorCode.CONFLICT, 409),
        (AssessmentErrorCode.ALREADY_COMPLETED, 409),
        (AssessmentErrorCode.INVALID_DEFINITION, 503),
        (AssessmentErrorCode.UNAVAILABLE, 503),
    ],
)
def test_assessment_denials_have_stable_public_status_without_diagnostics(
    code: AssessmentErrorCode, expected_status: int
) -> None:
    assessment = _Assessment()
    assessment.error = AssessmentError(
        code,
        "The practice request could not be completed.",
        diagnostic_code="private.storage.answer-detail",
    )
    client, _service = _client(assessment)

    response = _post(client)

    assert response.status_code == expected_status
    assert response.json()["code"] == code.value
    assert "private.storage.answer-detail" not in response.text


def test_unconfigured_service_and_invalid_service_result_fail_closed() -> None:
    no_service, absent = _client(configured=False)
    unavailable = _post(no_service)

    assessment = _Assessment()
    assessment.result = replace(assessment.result, package_version="latest")
    invalid_client, _service = _client(assessment)
    invalid = _post(invalid_client)

    assert unavailable.status_code == 503
    assert unavailable.json()["code"] == "unavailable"
    assert absent.calls == 0
    assert invalid.status_code == 500
    assert invalid.json()["code"] == "internal_error"
    assert "latest" not in invalid.text


def test_openapi_snapshot_exposes_the_exact_headless_operation() -> None:
    generated = generate_bytes()
    assert generated == OPENAPI_PATH.read_bytes()
    schema = json.loads(generated)
    operation = schema["paths"][
        "/api/v1/curriculum/placements/{placement_id}/practice/submissions"
    ]["post"]

    assert operation["operationId"] == "submitPlacedPractice"
    assert operation["security"] == [{"OpaqueSessionCookie": []}]
    assert "422" not in operation["responses"]
    request_schema = operation["requestBody"]["content"][
        "application/json"
    ]["schema"]
    assert request_schema == {
        "$ref": "#/components/schemas/PracticeSubmissionRequestModel"
    }
    serialized = json.dumps(operation, sort_keys=True)
    assert "learner_id" not in serialized
    assert "request_fingerprint" not in serialized


def test_transport_accepts_varied_valid_item_counts_and_request_order() -> None:
    client, service = _client()
    body = _submission()
    responses = body["responses"]
    assert isinstance(responses, list)
    body["responses"] = [responses[1]]
    service.result = replace(
        service.result,
        score=1,
        max_score=1,
        outcome="all_correct",
        item_results=(service.result.item_results[0],),
    )

    response = _post(client, deepcopy(body))

    assert response.status_code == 200
    assert len(response.json()["item_results"]) == 1
    assert response.json()["item_results"][0]["item_id"] == "risk-meaning"
