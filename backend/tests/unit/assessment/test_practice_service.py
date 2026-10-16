from __future__ import annotations

import json
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.assessment.adapters.practice_contract import (
    ContractPracticeDefinitionAdapter,
)
from financial_ai_academy.modules.assessment.adapters.practice_submission_contract import (
    ContractPracticeSubmissionAdapter,
)
from financial_ai_academy.modules.assessment.application.service import (
    AssessmentService,
)
from financial_ai_academy.modules.assessment.ports.gateways import (
    PlacedPracticeReference,
    PracticeDefinitionDocument,
)
from financial_ai_academy.modules.assessment.ports.repositories import (
    PracticeAlreadyCompleted,
    PracticeAttemptLimitReached,
    PracticeSubmissionConflict,
)
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    AssessmentErrorCode,
    OpenPlacedPracticeRequest,
    SubmitPlacedPracticeRequest,
)


REPOSITORY = Path(__file__).resolve().parents[4]
SCHEMAS = REPOSITORY / "contracts/learning/assessment/practice/v1"
DEFINITION = (
    REPOSITORY
    / "contracts/compatibility/assessment-practice/v1/approved/definition.json"
)
SUBMISSION = (
    REPOSITORY
    / "contracts/compatibility/assessment-practice/v1/approved/submission.json"
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

    def record_practice_submission(
        self, *_args: object, **_kwargs: object
    ) -> None:
        self.calls += 1
        raise AssertionError("Opening practice must not write evidence.")


class PracticeRepository:
    def __init__(self, failure: Exception | None = None) -> None:
        self.failure = failure
        self.candidates: list[object] = []

    def record_practice_submission(
        self, candidate: object, *, max_attempts: int
    ) -> tuple[object, bool]:
        self.candidates.append(candidate)
        assert max_attempts == 3
        if self.failure is not None:
            raise self.failure
        return candidate.result, True  # type: ignore[attr-defined]


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 10, 16, 15, 0, tzinfo=timezone.utc)


class SequentialIds:
    def __init__(self) -> None:
        self.value = 100

    def new(self) -> str:
        self.value += 1
        return f"00000000-0000-4000-8000-{self.value:012d}"


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


def build_submission_service(
    repository: PracticeRepository | None = None,
) -> tuple[AssessmentService, PracticeRepository]:
    evidence = repository or PracticeRepository()
    service = AssessmentService(
        CurriculumGateway(),
        ContentGateway(),
        object(),
        object(),
        evidence,  # type: ignore[arg-type]
        FixedClock(),
        SequentialIds(),
        ContractPracticeDefinitionAdapter(SCHEMAS),
        ContractPracticeSubmissionAdapter(SCHEMAS),
    )
    return service, evidence


def submission_bytes(**changes: object) -> bytes:
    document = json.loads(SUBMISSION.read_text(encoding="utf-8"))
    document["placement_id"] = "intro-risk-return-primary"
    document.update(changes)
    return json.dumps(document).encode("utf-8")


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


def test_submit_practice_uses_server_metadata_and_public_application_seam() -> None:
    service, repository = build_submission_service()

    result = service.submit_placed_practice(
        SubmitPlacedPracticeRequest(
            learner_id="11111111-1111-4111-8111-111111111111",
            placement_id="intro-risk-return-primary",
            submission=submission_bytes(),
        )
    )

    assert result.score == 2
    assert result.max_score == 3
    assert result.outcome == "review_needed"
    assert result.attempt_id.endswith("000000000101")
    assert result.evidence_id.endswith("000000000102")
    assert result.submitted_at == FixedClock().now()
    assert [item.response.item_id for item in result.item_results] == [
        "risk-meaning",
        "diversification-actions",
        "simple-growth",
    ]
    assert len(repository.candidates) == 1


@pytest.mark.parametrize(
    ("failure", "expected"),
    [
        (
            PracticeSubmissionConflict("sentinel-secret-response"),
            AssessmentErrorCode.CONFLICT,
        ),
        (
            PracticeAlreadyCompleted("sentinel-secret-history"),
            AssessmentErrorCode.ALREADY_COMPLETED,
        ),
        (
            PracticeAttemptLimitReached("sentinel-secret-limit"),
            AssessmentErrorCode.ATTEMPT_LIMIT_REACHED,
        ),
    ],
)
def test_submit_practice_maps_repository_denials_without_leaking_details(
    failure: Exception, expected: AssessmentErrorCode
) -> None:
    service, repository = build_submission_service(
        PracticeRepository(failure)
    )

    with pytest.raises(AssessmentError) as captured:
        service.submit_placed_practice(
            SubmitPlacedPracticeRequest(
                learner_id="11111111-1111-4111-8111-111111111111",
                placement_id="intro-risk-return-primary",
                submission=submission_bytes(),
            )
        )

    assert captured.value.code is expected
    assert "sentinel-secret" not in str(captured.value.as_dict())
    assert len(repository.candidates) == 1


def test_submit_practice_rejects_stale_body_before_persistence() -> None:
    service, repository = build_submission_service()

    with pytest.raises(AssessmentError) as captured:
        service.submit_placed_practice(
            SubmitPlacedPracticeRequest(
                learner_id="11111111-1111-4111-8111-111111111111",
                placement_id="intro-risk-return-primary",
                submission=submission_bytes(definition_digest="c" * 64),
            )
        )

    assert captured.value.code is AssessmentErrorCode.STALE_REFERENCE
    assert repository.candidates == []


def test_submit_practice_rejects_untrusted_learner_before_resolution() -> None:
    service, repository = build_submission_service()

    with pytest.raises(AssessmentError) as captured:
        service.submit_placed_practice(
            SubmitPlacedPracticeRequest(
                learner_id="caller-selected",
                placement_id="intro-risk-return-primary",
                submission=submission_bytes(),
            )
        )

    assert captured.value.code is AssessmentErrorCode.UNAUTHORIZED_CONTEXT
    assert repository.candidates == []
