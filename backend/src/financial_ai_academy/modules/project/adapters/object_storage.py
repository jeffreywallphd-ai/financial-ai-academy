"""Project adapter over the restrictive content-addressed filesystem store."""

from __future__ import annotations

from dataclasses import dataclass

from financial_ai_academy.platform.object_storage.filesystem import (
    FilesystemObjectStorage,
)

from ..ports.object_storage import StagedProjectObject


@dataclass(frozen=True, slots=True)
class _FilesystemStage:
    stage_id: str
    object_key: str


class ProjectFilesystemObjectStorage:
    """Expose one opaque artifact byte string without leaking storage paths."""

    _CONTENT_NAME = "content"

    def __init__(self, storage: FilesystemObjectStorage) -> None:
        self._storage = storage

    def stage(self, object_key: str, content: bytes) -> StagedProjectObject:
        staged = self._storage.stage(object_key, {self._CONTENT_NAME: content})
        return StagedProjectObject(staged.stage_id, staged.object_key)

    def finalize(self, staged: StagedProjectObject) -> None:
        self._storage.finalize(  # type: ignore[arg-type]
            _FilesystemStage(staged.stage_id, staged.object_key)
        )

    def discard_stage(self, staged: StagedProjectObject) -> None:
        self._storage.discard_stage(  # type: ignore[arg-type]
            _FilesystemStage(staged.stage_id, staged.object_key)
        )

    def read(self, object_key: str) -> bytes:
        files = self._storage.read(object_key)
        if set(files) != {self._CONTENT_NAME}:
            raise OSError("Stored Project artifact has an invalid shape.")
        return files[self._CONTENT_NAME]
