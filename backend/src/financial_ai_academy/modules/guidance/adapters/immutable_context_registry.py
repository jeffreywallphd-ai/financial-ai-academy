"""Checked-in immutable contextual-help registry adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

from ..domain import (
    ContextualHelpRecord,
    ContextualHelpRegistry,
    GuidanceError,
    GuidanceErrorCode,
    PlatformHelpTopic,
)
from .contextual_help_contract import context_from_mapping
from .immutable_corpus import (
    ImmutablePlatformHelpCorpus,
    PLATFORM_HELP_SOURCE_FINGERPRINTS,
)


CONTEXTUAL_HELP_MANIFEST_VERSION = "1.0.0"
REQUIRED_CONTEXTUAL_HELP_IDENTITIES = frozenset(
    {
        ("ai-assistance", "1.0.0"),
        ("lesson-publication", "1.0.0"),
        ("practice-result", "1.0.0"),
        ("project-result", "1.0.0"),
    }
)


def default_contextual_help_registry_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "resources/contextual-help/v1"


def _validate_manifest(records: tuple[ContextualHelpRecord, ...]) -> None:
    identities = {(record.context_key, record.context_version) for record in records}
    if not REQUIRED_CONTEXTUAL_HELP_IDENTITIES <= identities:
        raise GuidanceError(
            GuidanceErrorCode.INVALID_RECORD,
            "The contextual help registry is unavailable.",
            reference=f"contextual-help-manifest@{CONTEXTUAL_HELP_MANIFEST_VERSION}",
        )
    for record in records:
        for source in record.source_references:
            expected = PLATFORM_HELP_SOURCE_FINGERPRINTS.get(source.source_key)
            if expected is None or source.content_fingerprint != expected:
                raise GuidanceError(
                    GuidanceErrorCode.DIGEST_MISMATCH,
                    "Contextual help source binding is stale.",
                    reference=source.source_key,
                )


class ImmutableContextualHelpRegistry:
    """Load and atomically admit finite exact contexts at startup."""

    def __init__(
        self,
        registry_dir: Path | None = None,
        topics: Sequence[PlatformHelpTopic] | None = None,
    ) -> None:
        root = (registry_dir or default_contextual_help_registry_dir()).resolve()
        try:
            files = sorted(root.glob("*.json"), key=lambda path: path.name)
            if not root.is_dir() or not files:
                raise OSError("registry unavailable")
            mappings: list[dict[str, Any]] = []
            for path in files:
                value = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(value, dict):
                    raise ValueError("context must be an object")
                mappings.append(value)
            records = tuple(context_from_mapping(value) for value in mappings)
            _validate_manifest(records)
            admitted_topics = (
                tuple(topics)
                if topics is not None
                else ImmutablePlatformHelpCorpus().topics
            )
            self._registry = ContextualHelpRegistry(records, admitted_topics)
        except GuidanceError:
            raise
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
            raise GuidanceError(
                GuidanceErrorCode.INVALID_RECORD,
                "The contextual help registry is unavailable.",
                reference="contextual-help-registry",
            ) from error

    @property
    def records(self) -> tuple[ContextualHelpRecord, ...]:
        return self._registry.records

    @property
    def digest(self) -> str:
        return self._registry.digest

    def get(self, context_key: str, context_version: str) -> ContextualHelpRecord:
        return self._registry.get(context_key, context_version)


__all__ = [
    "CONTEXTUAL_HELP_MANIFEST_VERSION",
    "ImmutableContextualHelpRegistry",
    "REQUIRED_CONTEXTUAL_HELP_IDENTITIES",
    "default_contextual_help_registry_dir",
]
