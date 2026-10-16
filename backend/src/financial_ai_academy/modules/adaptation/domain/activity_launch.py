"""Deterministic resolution of an eligible curriculum activity launch."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import re

from financial_ai_academy.modules.adaptation.domain.models import (
    ActivityNavigationState,
    ActivitySourceState,
    CompletionState,
    EligibilityState,
    NavigationReason,
    NavigationReasonCode,
    NavigationStateProjection,
    RequirementState,
    canonical_timestamp,
    navigation_projection_digest,
)
from financial_ai_academy.modules.curriculum.public import (
    CurriculumActivityKind,
    CurriculumGraph,
    CurriculumGraphError,
    LessonActivityReference,
    validate_curriculum_graph,
)


SCHEMA_VERSION = "1.0.0"
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
VERSION = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")


class ActivityLaunchErrorCode(StrEnum):
    INVALID_CONTEXT = "invalid_context"
    ACTIVITY_NOT_FOUND = "activity_not_found"
    ACTIVITY_LOCKED = "activity_locked"
    ACTIVITY_UNAVAILABLE = "activity_unavailable"
    UNSUPPORTED_ACTIVITY = "unsupported_activity"


class ActivityLaunchError(ValueError):
    """Bounded launch denial without destinations or source payloads."""

    def __init__(
        self,
        code: ActivityLaunchErrorCode,
        message: str,
        *,
        reference: str = "activity-launch",
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.reference = _safe_reference(reference)

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code.value,
            "message": self.message,
            "reference": self.reference,
        }


@dataclass(frozen=True, slots=True)
class ResolveActivityLaunchRequest:
    graph: CurriculumGraph
    navigation_state: NavigationStateProjection
    activity_id: str


@dataclass(frozen=True, slots=True)
class ActivityLaunchResolution:
    schema_version: str
    curriculum_id: str
    curriculum_version: str
    graph_digest: str
    activity_id: str
    navigation_projection_digest: str
    evaluated_at: datetime
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str
    destination: str


def _safe_reference(value: object) -> str:
    return (
        str(value)
        .replace(chr(0), "")
        .replace("\r", " ")
        .replace("\n", " ")[:120]
    )


def _reject(
    code: ActivityLaunchErrorCode,
    reference: str,
    message: str,
) -> None:
    raise ActivityLaunchError(code, message, reference=reference)


def _identifier(value: object, reference: str) -> str:
    if not isinstance(value, str) or IDENTIFIER.fullmatch(value) is None:
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            reference,
            "Activity launch context is invalid.",
        )
    return value


def _version(value: object, reference: str) -> str:
    if not isinstance(value, str) or VERSION.fullmatch(value) is None:
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            reference,
            "Activity launch context is invalid.",
        )
    return value


def _digest(value: object, reference: str) -> str:
    if not isinstance(value, str) or DIGEST.fullmatch(value) is None:
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            reference,
            "Activity launch context is invalid.",
        )
    return value


def _validate_reason(reason: object, activity_id: str) -> None:
    if (
        not isinstance(reason, NavigationReason)
        or not isinstance(reason.code, NavigationReasonCode)
        or not isinstance(reason.explanation, str)
        or not 1 <= len(reason.explanation) <= 240
        or not isinstance(reason.references, tuple)
        or not 1 <= len(reason.references) <= 10
        or len(set(reason.references)) != len(reason.references)
    ):
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            activity_id,
            "Activity launch navigation state is invalid.",
        )
    for reference in reason.references:
        _identifier(reference, activity_id)


def _validate_state(state: object, expected_activity_id: str) -> None:
    if (
        not isinstance(state, ActivityNavigationState)
        or state.activity_id != expected_activity_id
        or not isinstance(state.completion, CompletionState)
        or not isinstance(state.eligibility, EligibilityState)
        or not isinstance(state.requirement, RequirementState)
        or not isinstance(state.availability, ActivitySourceState)
        or not isinstance(state.reasons, tuple)
        or not 2 <= len(state.reasons) <= 2002
    ):
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            expected_activity_id,
            "Activity launch navigation state is invalid.",
        )
    for reason in state.reasons:
        _validate_reason(reason, expected_activity_id)


def _validated_context(
    request: ResolveActivityLaunchRequest,
) -> tuple[CurriculumGraph, NavigationStateProjection]:
    if not isinstance(request, ResolveActivityLaunchRequest):
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            "request",
            "Activity launch request is invalid.",
        )
    _identifier(request.activity_id, "activity_id")
    try:
        graph = validate_curriculum_graph(request.graph)
    except (CurriculumGraphError, KeyError, TypeError, ValueError):
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            "curriculum-graph",
            "Activity launch curriculum context is invalid.",
        )
    projection = request.navigation_state
    if not isinstance(projection, NavigationStateProjection):
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            "navigation-state",
            "Activity launch navigation state is invalid.",
        )
    if (
        projection.schema_version != SCHEMA_VERSION
        or projection.curriculum_id != graph.curriculum_id
        or projection.curriculum_version != graph.curriculum_version
        or projection.graph_digest != graph.graph_digest
    ):
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            "navigation-state",
            "Activity launch context does not match.",
        )
    _identifier(projection.policy_id, "policy_id")
    _version(projection.policy_version, "policy_version")
    _digest(projection.source_set_digest, "source_set_digest")
    _digest(projection.projection_digest, "projection_digest")
    try:
        canonical_timestamp(projection.evaluated_at)
    except (OverflowError, TypeError, ValueError):
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            "evaluated_at",
            "Activity launch navigation state is invalid.",
        )
    activity_ids = tuple(item.activity_id for item in graph.activities)
    if (
        not isinstance(projection.activity_states, tuple)
        or len(projection.activity_states) != len(activity_ids)
    ):
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            "activity_states",
            "Activity launch navigation state is incomplete.",
        )
    for state, activity_id in zip(projection.activity_states, activity_ids):
        _validate_state(state, activity_id)
    try:
        actual_digest = navigation_projection_digest(projection)
    except (AttributeError, KeyError, TypeError, ValueError):
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            "projection_digest",
            "Activity launch navigation state is invalid.",
        )
    if actual_digest != projection.projection_digest:
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            "projection_digest",
            "Activity launch navigation state does not match its digest.",
        )
    return graph, projection


def resolve_activity_launch(
    request: ResolveActivityLaunchRequest,
) -> ActivityLaunchResolution:
    """Resolve one exact eligible lesson without persisting navigation state."""
    graph, projection = _validated_context(request)
    selected = next(
        (
            (activity, state)
            for activity, state in zip(
                graph.activities,
                projection.activity_states,
            )
            if activity.activity_id == request.activity_id
        ),
        None,
    )
    if selected is None:
        _reject(
            ActivityLaunchErrorCode.ACTIVITY_NOT_FOUND,
            request.activity_id,
            "Activity is not part of this curriculum version.",
        )
    activity, state = selected
    if (
        state.availability is ActivitySourceState.UNAVAILABLE
        or state.completion is CompletionState.UNAVAILABLE
        or state.eligibility is EligibilityState.UNAVAILABLE
    ):
        _reject(
            ActivityLaunchErrorCode.ACTIVITY_UNAVAILABLE,
            request.activity_id,
            "Activity is currently unavailable.",
        )
    if state.eligibility is EligibilityState.LOCKED:
        _reject(
            ActivityLaunchErrorCode.ACTIVITY_LOCKED,
            request.activity_id,
            "Activity is not ready to open.",
        )
    if state.eligibility is not EligibilityState.ELIGIBLE:
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            request.activity_id,
            "Activity launch navigation state is invalid.",
        )
    reference = activity.reference
    if (
        activity.kind is not CurriculumActivityKind.LESSON
        or not isinstance(reference, LessonActivityReference)
    ):
        _reject(
            ActivityLaunchErrorCode.UNSUPPORTED_ACTIVITY,
            request.activity_id,
            "This activity type cannot be opened here.",
        )
    _identifier(reference.placement_id, "placement_id")
    _identifier(reference.package_id, "package_id")
    _version(reference.package_version, "package_version")
    _digest(reference.package_digest, "package_digest")
    return ActivityLaunchResolution(
        schema_version=SCHEMA_VERSION,
        curriculum_id=graph.curriculum_id,
        curriculum_version=graph.curriculum_version,
        graph_digest=graph.graph_digest,
        activity_id=activity.activity_id,
        navigation_projection_digest=projection.projection_digest,
        evaluated_at=projection.evaluated_at,
        placement_id=reference.placement_id,
        package_id=reference.package_id,
        package_version=reference.package_version,
        package_digest=reference.package_digest,
        destination=f"/learn/placements/{reference.placement_id}",
    )


def activity_launch_payload(
    resolution: ActivityLaunchResolution,
) -> dict[str, str]:
    """Map a validated immutable resolution to the closed v1 record."""
    if not isinstance(resolution, ActivityLaunchResolution):
        _reject(
            ActivityLaunchErrorCode.INVALID_CONTEXT,
            "resolution",
            "Activity launch resolution is invalid.",
        )
    return {
        "schema_version": resolution.schema_version,
        "curriculum_id": resolution.curriculum_id,
        "curriculum_version": resolution.curriculum_version,
        "graph_digest": resolution.graph_digest,
        "activity_id": resolution.activity_id,
        "navigation_projection_digest": resolution.navigation_projection_digest,
        "evaluated_at": canonical_timestamp(resolution.evaluated_at),
        "placement_id": resolution.placement_id,
        "package_id": resolution.package_id,
        "package_version": resolution.package_version,
        "package_digest": resolution.package_digest,
        "destination": resolution.destination,
    }
