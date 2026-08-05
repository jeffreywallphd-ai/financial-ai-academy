"""Stable public types for the Content module."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from pathlib import Path
from typing import Protocol, runtime_checkable


class LessonErrorCode(StrEnum):
    INVALID_PACKAGE = "invalid_package"
    UNSUPPORTED_VERSION = "unsupported_version"
    IMMUTABLE_CONFLICT = "immutable_conflict"
    INTEGRITY_FAILURE = "integrity_failure"
    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"


class LessonReadError(RuntimeError):
    """Bounded application error without persistence or provider details."""

    def __init__(
        self,
        code: LessonErrorCode,
        message: str,
        *,
        reference: str = "lesson",
        diagnostic_code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )
        self.diagnostic_code = diagnostic_code

    def as_dict(self) -> dict[str, str]:
        result = {
            "code": self.code.value,
            "message": self.message,
            "reference": self.reference,
        }
        if self.diagnostic_code:
            result["diagnostic_code"] = self.diagnostic_code
        return result


@dataclass(frozen=True, slots=True)
class InlineText:
    value: str


@dataclass(frozen=True, slots=True)
class InlineCode:
    value: str


@dataclass(frozen=True, slots=True)
class SoftBreak:
    pass


@dataclass(frozen=True, slots=True)
class HardBreak:
    pass


@dataclass(frozen=True, slots=True)
class Emphasis:
    children: tuple["InlineNode", ...]


@dataclass(frozen=True, slots=True)
class Strong:
    children: tuple["InlineNode", ...]


@dataclass(frozen=True, slots=True)
class SourceLink:
    children: tuple["InlineNode", ...]
    href: str
    source_id: str


@dataclass(frozen=True, slots=True)
class AssetImage:
    asset_id: str
    alt_text: str


InlineNode = (
    InlineText
    | InlineCode
    | SoftBreak
    | HardBreak
    | Emphasis
    | Strong
    | SourceLink
    | AssetImage
)


@dataclass(frozen=True, slots=True)
class Heading:
    level: int
    children: tuple[InlineNode, ...]


@dataclass(frozen=True, slots=True)
class Paragraph:
    children: tuple[InlineNode, ...]


@dataclass(frozen=True, slots=True)
class CodeBlock:
    code: str
    language: str | None


@dataclass(frozen=True, slots=True)
class ThematicBreak:
    pass


@dataclass(frozen=True, slots=True)
class ListItem:
    blocks: tuple["BodyNode", ...]


@dataclass(frozen=True, slots=True)
class BulletList:
    items: tuple[ListItem, ...]


@dataclass(frozen=True, slots=True)
class OrderedList:
    start: int
    items: tuple[ListItem, ...]


BodyNode = Heading | Paragraph | CodeBlock | ThematicBreak | BulletList | OrderedList


@dataclass(frozen=True, slots=True)
class EducationalSource:
    source_id: str
    title: str
    publisher: str
    locator: str
    reviewed_on: date
    license_note: str | None


@dataclass(frozen=True, slots=True)
class PassiveAsset:
    asset_id: str
    media_type: str
    sha256: str
    alt_text: str


@dataclass(frozen=True, slots=True)
class PublicationProvenance:
    published_by: str
    published_at: datetime
    content_reviewed_on: date
    educational_use_notice: str


@dataclass(frozen=True, slots=True)
class PublishedLesson:
    package_id: str
    package_version: str
    package_digest: str
    title: str
    objectives: tuple[str, ...]
    body: tuple[BodyNode, ...]
    sources: tuple[EducationalSource, ...]
    assets: tuple[PassiveAsset, ...]
    provenance: PublicationProvenance


@dataclass(frozen=True, slots=True)
class AcceptedPackageVersion:
    package_id: str
    package_version: str
    package_digest: str
    publication_state: str
    published_at: datetime


@dataclass(frozen=True, slots=True)
class AdmitLessonPackageRequest:
    package_root: Path


@dataclass(frozen=True, slots=True)
class GetPublishedLessonVersionRequest:
    package_id: str
    package_version: str
    package_digest: str | None = None


@runtime_checkable
class ContentOperations(Protocol):
    def admit_lesson_package(
        self, request: AdmitLessonPackageRequest
    ) -> AcceptedPackageVersion: ...

    def get_published_lesson_version(
        self, request: GetPublishedLessonVersionRequest
    ) -> PublishedLesson: ...
