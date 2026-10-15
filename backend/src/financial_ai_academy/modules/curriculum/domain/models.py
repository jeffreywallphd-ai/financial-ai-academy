"""Curriculum exact-version references and discovery digest rules."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class PlacementReference:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str


def canonical_discovery_bytes(value: Mapping[str, object]) -> bytes:
    """Serialize discovery meaning for stable source/generation digests."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def discovery_digest(value: Mapping[str, object]) -> str:
    return hashlib.sha256(canonical_discovery_bytes(value)).hexdigest()


def projection_generation(
    records: Sequence[Mapping[str, object]],
) -> str:
    return hashlib.sha256(
        json.dumps(
            list(records),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
