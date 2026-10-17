from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    LearnerContext,
)
from financial_ai_academy.modules.learner_model.adapters.preference_contract import (
    ContractLearnerPreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.domain.preferences import (
    canonical_digest,
)
from financial_ai_academy.modules.learner_model.public import (
    ExportLearnerPreferencesRequest,
    LearnerModelError,
    LearnerModelErrorCode,
    MutateLearnerPreferencesRequest,
    OpenLearnerPreferencesRequest,
    ReadLearnerPreferenceHistoryRequest,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = ROOT / "contracts" / "learning" / "learner-preferences" / "v1"
FIXTURE_DIR = (
    ROOT / "contracts" / "compatibility" / "learner-preferences" / "v1"
)
ORIGIN = "http://127.0.0.1:8000"
COOKIE_NAME = "financial_ai_academy_session"
COOKIE = "a" * 43
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 10, 17, 18, 0, tzinfo=timezone.utc)


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
            expires_at=datetime(2026, 10, 18, tzinfo=timezone.utc),
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


class Preferences:
    def __init__(
        self,
        *,
        error: LearnerModelErrorCode | None = None,
    ) -> None:
        contract = ContractLearnerPreferenceAdapter(SCHEMA_DIR)
        self.empty = contract.parse_profile(
            (FIXTURE_DIR / "valid-empty-profile.json").read_bytes()
        )
        self.populated = contract.parse_profile(
            (FIXTURE_DIR / "valid-populated-profile.json").read_bytes()
        )
        self.history = contract.parse_history(
            (FIXTURE_DIR / "valid-history.json").read_bytes()
        )
        self.export = contract.parse_export(
            (FIXTURE_DIR / "valid-export.json").read_bytes()
        )
        self.error = error
        self.open_requests: list[OpenLearnerPreferencesRequest] = []
        self.mutation_requests: list[MutateLearnerPreferencesRequest] = []
        self.history_requests: list[ReadLearnerPreferenceHistoryRequest] = []
        self.export_requests: list[ExportLearnerPreferencesRequest] = []

    def _fail(self) -> None:
        if self.error is not None:
            raise LearnerModelError(
                self.error,
                "The learning preference request could not be completed.",
                reference="fixture",
            )

    def open_preferences(self, request: OpenLearnerPreferencesRequest):
        self.open_requests.append(request)
        self._fail()
        return self.empty

    def mutate_preferences(self, request: MutateLearnerPreferencesRequest):
        self.mutation_requests.append(request)
        self._fail()
        return self.populated

    def read_preference_history(
        self, request: ReadLearnerPreferenceHistoryRequest
    ):
        self.history_requests.append(request)
        self._fail()
        return self.history

    def export_preferences(self, request: ExportLearnerPreferencesRequest):
        self.export_requests.append(request)
        self._fail()
        return self.export


def client(
    permissions: tuple[str, ...],
    preferences: Preferences,
    *,
    authenticated: bool = True,
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
    if authenticated:
        result.cookies.set(COOKIE_NAME, COOKIE)
    return result


def mutation_body() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "idempotency_key": "intent.create-goal-1",
        "expected_revision": 1,
        "mutation": {
            "operation": "create_goal",
            "title": "Explain risk with evidence",
            "detail": None,
        },
    }


def test_headless_reads_use_server_learner_and_closed_contracts() -> None:
    preferences = Preferences()
    subject = client(("learner_preferences.read",), preferences)

    profile = subject.get("/api/v1/learner-preferences")
    history = subject.get("/api/v1/learner-preferences/history")
    export = subject.get("/api/v1/learner-preferences/export")

    assert profile.status_code == history.status_code == export.status_code == 200
    assert profile.json()["learner_id"] == LEARNER_ID
    assert profile.json()["created_at"].endswith("Z")
    assert history.json()["current_revision"] == 4
    assert export.json()["profile"]["learner_id"] == LEARNER_ID
    assert preferences.open_requests == [
        OpenLearnerPreferencesRequest(LEARNER_ID)
    ]
    assert preferences.history_requests == [
        ReadLearnerPreferenceHistoryRequest(LEARNER_ID)
    ]
    assert preferences.export_requests == [
        ExportLearnerPreferencesRequest(LEARNER_ID)
    ]


def test_profile_response_preserves_digest_canonical_fractional_timestamp() -> None:
    preferences = Preferences()
    contract = ContractLearnerPreferenceAdapter(SCHEMA_DIR)
    document = json.loads(
        (FIXTURE_DIR / "valid-populated-profile.json").read_text(
            encoding="utf-8"
        )
    )
    canonical_time = "2026-10-17T18:03:00.007590Z"
    document["updated_at"] = canonical_time
    document["goals"][0]["updated_at"] = canonical_time
    digest_input = dict(document)
    digest_input.pop("profile_digest")
    document["profile_digest"] = canonical_digest(digest_input)
    preferences.empty = contract.parse_profile(
        json.dumps(document).encode("utf-8")
    )
    history_document = json.loads(
        (FIXTURE_DIR / "valid-history.json").read_text(encoding="utf-8")
    )
    history_document["changes"][-1]["occurred_at"] = canonical_time
    preferences.history = contract.parse_history(
        json.dumps(history_document).encode("utf-8")
    )
    export_document = json.loads(
        (FIXTURE_DIR / "valid-export.json").read_text(encoding="utf-8")
    )
    export_document["exported_at"] = canonical_time
    export_document["profile"] = document
    export_document["history"]["changes"][-1][
        "occurred_at"
    ] = canonical_time
    export_document["history"]["changes"][-1][
        "resulting_profile_digest"
    ] = document["profile_digest"]
    preferences.export = contract.parse_export(
        json.dumps(export_document).encode("utf-8")
    )

    subject = client(("learner_preferences.read",), preferences)
    response = subject.get("/api/v1/learner-preferences")
    history_response = subject.get("/api/v1/learner-preferences/history")
    export_response = subject.get("/api/v1/learner-preferences/export")

    assert response.status_code == 200
    response_document = response.json()
    assert response_document["updated_at"] == canonical_time
    assert response_document["goals"][0]["updated_at"] == canonical_time
    response_digest = response_document.pop("profile_digest")
    assert canonical_digest(response_document) == response_digest
    assert (
        history_response.json()["changes"][-1]["occurred_at"]
        == canonical_time
    )
    exported = export_response.json()
    assert exported["exported_at"] == canonical_time
    assert exported["profile"]["updated_at"] == canonical_time
    assert (
        exported["history"]["changes"][-1]["occurred_at"] == canonical_time
    )


def test_mutation_uses_server_learner_and_exact_frozen_intent() -> None:
    preferences = Preferences()
    response = client(
        ("learner_preferences.write",), preferences
    ).post(
        "/api/v1/learner-preferences/mutations",
        json=mutation_body(),
        headers={"Origin": ORIGIN},
    )

    assert response.status_code == 200
    assert response.json()["revision"] == 4
    request = preferences.mutation_requests[0]
    assert request.learner_id == LEARNER_ID
    assert request.intent.idempotency_key == "intent.create-goal-1"
    assert request.intent.mutation.operation == "create_goal"
    assert request.intent.mutation.title == "Explain risk with evidence"


@pytest.mark.parametrize(
    ("method", "path", "permission"),
    [
        ("get", "/api/v1/learner-preferences", "learner_preferences.read"),
        (
            "get",
            "/api/v1/learner-preferences/history",
            "learner_preferences.read",
        ),
        (
            "get",
            "/api/v1/learner-preferences/export",
            "learner_preferences.read",
        ),
        (
            "post",
            "/api/v1/learner-preferences/mutations",
            "learner_preferences.write",
        ),
    ],
)
def test_routes_require_their_exact_permission(
    method: str, path: str, permission: str
) -> None:
    preferences = Preferences()
    subject = client((), preferences)
    kwargs = (
        {"json": mutation_body(), "headers": {"Origin": ORIGIN}}
        if method == "post"
        else {}
    )

    response = getattr(subject, method)(path, **kwargs)

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"
    assert permission not in response.text
    assert not (
        preferences.open_requests
        or preferences.mutation_requests
        or preferences.history_requests
        or preferences.export_requests
    )


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/learner-preferences?learner_id=someone-else",
        "/api/v1/learner-preferences/history?limit=1",
        "/api/v1/learner-preferences/export?include_private=true",
    ],
)
def test_reads_reject_all_query_input_before_service_access(path: str) -> None:
    preferences = Preferences()
    response = client(("learner_preferences.read",), preferences).get(path)

    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"
    assert not (
        preferences.open_requests
        or preferences.history_requests
        or preferences.export_requests
    )


@pytest.mark.parametrize(
    "extra",
    [
        {"learner_id": "44444444-4444-4444-8444-444444444444"},
        {"evidence": {"mastery": 1}},
    ],
)
def test_mutation_rejects_caller_identity_and_private_fields(
    extra: dict[str, object],
) -> None:
    preferences = Preferences()
    body = mutation_body()
    body.update(extra)

    response = client(
        ("learner_preferences.write",), preferences
    ).post(
        "/api/v1/learner-preferences/mutations",
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
        (LearnerModelErrorCode.NOT_FOUND, 404),
        (LearnerModelErrorCode.IMMUTABLE_CONFLICT, 409),
        (LearnerModelErrorCode.STALE_REVISION, 409),
        (LearnerModelErrorCode.PREFERENCE_LIMIT, 409),
        (LearnerModelErrorCode.INTEGRITY_FAILURE, 503),
        (LearnerModelErrorCode.UNAVAILABLE, 503),
    ],
)
def test_preference_errors_have_safe_stable_http_mapping(
    error: LearnerModelErrorCode, expected_status: int
) -> None:
    response = client(
        ("learner_preferences.read",), Preferences(error=error)
    ).get("/api/v1/learner-preferences")

    assert response.status_code == expected_status
    assert response.json()["code"] == error.value
    assert "fixture" not in response.text


def test_openapi_exposes_one_browser_and_headless_contract() -> None:
    schema = client(
        ("learner_preferences.read",), Preferences()
    ).app.openapi()

    assert schema["paths"]["/api/v1/learner-preferences"]["get"][
        "operationId"
    ] == "getLearnerPreferences"
    assert schema["paths"]["/api/v1/learner-preferences/mutations"]["post"][
        "operationId"
    ] == "mutateLearnerPreferences"
    assert "422" not in schema["paths"][
        "/api/v1/learner-preferences/mutations"
    ]["post"]["responses"]
    assert schema["paths"]["/api/v1/learner-preferences/history"]["get"][
        "operationId"
    ] == "getLearnerPreferenceHistory"
    assert schema["paths"]["/api/v1/learner-preferences/export"]["get"][
        "operationId"
    ] == "exportLearnerPreferences"
