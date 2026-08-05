"""Persistence contracts owned by Content."""

from __future__ import annotations

from typing import Protocol

from ..domain.models import StoredLessonPackage


class PackageVersionConflict(RuntimeError):
    pass


class ContentRepositoryPort(Protocol):
    def get(
        self, package_id: str, package_version: str
    ) -> StoredLessonPackage | None: ...

    def save_if_absent(
        self, package: StoredLessonPackage
    ) -> tuple[StoredLessonPackage, bool]: ...
