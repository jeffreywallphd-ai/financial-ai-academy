"""Content-owned object-storage port."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol


@dataclass(frozen=True, slots=True)
class StagedObject:
    stage_id: str
    object_key: str


class ObjectStoragePort(Protocol):
    def stage(
        self, object_key: str, files: Mapping[str, bytes]
    ) -> StagedObject: ...

    def finalize(self, staged: StagedObject) -> None: ...

    def discard_stage(self, staged: StagedObject) -> None: ...

    def read(self, object_key: str) -> Mapping[str, bytes]: ...
