from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from financial_ai_academy.modules.guidance.adapters import (
    ImmutablePlatformHelpCorpus,
    default_platform_help_corpus_dir,
)
from financial_ai_academy.modules.guidance.domain import (
    GuidanceError,
    GuidanceErrorCode,
    SearchRequest,
)


def _digest(value: dict[str, object]) -> str:
    payload = {key: item for key, item in value.items() if key != "topic_digest"}
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _copy_corpus(target: Path) -> None:
    target.mkdir()
    for source in default_platform_help_corpus_dir().glob("*.json"):
        shutil.copy2(source, target / source.name)


def test_default_corpus_is_atomically_admitted_with_stable_provenance() -> None:
    corpus = ImmutablePlatformHelpCorpus()

    assert [topic.topic_id for topic in corpus.topics] == [
        "approved-help",
        "education-not-advice",
        "how-ai-help-is-controlled",
        "platform-methods",
    ]
    assert len(corpus.digest) == 64
    assert all(topic.source_references for topic in corpus.topics)
    assert all(
        len(source.content_fingerprint) == 64
        for topic in corpus.topics
        for source in topic.source_references
    )
    assert corpus.get("approved-help", "1.0.0").title == "Approved help"


def test_valid_additional_topic_and_filename_order_do_not_freeze_corpus_size(
    tmp_path: Path,
) -> None:
    root = tmp_path / "corpus"
    _copy_corpus(root)
    value = json.loads((root / "platform-methods.json").read_text(encoding="utf-8"))
    value.update(
        topic_id="additional-method",
        title="An additional reviewed method",
        summary=(
            "This additional reviewed method proves that the immutable corpus "
            "can grow without changing its admission rules."
        ),
        related_topics=[],
    )
    value["topic_digest"] = _digest(value)
    (root / "00-additional.json").write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    corpus = ImmutablePlatformHelpCorpus(root)
    page = corpus.search(SearchRequest(page_size=50))

    assert len(corpus.topics) == 5
    assert [item.topic_id for item in page.results] == sorted(
        item.topic_id for item in page.results
    )
    assert corpus.get("additional-method", "1.0.0").topic_digest == _digest(value)


@pytest.mark.parametrize("failure", ["malformed", "duplicate", "missing"])
def test_startup_failure_is_bounded_and_never_admits_a_partial_corpus(
    tmp_path: Path,
    failure: str,
) -> None:
    root = tmp_path / "private-corpus-location"
    _copy_corpus(root)
    if failure == "malformed":
        (root / "broken.json").write_text("{", encoding="utf-8")
    elif failure == "duplicate":
        shutil.copy2(root / "approved-help.json", root / "duplicate.json")
    else:
        (root / "approved-help.json").unlink()
        (root / "education-not-advice.json").unlink()

    with pytest.raises(GuidanceError) as captured:
        ImmutablePlatformHelpCorpus(root)

    assert captured.value.code in {
        GuidanceErrorCode.INVALID_RECORD,
        GuidanceErrorCode.DUPLICATE_IDENTITY,
        GuidanceErrorCode.DANGLING_REFERENCE,
    }
    assert str(root) not in captured.value.message
    assert str(root) not in captured.value.reference
