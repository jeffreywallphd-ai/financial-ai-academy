"""Compose exact public evidence into deterministic navigation state."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timezone
from enum import StrEnum
import re
from uuid import UUID

from financial_ai_academy.modules.curriculum.public import (
    AssessmentActivityReference,
    CurriculumActivityKind,
    CurriculumGraph,
    LessonActivityReference,
)

from ..domain.activity_launch import (
    ActivityLaunchResolution,
    ResolveActivityLaunchRequest,
    resolve_activity_launch,
)
from ..domain.models import (
    ActivitySourceFact,
    ActivitySourceState,
    CompletionState,
    EvaluateNavigationStateRequest,
    NavigationStateProjection,
    evaluate_navigation_state,
)
from ..ports.navigation_sources import (
    AssessmentSourceReference,
    CurriculumNavigationSourcePort,
    ExactCurriculumGraphRequest,
    LessonCompletionSourcePort,
    LessonSourceReference,
    NavigationClockPort,
    NavigationSourceError,
    NavigationSourceErrorCode,
)


_CURRICULUM_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
_VERSION = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$"
)


class NavigationStateOperationErrorCode(StrEnum):
    INVALID_CONTEXT = "invalid_context"
    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"


class NavigationStateOperationError(RuntimeError):
    """Application error that cannot disclose learner or provider details."""

    def __init__(
        self,
        code: NavigationStateOperationErrorCode,
        safe_message: str,
    ) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message


@dataclass(frozen=True, slots=True)
class OpenNavigationStateRequest:
    learner_id: str
    curriculum_id: str
    curriculum_version: str


@dataclass(frozen=True, slots=True)
class OpenActivityLaunchRequest:
    learner_id: str
    curriculum_id: str
    curriculum_version: str
    activity_id: str


class AdaptationService:
    def __init__(
        self,
        curriculum: CurriculumNavigationSourcePort,
        completion: LessonCompletionSourcePort,
        clock: NavigationClockPort,
    ) -> None:
        self._curriculum = curriculum
        self._completion = completion
        self._clock = clock

    def evaluate_navigation_state(
        self,
        request: EvaluateNavigationStateRequest,
    ) -> NavigationStateProjection:
        return evaluate_navigation_state(request)

    def open_navigation_state(
        self,
        request: OpenNavigationStateRequest,
    ) -> NavigationStateProjection:
        _graph, projection = self._open_navigation_context(request)
        return projection

    def open_activity_launch(
        self,
        request: OpenActivityLaunchRequest,
    ) -> ActivityLaunchResolution:
        graph, projection = self._open_navigation_context(
            OpenNavigationStateRequest(
                learner_id=request.learner_id,
                curriculum_id=request.curriculum_id,
                curriculum_version=request.curriculum_version,
            )
        )
        return resolve_activity_launch(
            ResolveActivityLaunchRequest(
                graph=graph,
                navigation_state=projection,
                activity_id=request.activity_id,
            )
        )

    def _open_navigation_context(
        self,
        request: OpenNavigationStateRequest,
    ) -> tuple[CurriculumGraph, NavigationStateProjection]:
        self._validate_request(request)
        try:
            graph = self._curriculum.open_graph(
                ExactCurriculumGraphRequest(
                    request.curriculum_id,
                    request.curriculum_version,
                )
            )
        except NavigationSourceError as error:
            code = (
                NavigationStateOperationErrorCode.NOT_FOUND
                if error.code is NavigationSourceErrorCode.NOT_FOUND
                else NavigationStateOperationErrorCode.UNAVAILABLE
            )
            raise NavigationStateOperationError(
                code,
                "The exact curriculum navigation state could not be opened."
                if code is NavigationStateOperationErrorCode.NOT_FOUND
                else "Navigation state is currently unavailable.",
            ) from error
        except Exception as error:
            raise self._unavailable() from error

        facts: list[ActivitySourceFact] = []
        try:
            if (
                graph.curriculum_id != request.curriculum_id
                or graph.curriculum_version != request.curriculum_version
            ):
                raise self._unavailable()
            for activity in graph.activities:
                reference = activity.reference
                if (
                    activity.kind is CurriculumActivityKind.LESSON
                    and isinstance(reference, LessonActivityReference)
                ):
                    source = LessonSourceReference(
                        reference.placement_id,
                        reference.package_id,
                        reference.package_version,
                        reference.package_digest,
                    )
                    available = self._curriculum.lesson_is_available(source)
                    completion = self._completion.observe_lesson_completion(
                        learner_id=request.learner_id,
                        placement_id=reference.placement_id,
                        fallback_digest=reference.package_digest,
                    )
                    completion_state = completion.state
                    source_digest = completion.source_digest
                elif (
                    activity.kind is CurriculumActivityKind.ASSESSMENT
                    and isinstance(reference, AssessmentActivityReference)
                ):
                    source = AssessmentSourceReference(
                        reference.placement_id,
                        reference.assessment_id,
                        reference.assessment_version,
                        reference.definition_digest,
                    )
                    available = self._curriculum.assessment_is_available(
                        source
                    )
                    completion_state = CompletionState.UNAVAILABLE
                    source_digest = reference.definition_digest
                else:
                    raise self._unavailable()
                facts.append(
                    ActivitySourceFact(
                        activity_id=activity.activity_id,
                        activity_source_state=(
                            ActivitySourceState.AVAILABLE
                            if available
                            else ActivitySourceState.UNAVAILABLE
                        ),
                        completion_state=completion_state,
                        source_digest=source_digest,
                    )
                )
            evaluated_at = self._clock.now()
            if (
                evaluated_at.tzinfo is None
                or evaluated_at.utcoffset() is None
            ):
                raise self._unavailable()
            projection = evaluate_navigation_state(
                EvaluateNavigationStateRequest(
                    graph=graph,
                    activity_facts=tuple(facts),
                    evaluated_at=evaluated_at.astimezone(timezone.utc),
                )
            )
            return graph, projection
        except NavigationStateOperationError:
            raise
        except Exception as error:
            raise self._unavailable() from error

    @staticmethod
    def _validate_request(request: OpenNavigationStateRequest) -> None:
        try:
            UUID(request.learner_id)
        except (AttributeError, TypeError, ValueError) as error:
            raise NavigationStateOperationError(
                NavigationStateOperationErrorCode.INVALID_CONTEXT,
                "A valid learner context is required.",
            ) from error
        if (
            _CURRICULUM_ID.fullmatch(request.curriculum_id) is None
            or _VERSION.fullmatch(request.curriculum_version) is None
        ):
            raise NavigationStateOperationError(
                NavigationStateOperationErrorCode.INVALID_CONTEXT,
                "The navigation-state request is invalid.",
            )

    @staticmethod
    def _unavailable() -> NavigationStateOperationError:
        return NavigationStateOperationError(
            NavigationStateOperationErrorCode.UNAVAILABLE,
            "Navigation state is currently unavailable.",
        )
