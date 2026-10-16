from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.modules.assessment.adapters.practice_contract import (
    ContractPracticeDefinitionAdapter,
)
from financial_ai_academy.modules.assessment.domain.practice import (
    PracticePresentation,
    PracticePresentationContext,
)
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    AssessmentErrorCode,
    OpenPlacedPracticeRequest,
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
SCHEMAS = REPOSITORY / "contracts/learning/assessment/practice/v1"
DEFINITION = (
    REPOSITORY
    / "contracts/compatibility/assessment-practice/v1/approved/definition.json"
)
ORIGIN = "http://127.0.0.1:8000"
COOKIE = "a" * 43


class _Identity:
    def resolve_session(self, cookie_value: str | None) -> LearnerContext:
        if cookie_value != COOKIE:
            raise IdentityError(
                IdentityErrorCode.UNAUTHORIZED,
                "A valid learner session is required.",
            )
        return LearnerContext(
            actor_id="33333333-3333-4333-8333-333333333333",
            learner_id="11111111-1111-4111-8111-111111111111",
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
        self.presentation = _presentation()
        self.error: AssessmentError | None = None
        self.calls = 0

    def open_placed_practice(
        self, request: OpenPlacedPracticeRequest
    ) -> PracticePresentation:
        self.calls += 1
        if self.error is not None:
            raise self.error
        assert request.placement_id == "intro-risk-return-primary"
        return self.presentation


def _presentation() -> PracticePresentation:
    parser = ContractPracticeDefinitionAdapter(SCHEMAS)
    return parser.project(
        parser.parse(DEFINITION.read_bytes()),
        PracticePresentationContext(
            placement_id="intro-risk-return-primary",
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest="a" * 64,
        ),
    )


def _client(
    assessment: _Assessment | None = None,
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
                assessment=service,  # type: ignore[arg-type]
            )
        ),
        base_url=ORIGIN,
    )
    client.cookies.set("financial_ai_academy_session", COOKIE)
    return client, service


def test_authorized_api_returns_answer_safe_practice_for_headless_clients() -> None:
    client, service = _client()

    response = client.get(
        "/api/v1/curriculum/placements/intro-risk-return-primary/practice"
    )

    assert response.status_code == 200
    assert service.calls == 1
    body = response.json()
    assert body["practice_id"] == "risk-return-practice"
    assert [item["item_type"] for item in body["items"]] == [
        "single_select",
        "multiple_select",
        "numeric_entry",
    ]
    private_names = {
        "answer",
        "correct_option_id",
        "correct_option_ids",
        "feedback",
    }
    assert private_names.isdisjoint(response.text.split('"'))


def test_missing_session_and_client_selected_identity_fail_before_service() -> None:
    client, service = _client()
    client.cookies.clear()

    missing = client.get(
        "/api/v1/curriculum/placements/intro-risk-return-primary/practice"
    )
    client.cookies.set("financial_ai_academy_session", COOKIE)
    selected = client.get(
        "/api/v1/curriculum/placements/intro-risk-return-primary/practice",
        params={"learner_id": "client-selected"},
    )

    assert missing.status_code == 401
    assert selected.status_code == 400
    assert service.calls == 0
    assert "client-selected" not in selected.text


@pytest.mark.parametrize(
    ("code", "expected_status"),
    [
        (AssessmentErrorCode.NOT_FOUND, 404),
        (AssessmentErrorCode.STALE_REFERENCE, 409),
        (AssessmentErrorCode.UNAVAILABLE, 503),
    ],
)
def test_practice_failures_are_bounded_and_do_not_leak_diagnostics(
    code: AssessmentErrorCode,
    expected_status: int,
) -> None:
    assessment = _Assessment()
    assessment.error = AssessmentError(
        code,
        "Practice activities are unavailable.",
        diagnostic_code="private.storage.detail",
    )
    client, _service = _client(assessment)

    response = client.get(
        "/api/v1/curriculum/placements/intro-risk-return-primary/practice"
    )

    assert response.status_code == expected_status
    assert response.json()["code"] == code.value
    assert "private.storage.detail" not in response.text


def test_unconfigured_practice_service_fails_closed() -> None:
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

    response = no_service.get(
        "/api/v1/curriculum/placements/intro-risk-return-primary/practice"
    )

    assert response.status_code == 503
    assert response.json()["code"] == "unavailable"


def test_response_validation_rejects_private_or_invalid_service_output() -> None:
    assessment = _Assessment()
    assessment.presentation = replace(
        assessment.presentation,
        package_version="not-a-version",
    )
    client, _service = _client(assessment)

    response = client.get(
        "/api/v1/curriculum/placements/intro-risk-return-primary/practice"
    )

    assert response.status_code == 500
    assert response.json()["code"] == "internal_error"
