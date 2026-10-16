from __future__ import annotations

import os
from pathlib import Path

import psycopg
import pytest

from financial_ai_academy.modules.assessment.adapters.content_gateway import (
    PublicContentDefinitionGateway,
)
from financial_ai_academy.modules.assessment.adapters.curriculum_gateway import (
    PublicCurriculumAssessmentGateway,
)
from financial_ai_academy.modules.assessment.adapters.practice_contract import (
    ContractPracticeDefinitionAdapter,
)
from financial_ai_academy.modules.assessment.application.service import (
    AssessmentService,
)
from financial_ai_academy.modules.assessment.public import (
    OpenPlacedPracticeRequest,
)
from financial_ai_academy.modules.content.adapters.lesson_package import (
    ContractLessonPackageValidator,
)
from financial_ai_academy.modules.content.adapters.postgres_repository import (
    PostgresContentRepository,
)
from financial_ai_academy.modules.content.application.service import ContentService
from financial_ai_academy.modules.content.public import (
    AdmitLessonPackageRequest,
    LessonErrorCode,
    LessonReadError,
)
from financial_ai_academy.modules.curriculum.adapters.content_gateway import (
    PublicContentGateway,
)
from financial_ai_academy.modules.curriculum.adapters.postgres_repository import (
    PostgresCurriculumRepository,
)
from financial_ai_academy.modules.curriculum.application.service import (
    CurriculumService,
)
from financial_ai_academy.modules.curriculum.public import (
    CreateLessonPlacementRequest,
    CreatePracticePlacementRequest,
    PracticeReviewDestination,
    PracticeReviewResource,
    PracticeReviewState,
    PracticeReviewTarget,
    PracticeReviewUnavailableReason,
    RegisterPracticeReviewTargetRequest,
    ResolvePracticeReviewTargetsRequest,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)
from financial_ai_academy.platform.object_storage.filesystem import (
    FilesystemObjectStorage,
)


REPOSITORY = Path(__file__).resolve().parents[4]
PACKAGE = (
    REPOSITORY
    / "contracts/compatibility/lesson-package/v1/approved/intro-risk-return-practice"
)
LESSON_SCHEMAS = REPOSITORY / "contracts/learning/lesson-package/v1"
PRACTICE_SCHEMAS = REPOSITORY / "contracts/learning/assessment/practice/v1"
MIGRATIONS = REPOSITORY / "backend/migrations"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
DEFINITION_DIGEST = (
    "82cdc82c402aacdb0070fb19671d896ae22a4c16d338ccbf27f02a51a396d527"
)

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(
        POSTGRES_DSN is None,
        reason="FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN is not configured",
    ),
]


def _remove_stream(migration_id: str, down: Path) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(down.read_text(encoding="utf-8"))
        connection.execute(
            "DELETE FROM platform.schema_migrations WHERE migration_id = %s",
            (migration_id,),
        )


@pytest.fixture(scope="module", autouse=True)
def migrated_database() -> object:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute("DROP SCHEMA IF EXISTS curriculum CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS content CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS platform CASCADE")
    root = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS)
    curriculum = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS / "curriculum")
    root.apply_all()
    identifiers = {item.migration_id for item in curriculum.apply_all()}
    assert "curriculum_0004_practice_placements" in identifiers
    assert "curriculum_0005_practice_review_targets" in identifiers
    yield
    for migration_id in (
        "curriculum_0005_practice_review_targets",
        "curriculum_0004_practice_placements",
        "curriculum_0003_curriculum_graphs",
        "curriculum_0002_discovery_projection",
        "curriculum_0001_assessment_placements",
    ):
        _remove_stream(
            migration_id,
            MIGRATIONS / f"curriculum/{migration_id}.down.sql",
        )
    root.rollback_all()


@pytest.fixture(autouse=True)
def empty_tables(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                curriculum.practice_review_targets,
                curriculum.practice_placements,
                curriculum.lesson_placements,
                content.lesson_package_versions
            CASCADE
            """
        )


def test_exact_practice_opens_through_public_module_boundaries(
    tmp_path: Path,
) -> None:
    assert POSTGRES_DSN is not None
    content = ContentService(
        PostgresContentRepository(POSTGRES_DSN),
        FilesystemObjectStorage(tmp_path / "objects"),
        ContractLessonPackageValidator(LESSON_SCHEMAS),
    )
    curriculum = CurriculumService(
        PostgresCurriculumRepository(POSTGRES_DSN),
        PublicContentGateway(content),
    )
    accepted = content.admit_lesson_package(AdmitLessonPackageRequest(PACKAGE))
    lesson = curriculum.create_lesson_placement(
        CreateLessonPlacementRequest(
            placement_id="intro-risk-return-primary",
            package_id=accepted.package_id,
            package_version=accepted.package_version,
            package_digest=accepted.package_digest,
        )
    )
    second_lesson = curriculum.create_lesson_placement(
        CreateLessonPlacementRequest(
            placement_id="intro-risk-return-secondary",
            package_id=accepted.package_id,
            package_version=accepted.package_version,
            package_digest=accepted.package_digest,
        )
    )
    curriculum.create_practice_placement(
        CreatePracticePlacementRequest(
            placement_id=lesson.placement_id,
            package_id=lesson.package_id,
            package_version=lesson.package_version,
            package_digest=lesson.package_digest,
            practice_id="risk-return-practice",
            practice_version="1.0.0",
            definition_digest=DEFINITION_DIGEST,
        )
    )
    curriculum.create_practice_placement(
        CreatePracticePlacementRequest(
            placement_id=second_lesson.placement_id,
            package_id=second_lesson.package_id,
            package_version=second_lesson.package_version,
            package_digest=second_lesson.package_digest,
            practice_id="risk-return-practice",
            practice_version="1.0.0",
            definition_digest=DEFINITION_DIGEST,
        )
    )
    with pytest.raises(LessonReadError) as captured:
        curriculum.create_practice_placement(
            CreatePracticePlacementRequest(
                placement_id=lesson.placement_id,
                package_id=lesson.package_id,
                package_version=lesson.package_version,
                package_digest=lesson.package_digest,
                practice_id="risk-return-practice",
                practice_version="1.0.0",
                definition_digest="e" * 64,
            )
        )
    assert captured.value.code is LessonErrorCode.IMMUTABLE_CONFLICT
    assessment = AssessmentService(
        PublicCurriculumAssessmentGateway(curriculum),
        PublicContentDefinitionGateway(content),
        object(),
        object(),
        object(),
        object(),
        object(),
        ContractPracticeDefinitionAdapter(PRACTICE_SCHEMAS),
    )

    first = assessment.open_placed_practice(
        OpenPlacedPracticeRequest(lesson.placement_id)
    )
    second = assessment.open_placed_practice(
        OpenPlacedPracticeRequest(lesson.placement_id)
    )
    reused = assessment.open_placed_practice(
        OpenPlacedPracticeRequest(second_lesson.placement_id)
    )

    assert first == second
    assert reused.definition_digest == first.definition_digest
    assert reused.placement_id == second_lesson.placement_id
    assert first.definition_digest == DEFINITION_DIGEST
    assert [item.item_type for item in first.items] == [
        "single_select",
        "multiple_select",
        "numeric_entry",
    ]
    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute(
            "SELECT count(*) FROM curriculum.practice_placements"
        ).fetchone()[0] == 2


def test_exact_review_targets_survive_restart_and_remain_append_only(
    tmp_path: Path,
) -> None:
    assert POSTGRES_DSN is not None
    content = ContentService(
        PostgresContentRepository(POSTGRES_DSN),
        FilesystemObjectStorage(tmp_path / "objects"),
        ContractLessonPackageValidator(LESSON_SCHEMAS),
    )
    repository = PostgresCurriculumRepository(POSTGRES_DSN)
    curriculum = CurriculumService(repository, PublicContentGateway(content))
    accepted = content.admit_lesson_package(AdmitLessonPackageRequest(PACKAGE))
    practice_lesson = curriculum.create_lesson_placement(
        CreateLessonPlacementRequest(
            placement_id="risk-return-practice-placement",
            package_id=accepted.package_id,
            package_version=accepted.package_version,
            package_digest=accepted.package_digest,
        )
    )
    review_lesson = curriculum.create_lesson_placement(
        CreateLessonPlacementRequest(
            placement_id="risk-return-reading-placement",
            package_id=accepted.package_id,
            package_version=accepted.package_version,
            package_digest=accepted.package_digest,
        )
    )
    curriculum.create_practice_placement(
        CreatePracticePlacementRequest(
            placement_id=practice_lesson.placement_id,
            package_id=practice_lesson.package_id,
            package_version=practice_lesson.package_version,
            package_digest=practice_lesson.package_digest,
            practice_id="risk-return-practice",
            practice_version="1.0.0",
            definition_digest=DEFINITION_DIGEST,
        )
    )
    target = PracticeReviewTarget(
        schema_version="1.0.0",
        practice_placement_id=practice_lesson.placement_id,
        resource_id="risk-return-review",
        resource_version="1.0.0",
        resource_digest="c" * 64,
        resource_title="Review risk and return",
        state=PracticeReviewState.AVAILABLE,
        destination=PracticeReviewDestination(
            placement_id=review_lesson.placement_id,
            package_id=review_lesson.package_id,
            package_version=review_lesson.package_version,
            package_digest=review_lesson.package_digest,
            section_id="risk-return-review-section",
        ),
    )
    assert curriculum.register_practice_review_target(
        RegisterPracticeReviewTargetRequest(target)
    ) == target
    restarted = CurriculumService(
        PostgresCurriculumRepository(POSTGRES_DSN),
        PublicContentGateway(content),
    )
    resolved = restarted.resolve_practice_review_targets(
        ResolvePracticeReviewTargetsRequest(
            practice_placement_id=practice_lesson.placement_id,
            resources=(
                PracticeReviewResource(
                    resource_id="risk-return-review",
                    resource_version="1.0.0",
                    resource_digest="c" * 64,
                    resource_title="Review risk and return",
                ),
                PracticeReviewResource(
                    resource_id="additional-review",
                    resource_version="1.1.0",
                    resource_digest="d" * 64,
                    resource_title="Additional review",
                ),
            ),
        )
    )
    assert resolved[0] == target
    assert resolved[1].state is PracticeReviewState.UNAVAILABLE
    assert (
        resolved[1].unavailable_reason
        is PracticeReviewUnavailableReason.MAPPING_NOT_FOUND
    )
    with psycopg.connect(POSTGRES_DSN) as connection:
        with pytest.raises(psycopg.DatabaseError):
            connection.execute(
                """
                UPDATE curriculum.practice_review_targets
                SET resource_title = 'Changed'
                """
            )
