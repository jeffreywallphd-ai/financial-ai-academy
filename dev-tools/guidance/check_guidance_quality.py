#!/usr/bin/env python3
"""Qualify checked-in Guidance sources, exact links, and deterministic search."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Mapping


SOURCE_AUTHORITY_SCHEMA = "source-authority-v1"
REPORT_SCHEMA = "guidance-quality-report-v1"


class QualityFailure(ValueError):
    """Bounded contributor failure that never includes source bytes or paths."""

    def __init__(self, code: str, reference: str) -> None:
        super().__init__(code)
        self.code = code
        self.reference = reference[:120]


def repository_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() and (candidate / "docs").is_dir():
            return candidate
    raise QualityFailure("repository-unavailable", "repository")


def _load_runtime(root: Path) -> tuple[object, ...]:
    source_root = root / "backend" / "src"
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))
    from financial_ai_academy.modules.guidance.adapters import (  # noqa: PLC0415
        CONTEXTUAL_HELP_MANIFEST_VERSION,
        FEATURE_GUIDANCE_MANIFEST_VERSION,
        ImmutableContextualHelpRegistry,
        ImmutableFeatureGuidanceRegistry,
        ImmutablePlatformHelpCorpus,
        PLATFORM_HELP_MANIFEST_VERSION,
        PLATFORM_HELP_SOURCE_FINGERPRINTS,
    )
    from financial_ai_academy.modules.guidance.domain import (  # noqa: PLC0415
        GuidanceError,
        SearchRequest,
        TopicKind,
    )

    return (
        CONTEXTUAL_HELP_MANIFEST_VERSION,
        FEATURE_GUIDANCE_MANIFEST_VERSION,
        ImmutableContextualHelpRegistry,
        ImmutableFeatureGuidanceRegistry,
        ImmutablePlatformHelpCorpus,
        PLATFORM_HELP_MANIFEST_VERSION,
        PLATFORM_HELP_SOURCE_FINGERPRINTS,
        GuidanceError,
        SearchRequest,
        TopicKind,
    )


def validate_source_authority(
    root: Path,
    manifest_path: Path,
    expected_fingerprints: Mapping[str, str],
) -> dict[str, str]:
    try:
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise QualityFailure("source-authority-invalid", "manifest") from error
    if (
        not isinstance(value, dict)
        or set(value) != {"schema_version", "sources"}
        or value.get("schema_version") != SOURCE_AUTHORITY_SCHEMA
        or not isinstance(value.get("sources"), dict)
    ):
        raise QualityFailure("source-authority-invalid", "manifest")

    raw_sources = value["sources"]
    if set(raw_sources) != set(expected_fingerprints):
        raise QualityFailure("source-authority-keys", "manifest")

    resolved_root = root.resolve()
    sources: dict[str, str] = {}
    seen_paths: set[str] = set()
    for source_key in sorted(expected_fingerprints):
        relative = raw_sources.get(source_key)
        if not isinstance(relative, str):
            raise QualityFailure("source-authority-path", source_key)
        normalized = Path(relative.replace("\\", "/"))
        if (
            normalized.is_absolute()
            or ".." in normalized.parts
            or normalized.suffix.lower() != ".md"
            or normalized.as_posix() in seen_paths
        ):
            raise QualityFailure("source-authority-path", source_key)
        target = (resolved_root / normalized).resolve()
        if not target.is_relative_to(resolved_root) or not target.is_file():
            raise QualityFailure("source-authority-path", source_key)
        seen_paths.add(normalized.as_posix())
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected_fingerprints[source_key]:
            raise QualityFailure("source-binding-stale", source_key)
        sources[source_key] = normalized.as_posix()
    return sources


def traverse_search(corpus: object, SearchRequest: type, TopicKind: type) -> tuple[tuple[str, str], ...]:
    def traverse(*, page_size: int, topic_kind: object | None = None) -> tuple[tuple[str, str], ...]:
        cursor: str | None = None
        identities: list[tuple[str, str]] = []
        while True:
            page = corpus.search(  # type: ignore[attr-defined]
                SearchRequest(page_size=page_size, cursor=cursor, topic_kind=topic_kind)
            )
            identities.extend((item.topic_id, item.topic_version) for item in page.results)
            if page.next_cursor is None:
                break
            cursor = page.next_cursor
        if len(identities) != len(set(identities)):
            raise QualityFailure("search-duplicate", "platform-help")
        return tuple(identities)

    one_at_a_time = traverse(page_size=1)
    three_at_a_time = traverse(page_size=3)
    if one_at_a_time != three_at_a_time:
        raise QualityFailure("search-order", "platform-help")
    for topic_kind in TopicKind:
        filtered = traverse(page_size=2, topic_kind=topic_kind)
        expected = tuple(
            identity
            for identity in one_at_a_time
            if corpus.get(*identity).topic_kind is topic_kind  # type: ignore[attr-defined]
        )
        if filtered != expected:
            raise QualityFailure("search-filter", topic_kind.value)
    return one_at_a_time


def qualify(
    root: Path,
    *,
    authority_path: Path | None = None,
    corpus_dir: Path | None = None,
    context_dir: Path | None = None,
    feature_dir: Path | None = None,
) -> dict[str, object]:
    (
        contextual_manifest_version,
        feature_manifest_version,
        ImmutableContextualHelpRegistry,
        ImmutableFeatureGuidanceRegistry,
        ImmutablePlatformHelpCorpus,
        platform_manifest_version,
        expected_fingerprints,
        GuidanceError,
        SearchRequest,
        TopicKind,
    ) = _load_runtime(root)
    manifest = authority_path or root / "dev-tools/guidance/source_authority.json"
    sources = validate_source_authority(root, manifest, expected_fingerprints)
    try:
        corpus = ImmutablePlatformHelpCorpus(corpus_dir)
        contexts = ImmutableContextualHelpRegistry(context_dir, corpus.topics)
        features = ImmutableFeatureGuidanceRegistry(feature_dir, corpus.topics)
        identities = traverse_search(corpus, SearchRequest, TopicKind)
        if identities != tuple(
            (topic.topic_id, topic.topic_version)
            for topic in sorted(
                corpus.topics,
                key=lambda item: (
                    item.topic_id,
                    tuple(int(part) for part in item.topic_version.split(".")),
                ),
            )
        ):
            raise QualityFailure("search-coverage", "platform-help")
        for topic_id, topic_version in identities:
            corpus.get(topic_id, topic_version)
        for record in contexts.records:
            contexts.get(record.context_key, record.context_version)
        for mapping in features.mappings:
            features.resolve_with_mapping(
                mapping.surface_key,
                mapping.condition_key,
                mapping.mapping_version,
            )
    except GuidanceError as error:
        raise QualityFailure(f"guidance-{error.code.value}", error.reference) from error

    return {
        "schema_version": REPORT_SCHEMA,
        "status": "qualified",
        "source_authority_schema": SOURCE_AUTHORITY_SCHEMA,
        "source_count": len(sources),
        "platform_help": {
            "manifest_version": platform_manifest_version,
            "topic_count": len(corpus.topics),
            "digest": corpus.digest,
        },
        "contextual_help": {
            "manifest_version": contextual_manifest_version,
            "context_count": len(contexts.records),
            "digest": contexts.digest,
        },
        "feature_guidance": {
            "manifest_version": feature_manifest_version,
            "record_count": len(features.records),
            "mapping_count": len(features.mappings),
            "digest": features.digest,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="repository root; defaults to discovery from this file")
    parser.add_argument("--json", action="store_true", help="emit the stable JSON report")
    args = parser.parse_args()
    try:
        root = Path(args.root).resolve() if args.root else repository_root()
        report = qualify(root)
    except QualityFailure as error:
        if args.json:
            print(json.dumps({
                "schema_version": REPORT_SCHEMA,
                "status": "failed",
                "code": error.code,
                "reference": error.reference,
            }, indent=2, sort_keys=True))
        else:
            print(f"Guidance quality failed: {error.code} ({error.reference})", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "Guidance quality passed: "
            f"{report['source_count']} sources, "
            f"{report['platform_help']['topic_count']} topics, "  # type: ignore[index]
            f"{report['contextual_help']['context_count']} contexts, "  # type: ignore[index]
            f"{report['feature_guidance']['mapping_count']} feature mappings"  # type: ignore[index]
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
