from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from financial_ai_academy.modules.assessment.adapters.practice_contract import (
    ContractPracticeDefinitionAdapter,
)
from financial_ai_academy.modules.assessment.application.service import (
    AssessmentService,
)
from financial_ai_academy.modules.assessment.ports.gateways import (
    PlacedPracticeReference,
    PracticeDefinitionDocument,
)
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    AssessmentErrorCode,
    OpenPlacedPracticeRequest,
)


REPOSITORY = Path(__file__).resolve().parents[4]
SCHEMAS = REPOSITORY / "contracts/learning/assessment/practice/v1"
DEFINITION = (
    REPOSITORY
    / "contracts/compatibility/assessment-practice/v1/approved/definition.json"
)
DEFINITION_DIGEST = (
    "82cdc82c402aacdb0070fb19671d896ae22a4c16d338ccbf27f02a51a396d527"
)
PACKAGE_DIGEST = "a" * 64


class CurriculumGateway:
    def __init__(self) -> None:
        self.reference = PlacedPracticeReference(
            placement_id="intro-risk-return-primary",
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest=PACKAGE_DIGEST,
            practice_id="risk-return-practice",
            practice_version="1.0.0",
            definition_digest=DEFINITION_DIGEST,
        )

    def resolve_practice(self, placement_id: str) -> PlacedPracticeReference:
        assert placement_id == self.reference.placement_id
        return self.reference


class ContentGateway:
    def __init__(self) -> None:
        self.document = PracticeDefinitionDocument(
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest=PACKAGE_DIGEST,
            practice_id="risk-return-practice",
            schema_version="1.0.0",
            file_digest="b" * 64,
            value=DEFINITION.read_bytes(),
        )

    def get_practice_exact(
        self, _reference: PlacedPracticeReference
    ) -> PracticeDefinitionDocument:
        return self.document


class NoEvidenceRepository:
    def __init__(self) -> None:
        self.calls = 0

    def record_submission(self, *_args: object, **_kwargs: object) -> None:
        self.calls += 1
        raise AssertionError("Opening practice must not write evidence.")


def build_service(
    *,
    curriculum: CurriculumGateway | None = None,
    content: ContentGateway | None = None,
    repository: NoEvidenceRepository | None = None,
    with_parser: bool = True,
) -> tuple[AssessmentService, NoEvidenceRepository]:
    evidence = repository or NoEvidenceRepository()
    service = AssessmentService(
        curriculum or CurriculumGateway(),
        content or ContentGateway(),
        object(),  # Knowledge-check parser is outside this focused operation.
        object(),  # Completion-event parser is outside this focused operation.
        evidence,
        object(),  # Clock is not used while opening practice.
        object(),  # ID generation is not used while opening practice.
        (
            ContractPracticeDefinitionAdapter(SCHEMAS)
            if with_parser
            else None
        ),
    )
    return service, evidence


def test_open_practice_returns_all_closed_item_types_without_answers() -> None:
    service, repository = build_service()

    presentation = service.open_placed_practice(
        OpenPlacedPracticeRequest("intro-risk-return-primary")
    )

    assert presentation.definition_digest == DEFINITION_DIGEST
    assert [item.item_type for item in presentation.items] == [
        "single_select",
        "multiple_select",
        "numeric_entry",
    ]
    document = json.dumps(asdict(presentation), sort_keys=True)
    assert "correct_option_id" not in document
    assert "correct_option_ids" not in document
    assert '"answer"' not in document
    assert '"feedback"' not in document
    assert repository.calls == 0


def test_open_practice_rejects_stale_exact_reference_without_evidence() -> None:
    curriculum = CurriculumGateway()
    curriculum.reference = replace(
        curriculum.reference, definition_digest="c" * 64
    )
    service, repository = build_service(curriculum=curriculum)

    with pytest.raises(AssessmentError) as captured:
        service.open_placed_practice(
            OpenPlacedPracticeRequest("intro-risk-return-primary")
        )

    assert captured.value.code is AssessmentErrorCode.STALE_REFERENCE
    assert repository.calls == 0


def test_open_practice_rejects_malformed_private_definition() -> None:
    content = ContentGateway()
    content.document = replace(content.document, value=b"not-json")
    service, repository = build_service(content=content)

    with pytest.raises(AssessmentError) as captured:
        service.open_placed_practice(
            OpenPlacedPracticeRequest("intro-risk-return-primary")
        )

    assert captured.value.code is AssessmentErrorCode.INVALID_DEFINITION
    assert captured.value.diagnostic_code == "assessment.practice.schema_invalid"
    assert repository.calls == 0


def test_open_practice_requires_configured_contract_parser() -> None:
    service, repository = build_service(with_parser=False)

    with pytest.raises(AssessmentError) as captured:
        service.open_placed_practice(
            OpenPlacedPracticeRequest("intro-risk-return-primary")
        )

    assert captured.value.code is AssessmentErrorCode.UNAVAILABLE
    assert repository.calls == 0
