from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.assessment.adapters.practice_contract import (
    ContractPracticeDefinitionAdapter,
)
from financial_ai_academy.modules.assessment.adapters.practice_progress_contract import (
    ContractPracticeProgressAdapter,
)
from financial_ai_academy.modules.assessment.application.service import (
    AssessmentService,
)
from financial_ai_academy.modules.assessment.domain.practice import (
    PracticeDraft,
    PracticeScope,
)
from financial_ai_academy.modules.assessment.ports.gateways import (
    PlacedPracticeReference,
    PracticeDefinitionDocument,
)
from financial_ai_academy.modules.assessment.ports.practice_progress import (
    PracticeProgressFailure,
)
from financial_ai_academy.modules.assessment.ports.repositories import (
    StoredPracticeCompletionEvent,
)
from financial_ai_academy.modules.assessment.public import (
    ReadCompletedPracticesRequest,
    ReadPlacedPracticeProgressRequest,
    SavePlacedPracticeDraftRequest,
)


REPOSITORY = Path(__file__).resolve().parents[4]
SCHEMAS = REPOSITORY / "contracts/learning/assessment/practice/v1"
CORPUS = REPOSITORY / "contracts/compatibility/assessment-practice/v1/approved"
LEARNER_ID = "11111111-1111-4111-8111-111111111111"


def load(name: str) -> dict[str, object]:
    return json.loads((CORPUS / name).read_text(encoding="utf-8"))


class CurriculumGateway:
    def resolve_practice(self, placement_id: str) -> PlacedPracticeReference:
        assert placement_id == "risk-return-practice-placement"
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
        return datetime(2026, 10, 16, 16, 0, tzinfo=timezone.utc)


class ProgressRepository:
    def __init__(self, adapter: ContractPracticeProgressAdapter) -> None:
        self.adapter = adapter
        self.draft: PracticeDraft | None = None
        self.attempts = 1
        self.events = (
            StoredPracticeCompletionEvent(
                event_id="55555555-5555-4555-8555-555555555555",
                attempt_id="33333333-3333-4333-8333-333333333333",
                evidence_id="44444444-4444-4444-8444-444444444444",
                submission_id="22222222-2222-4222-8222-222222222222",
                attempt_order=1,
                document=load("completion-event.json"),
            ),
        )

    def save_practice_draft(
        self, *, learner_id: str, draft: object, saved_at: datetime
    ) -> PracticeDraft:
        assert learner_id == LEARNER_ID
        self.draft = PracticeDraft(
            scope=draft.scope,
            responses=draft.responses,
            revision=1,
            saved_at=saved_at,
            response_fingerprint=draft.response_fingerprint,
        )
        return self.draft

    def read_practice_draft(
        self, *, learner_id: str, scope: PracticeScope
    ) -> PracticeDraft | None:
        assert learner_id == LEARNER_ID
        assert self.draft is None or self.draft.scope == scope
        return self.draft

    def count_practice_attempts(
        self, *, learner_id: str, scope: PracticeScope
    ) -> int:
        assert learner_id == LEARNER_ID
        assert scope.placement_id == "risk-return-practice-placement"
        return self.attempts

    def list_practice_completion_event_documents(
        self, *, learner_id: str, scope: PracticeScope
    ) -> tuple[StoredPracticeCompletionEvent, ...]:
        assert learner_id == LEARNER_ID
        assert scope.placement_id == "risk-return-practice-placement"
        return self.events


def build_service() -> tuple[AssessmentService, ProgressRepository]:
    adapter = ContractPracticeProgressAdapter(SCHEMAS)
    repository = ProgressRepository(adapter)
    service = AssessmentService(
        CurriculumGateway(),  # type: ignore[arg-type]
        ContentGateway(),  # type: ignore[arg-type]
        object(),
        object(),
        repository,  # type: ignore[arg-type]
        Clock(),
        object(),
        ContractPracticeDefinitionAdapter(SCHEMAS),
        None,
        adapter,
    )
    return service, repository


def test_draft_adapter_accepts_partial_order_variation_without_private_data() -> None:
    adapter = ContractPracticeProgressAdapter(SCHEMAS)
    definition = ContractPracticeDefinitionAdapter(SCHEMAS).parse(
        (CORPUS / "definition.json").read_bytes()
    )
    context = CurriculumGateway().resolve_practice(
        "risk-return-practice-placement"
    )
    document = load("draft-save.json")
    first = adapter.parse_draft_save(
        json.dumps(document).encode(),
        definition,
        adapter_context(context),
    )
    document["responses"].reverse()  # type: ignore[union-attr]
    second = adapter.parse_draft_save(
        json.dumps(document).encode(),
        definition,
        adapter_context(context),
    )

    assert first.response_fingerprint == second.response_fingerprint
    assert len(first.responses) == 2
    assert "correct" not in json.dumps(adapter.response_document(first.responses[0]))


def test_draft_adapter_rejects_unknown_or_private_response_fields() -> None:
    adapter = ContractPracticeProgressAdapter(SCHEMAS)
    definition = ContractPracticeDefinitionAdapter(SCHEMAS).parse(
        (CORPUS / "definition.json").read_bytes()
    )
    reference = CurriculumGateway().resolve_practice(
        "risk-return-practice-placement"
    )
    document = load("draft-save.json")
    document["responses"][0]["correct"] = True  # type: ignore[index]

    with pytest.raises(PracticeProgressFailure) as captured:
        adapter.parse_draft_save(
            json.dumps(document).encode(),
            definition,
            adapter_context(reference),
        )

    assert captured.value.code == "assessment.practice.schema_invalid"


def test_application_progress_seam_is_transport_neutral_and_typed() -> None:
    service, repository = build_service()
    draft = service.save_placed_practice_draft(
        SavePlacedPracticeDraftRequest(
            learner_id=LEARNER_ID,
            placement_id="risk-return-practice-placement",
            draft=(CORPUS / "draft-save.json").read_bytes(),
        )
    )
    reopened = service.read_placed_practice_draft(
        ReadPlacedPracticeProgressRequest(
            learner_id=LEARNER_ID,
            placement_id="risk-return-practice-placement",
        )
    )
    retry = service.read_placed_practice_retry_state(
        ReadPlacedPracticeProgressRequest(
            learner_id=LEARNER_ID,
            placement_id="risk-return-practice-placement",
        )
    )
    history = service.read_completed_practices(
        ReadCompletedPracticesRequest(
            learner_id=LEARNER_ID,
            placement_id="risk-return-practice-placement",
        )
    )

    assert reopened == draft == repository.draft
    assert (retry.attempts_used, retry.attempts_remaining, retry.can_retry) == (
        1,
        2,
        True,
    )
    assert history[0].attempt_order == 1
    assert history[0].event.score == 2
    assert not hasattr(history[0].event.item_scores[0], "selected_option_id")


def test_completion_event_parser_rejects_inconsistent_evidence_identity() -> None:
    adapter = ContractPracticeProgressAdapter(SCHEMAS)
    event = copy.deepcopy(load("completion-event.json"))
    event["source"]["evidence_id"] = "99999999-9999-4999-8999-999999999999"  # type: ignore[index]

    with pytest.raises(PracticeProgressFailure) as captured:
        adapter.parse_completion_event(event)

    assert captured.value.code == "assessment.practice.inconsistent_event"


def test_completion_event_parser_rejects_mismatched_item_policy() -> None:
    adapter = ContractPracticeProgressAdapter(SCHEMAS)
    event = copy.deepcopy(load("completion-event.json"))
    event["payload"]["item_scores"][0]["scoring_policy_id"] = (  # type: ignore[index]
        "numeric-exact-or-inclusive-range"
    )

    with pytest.raises(PracticeProgressFailure) as captured:
        adapter.parse_completion_event(event)

    assert captured.value.code == "assessment.practice.inconsistent_event"


@pytest.mark.parametrize(
    ("field", "changed"),
    (
        ("event_id", "99999999-9999-4999-8999-999999999991"),
        ("attempt_id", "99999999-9999-4999-8999-999999999992"),
        ("evidence_id", "99999999-9999-4999-8999-999999999993"),
        ("submission_id", "99999999-9999-4999-8999-999999999994"),
    ),
)
def test_application_replay_rejects_payload_identity_drift(
    field: str, changed: str
) -> None:
    service, repository = build_service()
    stored = repository.events[0]
    document = copy.deepcopy(stored.document)
    if field == "event_id":
        document["event_id"] = changed
    elif field == "attempt_id":
        document["aggregate"]["aggregate_id"] = changed  # type: ignore[index]
    elif field == "evidence_id":
        document["source"]["evidence_id"] = changed  # type: ignore[index]
        document["idempotency_key"] = changed
    else:
        document["payload"]["submission_id"] = changed  # type: ignore[index]
    repository.events = (
        StoredPracticeCompletionEvent(
            event_id=stored.event_id,
            attempt_id=stored.attempt_id,
            evidence_id=stored.evidence_id,
            submission_id=stored.submission_id,
            attempt_order=stored.attempt_order,
            document=document,
        ),
    )

    from financial_ai_academy.modules.assessment.public import (
        AssessmentError,
        AssessmentErrorCode,
    )

    with pytest.raises(AssessmentError) as captured:
        service.read_completed_practices(
            ReadCompletedPracticesRequest(
                learner_id=LEARNER_ID,
                placement_id="risk-return-practice-placement",
            )
        )

    assert captured.value.code is AssessmentErrorCode.UNAVAILABLE
    assert changed not in str(captured.value.as_dict())


def adapter_context(reference: PlacedPracticeReference):
    from financial_ai_academy.modules.assessment.domain.practice import (
        PracticePresentationContext,
    )

    return PracticePresentationContext(
        placement_id=reference.placement_id,
        package_id=reference.package_id,
        package_version=reference.package_version,
        package_digest=reference.package_digest,
    )
