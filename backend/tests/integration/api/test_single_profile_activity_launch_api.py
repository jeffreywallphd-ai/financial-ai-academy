from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.hosts.api.generate_openapi import generate_bytes
from financial_ai_academy.modules.adaptation.public import (
    ActivityLaunchError,
    ActivityLaunchErrorCode,
    ActivityLaunchResolution,
    OpenActivityLaunchRequest,
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


ROOT = Path(__file__).resolve().parents[4]
LAUNCH_PATH = ROOT / "contracts/compatibility/adaptation-activity-launch/v1/approved/launch.json"
OPENAPI = ROOT / "contracts/api/openapi.json"
ORIGIN = "http://127.0.0.1:8000"
COOKIE_NAME = "financial_ai_academy_session"
COOKIE = "a" * 43
LEARNER_ID = "90a46e7e-8cbe-4f63-ab1b-8aa01ef95aa6"
NOW = datetime(2026, 10, 16, 1, 0, tzinfo=timezone.utc)


def resolution() -> ActivityLaunchResolution:
    value = json.loads(LAUNCH_PATH.read_text(encoding="utf-8"))
    return ActivityLaunchResolution(
        schema_version=value["schema_version"],
        curriculum_id=value["curriculum_id"],
        curriculum_version=value["curriculum_version"],
        graph_digest=value["graph_digest"],
        activity_id=value["activity_id"],
        navigation_projection_digest=value["navigation_projection_digest"],
        evaluated_at=datetime.fromisoformat(
            value["evaluated_at"].replace("Z", "+00:00")
        ),
        placement_id=value["placement_id"],
        package_id=value["package_id"],
        package_version=value["package_version"],
        package_digest=value["package_digest"],
        destination=value["destination"],
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
        self.result = result or resolution()
        self.calls: list[OpenActivityLaunchRequest] = []

    def open_activity_launch(self, request: OpenActivityLaunchRequest):
        self.calls.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def client(
    permissions: tuple[str, ...],
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
                identity=Identity(permissions),  # type: ignore[arg-type]
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


def path(activity_id: str = "activity-risk-return-lesson") -> str:
    return (
        "/api/v1/adaptation/curricula/investing-foundations/"
        f"versions/1.0.0/activities/{activity_id}/launch"
    )


PERMISSIONS = ("adaptation.navigation.read", "curriculum.lesson.read")


def test_authorized_launch_returns_only_the_closed_exact_resolution() -> None:
    adaptation = Adaptation()

    response = client(PERMISSIONS, adaptation).get(path())

    assert response.status_code == 200
    assert response.json() == json.loads(LAUNCH_PATH.read_text(encoding="utf-8"))
    assert adaptation.calls == [
        OpenActivityLaunchRequest(
            learner_id=LEARNER_ID,
            curriculum_id="investing-foundations",
            curriculum_version="1.0.0",
            activity_id="activity-risk-return-lesson",
        )
    ]
    serialized = json.dumps(response.json())
    assert all(
        value not in serialized
        for value in (LEARNER_ID, "learner_id", "actor_id", "permission")
    )


@pytest.mark.parametrize(
    "permissions",
    [
        (),
        ("adaptation.navigation.read",),
        ("curriculum.lesson.read",),
    ],
)
def test_both_existing_permissions_are_required_before_adaptation(
    permissions: tuple[str, ...],
) -> None:
    adaptation = Adaptation()

    response = client(permissions, adaptation).get(path())

    assert response.status_code == 403
    assert adaptation.calls == []


def test_missing_session_is_denied_before_adaptation() -> None:
    adaptation = Adaptation()

    response = client(PERMISSIONS, adaptation, authenticated=False).get(path())

    assert response.status_code == 401
    assert adaptation.calls == []


@pytest.mark.parametrize(
    "query",
    [
        {"learner_id": LEARNER_ID},
        {"destination": "/learn/placements/other"},
        {"placement_id": "other"},
        {"package_id": "other"},
        {"eligibility": "eligible"},
        {"latest": "true"},
        {"debug": "true"},
    ],
)
def test_authority_query_parameters_are_rejected_before_adaptation(query) -> None:
    adaptation = Adaptation()

    response = client(PERMISSIONS, adaptation).get(path(), params=query)

    assert response.status_code == 400
    assert adaptation.calls == []


def test_request_body_is_rejected_before_adaptation() -> None:
    adaptation = Adaptation()

    response = client(PERMISSIONS, adaptation).request(
        "GET", path(), content=b"{}"
    )

    assert response.status_code == 400
    assert adaptation.calls == []


@pytest.mark.parametrize(
    ("code", "expected_status"),
    [
        (ActivityLaunchErrorCode.INVALID_CONTEXT, 400),
        (ActivityLaunchErrorCode.ACTIVITY_NOT_FOUND, 404),
        (ActivityLaunchErrorCode.ACTIVITY_LOCKED, 409),
        (ActivityLaunchErrorCode.ACTIVITY_UNAVAILABLE, 503),
        (ActivityLaunchErrorCode.UNSUPPORTED_ACTIVITY, 409),
    ],
)
def test_launch_denials_use_bounded_statuses_without_destination(
    code: ActivityLaunchErrorCode,
    expected_status: int,
) -> None:
    adaptation = Adaptation(ActivityLaunchError(code, "Launch was refused."))

    response = client(PERMISSIONS, adaptation).get(path())

    assert response.status_code == expected_status
    assert response.json()["code"] == code.value
    assert "destination" not in json.dumps(response.json())


def test_openapi_and_snapshot_expose_only_exact_path_inputs() -> None:
    generated = json.loads(generate_bytes())
    operation = generated["paths"][
        "/api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/activities/{activity_id}/launch"
    ]["get"]

    assert operation["operationId"] == "getCurriculumActivityLaunch"
    assert "requestBody" not in operation
    assert "422" not in operation["responses"]
    assert [item["name"] for item in operation["parameters"]] == [
        "curriculum_id",
        "curriculum_version",
        "activity_id",
    ]
    response = generated["components"]["schemas"][
        "ActivityLaunchResponseModel"
    ]
    assert response["additionalProperties"] is False
    assert set(response["required"]) == {
        "schema_version",
        "curriculum_id",
        "curriculum_version",
        "graph_digest",
        "activity_id",
        "navigation_projection_digest",
        "evaluated_at",
        "placement_id",
        "package_id",
        "package_version",
        "package_digest",
        "destination",
    }
    assert OPENAPI.read_bytes() == generate_bytes()
