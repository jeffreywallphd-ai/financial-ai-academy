from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.hosts.api.generate_openapi import generate_bytes
from financial_ai_academy.hosts.api.models import (
    NavigationReasonResponseModel,
)
from financial_ai_academy.modules.adaptation.public import (
    ActivitySourceFact,
    ActivitySourceState,
    CompletionState,
    EvaluateNavigationStateRequest,
    NavigationStateOperationError,
    NavigationStateOperationErrorCode,
    OpenNavigationStateRequest,
    evaluate_navigation_state,
)
from financial_ai_academy.modules.curriculum.public import (
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
GRAPH_PATH = (
    REPOSITORY
    / "contracts/compatibility/curriculum-graph/v1/approved/graph.json"
)
OPENAPI = REPOSITORY / "contracts/api/openapi.json"
ORIGIN = "http://127.0.0.1:8000"
COOKIE_NAME = "financial_ai_academy_session"
COOKIE = "a" * 43
LEARNER_ID = "90a46e7e-8cbe-4f63-ab1b-8aa01ef95aa6"
NOW = datetime(2026, 10, 16, 1, 0, tzinfo=timezone.utc)


def projection():
    graph = curriculum_graph_from_mapping(
        json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    )
    facts = tuple(
        ActivitySourceFact(
            activity.activity_id,
            ActivitySourceState.AVAILABLE,
            CompletionState.INCOMPLETE
            if activity.kind.value == "lesson"
            else CompletionState.UNAVAILABLE,
            (
                activity.reference.package_digest
                if activity.kind.value == "lesson"
                else activity.reference.definition_digest
            ),
        )
        for activity in graph.activities
    )
    return evaluate_navigation_state(
        EvaluateNavigationStateRequest(graph, facts, NOW)
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
            learner_id=LEARNER_ID,
            session_id="opaque-session",
            authenticated_at=NOW,
            expires_at=datetime(2026, 10, 17, tzinfo=timezone.utc),
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


class Adaptation:
    def __init__(self, result=None) -> None:
        self.result = result or projection()
        self.calls: list[OpenNavigationStateRequest] = []

    def open_navigation_state(self, request: OpenNavigationStateRequest):
        self.calls.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def client(
    identity: Identity,
    adaptation: Adaptation,
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
                curriculum=Curriculum(),  # type: ignore[arg-type]
                request_policy=policy,
                adaptation=adaptation,  # type: ignore[arg-type]
            )
        ),
        base_url=ORIGIN,
    )
    if authenticated:
        result.cookies.set(COOKIE_NAME, COOKIE)
    return result


def path() -> str:
    return (
        "/api/v1/adaptation/curricula/investing-foundations/"
        "versions/1.0.0/navigation-state"
    )


def test_authorized_exact_state_returns_closed_projection() -> None:
    adaptation = Adaptation()

    response = client(
        Identity(("adaptation.navigation.read",)), adaptation
    ).get(path())

    assert response.status_code == 200
    body = response.json()
    assert body["schema_version"] == "1.0.0"
    assert len(body["activity_states"]) == 5
    assert body["activity_states"][1]["completion"] == "unavailable"
    assert adaptation.calls == [
        OpenNavigationStateRequest(
            LEARNER_ID, "investing-foundations", "1.0.0"
        )
    ]
    serialized = json.dumps(body)
    assert all(
        value not in serialized
        for value in ("learner_id", LEARNER_ID, "actor_id", "mastery")
    )


def test_missing_or_insufficient_context_denies_before_adaptation() -> None:
    missing_service = Adaptation()
    missing = client(
        Identity(("adaptation.navigation.read",)),
        missing_service,
        authenticated=False,
    ).get(path())
    denied_service = Adaptation()
    denied = client(
        Identity(("curriculum.graph.read",)), denied_service
    ).get(path())

    assert missing.status_code == 401
    assert denied.status_code == 403
    assert missing_service.calls == []
    assert denied_service.calls == []


@pytest.mark.parametrize(
    "query",
    [
        {"learner_id": LEARNER_ID},
        {"permission": "adaptation.navigation.read"},
        {"policy_id": "other"},
        {"policy_version": "9.9.9"},
        {"provider": "other"},
        {"latest": "true"},
        {"debug": "true"},
    ],
)
def test_query_parameters_are_rejected_before_adaptation(query) -> None:
    adaptation = Adaptation()
    result = client(
        Identity(("adaptation.navigation.read",)), adaptation
    ).get(path(), params=query)

    assert result.status_code == 400
    assert adaptation.calls == []


def test_bounded_not_found_and_unavailable_errors_are_mapped() -> None:
    missing = Adaptation(
        NavigationStateOperationError(
            NavigationStateOperationErrorCode.NOT_FOUND,
            "The exact curriculum navigation state could not be opened.",
        )
    )
    unavailable = Adaptation(
        NavigationStateOperationError(
            NavigationStateOperationErrorCode.UNAVAILABLE,
            "Navigation state is currently unavailable.",
        )
    )

    missing_result = client(
        Identity(("adaptation.navigation.read",)), missing
    ).get(path())
    unavailable_result = client(
        Identity(("adaptation.navigation.read",)), unavailable
    ).get(path())

    assert missing_result.status_code == 404
    assert unavailable_result.status_code == 503
    assert "database" not in json.dumps(unavailable_result.json()).lower()


def test_same_route_accepts_complete_projection_without_presentation_hints() -> None:
    flexible = replace(projection(), evaluated_at=NOW)

    response = client(
        Identity(("adaptation.navigation.read",)), Adaptation(flexible)
    ).get(path())

    assert response.status_code == 200
    assert [item["activity_id"] for item in response.json()["activity_states"]] == [
        item.activity_id for item in flexible.activity_states
    ]


def test_openapi_contains_only_the_exact_generated_operation_inputs() -> None:
    generated = json.loads(generate_bytes())
    operation = generated["paths"][
        "/api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/navigation-state"
    ]["get"]

    assert operation["operationId"] == "getCurriculumNavigationState"
    assert "422" not in operation["responses"]
    assert [item["name"] for item in operation["parameters"]] == [
        "curriculum_id",
        "curriculum_version",
    ]
    components = generated["components"]["schemas"]
    reason = components["NavigationReasonResponseModel"]["properties"]
    activity = components[
        "ActivityNavigationStateResponseModel"
    ]["properties"]
    state = components["NavigationStateResponseModel"]["properties"]
    assert reason["references"]["maxItems"] == 10
    assert reason["references"]["uniqueItems"] is True
    assert activity["reasons"]["minItems"] == 2
    assert activity["reasons"]["maxItems"] == 2002
    assert state["activity_states"]["uniqueItems"] is True
    assert "(?:-" not in state["policy_version"]["pattern"]
    assert state["evaluated_at"]["pattern"].startswith("^[0-9]{4}")
    assert OPENAPI.read_bytes() == generate_bytes()


def test_navigation_reason_runtime_matches_v1_reference_bounds() -> None:
    model = NavigationReasonResponseModel(
        code="prerequisite_incomplete",
        explanation="Every referenced prerequisite remains explicit.",
        references=["activity-target", "activity-one", "edge-one", "edge-two"],
    )
    assert len(model.references) == 4

    with pytest.raises(ValueError):
        NavigationReasonResponseModel(
            code="prerequisite_incomplete",
            explanation="Duplicate references are not contract-valid.",
            references=["activity-target", "activity-target"],
        )
