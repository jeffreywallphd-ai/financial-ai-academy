from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.assessment.adapters.contract import (
    ContractAssessmentDefinitionParser,
)
from financial_ai_academy.modules.assessment.adapters.event_contract import (
    ContractAssessmentEventParser,
)
from financial_ai_academy.modules.assessment.application.service import (
    AssessmentService,
)
from financial_ai_academy.modules.assessment.domain.models import (
    AssessmentSubmissionCandidate,
)
from financial_ai_academy.modules.assessment.ports.gateways import (
    DefinitionDocument,
    PlacedAssessmentReference,
)
from financial_ai_academy.modules.assessment.ports.repositories import (
    KnowledgeCheckAlreadyCompleted,
    SubmissionConflict,
)
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    AssessmentErrorCode,
    KnowledgeCheckPresentation,
    KnowledgeCheckResult,
    OpenPlacedKnowledgeCheckRequest,
    ReadCompletedKnowledgeChecksRequest,
    SubmitPlacedKnowledgeCheckRequest,
)


REPOSITORY = Path(__file__).resolve().parents[4]
CORPUS = REPOSITORY / "contracts/compatibility/assessment/v1/approved"
SCHEMAS = REPOSITORY / "contracts/learning/assessment/v1"
EVENT_SCHEMAS = REPOSITORY / "contracts/events/assessment/v1"
DEFINITION_DIGEST = (
    "98e941f9b53ef429cb6d359246ddb9812e354db2a9381a2ee180ed5758343d2b"
)
PACKAGE_DIGEST = (
    "7cf84bc2f7483d9131db315260b3812f3ea29821bf296571c0c7e38f05b536bc"
)
LEARNER_ID = "11111111-1111-4111-8111-111111111111"


class CurriculumGateway:
    def __init__(self) -> None:
        self.reference = PlacedAssessmentReference(
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
        )

    def resolve(self, placement_id: str) -> PlacedAssessmentReference:
        assert placement_id == self.reference.placement_id
        return self.reference


class ContentGateway:
    def get_exact(
        self, reference: PlacedAssessmentReference
    ) -> DefinitionDocument:
        return DefinitionDocument(
            package_id=reference.package_id,
            package_version=reference.package_version,
            package_digest=reference.package_digest,
            assessment_id=reference.assessment_id,
            schema_version="1.0.0",
            file_digest="4d011dafc90e746dd5b46c56d21ecf903e4fc193e51a78a900470cc8e4df51ba",
            value=(CORPUS / "definition.json").read_bytes(),
        )


class MemoryRepository:
    def __init__(self) -> None:
        self.by_submission: dict[tuple[str, str], tuple[str, KnowledgeCheckResult]] = {}
        self.completed: set[tuple[str, str, str, str]] = set()
        self.event_documents: list[dict[str, object]] = []

    def record_submission(
        self, candidate: AssessmentSubmissionCandidate
    ) -> tuple[KnowledgeCheckResult, bool]:
        result = candidate.result
        submission_key = (result.learner_id, result.submission_id)
        existing = self.by_submission.get(submission_key)
        if existing is not None:
            fingerprint, stored = existing
            if fingerprint != candidate.request_fingerprint:
                raise SubmissionConflict
            return stored, False
        completion_key = (
            result.learner_id,
            result.placement_id,
            result.assessment_id,
            result.assessment_version,
        )
        if completion_key in self.completed:
            raise KnowledgeCheckAlreadyCompleted
        self.by_submission[submission_key] = (
            candidate.request_fingerprint,
            result,
        )
        self.completed.add(completion_key)
        self.event_documents.append(dict(candidate.event))
        return result, True

    def list_completion_event_documents(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[dict[str, object], ...]:
        return tuple(
            document
            for document in self.event_documents
            if document["payload"]["learner_id"] == learner_id  # type: ignore[index]
            and document["payload"]["placement_id"] == placement_id  # type: ignore[index]
        )


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)


class SequentialIds:
    def __init__(self) -> None:
        self._value = 10

    def new(self) -> str:
        self._value += 1
        return f"00000000-0000-4000-8000-{self._value:012d}"


def build_service(
    repository: MemoryRepository | None = None,
    curriculum: CurriculumGateway | None = None,
) -> AssessmentService:
    return AssessmentService(
        curriculum or CurriculumGateway(),
        ContentGateway(),
        ContractAssessmentDefinitionParser(SCHEMAS),
        ContractAssessmentEventParser(EVENT_SCHEMAS),
        repository or MemoryRepository(),
        FixedClock(),
        SequentialIds(),
    )


def submission(
    presentation: KnowledgeCheckPresentation,
    *,
    submission_id: str = "22222222-2222-4222-8222-222222222222",
    option_id: str = "higher-potential-higher-uncertainty",
) -> SubmitPlacedKnowledgeCheckRequest:
    return SubmitPlacedKnowledgeCheckRequest(
        learner_id=LEARNER_ID,
        submission_id=submission_id,
        placement_id=presentation.placement_id,
        package_id=presentation.package_id,
        package_version=presentation.package_version,
        package_digest=presentation.package_digest,
        assessment_id=presentation.assessment_id,
        assessment_version=presentation.assessment_version,
        definition_digest=presentation.definition_digest,
        item_id=presentation.item_id,
        item_version=presentation.item_version,
        scoring_policy_id=presentation.scoring_policy_id,
        scoring_policy_version=presentation.scoring_policy_version,
        selected_option_id=option_id,
    )


def test_open_returns_only_safe_exact_presentation() -> None:
    presentation = build_service().open_placed_knowledge_check(
        OpenPlacedKnowledgeCheckRequest("intro-risk-return")
    )
    assert presentation.definition_digest == DEFINITION_DIGEST
    assert len(presentation.options) == 3
    assert not hasattr(presentation, "correct_option_id")
    assert not hasattr(presentation, "feedback")


@pytest.mark.parametrize(
    ("option_id", "score", "feedback_id"),
    [
        ("higher-potential-higher-uncertainty", 1, "risk-return-correct"),
        ("higher-risk-guarantees-return", 0, "risk-return-review"),
    ],
)
def test_deterministic_scoring_selects_reviewed_feedback(
    option_id: str, score: int, feedback_id: str
) -> None:
    service = build_service()
    presentation = service.open_placed_knowledge_check(
        OpenPlacedKnowledgeCheckRequest("intro-risk-return")
    )
    result = service.submit_placed_knowledge_check(
        submission(presentation, option_id=option_id)
    )
    assert result.score == score
    assert result.max_score == 1
    assert result.correct is (score == 1)
    assert result.feedback.feedback_id == feedback_id


def test_replay_conflict_and_one_completion_are_distinct() -> None:
    repository = MemoryRepository()
    service = build_service(repository)
    presentation = service.open_placed_knowledge_check(
        OpenPlacedKnowledgeCheckRequest("intro-risk-return")
    )
    request = submission(presentation)
    accepted = service.submit_placed_knowledge_check(request)
    replay = service.submit_placed_knowledge_check(request)
    assert replay == accepted
    with pytest.raises(AssessmentError) as conflict:
        service.submit_placed_knowledge_check(
            replace(request, selected_option_id="higher-risk-guarantees-return")
        )
    assert conflict.value.code is AssessmentErrorCode.CONFLICT
    with pytest.raises(AssessmentError) as complete:
        service.submit_placed_knowledge_check(
            replace(
                request,
                submission_id="33333333-3333-4333-8333-333333333333",
            )
        )
    assert complete.value.code is AssessmentErrorCode.ALREADY_COMPLETED
    assert len(repository.by_submission) == 1


def test_stale_reference_and_unknown_option_fail_before_evidence() -> None:
    repository = MemoryRepository()
    service = build_service(repository)
    presentation = service.open_placed_knowledge_check(
        OpenPlacedKnowledgeCheckRequest("intro-risk-return")
    )
    with pytest.raises(AssessmentError) as stale:
        service.submit_placed_knowledge_check(
            replace(submission(presentation), package_digest="a" * 64)
        )
    assert stale.value.code is AssessmentErrorCode.STALE_REFERENCE
    with pytest.raises(AssessmentError) as unknown:
        service.submit_placed_knowledge_check(
            submission(presentation, option_id="not-declared")
        )
    assert unknown.value.code is AssessmentErrorCode.UNKNOWN_OPTION
    assert repository.by_submission == {}


def test_completion_event_replay_is_exact_stable_and_context_filtered() -> None:
    repository = MemoryRepository()
    service = build_service(repository)
    presentation = service.open_placed_knowledge_check(
        OpenPlacedKnowledgeCheckRequest("intro-risk-return")
    )
    result = service.submit_placed_knowledge_check(submission(presentation))
    request = ReadCompletedKnowledgeChecksRequest(
        learner_id=LEARNER_ID,
        placement_id="intro-risk-return",
    )
    first = service.read_completed_knowledge_checks(request)
    second = service.read_completed_knowledge_checks(request)
    assert first == second
    assert len(first) == 1
    assert first[0].attempt_id == result.attempt_id
    assert first[0].evidence_id == result.evidence_id
    assert first[0].package_digest == PACKAGE_DIGEST
    assert service.read_completed_knowledge_checks(
        replace(request, placement_id="another-placement")
    ) == ()


def test_completion_event_replay_rejects_mismatched_context() -> None:
    repository = MemoryRepository()
    service = build_service(repository)
    presentation = service.open_placed_knowledge_check(
        OpenPlacedKnowledgeCheckRequest("intro-risk-return")
    )
    service.submit_placed_knowledge_check(submission(presentation))
    repository.event_documents[0]["payload"]["learner_id"] = (  # type: ignore[index]
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    )
    repository.list_completion_event_documents = lambda **_kwargs: tuple(  # type: ignore[method-assign]
        repository.event_documents
    )
    with pytest.raises(AssessmentError) as captured:
        service.read_completed_knowledge_checks(
            ReadCompletedKnowledgeChecksRequest(
                learner_id=LEARNER_ID,
                placement_id="intro-risk-return",
            )
        )
    assert captured.value.code is AssessmentErrorCode.UNAVAILABLE
    assert captured.value.diagnostic_code == "assessment.inconsistent_event"

