from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from financial_ai_academy.modules.audit.adapters import (
    cross_domain_envelope_from_mapping,
)
from financial_ai_academy.modules.audit.application import (
    CrossDomainConformanceCase,
    CrossDomainConformanceCode,
    evaluate_cross_domain_reference,
    run_cross_domain_conformance,
)
from financial_ai_academy.modules.audit.domain import (
    CrossDomainProfile,
    CrossDomainProvenanceEnvelope,
)


ROOT = Path(__file__).resolve().parents[4]
APPROVED = ROOT / "contracts/compatibility/provenance/v2/approved"


def _load(name: str) -> dict[str, object]:
    return json.loads((APPROVED / name).read_text(encoding="utf-8"))


@dataclass(frozen=True, slots=True)
class MappingAdapter:
    profile: CrossDomainProfile
    record: Mapping[str, object]

    def issue_reference(self) -> CrossDomainProvenanceEnvelope:
        return cross_domain_envelope_from_mapping(copy.deepcopy(self.record))


def test_single_adapter_and_partial_suite_return_only_bounded_evidence() -> None:
    adapter = MappingAdapter(
        CrossDomainProfile.DATASET_SNAPSHOT,
        _load("dataset-snapshot-envelope.json"),
    )
    case = evaluate_cross_domain_reference(adapter)
    report = run_cross_domain_conformance((adapter,))

    assert case.valid is True
    assert case.code is CrossDomainConformanceCode.VALID
    assert case.envelope_digest is not None and len(case.envelope_digest) == 64
    assert report.cases == (case,)
    assert CrossDomainProfile.DATASET_SNAPSHOT not in report.missing_profiles
    assert len(report.missing_profiles) == 8
    assert report.complete is False


def test_adapter_failure_and_invalid_reference_do_not_disable_valid_adapter() -> None:
    class FailingAdapter:
        profile = CrossDomainProfile.MARKET_OBSERVATION

        def issue_reference(self) -> CrossDomainProvenanceEnvelope:
            raise RuntimeError("private provider payload https://secret.invalid")

    invalid_record = _load("financial-result-envelope.json")
    invalid_record["resource"]["identity"]["subject_kind"] = "portfolio"  # type: ignore[index]
    adapters = (
        FailingAdapter(),
        MappingAdapter(CrossDomainProfile.FINANCIAL_RESULT, invalid_record),
        MappingAdapter(
            CrossDomainProfile.DATASET_SNAPSHOT,
            _load("dataset-snapshot-envelope.json"),
        ),
    )
    report = run_cross_domain_conformance(adapters)
    cases = {case.profile: case for case in report.cases}

    assert cases[CrossDomainProfile.DATASET_SNAPSHOT].valid is True
    assert cases[CrossDomainProfile.MARKET_OBSERVATION].code is (
        CrossDomainConformanceCode.ADAPTER_FAILURE
    )
    assert cases[CrossDomainProfile.FINANCIAL_RESULT].code is (
        CrossDomainConformanceCode.INVALID_REFERENCE
    )
    rendered = repr(report)
    assert "private provider" not in rendered
    assert "https://" not in rendered


def test_profile_mismatch_and_duplicates_fail_without_selecting_an_adapter() -> None:
    mismatched = MappingAdapter(
        CrossDomainProfile.MODEL_VERSION,
        _load("dataset-snapshot-envelope.json"),
    )
    mismatch = evaluate_cross_domain_reference(mismatched)
    assert mismatch.code is CrossDomainConformanceCode.PROFILE_MISMATCH

    calls: list[str] = []

    class DuplicateAdapter:
        profile = CrossDomainProfile.DATASET_SNAPSHOT

        def issue_reference(self) -> CrossDomainProvenanceEnvelope:
            calls.append("called")
            return cross_domain_envelope_from_mapping(
                _load("dataset-snapshot-envelope.json")
            )

    report = run_cross_domain_conformance((DuplicateAdapter(), DuplicateAdapter()))
    assert calls == []
    assert len(report.cases) == 1
    assert report.cases[0].code is CrossDomainConformanceCode.DUPLICATE_PROFILE


def test_invalid_declaration_and_oversized_suite_fail_before_reference_issue() -> None:
    calls: list[str] = []

    class InvalidProfileAdapter:
        profile = "dataset_snapshot"

        def issue_reference(self) -> CrossDomainProvenanceEnvelope:
            calls.append("called")
            return cross_domain_envelope_from_mapping(
                _load("dataset-snapshot-envelope.json")
            )

    invalid = evaluate_cross_domain_reference(InvalidProfileAdapter())  # type: ignore[arg-type]
    assert invalid.code is CrossDomainConformanceCode.PROFILE_INVALID
    assert calls == []

    oversized = run_cross_domain_conformance(
        tuple(InvalidProfileAdapter() for _ in range(10))  # type: ignore[arg-type]
    )
    assert oversized.cases[0].code is CrossDomainConformanceCode.SUITE_SIZE_INVALID
    assert calls == []

    injected = CrossDomainConformanceCase(
        profile=CrossDomainProfile.DATASET_SNAPSHOT,
        valid=True,
        code=CrossDomainConformanceCode.VALID,
        reference="private payload",
        envelope_digest="0" * 64,
    )

    class InjectedCaseAdapter:
        profile = injected

        def issue_reference(self) -> CrossDomainProvenanceEnvelope:
            calls.append("called")
            return cross_domain_envelope_from_mapping(
                _load("dataset-snapshot-envelope.json")
            )

    rejected = evaluate_cross_domain_reference(InjectedCaseAdapter())  # type: ignore[arg-type]
    assert rejected.code is CrossDomainConformanceCode.PROFILE_INVALID
    assert rejected.reference == "adapter.profile"
    assert calls == []


def test_input_order_cannot_change_case_order_or_results() -> None:
    dataset = MappingAdapter(
        CrossDomainProfile.DATASET_SNAPSHOT,
        _load("dataset-snapshot-envelope.json"),
    )
    project = MappingAdapter(
        CrossDomainProfile.PROJECT_SNAPSHOT,
        _load("project-snapshot-envelope.json"),
    )
    assert run_cross_domain_conformance((dataset, project)) == (
        run_cross_domain_conformance((project, dataset))
    )
