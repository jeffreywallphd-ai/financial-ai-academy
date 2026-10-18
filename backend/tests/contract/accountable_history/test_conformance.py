from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from financial_ai_academy.modules.audit.adapters import (
    accountable_history_payload as product_document_payload,
    lineage_view_from_mapping,
    portable_evidence_payload as product_export_payload,
)
from financial_ai_academy.modules.audit.domain import (
    AccountableHistoryPurpose,
    build_portable_evidence,
    compose_accountable_history,
)

from .runner import (
    AccountableHistoryContractValidator,
    ConformanceFailure,
    approved_records,
    default_corpus_dir,
    default_schema_dir,
    export_filename_stem,
    history_digest,
    provenance_fingerprints,
)


CORPUS = default_corpus_dir()
REPOSITORY = Path(__file__).resolve().parents[4]


def _at(value: dict[str, Any], path: list[object]) -> Any:
    current: Any = value
    for part in path:
        current = current[part]
    return current


def _apply(value: dict[str, Any], operation: dict[str, Any]) -> None:
    current: Any = value
    path = operation["path"]
    for part in path[:-1]:
        current = current[part]
    key = path[-1]
    if operation["op"] == "set":
        current[key] = operation["value"]
    elif operation["op"] == "remove":
        del current[key]
    elif operation["op"] == "repeat":
        original = list(_at(value, path))
        current[key] = [copy.deepcopy(original[index % len(original)]) for index in range(operation["count"])]
    else:
        raise AssertionError(operation["op"])


def test_accountable_history_schemas_are_valid_draft_2020_12() -> None:
    schemas = list(default_schema_dir().glob("*.schema.json"))
    assert {path.name for path in schemas} == {
        "request.schema.json",
        "document.schema.json",
        "export.schema.json",
    }
    for path in schemas:
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_two_closed_requests_have_no_caller_selected_identity_or_purpose() -> None:
    validator = AccountableHistoryContractValidator()
    validator.validate_request({
        "schema_version": "1.0.0",
        "root_kind": "published_lesson",
        "package_id": "leçon-diversification-été",
        "package_version": "1.0.0",
        "package_digest": "a" * 64,
    })
    validator.validate_request({
        "schema_version": "1.0.0",
        "root_kind": "knowledge_check_completion",
        "placement_id": "placement-risk-return",
        "evidence_id": "evidence-check-1",
        "occurrence": 1,
    })
    for added in (
        {"purpose": "support_investigation"},
        {"learner_id": "private-learner"},
        {"tenant_id": "private-tenant"},
        {"fields": ["answer"]},
    ):
        request = {
            "schema_version": "1.0.0",
            "root_kind": "published_lesson",
            "package_id": "intro-risk-return",
            "package_version": "1.0.0",
            "package_digest": "a" * 64,
            **added,
        }
        with pytest.raises(ConformanceFailure):
            validator.validate_request(request)


def test_approved_documents_and_export_match_canonical_vectors() -> None:
    lesson, completion, incomplete, portable = approved_records()
    validator = AccountableHistoryContractValidator()
    admitted = (
        validator.validate_document(lesson),
        validator.validate_document(completion),
        validator.validate_document(incomplete),
        validator.validate_export(portable),
    )
    vector = json.loads((CORPUS / "vectors/canonicalization.json").read_text(encoding="utf-8"))
    assert [value["history_digest"] for value in admitted[:3]] == [
        vector["lesson_review_digest"],
        vector["completion_review_digest"],
        vector["incomplete_review_digest"],
    ]
    assert admitted[3]["document_digest"] == vector["portable_evidence_document_digest"]


def test_product_core_matches_frozen_canonicalization_and_semantics() -> None:
    lineage_value = json.loads(
        (
            REPOSITORY
            / "contracts/compatibility/provenance/v1/approved/lineage-view.json"
        ).read_text(encoding="utf-8")
    )
    lineage = lineage_view_from_mapping(lineage_value)
    document = compose_accountable_history(
        lineage, AccountableHistoryPurpose.LEARNER_REVIEW
    )
    portable = build_portable_evidence(lineage)
    document_value = product_document_payload(document)
    portable_value = product_export_payload(portable)
    validator = AccountableHistoryContractValidator()

    admitted_document = validator.validate_document(document_value)
    admitted_export = validator.validate_export(portable_value)

    assert admitted_document["history_digest"] == history_digest(document_value)
    assert admitted_export["document_digest"] == portable.document_digest


def test_equivalent_order_and_time_offsets_project_one_document() -> None:
    _, _, _, portable = approved_records()
    reordered = copy.deepcopy(portable)
    reordered["document"]["entries"].reverse()
    reordered["document"]["transformations"].reverse()
    reordered["document"]["redactions"].reverse()
    validator = AccountableHistoryContractValidator()
    expected = validator.validate_export(portable)
    assert validator.validate_export(reordered) == expected


def test_valid_counts_unicode_and_redaction_sets_are_not_fixture_bound() -> None:
    lesson, _, incomplete, _ = approved_records()
    validator = AccountableHistoryContractValidator()
    varied = copy.deepcopy(lesson)
    varied["redactions"] = [{"category": "protected_content", "count": 7}]
    varied["history_digest"] = history_digest(varied)
    assert validator.validate_document(varied)["redactions"] == varied["redactions"]
    assert validator.validate_document(incomplete)["root"]["resource_id"] == "leçon-diversification-été"


def test_portable_filename_is_total_for_valid_unicode_root_identity() -> None:
    _, _, _, portable = approved_records()
    varied = copy.deepcopy(portable)
    document = varied["document"]
    unicode_identity = "évidence-été-東京"
    document["root"]["resource_id"] = unicode_identity
    document["entries"][0]["resource_id"] = unicode_identity
    document["history_digest"] = history_digest(document)
    varied["document_digest"] = document["history_digest"]
    varied["filename_stem"] = export_filename_stem(document)

    admitted = AccountableHistoryContractValidator().validate_export(varied)

    assert admitted["filename_stem"].startswith("completion-")
    assert admitted["filename_stem"].isascii()
    assert len(admitted["filename_stem"]) == len("completion-") + 16


def test_export_uses_instant_order_not_fractional_timestamp_text_order() -> None:
    _, _, _, portable = approved_records()
    varied = copy.deepcopy(portable)
    document = varied["document"]
    document["entries"][0]["recorded_at"] = "2026-08-05T16:15:01.100000Z"
    document["entries"][1]["recorded_at"] = "2026-08-05T16:15:01Z"
    document["history_digest"] = history_digest(document)
    varied["document_digest"] = document["history_digest"]
    varied["exported_at"] = "2026-08-05T16:15:01.100000Z"

    admitted = AccountableHistoryContractValidator().validate_export(varied)

    assert admitted["exported_at"] == "2026-08-05T16:15:01.100000Z"


def test_primary_display_copy_uses_plain_nontechnical_language() -> None:
    jargon = {"provenance", "schema", "digest", "resource_id", "owner_module", "validation_status"}
    for record in approved_records()[:3]:
        display = [record["title"], record["summary"]]
        display.extend(item[field] for item in record["entries"] for field in ("title", "explanation"))
        display.extend(item["explanation"] for item in record["missing_links"])
        display.extend(item["explanation"] for item in record["diagnostics"])
        words = " ".join(display).casefold()
        assert not any(term in words for term in jargon)


def test_reviewed_entry_copy_is_correlated_to_root_and_links() -> None:
    lesson, _, _, _ = approved_records()
    mismatched = copy.deepcopy(lesson)
    mismatched["entries"][1]["explanation"] = "The check belongs to this lesson."

    with pytest.raises(ConformanceFailure) as invalid:
        AccountableHistoryContractValidator().validate_document(
            mismatched, verify_digest=False
        )

    assert invalid.value.diagnostic.code == "accountable_history.display_text_invalid"


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_denial_corpus_fails_closed_with_bounded_diagnostics(case: dict[str, Any]) -> None:
    lesson, completion, incomplete, portable = approved_records()
    values = {
        "lesson_review": lesson,
        "completion_review": completion,
        "incomplete_review": incomplete,
        "portable_evidence": portable,
    }
    target = copy.deepcopy(values[case["target"]])
    for operation in case["ops"]:
        _apply(target, operation)
    validator = AccountableHistoryContractValidator()
    with pytest.raises(ConformanceFailure) as captured:
        if case["target"] == "portable_evidence":
            validator.validate_export(target, verify_digest=False)
        else:
            validator.validate_document(target, verify_digest=False)
    diagnostic = captured.value.diagnostic
    assert diagnostic.code == case["expected_code"]
    assert len(diagnostic.reference) <= 120
    combined = diagnostic.reference + diagnostic.message
    assert "private-learner" not in combined
    assert "C:\\private" not in combined
    assert "Traceback" not in combined


def test_existing_provenance_contracts_remain_exact() -> None:
    expected = json.loads((CORPUS / "vectors/provenance-fingerprints.json").read_text(encoding="utf-8"))
    assert provenance_fingerprints() == expected


def test_runner_has_no_product_import_and_cli_output_is_bounded() -> None:
    source = (Path(__file__).parent / "runner.py").read_text(encoding="utf-8")
    assert "financial_ai_academy" not in source
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.accountable_history.runner"],
        cwd=REPOSITORY / "backend",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    output = json.loads(completed.stdout)
    assert output["valid"] is True
    combined = completed.stdout + completed.stderr
    assert "private" not in combined
    assert "Traceback" not in combined
