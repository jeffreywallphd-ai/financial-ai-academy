"""Checked-in immutable feature-guidance registry adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

from ..domain import (
    FeatureGuidanceMapping,
    FeatureGuidanceRecord,
    FeatureGuidanceRegistry,
    GuidanceError,
    GuidanceErrorCode,
    PlatformHelpTopic,
)
from .feature_guidance_contract import (
    feature_guidance_from_mapping,
    feature_mapping_from_mapping,
)
from .immutable_corpus import ImmutablePlatformHelpCorpus, PLATFORM_HELP_SOURCE_FINGERPRINTS


FEATURE_GUIDANCE_MANIFEST_VERSION = "1.0.0"
REQUIRED_FEATURE_GUIDANCE_IDENTITIES = frozenset({
    ("ai-help-execution-unavailable", "1.0.0"),
    ("lesson-version-unavailable", "1.0.0"),
    ("practice-write-uncertain", "1.0.0"),
    ("project-artifact-inert", "1.0.0"),
    ("saved-source-unavailable", "1.0.0"),
})
REQUIRED_FEATURE_MAPPING_IDENTITIES = frozenset({
    ("ai-assistance", "provider-execution-not-enabled", "1.0.0"),
    ("lesson-reading", "exact-version-unavailable", "1.0.0"),
    ("practice-activity", "write-outcome-uncertain", "1.0.0"),
    ("project-workspace", "artifact-inert", "1.0.0"),
    ("saved-learning", "source-unavailable", "1.0.0"),
})


def default_feature_guidance_registry_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "resources/feature-guidance/v1"


def _load_objects(root: Path, child: str) -> list[dict[str, Any]]:
    directory = root / child
    files = sorted(directory.glob("*.json"), key=lambda path: path.name)
    if not directory.is_dir() or not files:
        raise OSError("registry unavailable")
    values: list[dict[str, Any]] = []
    for path in files:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("registry item must be an object")
        values.append(value)
    return values


class ImmutableFeatureGuidanceRegistry:
    """Load the complete exact record/mapping registry or expose nothing."""

    def __init__(
        self,
        registry_dir: Path | None = None,
        topics: Sequence[PlatformHelpTopic] | None = None,
    ) -> None:
        root = (registry_dir or default_feature_guidance_registry_dir()).resolve()
        try:
            records = tuple(feature_guidance_from_mapping(value) for value in _load_objects(root, "records"))
            mappings = tuple(feature_mapping_from_mapping(value) for value in _load_objects(root, "mappings"))
            if not REQUIRED_FEATURE_GUIDANCE_IDENTITIES <= {(item.guidance_id, item.guidance_version) for item in records}:
                raise GuidanceError(GuidanceErrorCode.INVALID_RECORD, "The feature guidance registry is unavailable.", reference=f"feature-guidance-manifest@{FEATURE_GUIDANCE_MANIFEST_VERSION}")
            if not REQUIRED_FEATURE_MAPPING_IDENTITIES <= {(item.surface_key, item.condition_key, item.mapping_version) for item in mappings}:
                raise GuidanceError(GuidanceErrorCode.INVALID_RECORD, "The feature guidance registry is unavailable.", reference=f"feature-guidance-manifest@{FEATURE_GUIDANCE_MANIFEST_VERSION}")
            admitted_topics = tuple(topics) if topics is not None else ImmutablePlatformHelpCorpus().topics
            self._registry = FeatureGuidanceRegistry(records, mappings, admitted_topics, PLATFORM_HELP_SOURCE_FINGERPRINTS)
        except GuidanceError:
            raise
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
            raise GuidanceError(GuidanceErrorCode.INVALID_RECORD, "The feature guidance registry is unavailable.", reference="feature-guidance-registry") from error

    @property
    def records(self) -> tuple[FeatureGuidanceRecord, ...]:
        return self._registry.records

    @property
    def mappings(self) -> tuple[FeatureGuidanceMapping, ...]:
        return self._registry.mappings

    @property
    def digest(self) -> str:
        return self._registry.digest

    def resolve(self, surface_key: str, condition_key: str, mapping_version: str) -> FeatureGuidanceRecord:
        return self._registry.resolve(surface_key, condition_key, mapping_version)


__all__ = [
    "FEATURE_GUIDANCE_MANIFEST_VERSION",
    "ImmutableFeatureGuidanceRegistry",
    "REQUIRED_FEATURE_GUIDANCE_IDENTITIES",
    "REQUIRED_FEATURE_MAPPING_IDENTITIES",
    "default_feature_guidance_registry_dir",
]
