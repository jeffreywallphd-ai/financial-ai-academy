"""Transport-neutral learner presentation-preference contract boundary."""

from __future__ import annotations

from datetime import datetime
from typing import Mapping, Protocol

from ..domain.presentation_preferences import (
    PresentationPreferenceChange,
    PresentationPreferenceExport,
    PresentationPreferenceHistory,
    PresentationPreferenceMutationIntent,
    PresentationPreferenceProfile,
)


class PresentationPreferenceContractFailure(ValueError):
    def __init__(self, code: str, reference: str) -> None:
        super().__init__("The display preference record could not be accepted.")
        self.code = code
        self.reference = reference


class PresentationPreferenceContract(Protocol):
    def parse_profile(self, value: bytes) -> PresentationPreferenceProfile: ...
    def parse_mutation_intent(
        self, value: bytes
    ) -> PresentationPreferenceMutationIntent: ...
    def parse_history(self, value: bytes) -> PresentationPreferenceHistory: ...
    def parse_export(self, value: bytes) -> PresentationPreferenceExport: ...
    def profile_document(
        self, value: PresentationPreferenceProfile
    ) -> dict[str, object]: ...
    def mutation_intent_document(
        self, value: PresentationPreferenceMutationIntent
    ) -> dict[str, object]: ...
    def history_document(
        self, value: PresentationPreferenceHistory
    ) -> dict[str, object]: ...
    def export_document(
        self, value: PresentationPreferenceExport
    ) -> dict[str, object]: ...
    def canonical_digest(self, value: Mapping[str, object]) -> str: ...
    def default_profile(
        self, *, profile_id: str, learner_id: str, created_at: datetime
    ) -> PresentationPreferenceProfile: ...
    def apply_mutation(
        self,
        profile: PresentationPreferenceProfile,
        intent: PresentationPreferenceMutationIntent,
        *,
        occurred_at: datetime,
    ) -> tuple[PresentationPreferenceProfile, PresentationPreferenceChange]: ...
