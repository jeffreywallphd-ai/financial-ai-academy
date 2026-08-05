#!/usr/bin/env python3
"""Local-only approval ledger helpers for planning automation."""

from __future__ import annotations

import json
import re
from pathlib import Path


DEFAULT_STORE = Path(".local-codex/approvals/ledger.json")
STAGES = {"capability", "decision", "selection", "planning", "implementation", "completion"}
DECISIONS = {"approved", "changes-requested", "rejected"}
REVIEW_STATES = {"identified", "accepted", "changes-requested", "rejected"}
ID_RE = re.compile(r"^(CAP|DEC|SLI|WRK)-\d{4,}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
STAGES_BY_PREFIX = {
    "CAP": {"capability"},
    "DEC": {"decision"},
    "SLI": {"selection", "completion"},
    "WRK": {"planning", "implementation"},
}


class ApprovalStoreError(ValueError):
    """Raised when a local approval ledger is missing or invalid."""


def empty_store() -> dict[str, object]:
    return {"version": 1, "records": [], "reviews": []}


def store_path(root: Path, override: Path | None = None) -> Path:
    candidate = override or DEFAULT_STORE
    return candidate if candidate.is_absolute() else root / candidate


def _text(value: object) -> str:
    return "" if value is None else str(value).strip()


def validate_store(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["approval ledger must be a JSON object"]
    if data.get("version") != 1:
        errors.append("approval ledger version must be 1")
    records = data.get("records")
    reviews = data.get("reviews")
    if not isinstance(records, list):
        errors.append("approval ledger records must be an array")
        records = []
    if not isinstance(reviews, list):
        errors.append("approval ledger reviews must be an array")
        reviews = []
    bundles: dict[str, list[dict[str, object]]] = {}
    for index, record in enumerate(records):
        label = f"records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        subject = _text(record.get("subject"))
        stage = _text(record.get("stage"))
        decision = _text(record.get("decision"))
        if not ID_RE.match(subject):
            errors.append(f"{label}.subject must be a planning ID")
        elif stage not in STAGES_BY_PREFIX.get(subject.split("-", 1)[0], set()):
            errors.append(f"{label}.stage is invalid for {subject}")
        if stage not in STAGES:
            errors.append(f"{label}.stage is invalid")
        if decision not in DECISIONS:
            errors.append(f"{label}.decision is invalid")
        if not _text(record.get("actor_label")):
            errors.append(f"{label}.actor_label is required")
        if not DATE_RE.match(_text(record.get("decided_at"))):
            errors.append(f"{label}.decided_at must be YYYY-MM-DD")
        if not _text(record.get("authority")):
            errors.append(f"{label}.authority is required")
        if not TIMESTAMP_RE.match(_text(record.get("recorded_at"))):
            errors.append(f"{label}.recorded_at must be an ISO UTC timestamp")
        if stage == "implementation" and not _text(record.get("scope")):
            errors.append(f"{label}.scope is required for implementation approval")
        bundle_id = _text(record.get("bundle_id"))
        if bundle_id:
            bundles.setdefault(bundle_id, []).append(record)
            size = record.get("bundle_size")
            if not isinstance(size, int) or isinstance(size, bool) or size < 2:
                errors.append(f"{label}.bundle_size must be an integer of at least 2")
            bundle_subject = _text(record.get("bundle_subject"))
            if bundle_subject and not ID_RE.match(bundle_subject):
                errors.append(f"{label}.bundle_subject must be a planning ID")
        elif "bundle_size" in record or "bundle_subject" in record:
            errors.append(f"{label}.bundle_id is required with bundle metadata")
    for bundle_id, items in bundles.items():
        sizes = {item.get("bundle_size") for item in items}
        stages = {_text(item.get("stage")) for item in items}
        subjects = [_text(item.get("subject")) for item in items]
        timestamps = {_text(item.get("recorded_at")) for item in items}
        bundle_subjects = {_text(item.get("bundle_subject")) for item in items}
        expected = next(iter(sizes)) if len(sizes) == 1 else None
        if len(sizes) != 1 or expected != len(items):
            errors.append(f"bundle {bundle_id} must contain exactly its declared bundle_size")
        if len(stages) != 1:
            errors.append(f"bundle {bundle_id} must use one approval stage")
        if len(subjects) != len(set(subjects)):
            errors.append(f"bundle {bundle_id} subjects must be unique")
        if len(timestamps) != 1:
            errors.append(f"bundle {bundle_id} must use one recorded_at timestamp")
        if len(bundle_subjects) != 1:
            errors.append(f"bundle {bundle_id} must use one bundle_subject")
    for index, review in enumerate(reviews):
        label = f"reviews[{index}]"
        if not isinstance(review, dict):
            errors.append(f"{label} must be an object")
            continue
        if not ID_RE.match(_text(review.get("subject"))):
            errors.append(f"{label}.subject must be a planning ID")
        if not _text(review.get("review_type")):
            errors.append(f"{label}.review_type is required")
        if not _text(review.get("reviewer_label")):
            errors.append(f"{label}.reviewer_label is required")
        if _text(review.get("status")) not in REVIEW_STATES:
            errors.append(f"{label}.status is invalid")
        if not TIMESTAMP_RE.match(_text(review.get("recorded_at"))):
            errors.append(f"{label}.recorded_at must be an ISO UTC timestamp")
    return errors


def load_store(
    root: Path, override: Path | None = None, *, required: bool = False
) -> tuple[dict[str, object], Path]:
    path = store_path(root, override)
    if not path.is_file():
        if required:
            raise ApprovalStoreError(f"local approval ledger not found: {path}")
        return empty_store(), path
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ApprovalStoreError(f"cannot read local approval ledger: {error}") from error
    errors = validate_store(data)
    if errors:
        raise ApprovalStoreError("invalid local approval ledger: " + "; ".join(errors))
    return data, path


def latest_record(store: dict[str, object], subject: str, stage: str) -> dict[str, object] | None:
    matches = [
        record for record in store.get("records", [])
        if isinstance(record, dict)
        and record.get("subject") == subject
        and record.get("stage") == stage
    ]
    return matches[-1] if matches else None


def require_decision(
    store: dict[str, object], subject: str, stage: str, expected: str = "approved"
) -> dict[str, object]:
    record = latest_record(store, subject, stage)
    if record is None:
        raise ApprovalStoreError(f"missing local {stage} decision for {subject}")
    if record.get("decision") != expected:
        raise ApprovalStoreError(
            f"local {stage} decision for {subject} is {record.get('decision')!r}, not {expected!r}"
        )
    return record


def save_store(path: Path, data: dict[str, object]) -> None:
    errors = validate_store(data)
    if errors:
        raise ApprovalStoreError("refusing invalid local approval ledger: " + "; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(data, indent=2, sort_keys=True) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8", newline="\n")
    temporary.replace(path)
