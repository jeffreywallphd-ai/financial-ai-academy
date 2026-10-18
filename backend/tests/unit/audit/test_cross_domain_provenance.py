from __future__ import annotations

import copy
from dataclasses import replace
from datetime import datetime, tzinfo
import importlib.util
import json
from pathlib import Path
import sys

import pytest

from financial_ai_academy.modules.audit.adapters import (
    cross_domain_envelope_from_mapping,
    cross_domain_envelope_to_mapping,
)
from financial_ai_academy.modules.audit.domain import (
    CrossDomainProducer,
    CrossDomainProfile,
    CrossDomainProvenanceEnvelope,
    CrossDomainResourceReference,
    CrossDomainSource,
    DatasetSnapshotIdentity,
    FinancialAccountIdentity,
    InvalidCrossDomainProvenance,
    MarketObservationIdentity,
    cross_domain_envelope_digest,
    market_observation_resource_id,
    validate_cross_domain_envelope,
)
ROOT = Path(__file__).resolve().parents[4]
APPROVED = ROOT / "contracts/compatibility/provenance/v2/approved"
RUNNER_PATH = ROOT / "backend/tests/contract/provenance_v2/runner.py"
RUNNER_SPEC = importlib.util.spec_from_file_location(
    "cross_domain_contract_runner", RUNNER_PATH
)
assert RUNNER_SPEC is not None and RUNNER_SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(RUNNER_SPEC)
sys.modules[RUNNER_SPEC.name] = RUNNER
RUNNER_SPEC.loader.exec_module(RUNNER)


def _load(name: str) -> dict[str, object]:
    return json.loads((APPROVED / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "profile",
    [
        "administrative_action",
        "dataset_snapshot",
        "financial_result",
        "market_observation",
        "model_execution",
        "model_version",
        "project_snapshot",
        "recommendation_record",
        "simulation_result",
    ],
)
def test_approved_profiles_round_trip_and_match_frozen_canonical_digest(
    profile: str,
) -> None:
    record = RUNNER.approved_records()[profile]
    original = copy.deepcopy(record)
    admitted = cross_domain_envelope_from_mapping(record)
    projected = cross_domain_envelope_to_mapping(admitted)

    assert record == original
    assert projected["resource"]["profile"] == profile  # type: ignore[index]
    assert cross_domain_envelope_from_mapping(projected) == admitted
    assert cross_domain_envelope_digest(admitted) == RUNNER.CrossDomainContractValidator().envelope_digest(record)


def test_financial_result_uses_explicit_analysis_and_account_variants() -> None:
    analysis = cross_domain_envelope_from_mapping(
        _load("financial-result-envelope.json")
    )
    assert analysis.resource.profile is CrossDomainProfile.FINANCIAL_RESULT
    assert analysis.resource.identity.subject_kind == "analysis"  # type: ignore[union-attr]

    account_mapping = _load("financial-result-envelope.json")
    account_mapping["resource"]["resource_id"] = "account-research-été"  # type: ignore[index]
    identity = account_mapping["resource"]["identity"]  # type: ignore[index]
    identity["subject_kind"] = "account"  # type: ignore[index]
    identity["account_id"] = "account-research-été"  # type: ignore[index]
    del identity["analysis_id"]  # type: ignore[index]
    account = cross_domain_envelope_from_mapping(account_mapping)

    assert isinstance(account.resource.identity, FinancialAccountIdentity)
    assert account.resource.resource_id == "account-research-été"

    ambiguous = copy.deepcopy(account_mapping)
    ambiguous["resource"]["identity"]["analysis_id"] = "analysis-other"  # type: ignore[index]
    with pytest.raises(InvalidCrossDomainProvenance):
        cross_domain_envelope_from_mapping(ambiguous)


def test_market_resource_id_is_only_the_normalized_exact_identity_digest() -> None:
    admitted = cross_domain_envelope_from_mapping(
        _load("market-observation-envelope.json")
    )
    identity = admitted.resource.identity
    assert isinstance(identity, MarketObservationIdentity)
    assert admitted.resource.resource_id == market_observation_resource_id(identity)

    changed = replace(admitted, resource=replace(admitted.resource, resource_id="observation-other"))
    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        validate_cross_domain_envelope(changed)
    assert invalid.value.reference == "resource.resource_id"

    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        market_observation_resource_id(  # type: ignore[arg-type]
            DatasetSnapshotIdentity("dataset-a", "1.0.0")
        )
    assert invalid.value.reference == "identity"


def test_equivalent_source_order_and_aware_time_offsets_have_one_digest() -> None:
    original_mapping = _load("project-snapshot-envelope.json")
    reordered_mapping = copy.deepcopy(original_mapping)
    reordered_mapping["sources"].reverse()  # type: ignore[union-attr]
    reordered_mapping["resource"]["recorded_at"] = "2026-10-18T04:04:00-04:00"  # type: ignore[index]

    original = cross_domain_envelope_from_mapping(original_mapping)
    reordered = cross_domain_envelope_from_mapping(reordered_mapping)
    assert reordered == original
    assert cross_domain_envelope_digest(reordered) == cross_domain_envelope_digest(original)
    assert cross_domain_envelope_to_mapping(reordered)["resource"]["recorded_at"] == "2026-10-18T08:04:00Z"  # type: ignore[index]


def test_duplicate_and_changed_exact_identities_fail_independently() -> None:
    admitted = cross_domain_envelope_from_mapping(_load("model-execution-envelope.json"))
    duplicate = replace(admitted, sources=(*admitted.sources, admitted.sources[0]))
    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        validate_cross_domain_envelope(duplicate)
    assert invalid.value.reference.endswith("duplicate")

    changed_reference = replace(
        admitted.sources[0].reference,
        integrity_digest="1" * 64,
    )
    conflict = replace(
        admitted,
        sources=(
            *admitted.sources,
            replace(admitted.sources[0], reference=changed_reference),
        ),
    )
    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        validate_cross_domain_envelope(conflict)
    assert invalid.value.reference.endswith("identity_conflict")


def test_private_unknown_and_malformed_input_fail_with_bounded_diagnostics() -> None:
    private = _load("market-observation-envelope.json")
    private["resource"]["provider_payload"] = "private-value"  # type: ignore[index]
    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        cross_domain_envelope_from_mapping(private)
    assert invalid.value.reference == "resource"
    assert len(invalid.value.reference) <= 120
    assert "private-value" not in str(invalid.value)

    malformed = _load("financial-result-envelope.json")
    malformed["resource"]["identity"]["subject_kind"] = "portfolio"  # type: ignore[index]
    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        cross_domain_envelope_from_mapping(malformed)
    assert invalid.value.reference == "resource.identity.subject_kind"


def test_extended_closed_values_cannot_hide_uncanonicalized_state() -> None:
    class ExtendedDatasetIdentity(DatasetSnapshotIdentity):
        __slots__ = ("provider_payload",)

    class ExtendedResource(CrossDomainResourceReference):
        pass

    class ExtendedEnvelope(CrossDomainProvenanceEnvelope):
        pass

    admitted = cross_domain_envelope_from_mapping(
        _load("dataset-snapshot-envelope.json")
    )
    extended_identity = ExtendedDatasetIdentity(
        admitted.resource.identity.dataset_id,  # type: ignore[union-attr]
        admitted.resource.identity.dataset_version,  # type: ignore[union-attr]
    )
    object.__setattr__(extended_identity, "provider_payload", "private-value")
    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        validate_cross_domain_envelope(
            replace(
                admitted,
                resource=replace(admitted.resource, identity=extended_identity),
            )
        )
    assert invalid.value.reference == "resource.identity"

    extended_resource = ExtendedResource(
        admitted.resource.profile,
        admitted.resource.owner_module,
        admitted.resource.resource_kind,
        admitted.resource.resource_id,
        admitted.resource.identity,
        admitted.resource.integrity_digest,
        admitted.resource.recorded_at,
        admitted.resource.provenance_label,
        admitted.resource.validation_status,
    )
    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        validate_cross_domain_envelope(replace(admitted, resource=extended_resource))
    assert invalid.value.reference == "resource"

    extended_envelope = ExtendedEnvelope(
        admitted.schema_version,
        admitted.resource,
        admitted.producer,
        admitted.sources,
    )
    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        validate_cross_domain_envelope(extended_envelope)
    assert invalid.value.reference == "envelope"

    class ExtendedProducer(CrossDomainProducer):
        pass

    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        validate_cross_domain_envelope(
            replace(
                admitted,
                producer=ExtendedProducer(
                    admitted.producer.producer_id,
                    admitted.producer.producer_version,
                ),
            )
        )
    assert invalid.value.reference == "producer"

    class ExtendedSource(CrossDomainSource):
        pass

    with_sources = cross_domain_envelope_from_mapping(
        _load("model-execution-envelope.json")
    )
    source = with_sources.sources[0]
    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        validate_cross_domain_envelope(
            replace(
                with_sources,
                sources=(ExtendedSource(source.relation, source.reference),),
            )
        )
    assert invalid.value.reference == "sources.0"


def test_profile_rules_are_process_immutable() -> None:
    from financial_ai_academy.modules.audit.domain import cross_domain_provenance

    rules = cross_domain_provenance._PROFILE_RULES
    with pytest.raises(TypeError):
        rules[CrossDomainProfile.DATASET_SNAPSHOT] = rules[  # type: ignore[index]
            CrossDomainProfile.PROJECT_SNAPSHOT
        ]
    assert len(rules) == 9


def test_invalid_aware_times_fail_with_bounded_deterministic_errors() -> None:
    class MissingOffset(tzinfo):
        def utcoffset(self, value: datetime | None) -> None:
            return None

        def dst(self, value: datetime | None) -> None:
            return None

    admitted = cross_domain_envelope_from_mapping(
        _load("dataset-snapshot-envelope.json")
    )
    missing_offset = datetime(2026, 1, 1, tzinfo=MissingOffset())
    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        validate_cross_domain_envelope(
            replace(
                admitted,
                resource=replace(admitted.resource, recorded_at=missing_offset),
            )
        )
    assert invalid.value.reference == "resource.recorded_at"

    underflow = _load("dataset-snapshot-envelope.json")
    underflow["resource"]["recorded_at"] = "0001-01-01T00:00:00+23:59"  # type: ignore[index]
    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        cross_domain_envelope_from_mapping(underflow)
    assert invalid.value.reference == "resource.recorded_at"


def test_source_limit_rejects_before_parsing_source_elements() -> None:
    oversized = _load("dataset-snapshot-envelope.json")
    oversized["sources"] = ["private-value"] * 21
    with pytest.raises(InvalidCrossDomainProvenance) as invalid:
        cross_domain_envelope_from_mapping(oversized)
    assert invalid.value.reference == "sources"
    assert "private-value" not in str(invalid.value)


def test_one_invalid_profile_does_not_disable_unrelated_valid_profiles() -> None:
    dataset = cross_domain_envelope_from_mapping(_load("dataset-snapshot-envelope.json"))
    invalid_market = _load("market-observation-envelope.json")
    invalid_market["resource"]["owner_module"] = "audit"  # type: ignore[index]
    project = cross_domain_envelope_from_mapping(_load("project-snapshot-envelope.json"))

    assert validate_cross_domain_envelope(dataset) == dataset
    with pytest.raises(InvalidCrossDomainProvenance):
        cross_domain_envelope_from_mapping(invalid_market)
    assert validate_cross_domain_envelope(project) == project


def test_valid_unicode_and_zero_sources_do_not_depend_on_fixture_values() -> None:
    record = _load("dataset-snapshot-envelope.json")
    record["resource"]["resource_id"] = "資料-été-02"  # type: ignore[index]
    record["resource"]["identity"]["dataset_id"] = "資料-été-02"  # type: ignore[index]
    record["resource"]["identity"]["dataset_version"] = "2026.10.19-beta+2"  # type: ignore[index]
    record["resource"]["recorded_at"] = "2026-10-18T10:01:00+02:00"  # type: ignore[index]
    record["resource"]["provenance_label"] = "generated"  # type: ignore[index]
    record["sources"] = []

    admitted = cross_domain_envelope_from_mapping(record)
    assert admitted.resource.resource_id == "資料-été-02"
    assert admitted.sources == ()
    assert cross_domain_envelope_to_mapping(admitted)["resource"]["recorded_at"] == "2026-10-18T08:01:00Z"  # type: ignore[index]


def test_pure_core_has_no_runtime_or_provider_imports() -> None:
    source = (
        ROOT
        / "backend/src/financial_ai_academy/modules/audit/domain/cross_domain_provenance.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "requests",
        "psycopg",
        "subprocess",
        "pathlib",
        "urllib",
        "financial_ai_academy.modules.project",
    ):
        assert forbidden not in source
