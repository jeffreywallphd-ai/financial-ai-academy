"""Transport-neutral learner assistance-preference contract boundary."""

from __future__ import annotations

from datetime import datetime
from typing import Mapping, Protocol

from ..domain.assistance_preferences import (
    AssistancePreferenceChange,
    AssistancePreferenceExport,
    AssistancePreferenceHistory,
    AssistancePreferenceMutationIntent,
    AssistancePreferenceProfile,
)


class AssistancePreferenceContractFailure(ValueError):
    def __init__(self, code: str, reference: str) -> None:
        super().__init__("The AI-help preference record could not be accepted.")
        self.code = code
        self.reference = reference


class AssistancePreferenceContract(Protocol):
    def parse_profile(self, value: bytes) -> AssistancePreferenceProfile: ...
    def parse_mutation_intent(
        self, value: bytes
    ) -> AssistancePreferenceMutationIntent: ...
    def parse_history(self, value: bytes) -> AssistancePreferenceHistory: ...
    def parse_export(self, value: bytes) -> AssistancePreferenceExport: ...
    def profile_document(
        self, value: AssistancePreferenceProfile
    ) -> dict[str, object]: ...
    def mutation_intent_document(
        self, value: AssistancePreferenceMutationIntent
    ) -> dict[str, object]: ...
    def history_document(
        self, value: AssistancePreferenceHistory
    ) -> dict[str, object]: ...
    def export_document(
        self, value: AssistancePreferenceExport
    ) -> dict[str, object]: ...
    def canonical_digest(self, value: Mapping[str, object]) -> str: ...
    def default_profile(
        self, *, profile_id: str, learner_id: str, created_at: datetime
    ) -> AssistancePreferenceProfile: ...
    def apply_mutation(
        self,
        profile: AssistancePreferenceProfile,
        intent: AssistancePreferenceMutationIntent,
        *,
        occurred_at: datetime,
    ) -> tuple[AssistancePreferenceProfile, AssistancePreferenceChange]: ...
