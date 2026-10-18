"""Test-only synthetic owner adapters for the closed provenance v2 profiles."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Mapping

from financial_ai_academy.modules.audit.adapters import (
    cross_domain_envelope_from_mapping,
)
from financial_ai_academy.modules.audit.domain import (
    CrossDomainProfile,
    CrossDomainProvenanceEnvelope,
)

from .runner import approved_records


@dataclass(frozen=True, slots=True)
class SyntheticReferenceAdapter:
    """Issue a fresh typed envelope from one deterministic contract fixture."""

    profile: CrossDomainProfile
    record: Mapping[str, object]

    def issue_reference(self) -> CrossDomainProvenanceEnvelope:
        return cross_domain_envelope_from_mapping(copy.deepcopy(self.record))


def synthetic_reference_adapters() -> tuple[SyntheticReferenceAdapter, ...]:
    records = approved_records()
    return tuple(
        SyntheticReferenceAdapter(CrossDomainProfile(profile), records[profile])
        for profile in sorted(records)
    )


__all__ = ["SyntheticReferenceAdapter", "synthetic_reference_adapters"]
