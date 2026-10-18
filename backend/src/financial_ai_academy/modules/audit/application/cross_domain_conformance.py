"""Pure, per-call conformance evaluation for cross-domain owner adapters."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import StrEnum

from ..domain.cross_domain_provenance import (
    CrossDomainProfile,
    InvalidCrossDomainProvenance,
    cross_domain_envelope_digest,
    validate_cross_domain_envelope,
)
from ..ports.cross_domain_provenance import CrossDomainReferenceAdapter


class CrossDomainConformanceCode(StrEnum):
    VALID = "valid"
    ADAPTER_FAILURE = "adapter_failure"
    DUPLICATE_PROFILE = "duplicate_profile"
    INVALID_REFERENCE = "invalid_reference"
    PROFILE_INVALID = "profile_invalid"
    PROFILE_MISMATCH = "profile_mismatch"
    SUITE_SIZE_INVALID = "suite_size_invalid"


@dataclass(frozen=True, slots=True)
class CrossDomainConformanceCase:
    profile: CrossDomainProfile | None
    valid: bool
    code: CrossDomainConformanceCode
    reference: str
    envelope_digest: str | None


@dataclass(frozen=True, slots=True)
class CrossDomainConformanceReport:
    cases: tuple[CrossDomainConformanceCase, ...]
    missing_profiles: tuple[CrossDomainProfile, ...]
    complete: bool


_CLOSED_PROFILES = tuple(sorted(CrossDomainProfile, key=lambda item: item.value))


def evaluate_cross_domain_reference(
    adapter: CrossDomainReferenceAdapter,
) -> CrossDomainConformanceCase:
    """Evaluate one adapter without retaining its reference or exception."""

    profile, failure = _read_profile(adapter)
    if failure is not None:
        return failure
    assert profile is not None
    return _evaluate_declared_adapter(profile, adapter)


def run_cross_domain_conformance(
    adapters: tuple[CrossDomainReferenceAdapter, ...],
) -> CrossDomainConformanceReport:
    """Evaluate a bounded adapter tuple with deterministic isolated results."""

    if type(adapters) is not tuple or len(adapters) > len(_CLOSED_PROFILES):
        case = _invalid_case(
            None,
            CrossDomainConformanceCode.SUITE_SIZE_INVALID,
            "adapters",
        )
        return CrossDomainConformanceReport((case,), _CLOSED_PROFILES, False)

    declarations: list[
        tuple[CrossDomainProfile, CrossDomainReferenceAdapter]
        | CrossDomainConformanceCase
    ] = []
    for adapter in adapters:
        profile, failure = _read_profile(adapter)
        if failure is not None:
            declarations.append(failure)
        else:
            assert profile is not None
            declarations.append((profile, adapter))

    declared_profiles = [
        item[0] for item in declarations if isinstance(item, tuple)
    ]
    counts = Counter(declared_profiles)
    duplicate_profiles = {
        profile for profile, count in counts.items() if count > 1
    }
    cases: list[CrossDomainConformanceCase] = [
        item
        for item in declarations
        if isinstance(item, CrossDomainConformanceCase)
    ]
    for profile in sorted(duplicate_profiles, key=lambda item: item.value):
        cases.append(
            _invalid_case(
                profile,
                CrossDomainConformanceCode.DUPLICATE_PROFILE,
                "adapter.profile",
            )
        )
    for item in declarations:
        if not isinstance(item, tuple) or item[0] in duplicate_profiles:
            continue
        cases.append(_evaluate_declared_adapter(item[0], item[1]))

    cases.sort(
        key=lambda item: (
            item.profile.value if item.profile is not None else "~",
            item.code.value,
        )
    )
    declared = frozenset(declared_profiles)
    missing = tuple(profile for profile in _CLOSED_PROFILES if profile not in declared)
    complete = (
        not missing
        and len(cases) == len(_CLOSED_PROFILES)
        and all(case.valid for case in cases)
    )
    return CrossDomainConformanceReport(tuple(cases), missing, complete)


def _read_profile(
    adapter: CrossDomainReferenceAdapter,
) -> tuple[CrossDomainProfile | None, CrossDomainConformanceCase | None]:
    try:
        profile = adapter.profile
    except Exception:
        return (
            None,
            _invalid_case(
                None,
                CrossDomainConformanceCode.ADAPTER_FAILURE,
                "adapter.profile",
            ),
        )
    if type(profile) is not CrossDomainProfile:
        return (
            None,
            _invalid_case(
                None,
                CrossDomainConformanceCode.PROFILE_INVALID,
                "adapter.profile",
            ),
        )
    return profile, None


def _evaluate_declared_adapter(
    profile: CrossDomainProfile,
    adapter: CrossDomainReferenceAdapter,
) -> CrossDomainConformanceCase:
    try:
        envelope = adapter.issue_reference()
    except InvalidCrossDomainProvenance as error:
        return _invalid_case(
            profile,
            CrossDomainConformanceCode.INVALID_REFERENCE,
            error.reference,
        )
    except Exception:
        return _invalid_case(
            profile,
            CrossDomainConformanceCode.ADAPTER_FAILURE,
            "adapter.reference",
        )
    try:
        admitted = validate_cross_domain_envelope(envelope)
    except InvalidCrossDomainProvenance as error:
        return _invalid_case(
            profile,
            CrossDomainConformanceCode.INVALID_REFERENCE,
            error.reference,
        )
    except Exception:
        return _invalid_case(
            profile,
            CrossDomainConformanceCode.ADAPTER_FAILURE,
            "adapter.reference",
        )
    if admitted.resource.profile is not profile:
        return _invalid_case(
            profile,
            CrossDomainConformanceCode.PROFILE_MISMATCH,
            "adapter.profile",
        )
    return CrossDomainConformanceCase(
        profile=profile,
        valid=True,
        code=CrossDomainConformanceCode.VALID,
        reference="adapter.reference",
        envelope_digest=cross_domain_envelope_digest(admitted),
    )


def _invalid_case(
    profile: CrossDomainProfile | None,
    code: CrossDomainConformanceCode,
    reference: object,
) -> CrossDomainConformanceCase:
    return CrossDomainConformanceCase(
        profile=profile,
        valid=False,
        code=code,
        reference=_safe_reference(reference),
        envelope_digest=None,
    )


def _safe_reference(value: object) -> str:
    return (
        str(value)
        .replace(chr(0), "")
        .replace("\r", " ")
        .replace("\n", " ")[:120]
    )


__all__ = [
    "CrossDomainConformanceCase",
    "CrossDomainConformanceCode",
    "CrossDomainConformanceReport",
    "evaluate_cross_domain_reference",
    "run_cross_domain_conformance",
]
