from __future__ import annotations

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
from financial_ai_academy.modules.personal_workspace.adapters.workspace_contract import (
    ContractPersonalWorkspaceAdapter,
)
from financial_ai_academy.modules.personal_workspace.public import (
    CreateNoteCommand,
    MutatePersonalWorkspaceRequest,
    OpenPersonalWorkspaceRequest,
    PersonalWorkspaceError,
    PersonalWorkspaceErrorCode,
    ProjectArtifactSelector,
    ProjectSnapshotSelector,
    ProjectWorkspaceSelector,
    QueryPersonalWorkspaceRequest,
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
    def __init__(self, *, project_response: bool = False) -> None:
        contract = ContractPersonalWorkspaceAdapter(SCHEMA_DIR)
        self.empty = contract.parse_workspace(
            (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
        )
        self.populated = contract.parse_workspace(
            (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
        )
        if project_response:
            workspace = self.empty
            for index, fixture in enumerate(
                (
                    "valid-project-workspace-note.json",
                    "valid-project-snapshot-bookmark.json",
                    "valid-project-artifact-bookmark.json",
                ),
                start=1,
            ):
                workspace = contract.apply_mutation(
                    workspace,
                    contract.parse_mutation_intent(
                        (FIXTURE_DIR / fixture).read_bytes()
                    ),
                    occurred_at=NOW,
                    issued_id=f"record.project-{index}",
                )
            self.populated = workspace
        self.open_requests: list[OpenPersonalWorkspaceRequest] = []
        self.mutation_requests: list[MutatePersonalWorkspaceRequest] = []
        self.query_requests: list[QueryPersonalWorkspaceRequest] = []

    def open_workspace(self, request: OpenPersonalWorkspaceRequest):
        self.open_requests.append(request)
        return self.empty

    def mutate_workspace(self, request: MutatePersonalWorkspaceRequest):
        self.mutation_requests.append(request)
        return self.populated

    def query_workspace(self, request: QueryPersonalWorkspaceRequest):
        self.query_requests.append(request)
        contract = ContractPersonalWorkspaceAdapter(SCHEMA_DIR)
        return contract.query_workspace(self.populated, request.query)


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


def project_note_body(selector: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "idempotency_key": f"save-{selector['reference_kind']}",
        "expected_revision": 1,
        "mutation": {
            "operation": "create_note",
            "selector": selector,
            "title": "Project evidence",
            "body": "Keep this exact Project reference.",
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
        (
            "personal_workspace.read",
            "personal_workspace.write",
            "curriculum.discovery.read",
        ),
        workspaces,
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


def test_headless_query_uses_server_learner_and_closed_body() -> None:
    workspaces = Workspaces()
    response = client(("personal_workspace.read",), workspaces).post(
        "/api/v1/personal-workspace/query",
        json={
            "schema_version": "1.0.0",
            "record_kinds": ["note"],
            "target_statuses": ["available"],
            "limit": 10,
        },
        headers={"origin": ORIGIN},
    )

    assert response.status_code == 200
    assert response.json()["schema_version"] == "1.0.0"
    assert response.json()["applied_query"]["record_kinds"] == ["note"]
    assert not {
        "text",
        "owner_modules",
        "reference_kinds",
        "archived",
        "collection_id",
        "cursor",
    }.intersection(response.json()["applied_query"])
    assert "next_cursor" in response.json()
    assert workspaces.query_requests[0].learner_id == "learner.demo"
    assert workspaces.query_requests[0].query.limit == 10


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("learner_id", "learner.other"),
        ("owner", "curriculum"),
        ("permission", "project.read"),
        ("cursor", None),
        ("record_kinds", []),
        ("target_statuses", ["available", "available"]),
    ],
)
def test_query_rejects_private_null_empty_or_duplicate_fields(
    field: str, value: object
) -> None:
    workspaces = Workspaces()
    body: dict[str, object] = {"schema_version": "1.0.0", field: value}
    response = client(("personal_workspace.read",), workspaces).post(
        "/api/v1/personal-workspace/query",
        json=body,
        headers={"origin": ORIGIN},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"
    assert workspaces.query_requests == []


def test_refresh_receives_only_server_derived_reference_kind_access() -> None:
    workspaces = Workspaces()
    response = client(
        (
            "personal_workspace.write",
            "curriculum.discovery.read",
            "project.read",
        ),
        workspaces,
    ).post(
        "/api/v1/personal-workspace/mutations",
        json={
            "schema_version": "1.0.0",
            "idempotency_key": "refresh-record-one",
            "expected_revision": 1,
            "mutation": {
                "operation": "refresh_reference",
                "record_id": "record.one",
            },
        },
        headers={"origin": ORIGIN},
    )

    assert response.status_code == 200
    request = workspaces.mutation_requests[0]
    assert request.command.mutation.operation == "refresh_reference"
    assert request.readable_reference_kinds == frozenset(
        {
            "learning_opportunity",
            "project_workspace",
            "project_snapshot",
            "project_artifact",
        }
    )


def test_refresh_without_owner_read_is_not_rejected_or_disclosed_by_host() -> None:
    workspaces = Workspaces()
    response = client(("personal_workspace.write",), workspaces).post(
        "/api/v1/personal-workspace/mutations",
        json={
            "schema_version": "1.0.0",
            "idempotency_key": "refresh-without-owner-read",
            "expected_revision": 1,
            "mutation": {
                "operation": "refresh_reference",
                "record_id": "record.one",
            },
        },
        headers={"origin": ORIGIN},
    )

    assert response.status_code == 200
    assert workspaces.mutation_requests[0].readable_reference_kinds == frozenset()


def test_query_selected_learner_is_rejected_before_workspace_access() -> None:
    workspaces = Workspaces()
    subject = client(
        (
            "personal_workspace.read",
            "personal_workspace.write",
            "curriculum.discovery.read",
        ),
        workspaces,
    )
    opened = subject.get(
        "/api/v1/personal-workspace?learner_id=learner.other"
    )
    mutated = subject.post(
        "/api/v1/personal-workspace/mutations?learner_id=learner.other",
        json=note_body(),
        headers={"origin": ORIGIN},
    )
    assert opened.status_code == 400
    assert mutated.status_code == 400
    assert opened.json()["code"] == "invalid_request"
    assert mutated.json()["code"] == "invalid_request"
    assert workspaces.open_requests == []
    assert workspaces.mutation_requests == []


def test_source_creation_requires_owning_curriculum_read_permission() -> None:
    opportunity_workspaces = Workspaces()
    opportunity_denied = client(
        ("personal_workspace.write",), opportunity_workspaces
    ).post(
        "/api/v1/personal-workspace/mutations",
        json=note_body(),
        headers={"origin": ORIGIN},
    )
    lesson_body = note_body()
    lesson_body["mutation"]["selector"] = {  # type: ignore[index]
        "reference_kind": "placed_lesson",
        "placement_id": "placement.diversification",
    }
    lesson_workspaces = Workspaces()
    lesson_denied = client(
        (
            "personal_workspace.write",
            "curriculum.discovery.read",
        ),
        lesson_workspaces,
    ).post(
        "/api/v1/personal-workspace/mutations",
        json=lesson_body,
        headers={"origin": ORIGIN},
    )
    lesson_allowed = client(
        (
            "personal_workspace.write",
            "curriculum.lesson.read",
        ),
        lesson_workspaces,
    ).post(
        "/api/v1/personal-workspace/mutations",
        json=lesson_body,
        headers={"origin": ORIGIN},
    )
    assert opportunity_denied.status_code == 403
    assert lesson_denied.status_code == 403
    assert lesson_allowed.status_code == 200
    assert opportunity_workspaces.mutation_requests == []
    assert len(lesson_workspaces.mutation_requests) == 1


@pytest.mark.parametrize(
    ("selector", "expected_type"),
    [
        (
            {
                "reference_kind": "project_workspace",
                "project_id": "project.research-1",
            },
            ProjectWorkspaceSelector,
        ),
        (
            {
                "reference_kind": "project_snapshot",
                "project_id": "project.research-1",
                "snapshot_id": "snapshot.baseline-1",
            },
            ProjectSnapshotSelector,
        ),
        (
            {
                "reference_kind": "project_artifact",
                "project_id": "project.research-1",
                "artifact_id": "artifact.allocation-inputs",
                "artifact_version": 3,
            },
            ProjectArtifactSelector,
        ),
    ],
)
def test_project_source_variants_require_project_read_and_map_closed_selectors(
    selector: dict[str, object], expected_type: type
) -> None:
    denied_workspaces = Workspaces()
    denied = client(
        ("personal_workspace.write",), denied_workspaces
    ).post(
        "/api/v1/personal-workspace/mutations",
        json=project_note_body(selector),
        headers={"origin": ORIGIN},
    )
    allowed_workspaces = Workspaces(project_response=True)
    allowed = client(
        ("personal_workspace.write", "project.read"), allowed_workspaces
    ).post(
        "/api/v1/personal-workspace/mutations",
        json=project_note_body(selector),
        headers={"origin": ORIGIN},
    )

    assert denied.status_code == 403
    assert denied_workspaces.mutation_requests == []
    assert allowed.status_code == 200
    assert [
        record["target"]["reference_kind"]
        for record in allowed.json()["records"]
    ] == ["project_workspace", "project_snapshot", "project_artifact"]
    request = allowed_workspaces.mutation_requests[0]
    assert request.learner_id == "learner.demo"
    assert isinstance(request.command.mutation, CreateNoteCommand)
    assert isinstance(request.command.mutation.selector, expected_type)


def test_non_source_mutation_needs_no_curriculum_permission() -> None:
    workspaces = Workspaces()
    body = {
        "schema_version": "1.0.0",
        "idempotency_key": "collection-one",
        "expected_revision": 1,
        "mutation": {
            "operation": "create_collection",
            "title": "Keep learning",
        },
    }
    response = client(("personal_workspace.write",), workspaces).post(
        "/api/v1/personal-workspace/mutations",
        json=body,
        headers={"origin": ORIGIN},
    )
    assert response.status_code == 200
    assert len(workspaces.mutation_requests) == 1


def test_personal_workspace_not_found_maps_to_404() -> None:
    class MissingWorkspaces(Workspaces):
        def mutate_workspace(self, request: MutatePersonalWorkspaceRequest):
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.NOT_FOUND,
                "The saved learning item was not found.",
            )

    response = client(
        ("personal_workspace.write",), MissingWorkspaces()
    ).post(
        "/api/v1/personal-workspace/mutations",
        json={
            "schema_version": "1.0.0",
            "idempotency_key": "remove-missing",
            "expected_revision": 1,
            "mutation": {
                "operation": "remove_record",
                "record_id": "record.missing",
            },
        },
        headers={"origin": ORIGIN},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_openapi_requires_nullable_bookmark_label() -> None:
    workspaces = Workspaces()
    schema = client(("personal_workspace.read",), workspaces).app.openapi()
    bookmark = schema["components"]["schemas"][
        "PersonalWorkspaceBookmarkModel"
    ]
    assert "label" in bookmark["required"]
    for model_name in (
        "PersonalProjectWorkspaceReferenceModel",
        "PersonalProjectSnapshotReferenceModel",
        "PersonalProjectArtifactReferenceModel",
    ):
        assert model_name in schema["components"]["schemas"]
        model = schema["components"]["schemas"][model_name]
        assert not {
            "content",
            "content_base64",
            "download_url",
            "object_key",
            "storage_key",
        }.intersection(model.get("properties", {}))


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
