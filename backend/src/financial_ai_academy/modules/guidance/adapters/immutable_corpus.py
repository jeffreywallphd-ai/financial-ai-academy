"""Checked-in immutable JSON corpus adapter for platform help."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..domain import (
    GuidanceError,
    GuidanceErrorCode,
    PlatformHelpCorpus,
    PlatformHelpTopic,
    SearchPage,
    SearchRequest,
)
from .platform_help_contract import topic_from_mapping


def default_platform_help_corpus_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "resources/platform-help/v1"


class ImmutablePlatformHelpCorpus:
    """Load and atomically admit a finite versioned JSON corpus at startup."""

    def __init__(self, corpus_dir: Path | None = None) -> None:
        root = (corpus_dir or default_platform_help_corpus_dir()).resolve()
        try:
            files = sorted(root.glob("*.json"), key=lambda path: path.name)
            if not root.is_dir() or not files:
                raise OSError("corpus unavailable")
            mappings: list[dict[str, Any]] = []
            for path in files:
                value = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(value, dict):
                    raise ValueError("topic must be an object")
                mappings.append(value)
            topics = tuple(topic_from_mapping(value) for value in mappings)
            self._corpus = PlatformHelpCorpus(topics)
        except GuidanceError:
            raise
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
            raise GuidanceError(
                GuidanceErrorCode.INVALID_RECORD,
                "The platform help corpus is unavailable.",
                reference="platform-help-corpus",
            ) from error

    @property
    def topics(self) -> tuple[PlatformHelpTopic, ...]:
        return self._corpus.topics

    @property
    def digest(self) -> str:
        return self._corpus.digest

    def get(self, topic_id: str, topic_version: str) -> PlatformHelpTopic:
        return self._corpus.get(topic_id, topic_version)

    def search(self, request: SearchRequest) -> SearchPage:
        return self._corpus.search(request)
