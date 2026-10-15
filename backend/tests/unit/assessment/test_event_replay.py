from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from financial_ai_academy.modules.assessment.adapters.event_contract import (
    ContractAssessmentEventParser,
)
from financial_ai_academy.modules.assessment.ports.event_parser import (
    EventParsingFailure,
)


REPOSITORY = Path(__file__).resolve().parents[4]
SCHEMAS = REPOSITORY / "contracts/events/assessment/v1"
EVENT = json.loads(
    (
        REPOSITORY
        / "contracts/compatibility/assessment/v1/approved/events/correct.json"
    ).read_text(encoding="utf-8")
)


def test_contract_event_parser_returns_typed_complete_provenance() -> None:
    parsed = ContractAssessmentEventParser(SCHEMAS).parse(EVENT)
    assert parsed.event_type == "assessment.knowledge-check.completed"
    assert parsed.event_version == "1.0.0"
    assert parsed.attempt_id == EVENT["aggregate"]["aggregate_id"]
    assert parsed.evidence_id == EVENT["source"]["evidence_id"]
    assert parsed.package_version == "1.1.0"
    assert parsed.assessment_version == "1.0.0"
    assert parsed.score == 1
    assert parsed.occurred_at == parsed.completed_at


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        (
            lambda value: value.update({"event_version": "2.0.0"}),
            "assessment.unsupported_event_version",
        ),
        (
            lambda value: value.update({"unexpected": "field"}),
            "assessment.schema_invalid",
        ),
        (
            lambda value: value.update(
                {"idempotency_key": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"}
            ),
            "assessment.inconsistent_event",
        ),
    ],
)
def test_contract_event_parser_rejects_unsupported_malformed_or_inconsistent(
    mutation: object,
    code: str,
) -> None:
    value = deepcopy(EVENT)
    mutation(value)  # type: ignore[operator]
    with pytest.raises(EventParsingFailure) as captured:
        ContractAssessmentEventParser(SCHEMAS).parse(value)
    assert captured.value.code == code
