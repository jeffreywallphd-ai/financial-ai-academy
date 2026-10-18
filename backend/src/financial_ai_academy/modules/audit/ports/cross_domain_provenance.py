"""Owner-facing port for issuing one typed cross-domain provenance reference."""

from __future__ import annotations

from typing import Protocol

from ..domain.cross_domain_provenance import (
    CrossDomainProfile,
    CrossDomainProvenanceEnvelope,
)


class CrossDomainReferenceAdapter(Protocol):
    """Minimal seam a domain owner implements for conformance evaluation."""

    @property
    def profile(self) -> CrossDomainProfile:
        """Return the one closed profile issued by this adapter."""

    def issue_reference(self) -> CrossDomainProvenanceEnvelope:
        """Issue one deterministic typed reference without external effects."""


__all__ = ["CrossDomainReferenceAdapter"]
