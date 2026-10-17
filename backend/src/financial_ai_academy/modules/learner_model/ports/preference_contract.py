"""Transport-neutral learner-preference contract boundary."""

from __future__ import annotations

from datetime import datetime
from typing import Mapping, Protocol

from ..domain.preferences import (
    LearnerPreferenceProfile,
    PreferenceChange,
    PreferenceExport,
    PreferenceHistory,
    PreferenceMutationIntent,
)


class LearnerPreferenceContractFailure(ValueError):
    def __init__(self, code: str, reference: str) -> None:
        super().__init__("The learning preference record could not be accepted.")
        self.code = code
        self.reference = reference


class LearnerPreferenceContract(Protocol):
    def parse_profile(self, value: bytes) -> LearnerPreferenceProfile: ...

    def parse_mutation_intent(self, value: bytes) -> PreferenceMutationIntent: ...

    def parse_history(self, value: bytes) -> PreferenceHistory: ...

    def parse_export(self, value: bytes) -> PreferenceExport: ...

    def profile_document(
        self, value: LearnerPreferenceProfile
    ) -> dict[str, object]: ...

    def mutation_intent_document(
        self, value: PreferenceMutationIntent
    ) -> dict[str, object]: ...

    def history_document(self, value: PreferenceHistory) -> dict[str, object]: ...

    def export_document(self, value: PreferenceExport) -> dict[str, object]: ...

    def canonical_digest(self, value: Mapping[str, object]) -> str: ...

    def empty_profile(
        self,
        *,
        profile_id: str,
        learner_id: str,
        created_at: datetime,
    ) -> LearnerPreferenceProfile: ...

    def apply_mutation(
        self,
        profile: LearnerPreferenceProfile,
        intent: PreferenceMutationIntent,
        *,
        occurred_at: datetime,
        issued_id: str | None = None,
    ) -> tuple[LearnerPreferenceProfile, PreferenceChange]: ...
