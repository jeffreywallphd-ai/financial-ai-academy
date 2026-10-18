from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.audit.adapters import lineage_view_from_mapping
from financial_ai_academy.modules.audit.application.service import AuditService
from financial_ai_academy.modules.audit.domain import AccountableHistoryPurpose
from financial_ai_academy.modules.audit.public import (
    AuditError,
    AuditErrorCode,
    ReadPublishedLessonLineageRequest,
)


ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "contracts/compatibility/provenance/v1/approved"
REQUEST = ReadPublishedLessonLineageRequest(
    "intro-risk-return", "1.1.0", "7" * 64
)


def _lineage():
    return lineage_view_from_mapping(
        json.loads((FIXTURES / "lineage-view.json").read_text(encoding="utf-8"))
    )


def _service_with_lineage(lineage) -> AuditService:
    service = AuditService(object(), object(), object())  # type: ignore[arg-type]
    service.read_published_lesson_lineage = lambda _request: lineage  # type: ignore[method-assign]
    return service


def test_application_selects_review_and_export_purposes_without_new_state() -> None:
    service = _service_with_lineage(_lineage())

    review = service.read_published_lesson_accountable_history(REQUEST)
    first = service.export_published_lesson_accountable_history(REQUEST)
    second = service.export_published_lesson_accountable_history(REQUEST)

    assert review.purpose is AccountableHistoryPurpose.LEARNER_REVIEW
    assert first.document.purpose is AccountableHistoryPurpose.PORTABLE_EVIDENCE
    assert first == second
    serialized = json.dumps(first, default=str)
    for forbidden in (
        "learner_id",
        "answer",
        "score",
        "feedback",
        "provider",
        "storage_path",
    ):
        assert forbidden not in serialized


def test_inconsistent_lineage_maps_to_one_safe_audit_error() -> None:
    service = _service_with_lineage(replace(_lineage(), view_digest="f" * 64))

    with pytest.raises(AuditError) as invalid:
        service.read_published_lesson_accountable_history(REQUEST)

    assert invalid.value.code is AuditErrorCode.INCONSISTENT_EVIDENCE
    assert str(invalid.value) == "Accountable history facts are inconsistent."
    assert "private" not in str(invalid.value)
