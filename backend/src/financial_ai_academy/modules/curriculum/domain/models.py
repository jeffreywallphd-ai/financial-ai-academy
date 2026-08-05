"""Curriculum exact-version references."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlacementReference:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
