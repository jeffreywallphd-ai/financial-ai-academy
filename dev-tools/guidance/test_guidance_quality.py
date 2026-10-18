#!/usr/bin/env python3
"""Focused qualification for the contributor-facing Guidance quality gate."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT / "backend" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend" / "src"))

from check_guidance_quality import (  # noqa: E402
    QualityFailure,
    qualify,
    traverse_search,
    validate_source_authority,
)
from financial_ai_academy.modules.guidance.adapters import (  # noqa: E402
    ImmutablePlatformHelpCorpus,
    PLATFORM_HELP_SOURCE_FINGERPRINTS,
)
from financial_ai_academy.modules.guidance.domain import (  # noqa: E402
    PlatformHelpCorpus,
    SearchRequest,
    TopicKind,
    topic_digest,
)


class GuidanceQualityTests(unittest.TestCase):
    def test_current_repository_qualifies_with_privacy_minimized_summary(self) -> None:
        report = qualify(ROOT)
        self.assertEqual("qualified", report["status"])
        self.assertEqual(len(PLATFORM_HELP_SOURCE_FINGERPRINTS), report["source_count"])
        serialized = json.dumps(report, sort_keys=True)
        self.assertNotIn(str(ROOT), serialized)
        self.assertNotIn("docs/", serialized)

    def test_source_authority_accepts_exact_safe_keys_and_current_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "docs").mkdir()
            (root / "docs/source.md").write_text("Current source\n", encoding="utf-8")
            expected = {"source-one": hashlib.sha256((root / "docs/source.md").read_bytes()).hexdigest()}
            manifest = root / "authority.json"
            manifest.write_text(json.dumps({
                "schema_version": "source-authority-v1",
                "sources": {"source-one": "docs/source.md"},
            }), encoding="utf-8")
            self.assertEqual(
                {"source-one": "docs/source.md"},
                validate_source_authority(root, manifest, expected),
            )

    def test_source_authority_fails_closed_for_stale_or_malformed_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "docs").mkdir()
            (root / "docs/one.md").write_text("one", encoding="utf-8")
            (root / "docs/two.md").write_text("two", encoding="utf-8")
            expected = {
                "source-one": hashlib.sha256(b"expected one").hexdigest(),
                "source-two": hashlib.sha256(b"two").hexdigest(),
            }
            cases = {
                "malformed": "{",
                "missing-key": json.dumps({"schema_version": "source-authority-v1", "sources": {"source-one": "docs/one.md"}}),
                "unknown-key": json.dumps({"schema_version": "source-authority-v1", "sources": {"source-one": "docs/one.md", "source-two": "docs/two.md", "source-three": "docs/two.md"}}),
                "absolute": json.dumps({"schema_version": "source-authority-v1", "sources": {"source-one": str((root / "docs/one.md").resolve()), "source-two": "docs/two.md"}}),
                "escape": json.dumps({"schema_version": "source-authority-v1", "sources": {"source-one": "../outside.md", "source-two": "docs/two.md"}}),
                "duplicate": json.dumps({"schema_version": "source-authority-v1", "sources": {"source-one": "docs/two.md", "source-two": "docs/two.md"}}),
                "missing-file": json.dumps({"schema_version": "source-authority-v1", "sources": {"source-one": "docs/missing.md", "source-two": "docs/two.md"}}),
                "stale": json.dumps({"schema_version": "source-authority-v1", "sources": {"source-one": "docs/one.md", "source-two": "docs/two.md"}}),
            }
            for name, payload in cases.items():
                with self.subTest(name=name):
                    manifest = root / f"{name}.json"
                    manifest.write_text(payload, encoding="utf-8")
                    with self.assertRaises(QualityFailure):
                        validate_source_authority(root, manifest, expected)

    def test_search_traversal_accepts_reordered_and_extended_valid_corpus(self) -> None:
        current = ImmutablePlatformHelpCorpus().topics
        seed = current[0]
        additional = replace(
            seed,
            topic_id="additional-quality-topic",
            title="Additional quality topic",
            summary="An additional reviewed topic proves that search qualification does not freeze corpus size.",
            keywords=("additional", "quality"),
            related_topics=(),
            topic_digest="0" * 64,
        )
        additional = replace(additional, topic_digest=topic_digest(additional))
        corpus = PlatformHelpCorpus((*reversed(current), additional))
        traversed = traverse_search(corpus, SearchRequest, TopicKind)
        self.assertEqual(len(current) + 1, len(traversed))
        self.assertIn(("additional-quality-topic", seed.topic_version), traversed)

    def test_broken_exact_graph_fails_before_a_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus_dir = Path(temporary) / "platform-help"
            source_dir = ROOT / "backend/src/financial_ai_academy/modules/guidance/resources/platform-help/v1"
            shutil.copytree(source_dir, corpus_dir)
            target = corpus_dir / "approved-help.json"
            value = json.loads(target.read_text(encoding="utf-8"))
            value["related_topics"] = [{
                "topic_id": "missing-topic",
                "topic_version": "1.0.0",
                "relationship": "see_also",
            }]
            payload = {key: item for key, item in value.items() if key != "topic_digest"}
            value["topic_digest"] = hashlib.sha256(json.dumps(
                payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")).hexdigest()
            target.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(QualityFailure, "guidance-dangling_reference"):
                qualify(ROOT, corpus_dir=corpus_dir)


if __name__ == "__main__":
    unittest.main(verbosity=2)
