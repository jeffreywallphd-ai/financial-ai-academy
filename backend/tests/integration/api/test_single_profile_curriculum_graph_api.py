from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path

from fastapi.testclient import TestClient

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.hosts.api.generate_openapi import generate_bytes
from financial_ai_academy.modules.curriculum.public import (
    CurriculumGraph,
    CurriculumGraphError,
    CurriculumGraphErrorCode,
    OpenCurriculumGraphRequest,
    curriculum_graph_digest,
    curriculum_graph_from_mapping,
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
APPROVED = (
    REPOSITORY
    / "contracts/compatibility/curriculum-graph/v1/approved/graph.json"
)
ORIGIN = "http://127.0.0.1:8000"
COOKIE_NAME = "financial_ai_academy_session"
COOKIE = "a" * 43
NOW = datetime(2026, 10, 15, tzinfo=timezone.utc)


def approved_graph() -> CurriculumGraph:
    return curriculum_graph_from_mapping(
        json.loads(APPROVED.read_text(encoding="utf-8"))
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
            actor_id="opaque-actor",
            learner_id="opaque-learner",
            session_id="opaque-session",
            authenticated_at=NOW,
            expires_at=datetime(2026, 10, 16, tzinfo=timezone.utc),
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
    def __init__(self, result: CurriculumGraph | Exception) -> None:
        self.result = result
        self.calls: list[OpenCurriculumGraphRequest] = []

    def open_curriculum_graph(
        self,
        request: OpenCurriculumGraphRequest,
    ) -> CurriculumGraph:
        self.calls.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def client(
    identity: Identity,
    curriculum: Curriculum,
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
                curriculum=curriculum,  # type: ignore[arg-type]
                request_policy=policy,
            )
        ),
        base_url=ORIGIN,
    )
    if authenticated:
        result.cookies.set(COOKIE_NAME, COOKIE)
    return result


def graph_path(version: str = "1.0.0") -> str:
    return f"/api/v1/curriculum/graphs/investing-foundations/versions/{version}"


def test_authorized_exact_graph_returns_closed_contract() -> None:
    graph = approved_graph()
    curriculum = Curriculum(graph)

    response = client(
        Identity(("curriculum.graph.read",)),
        curriculum,
    ).get(graph_path())

    assert response.status_code == 200
    assert response.json()["curriculum_version"] == "1.0.0"
    assert response.json()["graph_digest"] == graph.graph_digest
    serialized = json.dumps(response.json())
    assert all(
        prohibited not in serialized
        for prohibited in (
            "actor_id",
            "learner_id",
            "session_id",
            "eligibility",
            "mastery",
            "recommendation",
            "database",
        )
    )
    assert curriculum.calls == [
        OpenCurriculumGraphRequest("investing-foundations", "1.0.0")
    ]


def test_missing_and_insufficient_context_deny_before_graph_access() -> None:
    missing_curriculum = Curriculum(approved_graph())
    missing = client(
        Identity(("curriculum.graph.read",)),
        missing_curriculum,
        authenticated=False,
    ).get(graph_path())
    denied_curriculum = Curriculum(approved_graph())
    denied = client(
        Identity(("curriculum.lesson.read",)),
        denied_curriculum,
    ).get(graph_path())

    assert missing.status_code == 401
    assert denied.status_code == 403
    assert missing_curriculum.calls == []
    assert denied_curriculum.calls == []


def test_client_selected_permission_is_rejected_before_identity_use() -> None:
    curriculum = Curriculum(approved_graph())
    response = client(
        Identity(("curriculum.graph.read",)),
        curriculum,
    ).get(
        graph_path(),
        headers={"X-Permission": "curriculum.graph.read"},
    )

    assert response.status_code == 403
    assert curriculum.calls == []


def test_unknown_and_corrupt_graphs_map_to_bounded_errors() -> None:
    missing = Curriculum(
        CurriculumGraphError(
            CurriculumGraphErrorCode.NOT_FOUND,
            "The exact curriculum graph version was not found.",
        )
    )
    unavailable = Curriculum(
        CurriculumGraphError(
            CurriculumGraphErrorCode.UNAVAILABLE,
            "Stored curriculum graph is unavailable.",
        )
    )

    missing_response = client(
        Identity(("curriculum.graph.read",)), missing
    ).get(graph_path())
    unavailable_response = client(
        Identity(("curriculum.graph.read",)), unavailable
    ).get(graph_path())

    assert missing_response.status_code == 404
    assert unavailable_response.status_code == 503
    assert "sql" not in json.dumps(unavailable_response.json()).lower()


def test_flexible_graph_without_presentation_order_uses_same_route() -> None:
    graph = approved_graph()
    flexible = replace(graph, presentation_order=None, graph_digest="0" * 64)
    flexible = replace(
        flexible,
        graph_digest=curriculum_graph_digest(flexible),
    )

    response = client(
        Identity(("curriculum.graph.read",)),
        Curriculum(flexible),
    ).get(graph_path())

    assert response.status_code == 200
    assert response.json()["presentation_order"] is None
    assert len(response.json()["branches"]) == len(graph.branches)


def test_openapi_snapshot_contains_stable_exact_graph_operation() -> None:
    generated = json.loads(generate_bytes())
    operation = generated["paths"][
        "/api/v1/curriculum/graphs/{curriculum_id}/versions/{curriculum_version}"
    ]["get"]

    assert operation["operationId"] == "getCurriculumGraphVersion"
    assert "422" not in operation["responses"]
    assert OPENAPI.read_bytes() == generate_bytes()
