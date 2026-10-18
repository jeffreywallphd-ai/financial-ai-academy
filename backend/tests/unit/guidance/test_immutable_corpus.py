from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from financial_ai_academy.modules.guidance.adapters import (
    ImmutablePlatformHelpCorpus,
    PLATFORM_HELP_MANIFEST_VERSION,
    PLATFORM_HELP_SOURCE_FINGERPRINTS,
    REQUIRED_PLATFORM_HELP_IDENTITIES,
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
        "data-meaning",
        "education-not-advice",
        "how-ai-help-is-controlled",
        "platform-methods",
        "project-artifact-use",
        "safe-recovery",
        "source-and-history",
    ]
    assert len(corpus.digest) == 64
    assert all(topic.source_references for topic in corpus.topics)
    assert all(
        len(source.content_fingerprint) == 64
        for topic in corpus.topics
        for source in topic.source_references
    )
    assert corpus.get("approved-help", "1.0.0").title == "Approved help"
    safe_recovery = corpus.get("safe-recovery", "1.0.0")
    assert {source.source_key for source in safe_recovery.source_references} == {
        "assessment-contract",
        "user-facing-language",
    }
    assert all(
        source.content_fingerprint
        == PLATFORM_HELP_SOURCE_FINGERPRINTS[source.source_key]
        for source in safe_recovery.source_references
    )
    assert PLATFORM_HELP_MANIFEST_VERSION == "1.0.0"
    assert REQUIRED_PLATFORM_HELP_IDENTITIES <= {
        (topic.topic_id, topic.topic_version) for topic in corpus.topics
    }


def test_source_manifest_matches_current_canonical_sources() -> None:
    repository_root = Path(__file__).resolve().parents[4]
    sources = {
        "ai-ml-boundaries": "docs/architecture/ai-ml/ai-ml-system-boundaries.md",
        "architecture-principles": "docs/architecture/system/architecture-principles.md",
        "contract-architecture": "docs/architecture/contracts/contract-architecture.md",
        "education-advice-boundary": (
            "docs/risk-compliance/education-versus-financial-advice.md"
        ),
        "financial-method-architecture": (
            "docs/architecture/finance/financial-method-and-simulation-architecture.md"
        ),
        "inert-project-artifacts": "docs/adr/ADR-0011-inert-applied-project-artifacts.md",
        "assessment-contract": "docs/architecture/contracts/assessment-contract.md",
        "personal-workspace-contract": (
            "docs/architecture/contracts/personal-workspace-contract.md"
        ),
        "product-vision": "docs/product/product-vision-and-scope.md",
        "user-facing-language": "docs/standards/user-facing-language-standards.md",
    }

    assert set(sources) == set(PLATFORM_HELP_SOURCE_FINGERPRINTS)
    for source_key, relative_path in sources.items():
        assert (
            hashlib.sha256((repository_root / relative_path).read_bytes()).hexdigest()
            == PLATFORM_HELP_SOURCE_FINGERPRINTS[source_key]
        )


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

    assert len(corpus.topics) == 9
    assert [item.topic_id for item in page.results] == sorted(
        item.topic_id for item in page.results
    )
    assert corpus.get("additional-method", "1.0.0").topic_digest == _digest(value)


@pytest.mark.parametrize("failure", ["malformed", "duplicate"])
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
    with pytest.raises(GuidanceError) as captured:
        ImmutablePlatformHelpCorpus(root)

    assert captured.value.code in {
        GuidanceErrorCode.INVALID_RECORD,
        GuidanceErrorCode.DUPLICATE_IDENTITY,
    }
    assert str(root) not in captured.value.message
    assert str(root) not in captured.value.reference


@pytest.mark.parametrize(
    "filename",
    [
        "approved-help.json",
        "data-meaning.json",
        "education-not-advice.json",
        "how-ai-help-is-controlled.json",
        "platform-methods.json",
        "project-artifact-use.json",
        "safe-recovery.json",
        "source-and-history.json",
    ],
)
def test_each_required_starter_topic_is_bound_by_the_versioned_manifest(
    tmp_path: Path,
    filename: str,
) -> None:
    root = tmp_path / "private-corpus-location"
    _copy_corpus(root)
    (root / filename).unlink()

    with pytest.raises(GuidanceError) as captured:
        ImmutablePlatformHelpCorpus(root)

    assert captured.value.code is GuidanceErrorCode.INVALID_RECORD
    assert captured.value.reference == "platform-help-manifest@1.0.0"
    assert str(root) not in captured.value.message
    assert str(root) not in captured.value.reference


def test_stale_source_fingerprint_fails_closed_without_path_disclosure(
    tmp_path: Path,
) -> None:
    root = tmp_path / "private-corpus-location"
    _copy_corpus(root)
    topic_path = root / "approved-help.json"
    value = json.loads(topic_path.read_text(encoding="utf-8"))
    value["source_references"][0]["content_fingerprint"] = "0" * 64
    value["topic_digest"] = _digest(value)
    topic_path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(GuidanceError) as captured:
        ImmutablePlatformHelpCorpus(root)

    assert captured.value.code is GuidanceErrorCode.DIGEST_MISMATCH
    assert captured.value.reference == "product-vision"
    assert str(root) not in captured.value.message
    assert str(root) not in captured.value.reference
