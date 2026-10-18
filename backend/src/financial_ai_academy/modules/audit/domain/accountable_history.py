"""Purpose-limited accountable-history values and deterministic composition."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import re

from .provenance import (
    IncompleteReason,
    InvalidProvenance,
    LineageView,
    OwnerModule,
    RelationKind,
    ResourceKind,
    RootKind,
    ValidationStatus,
    validate_identifier,
    validate_lineage_view,
)


_DIGEST = re.compile(r"^[a-f0-9]{64}$")
_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,79}$")
_FILENAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
_MEDIA_TYPE = "application/vnd.financial-ai-academy.accountable-history+json"


class InvalidAccountableHistory(ValueError):
    def __init__(self, reference: str) -> None:
        super().__init__("Accountable history is inconsistent.")
        self.reference = reference


class AccountableHistoryPurpose(StrEnum):
    LEARNER_REVIEW = "learner_review"
    PORTABLE_EVIDENCE = "portable_evidence"


class AccountableHistoryState(StrEnum):
    VALID = "valid"
    INCOMPLETE = "incomplete"
    INVALID = "invalid"


class AccountableHistoryRole(StrEnum):
    SOURCE = "source"
    PUBLISHED = "published"
    DEFINED = "defined"
    COMPLETED = "completed"
    RECORDED = "recorded"


class AccountableHistoryDiagnosticCode(StrEnum):
    MISSING_REFERENCE = "missing_reference"
    OWNER_UNAVAILABLE = "owner_unavailable"
    UNSUPPORTED_CONTRACT_VERSION = "unsupported_contract_version"
    INTEGRITY_MISMATCH = "integrity_mismatch"
    INVALID_RELATION = "invalid_relation"
    IDENTITY_CONFLICT = "identity_conflict"
    REDACTED_DETAIL = "redacted_detail"


class AccountableHistoryRedactionCategory(StrEnum):
    PROTECTED_CONTENT = "protected_content"
    LEARNER_PRIVATE_IDENTITY = "learner_private_identity"
    OWNER_PAYLOAD = "owner_payload"
    PROVIDER_OR_SECRET_MATERIAL = "provider_or_secret_material"
    INTERNAL_DIAGNOSTICS = "internal_diagnostics"
    STORAGE_DETAILS = "storage_details"


@dataclass(frozen=True, slots=True)
class AccountableHistoryRoot:
    root_kind: RootKind
    resource_id: str
    resource_version: str | None
    occurrence: int | None


@dataclass(frozen=True, slots=True)
class AccountableHistoryEntry:
    sequence: int
    entry_id: str
    role: AccountableHistoryRole
    title: str
    explanation: str
    owner_module: OwnerModule
    resource_kind: ResourceKind
    resource_id: str
    resource_version: str | None
    occurrence: int | None
    integrity_digest: str
    recorded_at: datetime
    validation_status: ValidationStatus


@dataclass(frozen=True, slots=True)
class AccountableHistoryTransformation:
    source_entry_id: str
    target_entry_id: str
    relation: RelationKind


@dataclass(frozen=True, slots=True)
class AccountableHistoryMissingLink:
    source_entry_id: str
    relation: RelationKind
    target_reference: str
    reason: IncompleteReason
    explanation: str


@dataclass(frozen=True, slots=True)
class AccountableHistoryDiagnostic:
    code: AccountableHistoryDiagnosticCode
    reference: str
    explanation: str


@dataclass(frozen=True, slots=True)
class AccountableHistoryRedaction:
    category: AccountableHistoryRedactionCategory
    count: int


@dataclass(frozen=True, slots=True)
class AccountableHistoryDocument:
    schema_version: str
    purpose: AccountableHistoryPurpose
    root: AccountableHistoryRoot
    state: AccountableHistoryState
    title: str
    summary: str
    source_lineage_digest: str
    entries: tuple[AccountableHistoryEntry, ...]
    transformations: tuple[AccountableHistoryTransformation, ...]
    missing_links: tuple[AccountableHistoryMissingLink, ...]
    diagnostics: tuple[AccountableHistoryDiagnostic, ...]
    redactions: tuple[AccountableHistoryRedaction, ...]
    history_digest: str


@dataclass(frozen=True, slots=True)
class PortableEvidenceExport:
    schema_version: str
    media_type: str
    filename_stem: str
    exported_at: datetime
    document_digest: str
    document: AccountableHistoryDocument


_ROLE_BY_KIND = {
    ResourceKind.EDUCATIONAL_SOURCE: AccountableHistoryRole.SOURCE,
    ResourceKind.PUBLISHED_LESSON: AccountableHistoryRole.PUBLISHED,
    ResourceKind.ASSESSMENT_DEFINITION: AccountableHistoryRole.DEFINED,
    ResourceKind.KNOWLEDGE_CHECK_EVENT: AccountableHistoryRole.COMPLETED,
    ResourceKind.COMPLETION_EVIDENCE: AccountableHistoryRole.COMPLETED,
    ResourceKind.AUDIT_REFERENCE: AccountableHistoryRole.RECORDED,
}
_OWNER_BY_KIND = {
    ResourceKind.EDUCATIONAL_SOURCE: OwnerModule.CONTENT,
    ResourceKind.PUBLISHED_LESSON: OwnerModule.CONTENT,
    ResourceKind.ASSESSMENT_DEFINITION: OwnerModule.ASSESSMENT,
    ResourceKind.KNOWLEDGE_CHECK_EVENT: OwnerModule.ASSESSMENT,
    ResourceKind.COMPLETION_EVIDENCE: OwnerModule.ASSESSMENT,
    ResourceKind.AUDIT_REFERENCE: OwnerModule.AUDIT,
}
_ENTRY_COPY = {
    ResourceKind.EDUCATIONAL_SOURCE: (
        "Reviewed source",
        "This source was used to prepare the lesson.",
    ),
    ResourceKind.ASSESSMENT_DEFINITION: (
        "Knowledge check",
        "This reviewed check was used for the completion.",
    ),
    ResourceKind.KNOWLEDGE_CHECK_EVENT: (
        "Completed check",
        "The completed check produced an evidence record.",
    ),
    ResourceKind.COMPLETION_EVIDENCE: (
        "Completion evidence",
        "The completed check produced this evidence record.",
    ),
    ResourceKind.AUDIT_REFERENCE: (
        "Integrity record",
        "An audit reference records the accepted completion evidence.",
    ),
}
_MISSING_COPY = {
    IncompleteReason.NOT_FOUND: "The source record could not be found.",
    IncompleteReason.UNAVAILABLE: "The source record is not available now.",
    IncompleteReason.REDACTED: "The source details are not shown for this purpose.",
}
_DIAGNOSTIC_BY_REASON = {
    IncompleteReason.NOT_FOUND: AccountableHistoryDiagnosticCode.MISSING_REFERENCE,
    IncompleteReason.UNAVAILABLE: AccountableHistoryDiagnosticCode.OWNER_UNAVAILABLE,
    IncompleteReason.REDACTED: AccountableHistoryDiagnosticCode.REDACTED_DETAIL,
}
_DIAGNOSTIC_COPY = {
    AccountableHistoryDiagnosticCode.MISSING_REFERENCE: (
        "A source reference is missing."
    ),
    AccountableHistoryDiagnosticCode.OWNER_UNAVAILABLE: (
        "The source owner could not return this record."
    ),
    AccountableHistoryDiagnosticCode.UNSUPPORTED_CONTRACT_VERSION: (
        "The source uses a version that this history view cannot read."
    ),
    AccountableHistoryDiagnosticCode.INTEGRITY_MISMATCH: (
        "The integrity check did not match the disclosed record."
    ),
    AccountableHistoryDiagnosticCode.INVALID_RELATION: (
        "A source link does not match the disclosed history."
    ),
    AccountableHistoryDiagnosticCode.IDENTITY_CONFLICT: (
        "Two disclosed records use the same identity with different facts."
    ),
    AccountableHistoryDiagnosticCode.REDACTED_DETAIL: (
        "Some details are not shown for this purpose."
    ),
}
_TITLE_BY_PURPOSE = {
    AccountableHistoryPurpose.LEARNER_REVIEW: "Source and history",
    AccountableHistoryPurpose.PORTABLE_EVIDENCE: "Portable evidence record",
}
_SUMMARY_BY_CONTEXT = {
    (
        AccountableHistoryPurpose.LEARNER_REVIEW,
        RootKind.PUBLISHED_LESSON,
        AccountableHistoryState.VALID,
    ): "This view shows the source and history available for the lesson.",
    (
        AccountableHistoryPurpose.LEARNER_REVIEW,
        RootKind.PUBLISHED_LESSON,
        AccountableHistoryState.INCOMPLETE,
    ): "Some source history for this lesson is incomplete.",
    (
        AccountableHistoryPurpose.LEARNER_REVIEW,
        RootKind.PUBLISHED_LESSON,
        AccountableHistoryState.INVALID,
    ): "The lesson history includes a record that does not match the expected facts.",
    (
        AccountableHistoryPurpose.LEARNER_REVIEW,
        RootKind.KNOWLEDGE_CHECK_COMPLETION,
        AccountableHistoryState.VALID,
    ): "This completion is linked to the check, the published lesson, and its audit record.",
    (
        AccountableHistoryPurpose.LEARNER_REVIEW,
        RootKind.KNOWLEDGE_CHECK_COMPLETION,
        AccountableHistoryState.INCOMPLETE,
    ): "Some source history for this completion is incomplete.",
    (
        AccountableHistoryPurpose.LEARNER_REVIEW,
        RootKind.KNOWLEDGE_CHECK_COMPLETION,
        AccountableHistoryState.INVALID,
    ): "The completion history includes a record that does not match the expected facts.",
    (
        AccountableHistoryPurpose.PORTABLE_EVIDENCE,
        RootKind.PUBLISHED_LESSON,
        AccountableHistoryState.VALID,
    ): "This record shows the source and history disclosed for the lesson.",
    (
        AccountableHistoryPurpose.PORTABLE_EVIDENCE,
        RootKind.PUBLISHED_LESSON,
        AccountableHistoryState.INCOMPLETE,
    ): "This record shows the available source and history disclosed for the lesson.",
    (
        AccountableHistoryPurpose.PORTABLE_EVIDENCE,
        RootKind.PUBLISHED_LESSON,
        AccountableHistoryState.INVALID,
    ): "This record shows lesson history with a record that does not match the expected facts.",
    (
        AccountableHistoryPurpose.PORTABLE_EVIDENCE,
        RootKind.KNOWLEDGE_CHECK_COMPLETION,
        AccountableHistoryState.VALID,
    ): "This record shows the source and history disclosed for the completion.",
    (
        AccountableHistoryPurpose.PORTABLE_EVIDENCE,
        RootKind.KNOWLEDGE_CHECK_COMPLETION,
        AccountableHistoryState.INCOMPLETE,
    ): "This record shows the available source and history disclosed for the completion.",
    (
        AccountableHistoryPurpose.PORTABLE_EVIDENCE,
        RootKind.KNOWLEDGE_CHECK_COMPLETION,
        AccountableHistoryState.INVALID,
    ): "This record shows completion history with a record that does not match the expected facts.",
}


def compose_accountable_history(
    lineage: LineageView,
    purpose: AccountableHistoryPurpose,
) -> AccountableHistoryDocument:
    if not isinstance(purpose, AccountableHistoryPurpose):
        raise InvalidAccountableHistory("purpose")
    try:
        admitted = validate_lineage_view(lineage)
    except (AttributeError, InvalidProvenance, TypeError) as error:
        raise InvalidAccountableHistory("lineage") from error

    incomplete = bool(admitted.incomplete_links) or admitted.truncated or any(
        node.envelope.resource.validation_status is ValidationStatus.INCOMPLETE
        for node in admitted.nodes
    )
    state = (
        AccountableHistoryState.INCOMPLETE
        if incomplete
        else AccountableHistoryState.VALID
    )
    has_reviewed_source = any(
        edge.relation is RelationKind.PUBLISHED_FROM
        and next(
            node for node in admitted.nodes if node.node_id == edge.target_node_id
        ).envelope.resource.resource_kind
        is ResourceKind.EDUCATIONAL_SOURCE
        for edge in admitted.edges
    )
    entries = tuple(
        _entry_from_node(
            sequence,
            node.node_id,
            node.envelope.resource,
            admitted.root.root_kind,
            has_reviewed_source,
        )
        for sequence, node in enumerate(admitted.nodes, start=1)
    )
    transformations = tuple(
        AccountableHistoryTransformation(
            edge.source_node_id,
            edge.target_node_id,
            edge.relation,
        )
        for edge in admitted.edges
    )
    missing_links = tuple(
        AccountableHistoryMissingLink(
            source_entry_id=link.source_node_id,
            relation=link.relation,
            target_reference=link.target_resource_id,
            reason=link.reason,
            explanation=_MISSING_COPY[link.reason],
        )
        for link in admitted.incomplete_links
    )
    diagnostics = [
        AccountableHistoryDiagnostic(
            code=_DIAGNOSTIC_BY_REASON[link.reason],
            reference=link.target_resource_id,
            explanation=_DIAGNOSTIC_COPY[_DIAGNOSTIC_BY_REASON[link.reason]],
        )
        for link in admitted.incomplete_links
    ]
    if admitted.truncated:
        diagnostics.append(
            AccountableHistoryDiagnostic(
                code=AccountableHistoryDiagnosticCode.REDACTED_DETAIL,
                reference=admitted.root.resource.resource_id,
                explanation=_DIAGNOSTIC_COPY[
                    AccountableHistoryDiagnosticCode.REDACTED_DETAIL
                ],
            )
        )
    root_resource = admitted.root.resource
    root = AccountableHistoryRoot(
        root_kind=admitted.root.root_kind,
        resource_id=root_resource.resource_id,
        resource_version=root_resource.resource_version,
        occurrence=root_resource.occurrence,
    )
    provisional = AccountableHistoryDocument(
        schema_version="1.0.0",
        purpose=purpose,
        root=root,
        state=state,
        title=_TITLE_BY_PURPOSE[purpose],
        summary=_SUMMARY_BY_CONTEXT[(purpose, root.root_kind, state)],
        source_lineage_digest=admitted.view_digest,
        entries=entries,
        transformations=transformations,
        missing_links=missing_links,
        diagnostics=tuple(diagnostics),
        redactions=_redactions(admitted),
        history_digest="0" * 64,
    )
    return validate_accountable_history(
        replace(provisional, history_digest=accountable_history_digest(provisional))
    )


def build_portable_evidence(lineage: LineageView) -> PortableEvidenceExport:
    document = compose_accountable_history(
        lineage, AccountableHistoryPurpose.PORTABLE_EVIDENCE
    )
    latest = max(entry.recorded_at for entry in document.entries)
    return validate_portable_evidence(
        PortableEvidenceExport(
            schema_version="1.0.0",
            media_type=_MEDIA_TYPE,
            filename_stem=_filename_stem(document.root),
            exported_at=latest,
            document_digest=document.history_digest,
            document=document,
        )
    )


def validate_accountable_history(
    value: AccountableHistoryDocument,
) -> AccountableHistoryDocument:
    return _normalize_document(value, verify_digest=True)


def validate_portable_evidence(value: PortableEvidenceExport) -> PortableEvidenceExport:
    if not isinstance(value, PortableEvidenceExport):
        raise InvalidAccountableHistory("export")
    document = validate_accountable_history(value.document)
    if (
        value.schema_version != "1.0.0"
        or value.media_type != _MEDIA_TYPE
        or document.purpose is not AccountableHistoryPurpose.PORTABLE_EVIDENCE
        or value.document_digest != document.history_digest
        or not isinstance(value.filename_stem, str)
        or _FILENAME.fullmatch(value.filename_stem) is None
        or value.filename_stem != _filename_stem(document.root)
    ):
        raise InvalidAccountableHistory("export")
    latest = max(entry.recorded_at for entry in document.entries)
    exported_at = _utc(value.exported_at, "exported_at")
    if exported_at != latest:
        raise InvalidAccountableHistory("exported_at")
    return replace(value, exported_at=exported_at, document=document)


def accountable_history_digest(value: AccountableHistoryDocument) -> str:
    normalized = _normalize_document(value, verify_digest=False)
    return hashlib.sha256(
        json.dumps(
            _document_payload(normalized, include_digest=False),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def accountable_history_payload(value: AccountableHistoryDocument) -> dict[str, object]:
    return _document_payload(validate_accountable_history(value), include_digest=True)


def portable_evidence_payload(value: PortableEvidenceExport) -> dict[str, object]:
    admitted = validate_portable_evidence(value)
    return {
        "schema_version": admitted.schema_version,
        "media_type": admitted.media_type,
        "filename_stem": admitted.filename_stem,
        "exported_at": _timestamp(admitted.exported_at),
        "document_digest": admitted.document_digest,
        "document": accountable_history_payload(admitted.document),
    }


def _entry_from_node(
    sequence: int,
    node_id: str,
    resource,
    root_kind: RootKind,
    has_reviewed_source: bool,
) -> AccountableHistoryEntry:
    if resource.resource_kind is ResourceKind.PUBLISHED_LESSON:
        if root_kind is RootKind.KNOWLEDGE_CHECK_COMPLETION:
            copy = ("Published lesson", "The check belongs to this lesson.")
        elif has_reviewed_source:
            copy = (
                "Published lesson",
                "The lesson was published from the reviewed source.",
            )
        else:
            copy = ("Published lesson", "The lesson record is available.")
    else:
        copy = _ENTRY_COPY[resource.resource_kind]
    return AccountableHistoryEntry(
        sequence=sequence,
        entry_id=node_id,
        role=_ROLE_BY_KIND[resource.resource_kind],
        title=copy[0],
        explanation=copy[1],
        owner_module=resource.owner_module,
        resource_kind=resource.resource_kind,
        resource_id=resource.resource_id,
        resource_version=resource.resource_version,
        occurrence=resource.occurrence,
        integrity_digest=resource.integrity_digest,
        recorded_at=resource.recorded_at,
        validation_status=resource.validation_status,
    )


def _redactions(lineage: LineageView) -> tuple[AccountableHistoryRedaction, ...]:
    counts = _redaction_counts(lineage.root.root_kind, len(lineage.nodes))
    return tuple(
        AccountableHistoryRedaction(category, count)
        for category, count in sorted(counts.items(), key=lambda item: item[0].value)
        if count > 0
    )


def _normalize_document(
    value: AccountableHistoryDocument,
    *,
    verify_digest: bool,
) -> AccountableHistoryDocument:
    if not isinstance(value, AccountableHistoryDocument):
        raise InvalidAccountableHistory("document")
    if (
        value.schema_version != "1.0.0"
        or not isinstance(value.purpose, AccountableHistoryPurpose)
        or not isinstance(value.state, AccountableHistoryState)
        or not isinstance(value.root, AccountableHistoryRoot)
    ):
        raise InvalidAccountableHistory("document")
    _validate_root(value.root)
    if (
        value.title != _TITLE_BY_PURPOSE[value.purpose]
        or value.summary
        != _SUMMARY_BY_CONTEXT[(value.purpose, value.root.root_kind, value.state)]
        or not isinstance(value.source_lineage_digest, str)
        or _DIGEST.fullmatch(value.source_lineage_digest) is None
        or not isinstance(value.entries, tuple)
        or not 1 <= len(value.entries) <= 64
    ):
        raise InvalidAccountableHistory("display")
    entries = tuple(
        sorted(
            (_validate_entry(item) for item in value.entries),
            key=lambda item: item.sequence,
        )
    )
    if [item.sequence for item in entries] != list(range(1, len(entries) + 1)):
        raise InvalidAccountableHistory("entries")
    entry_ids = [item.entry_id for item in entries]
    if len(set(entry_ids)) != len(entry_ids):
        raise InvalidAccountableHistory("entries")
    root_matches = [
        item
        for item in entries
        if item.resource_id == value.root.resource_id
        and item.resource_version == value.root.resource_version
        and item.occurrence == value.root.occurrence
        and item.resource_kind
        is (
            ResourceKind.PUBLISHED_LESSON
            if value.root.root_kind is RootKind.PUBLISHED_LESSON
            else ResourceKind.COMPLETION_EVIDENCE
        )
    ]
    if len(root_matches) != 1:
        raise InvalidAccountableHistory("root")
    transformations = tuple(
        sorted(
            (_validate_transformation(item) for item in value.transformations),
            key=lambda item: (
                item.source_entry_id,
                item.relation.value,
                item.target_entry_id,
            ),
        )
    )
    if len(transformations) > 128:
        raise InvalidAccountableHistory("transformations")
    transformation_keys = {
        (item.source_entry_id, item.target_entry_id, item.relation)
        for item in transformations
    }
    if len(transformation_keys) != len(transformations) or any(
        item.source_entry_id not in entry_ids or item.target_entry_id not in entry_ids
        for item in transformations
    ):
        raise InvalidAccountableHistory("transformations")
    entries_by_id = {item.entry_id: item for item in entries}
    for entry in entries:
        if entry.resource_kind is not ResourceKind.PUBLISHED_LESSON:
            continue
        if value.root.root_kind is RootKind.KNOWLEDGE_CHECK_COMPLETION:
            expected_explanation = "The check belongs to this lesson."
        elif any(
            item.source_entry_id == entry.entry_id
            and item.relation is RelationKind.PUBLISHED_FROM
            and entries_by_id[item.target_entry_id].resource_kind
            is ResourceKind.EDUCATIONAL_SOURCE
            for item in transformations
        ):
            expected_explanation = "The lesson was published from the reviewed source."
        else:
            expected_explanation = "The lesson record is available."
        if entry.explanation != expected_explanation:
            raise InvalidAccountableHistory("entries")
    missing_links = tuple(
        sorted(
            (_validate_missing_link(item) for item in value.missing_links),
            key=lambda item: (
                item.source_entry_id,
                item.relation.value,
                item.target_reference,
                item.reason.value,
            ),
        )
    )
    if len(missing_links) > 32 or any(
        item.source_entry_id not in entry_ids for item in missing_links
    ):
        raise InvalidAccountableHistory("missing_links")
    diagnostics = tuple(
        sorted(
            (_validate_diagnostic(item) for item in value.diagnostics),
            key=lambda item: (item.code.value, item.reference, item.explanation),
        )
    )
    if len(diagnostics) > 32:
        raise InvalidAccountableHistory("diagnostics")
    redactions = tuple(
        sorted(
            (_validate_redaction(item) for item in value.redactions),
            key=lambda item: item.category.value,
        )
    )
    if len(redactions) > 6 or len({item.category for item in redactions}) != len(redactions):
        raise InvalidAccountableHistory("redactions")
    if {item.category: item.count for item in redactions} != _redaction_counts(
        value.root.root_kind, len(entries)
    ):
        raise InvalidAccountableHistory("redactions")
    diagnostic_keys = {(item.code, item.reference) for item in diagnostics}
    if any(
        (_DIAGNOSTIC_BY_REASON[item.reason], item.target_reference)
        not in diagnostic_keys
        for item in missing_links
    ):
        raise InvalidAccountableHistory("diagnostics")
    incomplete_codes = {
        AccountableHistoryDiagnosticCode.MISSING_REFERENCE,
        AccountableHistoryDiagnosticCode.OWNER_UNAVAILABLE,
        AccountableHistoryDiagnosticCode.REDACTED_DETAIL,
    }
    invalid_codes = {
        AccountableHistoryDiagnosticCode.UNSUPPORTED_CONTRACT_VERSION,
        AccountableHistoryDiagnosticCode.INTEGRITY_MISMATCH,
        AccountableHistoryDiagnosticCode.INVALID_RELATION,
        AccountableHistoryDiagnosticCode.IDENTITY_CONFLICT,
    }
    codes = {item.code for item in diagnostics}
    if value.state is AccountableHistoryState.VALID and (
        missing_links
        or diagnostics
        or any(item.validation_status is not ValidationStatus.VALIDATED for item in entries)
    ):
        raise InvalidAccountableHistory("state")
    if value.state is AccountableHistoryState.INCOMPLETE and (
        not (
            missing_links
            or diagnostics
            or any(item.validation_status is ValidationStatus.INCOMPLETE for item in entries)
        )
        or not codes.issubset(incomplete_codes)
    ):
        raise InvalidAccountableHistory("state")
    if value.state is AccountableHistoryState.INVALID and not codes.intersection(invalid_codes):
        raise InvalidAccountableHistory("state")
    if value.state is not AccountableHistoryState.INVALID and codes.intersection(invalid_codes):
        raise InvalidAccountableHistory("state")
    normalized = replace(
        value,
        entries=entries,
        transformations=transformations,
        missing_links=missing_links,
        diagnostics=diagnostics,
        redactions=redactions,
    )
    if verify_digest and (
        not isinstance(value.history_digest, str)
        or _DIGEST.fullmatch(value.history_digest) is None
        or accountable_history_digest(normalized) != value.history_digest
    ):
        raise InvalidAccountableHistory("history_digest")
    return normalized


def _validate_root(value: AccountableHistoryRoot) -> None:
    try:
        validate_identifier(value.resource_id, "root.resource_id")
    except InvalidProvenance as error:
        raise InvalidAccountableHistory("root") from error
    if value.root_kind is RootKind.PUBLISHED_LESSON:
        if (
            not isinstance(value.resource_version, str)
            or _VERSION.fullmatch(value.resource_version) is None
            or value.occurrence is not None
        ):
            raise InvalidAccountableHistory("root")
    elif value.root_kind is RootKind.KNOWLEDGE_CHECK_COMPLETION:
        if (
            not isinstance(value.occurrence, int)
            or isinstance(value.occurrence, bool)
            or value.occurrence < 1
            or value.resource_version is not None
        ):
            raise InvalidAccountableHistory("root")
    else:
        raise InvalidAccountableHistory("root")


def _validate_entry(value: AccountableHistoryEntry) -> AccountableHistoryEntry:
    if not isinstance(value, AccountableHistoryEntry):
        raise InvalidAccountableHistory("entries")
    try:
        validate_identifier(value.entry_id, "entry_id")
        validate_identifier(value.resource_id, "resource_id")
    except InvalidProvenance as error:
        raise InvalidAccountableHistory("entries") from error
    expected_copy = _ENTRY_COPY.get(value.resource_kind)
    if value.resource_kind is ResourceKind.PUBLISHED_LESSON:
        expected_copy = (value.title, value.explanation) if (
            value.title == "Published lesson"
            and value.explanation
            in {
                "The lesson was published from the reviewed source.",
                "The check belongs to this lesson.",
                "The lesson record is available.",
            }
        ) else None
    if (
        not isinstance(value.sequence, int)
        or isinstance(value.sequence, bool)
        or not 1 <= value.sequence <= 64
        or value.role is not _ROLE_BY_KIND.get(value.resource_kind)
        or value.owner_module is not _OWNER_BY_KIND.get(value.resource_kind)
        or expected_copy != (value.title, value.explanation)
        or not isinstance(value.integrity_digest, str)
        or _DIGEST.fullmatch(value.integrity_digest) is None
        or not isinstance(value.validation_status, ValidationStatus)
    ):
        raise InvalidAccountableHistory("entries")
    if value.resource_kind in {
        ResourceKind.EDUCATIONAL_SOURCE,
        ResourceKind.PUBLISHED_LESSON,
        ResourceKind.ASSESSMENT_DEFINITION,
    }:
        if (
            not isinstance(value.resource_version, str)
            or _VERSION.fullmatch(value.resource_version) is None
            or value.occurrence is not None
        ):
            raise InvalidAccountableHistory("entries")
    elif (
        not isinstance(value.occurrence, int)
        or isinstance(value.occurrence, bool)
        or value.occurrence < 1
        or value.resource_version is not None
    ):
        raise InvalidAccountableHistory("entries")
    return replace(value, recorded_at=_utc(value.recorded_at, "entries.recorded_at"))


def _validate_transformation(
    value: AccountableHistoryTransformation,
) -> AccountableHistoryTransformation:
    if not isinstance(value, AccountableHistoryTransformation) or not isinstance(
        value.relation, RelationKind
    ):
        raise InvalidAccountableHistory("transformations")
    try:
        validate_identifier(value.source_entry_id, "source_entry_id")
        validate_identifier(value.target_entry_id, "target_entry_id")
    except InvalidProvenance as error:
        raise InvalidAccountableHistory("transformations") from error
    return value


def _validate_missing_link(
    value: AccountableHistoryMissingLink,
) -> AccountableHistoryMissingLink:
    if (
        not isinstance(value, AccountableHistoryMissingLink)
        or not isinstance(value.relation, RelationKind)
        or not isinstance(value.reason, IncompleteReason)
        or value.explanation != _MISSING_COPY.get(value.reason)
    ):
        raise InvalidAccountableHistory("missing_links")
    try:
        validate_identifier(value.source_entry_id, "source_entry_id")
        validate_identifier(value.target_reference, "target_reference")
    except InvalidProvenance as error:
        raise InvalidAccountableHistory("missing_links") from error
    return value


def _validate_diagnostic(
    value: AccountableHistoryDiagnostic,
) -> AccountableHistoryDiagnostic:
    if (
        not isinstance(value, AccountableHistoryDiagnostic)
        or not isinstance(value.code, AccountableHistoryDiagnosticCode)
        or value.explanation != _DIAGNOSTIC_COPY[value.code]
    ):
        raise InvalidAccountableHistory("diagnostics")
    try:
        validate_identifier(value.reference, "diagnostic.reference")
    except InvalidProvenance as error:
        raise InvalidAccountableHistory("diagnostics") from error
    return value


def _validate_redaction(
    value: AccountableHistoryRedaction,
) -> AccountableHistoryRedaction:
    if (
        not isinstance(value, AccountableHistoryRedaction)
        or not isinstance(value.category, AccountableHistoryRedactionCategory)
        or not isinstance(value.count, int)
        or isinstance(value.count, bool)
        or not 1 <= value.count <= 1_000_000
    ):
        raise InvalidAccountableHistory("redactions")
    return value


def _redaction_counts(
    root_kind: RootKind,
    entry_count: int,
) -> dict[AccountableHistoryRedactionCategory, int]:
    counts = {
        AccountableHistoryRedactionCategory.OWNER_PAYLOAD: entry_count,
        AccountableHistoryRedactionCategory.STORAGE_DETAILS: entry_count,
    }
    if root_kind is RootKind.KNOWLEDGE_CHECK_COMPLETION:
        counts[AccountableHistoryRedactionCategory.LEARNER_PRIVATE_IDENTITY] = 1
        counts[AccountableHistoryRedactionCategory.PROTECTED_CONTENT] = 2
    return counts


def _document_payload(
    value: AccountableHistoryDocument,
    *,
    include_digest: bool,
) -> dict[str, object]:
    root: dict[str, object] = {
        "root_kind": value.root.root_kind.value,
        "resource_id": value.root.resource_id,
    }
    if value.root.resource_version is not None:
        root["resource_version"] = value.root.resource_version
    if value.root.occurrence is not None:
        root["occurrence"] = value.root.occurrence
    result: dict[str, object] = {
        "schema_version": value.schema_version,
        "purpose": value.purpose.value,
        "root": root,
        "state": value.state.value,
        "title": value.title,
        "summary": value.summary,
        "source_lineage_digest": value.source_lineage_digest,
        "entries": [_entry_payload(item) for item in value.entries],
        "transformations": [
            {
                "source_entry_id": item.source_entry_id,
                "target_entry_id": item.target_entry_id,
                "relation": item.relation.value,
            }
            for item in value.transformations
        ],
        "missing_links": [
            {
                "source_entry_id": item.source_entry_id,
                "relation": item.relation.value,
                "target_reference": item.target_reference,
                "reason": item.reason.value,
                "explanation": item.explanation,
            }
            for item in value.missing_links
        ],
        "diagnostics": [
            {
                "code": item.code.value,
                "reference": item.reference,
                "explanation": item.explanation,
            }
            for item in value.diagnostics
        ],
        "redactions": [
            {"category": item.category.value, "count": item.count}
            for item in value.redactions
        ],
    }
    if include_digest:
        result["history_digest"] = value.history_digest
    return result


def _entry_payload(value: AccountableHistoryEntry) -> dict[str, object]:
    result: dict[str, object] = {
        "sequence": value.sequence,
        "entry_id": value.entry_id,
        "role": value.role.value,
        "title": value.title,
        "explanation": value.explanation,
        "owner_module": value.owner_module.value,
        "resource_kind": value.resource_kind.value,
        "resource_id": value.resource_id,
        "integrity_digest": value.integrity_digest,
        "recorded_at": _timestamp(value.recorded_at),
        "validation_status": value.validation_status.value,
    }
    if value.resource_version is not None:
        result["resource_version"] = value.resource_version
    if value.occurrence is not None:
        result["occurrence"] = value.occurrence
    return result


def _filename_stem(root: AccountableHistoryRoot) -> str:
    root_payload: dict[str, object] = {
        "root_kind": root.root_kind.value,
        "resource_id": root.resource_id,
    }
    if root.resource_version is not None:
        root_payload["resource_version"] = root.resource_version
    if root.occurrence is not None:
        root_payload["occurrence"] = root.occurrence
    digest = hashlib.sha256(
        json.dumps(
            root_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()[:16]
    prefix = (
        "lesson"
        if root.root_kind is RootKind.PUBLISHED_LESSON
        else "completion"
    )
    return f"{prefix}-{digest}"


def _utc(value: datetime, reference: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise InvalidAccountableHistory(reference)
    return value.astimezone(timezone.utc)


def _timestamp(value: datetime) -> str:
    utc = _utc(value, "timestamp")
    rendered = utc.isoformat(timespec="microseconds" if utc.microsecond else "seconds")
    return rendered.replace("+00:00", "Z")


__all__ = [
    "AccountableHistoryDiagnostic",
    "AccountableHistoryDiagnosticCode",
    "AccountableHistoryDocument",
    "AccountableHistoryEntry",
    "AccountableHistoryMissingLink",
    "AccountableHistoryPurpose",
    "AccountableHistoryRedaction",
    "AccountableHistoryRedactionCategory",
    "AccountableHistoryRole",
    "AccountableHistoryRoot",
    "AccountableHistoryState",
    "AccountableHistoryTransformation",
    "InvalidAccountableHistory",
    "PortableEvidenceExport",
    "accountable_history_digest",
    "accountable_history_payload",
    "build_portable_evidence",
    "compose_accountable_history",
    "portable_evidence_payload",
    "validate_accountable_history",
    "validate_portable_evidence",
]
