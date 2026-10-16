from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.assessment.adapters.practice_contract import (
    ContractPracticeDefinitionAdapter,
)
from financial_ai_academy.modules.assessment.adapters.practice_progress_contract import (
    ContractPracticeProgressAdapter,
)
from financial_ai_academy.modules.assessment.adapters.practice_submission_contract import (
    ContractPracticeSubmissionAdapter,
)
from financial_ai_academy.modules.assessment.application.service import AssessmentService
from financial_ai_academy.modules.assessment.domain.practice import (
    PracticePresentationContext,
    PracticeScope,
)
from financial_ai_academy.modules.assessment.ports.gateways import (
    PlacedPracticeReference,
    PracticeDefinitionDocument,
)
from financial_ai_academy.modules.assessment.ports.repositories import (
    StoredPracticeCompletionEvent,
)
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    AssessmentErrorCode,
    ReadCompletedPracticesRequest,
)


ROOT = Path(__file__).resolve().parents[4]
SCHEMAS = ROOT / "contracts/learning/assessment/practice/v1"
CORPUS = ROOT / "contracts/compatibility/assessment-practice/v1/approved"
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
PLACEMENT_ID = "risk-return-practice-placement"


class CurriculumGateway:
    def resolve_practice(self, placement_id: str) -> PlacedPracticeReference:
        assert placement_id == PLACEMENT_ID
        return PlacedPracticeReference(
            placement_id=placement_id,
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest="a" * 64,
            practice_id="risk-return-practice",
            practice_version="1.0.0",
            definition_digest=(
                "82cdc82c402aacdb0070fb19671d896ae22a4c16d338ccbf27f02a51a396d527"
            ),
        )


class ContentGateway:
    def get_practice_exact(
        self, _reference: PlacedPracticeReference
    ) -> PracticeDefinitionDocument:
        return PracticeDefinitionDocument(
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest="a" * 64,
            practice_id="risk-return-practice",
            schema_version="1.0.0",
            file_digest="b" * 64,
            value=(CORPUS / "definition.json").read_bytes(),
        )


class Clock:
    def now(self) -> datetime:
        return datetime(2026, 10, 16, 15, 0, tzinfo=timezone.utc)


class Repository:
    def __init__(self, stored: StoredPracticeCompletionEvent) -> None:
        self.stored = stored

    def list_practice_completion_event_documents(
        self, *, learner_id: str, scope: PracticeScope
    ) -> tuple[StoredPracticeCompletionEvent, ...]:
        assert learner_id == LEARNER_ID
        assert scope.placement_id == PLACEMENT_ID
        return (self.stored,)


def build_service() -> tuple[AssessmentService, Repository]:
    definition = ContractPracticeDefinitionAdapter(SCHEMAS).parse(
        (CORPUS / "definition.json").read_bytes()
    )
    candidate = ContractPracticeSubmissionAdapter(SCHEMAS).parse_and_score(
        (CORPUS / "submission.json").read_bytes(),
        definition,
        PracticePresentationContext(
            placement_id=PLACEMENT_ID,
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest="a" * 64,
        ),
        learner_id=LEARNER_ID,
        attempt_id="33333333-3333-4333-8333-333333333333",
        evidence_id="44444444-4444-4444-8444-444444444444",
        event_id="55555555-5555-4555-8555-555555555555",
        submitted_at=datetime(2026, 10, 16, 15, 0, tzinfo=timezone.utc),
    )
    repository = Repository(
        StoredPracticeCompletionEvent(
            event_id=candidate.event_id,
            attempt_id=candidate.result.attempt_id,
            evidence_id=candidate.result.evidence_id,
            submission_id=candidate.result.submission_id,
            attempt_order=1,
            document=candidate.event,
            result=candidate.result,
        )
    )
    return (
        AssessmentService(
            CurriculumGateway(),  # type: ignore[arg-type]
            ContentGateway(),  # type: ignore[arg-type]
            object(),
            object(),
            repository,  # type: ignore[arg-type]
            Clock(),
            object(),
            ContractPracticeDefinitionAdapter(SCHEMAS),
            None,
            ContractPracticeProgressAdapter(SCHEMAS),
        ),
        repository,
    )


def test_history_source_correlates_safe_result_facts_without_private_values() -> None:
    service, _repository = build_service()

    source = service.read_practice_history_source(
        ReadCompletedPracticesRequest(
            learner_id=LEARNER_ID,
            placement_id=PLACEMENT_ID,
        )
    )

    assert source.placement_id == PLACEMENT_ID
    assert source.attempts[0].attempt_order == 1
    assert [item.correct for item in source.attempts[0].item_summaries] == [
        True,
        False,
        True,
    ]
    assert source.attempts[0].item_summaries[0].review_reference_ids == ()
    assert source.attempts[0].item_summaries[1].review_reference_ids == (
        "risk-return-review",
    )
    payload = json.dumps(asdict(source), default=str)
    for private_name in (
        "selected_option_id",
        "selected_option_ids",
        "entered_value",
        "feedback",
        "correct_answer",
    ):
        assert private_name not in payload


def test_history_source_fails_closed_when_result_and_event_do_not_correlate() -> None:
    service, repository = build_service()
    result = repository.stored.result
    assert result is not None
    repository.stored = StoredPracticeCompletionEvent(
        event_id=repository.stored.event_id,
        attempt_id=repository.stored.attempt_id,
        evidence_id=repository.stored.evidence_id,
        submission_id="99999999-9999-4999-8999-999999999999",
        attempt_order=1,
        document=repository.stored.document,
        result=result,
    )

    with pytest.raises(AssessmentError) as captured:
        service.read_practice_history_source(
            ReadCompletedPracticesRequest(
                learner_id=LEARNER_ID,
                placement_id=PLACEMENT_ID,
            )
        )

    assert captured.value.code is AssessmentErrorCode.UNAVAILABLE
    assert "99999999" not in str(captured.value.as_dict())
