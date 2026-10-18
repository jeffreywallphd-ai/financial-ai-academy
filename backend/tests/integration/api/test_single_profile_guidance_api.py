from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from fastapi.testclient import TestClient

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.hosts.api.generate_openapi import generate_bytes
from financial_ai_academy.modules.guidance.adapters import ImmutablePlatformHelpCorpus
from financial_ai_academy.modules.guidance.application import GuidanceService
from financial_ai_academy.modules.guidance.public import (
    OpenPlatformHelpTopicRequest,
    PlatformHelpTopic,
    SearchPage,
    SearchRequest,
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
OPENAPI = REPOSITORY / "contracts/api/openapi.json"
ORIGIN = "http://127.0.0.1:8000"
COOKIE_NAME = "financial_ai_academy_session"
COOKIE = "a" * 43
NOW = datetime(2026, 10, 18, tzinfo=timezone.utc)


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
            actor_id="opaque-actor",
            learner_id="opaque-learner",
            session_id="opaque-session",
            authenticated_at=NOW,
            expires_at=datetime(2026, 10, 19, tzinfo=timezone.utc),
            authentication_method="single_profile",
            permissions=self.permissions,
        )

    def bootstrap_single_profile(self, request: object) -> object:
        raise NotImplementedError

    def revoke_session(self, cookie_value: str | None) -> None:
        return None

    def health(self) -> bool:
        return True


class Guidance:
    def __init__(self) -> None:
        self._service = GuidanceService(ImmutablePlatformHelpCorpus())
        self.search_calls: list[SearchRequest] = []
        self.open_calls: list[OpenPlatformHelpTopicRequest] = []

    def search_platform_help(self, request: SearchRequest) -> SearchPage:
        self.search_calls.append(request)
        return self._service.search_platform_help(request)

    def open_platform_help_topic(
        self, request: OpenPlatformHelpTopicRequest
    ) -> PlatformHelpTopic:
        self.open_calls.append(request)
        return self._service.open_platform_help_topic(request)


def client(
    identity: Identity,
    guidance: Guidance,
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
                identity=identity,  # type: ignore[arg-type]
                curriculum=object(),  # type: ignore[arg-type]
                request_policy=policy,
                guidance=guidance,
            )
        ),
        base_url=ORIGIN,
    )
    if authenticated:
        result.cookies.set(COOKIE_NAME, COOKIE)
    return result


def exact_path(version: str = "1.0.0") -> str:
    return f"/api/v1/guidance/platform-help/approved-help/versions/{version}"


def test_authorized_search_and_exact_read_preserve_closed_public_facts() -> None:
    guidance = Guidance()
    http = client(Identity(("guidance.platform_help.read",)), guidance)

    search = http.get(
        "/api/v1/guidance/platform-help",
        params={"query": "approved help", "page_size": 2},
    )
    exact = http.get(exact_path())

    assert search.status_code == 200
    assert search.json()["query"] == "approved help"
    assert search.json()["results"]
    assert all(item["source_references"] for item in search.json()["results"])
    assert exact.status_code == 200
    assert exact.json()["topic_id"] == "approved-help"
    assert exact.json()["publication"]["state"] == "approved"
    assert exact.json()["source_references"]
    serialized = json.dumps((search.json(), exact.json()))
    assert all(
        prohibited not in serialized
        for prohibited in (
            "actor_id",
            "learner_id",
            "session_id",
            "repository_path",
            "prompt",
            "model_output",
        )
    )


def test_search_preserves_required_nullable_cursor_on_every_page() -> None:
    http = client(
        Identity(("guidance.platform_help.read",)),
        Guidance(),
    )

    continued = http.get(
        "/api/v1/guidance/platform-help",
        params={"page_size": 1},
    )
    terminal = http.get(
        "/api/v1/guidance/platform-help",
        params={"query": "approved help", "page_size": 50},
    )

    assert continued.status_code == 200
    assert isinstance(continued.json()["next_cursor"], str)
    assert continued.json()["next_cursor"]
    assert terminal.status_code == 200
    assert "next_cursor" in terminal.json()
    assert terminal.json()["next_cursor"] is None


def test_missing_and_insufficient_context_deny_before_corpus_access() -> None:
    missing_guidance = Guidance()
    missing = client(
        Identity(("guidance.platform_help.read",)),
        missing_guidance,
        authenticated=False,
    ).get("/api/v1/guidance/platform-help")
    denied_guidance = Guidance()
    denied = client(
        Identity(("curriculum.lesson.read",)), denied_guidance
    ).get(exact_path())

    assert missing.status_code == 401
    assert denied.status_code == 403
    assert missing_guidance.search_calls == []
    assert denied_guidance.open_calls == []


def test_client_selected_permission_is_rejected_before_corpus_access() -> None:
    guidance = Guidance()
    response = client(
        Identity(("guidance.platform_help.read",)), guidance
    ).get(
        "/api/v1/guidance/platform-help",
        headers={"X-Permission": "guidance.platform_help.read"},
    )

    assert response.status_code == 403
    assert guidance.search_calls == []


def test_exact_version_absence_and_invalid_cursor_are_bounded() -> None:
    guidance = Guidance()
    http = client(Identity(("guidance.platform_help.read",)), guidance)

    absent = http.get(exact_path("2.0.0"))
    invalid_cursor = http.get(
        "/api/v1/guidance/platform-help", params={"cursor": "not-a-cursor"}
    )

    assert absent.status_code == 404
    assert absent.json()["code"] == "not_found"
    assert invalid_cursor.status_code == 409
    assert invalid_cursor.json()["code"] == "invalid_cursor"
    assert "not-a-cursor" not in json.dumps(invalid_cursor.json())


def test_unknown_query_and_get_bodies_are_rejected() -> None:
    http = client(Identity(("guidance.platform_help.read",)), Guidance())

    unknown = http.get(
        "/api/v1/guidance/platform-help", params={"unexpected": "value"}
    )
    body = http.request("GET", exact_path(), content=b"{}")

    assert unknown.status_code == 400
    assert body.status_code == 400


def test_openapi_snapshot_contains_stable_cookie_protected_operations() -> None:
    generated = json.loads(generate_bytes())
    search = generated["paths"]["/api/v1/guidance/platform-help"]["get"]
    exact = generated["paths"][
        "/api/v1/guidance/platform-help/{topic_id}/versions/{topic_version}"
    ]["get"]

    assert search["operationId"] == "searchPlatformHelp"
    assert exact["operationId"] == "getPlatformHelpTopicVersion"
    assert search["security"] == [{"OpaqueSessionCookie": []}]
    assert exact["security"] == [{"OpaqueSessionCookie": []}]
    assert "422" not in search["responses"]
    assert "422" not in exact["responses"]
    assert OPENAPI.read_bytes() == generate_bytes()
