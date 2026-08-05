from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import fields
from pathlib import Path

import pytest

from financial_ai_academy.modules.content.adapters.lesson_package import (
    ContractLessonPackageValidator,
)
from financial_ai_academy.modules.content.application.service import ContentService
from financial_ai_academy.modules.content.domain.models import StoredLessonPackage
from financial_ai_academy.modules.content.ports.repositories import (
    PackageVersionConflict,
)
from financial_ai_academy.modules.content.public import (
    AdmitLessonPackageRequest,
    GetPublishedLessonVersionRequest,
    LessonErrorCode,
    LessonReadError,
    PublishedLesson,
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


class MemoryContentRepository:
    def __init__(self) -> None:
        self.records: dict[tuple[str, str], StoredLessonPackage] = {}

    def get(
        self, package_id: str, package_version: str
    ) -> StoredLessonPackage | None:
        return self.records.get((package_id, package_version))

    def save_if_absent(
        self, package: StoredLessonPackage
    ) -> tuple[StoredLessonPackage, bool]:
        key = (package.lesson.package_id, package.lesson.package_version)
        existing = self.records.get(key)
        if existing is None:
            self.records[key] = package
            return package, True
        if existing.lesson.package_digest != package.lesson.package_digest:
            raise PackageVersionConflict
        return existing, False


class FailingStorage:
    def stage(self, object_key: str, files: object) -> object:
        raise OSError("sensitive absolute path")

    def finalize(self, staged: object) -> None:
        raise AssertionError("finalize must not run")

    def discard_stage(self, staged: object) -> None:
        pass

    def read(self, object_key: str) -> object:
        raise AssertionError("read must not run")


class FailingRepository(MemoryContentRepository):
    def save_if_absent(
        self, package: StoredLessonPackage
    ) -> tuple[StoredLessonPackage, bool]:
        raise RuntimeError("database details")


def build_service(
    tmp_path: Path,
    repository: MemoryContentRepository | None = None,
) -> tuple[ContentService, MemoryContentRepository, FilesystemObjectStorage]:
    selected = repository or MemoryContentRepository()
    storage = FilesystemObjectStorage(tmp_path / "objects")
    service = ContentService(
        selected,
        storage,
        ContractLessonPackageValidator(SCHEMAS),
    )
    return service, selected, storage


def changed_package(tmp_path: Path) -> Path:
    target = tmp_path / "changed"
    shutil.copytree(APPROVED, target)
    manifest_path = target / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["title"] = "A conflicting immutable lesson"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + chr(10), encoding="utf-8"
    )
    return target


def unsafe_package(tmp_path: Path) -> Path:
    target = tmp_path / "unsafe"
    shutil.copytree(APPROVED, target)
    lesson_path = target / "lesson.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8")
        + chr(10)
        + "<script>alert(1)</script>"
        + chr(10),
        encoding="utf-8",
    )
    manifest_path = target / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    value = lesson_path.read_bytes()
    manifest["lesson"]["size_bytes"] = len(value)
    manifest["lesson"]["sha256"] = hashlib.sha256(value).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + chr(10), encoding="utf-8"
    )
    return target


def test_admit_open_and_identical_retry_are_safe_and_idempotent(
    tmp_path: Path,
) -> None:
    service, repository, _storage = build_service(tmp_path)

    first = service.admit_lesson_package(AdmitLessonPackageRequest(APPROVED))
    second = service.admit_lesson_package(AdmitLessonPackageRequest(APPROVED))
    lesson = service.get_published_lesson_version(
        GetPublishedLessonVersionRequest(
            first.package_id,
            first.package_version,
            first.package_digest,
        )
    )

    assert first == second
    assert first.package_digest == (
        "576d543b404a7f70f2e5bebee55c32a3f945d8e8da73654c43ef92e656aee008"
    )
    assert lesson.title == "Understanding Risk and Return"
    assert len(lesson.objectives) == 2
    assert lesson.sources[0].locator.startswith("https://")
    assert len(lesson.body) == 5
    assert len(repository.records) == 1


def test_immutable_conflict_preserves_the_accepted_package(
    tmp_path: Path,
) -> None:
    service, repository, _storage = build_service(tmp_path)
    accepted = service.admit_lesson_package(
        AdmitLessonPackageRequest(APPROVED)
    )

    with pytest.raises(LessonReadError) as captured:
        service.admit_lesson_package(
            AdmitLessonPackageRequest(changed_package(tmp_path))
        )

    assert captured.value.code is LessonErrorCode.IMMUTABLE_CONFLICT
    stored = next(iter(repository.records.values()))
    assert stored.lesson.package_digest == accepted.package_digest
    assert accepted.package_digest not in captured.value.message


def test_unsafe_package_fails_before_storage_or_publication(
    tmp_path: Path,
) -> None:
    repository = MemoryContentRepository()
    service = ContentService(
        repository,
        FailingStorage(),
        ContractLessonPackageValidator(SCHEMAS),
    )

    with pytest.raises(LessonReadError) as captured:
        service.admit_lesson_package(
            AdmitLessonPackageRequest(unsafe_package(tmp_path))
        )

    assert captured.value.code is LessonErrorCode.INVALID_PACKAGE
    assert captured.value.diagnostic_code == "markup.unsafe_html"
    assert repository.records == {}


def test_storage_failure_is_redacted_and_creates_no_publication() -> None:
    repository = MemoryContentRepository()
    service = ContentService(
        repository,
        FailingStorage(),
        ContractLessonPackageValidator(SCHEMAS),
    )

    with pytest.raises(LessonReadError) as captured:
        service.admit_lesson_package(AdmitLessonPackageRequest(APPROVED))

    assert captured.value.code is LessonErrorCode.UNAVAILABLE
    assert "sensitive" not in str(captured.value)
    assert repository.records == {}


def test_database_failure_leaves_only_a_reconcilable_orphan_object(
    tmp_path: Path,
) -> None:
    repository = FailingRepository()
    service, _repository, storage = build_service(tmp_path, repository)
    digest = (
        "576d543b404a7f70f2e5bebee55c32a3f945d8e8da73654c43ef92e656aee008"
    )

    with pytest.raises(LessonReadError) as captured:
        service.admit_lesson_package(AdmitLessonPackageRequest(APPROVED))

    assert captured.value.code is LessonErrorCode.UNAVAILABLE
    assert repository.records == {}
    assert set(storage.read(f"{digest[:2]}/{digest}")) == {
        "manifest.json",
        "lesson.md",
        "assessments/check-1.json",
    }


def test_conflicting_orphan_bytes_never_become_published(
    tmp_path: Path,
) -> None:
    service, repository, storage = build_service(tmp_path)
    digest = (
        "576d543b404a7f70f2e5bebee55c32a3f945d8e8da73654c43ef92e656aee008"
    )
    object_key = f"{digest[:2]}/{digest}"
    orphan = storage.stage(object_key, {"manifest.json": b"{}"})
    storage.finalize(orphan)

    with pytest.raises(LessonReadError) as captured:
        service.admit_lesson_package(AdmitLessonPackageRequest(APPROVED))

    assert captured.value.code is LessonErrorCode.INTEGRITY_FAILURE
    assert repository.records == {}


def test_corrupted_stored_bytes_fail_closed_without_path_leak(
    tmp_path: Path,
) -> None:
    service, _repository, _storage = build_service(tmp_path)
    accepted = service.admit_lesson_package(
        AdmitLessonPackageRequest(APPROVED)
    )
    stored_lesson = (
        tmp_path
        / "objects/objects"
        / accepted.package_digest[:2]
        / accepted.package_digest
        / "lesson.md"
    )
    stored_lesson.write_text("corrupted", encoding="utf-8")

    with pytest.raises(LessonReadError) as captured:
        service.get_published_lesson_version(
            GetPublishedLessonVersionRequest(
                accepted.package_id,
                accepted.package_version,
                accepted.package_digest,
            )
        )

    assert captured.value.code is LessonErrorCode.INTEGRITY_FAILURE
    assert str(stored_lesson) not in str(captured.value.as_dict())


def test_public_result_has_no_storage_or_database_field() -> None:
    prohibited = {"path", "object_key", "storage_key", "row", "driver"}
    public_fields = {field.name for field in fields(PublishedLesson)}
    assert public_fields.isdisjoint(prohibited)
