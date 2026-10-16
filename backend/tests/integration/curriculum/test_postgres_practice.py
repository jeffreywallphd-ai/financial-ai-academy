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
    "d08e8f645941494bef7cc83c5987f36861023f4fba0b97653b91e5d774b202ca"
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
    yield
    for migration_id in (
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
    assert [item.item_type for item in first.items] == ["single_select"]
    with psycopg.connect(POSTGRES_DSN) as connection:
        assert connection.execute(
            "SELECT count(*) FROM curriculum.practice_placements"
        ).fetchone()[0] == 2
