"""Untrusted lesson-package admission boundary."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Protocol

from ..domain.models import ValidatedLessonPackage


class PackageValidationFailure(ValueError):
    def __init__(self, code: str, reference: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )
        self.safe_message = message


class LessonPackageValidatorPort(Protocol):
    def validate_directory(self, root: Path) -> ValidatedLessonPackage: ...

    def validate_files(
        self, files: Mapping[str, bytes]
    ) -> ValidatedLessonPackage: ...
