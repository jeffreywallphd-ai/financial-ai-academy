"""Transport-neutral exact-resolution port for admitted feature guidance."""

from __future__ import annotations

from typing import Protocol

from ..domain import FeatureGuidanceResolution


class FeatureGuidanceRegistryPort(Protocol):
    def resolve_with_mapping(
        self,
        surface_key: str,
        condition_key: str,
        mapping_version: str,
    ) -> FeatureGuidanceResolution: ...


__all__ = ["FeatureGuidanceRegistryPort"]
