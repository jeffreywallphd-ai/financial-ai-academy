"""Transport-neutral exact-read port for admitted contextual help."""

from __future__ import annotations

from typing import Protocol

from ..domain import ContextualHelpRecord


class ContextualHelpRegistryPort(Protocol):
    @property
    def records(self) -> tuple[ContextualHelpRecord, ...]: ...

    def get(
        self,
        context_key: str,
        context_version: str,
    ) -> ContextualHelpRecord: ...


__all__ = ["ContextualHelpRegistryPort"]
