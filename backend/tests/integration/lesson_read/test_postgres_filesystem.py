from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import psycopg
import pytest

from financial_ai_academy.modules.content.adapters.lesson_package import (
    ContractLessonPackageValidator,
)
from financial_ai_academy.modules.content.adapters.postgres_repository import (
    PostgresContentRepository,
)
from financial_ai_academy.modules.content.application.service import ContentService
from financial_ai_academy.modules.content.domain.models import StoredLessonPackage
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
    OpenPlacedLessonRequest,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)
from financial_ai_academy.platform.object_storage.filesystem import (
    FilesystemObjectStorage,
)


REPOSITORY = Path(__file__).resolve().parents[4]
APPROVED = (
    REPOSITORY
    / "contracts/compatibility/lesson-package/v1/approved/intro-risk-return"
)
SCHEMAS = REPOSITORY / "contracts/learning/lesson-package/v1"
MIGRATIONS = REPOSITORY / "backend/migrations"
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(
        POSTGRES_DSN is None,
        reason="FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN is not configured",
    ),
]


@pytest.fixture(scope="module", autouse=True)
def migrated_database() -> object:
    assert POSTGRES_DSN is not None
    runner = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS)
    runner.rollback_all()
    statuses = runner.apply_all()
    assert [status.migration_id for status in statuses] == [
        "0001_content_lesson_package_versions",
        "0002_curriculum_lesson_placements",
    ]
    assert runner.apply_all() == statuses
    yield
    runner.rollback_all()


@pytest.fixture(autouse=True)
def empty_module_tables(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                curriculum.lesson_placements,
                content.lesson_package_versions
            """
        )


def build_application(
    tmp_path: Path,
) -> tuple[ContentService, CurriculumService, FilesystemObjectStorage]:
    assert POSTGRES_DSN is not None
    storage = FilesystemObjectStorage(tmp_path / "objects")
    content = ContentService(
        PostgresContentRepository(POSTGRES_DSN),
        storage,
        ContractLessonPackageValidator(SCHEMAS),
    )
    curriculum = CurriculumService(
        PostgresCurriculumRepository(POSTGRES_DSN),
        PublicContentGateway(content),
    )
    return content, curriculum, storage


def admit_and_place(
    content: ContentService,
    curriculum: CurriculumService,
) -> tuple[str, str]:
    accepted = content.admit_lesson_package(
        AdmitLessonPackageRequest(APPROVED)
    )
    placement = curriculum.create_lesson_placement(
        CreateLessonPlacementRequest(
            placement_id="intro-risk-return-primary",
            package_id=accepted.package_id,
            package_version=accepted.package_version,
            package_digest=accepted.package_digest,
        )
    )
    return placement.placement_id, accepted.package_digest


def conflicting_package(tmp_path: Path) -> Path:
    target = tmp_path / "conflict"
    shutil.copytree(APPROVED, target)
    manifest_path = target / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["title"] = "Conflicting immutable bytes"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + chr(10), encoding="utf-8"
    )
    return target


def test_real_postgres_and_filesystem_admit_place_and_open(
    tmp_path: Path,
) -> None:
    content, curriculum, _storage = build_application(tmp_path)

    placement_id, digest = admit_and_place(content, curriculum)
    repeated_id, repeated_digest = admit_and_place(content, curriculum)
    reading = curriculum.open_placed_lesson(
        OpenPlacedLessonRequest(placement_id)
    )

    assert (repeated_id, repeated_digest) == (placement_id, digest)
    assert reading.package_digest == digest
    assert reading.title == "Understanding Risk and Return"
    assert len(reading.objectives) == 2
    assert len(reading.body) == 5
    assert reading.sources[0].publisher == (
        "U.S. Securities and Exchange Commission"
    )


def test_real_postgres_rejects_immutable_conflict_without_replacement(
    tmp_path: Path,
) -> None:
    assert POSTGRES_DSN is not None
    content, curriculum, _storage = build_application(tmp_path)
    _placement_id, accepted_digest = admit_and_place(content, curriculum)

    with pytest.raises(LessonReadError) as captured:
        content.admit_lesson_package(
            AdmitLessonPackageRequest(conflicting_package(tmp_path))
        )

    assert captured.value.code is LessonErrorCode.IMMUTABLE_CONFLICT
    with psycopg.connect(POSTGRES_DSN) as connection:
        row = connection.execute(
            """
            SELECT package_digest
            FROM content.lesson_package_versions
            WHERE package_id = 'intro-risk-return'
              AND package_version = '1.0.0'
            """
        ).fetchone()
    assert row is not None
    assert row[0] == accepted_digest


def test_stale_curriculum_reference_returns_unavailable_without_latest(
    tmp_path: Path,
) -> None:
    assert POSTGRES_DSN is not None
    content, curriculum, _storage = build_application(tmp_path)
    placement_id, _digest = admit_and_place(content, curriculum)
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            DELETE FROM content.lesson_package_versions
            WHERE package_id = 'intro-risk-return'
              AND package_version = '1.0.0'
            """
        )

    with pytest.raises(LessonReadError) as captured:
        curriculum.open_placed_lesson(OpenPlacedLessonRequest(placement_id))

    assert captured.value.code is LessonErrorCode.UNAVAILABLE


def test_corrupt_object_fails_closed_after_postgres_resolution(
    tmp_path: Path,
) -> None:
    content, curriculum, _storage = build_application(tmp_path)
    placement_id, digest = admit_and_place(content, curriculum)
    lesson_path = (
        tmp_path
        / "objects/objects"
        / digest[:2]
        / digest
        / "lesson.md"
    )
    lesson_path.write_bytes(b"corrupt")

    with pytest.raises(LessonReadError) as captured:
        curriculum.open_placed_lesson(OpenPlacedLessonRequest(placement_id))

    assert captured.value.code is LessonErrorCode.INTEGRITY_FAILURE
    assert str(lesson_path) not in str(captured.value.as_dict())


class FailingPostgresContentRepository:
    def get(
        self, package_id: str, package_version: str
    ) -> StoredLessonPackage | None:
        return None

    def save_if_absent(
        self, package: StoredLessonPackage
    ) -> tuple[StoredLessonPackage, bool]:
        raise psycopg.OperationalError("simulated transaction failure")


def test_database_failure_never_creates_partial_publication(
    tmp_path: Path,
) -> None:
    assert POSTGRES_DSN is not None
    storage = FilesystemObjectStorage(tmp_path / "objects")
    content = ContentService(
        FailingPostgresContentRepository(),
        storage,
        ContractLessonPackageValidator(SCHEMAS),
    )

    with pytest.raises(LessonReadError) as captured:
        content.admit_lesson_package(AdmitLessonPackageRequest(APPROVED))

    assert captured.value.code is LessonErrorCode.UNAVAILABLE
    with psycopg.connect(POSTGRES_DSN) as connection:
        count = connection.execute(
            "SELECT count(*) FROM content.lesson_package_versions"
        ).fetchone()
    assert count == (0,)
    digest = (
        "576d543b404a7f70f2e5bebee55c32a3f945d8e8da73654c43ef92e656aee008"
    )
    assert "manifest.json" in storage.read(f"{digest[:2]}/{digest}")
