"""Atomic lesson-package admission and exact-version reads."""

from __future__ import annotations

from ..domain.models import StoredLessonPackage, ValidatedLessonPackage
from ..ports.object_storage import ObjectStoragePort, StagedObject
from ..ports.package_validator import (
    LessonPackageValidatorPort,
    PackageValidationFailure,
)
from ..ports.repositories import ContentRepositoryPort, PackageVersionConflict
from ..public import (
    AcceptedPackageVersion,
    AdmitLessonPackageRequest,
    GetPublishedLessonVersionRequest,
    LessonErrorCode,
    LessonReadError,
    PublishedLesson,
)


class ContentService:
    """Content facade; callers never receive persistence or storage identifiers."""

    def __init__(
        self,
        repository: ContentRepositoryPort,
        object_storage: ObjectStoragePort,
        validator: LessonPackageValidatorPort,
    ) -> None:
        self._repository = repository
        self._object_storage = object_storage
        self._validator = validator

    def admit_lesson_package(
        self, request: AdmitLessonPackageRequest
    ) -> AcceptedPackageVersion:
        validated = self._validate_for_admission(request)
        lesson = validated.lesson
        existing = self._get_existing(lesson.package_id, lesson.package_version)
        if existing is not None:
            self._assert_same_immutable_version(existing.lesson, lesson)
            self._verify_stored(existing)
            return self._accepted(existing.lesson)

        object_key = self._object_key(lesson.package_digest)
        try:
            staged = self._object_storage.stage(object_key, validated.files)
        except (OSError, RuntimeError, ValueError) as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Lesson package storage is unavailable.",
                reference=f"{lesson.package_id}@{lesson.package_version}",
            ) from error

        try:
            self._object_storage.finalize(staged)
        except (OSError, RuntimeError, ValueError) as error:
            self._discard_stage(staged)
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Lesson package storage could not be finalized.",
                reference=f"{lesson.package_id}@{lesson.package_version}",
            ) from error

        candidate = StoredLessonPackage(lesson=lesson, object_key=object_key)
        # An existing digest-addressed orphan may have won the finalize race.
        # Revalidate the final bytes before making metadata visible.
        self._verify_stored(candidate)
        try:
            stored, _created = self._repository.save_if_absent(candidate)
        except PackageVersionConflict as error:
            raise self._immutable_conflict(lesson) from error
        except Exception as error:
            # Final bytes are deliberately retained as an unreferenced object for
            # bounded reconciliation; no published metadata was made visible.
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Lesson publication metadata is unavailable.",
                reference=f"{lesson.package_id}@{lesson.package_version}",
            ) from error

        self._assert_same_immutable_version(stored.lesson, lesson)
        return self._accepted(stored.lesson)

    def get_published_lesson_version(
        self, request: GetPublishedLessonVersionRequest
    ) -> PublishedLesson:
        stored = self._get_existing(request.package_id, request.package_version)
        if stored is None:
            raise LessonReadError(
                LessonErrorCode.NOT_FOUND,
                "The exact published lesson version was not found.",
                reference=f"{request.package_id}@{request.package_version}",
            )
        if (
            request.package_digest is not None
            and request.package_digest != stored.lesson.package_digest
        ):
            raise LessonReadError(
                LessonErrorCode.NOT_FOUND,
                "The exact published lesson digest was not found.",
                reference=f"{request.package_id}@{request.package_version}",
            )
        return self._verify_stored(stored)

    def _validate_for_admission(
        self, request: AdmitLessonPackageRequest
    ) -> ValidatedLessonPackage:
        try:
            return self._validator.validate_directory(request.package_root)
        except PackageValidationFailure as error:
            if error.code in {
                "package.unsupported_version",
                "package.unsupported_capability",
            }:
                public_code = LessonErrorCode.UNSUPPORTED_VERSION
            elif error.code in {
                "package.integrity_mismatch",
                "package.media_mismatch",
            }:
                public_code = LessonErrorCode.INTEGRITY_FAILURE
            else:
                public_code = LessonErrorCode.INVALID_PACKAGE
            raise LessonReadError(
                public_code,
                "Lesson package admission was rejected.",
                reference=error.reference,
                diagnostic_code=error.code,
            ) from error

    def _get_existing(
        self, package_id: str, package_version: str
    ) -> StoredLessonPackage | None:
        try:
            return self._repository.get(package_id, package_version)
        except Exception as error:
            raise LessonReadError(
                LessonErrorCode.UNAVAILABLE,
                "Lesson publication metadata is unavailable.",
                reference=f"{package_id}@{package_version}",
            ) from error

    def _verify_stored(self, stored: StoredLessonPackage) -> PublishedLesson:
        try:
            files = self._object_storage.read(stored.object_key)
            measured = self._validator.validate_files(files)
        except (OSError, RuntimeError, ValueError, PackageValidationFailure) as error:
            diagnostic = (
                error.code if isinstance(error, PackageValidationFailure) else None
            )
            raise LessonReadError(
                LessonErrorCode.INTEGRITY_FAILURE,
                "Stored lesson integrity verification failed.",
                reference=(
                    f"{stored.lesson.package_id}@"
                    f"{stored.lesson.package_version}"
                ),
                diagnostic_code=diagnostic,
            ) from error
        expected = stored.lesson
        actual = measured.lesson
        if (
            expected.package_id,
            expected.package_version,
            expected.package_digest,
        ) != (
            actual.package_id,
            actual.package_version,
            actual.package_digest,
        ):
            raise LessonReadError(
                LessonErrorCode.INTEGRITY_FAILURE,
                "Stored lesson metadata and bytes do not match.",
                reference=f"{expected.package_id}@{expected.package_version}",
            )
        return actual

    @staticmethod
    def _assert_same_immutable_version(
        accepted: PublishedLesson, candidate: PublishedLesson
    ) -> None:
        if accepted.package_digest != candidate.package_digest:
            raise ContentService._immutable_conflict(candidate)

    @staticmethod
    def _immutable_conflict(lesson: PublishedLesson) -> LessonReadError:
        return LessonReadError(
            LessonErrorCode.IMMUTABLE_CONFLICT,
            "The package identity and version already map to different bytes.",
            reference=f"{lesson.package_id}@{lesson.package_version}",
            diagnostic_code="package.immutable_conflict",
        )

    @staticmethod
    def _accepted(lesson: PublishedLesson) -> AcceptedPackageVersion:
        return AcceptedPackageVersion(
            package_id=lesson.package_id,
            package_version=lesson.package_version,
            package_digest=lesson.package_digest,
            publication_state="published",
            published_at=lesson.provenance.published_at,
        )

    @staticmethod
    def _object_key(package_digest: str) -> str:
        return f"{package_digest[:2]}/{package_digest}"

    def _discard_stage(self, staged: StagedObject) -> None:
        try:
            self._object_storage.discard_stage(staged)
        except (OSError, RuntimeError, ValueError):
            pass
