"""Stable public deterministic Adaptation navigation-state surface."""

from __future__ import annotations

from typing import Protocol

from financial_ai_academy.modules.adaptation.domain.models import (
    ActivityNavigationState,
    ActivitySourceFact,
    ActivitySourceState,
    CompletionState,
    DEFAULT_POLICY_ID,
    DEFAULT_POLICY_VERSION,
    EligibilityState,
    EvaluateNavigationStateRequest,
    NavigationReason,
    NavigationReasonCode,
    NavigationStateError,
    NavigationStateErrorCode,
    NavigationStateProjection,
    RequirementState,
    canonical_projection_bytes,
    canonical_source_set_bytes,
    evaluate_navigation_state,
    navigation_projection_digest,
    navigation_state_payload,
    source_facts_payload,
    source_set_digest,
)


class AdaptationOperations(Protocol):
    def evaluate_navigation_state(
        self,
        request: EvaluateNavigationStateRequest,
    ) -> NavigationStateProjection: ...


__all__ = [
    "ActivityNavigationState",
    "ActivitySourceFact",
    "ActivitySourceState",
    "AdaptationOperations",
    "CompletionState",
    "DEFAULT_POLICY_ID",
    "DEFAULT_POLICY_VERSION",
    "EligibilityState",
    "EvaluateNavigationStateRequest",
    "NavigationReason",
    "NavigationReasonCode",
    "NavigationStateError",
    "NavigationStateErrorCode",
    "NavigationStateProjection",
    "RequirementState",
    "canonical_projection_bytes",
    "canonical_source_set_bytes",
    "evaluate_navigation_state",
    "navigation_projection_digest",
    "navigation_state_payload",
    "source_facts_payload",
    "source_set_digest",
]
