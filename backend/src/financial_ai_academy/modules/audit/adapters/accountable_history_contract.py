"""Strict mapping adapter for accountable-history v1."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any, Mapping

from ..domain.accountable_history import (
    AccountableHistoryDiagnostic,
    AccountableHistoryDiagnosticCode,
    AccountableHistoryDocument,
    AccountableHistoryEntry,
    AccountableHistoryMissingLink,
    AccountableHistoryPurpose,
    AccountableHistoryRedaction,
    AccountableHistoryRedactionCategory,
    AccountableHistoryRole,
    AccountableHistoryRoot,
    AccountableHistoryState,
    AccountableHistoryTransformation,
    InvalidAccountableHistory,
    PortableEvidenceExport,
    accountable_history_payload,
    portable_evidence_payload,
    validate_accountable_history,
    validate_portable_evidence,
)
from ..domain.provenance import (
    IncompleteReason,
    OwnerModule,
    RelationKind,
    ResourceKind,
    RootKind,
    ValidationStatus,
)


_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$"
)


def _reject(reference: str) -> None:
    raise InvalidAccountableHistory(reference)


def _mapping(value: object, reference: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        _reject(reference)
    return value


def _exact_keys(
    value: Mapping[str, Any],
    required: set[str],
    optional: set[str],
    reference: str,
) -> None:
    keys = set(value)
    if not required <= keys or not keys <= required | optional:
        _reject(reference)


def _sequence(value: object, reference: str) -> tuple[Any, ...]:
    if not isinstance(value, list):
        _reject(reference)
    return tuple(value)


def _enum(enum_type, value: object, reference: str):
    try:
        return enum_type(value)
    except (TypeError, ValueError):
        _reject(reference)


def _timestamp(value: object, reference: str) -> datetime:
    if not isinstance(value, str) or _TIMESTAMP.fullmatch(value) is None:
        _reject(reference)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _reject(reference)


def accountable_history_document_from_mapping(
    value: object,
) -> AccountableHistoryDocument:
    item = _mapping(value, "document")
    _exact_keys(
        item,
        {
            "schema_version",
            "purpose",
            "root",
            "state",
            "title",
            "summary",
            "source_lineage_digest",
            "entries",
            "transformations",
            "missing_links",
            "diagnostics",
            "redactions",
            "history_digest",
        },
        set(),
        "document",
    )
    root_value = _mapping(item["root"], "root")
    _exact_keys(
        root_value,
        {"root_kind", "resource_id"},
        {"resource_version", "occurrence"},
        "root",
    )
    root = AccountableHistoryRoot(
        root_kind=_enum(RootKind, root_value["root_kind"], "root.root_kind"),
        resource_id=root_value["resource_id"],
        resource_version=root_value.get("resource_version"),
        occurrence=root_value.get("occurrence"),
    )
    entries = tuple(
        _entry_from_mapping(value, index)
        for index, value in enumerate(_sequence(item["entries"], "entries"))
    )
    transformations = tuple(
        _transformation_from_mapping(value, index)
        for index, value in enumerate(
            _sequence(item["transformations"], "transformations")
        )
    )
    missing_links = tuple(
        _missing_link_from_mapping(value, index)
        for index, value in enumerate(
            _sequence(item["missing_links"], "missing_links")
        )
    )
    diagnostics = tuple(
        _diagnostic_from_mapping(value, index)
        for index, value in enumerate(
            _sequence(item["diagnostics"], "diagnostics")
        )
    )
    redactions = tuple(
        _redaction_from_mapping(value, index)
        for index, value in enumerate(_sequence(item["redactions"], "redactions"))
    )
    return validate_accountable_history(
        AccountableHistoryDocument(
            schema_version=item["schema_version"],
            purpose=_enum(
                AccountableHistoryPurpose, item["purpose"], "purpose"
            ),
            root=root,
            state=_enum(AccountableHistoryState, item["state"], "state"),
            title=item["title"],
            summary=item["summary"],
            source_lineage_digest=item["source_lineage_digest"],
            entries=entries,
            transformations=transformations,
            missing_links=missing_links,
            diagnostics=diagnostics,
            redactions=redactions,
            history_digest=item["history_digest"],
        )
    )


def portable_evidence_from_mapping(value: object) -> PortableEvidenceExport:
    item = _mapping(value, "export")
    _exact_keys(
        item,
        {
            "schema_version",
            "media_type",
            "filename_stem",
            "exported_at",
            "document_digest",
            "document",
        },
        set(),
        "export",
    )
    return validate_portable_evidence(
        PortableEvidenceExport(
            schema_version=item["schema_version"],
            media_type=item["media_type"],
            filename_stem=item["filename_stem"],
            exported_at=_timestamp(item["exported_at"], "exported_at"),
            document_digest=item["document_digest"],
            document=accountable_history_document_from_mapping(item["document"]),
        )
    )


def _entry_from_mapping(value: object, index: int) -> AccountableHistoryEntry:
    reference = f"entries.{index}"
    item = _mapping(value, reference)
    _exact_keys(
        item,
        {
            "sequence",
            "entry_id",
            "role",
            "title",
            "explanation",
            "owner_module",
            "resource_kind",
            "resource_id",
            "integrity_digest",
            "recorded_at",
            "validation_status",
        },
        {"resource_version", "occurrence"},
        reference,
    )
    return AccountableHistoryEntry(
        sequence=item["sequence"],
        entry_id=item["entry_id"],
        role=_enum(AccountableHistoryRole, item["role"], f"{reference}.role"),
        title=item["title"],
        explanation=item["explanation"],
        owner_module=_enum(
            OwnerModule, item["owner_module"], f"{reference}.owner_module"
        ),
        resource_kind=_enum(
            ResourceKind, item["resource_kind"], f"{reference}.resource_kind"
        ),
        resource_id=item["resource_id"],
        resource_version=item.get("resource_version"),
        occurrence=item.get("occurrence"),
        integrity_digest=item["integrity_digest"],
        recorded_at=_timestamp(item["recorded_at"], f"{reference}.recorded_at"),
        validation_status=_enum(
            ValidationStatus,
            item["validation_status"],
            f"{reference}.validation_status",
        ),
    )


def _transformation_from_mapping(
    value: object, index: int
) -> AccountableHistoryTransformation:
    reference = f"transformations.{index}"
    item = _mapping(value, reference)
    _exact_keys(
        item,
        {"source_entry_id", "target_entry_id", "relation"},
        set(),
        reference,
    )
    return AccountableHistoryTransformation(
        source_entry_id=item["source_entry_id"],
        target_entry_id=item["target_entry_id"],
        relation=_enum(RelationKind, item["relation"], f"{reference}.relation"),
    )


def _missing_link_from_mapping(
    value: object, index: int
) -> AccountableHistoryMissingLink:
    reference = f"missing_links.{index}"
    item = _mapping(value, reference)
    _exact_keys(
        item,
        {
            "source_entry_id",
            "relation",
            "target_reference",
            "reason",
            "explanation",
        },
        set(),
        reference,
    )
    return AccountableHistoryMissingLink(
        source_entry_id=item["source_entry_id"],
        relation=_enum(RelationKind, item["relation"], f"{reference}.relation"),
        target_reference=item["target_reference"],
        reason=_enum(IncompleteReason, item["reason"], f"{reference}.reason"),
        explanation=item["explanation"],
    )


def _diagnostic_from_mapping(
    value: object, index: int
) -> AccountableHistoryDiagnostic:
    reference = f"diagnostics.{index}"
    item = _mapping(value, reference)
    _exact_keys(item, {"code", "reference", "explanation"}, set(), reference)
    return AccountableHistoryDiagnostic(
        code=_enum(
            AccountableHistoryDiagnosticCode,
            item["code"],
            f"{reference}.code",
        ),
        reference=item["reference"],
        explanation=item["explanation"],
    )


def _redaction_from_mapping(
    value: object, index: int
) -> AccountableHistoryRedaction:
    reference = f"redactions.{index}"
    item = _mapping(value, reference)
    _exact_keys(item, {"category", "count"}, set(), reference)
    return AccountableHistoryRedaction(
        category=_enum(
            AccountableHistoryRedactionCategory,
            item["category"],
            f"{reference}.category",
        ),
        count=item["count"],
    )


__all__ = [
    "accountable_history_document_from_mapping",
    "accountable_history_payload",
    "portable_evidence_from_mapping",
    "portable_evidence_payload",
]
