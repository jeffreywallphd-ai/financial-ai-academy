from __future__ import annotations

import copy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from financial_ai_academy.modules.audit.adapters import (
    accountable_history_document_from_mapping,
    accountable_history_payload,
    lineage_view_from_mapping,
    portable_evidence_from_mapping,
    portable_evidence_payload,
)
from financial_ai_academy.modules.audit.domain import (
    AccountableHistoryDiagnosticCode,
    AccountableHistoryPurpose,
    AccountableHistoryState,
    IncompleteReason,
    InvalidAccountableHistory,
    LineageEdge,
    LineageNode,
    LineageRoot,
    OwnerModule,
    ProvenanceEnvelope,
    ProvenanceSource,
    RelationKind,
    ResourceKind,
    ResourceReference,
    RootKind,
    ValidationStatus,
    build_lineage_view,
    build_portable_evidence,
    compose_accountable_history,
)
ROOT = Path(__file__).resolve().parents[4]
PROVENANCE = ROOT / "contracts/compatibility/provenance/v1/approved"
ACCOUNTABLE_HISTORY = ROOT / "contracts/accountable-history/v1"


def _lineage(name: str):
    return lineage_view_from_mapping(
        json.loads((PROVENANCE / name).read_text(encoding="utf-8"))
    )


def _schema(name: str) -> dict[str, object]:
    return json.loads((ACCOUNTABLE_HISTORY / name).read_text(encoding="utf-8"))


def _assert_document_contract(value: dict[str, object]) -> None:
    errors = list(
        Draft202012Validator(
            _schema("document.schema.json"), format_checker=FormatChecker()
        ).iter_errors(value)
    )
    assert not errors, [error.message for error in errors]


def _assert_export_contract(value: dict[str, object]) -> None:
    document = _schema("document.schema.json")
    registry = Registry().with_resource(
        str(document["$id"]), Resource.from_contents(document)
    )
    errors = list(
        Draft202012Validator(
            _schema("export.schema.json"),
            format_checker=FormatChecker(),
            registry=registry,
        ).iter_errors(value)
    )
    assert not errors, [error.message for error in errors]


def _lesson_lineage(
    source_count: int,
    *,
    offset: timezone = timezone.utc,
    local_hour: int = 12,
    microsecond: int = 0,
):
    recorded_at = datetime(
        2026, 8, 5, local_hour, microsecond=microsecond, tzinfo=offset
    )
    lesson = ResourceReference(
        owner_module=OwnerModule.CONTENT,
        resource_kind=ResourceKind.PUBLISHED_LESSON,
        resource_id="leçon-diversification-été",
        resource_version="1.0.0",
        occurrence=None,
        integrity_digest="8" * 64,
        recorded_at=recorded_at,
        validation_status=ValidationStatus.VALIDATED,
    )
    sources = tuple(
        ResourceReference(
            owner_module=OwnerModule.CONTENT,
            resource_kind=ResourceKind.EDUCATIONAL_SOURCE,
            resource_id=f"source-économie-{index}",
            resource_version=f"2026.08.{index + 1:02}",
            occurrence=None,
            integrity_digest=f"{(index % 9) + 1}" * 64,
            recorded_at=recorded_at - timedelta(minutes=index + 1),
            validation_status=ValidationStatus.VALIDATED,
        )
        for index in range(source_count)
    )
    nodes = (
        LineageNode(
            "lesson",
            ProvenanceEnvelope(
                schema_version="1.0.0",
                resource=lesson,
                producer_id="content.lesson-package",
                producer_version="1.0.0",
                sources=tuple(
                    ProvenanceSource(RelationKind.PUBLISHED_FROM, source)
                    for source in sources
                ),
            ),
        ),
        *(
            LineageNode(
                f"source-{index}",
                ProvenanceEnvelope(
                    schema_version="1.0.0",
                    resource=source,
                    producer_id="content.source",
                    producer_version="1.0.0",
                    sources=(),
                ),
            )
            for index, source in enumerate(sources)
        ),
    )
    return build_lineage_view(
        root=LineageRoot(RootKind.PUBLISHED_LESSON, lesson),
        nodes=nodes,
        edges=tuple(
            LineageEdge("lesson", f"source-{index}", RelationKind.PUBLISHED_FROM)
            for index in range(source_count)
        ),
    )


@pytest.mark.parametrize("source_count", (0, 1, 7))
def test_valid_lesson_counts_use_truthful_generic_copy_and_exact_contract(
    source_count: int,
) -> None:
    document = compose_accountable_history(
        _lesson_lineage(source_count),
        AccountableHistoryPurpose.LEARNER_REVIEW,
    )
    payload = accountable_history_payload(document)

    assert document.state is AccountableHistoryState.VALID
    assert document.summary == "This view shows the source and history available for the lesson."
    assert len(document.entries) == source_count + 1
    assert payload["history_digest"] == document.history_digest
    assert accountable_history_document_from_mapping(payload) == document
    _assert_document_contract(payload)


def test_completion_history_and_export_are_deterministic_and_confidential() -> None:
    lineage = _lineage("lineage-view.json")
    review = compose_accountable_history(
        lineage, AccountableHistoryPurpose.LEARNER_REVIEW
    )
    first = build_portable_evidence(lineage)
    second = build_portable_evidence(lineage)
    review_payload = accountable_history_payload(review)
    export_payload = portable_evidence_payload(first)

    assert first == second
    assert review.root.resource_id == "evidence-check-1"
    assert [entry.resource_kind for entry in review.entries] == [
        ResourceKind.COMPLETION_EVIDENCE,
        ResourceKind.KNOWLEDGE_CHECK_EVENT,
        ResourceKind.AUDIT_REFERENCE,
        ResourceKind.ASSESSMENT_DEFINITION,
        ResourceKind.PUBLISHED_LESSON,
        ResourceKind.EDUCATIONAL_SOURCE,
    ]
    assert first.filename_stem.startswith("completion-")
    assert first.filename_stem.isascii()
    assert portable_evidence_from_mapping(export_payload) == first
    _assert_document_contract(review_payload)
    _assert_export_contract(export_payload)
    serialized = json.dumps(export_payload, ensure_ascii=False)
    for private in ("learner_id", "answer", "score", "feedback", "storage_path"):
        assert private not in serialized


def test_incomplete_lineage_maps_exact_gap_and_safe_diagnostic() -> None:
    document = compose_accountable_history(
        _lineage("incomplete-lineage-view.json"),
        AccountableHistoryPurpose.LEARNER_REVIEW,
    )
    payload = accountable_history_payload(document)

    assert document.state is AccountableHistoryState.INCOMPLETE
    assert document.summary == "Some source history for this lesson is incomplete."
    assert document.missing_links[0].reason is IncompleteReason.UNAVAILABLE
    assert (
        document.diagnostics[0].code
        is AccountableHistoryDiagnosticCode.OWNER_UNAVAILABLE
    )
    assert "Traceback" not in json.dumps(payload)
    _assert_document_contract(payload)


def test_mapping_is_closed_and_copy_cannot_cross_purpose_or_root() -> None:
    document = compose_accountable_history(
        _lesson_lineage(1), AccountableHistoryPurpose.LEARNER_REVIEW
    )
    payload = accountable_history_payload(document)

    unknown = copy.deepcopy(payload)
    unknown["storage_path"] = "C:/private/history.json"
    with pytest.raises(InvalidAccountableHistory):
        accountable_history_document_from_mapping(unknown)

    wrong_title = copy.deepcopy(payload)
    wrong_title["title"] = "Portable evidence record"
    with pytest.raises(InvalidAccountableHistory):
        accountable_history_document_from_mapping(wrong_title)

    wrong_summary = copy.deepcopy(payload)
    wrong_summary["summary"] = (
        "This completion is linked to the check, the published lesson, and its audit record."
    )
    with pytest.raises(InvalidAccountableHistory):
        accountable_history_document_from_mapping(wrong_summary)

    wrong_entry_copy = copy.deepcopy(payload)
    wrong_entry_copy["entries"][0]["explanation"] = "The check belongs to this lesson."
    with pytest.raises(InvalidAccountableHistory):
        accountable_history_document_from_mapping(wrong_entry_copy)

    invalid_version = copy.deepcopy(payload)
    invalid_version["root"]["resource_version"] = "bad version"
    invalid_version["entries"][0]["resource_version"] = "bad version"
    with pytest.raises(InvalidAccountableHistory):
        accountable_history_document_from_mapping(invalid_version)

    false_redaction_count = copy.deepcopy(payload)
    false_redaction_count["redactions"][0]["count"] = 999
    with pytest.raises(InvalidAccountableHistory):
        accountable_history_document_from_mapping(false_redaction_count)


def test_changed_lineage_digest_fails_without_partial_history() -> None:
    lineage = _lineage("lineage-view.json")
    changed = replace(lineage, view_digest="f" * 64)

    with pytest.raises(InvalidAccountableHistory, match="inconsistent") as invalid:
        compose_accountable_history(
            changed, AccountableHistoryPurpose.LEARNER_REVIEW
        )

    assert invalid.value.reference == "lineage"
    assert "private" not in str(invalid.value)


def test_equivalent_offsets_and_fractional_instants_canonicalize_identically() -> None:
    utc_lineage = _lesson_lineage(3, microsecond=100_000)
    offset_lineage = _lesson_lineage(
        3,
        offset=timezone(timedelta(hours=-4)),
        local_hour=8,
        microsecond=100_000,
    )

    utc = build_portable_evidence(utc_lineage)
    equivalent = build_portable_evidence(offset_lineage)

    assert utc == equivalent
    assert portable_evidence_payload(utc)["exported_at"].endswith(".100000Z")


def test_domain_and_adapter_sources_have_no_outer_layer_imports() -> None:
    domain_source = (
        ROOT
        / "backend/src/financial_ai_academy/modules/audit/domain/accountable_history.py"
    ).read_text(encoding="utf-8")
    adapter_source = (
        ROOT
        / "backend/src/financial_ai_academy/modules/audit/adapters/accountable_history_contract.py"
    ).read_text(encoding="utf-8")
    forbidden = (
        "fastapi",
        "sqlalchemy",
        "modules.identity",
        "modules.content",
        "modules.assessment",
        "application.",
        "requests",
        "httpx",
    )

    assert not any(marker in domain_source for marker in forbidden)
    assert not any(marker in adapter_source for marker in forbidden)
