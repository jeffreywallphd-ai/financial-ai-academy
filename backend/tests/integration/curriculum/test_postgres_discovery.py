from __future__ import annotations

import os
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.modules.content.adapters.lesson_package import (
    ContractLessonPackageValidator,
)
from financial_ai_academy.modules.content.public import PublishedLesson
from financial_ai_academy.modules.curriculum.adapters.postgres_repository import (
    PostgresCurriculumRepository,
)
from financial_ai_academy.modules.curriculum.application.service import (
    CurriculumService,
)
from financial_ai_academy.modules.curriculum.public import (
    BrowseLearningOpportunitiesRequest,
    CreateLessonPlacementRequest,
    DiscoveryError,
    DiscoveryErrorCode,
    OpportunityAvailability,
    OpportunityLevel,
    RebuildLearningOpportunityProjectionRequest,
    RegisterLessonOpportunityRequest,
)
from financial_ai_academy.modules.identity.public import LearnerContext
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)


REPOSITORY = Path(__file__).resolve().parents[4]
MIGRATIONS = REPOSITORY / "backend/migrations"
APPROVED = (
    REPOSITORY
    / "contracts/compatibility/lesson-package/v1/approved/intro-risk-return-knowledge-check"
)
SCHEMAS = REPOSITORY / "contracts/learning/lesson-package/v1"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
NOW = datetime(2026, 10, 15, 17, 0, tzinfo=timezone.utc)
ORIGIN = "http://127.0.0.1:8000"
COOKIE = "a" * 43

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(
        POSTGRES_DSN is None,
        reason="FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN is not configured",
    ),
]


class ContentGateway:
    def __init__(self, lesson: PublishedLesson) -> None:
        self.lesson = lesson

    def get_exact(
        self,
        package_id: str,
        package_version: str,
        package_digest: str,
    ) -> PublishedLesson:
        assert (
            package_id,
            package_version,
            package_digest,
        ) == (
            self.lesson.package_id,
            self.lesson.package_version,
            self.lesson.package_digest,
        )
        return self.lesson


class IdentityGateway:
    def resolve_session(self, cookie_value: str | None) -> LearnerContext:
        assert cookie_value == COOKIE
        return LearnerContext(
            actor_id="opaque-actor",
            learner_id="opaque-learner",
            session_id="opaque-session",
            authenticated_at=NOW,
            expires_at=datetime(2026, 10, 16, tzinfo=timezone.utc),
            authentication_method="single_profile",
            permissions=("curriculum.discovery.read",),
        )


@pytest.fixture(scope="module")
def lesson() -> PublishedLesson:
    return ContractLessonPackageValidator(SCHEMAS).validate_directory(
        APPROVED
    ).lesson


@pytest.fixture(scope="module", autouse=True)
def migrated_database() -> object:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as connection:
        connection.execute("DROP SCHEMA IF EXISTS curriculum CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS content CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS platform CASCADE")
    root = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS)
    curriculum = PostgresMigrationRunner(
        POSTGRES_DSN,
        MIGRATIONS / "curriculum",
    )
    root.apply_all()
    statuses = curriculum.apply_all()
    identifiers = {status.migration_id for status in statuses}
    assert "curriculum_0002_discovery_projection" in identifiers
    assert curriculum.apply_all() == statuses
    yield
    with psycopg.connect(POSTGRES_DSN) as connection:
        for migration_id in (
            "curriculum_0002_discovery_projection",
            "curriculum_0001_assessment_placements",
        ):
            connection.execute(
                (
                    MIGRATIONS / f"curriculum/{migration_id}.down.sql"
                ).read_text(encoding="utf-8")
            )
            connection.execute(
                """
                DELETE FROM platform.schema_migrations
                WHERE migration_id = %s
                """,
                (migration_id,),
            )
    root.rollback_all()


@pytest.fixture(autouse=True)
def empty_tables(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                curriculum.discovery_projection_records,
                curriculum.discovery_projection_state,
                curriculum.lesson_opportunity_classifications,
                curriculum.lesson_placements
            CASCADE
            """
        )


def classification_request() -> RegisterLessonOpportunityRequest:
    return RegisterLessonOpportunityRequest(
        opportunity_id="intro-risk-return-primary",
        placement_id="intro-risk-return-primary",
        summary="Learn the relationship between investment risk and return.",
        topics=("investing-basics", "risk-return"),
        level=OpportunityLevel.INTRODUCTORY,
        estimated_minutes=20,
        prerequisite_summary="No prior investing knowledge is required.",
        availability=OpportunityAvailability.AVAILABLE,
        availability_reason="Available as an approved versioned lesson.",
    )


def service(
    lesson: PublishedLesson,
    *,
    clock: datetime = NOW,
    before_projection_commit: object | None = None,
) -> CurriculumService:
    assert POSTGRES_DSN is not None
    return CurriculumService(
        PostgresCurriculumRepository(
            POSTGRES_DSN,
            before_projection_commit=before_projection_commit,  # type: ignore[arg-type]
        ),
        ContentGateway(lesson),
        clock=lambda: clock,
    )


def seed(service_under_test: CurriculumService, lesson: PublishedLesson) -> None:
    service_under_test.create_lesson_placement(
        CreateLessonPlacementRequest(
            placement_id="intro-risk-return-primary",
            package_id=lesson.package_id,
            package_version=lesson.package_version,
            package_digest=lesson.package_digest,
        )
    )
    service_under_test.register_lesson_opportunity(classification_request())


def test_persisted_registration_rebuild_and_browse_are_stable(
    lesson: PublishedLesson,
) -> None:
    first_service = service(lesson)
    seed(first_service, lesson)
    repeated = first_service.register_lesson_opportunity(
        classification_request()
    )

    first = first_service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )
    reopened = service(lesson).browse_learning_opportunities(
        BrowseLearningOpportunitiesRequest()
    )

    assert repeated.opportunity_id == "intro-risk-return-primary"
    assert reopened == first
    assert reopened.records[0].title == "Understanding Risk and Return"
    assert reopened.records[0].topics == (
        "investing-basics",
        "risk-return",
    )

    with pytest.raises(DiscoveryError) as conflict:
        first_service.register_lesson_opportunity(
            replace(classification_request(), estimated_minutes=25)
        )
    assert conflict.value.code is DiscoveryErrorCode.IMMUTABLE_CONFLICT
    assert service(lesson).browse_learning_opportunities(
        BrowseLearningOpportunitiesRequest()
    ) == first


def test_empty_generation_is_persisted_as_one_complete_projection(
    lesson: PublishedLesson,
) -> None:
    result = service(lesson).rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )

    assert result.records == ()
    assert service(lesson).browse_learning_opportunities(
        BrowseLearningOpportunitiesRequest()
    ) == result


def test_protected_http_returns_the_exact_persisted_generation(
    lesson: PublishedLesson,
) -> None:
    persisted_service = service(lesson)
    seed(persisted_service, lesson)
    accepted = persisted_service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )
    policy = SingleProfileRequestPolicy(
        SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin=ORIGIN,
            allowed_hosts=("127.0.0.1:8000",),
            secure_cookie=False,
        )
    )
    api = TestClient(
        create_app(
            ApiServices(
                identity=IdentityGateway(),  # type: ignore[arg-type]
                curriculum=persisted_service,
                request_policy=policy,
            )
        ),
        base_url=ORIGIN,
    )
    api.cookies.set(policy.settings.cookie_name, COOKIE)

    response = api.get("/api/v1/curriculum/opportunities")

    assert response.status_code == 200
    assert response.json()["projection_generation"] == (
        accepted.projection_generation
    )
    assert response.json()["records"][0]["source_fingerprint"] == (
        accepted.records[0].source_fingerprint
    )


def test_interrupted_replacement_preserves_prior_complete_generation(
    lesson: PublishedLesson,
) -> None:
    accepted_service = service(lesson)
    seed(accepted_service, lesson)
    accepted = accepted_service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )

    def fail() -> None:
        raise psycopg.OperationalError("private transaction detail")

    changed_lesson = replace(lesson, title="Changed authoritative title")
    with pytest.raises(DiscoveryError) as captured:
        service(
            changed_lesson,
            clock=datetime(2026, 10, 15, 18, 0, tzinfo=timezone.utc),
            before_projection_commit=fail,
        ).rebuild_learning_opportunity_projection(
            RebuildLearningOpportunityProjectionRequest()
        )

    assert captured.value.code is DiscoveryErrorCode.UNAVAILABLE
    assert "transaction" not in captured.value.message
    assert service(lesson).browse_learning_opportunities(
        BrowseLearningOpportunitiesRequest()
    ) == accepted


def test_corrupt_stored_projection_fails_closed_without_row_detail(
    lesson: PublishedLesson,
) -> None:
    accepted_service = service(lesson)
    seed(accepted_service, lesson)
    accepted_service.rebuild_learning_opportunity_projection(
        RebuildLearningOpportunityProjectionRequest()
    )
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            UPDATE curriculum.discovery_projection_records
            SET title = ' '
            """
        )

    with pytest.raises(DiscoveryError) as captured:
        service(lesson).browse_learning_opportunities(
            BrowseLearningOpportunitiesRequest()
        )

    assert captured.value.code is DiscoveryErrorCode.STALE_SOURCE
    assert "curriculum" not in captured.value.message.casefold()
    assert "title" not in captured.value.message.casefold()
