"""Dependency-light conformance runner for accountable-history v1."""

from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import unicodedata
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    reference: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "reference": _safe_reference(self.reference), "message": self.message}


class ConformanceFailure(ValueError):
    def __init__(self, code: str, reference: str, message: str) -> None:
        self.diagnostic = Diagnostic(code, reference, message)
        super().__init__(message)


def _safe_reference(value: object) -> str:
    return str(value).replace(chr(0), "").replace("\r", " ").replace("\n", " ")[:120]


def reject(code: str, reference: str, message: str) -> None:
    raise ConformanceFailure(code, _safe_reference(reference), message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_schema_dir() -> Path:
    return repository_root() / "contracts/accountable-history/v1"


def default_corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/accountable-history/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject("accountable_history.schema_invalid", path.name, "Record must be an object.")
    return value


def _parsed_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        reject("accountable_history.time_invalid", "recorded_at", "History time must include an offset.")
    return parsed.astimezone(timezone.utc)


def _rendered_time(value: datetime) -> str:
    utc = value.astimezone(timezone.utc)
    rendered = utc.isoformat(timespec="microseconds" if utc.microsecond else "seconds")
    return rendered.replace("+00:00", "Z")


def _normalized_time(value: str) -> str:
    return _rendered_time(_parsed_time(value))


def _canonical_document(value: Mapping[str, Any]) -> dict[str, Any]:
    document = copy.deepcopy(dict(value))
    document.pop("history_digest", None)
    for entry in document["entries"]:
        entry["recorded_at"] = _normalized_time(entry["recorded_at"])
    document["entries"] = sorted(document["entries"], key=lambda item: (item["sequence"], item["entry_id"]))
    document["transformations"] = sorted(
        document["transformations"], key=lambda item: (item["source_entry_id"], item["relation"], item["target_entry_id"])
    )
    document["missing_links"] = sorted(
        document["missing_links"], key=lambda item: (item["source_entry_id"], item["relation"], item["target_reference"], item["reason"])
    )
    document["diagnostics"] = sorted(
        document["diagnostics"], key=lambda item: (item["code"], item["reference"], item["explanation"])
    )
    document["redactions"] = sorted(document["redactions"], key=lambda item: item["category"])
    return document


def canonical_document_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(_canonical_document(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def history_digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_document_bytes(value)).hexdigest()


def export_filename_stem(document: Mapping[str, Any]) -> str:
    root = document["root"]
    root_digest = hashlib.sha256(
        json.dumps(root, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    prefix = "lesson" if root["root_kind"] == "published_lesson" else "completion"
    return f"{prefix}-{root_digest}"


def _safe_identifier(value: str) -> bool:
    if not value or not value[0].isalnum():
        return False
    return all(
        not character.isspace()
        and unicodedata.category(character) not in {"Cc", "Cf", "Cs"}
        and character not in "/\\?#"
        for character in value
    )


def _check_display_text(value: Mapping[str, Any]) -> None:
    display_values = [str(value["title"]), str(value["summary"])]
    display_values.extend(str(entry[field]) for entry in value["entries"] for field in ("title", "explanation"))
    display_values.extend(str(item["explanation"]) for item in value["missing_links"])
    display_values.extend(str(item["explanation"]) for item in value["diagnostics"])
    forbidden = ("https://", "http://", "file:", "traceback", "exception", "password=", "token=", "c:\\")
    if any(marker in text.casefold() for text in display_values for marker in forbidden):
        reject("accountable_history.unsafe_text", "display", "History text contains an unsafe detail.")
    if any(unicodedata.category(character) in {"Cc", "Cf", "Cs"} for text in display_values for character in text):
        reject("accountable_history.unsafe_text", "display", "History text contains an unsafe detail.")

    approved_titles = {
        "learner_review": "Source and history",
        "portable_evidence": "Portable evidence record",
    }
    approved_summaries = {
        ("learner_review", "published_lesson", "valid"):
            "This view shows the source and history available for the lesson.",
        ("learner_review", "published_lesson", "incomplete"):
            "Some source history for this lesson is incomplete.",
        ("learner_review", "published_lesson", "invalid"):
            "The lesson history includes a record that does not match the expected facts.",
        ("learner_review", "knowledge_check_completion", "valid"):
            "This completion is linked to the check, the published lesson, and its audit record.",
        ("learner_review", "knowledge_check_completion", "incomplete"):
            "Some source history for this completion is incomplete.",
        ("learner_review", "knowledge_check_completion", "invalid"):
            "The completion history includes a record that does not match the expected facts.",
        ("portable_evidence", "published_lesson", "valid"):
            "This record shows the source and history disclosed for the lesson.",
        ("portable_evidence", "published_lesson", "incomplete"):
            "This record shows the available source and history disclosed for the lesson.",
        ("portable_evidence", "published_lesson", "invalid"):
            "This record shows lesson history with a record that does not match the expected facts.",
        ("portable_evidence", "knowledge_check_completion", "valid"):
            "This record shows the source and history disclosed for the completion.",
        ("portable_evidence", "knowledge_check_completion", "incomplete"):
            "This record shows the available source and history disclosed for the completion.",
        ("portable_evidence", "knowledge_check_completion", "invalid"):
            "This record shows completion history with a record that does not match the expected facts.",
    }
    approved_entry_text = {
        "educational_source": {("Reviewed source", "This source was used to prepare the lesson.")},
        "published_lesson": {
            ("Published lesson", "The lesson was published from the reviewed source."),
            ("Published lesson", "The check belongs to this lesson."),
            ("Published lesson", "The lesson record is available."),
        },
        "assessment_definition": {("Knowledge check", "This reviewed check was used for the completion.")},
        "knowledge_check_event": {("Completed check", "The completed check produced an evidence record.")},
        "completion_evidence": {("Completion evidence", "The completed check produced this evidence record.")},
        "audit_reference": {("Integrity record", "An audit reference records the accepted completion evidence.")},
    }
    approved_missing_text = {
        "not_found": "The source record could not be found.",
        "unavailable": "The source record is not available now.",
        "redacted": "The source details are not shown for this purpose.",
    }
    approved_diagnostic_text = {
        "missing_reference": "A source reference is missing.",
        "owner_unavailable": "The source owner could not return this record.",
        "unsupported_contract_version": "The source uses a version that this history view cannot read.",
        "integrity_mismatch": "The integrity check did not match the disclosed record.",
        "invalid_relation": "A source link does not match the disclosed history.",
        "identity_conflict": "Two disclosed records use the same identity with different facts.",
        "redacted_detail": "Some details are not shown for this purpose.",
    }
    display_key = (value["purpose"], value["root"]["root_kind"], value["state"])
    if value["title"] != approved_titles[value["purpose"]] or value["summary"] != approved_summaries[display_key]:
        reject("accountable_history.display_text_invalid", "summary", "History text is not reviewed.")
    if any((item["title"], item["explanation"]) not in approved_entry_text[item["resource_kind"]] for item in value["entries"]):
        reject("accountable_history.display_text_invalid", "entries", "History text is not reviewed.")
    entries_by_id = {item["entry_id"]: item for item in value["entries"]}
    for item in value["entries"]:
        if item["resource_kind"] != "published_lesson":
            continue
        if value["root"]["root_kind"] == "knowledge_check_completion":
            expected_explanation = "The check belongs to this lesson."
        elif any(
            link["source_entry_id"] == item["entry_id"]
            and link["relation"] == "published_from"
            and entries_by_id.get(link["target_entry_id"], {}).get("resource_kind") == "educational_source"
            for link in value["transformations"]
        ):
            expected_explanation = "The lesson was published from the reviewed source."
        else:
            expected_explanation = "The lesson record is available."
        if item["explanation"] != expected_explanation:
            reject("accountable_history.display_text_invalid", "entries", "History text is not reviewed.")
    if any(item["explanation"] != approved_missing_text[item["reason"]] for item in value["missing_links"]):
        reject("accountable_history.display_text_invalid", "missing_links", "History text is not reviewed.")
    if any(item["explanation"] != approved_diagnostic_text[item["code"]] for item in value["diagnostics"]):
        reject("accountable_history.display_text_invalid", "diagnostics", "History text is not reviewed.")


class AccountableHistoryContractValidator:
    def __init__(self, schema_dir: Path | None = None) -> None:
        root = schema_dir or default_schema_dir()
        self.schemas = {
            "request": load_json(root / "request.schema.json"),
            "document": load_json(root / "document.schema.json"),
            "export": load_json(root / "export.schema.json"),
        }
        for schema in self.schemas.values():
            Draft202012Validator.check_schema(schema)
        registry = Registry().with_resource(
            self.schemas["document"]["$id"], Resource.from_contents(self.schemas["document"])
        )
        self.validators = {
            "request": Draft202012Validator(self.schemas["request"], format_checker=FormatChecker()),
            "document": Draft202012Validator(self.schemas["document"], format_checker=FormatChecker()),
            "export": Draft202012Validator(self.schemas["export"], format_checker=FormatChecker(), registry=registry),
        }

    def _shape(self, name: str, value: Mapping[str, Any]) -> None:
        error = next(iter(self.validators[name].iter_errors(value)), None)
        if error is not None:
            location = ".".join(str(part) for part in error.absolute_path)
            reject("accountable_history.schema_invalid", location or name, "History record is malformed.")

    def validate_request(self, value: Mapping[str, Any]) -> None:
        self._shape("request", value)
        for key, item in value.items():
            if key.endswith("_id") and not _safe_identifier(str(item)):
                reject("accountable_history.request_invalid", key, "History request is inconsistent.")

    def validate_document(self, value: Mapping[str, Any], *, verify_digest: bool = True) -> dict[str, Any]:
        self._shape("document", value)
        entries = list(value["entries"])
        expected_sequence = list(range(1, len(entries) + 1))
        actual_sequence = sorted(int(item["sequence"]) for item in entries)
        entry_ids = [str(item["entry_id"]) for item in entries]
        if actual_sequence != expected_sequence or len(set(entry_ids)) != len(entry_ids):
            reject("accountable_history.sequence_invalid", "entries", "History order is inconsistent.")
        if any(not _safe_identifier(identifier) for identifier in entry_ids):
            reject("accountable_history.identity_invalid", "entries", "History identity is inconsistent.")
        roles = {
            "educational_source": "source",
            "published_lesson": "published",
            "assessment_definition": "defined",
            "knowledge_check_event": "completed",
            "completion_evidence": "completed",
            "audit_reference": "recorded",
        }
        owners = {
            "educational_source": "content",
            "published_lesson": "content",
            "assessment_definition": "assessment",
            "knowledge_check_event": "assessment",
            "completion_evidence": "assessment",
            "audit_reference": "audit",
        }
        if any(roles[item["resource_kind"]] != item["role"] for item in entries):
            reject("accountable_history.identity_invalid", "role", "History identity is inconsistent.")
        if any(owners[item["resource_kind"]] != item["owner_module"] for item in entries):
            reject("accountable_history.identity_invalid", "owner_module", "History identity is inconsistent.")
        root = value["root"]
        expected_kind = "published_lesson" if root["root_kind"] == "published_lesson" else "completion_evidence"
        matching = [item for item in entries if item["resource_kind"] == expected_kind and item["resource_id"] == root["resource_id"]]
        if len(matching) != 1:
            reject("accountable_history.root_mismatch", "root", "History root is inconsistent.")
        exact = matching[0]
        if root.get("resource_version") != exact.get("resource_version") or root.get("occurrence") != exact.get("occurrence"):
            reject("accountable_history.root_mismatch", "root", "History root is inconsistent.")
        known = set(entry_ids)
        links = [
            (item["source_entry_id"], item["target_entry_id"], item["relation"])
            for item in value["transformations"]
        ]
        if len(set(links)) != len(links) or any(source not in known or target not in known for source, target, _ in links):
            reject("accountable_history.link_invalid", "transformations", "History link is inconsistent.")
        if any(item["source_entry_id"] not in known for item in value["missing_links"]):
            reject("accountable_history.link_invalid", "missing_links", "History link is inconsistent.")
        categories = [item["category"] for item in value["redactions"]]
        if len(set(categories)) != len(categories):
            reject("accountable_history.redaction_invalid", "redactions", "History redaction summary is inconsistent.")
        state = value["state"]
        incomplete_codes = {"missing_reference", "owner_unavailable", "redacted_detail"}
        invalid_codes = {"unsupported_contract_version", "integrity_mismatch", "invalid_relation", "identity_conflict"}
        diagnostic_codes = {item["code"] for item in value["diagnostics"]}
        if state == "valid" and (value["missing_links"] or value["diagnostics"] or any(item["validation_status"] != "validated" for item in entries)):
            reject("accountable_history.state_invalid", "state", "History state is inconsistent.")
        if state == "incomplete" and (
            not (value["missing_links"] or value["diagnostics"] or any(item["validation_status"] == "incomplete" for item in entries))
            or not diagnostic_codes.issubset(incomplete_codes)
        ):
            reject("accountable_history.state_invalid", "state", "History state is inconsistent.")
        if state == "invalid" and not any(item["code"] in invalid_codes for item in value["diagnostics"]):
            reject("accountable_history.state_invalid", "state", "History state is inconsistent.")
        if state != "invalid" and diagnostic_codes.intersection(invalid_codes):
            reject("accountable_history.state_invalid", "state", "History state is inconsistent.")
        _check_display_text(value)
        expected_digest = history_digest(value)
        if verify_digest and value["history_digest"] != expected_digest:
            reject("accountable_history.digest_invalid", "history_digest", "History digest is inconsistent.")
        projected = _canonical_document(value)
        projected["history_digest"] = expected_digest
        return projected

    def validate_export(self, value: Mapping[str, Any], *, verify_digest: bool = True) -> dict[str, Any]:
        self._shape("export", value)
        if value["document"]["purpose"] != "portable_evidence":
            reject("accountable_history.export_invalid", "document", "Portable evidence is inconsistent.")
        document = self.validate_document(value["document"], verify_digest=verify_digest)
        if value["document_digest"] != document["history_digest"]:
            reject("accountable_history.export_invalid", "document", "Portable evidence is inconsistent.")
        latest_instant = max(_parsed_time(item["recorded_at"]) for item in document["entries"])
        latest = _rendered_time(latest_instant)
        if _parsed_time(value["exported_at"]) != latest_instant:
            reject("accountable_history.export_invalid", "exported_at", "Portable evidence is inconsistent.")
        expected_stem = export_filename_stem(document)
        if value["filename_stem"] != expected_stem:
            reject("accountable_history.export_invalid", "filename_stem", "Portable evidence is inconsistent.")
        projected = copy.deepcopy(dict(value))
        projected["exported_at"] = latest
        projected["document"] = document
        return projected


def approved_records(corpus: Path | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = corpus or default_corpus_dir()
    return (
        load_json(root / "approved/lesson-review.json"),
        load_json(root / "approved/completion-review.json"),
        load_json(root / "approved/incomplete-review.json"),
        load_json(root / "approved/portable-evidence.json"),
    )


def provenance_fingerprints() -> dict[str, str]:
    root = repository_root()
    paths = sorted(
        list((root / "contracts/provenance/v1").glob("*.json"))
        + list((root / "contracts/provenance/v2").glob("*.json"))
        + list((root / "contracts/compatibility/provenance/v1/approved").glob("*.json"))
        + list((root / "contracts/compatibility/provenance/v2/approved").glob("*.json"))
    )
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=default_corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        lesson, completion, incomplete, portable = approved_records(arguments.corpus)
        validator = AccountableHistoryContractValidator()
        lesson_value = validator.validate_document(lesson)
        completion_value = validator.validate_document(completion)
        incomplete_value = validator.validate_document(incomplete)
        portable_value = validator.validate_export(portable)
        expected_fingerprints = load_json(arguments.corpus / "vectors/provenance-fingerprints.json")
        if provenance_fingerprints() != expected_fingerprints:
            reject("accountable_history.compatibility_invalid", "provenance", "Existing provenance contracts changed.")
    except (ConformanceFailure, OSError, RuntimeError, ValueError) as error:
        diagnostic = error.diagnostic if isinstance(error, ConformanceFailure) else Diagnostic(
            "accountable_history.internal_error", "accountable_history", "Accountable-history conformance could not complete."
        )
        print(json.dumps({"valid": False, "diagnostic": diagnostic.as_dict()}, sort_keys=True))
        return 1
    print(json.dumps({
        "valid": True,
        "lesson_review_digest": lesson_value["history_digest"],
        "completion_review_digest": completion_value["history_digest"],
        "incomplete_review_digest": incomplete_value["history_digest"],
        "portable_evidence_document_digest": portable_value["document_digest"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
