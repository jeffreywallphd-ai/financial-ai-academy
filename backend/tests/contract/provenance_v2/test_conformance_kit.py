from __future__ import annotations

import copy

import pytest

from financial_ai_academy.modules.audit.application import (
    CrossDomainConformanceCode,
    run_cross_domain_conformance,
)
from financial_ai_academy.modules.audit.domain import CrossDomainProfile

from .runner import CrossDomainContractValidator, approved_records
from .synthetic_adapters import (
    SyntheticReferenceAdapter,
    synthetic_reference_adapters,
)


def test_all_synthetic_profiles_match_the_frozen_language_neutral_runner() -> None:
    adapters = synthetic_reference_adapters()
    report = run_cross_domain_conformance(adapters)
    validator = CrossDomainContractValidator()
    records = approved_records()

    assert report.complete is True
    assert report.missing_profiles == ()
    assert {case.profile: case.envelope_digest for case in report.cases} == {
        CrossDomainProfile(profile): validator.envelope_digest(record)
        for profile, record in records.items()
    }


@pytest.mark.parametrize(
    ("profile", "mutate"),
    [
        (
            CrossDomainProfile.DATASET_SNAPSHOT,
            lambda record: record["resource"].update(  # type: ignore[union-attr]
                {
                    "resource_id": "資料-été-02",
                    "recorded_at": "2026-10-18T10:01:00+02:00",
                    "provenance_label": "generated",
                }
            )
            or record["resource"]["identity"].update(  # type: ignore[index]
                {"dataset_id": "資料-été-02", "dataset_version": "2026.10.19-beta+2"}
            ),
        ),
        (
            CrossDomainProfile.FINANCIAL_RESULT,
            lambda record: record["resource"].update(  # type: ignore[union-attr]
                {"resource_id": "account-research-002"}
            )
            or record["resource"]["identity"].update(  # type: ignore[index]
                {"subject_kind": "account", "account_id": "account-research-002"}
            )
            or record["resource"]["identity"].pop("analysis_id"),  # type: ignore[index]
        ),
        (
            CrossDomainProfile.PROJECT_SNAPSHOT,
            lambda record: record["sources"].reverse(),  # type: ignore[union-attr]
        ),
        (
            CrossDomainProfile.MODEL_EXECUTION,
            lambda record: record["resource"]["identity"].update(  # type: ignore[index]
                {"occurrence": 7}
            ),
        ),
    ],
)
def test_varied_valid_adapter_values_match_runner_canonical_meaning(
    profile: CrossDomainProfile,
    mutate: object,
) -> None:
    record = copy.deepcopy(approved_records()[profile.value])
    mutate(record)  # type: ignore[operator]
    adapter = SyntheticReferenceAdapter(profile, record)
    report = run_cross_domain_conformance((adapter,))

    assert len(report.cases) == 1
    assert report.cases[0].code is CrossDomainConformanceCode.VALID
    assert report.cases[0].envelope_digest == (
        CrossDomainContractValidator().envelope_digest(record)
    )


def test_synthetic_adapters_are_test_only_and_product_kit_has_no_runtime_io() -> None:
    import inspect

    from financial_ai_academy.modules.audit.application import (
        cross_domain_conformance,
    )

    source = inspect.getsource(cross_domain_conformance)
    for forbidden in (
        "synthetic_adapters",
        "pathlib",
        "requests",
        "psycopg",
        "subprocess",
        "urllib",
        "financial_ai_academy.modules.project",
    ):
        assert forbidden not in source
