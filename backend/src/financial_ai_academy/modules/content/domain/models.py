"""Internal Content records; storage identifiers never cross the public facade."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ..public import PublishedLesson


@dataclass(frozen=True, slots=True)
class ValidatedLessonPackage:
    lesson: PublishedLesson
    files: Mapping[str, bytes]
    index: tuple[dict[str, object], ...]


@dataclass(frozen=True, slots=True)
class StoredLessonPackage:
    lesson: PublishedLesson
    object_key: str
