from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from financial_ai_academy.modules.assessment.public import (
    KnowledgeCheckCompletionEvent,
)
from financial_ai_academy.modules.learner_model.adapters.assessment_gateway import (
    AssessmentCompletionEvidenceSource,
)
from financial_ai_academy.modules.learner_model.application.service import (
    LearnerModelService,
)
from financial_ai_academy.modules.learner_model.domain.models import (
    LessonCompletionProjection,
    SourceCompletionEvidence,
)
from financial_ai_academy.modules.learner_model.public import (
    LearnerModelError,
    LearnerModelErrorCode,
    OpenLessonCompletionRequest,
)


LEARNER_ID = "11111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)
PACKAGE_DIGEST = "7cf84bc2f7483d9131db315260b3812f3ea29821bf296571c0c7e38f05b536bc"
DEFINITION_DIGEST = "98e941f9b53ef429cb6d359246ddb9812e354db2a9381a2ee180ed5758343d2b"


def source_evidence() -> SourceCompletionEvidence:
    return SourceCompletionEvidence(
        event_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        event_version="1.0.0",
        occurred_at=NOW,
        attempt_id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
        evidence_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        learner_id=LEARNER_ID,
        placement_id="intro-risk-return",
        package_id="intro-risk-return",
        package_version="1.1.0",
        package_digest=PACKAGE_DIGEST,
        assessment_id="risk-return-check-1",
        assessment_version="1.0.0",
        definition_digest=DEFINITION_DIGEST,
        item_id="risk-return-tradeoff",
        item_version="1.0.0",
        scoring_policy_id="single-select-exact-match",
        scoring_policy_version="1.0.0",
        score=1,
        max_score=1,
        completed_at=NOW,
    )


class Source:
    def __init__(self, values: tuple[SourceCompletionEvidence, ...]) -> None:
        self.values = values

    def list_for_lesson(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[SourceCompletionEvidence, ...]:
        return self.values


class Repository:
    def __init__(self, fail: bool = False) -> None:
        self.values: list[LessonCompletionProjection] = []
        self.fail = fail

    def replace(self, projection: LessonCompletionProjection) -> None:
        if self.fail:
            raise RuntimeError("private storage details")
        self.values.append(projection)


class Clock:
    def now(self) -> datetime:
        return NOW


def service(
    values: tuple[SourceCompletionEvidence, ...],
    repository: Repository | None = None,
) -> LearnerModelService:
    return LearnerModelService(Source(values), repository or Repository(), Clock())


def request() -> OpenLessonCompletionRequest:
    return OpenLessonCompletionRequest(LEARNER_ID, "intro-risk-return")


def test_empty_source_returns_bounded_incomplete_projection() -> None:
    view = service(()).open_lesson_completion(request())
    assert view.completed is False
    assert view.completion_meaning == "not_completed"
    assert view.history == ()
    assert len(view.source_digest) == 64


def test_exact_source_returns_completion_without_mastery_meaning() -> None:
    repository = Repository()
    view = service((source_evidence(),), repository).open_lesson_completion(
        request()
    )
    assert view.completed is True
    assert view.completion_meaning == "bounded_knowledge_check_completed"
    assert len(view.history) == 1
    assert view.history[0].evidence_id == source_evidence().evidence_id
    assert repository.values[0].source_digest == view.source_digest


@pytest.mark.parametrize(
    "invalid",
    [
        replace(source_evidence(), learner_id="dddddddd-dddd-4ddd-8ddd-dddddddddddd"),
        replace(source_evidence(), event_version="2.0.0"),
        replace(source_evidence(), score=2),
    ],
)
def test_inconsistent_source_fails_before_projection(
    invalid: SourceCompletionEvidence,
) -> None:
    repository = Repository()
    with pytest.raises(LearnerModelError) as captured:
        service((invalid,), repository).open_lesson_completion(request())
    assert captured.value.code is LearnerModelErrorCode.INCONSISTENT_EVIDENCE
    assert repository.values == []


def test_duplicate_event_fails_before_projection() -> None:
    repository = Repository()
    value = source_evidence()
    with pytest.raises(LearnerModelError) as captured:
        service((value, value), repository).open_lesson_completion(request())
    assert captured.value.code is LearnerModelErrorCode.INCONSISTENT_EVIDENCE
    assert repository.values == []


def test_storage_failure_is_bounded() -> None:
    with pytest.raises(LearnerModelError) as captured:
        service((source_evidence(),), Repository(fail=True)).open_lesson_completion(
            request()
        )
    assert captured.value.code is LearnerModelErrorCode.UNAVAILABLE
    assert "private" not in captured.value.safe_message


class Assessment:
    def read_completed_knowledge_checks(self, _request: object) -> tuple[KnowledgeCheckCompletionEvent, ...]:
        value = source_evidence()
        return (
            KnowledgeCheckCompletionEvent(
                schema_version="1.0.0",
                event_id=value.event_id,
                event_type="assessment.knowledge-check.completed",
                event_version=value.event_version,
                owner="assessment",
                occurred_at=value.occurred_at,
                idempotency_key=value.evidence_id,
                attempt_id=value.attempt_id,
                evidence_id=value.evidence_id,
                learner_id=value.learner_id,
                placement_id=value.placement_id,
                package_id=value.package_id,
                package_version=value.package_version,
                package_digest=value.package_digest,
                assessment_id=value.assessment_id,
                assessment_version=value.assessment_version,
                definition_digest=value.definition_digest,
                item_id=value.item_id,
                item_version=value.item_version,
                scoring_policy_id=value.scoring_policy_id,
                scoring_policy_version=value.scoring_policy_version,
                score=value.score,
                max_score=value.max_score,
                completed_at=value.completed_at,
            ),
        )


def test_assessment_adapter_maps_only_the_public_event() -> None:
    values = AssessmentCompletionEvidenceSource(Assessment()).list_for_lesson(
        learner_id=LEARNER_ID,
        placement_id="intro-risk-return",
    )
    assert values == (source_evidence(),)
