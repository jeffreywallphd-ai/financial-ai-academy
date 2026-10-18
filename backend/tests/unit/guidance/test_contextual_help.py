from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from financial_ai_academy.modules.guidance.adapters import (
    CONTEXTUAL_HELP_MANIFEST_VERSION,
    ImmutableContextualHelpRegistry,
    ImmutablePlatformHelpCorpus,
    REQUIRED_CONTEXTUAL_HELP_IDENTITIES,
    context_from_mapping,
    default_contextual_help_registry_dir,
)
from financial_ai_academy.modules.guidance.domain import (
    ContextualHelpRegistry,
    GuidanceError,
    GuidanceErrorCode,
    context_digest,
    context_payload,
)


APPROVED = (
    Path(__file__).resolve().parents[4]
    / "contracts/compatibility/contextual-help/v1/approved/context.json"
)


def _value() -> dict[str, object]:
    return json.loads(APPROVED.read_text(encoding="utf-8"))


def _digest(value: dict[str, object]) -> str:
    payload = {key: item for key, item in value.items() if key != "context_digest"}
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _copy_registry(target: Path) -> None:
    target.mkdir()
    for source in default_contextual_help_registry_dir().glob("*.json"):
        shutil.copy2(source, target / source.name)


def test_contract_mapping_round_trips_exact_context_and_digest() -> None:
    value = _value()
    context = context_from_mapping(value)
    assert context_payload(context) == value
    assert context_digest(context) == value["context_digest"]
    assert [item.purpose.value for item in context.help_references] == [
        "data_meaning",
        "source",
        "method",
        "education_boundary",
    ]


def test_default_registry_is_source_bound_and_exact() -> None:
    registry = ImmutableContextualHelpRegistry()
    assert [record.context_key for record in registry.records] == [
        "ai-assistance",
        "lesson-publication",
        "practice-result",
        "project-result",
    ]
    assert len(registry.digest) == 64
    assert registry.get("project-result", "1.0.0").context_digest == _value()[
        "context_digest"
    ]
    assert CONTEXTUAL_HELP_MANIFEST_VERSION == "1.0.0"
    assert REQUIRED_CONTEXTUAL_HELP_IDENTITIES <= {
        (record.context_key, record.context_version) for record in registry.records
    }


def test_registry_never_substitutes_a_different_version() -> None:
    registry = ImmutableContextualHelpRegistry()
    with pytest.raises(GuidanceError) as captured:
        registry.get("project-result", "2.0.0")
    assert captured.value.code is GuidanceErrorCode.NOT_FOUND
    assert "2.0.0" in captured.value.reference


def test_dangling_exact_topic_rejects_complete_registry() -> None:
    context = context_from_mapping(_value())
    topics = tuple(
        topic
        for topic in ImmutablePlatformHelpCorpus().topics
        if topic.topic_id != "data-meaning"
    )
    with pytest.raises(GuidanceError) as captured:
        ContextualHelpRegistry((context,), topics)
    assert captured.value.code is GuidanceErrorCode.DANGLING_REFERENCE


@pytest.mark.parametrize(
    "path, replacement",
    [
        (("feature_label",), "Unsafe\u0000label"),
        (("help_references", 1, "purpose"), "method"),
        (("help_references", 0, "topic_version"), "latest"),
        (("publication", "updated_at"), "2020-01-01T00:00:00Z"),
    ],
)
def test_invalid_or_duplicate_meaning_fails_without_payload_disclosure(
    path: tuple[object, ...],
    replacement: object,
) -> None:
    value = copy.deepcopy(_value())
    target = value
    for part in path[:-1]:
        target = target[part]  # type: ignore[index,assignment]
    target[path[-1]] = replacement  # type: ignore[index]
    if path != ("help_references", 0, "topic_version"):
        value["context_digest"] = _digest(value)
    with pytest.raises(GuidanceError) as captured:
        context_from_mapping(value)
    assert str(replacement) not in captured.value.message


def test_additional_valid_context_and_filename_order_do_not_freeze_registry_size(
    tmp_path: Path,
) -> None:
    root = tmp_path / "registry"
    _copy_registry(root)
    value = _value()
    value.update(
        context_key="additional-project-context",
        feature_label="Additional Project explanation",
    )
    value["context_digest"] = _digest(value)
    (root / "00-additional.json").write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    registry = ImmutableContextualHelpRegistry(root)
    assert len(registry.records) == 5
    assert [item.context_key for item in registry.records] == sorted(
        item.context_key for item in registry.records
    )


@pytest.mark.parametrize("failure", ["malformed", "duplicate", "missing"])
def test_registry_admission_is_atomic_and_diagnostics_hide_private_path(
    tmp_path: Path,
    failure: str,
) -> None:
    root = tmp_path / "private-registry-location"
    _copy_registry(root)
    if failure == "malformed":
        (root / "broken.json").write_text("{", encoding="utf-8")
    elif failure == "duplicate":
        shutil.copy2(root / "project-result.json", root / "duplicate.json")
    else:
        (root / "project-result.json").unlink()
    with pytest.raises(GuidanceError) as captured:
        ImmutableContextualHelpRegistry(root)
    assert captured.value.code in {
        GuidanceErrorCode.INVALID_RECORD,
        GuidanceErrorCode.DUPLICATE_IDENTITY,
    }
    assert str(root) not in captured.value.message
    assert str(root) not in captured.value.reference
