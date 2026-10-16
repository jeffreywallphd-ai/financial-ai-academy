"""Project-owned port for inert content-addressed artifact bytes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class StagedProjectObject:
    stage_id: str
    object_key: str


class ProjectObjectStoragePort(Protocol):
    def stage(self, object_key: str, content: bytes) -> StagedProjectObject: ...

    def finalize(self, staged: StagedProjectObject) -> None: ...

    def discard_stage(self, staged: StagedProjectObject) -> None: ...

    def read(self, object_key: str) -> bytes: ...
