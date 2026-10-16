"""Learner-model public-surface adapter for lesson completion."""

from __future__ import annotations

import re

from financial_ai_academy.modules.learner_model.public import (
    LearnerModelOperations,
    OpenLessonCompletionRequest,
)

from ..domain.models import CompletionState
from ..ports.navigation_sources import LessonCompletionObservation


_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class PublicLearnerModelCompletionGateway:
    def __init__(self, operations: LearnerModelOperations) -> None:
        self._operations = operations

    def observe_lesson_completion(
        self,
        *,
        learner_id: str,
        placement_id: str,
        fallback_digest: str,
    ) -> LessonCompletionObservation:
        try:
            view = self._operations.open_lesson_completion(
                OpenLessonCompletionRequest(
                    learner_id=learner_id,
                    placement_id=placement_id,
                )
            )
        except Exception:
            return LessonCompletionObservation(
                CompletionState.UNAVAILABLE,
                fallback_digest,
            )
        if (
            view.placement_id != placement_id
            or not isinstance(view.completed, bool)
            or _DIGEST.fullmatch(view.source_digest) is None
            or (
                view.completed
                and getattr(view, "completion_meaning", None)
                != "bounded_knowledge_check_completed"
            )
            or (
                not view.completed
                and getattr(view, "completion_meaning", None)
                != "not_completed"
            )
        ):
            return LessonCompletionObservation(
                CompletionState.UNAVAILABLE,
                fallback_digest,
            )
        return LessonCompletionObservation(
            CompletionState.COMPLETED
            if view.completed
            else CompletionState.INCOMPLETE,
            view.source_digest,
        )
