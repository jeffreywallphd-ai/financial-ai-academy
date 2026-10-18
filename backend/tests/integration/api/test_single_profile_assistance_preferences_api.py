from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    LearnerContext,
)
from financial_ai_academy.modules.learner_model.adapters.assistance_preference_contract import (
    ContractAssistancePreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.domain.assistance_preferences import (
    AssistancePreferenceExport,
    AssistancePreferenceHistory,
    AssistancePreferenceMutation,
    AssistancePreferenceMutationIntent,
)
from financial_ai_academy.modules.learner_model.public import (
    ExportAssistancePreferencesRequest,
    LearnerModelError,
    LearnerModelErrorCode,
    MutateAssistancePreferencesRequest,
    OpenAssistancePreferencesRequest,
    ReadAssistancePreferenceHistoryRequest,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = (
    ROOT / "contracts" / "learning" / "learner-assistance-preferences" / "v1"
)
ORIGIN = "http://127.0.0.1:8000"
COOKIE_NAME = "financial_ai_academy_session"
COOKIE = "a" * 43
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 10, 17, 23, 0, tzinfo=timezone.utc)


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
            authenticated_at=NOW,
            expires_at=NOW + timedelta(days=1),
            authentication_method="single_profile",
            permissions=self.permissions,
        )

    def bootstrap_single_profile(self, request: object) -> object:
        raise NotImplementedError

    def revoke_session(self, cookie_value: str | None) -> None:
        return None

    def health(self) -> bool:
        return True


class Curriculum:
    pass


class AssistancePreferences:
    def __init__(self, *, error: LearnerModelErrorCode | None = None) -> None:
        contract = ContractAssistancePreferenceAdapter(SCHEMA_DIR)
        self.profile = contract.default_profile(
            profile_id="assistance.api-fixture",
            learner_id=LEARNER_ID,
            created_at=NOW,
        )
        self.intent = AssistancePreferenceMutationIntent(
            schema_version="1.0.0",
            idempotency_key="assistance.api-fixture",
            expected_revision=1,
            mutation=AssistancePreferenceMutation(
                operation="replace_preferences",
                assistance_mode="on_request",
            ),
        )
        self.accepted, change = contract.apply_mutation(
            self.profile,
            self.intent,
            occurred_at=NOW + timedelta(minutes=1),
        )
        self.reset_intent = AssistancePreferenceMutationIntent(
            schema_version="1.0.0",
            idempotency_key="assistance.api-reset",
            expected_revision=self.accepted.revision,
            mutation=AssistancePreferenceMutation(operation="reset_profile"),
        )
        self.reset, _ = contract.apply_mutation(
            self.accepted,
            self.reset_intent,
            occurred_at=NOW + timedelta(minutes=2),
        )
        self.history = AssistancePreferenceHistory(
            schema_version="1.0.0",
            profile_id=self.accepted.profile_id,
            current_revision=self.accepted.revision,
            changes=(change,),
        )
        self.export = AssistancePreferenceExport(
            schema_version="1.0.0",
            purpose="A portable copy of the AI-help choice you selected.",
            limitations=(
                "On request records your choice only and does not enable or call an AI service.",
                "This choice is not learning evidence or permission to share data.",
            ),
            exported_at=NOW + timedelta(minutes=2),
            profile=self.accepted,
            history=self.history,
        )
        self.error = error
        self.open_requests: list[OpenAssistancePreferencesRequest] = []
        self.mutation_requests: list[MutateAssistancePreferencesRequest] = []
        self.history_requests: list[ReadAssistancePreferenceHistoryRequest] = []
        self.export_requests: list[ExportAssistancePreferencesRequest] = []

    def _fail(self) -> None:
        if self.error is not None:
            raise LearnerModelError(
                self.error,
                "The AI-help preference request could not be completed.",
                reference="private-fixture",
            )

    def open_assistance_preferences(
        self, request: OpenAssistancePreferencesRequest
    ):
        self.open_requests.append(request)
        self._fail()
        return self.profile

    def mutate_assistance_preferences(
        self, request: MutateAssistancePreferencesRequest
    ):
        self.mutation_requests.append(request)
        self._fail()
        return (
            self.reset
            if request.intent.mutation.operation == "reset_profile"
            else self.accepted
        )

    def read_assistance_preference_history(
        self, request: ReadAssistancePreferenceHistoryRequest
    ):
        self.history_requests.append(request)
        self._fail()
        return self.history

    def export_assistance_preferences(
        self, request: ExportAssistancePreferencesRequest
    ):
        self.export_requests.append(request)
        self._fail()
        return self.export


def client(
    permissions: tuple[str, ...], preferences: AssistancePreferences
) -> TestClient:
    policy = SingleProfileRequestPolicy(
        SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin=ORIGIN,
            allowed_hosts=("127.0.0.1:8000",),
            secure_cookie=False,
        )
    )
    result = TestClient(
        create_app(
            ApiServices(
                identity=Identity(permissions),  # type: ignore[arg-type]
                curriculum=Curriculum(),  # type: ignore[arg-type]
                request_policy=policy,
                learner_model=preferences,  # type: ignore[arg-type]
            )
        ),
        base_url=ORIGIN,
    )
    result.cookies.set(COOKIE_NAME, COOKIE)
    return result


def mutation_body() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "idempotency_key": "assistance.api-change",
        "expected_revision": 1,
        "mutation": {
            "operation": "replace_preferences",
            "assistance_mode": "on_request",
        },
    }


def reset_body() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "idempotency_key": "assistance.api-reset",
        "expected_revision": 2,
        "mutation": {"operation": "reset_profile"},
    }


def test_headless_routes_use_server_learner_and_frozen_shapes() -> None:
    preferences = AssistancePreferences()
    subject = client(("learner_assistance_preferences.read",), preferences)

    profile = subject.get("/api/v1/learner-assistance-preferences")
    history = subject.get("/api/v1/learner-assistance-preferences/history")
    exported = subject.get("/api/v1/learner-assistance-preferences/export")

    assert profile.status_code == history.status_code == exported.status_code == 200
    assert profile.json()["learner_id"] == LEARNER_ID
    assert profile.json()["assistance_mode"] == "off"
    assert profile.json()["created_at"].endswith("Z")
    assert history.json()["current_revision"] == 2
    export_document = exported.json()
    assert export_document["profile"]["learner_id"] == LEARNER_ID
    assert "provider" not in export_document["profile"]
    assert "local_reminder" not in export_document["profile"]
    assert preferences.open_requests == [OpenAssistancePreferencesRequest(LEARNER_ID)]
    assert preferences.history_requests == [
        ReadAssistancePreferenceHistoryRequest(LEARNER_ID)
    ]
    assert preferences.export_requests == [
        ExportAssistancePreferencesRequest(LEARNER_ID)
    ]


def test_mutation_and_reset_use_server_learner_and_closed_intents() -> None:
    preferences = AssistancePreferences()
    mutated = client(
        ("learner_assistance_preferences.write",), preferences
    ).post(
        "/api/v1/learner-assistance-preferences/mutations",
        json=mutation_body(),
        headers={"Origin": ORIGIN},
    )
    reset = client(
        ("learner_assistance_preferences.write",), preferences
    ).post(
        "/api/v1/learner-assistance-preferences/mutations",
        json=reset_body(),
        headers={"Origin": ORIGIN},
    )

    assert (mutated.status_code, mutated.json()["assistance_mode"]) == (
        200,
        "on_request",
    )
    assert (reset.status_code, reset.json()["assistance_mode"]) == (200, "off")
    assert all(
        request.learner_id == LEARNER_ID
        for request in preferences.mutation_requests
    )
    assert preferences.mutation_requests[0].intent.mutation.assistance_mode == (
        "on_request"
    )
    assert preferences.mutation_requests[1].intent == preferences.reset_intent


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/api/v1/learner-assistance-preferences"),
        ("get", "/api/v1/learner-assistance-preferences/history"),
        ("get", "/api/v1/learner-assistance-preferences/export"),
        ("post", "/api/v1/learner-assistance-preferences/mutations"),
    ],
)
def test_routes_require_their_exact_permission(method: str, path: str) -> None:
    preferences = AssistancePreferences()
    kwargs = (
        {"json": mutation_body(), "headers": {"Origin": ORIGIN}}
        if method == "post"
        else {}
    )
    response = getattr(client((), preferences), method)(path, **kwargs)

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"
    assert not (
        preferences.open_requests
        or preferences.mutation_requests
        or preferences.history_requests
        or preferences.export_requests
    )


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/learner-assistance-preferences?learner_id=someone-else",
        "/api/v1/learner-assistance-preferences/history?limit=1",
        "/api/v1/learner-assistance-preferences/export?include_private=true",
    ],
)
def test_reads_reject_all_query_input_before_service_access(path: str) -> None:
    preferences = AssistancePreferences()
    response = client(
        ("learner_assistance_preferences.read",), preferences
    ).get(path)

    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"
    assert not (
        preferences.open_requests
        or preferences.history_requests
        or preferences.export_requests
    )


@pytest.mark.parametrize(
    "change",
    [
        {"learner_id": "44444444-4444-4444-8444-444444444444"},
        {"provider": "example"},
        {"model": "example"},
        {"data_permission": "all"},
        {"local_reminder": "in_app_when_available"},
    ],
)
def test_mutation_rejects_identity_execution_and_local_fields(
    change: dict[str, object],
) -> None:
    preferences = AssistancePreferences()
    body = mutation_body()
    body.update(change)
    response = client(
        ("learner_assistance_preferences.write",), preferences
    ).post(
        "/api/v1/learner-assistance-preferences/mutations",
        json=body,
        headers={"Origin": ORIGIN},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"
    assert preferences.mutation_requests == []


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (LearnerModelErrorCode.INVALID_REQUEST, 400),
        (LearnerModelErrorCode.IMMUTABLE_CONFLICT, 409),
        (LearnerModelErrorCode.STALE_REVISION, 409),
        (LearnerModelErrorCode.INTEGRITY_FAILURE, 503),
        (LearnerModelErrorCode.UNAVAILABLE, 503),
    ],
)
def test_errors_have_safe_stable_http_mapping(
    error: LearnerModelErrorCode, expected_status: int
) -> None:
    response = client(
        ("learner_assistance_preferences.read",),
        AssistancePreferences(error=error),
    ).get("/api/v1/learner-assistance-preferences")

    assert response.status_code == expected_status
    assert response.json()["code"] == error.value
    assert "private-fixture" not in response.text


def test_openapi_exposes_one_browser_and_headless_contract() -> None:
    schema = client(
        ("learner_assistance_preferences.read",),
        AssistancePreferences(),
    ).app.openapi()

    assert schema["paths"]["/api/v1/learner-assistance-preferences"]["get"][
        "operationId"
    ] == "getLearnerAssistancePreferences"
    mutation = schema["paths"][
        "/api/v1/learner-assistance-preferences/mutations"
    ]["post"]
    assert mutation["operationId"] == "mutateLearnerAssistancePreferences"
    assert "422" not in mutation["responses"]
    assert schema["paths"][
        "/api/v1/learner-assistance-preferences/history"
    ]["get"]["operationId"] == "getLearnerAssistancePreferenceHistory"
    assert schema["paths"][
        "/api/v1/learner-assistance-preferences/export"
    ]["get"]["operationId"] == "exportLearnerAssistancePreferences"
