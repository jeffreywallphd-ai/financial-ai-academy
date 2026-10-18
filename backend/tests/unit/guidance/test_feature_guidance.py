from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from financial_ai_academy.modules.guidance.adapters import (
    FEATURE_GUIDANCE_MANIFEST_VERSION,
    ImmutableFeatureGuidanceRegistry,
    ImmutablePlatformHelpCorpus,
    REQUIRED_FEATURE_GUIDANCE_IDENTITIES,
    REQUIRED_FEATURE_MAPPING_IDENTITIES,
    default_feature_guidance_registry_dir,
    feature_guidance_from_mapping,
)
from financial_ai_academy.modules.guidance.domain import (
    FeatureGuidanceActionKind,
    FeatureGuidanceRegistry,
    GuidanceError,
    GuidanceErrorCode,
    feature_guidance_resolution_payload,
    feature_guidance_payload,
)


def _digest(value: dict[str, object], field: str) -> str:
    return hashlib.sha256(json.dumps(
        {key: item for key, item in value.items() if key != field},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def _copy_registry(target: Path) -> None:
    shutil.copytree(default_feature_guidance_registry_dir(), target)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_default_registry_admits_all_starter_conditions_exactly() -> None:
    registry = ImmutableFeatureGuidanceRegistry()
    assert FEATURE_GUIDANCE_MANIFEST_VERSION == "1.0.0"
    assert REQUIRED_FEATURE_GUIDANCE_IDENTITIES <= {
        (item.guidance_id, item.guidance_version) for item in registry.records
    }
    assert REQUIRED_FEATURE_MAPPING_IDENTITIES <= {
        (item.surface_key, item.condition_key, item.mapping_version)
        for item in registry.mappings
    }
    assert len(registry.digest) == 64
    record = registry.resolve("project-workspace", "artifact-inert", "1.0.0")
    assert record.guidance_id == "project-artifact-inert"
    assert [item.action_kind for item in record.actions] == [
        FeatureGuidanceActionKind.DOWNLOAD_INERT_ARTIFACT,
        FeatureGuidanceActionKind.OPEN_HELP_TOPIC,
    ]
    resolution = registry.resolve_with_mapping(
        "project-workspace",
        "artifact-inert",
        "1.0.0",
    )
    payload = feature_guidance_resolution_payload(resolution)
    assert payload["mapping"]["mapping_digest"] == resolution.mapping.mapping_digest
    assert payload["guidance"]["guidance_digest"] == record.guidance_digest


def test_exact_lookup_never_substitutes_a_version_or_condition() -> None:
    registry = ImmutableFeatureGuidanceRegistry()
    for condition, version in [("artifact-missing", "1.0.0"), ("artifact-inert", "2.0.0")]:
        with pytest.raises(GuidanceError) as captured:
            registry.resolve("project-workspace", condition, version)
        assert captured.value.code is GuidanceErrorCode.NOT_FOUND


def test_record_round_trip_preserves_canonical_payload() -> None:
    path = default_feature_guidance_registry_dir() / "records/project-artifact-inert.json"
    value = _load(path)
    assert feature_guidance_payload(feature_guidance_from_mapping(value)) == value


def test_registry_rejects_missing_exact_help_topic() -> None:
    topics = tuple(
        item
        for item in ImmutablePlatformHelpCorpus().topics
        if item.topic_id != "project-artifact-use"
    )
    with pytest.raises(GuidanceError) as captured:
        ImmutableFeatureGuidanceRegistry(topics=topics)
    assert captured.value.code is GuidanceErrorCode.DANGLING_REFERENCE


def test_explicit_empty_help_corpus_never_falls_back_to_defaults() -> None:
    with pytest.raises(GuidanceError) as captured:
        ImmutableFeatureGuidanceRegistry(topics=())
    assert captured.value.code is GuidanceErrorCode.DANGLING_REFERENCE


@pytest.mark.parametrize("failure", ["malformed", "missing", "duplicate"])
def test_complete_registry_failure_is_atomic_and_hides_private_path(
    tmp_path: Path,
    failure: str,
) -> None:
    root = tmp_path / "private-feature-guidance"
    _copy_registry(root)
    if failure == "malformed":
        (root / "records/broken.json").write_text("{", encoding="utf-8")
    elif failure == "missing":
        (root / "records/project-artifact-inert.json").unlink()
    else:
        shutil.copy2(
            root / "mappings/project-workspace-artifact-inert.json",
            root / "mappings/duplicate.json",
        )
    with pytest.raises(GuidanceError) as captured:
        ImmutableFeatureGuidanceRegistry(root)
    assert captured.value.code in {
        GuidanceErrorCode.INVALID_RECORD,
        GuidanceErrorCode.DUPLICATE_IDENTITY,
        GuidanceErrorCode.DANGLING_REFERENCE,
    }
    assert str(root) not in captured.value.message
    assert str(root) not in captured.value.reference


def test_stale_source_binding_fails_after_valid_canonical_digest(tmp_path: Path) -> None:
    root = tmp_path / "registry"
    _copy_registry(root)
    path = root / "records/project-artifact-inert.json"
    value = _load(path)
    value["source_references"][0]["content_fingerprint"] = "0" * 64
    value["guidance_digest"] = _digest(value, "guidance_digest")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(GuidanceError) as captured:
        ImmutableFeatureGuidanceRegistry(root)
    assert captured.value.code is GuidanceErrorCode.DIGEST_MISMATCH
    assert captured.value.reference == "inert-project-artifacts"


def test_valid_added_record_and_mapping_do_not_freeze_registry_size(tmp_path: Path) -> None:
    root = tmp_path / "registry"
    _copy_registry(root)
    record_path = root / "records/project-artifact-inert.json"
    record = _load(record_path)
    record.update(guidance_id="additional-inert-guidance", heading="Additional inert guidance")
    record["guidance_digest"] = _digest(record, "guidance_digest")
    (root / "records/00-additional.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    mapping_path = root / "mappings/project-workspace-artifact-inert.json"
    mapping = _load(mapping_path)
    mapping.update(
        surface_key="additional-surface",
        condition_key="additional-condition",
        guidance_id="additional-inert-guidance",
    )
    mapping["mapping_digest"] = _digest(mapping, "mapping_digest")
    (root / "mappings/00-additional.json").write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    registry = ImmutableFeatureGuidanceRegistry(root)
    assert len(registry.records) == 6
    assert len(registry.mappings) == 6
    assert registry.resolve("additional-surface", "additional-condition", "1.0.0").guidance_id == "additional-inert-guidance"


def test_public_registry_has_no_runtime_feature_or_execution_authority() -> None:
    fields = set(FeatureGuidanceRegistry.__dict__)
    assert not fields.intersection({"save", "submit", "execute", "repair", "authorize"})
