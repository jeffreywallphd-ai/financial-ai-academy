"""Checked-in immutable JSON corpus adapter for platform help."""

from __future__ import annotations

import json
from pathlib import Path
from types import MappingProxyType
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


PLATFORM_HELP_MANIFEST_VERSION = "1.0.0"
REQUIRED_PLATFORM_HELP_IDENTITIES = frozenset(
    {
        ("approved-help", "1.0.0"),
        ("data-meaning", "1.0.0"),
        ("education-not-advice", "1.0.0"),
        ("how-ai-help-is-controlled", "1.0.0"),
        ("platform-methods", "1.0.0"),
        ("project-artifact-use", "1.0.0"),
        ("safe-recovery", "1.0.0"),
        ("source-and-history", "1.0.0"),
    }
)
PLATFORM_HELP_SOURCE_FINGERPRINTS = MappingProxyType(
    {
        "ai-ml-boundaries": (
            "c3f521c4d9a156cdd80651609cfa105e6134f2a7800480deefcaecb2d544b775"
        ),
        "architecture-principles": (
            "7ed7fc91381b48fb6b63c66b7f0caf24799fbe46cad8cd0762268ebb58f371ea"
        ),
        "contract-architecture": (
            "510a5f1d83a2e8963ade6ef91b6e68eae56f25eb0e532277fc49f07d4a88efd3"
        ),
        "education-advice-boundary": (
            "917c157fc1da47a686a609fd72e5d36d297c9b99254724e8adf8081a14ad33d6"
        ),
        "financial-method-architecture": (
            "24aca8e940ceb2d31232d3cf27542d5627fe179325eecc75428e384c6812e405"
        ),
        "inert-project-artifacts": (
            "d5c7f26c75f303c565facbe30fbcef9fbac2b62272888fe923b89aa1fe0c6976"
        ),
        "assessment-contract": (
            "50227c013b7a7f41545de266fb59adbe51067defeb42c083839510b9cc09ad4a"
        ),
        "personal-workspace-contract": (
            "61c0167c91cdac53708fdfdd0a97c27822613491ceb8d77021032bb37bba5e10"
        ),
        "product-vision": (
            "e5d82e2a7cdc352248a1dbc4b4636fe97aca978dd2e1a90667cc70cd1d75922b"
        ),
        "user-facing-language": (
            "dbde9accd04fe3f438855290341a2bcd3a00bdd5db109c38e303d0b216aa355a"
        ),
    }
)


def default_platform_help_corpus_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "resources/platform-help/v1"


def _validate_manifest_bindings(topics: tuple[PlatformHelpTopic, ...]) -> None:
    identities = {(topic.topic_id, topic.topic_version) for topic in topics}
    if not REQUIRED_PLATFORM_HELP_IDENTITIES <= identities:
        raise GuidanceError(
            GuidanceErrorCode.INVALID_RECORD,
            "The platform help corpus is unavailable.",
            reference=f"platform-help-manifest@{PLATFORM_HELP_MANIFEST_VERSION}",
        )
    for topic in topics:
        for source in topic.source_references:
            expected = PLATFORM_HELP_SOURCE_FINGERPRINTS.get(source.source_key)
            if expected is None or source.content_fingerprint != expected:
                raise GuidanceError(
                    GuidanceErrorCode.DIGEST_MISMATCH,
                    "Platform help source binding is stale.",
                    reference=source.source_key,
                )


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
            _validate_manifest_bindings(topics)
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
