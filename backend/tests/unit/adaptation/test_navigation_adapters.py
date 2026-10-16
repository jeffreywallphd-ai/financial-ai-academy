from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from financial_ai_academy.modules.adaptation.adapters.curriculum_gateway import (
    PublicCurriculumNavigationGateway,
)
from financial_ai_academy.modules.adaptation.adapters.learner_model_gateway import (
    PublicLearnerModelCompletionGateway,
)
from financial_ai_academy.modules.adaptation.public import CompletionState
from financial_ai_academy.modules.adaptation.ports.navigation_sources import (
    AssessmentSourceReference,
    ExactCurriculumGraphRequest,
    LessonSourceReference,
    NavigationSourceError,
    NavigationSourceErrorCode,
)
from financial_ai_academy.modules.curriculum.public import (
    CurriculumGraphError,
    CurriculumGraphErrorCode,
    OpenCurriculumGraphRequest,
    OpenPlacedLessonRequest,
    ResolvePlacedAssessmentRequest,
)
from financial_ai_academy.modules.learner_model.public import (
    OpenLessonCompletionRequest,
)


class CurriculumOperations:
    graph = object()
    graph_error: Exception | None = None
    lesson_error: Exception | None = None
    assessment_error: Exception | None = None

    def open_curriculum_graph(self, request):
        self.graph_request = request
        if self.graph_error:
            raise self.graph_error
        return self.graph

    def open_placed_lesson(self, request):
        self.lesson_request = request
        if self.lesson_error:
            raise self.lesson_error
        return SimpleNamespace(
            placement_id="lesson-placement",
            package_id="lesson-package",
            package_version="1.0.0",
            package_digest="a" * 64,
        )

    def resolve_placed_assessment(self, request):
        self.assessment_request = request
        if self.assessment_error:
            raise self.assessment_error
        return SimpleNamespace(
            placement_id="assessment-placement",
            assessment_id="assessment-one",
            assessment_version="1.0.0",
            definition_digest="b" * 64,
        )


def test_curriculum_gateway_preserves_exact_public_requests_and_matches() -> None:
    operations = CurriculumOperations()
    gateway = PublicCurriculumNavigationGateway(operations)  # type: ignore[arg-type]

    assert gateway.open_graph(
        ExactCurriculumGraphRequest("curriculum-one", "1.0.0")
    ) is operations.graph
    assert operations.graph_request == OpenCurriculumGraphRequest(
        "curriculum-one", "1.0.0"
    )
    assert gateway.lesson_is_available(
        LessonSourceReference(
            "lesson-placement", "lesson-package", "1.0.0", "a" * 64
        )
    )
    assert operations.lesson_request == OpenPlacedLessonRequest(
        "lesson-placement"
    )
    assert gateway.assessment_is_available(
        AssessmentSourceReference(
            "assessment-placement",
            "assessment-one",
            "1.0.0",
            "b" * 64,
        )
    )
    assert operations.assessment_request == ResolvePlacedAssessmentRequest(
        "assessment-placement"
    )


@pytest.mark.parametrize(
    "error_code",
    [CurriculumGraphErrorCode.NOT_FOUND, CurriculumGraphErrorCode.UNAVAILABLE],
)
def test_curriculum_graph_errors_are_bounded(error_code) -> None:
    operations = CurriculumOperations()
    operations.graph_error = CurriculumGraphError(
        error_code, "private upstream detail"
    )
    gateway = PublicCurriculumNavigationGateway(operations)  # type: ignore[arg-type]

    with pytest.raises(NavigationSourceError) as captured:
        gateway.open_graph(ExactCurriculumGraphRequest("curriculum-one", "1.0.0"))

    assert captured.value.code is (
        NavigationSourceErrorCode.NOT_FOUND
        if error_code is CurriculumGraphErrorCode.NOT_FOUND
        else NavigationSourceErrorCode.UNAVAILABLE
    )
    assert "private" not in str(captured.value)


def test_activity_read_failures_and_exact_mismatches_become_unavailable() -> None:
    operations = CurriculumOperations()
    gateway = PublicCurriculumNavigationGateway(operations)  # type: ignore[arg-type]
    assert not gateway.lesson_is_available(
        LessonSourceReference(
            "lesson-placement", "wrong-package", "1.0.0", "a" * 64
        )
    )
    operations.assessment_error = RuntimeError("private database detail")
    assert not gateway.assessment_is_available(
        AssessmentSourceReference(
            "assessment-placement",
            "assessment-one",
            "1.0.0",
            "b" * 64,
        )
    )


class LearnerModelOperations:
    def __init__(self, result) -> None:
        self.result = result

    def open_lesson_completion(self, request):
        self.request = request
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def test_completion_gateway_maps_exact_public_view() -> None:
    operations = LearnerModelOperations(
        SimpleNamespace(
            placement_id="lesson-placement",
            completed=True,
            completion_meaning="bounded_knowledge_check_completed",
            source_digest="c" * 64,
            rebuilt_at=datetime(2026, 10, 16, tzinfo=timezone.utc),
        )
    )
    gateway = PublicLearnerModelCompletionGateway(operations)  # type: ignore[arg-type]

    observation = gateway.observe_lesson_completion(
        learner_id="90a46e7e-8cbe-4f63-ab1b-8aa01ef95aa6",
        placement_id="lesson-placement",
        fallback_digest="a" * 64,
    )

    assert observation.state is CompletionState.COMPLETED
    assert observation.source_digest == "c" * 64
    assert operations.request == OpenLessonCompletionRequest(
        "90a46e7e-8cbe-4f63-ab1b-8aa01ef95aa6", "lesson-placement"
    )


@pytest.mark.parametrize(
    "result",
    [
        RuntimeError("private source error"),
        SimpleNamespace(
            placement_id="other-placement",
            completed=True,
            completion_meaning="bounded_knowledge_check_completed",
            source_digest="c" * 64,
        ),
        SimpleNamespace(
            placement_id="lesson-placement",
            completed=True,
            completion_meaning="bounded_knowledge_check_completed",
            source_digest="not-a-digest",
        ),
        SimpleNamespace(
            placement_id="lesson-placement",
            completed=True,
            completion_meaning="not_completed",
            source_digest="c" * 64,
        ),
    ],
)
def test_completion_failures_use_bounded_unavailable_fallback(result) -> None:
    observation = PublicLearnerModelCompletionGateway(
        LearnerModelOperations(result)  # type: ignore[arg-type]
    ).observe_lesson_completion(
        learner_id="90a46e7e-8cbe-4f63-ab1b-8aa01ef95aa6",
        placement_id="lesson-placement",
        fallback_digest="a" * 64,
    )

    assert observation.state is CompletionState.UNAVAILABLE
    assert observation.source_digest == "a" * 64
