from __future__ import annotations

import copy
import hashlib
import json

import pytest

from financial_ai_academy.modules.guidance.domain import (
    feature_guidance_payload,
    feature_mapping_payload,
)

from .runner import (
    ConformanceFailure,
    FeatureGuidanceContractValidator,
    approved,
    default_corpus_dir,
    load_json,
)


def _digest(value: dict[str, object], field: str) -> str:
    return hashlib.sha256(json.dumps(
        {key: item for key, item in value.items() if key != field},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def test_approved_record_and_mapping_round_trip_exactly() -> None:
    record_value, mapping_value = approved()
    validator = FeatureGuidanceContractValidator()
    assert feature_guidance_payload(validator.validate_record(record_value)) == record_value
    assert feature_mapping_payload(validator.validate_mapping(mapping_value)) == mapping_value


def test_every_declared_denial_case_fails_closed() -> None:
    record_value, mapping_value = approved()
    cases = load_json(default_corpus_dir() / "cases/denials.json")["cases"]
    validator = FeatureGuidanceContractValidator()
    for case in cases:
        artifact = copy.deepcopy(record_value if case["artifact"] == "record" else mapping_value)
        mutation = case["mutation"]
        if mutation == "unknown_field":
            artifact["unexpected"] = "private"
        elif mutation == "private_field":
            artifact["route"] = "/private/path"
        elif mutation == "arbitrary_destination":
            artifact["actions"][0]["url"] = "https://example.invalid"
        elif mutation == "command_text":
            artifact["reason"] = "Run powershell Get-Secret"
            artifact["guidance_digest"] = _digest(artifact, "guidance_digest")
        elif mutation == "guarantee_text":
            artifact["outcome"] = "Recovery is guaranteed."
            artifact["guidance_digest"] = _digest(artifact, "guidance_digest")
        elif mutation == "invalid_chronology":
            artifact["publication"]["reviewed_on"] = "2026-10-19"
            artifact["guidance_digest"] = _digest(artifact, "guidance_digest")
        elif mutation == "digest_mismatch":
            artifact["mapping_digest"] = "0" * 64
        else:  # pragma: no cover - fixture expansion must add an explicit mutation
            raise AssertionError(mutation)
        with pytest.raises(ConformanceFailure):
            if case["artifact"] == "record":
                validator.validate_record(artifact)
            else:
                validator.validate_mapping(artifact)


def test_safe_unicode_and_changed_valid_wording_are_not_frozen() -> None:
    record_value, _ = approved()
    record_value["heading"] = "Résumé — 状態"
    record_value["source_references"][0]["title"] = "Python method record"
    record_value["guidance_digest"] = _digest(record_value, "guidance_digest")
    admitted = FeatureGuidanceContractValidator().validate_record(record_value)
    assert admitted.heading == "Résumé — 状態"
    assert admitted.source_references[0].title == "Python method record"
