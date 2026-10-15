from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.hosts.api.generate_openapi import generate_bytes
from financial_ai_academy.modules.curriculum.public import (
    BrowseLearningOpportunitiesRequest,
    DiscoveryError,
    DiscoveryErrorCode,
    DiscoveryProvenance,
    LearningOpportunityBrowse,
    LearningOpportunityRecord,
    OpportunityAvailability,
    OpportunityKind,
    OpportunityLevel,
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
NOW = datetime(2026, 10, 15, 17, 0, tzinfo=timezone.utc)
DIGEST = "a" * 64
SOURCE = "b" * 64
GENERATION = "c" * 64


def browse_result() -> LearningOpportunityBrowse:
    return LearningOpportunityBrowse(
        schema_version="1.0.0",
        projection_generation=GENERATION,
        projected_at=NOW,
        records=(
            LearningOpportunityRecord(
                schema_version="1.0.0",
                opportunity_id="intro-risk-return-primary",
                placement_id="intro-risk-return-primary",
                destination=(
                    "/learn/placements/intro-risk-return-primary"
                ),
                kind=OpportunityKind.LESSON,
                title="Understanding Risk and Return",
                summary=(
                    "Learn the relationship between investment risk and return."
                ),
                objectives=("Explain the risk-return relationship.",),
                topics=("risk-return",),
                level=OpportunityLevel.INTRODUCTORY,
                estimated_minutes=20,
                prerequisite_summary="No prior investing knowledge is required.",
                availability=OpportunityAvailability.AVAILABLE,
                availability_reason=(
                    "Available as an approved versioned lesson."
                ),
                package_id="intro-risk-return",
                package_version="1.0.0",
                package_digest=DIGEST,
                provenance=DiscoveryProvenance(
                    published_by="reviewed-editor",
                    published_at=NOW,
                    content_reviewed_on=date(2026, 10, 15),
                    educational_use_notice="Education only.",
                ),
                source_fingerprint=SOURCE,
                projected_at=NOW,
            ),
        ),
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
    def __init__(self, result: LearningOpportunityBrowse | Exception) -> None:
        self.result = result
        self.calls = 0

    def browse_learning_opportunities(
        self,
        request: BrowseLearningOpportunitiesRequest,
    ) -> LearningOpportunityBrowse:
        self.calls += 1
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


def test_authorized_catalog_returns_closed_discovery_contract() -> None:
    curriculum = Curriculum(browse_result())
    response = client(
        Identity(("curriculum.discovery.read",)),
        curriculum,
    ).get("/api/v1/curriculum/opportunities")

    assert response.status_code == 200
    assert response.json()["projection_generation"] == GENERATION
    assert response.json()["records"][0]["opportunity_id"] == (
        "intro-risk-return-primary"
    )
    assert response.json()["records"][0]["destination"] == (
        "/learn/placements/intro-risk-return-primary"
    )
    assert {"actor_id", "learner_id", "session_id"}.isdisjoint(
        response.json()
    )
    assert curriculum.calls == 1


def test_missing_or_insufficient_context_denies_before_disclosure() -> None:
    missing_curriculum = Curriculum(browse_result())
    missing = client(
        Identity(("curriculum.discovery.read",)),
        missing_curriculum,
        authenticated=False,
    ).get("/api/v1/curriculum/opportunities")
    denied_curriculum = Curriculum(browse_result())
    denied = client(
        Identity(("curriculum.lesson.read",)),
        denied_curriculum,
    ).get("/api/v1/curriculum/opportunities")

    assert missing.status_code == 401
    assert missing.json()["code"] == "unauthorized"
    assert missing_curriculum.calls == 0
    assert denied.status_code == 403
    assert denied.json()["code"] == "forbidden"
    assert denied_curriculum.calls == 0
    assert GENERATION not in missing.text + denied.text


def test_client_selected_permission_is_rejected_before_identity_resolution() -> None:
    curriculum = Curriculum(browse_result())
    response = client(
        Identity(("curriculum.discovery.read",)),
        curriculum,
    ).get(
        "/api/v1/curriculum/opportunities",
        headers={"X-Permission": "curriculum.discovery.read"},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"
    assert curriculum.calls == 0
    assert GENERATION not in response.text


def test_projection_failure_is_bounded_and_redacted() -> None:
    curriculum = Curriculum(
        DiscoveryError(
            DiscoveryErrorCode.UNAVAILABLE,
            "Learning-opportunity projection is unavailable.",
        )
    )
    response = client(
        Identity(("curriculum.discovery.read",)),
        curriculum,
    ).get("/api/v1/curriculum/opportunities")

    assert response.status_code == 503
    assert response.json()["code"] == "unavailable"
    assert response.json()["message"] == (
        "Learning-opportunity projection is unavailable."
    )
    assert "postgres" not in response.text.casefold()


def test_openapi_catalog_contract_is_stable_queryless_and_cookie_secured() -> None:
    first = generate_bytes()
    second = generate_bytes()
    assert first == second == OPENAPI.read_bytes()
    schema = json.loads(first)
    operation = schema["paths"][
        "/api/v1/curriculum/opportunities"
    ]["get"]
    assert operation["operationId"] == "browseLearningOpportunities"
    assert operation["security"] == [{"OpaqueSessionCookie": []}]
    assert operation.get("parameters", []) == []
    model = schema["components"]["schemas"][
        "LearningOpportunityBrowseResponseModel"
    ]
    assert model["additionalProperties"] is False
    assert "schema_version" in model["required"]
    record = schema["components"]["schemas"][
        "LearningOpportunityResponseModel"
    ]
    assert "schema_version" in record["required"]
    assert record["properties"]["objectives"]["uniqueItems"] is True
    assert record["properties"]["topics"]["uniqueItems"] is True
    assert record["properties"]["destination"]["pattern"] == (
        r"^/learn/placements/[a-z0-9][a-z0-9._-]{2,63}$"
    )
    assert "learner_id" not in first.decode("utf-8")
