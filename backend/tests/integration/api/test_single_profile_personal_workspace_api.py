from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    LearnerContext,
)
from financial_ai_academy.modules.personal_workspace.adapters.workspace_contract import (
    ContractPersonalWorkspaceAdapter,
)
from financial_ai_academy.modules.personal_workspace.public import (
    CreateNoteCommand,
    MutatePersonalWorkspaceRequest,
    OpenPersonalWorkspaceRequest,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = ROOT / "contracts" / "learning" / "personal-workspace" / "v1"
FIXTURE_DIR = ROOT / "contracts" / "compatibility" / "personal-workspace" / "v1"
ORIGIN = "http://127.0.0.1:8000"
COOKIE_NAME = "financial_ai_academy_session"
COOKIE = "a" * 43
NOW = datetime(2026, 10, 17, 13, 0, tzinfo=timezone.utc)


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
            actor_id="actor.demo",
            learner_id="learner.demo",
            session_id="session.demo",
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


class Workspaces:
    def __init__(self) -> None:
        contract = ContractPersonalWorkspaceAdapter(SCHEMA_DIR)
        self.empty = contract.parse_workspace(
            (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
        )
        self.populated = contract.parse_workspace(
            (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
        )
        self.open_requests: list[OpenPersonalWorkspaceRequest] = []
        self.mutation_requests: list[MutatePersonalWorkspaceRequest] = []

    def open_workspace(self, request: OpenPersonalWorkspaceRequest):
        self.open_requests.append(request)
        return self.empty

    def mutate_workspace(self, request: MutatePersonalWorkspaceRequest):
        self.mutation_requests.append(request)
        return self.populated


def client(
    permissions: tuple[str, ...],
    workspaces: Workspaces,
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
                personal_workspace=workspaces,
            )
        ),
        base_url=ORIGIN,
    )
    if authenticated:
        result.cookies.set(COOKIE_NAME, COOKIE)
    return result


def note_body() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "idempotency_key": "saved-learning-note-1",
        "expected_revision": 1,
        "mutation": {
            "operation": "create_note",
            "selector": {
                "reference_kind": "learning_opportunity",
                "opportunity_id": "opportunity.diversification",
                "placement_id": "placement.diversification",
            },
            "title": "Why diversification matters",
            "body": "Diversification can reduce concentration risk.",
        },
    }


def test_authenticated_headless_read_returns_closed_workspace_contract() -> None:
    workspaces = Workspaces()
    response = client(("personal_workspace.read",), workspaces).get(
        "/api/v1/personal-workspace"
    )
    assert response.status_code == 200
    assert response.json() == {
        "schema_version": "1.0.0",
        "workspace_id": "workspace.demo",
        "learner_id": "learner.demo",
        "revision": 1,
        "records": [],
        "collections": [],
        "created_at": "2026-10-17T12:00:00Z",
        "updated_at": "2026-10-17T12:00:00Z",
        "workspace_digest": "0e98827b567453998ba38dc8fb6489b74675c8fb7512026ec2077333961cca8b",
    }
    assert workspaces.open_requests == [
        OpenPersonalWorkspaceRequest(learner_id="learner.demo")
    ]


def test_authenticated_write_uses_server_learner_and_selector_command() -> None:
    workspaces = Workspaces()
    response = client(
        ("personal_workspace.read", "personal_workspace.write"), workspaces
    ).post(
        "/api/v1/personal-workspace/mutations",
        json=note_body(),
        headers={"origin": ORIGIN},
    )
    assert response.status_code == 200
    assert response.json()["revision"] == 4
    request = workspaces.mutation_requests[0]
    assert request.learner_id == "learner.demo"
    assert isinstance(request.command.mutation, CreateNoteCommand)
    assert request.command.mutation.selector.opportunity_id == (
        "opportunity.diversification"
    )


def test_identity_and_server_fields_cannot_be_supplied_by_caller() -> None:
    workspaces = Workspaces()
    body = note_body()
    body["learner_id"] = "learner.other"
    response = client(("personal_workspace.write",), workspaces).post(
        "/api/v1/personal-workspace/mutations",
        json=body,
        headers={"origin": ORIGIN},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"
    assert workspaces.mutation_requests == []


def test_missing_or_insufficient_session_denies_before_workspace_access() -> None:
    missing_workspaces = Workspaces()
    missing = client(
        ("personal_workspace.read",),
        missing_workspaces,
        authenticated=False,
    ).get("/api/v1/personal-workspace")
    denied_workspaces = Workspaces()
    denied = client(("curriculum.lesson.read",), denied_workspaces).get(
        "/api/v1/personal-workspace"
    )
    assert missing.status_code == 401
    assert denied.status_code == 403
    assert missing_workspaces.open_requests == []
    assert denied_workspaces.open_requests == []


def test_write_requires_same_origin_and_write_permission() -> None:
    no_permission = Workspaces()
    denied = client(("personal_workspace.read",), no_permission).post(
        "/api/v1/personal-workspace/mutations",
        json=note_body(),
        headers={"origin": ORIGIN},
    )
    wrong_origin = Workspaces()
    forbidden = client(
        ("personal_workspace.write",), wrong_origin
    ).post(
        "/api/v1/personal-workspace/mutations",
        json=note_body(),
        headers={"origin": "http://example.invalid"},
    )
    assert denied.status_code == 403
    assert forbidden.status_code == 403
    assert no_permission.mutation_requests == []
    assert wrong_origin.mutation_requests == []
