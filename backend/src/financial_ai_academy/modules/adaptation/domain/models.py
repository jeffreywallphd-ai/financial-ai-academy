"""Deterministic, provider-neutral curriculum navigation-state policy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import re
from typing import Mapping

from financial_ai_academy.modules.curriculum.public import (
    CurriculumBranchKind,
    CurriculumGraph,
    CurriculumGraphError,
    CurriculumRelationshipKind,
    validate_curriculum_graph,
)


SCHEMA_VERSION = "1.0.0"
DEFAULT_POLICY_ID = "deterministic-prerequisite-baseline"
DEFAULT_POLICY_VERSION = "1.0.0"
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
VERSION = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")


class ActivitySourceState(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class CompletionState(StrEnum):
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"
    UNAVAILABLE = "unavailable"


class EligibilityState(StrEnum):
    ELIGIBLE = "eligible"
    LOCKED = "locked"
    UNAVAILABLE = "unavailable"


class RequirementState(StrEnum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    UNASSIGNED = "unassigned"


class NavigationReasonCode(StrEnum):
    ACTIVITY_COMPLETED = "activity_completed"
    REQUIRED_ACTIVITY = "required_activity"
    OPTIONAL_ACTIVITY = "optional_activity"
    UNASSIGNED_ACTIVITY = "unassigned_activity"
    ACTIVITY_SOURCE_UNAVAILABLE = "activity_source_unavailable"
    COMPLETION_SOURCE_UNAVAILABLE = "completion_source_unavailable"
    ENTRY_ACTIVITY = "entry_activity"
    PREREQUISITE_INCOMPLETE = "prerequisite_incomplete"
    PREREQUISITE_UNAVAILABLE = "prerequisite_unavailable"
    PREREQUISITE_SATISFIED = "prerequisite_satisfied"


class NavigationStateErrorCode(StrEnum):
    INVALID_CONTEXT = "invalid_context"
    INVALID_GRAPH = "invalid_graph"
    INVALID_SOURCE_FACTS = "invalid_source_facts"
    UNSUPPORTED_VERSION = "unsupported_version"
    DIGEST_MISMATCH = "digest_mismatch"


class NavigationStateError(ValueError):
    """Bounded policy error without another module's payload or details."""

    def __init__(
        self,
        code: NavigationStateErrorCode,
        message: str,
        *,
        reference: str = "navigation-state",
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
class ActivitySourceFact:
    activity_id: str
    activity_source_state: ActivitySourceState
    completion_state: CompletionState
    source_digest: str


@dataclass(frozen=True, slots=True)
class EvaluateNavigationStateRequest:
    graph: CurriculumGraph
    activity_facts: tuple[ActivitySourceFact, ...]
    evaluated_at: datetime
    policy_id: str = DEFAULT_POLICY_ID
    policy_version: str = DEFAULT_POLICY_VERSION


@dataclass(frozen=True, slots=True)
class NavigationReason:
    code: NavigationReasonCode
    explanation: str
    references: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ActivityNavigationState:
    activity_id: str
    completion: CompletionState
    eligibility: EligibilityState
    requirement: RequirementState
    availability: ActivitySourceState
    reasons: tuple[NavigationReason, ...]


@dataclass(frozen=True, slots=True)
class NavigationStateProjection:
    schema_version: str
    curriculum_id: str
    curriculum_version: str
    graph_digest: str
    policy_id: str
    policy_version: str
    evaluated_at: datetime
    source_set_digest: str
    activity_states: tuple[ActivityNavigationState, ...]
    projection_digest: str


def _safe_reference(value: object) -> str:
    return (
        str(value)
        .replace(chr(0), "")
        .replace("\r", " ")
        .replace("\n", " ")[:120]
    )


def _reject(
    code: NavigationStateErrorCode,
    reference: str,
    message: str,
) -> None:
    raise NavigationStateError(code, message, reference=reference)


def _validate_identifier(value: object, reference: str) -> str:
    if not isinstance(value, str) or IDENTIFIER.fullmatch(value) is None:
        _reject(
            NavigationStateErrorCode.INVALID_CONTEXT,
            reference,
            "Navigation-state context is invalid.",
        )
    return value


def _validate_version(value: object, reference: str) -> str:
    if not isinstance(value, str) or VERSION.fullmatch(value) is None:
        _reject(
            NavigationStateErrorCode.UNSUPPORTED_VERSION,
            reference,
            "Navigation-state version is unsupported.",
        )
    return value


def _validate_digest(value: object, reference: str) -> str:
    if not isinstance(value, str) or DIGEST.fullmatch(value) is None:
        _reject(
            NavigationStateErrorCode.INVALID_SOURCE_FACTS,
            reference,
            "Navigation-state source facts are invalid.",
        )
    return value


def canonical_timestamp(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None:
        _reject(
            NavigationStateErrorCode.INVALID_CONTEXT,
            "evaluated_at",
            "Navigation-state evaluation time is invalid.",
        )
    try:
        offset = value.utcoffset()
        if offset is None:
            raise ValueError("missing offset")
        normalized = value.astimezone(timezone.utc)
    except (OverflowError, ValueError):
        _reject(
            NavigationStateErrorCode.INVALID_CONTEXT,
            "evaluated_at",
            "Navigation-state evaluation time is invalid.",
        )
    return normalized.isoformat().removesuffix("+00:00") + "Z"


def _reason(
    code: NavigationReasonCode,
    explanation: str,
    *references: str,
) -> NavigationReason:
    if not 1 <= len(references) <= 10 or any(
        not isinstance(item, str)
        or IDENTIFIER.fullmatch(item) is None
        for item in references
    ):
        _reject(
            NavigationStateErrorCode.INVALID_CONTEXT,
            "reason.references",
            "Navigation-state reason references are invalid.",
        )
    return NavigationReason(code, explanation, tuple(references))


def _fact_payload(fact: ActivitySourceFact) -> dict[str, str]:
    return {
        "activity_id": fact.activity_id,
        "activity_source_state": fact.activity_source_state.value,
        "completion_state": fact.completion_state.value,
        "source_digest": fact.source_digest,
    }


def source_facts_payload(
    request: EvaluateNavigationStateRequest,
) -> dict[str, object]:
    """Return the closed portable evaluation input after validation/order."""
    graph, facts = _validated_inputs(request)
    ordered = {fact.activity_id: fact for fact in facts}
    return {
        "schema_version": SCHEMA_VERSION,
        "curriculum_id": graph.curriculum_id,
        "curriculum_version": graph.curriculum_version,
        "graph_digest": graph.graph_digest,
        "policy_id": request.policy_id,
        "policy_version": request.policy_version,
        "evaluated_at": canonical_timestamp(request.evaluated_at),
        "activity_facts": [
            _fact_payload(ordered[activity.activity_id])
            for activity in graph.activities
        ],
    }


def canonical_source_set_bytes(
    graph: CurriculumGraph,
    facts: tuple[ActivitySourceFact, ...],
) -> bytes:
    ordered = {fact.activity_id: fact for fact in facts}
    meaning = {
        "schema_version": SCHEMA_VERSION,
        "curriculum_id": graph.curriculum_id,
        "curriculum_version": graph.curriculum_version,
        "graph_digest": graph.graph_digest,
        "activity_facts": [
            _fact_payload(ordered[activity.activity_id])
            for activity in graph.activities
        ],
    }
    return json.dumps(
        meaning,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def source_set_digest(
    graph: CurriculumGraph,
    facts: tuple[ActivitySourceFact, ...],
) -> str:
    return hashlib.sha256(canonical_source_set_bytes(graph, facts)).hexdigest()


def _reason_payload(reason: NavigationReason) -> dict[str, object]:
    return {
        "code": reason.code.value,
        "explanation": reason.explanation,
        "references": list(reason.references),
    }


def _state_payload(state: ActivityNavigationState) -> dict[str, object]:
    return {
        "activity_id": state.activity_id,
        "completion": state.completion.value,
        "eligibility": state.eligibility.value,
        "requirement": state.requirement.value,
        "availability": state.availability.value,
        "reasons": [_reason_payload(reason) for reason in state.reasons],
    }


def navigation_state_payload(
    projection: NavigationStateProjection,
) -> dict[str, object]:
    return {
        "schema_version": projection.schema_version,
        "curriculum_id": projection.curriculum_id,
        "curriculum_version": projection.curriculum_version,
        "graph_digest": projection.graph_digest,
        "policy_id": projection.policy_id,
        "policy_version": projection.policy_version,
        "evaluated_at": canonical_timestamp(projection.evaluated_at),
        "source_set_digest": projection.source_set_digest,
        "activity_states": [
            _state_payload(state) for state in projection.activity_states
        ],
        "projection_digest": projection.projection_digest,
    }


def canonical_projection_bytes(
    projection: NavigationStateProjection,
) -> bytes:
    meaning = navigation_state_payload(projection)
    meaning.pop("projection_digest")
    return json.dumps(
        meaning,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def navigation_projection_digest(
    projection: NavigationStateProjection,
) -> str:
    return hashlib.sha256(canonical_projection_bytes(projection)).hexdigest()


def _validated_inputs(
    request: EvaluateNavigationStateRequest,
) -> tuple[CurriculumGraph, tuple[ActivitySourceFact, ...]]:
    if not isinstance(request, EvaluateNavigationStateRequest):
        _reject(
            NavigationStateErrorCode.INVALID_CONTEXT,
            "request",
            "Navigation-state request is invalid.",
        )
    try:
        graph = validate_curriculum_graph(request.graph)
    except (CurriculumGraphError, KeyError, TypeError, ValueError):
        _reject(
            NavigationStateErrorCode.INVALID_GRAPH,
            "curriculum-graph",
            "Curriculum graph is invalid for navigation evaluation.",
        )
    _validate_identifier(request.policy_id, "policy_id")
    _validate_version(request.policy_version, "policy_version")
    canonical_timestamp(request.evaluated_at)
    activity_ids = [activity.activity_id for activity in graph.activities]
    facts_by_id: dict[str, ActivitySourceFact] = {}
    for fact in request.activity_facts:
        if not isinstance(fact, ActivitySourceFact):
            _reject(
                NavigationStateErrorCode.INVALID_SOURCE_FACTS,
                "activity_facts",
                "Navigation-state source facts are invalid.",
            )
        _validate_identifier(fact.activity_id, "activity_id")
        if (
            not isinstance(fact.activity_source_state, ActivitySourceState)
            or not isinstance(fact.completion_state, CompletionState)
        ):
            _reject(
                NavigationStateErrorCode.INVALID_SOURCE_FACTS,
                fact.activity_id,
                "Navigation-state source facts are invalid.",
            )
        _validate_digest(fact.source_digest, fact.activity_id)
        if fact.activity_id in facts_by_id:
            _reject(
                NavigationStateErrorCode.INVALID_SOURCE_FACTS,
                fact.activity_id,
                "Navigation-state source facts must be unique.",
            )
        facts_by_id[fact.activity_id] = fact
    if set(facts_by_id) != set(activity_ids):
        _reject(
            NavigationStateErrorCode.INVALID_SOURCE_FACTS,
            "activity_facts",
            "Navigation-state source facts must cover the exact graph.",
        )
    return graph, tuple(facts_by_id[item] for item in activity_ids)


def _requirements(graph: CurriculumGraph) -> Mapping[str, RequirementState]:
    result: dict[str, RequirementState] = {
        activity.activity_id: RequirementState.UNASSIGNED
        for activity in graph.activities
    }
    for branch in graph.branches:
        requirement = (
            RequirementState.REQUIRED
            if branch.kind is CurriculumBranchKind.REQUIRED
            else RequirementState.OPTIONAL
        )
        for activity_id in branch.activity_ids:
            result[activity_id] = requirement
    return result


def evaluate_navigation_state(
    request: EvaluateNavigationStateRequest,
) -> NavigationStateProjection:
    """Evaluate exact source closure with the permanent deterministic baseline."""
    graph, facts = _validated_inputs(request)
    facts_by_id = {fact.activity_id: fact for fact in facts}
    requirements = _requirements(graph)
    prerequisites: dict[str, list[object]] = {
        activity.activity_id: [] for activity in graph.activities
    }
    for relationship in graph.relationships:
        if relationship.kind is CurriculumRelationshipKind.ACTIVITY_PREREQUISITE:
            prerequisites[relationship.target_id].append(relationship)

    states: list[ActivityNavigationState] = []
    requirement_reasons = {
        RequirementState.REQUIRED: (
            NavigationReasonCode.REQUIRED_ACTIVITY,
            "This activity belongs to a required curriculum branch.",
        ),
        RequirementState.OPTIONAL: (
            NavigationReasonCode.OPTIONAL_ACTIVITY,
            "This activity belongs to an optional curriculum branch.",
        ),
        RequirementState.UNASSIGNED: (
            NavigationReasonCode.UNASSIGNED_ACTIVITY,
            "This activity is not assigned to a required or optional branch.",
        ),
    }
    for activity in graph.activities:
        fact = facts_by_id[activity.activity_id]
        requirement = requirements[activity.activity_id]
        reasons: list[NavigationReason] = []
        if fact.completion_state is CompletionState.COMPLETED:
            reasons.append(
                _reason(
                    NavigationReasonCode.ACTIVITY_COMPLETED,
                    "Accepted completion evidence exists for this exact activity.",
                    activity.activity_id,
                )
            )
        requirement_code, requirement_text = requirement_reasons[requirement]
        reasons.append(
            _reason(
                requirement_code,
                requirement_text,
                activity.activity_id,
            )
        )

        eligibility: EligibilityState
        if fact.activity_source_state is ActivitySourceState.UNAVAILABLE:
            eligibility = EligibilityState.UNAVAILABLE
            reasons.append(
                _reason(
                    NavigationReasonCode.ACTIVITY_SOURCE_UNAVAILABLE,
                    "The exact activity source is currently unavailable.",
                    activity.activity_id,
                )
            )
        elif fact.completion_state is CompletionState.UNAVAILABLE:
            eligibility = EligibilityState.UNAVAILABLE
            reasons.append(
                _reason(
                    NavigationReasonCode.COMPLETION_SOURCE_UNAVAILABLE,
                    "Current completion evidence cannot be evaluated safely.",
                    activity.activity_id,
                )
            )
        else:
            incoming = prerequisites[activity.activity_id]
            unmet = [
                relationship
                for relationship in incoming
                if facts_by_id[relationship.source_id].completion_state
                is not CompletionState.COMPLETED
                or facts_by_id[relationship.source_id].activity_source_state
                is not ActivitySourceState.AVAILABLE
            ]
            if unmet:
                eligibility = EligibilityState.LOCKED
                for relationship in unmet:
                    prerequisite = facts_by_id[relationship.source_id]
                    unavailable = (
                        prerequisite.completion_state
                        is CompletionState.UNAVAILABLE
                        or prerequisite.activity_source_state
                        is ActivitySourceState.UNAVAILABLE
                    )
                    reasons.append(
                        _reason(
                            NavigationReasonCode.PREREQUISITE_UNAVAILABLE
                            if unavailable
                            else NavigationReasonCode.PREREQUISITE_INCOMPLETE,
                            "A required prerequisite cannot be evaluated safely."
                            if unavailable
                            else "A required prerequisite is not complete.",
                            activity.activity_id,
                            relationship.source_id,
                            relationship.relationship_id,
                        )
                    )
            else:
                eligibility = EligibilityState.ELIGIBLE
                if incoming:
                    for relationship in incoming:
                        reasons.append(
                            _reason(
                                NavigationReasonCode.PREREQUISITE_SATISFIED,
                                "A required activity prerequisite is complete.",
                                activity.activity_id,
                                relationship.source_id,
                                relationship.relationship_id,
                            )
                        )
                else:
                    reasons.append(
                        _reason(
                            NavigationReasonCode.ENTRY_ACTIVITY,
                            "This activity has no activity prerequisite.",
                            activity.activity_id,
                        )
                    )
        states.append(
            ActivityNavigationState(
                activity_id=activity.activity_id,
                completion=fact.completion_state,
                eligibility=eligibility,
                requirement=requirement,
                availability=fact.activity_source_state,
                reasons=tuple(reasons),
            )
        )

    projection = NavigationStateProjection(
        schema_version=SCHEMA_VERSION,
        curriculum_id=graph.curriculum_id,
        curriculum_version=graph.curriculum_version,
        graph_digest=graph.graph_digest,
        policy_id=request.policy_id,
        policy_version=request.policy_version,
        evaluated_at=request.evaluated_at,
        source_set_digest=source_set_digest(graph, facts),
        activity_states=tuple(states),
        projection_digest="0" * 64,
    )
    return NavigationStateProjection(
        schema_version=projection.schema_version,
        curriculum_id=projection.curriculum_id,
        curriculum_version=projection.curriculum_version,
        graph_digest=projection.graph_digest,
        policy_id=projection.policy_id,
        policy_version=projection.policy_version,
        evaluated_at=projection.evaluated_at,
        source_set_digest=projection.source_set_digest,
        activity_states=projection.activity_states,
        projection_digest=navigation_projection_digest(projection),
    )
