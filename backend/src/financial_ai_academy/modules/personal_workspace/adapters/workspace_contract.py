"""Closed parser, projector, and pure mutation core for Personal workspace v1."""

from __future__ import annotations

import base64
import binascii
from dataclasses import asdict, is_dataclass, replace
from datetime import datetime, timezone
import hashlib
import hmac
import json
from pathlib import Path
import secrets
from typing import Any, Mapping, Never
import unicodedata

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from ..domain.workspace import (
    ArchiveRecordMutation,
    CreateBookmarkMutation,
    CreateCollectionMutation,
    CreateNoteMutation,
    LearningOpportunityReference,
    LearningReference,
    PersonalWorkspace,
    PlacedLessonReference,
    ProjectArtifactReference,
    ProjectSnapshotReference,
    ProjectWorkspaceReference,
    PublicationProvenance,
    RefreshReferenceMutation,
    RemoveCollectionMutation,
    RemoveRecordMutation,
    RenameCollectionMutation,
    ReorderRecordsMutation,
    RestoreRecordMutation,
    SetCollectionMembersMutation,
    UpdateBookmarkMutation,
    UpdateNoteMutation,
    WorkspaceBookmark,
    WorkspaceCollection,
    WorkspaceMutationIntent,
    WorkspaceNote,
    WorkspaceQuery,
    WorkspaceQueryResult,
    WorkspaceRecord,
    is_canonical_project_logical_path,
)
from ..ports.workspace_contract import PersonalWorkspaceContractFailure


VERSION = "1.0.0"
_PROCESS_CURSOR_SIGNING_KEY = secrets.token_bytes(32)


class ContractPersonalWorkspaceAdapter:
    """Validate portable documents and return immutable workspace values."""

    def __init__(
        self,
        schema_dir: Path,
        *,
        cursor_signing_key: bytes | None = None,
    ) -> None:
        signing_key = (
            _PROCESS_CURSOR_SIGNING_KEY
            if cursor_signing_key is None
            else cursor_signing_key
        )
        if not isinstance(signing_key, bytes) or len(signing_key) < 32:
            raise ValueError("cursor_signing_key must contain at least 32 bytes")
        self._cursor_signing_key = signing_key
        schemas = {
            name: json.loads(
                (schema_dir / f"{name}.schema.json").read_text(encoding="utf-8")
            )
            for name in (
                "learning-reference",
                "workspace",
                "mutation-intent",
                "workspace-query",
                "workspace-query-result",
            )
        }
        registry = Registry().with_resources(
            (
                schema["$id"],
                Resource.from_contents(schema),
            )
            for schema in schemas.values()
        )
        self._validators: dict[str, Draft202012Validator] = {}
        for name, schema in schemas.items():
            Draft202012Validator.check_schema(schema)
            self._validators[name] = Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
                registry=registry,
            )

    def canonical_digest(self, value: Mapping[str, object]) -> str:
        return hashlib.sha256(self._canonical_bytes(value)).hexdigest()

    def parse_reference(self, value: bytes) -> LearningReference:
        document = self._document(value, "learning-reference")
        self._version(document)
        self._validate_reference_semantics(document["reference"])
        return self._reference(document["reference"])

    def parse_workspace(self, value: bytes) -> PersonalWorkspace:
        document = self._document(value, "workspace")
        self._version(document)
        self._validate_workspace_semantics(document)
        return self._workspace(document)

    def parse_mutation_intent(self, value: bytes) -> WorkspaceMutationIntent:
        document = self._document(value, "mutation-intent")
        self._version(document)
        self._validate_mutation_semantics(document)
        mutation = document["mutation"]
        operation = mutation["operation"]
        if operation == "create_note":
            parsed = CreateNoteMutation(
                target=self._reference(mutation["target"]),
                title=mutation["title"],
                body=mutation["body"],
            )
        elif operation == "update_note":
            parsed = UpdateNoteMutation(
                record_id=mutation["record_id"],
                title=mutation["title"],
                body=mutation["body"],
            )
        elif operation == "create_bookmark":
            parsed = CreateBookmarkMutation(
                target=self._reference(mutation["target"]),
                label=mutation.get("label"),
            )
        elif operation == "update_bookmark":
            parsed = UpdateBookmarkMutation(
                record_id=mutation["record_id"],
                label=mutation.get("label"),
            )
        elif operation == "create_collection":
            parsed = CreateCollectionMutation(title=mutation["title"])
        elif operation == "rename_collection":
            parsed = RenameCollectionMutation(
                collection_id=mutation["collection_id"],
                title=mutation["title"],
            )
        elif operation == "remove_collection":
            parsed = RemoveCollectionMutation(
                collection_id=mutation["collection_id"]
            )
        elif operation == "set_collection_members":
            parsed = SetCollectionMembersMutation(
                collection_id=mutation["collection_id"],
                member_record_ids=tuple(mutation["member_record_ids"]),
            )
        elif operation == "reorder_records":
            parsed = ReorderRecordsMutation(record_ids=tuple(mutation["record_ids"]))
        elif operation == "archive_record":
            parsed = ArchiveRecordMutation(record_id=mutation["record_id"])
        elif operation == "restore_record":
            parsed = RestoreRecordMutation(record_id=mutation["record_id"])
        elif operation == "remove_record":
            parsed = RemoveRecordMutation(record_id=mutation["record_id"])
        else:
            parsed = RefreshReferenceMutation(record_id=mutation["record_id"])
        return WorkspaceMutationIntent(
            schema_version=document["schema_version"],
            idempotency_key=document["idempotency_key"],
            expected_revision=document["expected_revision"],
            mutation=parsed,
        )

    def parse_workspace_query(self, value: bytes) -> WorkspaceQuery:
        document = self._document(value, "workspace-query")
        self._version(document)
        return self._workspace_query(document)

    def parse_workspace_query_result(self, value: bytes) -> WorkspaceQueryResult:
        document = self._document(value, "workspace-query-result")
        self._version(document)
        query = self._workspace_query(document["applied_query"])
        expected_digest = self._query_digest(query)
        if document["query_digest"] != expected_digest:
            self._reject(
                "personal_workspace.contract.query_digest_mismatch",
                "query_digest",
            )
        applied_offset = 0
        applied_scope = None
        if query.cursor is not None:
            applied_offset, applied_scope = self._decode_cursor(
                query.cursor,
                revision=document["workspace_revision"],
                query_digest=expected_digest,
            )
        next_offset = None
        next_scope = None
        if document.get("next_cursor") is not None:
            next_offset, next_scope = self._decode_cursor(
                document["next_cursor"],
                revision=document["workspace_revision"],
                query_digest=expected_digest,
            )
        records = tuple(
            self._workspace_record(record) for record in document["records"]
        )
        if len(records) > query.limit:
            self._reject(
                "personal_workspace.contract.invalid_query_result",
                "records",
            )
        self._unique(
            [record.record_id for record in records],
            "records.record_id",
        )
        if next_offset is not None and (
            not records
            or next_offset != applied_offset + len(records)
            or (applied_scope is not None and applied_scope != next_scope)
        ):
            self._reject(
                "personal_workspace.contract.invalid_query_result",
                "next_cursor",
            )
        return WorkspaceQueryResult(
            schema_version=document["schema_version"],
            workspace_revision=document["workspace_revision"],
            query_digest=document["query_digest"],
            applied_query=query,
            records=records,
            next_cursor=document.get("next_cursor"),
        )

    def reference_document(self, value: LearningReference) -> dict[str, object]:
        document = {
            "schema_version": VERSION,
            "reference": self._portable(value),
        }
        self._shape("learning-reference", document)
        self._validate_reference_semantics(document["reference"])
        return document

    def workspace_document(self, value: PersonalWorkspace) -> dict[str, object]:
        document = self._portable(value)
        self._shape("workspace", document)
        self._validate_workspace_semantics(document)
        return document

    def mutation_intent_document(
        self,
        value: WorkspaceMutationIntent,
    ) -> dict[str, object]:
        document = self._portable(value)
        self._shape("mutation-intent", document)
        self._validate_mutation_semantics(document)
        return document

    def workspace_query_document(self, value: WorkspaceQuery) -> dict[str, object]:
        document = self._query_mapping(self._normalized_query(value))
        self._shape("workspace-query", document)
        return document

    def workspace_query_result_document(
        self,
        value: WorkspaceQueryResult,
    ) -> dict[str, object]:
        document = {
            "schema_version": value.schema_version,
            "workspace_revision": value.workspace_revision,
            "query_digest": value.query_digest,
            "applied_query": self._query_mapping(value.applied_query),
            "records": self._portable(value.records),
            "next_cursor": value.next_cursor,
        }
        self._shape("workspace-query-result", document)
        parsed = self.parse_workspace_query_result(self._canonical_bytes(document))
        if parsed != value:
            self._reject(
                "personal_workspace.contract.noncanonical_query_result",
                "workspace-query-result",
            )
        return document

    def query_workspace(
        self,
        workspace: PersonalWorkspace,
        query: WorkspaceQuery,
    ) -> WorkspaceQueryResult:
        self.workspace_document(workspace)
        normalized = self._normalized_query(query)
        self.workspace_query_document(normalized)
        query_digest = self._query_digest(normalized)
        offset = 0
        if normalized.cursor is not None:
            offset, _scope = self._decode_cursor(
                normalized.cursor,
                revision=workspace.revision,
                query_digest=query_digest,
                expected_scope=self._cursor_scope(workspace),
            )

        known_collections = {
            collection.collection_id: set(collection.member_record_ids)
            for collection in workspace.collections
        }
        if (
            normalized.collection_id is not None
            and normalized.collection_id not in known_collections
        ):
            self._reject(
                "personal_workspace.contract.collection_not_found",
                normalized.collection_id,
            )
        collection_members = (
            None
            if normalized.collection_id is None
            else known_collections[normalized.collection_id]
        )
        records = [
            record
            for record in workspace.records
            if self._query_match(record, normalized, collection_members)
        ]
        records = self._query_sort(records, normalized.sort)
        if offset > len(records):
            self._reject(
                "personal_workspace.contract.invalid_cursor",
                "cursor",
            )
        selected = tuple(records[offset : offset + normalized.limit])
        next_offset = offset + len(selected)
        next_cursor = (
            self._encode_cursor(
                revision=workspace.revision,
                query_digest=query_digest,
                offset=next_offset,
                workspace=workspace,
            )
            if next_offset < len(records)
            else None
        )
        result = WorkspaceQueryResult(
            schema_version=VERSION,
            workspace_revision=workspace.revision,
            query_digest=query_digest,
            applied_query=normalized,
            records=selected,
            next_cursor=next_cursor,
        )
        self.workspace_query_result_document(result)
        return result

    def apply_mutation(
        self,
        workspace: PersonalWorkspace,
        intent: WorkspaceMutationIntent,
        *,
        occurred_at: datetime,
        issued_id: str | None = None,
    ) -> PersonalWorkspace:
        occurred_at = self._aware_timestamp(occurred_at, "occurred_at")
        self.workspace_document(workspace)
        self.mutation_intent_document(intent)
        if intent.schema_version != VERSION or workspace.schema_version != VERSION:
            self._reject("personal_workspace.contract.unsupported_version", "schema_version")
        if intent.expected_revision != workspace.revision:
            self._reject("personal_workspace.contract.stale_revision", "expected_revision")
        if occurred_at < workspace.updated_at:
            self._reject("personal_workspace.contract.invalid_time", "occurred_at")

        records = list(workspace.records)
        collections = list(workspace.collections)
        mutation = intent.mutation

        if isinstance(mutation, CreateNoteMutation):
            record_id = self._new_id(issued_id, records, collections)
            records.append(
                WorkspaceNote(
                    record_id=record_id,
                    title=mutation.title,
                    body=mutation.body,
                    target=mutation.target,
                    archived=False,
                    created_at=occurred_at,
                    updated_at=occurred_at,
                )
            )
        elif isinstance(mutation, UpdateNoteMutation):
            index, record = self._record(records, mutation.record_id)
            if not isinstance(record, WorkspaceNote):
                self._reject("personal_workspace.contract.record_kind_conflict", mutation.record_id)
            records[index] = replace(
                record,
                title=mutation.title,
                body=mutation.body,
                updated_at=occurred_at,
            )
        elif isinstance(mutation, CreateBookmarkMutation):
            record_id = self._new_id(issued_id, records, collections)
            records.append(
                WorkspaceBookmark(
                    record_id=record_id,
                    target=mutation.target,
                    label=mutation.label,
                    archived=False,
                    created_at=occurred_at,
                    updated_at=occurred_at,
                )
            )
        elif isinstance(mutation, UpdateBookmarkMutation):
            index, record = self._record(records, mutation.record_id)
            if not isinstance(record, WorkspaceBookmark):
                self._reject("personal_workspace.contract.record_kind_conflict", mutation.record_id)
            records[index] = replace(record, label=mutation.label, updated_at=occurred_at)
        elif isinstance(mutation, CreateCollectionMutation):
            collection_id = self._new_id(issued_id, records, collections)
            collections.append(
                WorkspaceCollection(
                    collection_id=collection_id,
                    title=mutation.title,
                    member_record_ids=(),
                    created_at=occurred_at,
                    updated_at=occurred_at,
                )
            )
        elif isinstance(mutation, RenameCollectionMutation):
            index, collection = self._collection(collections, mutation.collection_id)
            collections[index] = replace(
                collection,
                title=mutation.title,
                updated_at=occurred_at,
            )
        elif isinstance(mutation, RemoveCollectionMutation):
            index, _collection = self._collection(collections, mutation.collection_id)
            collections.pop(index)
        elif isinstance(mutation, SetCollectionMembersMutation):
            index, collection = self._collection(collections, mutation.collection_id)
            self._same_unique_ids(
                mutation.member_record_ids,
                {record.record_id for record in records},
                "mutation.member_record_ids",
                allow_subset=True,
            )
            collections[index] = replace(
                collection,
                member_record_ids=mutation.member_record_ids,
                updated_at=occurred_at,
            )
        elif isinstance(mutation, ReorderRecordsMutation):
            self._same_unique_ids(
                mutation.record_ids,
                {record.record_id for record in records},
                "mutation.record_ids",
            )
            by_id = {record.record_id: record for record in records}
            records = [by_id[record_id] for record_id in mutation.record_ids]
        elif isinstance(mutation, (ArchiveRecordMutation, RestoreRecordMutation)):
            index, record = self._record(records, mutation.record_id)
            records[index] = replace(
                record,
                archived=isinstance(mutation, ArchiveRecordMutation),
                updated_at=occurred_at,
            )
        elif isinstance(mutation, RefreshReferenceMutation):
            self._reject(
                "personal_workspace.contract.refresh_resolution_required",
                mutation.record_id,
            )
        else:
            index, record = self._record(records, mutation.record_id)
            records.pop(index)
            collections = [
                replace(
                    collection,
                    member_record_ids=tuple(
                        record_id
                        for record_id in collection.member_record_ids
                        if record_id != record.record_id
                    ),
                    updated_at=(
                        occurred_at
                        if record.record_id in collection.member_record_ids
                        else collection.updated_at
                    ),
                )
                for collection in collections
            ]

        result = PersonalWorkspace(
            schema_version=VERSION,
            workspace_id=workspace.workspace_id,
            learner_id=workspace.learner_id,
            revision=workspace.revision + 1,
            records=tuple(records),
            collections=tuple(collections),
            created_at=workspace.created_at,
            updated_at=occurred_at,
            workspace_digest="0" * 64,
        )
        material = self._portable(result)
        material.pop("workspace_digest")
        completed = replace(result, workspace_digest=self.canonical_digest(material))
        self.workspace_document(completed)
        return completed

    def apply_reference_refresh(
        self,
        workspace: PersonalWorkspace,
        intent: WorkspaceMutationIntent,
        *,
        occurred_at: datetime,
        resolved_reference: LearningReference | None,
    ) -> PersonalWorkspace:
        occurred_at = self._aware_timestamp(occurred_at, "occurred_at")
        self.workspace_document(workspace)
        self.mutation_intent_document(intent)
        if not isinstance(intent.mutation, RefreshReferenceMutation):
            self._reject(
                "personal_workspace.contract.refresh_intent_required",
                "mutation.operation",
            )
        if intent.schema_version != VERSION or workspace.schema_version != VERSION:
            self._reject("personal_workspace.contract.unsupported_version", "schema_version")
        if intent.expected_revision != workspace.revision:
            self._reject("personal_workspace.contract.stale_revision", "expected_revision")
        if occurred_at < workspace.updated_at:
            self._reject("personal_workspace.contract.invalid_time", "occurred_at")

        records = list(workspace.records)
        index, record = self._record(records, intent.mutation.record_id)
        original = record.target
        if resolved_reference is None:
            refreshed = replace(
                original,
                target_status="unavailable",
                validated_at=occurred_at,
            )
        else:
            self.reference_document(resolved_reference)
            if (
                resolved_reference.target_status != "available"
                or resolved_reference.validated_at != occurred_at
                or not self._same_selector(original, resolved_reference)
            ):
                self._reject(
                    "personal_workspace.contract.invalid_refresh_result",
                    intent.mutation.record_id,
                )
            if self._same_immutable_meaning(original, resolved_reference):
                refreshed = resolved_reference
            else:
                refreshed = replace(
                    original,
                    target_status="stale",
                    validated_at=occurred_at,
                )
        records[index] = replace(record, target=refreshed, updated_at=occurred_at)
        result = PersonalWorkspace(
            schema_version=VERSION,
            workspace_id=workspace.workspace_id,
            learner_id=workspace.learner_id,
            revision=workspace.revision + 1,
            records=tuple(records),
            collections=workspace.collections,
            created_at=workspace.created_at,
            updated_at=occurred_at,
            workspace_digest="0" * 64,
        )
        material = self._portable(result)
        material.pop("workspace_digest")
        completed = replace(result, workspace_digest=self.canonical_digest(material))
        self.workspace_document(completed)
        return completed

    def empty_workspace(
        self,
        *,
        workspace_id: str,
        learner_id: str,
        created_at: datetime,
    ) -> PersonalWorkspace:
        created_at = self._aware_timestamp(created_at, "created_at")
        value = PersonalWorkspace(
            schema_version=VERSION,
            workspace_id=workspace_id,
            learner_id=learner_id,
            revision=1,
            records=(),
            collections=(),
            created_at=created_at,
            updated_at=created_at,
            workspace_digest="0" * 64,
        )
        material = self._portable(value)
        material.pop("workspace_digest")
        completed = replace(value, workspace_digest=self.canonical_digest(material))
        self.workspace_document(completed)
        return completed

    def _workspace_query(self, document: Mapping[str, Any]) -> WorkspaceQuery:
        return self._normalized_query(
            WorkspaceQuery(
                schema_version=document["schema_version"],
                text=document.get("text"),
                record_kinds=tuple(document.get("record_kinds", ())),
                owner_modules=tuple(document.get("owner_modules", ())),
                reference_kinds=tuple(document.get("reference_kinds", ())),
                target_statuses=tuple(document.get("target_statuses", ())),
                archived=document.get("archived"),
                collection_id=document.get("collection_id"),
                sort=document.get("sort", "workspace_order"),
                limit=document.get("limit", 50),
                cursor=document.get("cursor"),
            )
        )

    def _normalized_query(self, query: WorkspaceQuery) -> WorkspaceQuery:
        if query.schema_version != VERSION:
            self._reject(
                "personal_workspace.contract.unsupported_version",
                "schema_version",
            )
        text = None
        if query.text is not None:
            text = " ".join(
                unicodedata.normalize("NFKC", query.text).casefold().split()
            )
            if not text:
                self._reject(
                    "personal_workspace.contract.invalid_query",
                    "text",
                )
        return replace(
            query,
            text=text,
            record_kinds=tuple(sorted(query.record_kinds)),
            owner_modules=tuple(sorted(query.owner_modules)),
            reference_kinds=tuple(sorted(query.reference_kinds)),
            target_statuses=tuple(sorted(query.target_statuses)),
        )

    def _query_digest(self, query: WorkspaceQuery) -> str:
        material = self._query_mapping(replace(query, cursor=None))
        return self.canonical_digest(material)

    def _query_mapping(
        self,
        query: WorkspaceQuery,
    ) -> dict[str, object]:
        document: dict[str, object] = {"schema_version": query.schema_version}
        if query.text is not None:
            document["text"] = query.text
        if query.record_kinds:
            document["record_kinds"] = list(query.record_kinds)
        if query.owner_modules:
            document["owner_modules"] = list(query.owner_modules)
        if query.reference_kinds:
            document["reference_kinds"] = list(query.reference_kinds)
        if query.target_statuses:
            document["target_statuses"] = list(query.target_statuses)
        if query.archived is not None:
            document["archived"] = query.archived
        if query.collection_id is not None:
            document["collection_id"] = query.collection_id
        if query.sort != "workspace_order":
            document["sort"] = query.sort
        if query.limit != 50:
            document["limit"] = query.limit
        if query.cursor is not None:
            document["cursor"] = query.cursor
        return document

    def _query_match(
        self,
        record: WorkspaceRecord,
        query: WorkspaceQuery,
        collection_members: set[str] | None,
    ) -> bool:
        target = record.target
        if query.record_kinds and record.record_kind not in query.record_kinds:
            return False
        if query.owner_modules and target.owner_module not in query.owner_modules:
            return False
        if query.reference_kinds and target.reference_kind not in query.reference_kinds:
            return False
        if query.target_statuses and target.target_status not in query.target_statuses:
            return False
        if query.archived is not None and record.archived is not query.archived:
            return False
        if collection_members is not None and record.record_id not in collection_members:
            return False
        if query.text is None:
            return True
        haystack = " ".join(
            self._normalized_search_value(value)
            for value in self._searchable_values(record)
            if value
        )
        return all(token in haystack for token in query.text.split())

    def _query_sort(
        self,
        records: list[WorkspaceRecord],
        sort: str,
    ) -> list[WorkspaceRecord]:
        if sort == "workspace_order":
            return records
        if sort == "updated_desc":
            return sorted(
                records,
                key=lambda record: (-record.updated_at.timestamp(), record.record_id),
            )
        if sort == "updated_asc":
            return sorted(records, key=lambda record: (record.updated_at, record.record_id))
        if sort == "title_asc":
            return sorted(
                records,
                key=lambda record: (
                    self._normalized_search_value(self._record_title(record)),
                    record.record_id,
                ),
            )
        return sorted(
            records,
            key=lambda record: (
                record.target.owner_module,
                record.target.reference_kind,
                self._normalized_search_value(record.target.title),
                record.record_id,
            ),
        )

    def _searchable_values(self, record: WorkspaceRecord) -> tuple[str, ...]:
        target = record.target
        values = [record.record_id, self._record_title(record), target.title]
        if isinstance(record, WorkspaceNote):
            values.append(record.body)
        for name in (
            "opportunity_id",
            "placement_id",
            "package_id",
            "project_id",
            "snapshot_id",
            "artifact_id",
            "logical_path",
        ):
            value = getattr(target, name, None)
            if isinstance(value, str):
                values.append(value)
        return tuple(values)

    def _record_title(self, record: WorkspaceRecord) -> str:
        if isinstance(record, WorkspaceNote):
            return record.title
        return record.label or record.target.title

    @staticmethod
    def _normalized_search_value(value: str) -> str:
        return " ".join(unicodedata.normalize("NFKC", value).casefold().split())

    def _encode_cursor(
        self,
        *,
        revision: int,
        query_digest: str,
        offset: int,
        workspace: PersonalWorkspace,
    ) -> str:
        material = {
            "offset": offset,
            "query_digest": query_digest,
            "workspace_revision": revision,
            "workspace_scope": self._cursor_scope(workspace),
        }
        mac = hmac.new(
            self._cursor_signing_key,
            self._canonical_bytes(material),
            hashlib.sha256,
        ).hexdigest()
        document = {**material, "mac": mac}
        return base64.urlsafe_b64encode(self._canonical_bytes(document)).decode(
            "ascii"
        ).rstrip("=")

    def _decode_cursor(
        self,
        cursor: str,
        *,
        revision: int,
        query_digest: str,
        expected_scope: str | None = None,
    ) -> tuple[int, str]:
        if not cursor or len(cursor) > 512:
            self._reject("personal_workspace.contract.invalid_cursor", "cursor")
        try:
            padded = cursor + "=" * (-len(cursor) % 4)
            decoded = base64.b64decode(
                padded,
                altchars=b"-_",
                validate=True,
            )
            document = json.loads(decoded.decode("utf-8"))
        except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
            self._reject("personal_workspace.contract.invalid_cursor", "cursor")
        if not isinstance(document, dict) or set(document) != {
            "mac",
            "offset",
            "query_digest",
            "workspace_revision",
            "workspace_scope",
        }:
            self._reject("personal_workspace.contract.invalid_cursor", "cursor")
        offset = document["offset"]
        observed_revision = document["workspace_revision"]
        observed_digest = document["query_digest"]
        observed_scope = document["workspace_scope"]
        mac = document["mac"]
        if (
            not isinstance(offset, int)
            or isinstance(offset, bool)
            or offset < 0
            or not isinstance(observed_revision, int)
            or isinstance(observed_revision, bool)
            or not isinstance(observed_digest, str)
            or not isinstance(observed_scope, str)
            or len(observed_scope) != 64
            or any(character not in "0123456789abcdef" for character in observed_scope)
            or not isinstance(mac, str)
        ):
            self._reject("personal_workspace.contract.invalid_cursor", "cursor")
        material = {
            "offset": offset,
            "query_digest": observed_digest,
            "workspace_revision": observed_revision,
            "workspace_scope": observed_scope,
        }
        expected_mac = hmac.new(
            self._cursor_signing_key,
            self._canonical_bytes(material),
            hashlib.sha256,
        ).hexdigest()
        if (
            not hmac.compare_digest(mac, expected_mac)
            or observed_revision != revision
            or observed_digest != query_digest
            or (expected_scope is not None and observed_scope != expected_scope)
        ):
            self._reject("personal_workspace.contract.invalid_cursor", "cursor")
        return offset, observed_scope

    def _cursor_scope(self, workspace: PersonalWorkspace) -> str:
        return hmac.new(
            self._cursor_signing_key,
            self._canonical_bytes(
                {
                    "learner_id": workspace.learner_id,
                    "workspace_id": workspace.workspace_id,
                }
            ),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def _same_selector(
        original: LearningReference,
        resolved: LearningReference,
    ) -> bool:
        if type(original) is not type(resolved):
            return False
        if isinstance(original, LearningOpportunityReference):
            return (
                original.opportunity_id,
                original.placement_id,
            ) == (resolved.opportunity_id, resolved.placement_id)
        if isinstance(original, PlacedLessonReference):
            return original.placement_id == resolved.placement_id
        if isinstance(original, ProjectWorkspaceReference):
            return original.project_id == resolved.project_id
        if isinstance(original, ProjectSnapshotReference):
            return (
                original.project_id,
                original.snapshot_id,
            ) == (resolved.project_id, resolved.snapshot_id)
        return (
            original.project_id,
            original.artifact_id,
            original.artifact_version,
        ) == (
            resolved.project_id,
            resolved.artifact_id,
            resolved.artifact_version,
        )

    @staticmethod
    def _same_immutable_meaning(
        original: LearningReference,
        resolved: LearningReference,
    ) -> bool:
        if isinstance(original, LearningOpportunityReference) and isinstance(
            resolved, LearningOpportunityReference
        ):
            return (
                original.package_id,
                original.package_version,
                original.package_digest,
                original.source_fingerprint,
                original.provenance,
            ) == (
                resolved.package_id,
                resolved.package_version,
                resolved.package_digest,
                resolved.source_fingerprint,
                resolved.provenance,
            )
        if isinstance(original, PlacedLessonReference) and isinstance(
            resolved, PlacedLessonReference
        ):
            return (
                original.package_id,
                original.package_version,
                original.package_digest,
                original.provenance,
            ) == (
                resolved.package_id,
                resolved.package_version,
                resolved.package_digest,
                resolved.provenance,
            )
        if isinstance(original, ProjectWorkspaceReference) and isinstance(
            resolved, ProjectWorkspaceReference
        ):
            return True
        if isinstance(original, ProjectSnapshotReference) and isinstance(
            resolved, ProjectSnapshotReference
        ):
            return (
                original.project_revision,
                original.workspace_revision,
                original.snapshot_digest,
                original.closed_at,
            ) == (
                resolved.project_revision,
                resolved.workspace_revision,
                resolved.snapshot_digest,
                resolved.closed_at,
            )
        if isinstance(original, ProjectArtifactReference) and isinstance(
            resolved, ProjectArtifactReference
        ):
            return (
                original.artifact_kind,
                original.logical_path,
                original.media_type,
                original.inspection_mode,
                original.byte_count,
                original.content_digest,
                original.created_at,
            ) == (
                resolved.artifact_kind,
                resolved.logical_path,
                resolved.media_type,
                resolved.inspection_mode,
                resolved.byte_count,
                resolved.content_digest,
                resolved.created_at,
            )
        return False

    def _document(self, value: bytes, schema: str) -> dict[str, Any]:
        try:
            document = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._reject("personal_workspace.contract.invalid_json", schema)
        if not isinstance(document, dict):
            self._reject("personal_workspace.contract.invalid_shape", schema)
        self._shape(schema, document)
        return document

    def _shape(self, schema: str, document: Mapping[str, object]) -> None:
        errors = sorted(
            self._validators[schema].iter_errors(document),
            key=lambda error: (
                tuple(str(part) for part in error.absolute_path),
                error.message,
            ),
        )
        if errors:
            path = ".".join(str(part) for part in errors[0].absolute_path)
            self._reject(
                "personal_workspace.contract.invalid_shape",
                path or schema,
            )

    def _version(self, document: Mapping[str, object]) -> None:
        if document.get("schema_version") != VERSION:
            self._reject(
                "personal_workspace.contract.unsupported_version",
                "schema_version",
            )

    def _workspace(self, document: Mapping[str, Any]) -> PersonalWorkspace:
        return PersonalWorkspace(
            schema_version=document["schema_version"],
            workspace_id=document["workspace_id"],
            learner_id=document["learner_id"],
            revision=document["revision"],
            records=tuple(self._workspace_record(item) for item in document["records"]),
            collections=tuple(
                WorkspaceCollection(
                    collection_id=item["collection_id"],
                    title=item["title"],
                    member_record_ids=tuple(item["member_record_ids"]),
                    created_at=self._timestamp(item["created_at"]),
                    updated_at=self._timestamp(item["updated_at"]),
                )
                for item in document["collections"]
            ),
            created_at=self._timestamp(document["created_at"]),
            updated_at=self._timestamp(document["updated_at"]),
            workspace_digest=document["workspace_digest"],
        )

    def _workspace_record(self, value: Mapping[str, Any]) -> WorkspaceRecord:
        common = {
            "record_id": value["record_id"],
            "target": self._reference(value["target"]),
            "archived": value["archived"],
            "created_at": self._timestamp(value["created_at"]),
            "updated_at": self._timestamp(value["updated_at"]),
        }
        if value["record_kind"] == "note":
            return WorkspaceNote(title=value["title"], body=value["body"], **common)
        return WorkspaceBookmark(label=value.get("label"), **common)

    def _reference(self, value: Mapping[str, Any]) -> LearningReference:
        self._validate_reference_semantics(value)
        reference_kind = value["reference_kind"]
        if reference_kind == "project_workspace":
            return ProjectWorkspaceReference(
                project_id=value["project_id"],
                title=value["title"],
                lifecycle=value["lifecycle"],
                project_revision=value["project_revision"],
                workspace_revision=value["workspace_revision"],
                destination=value["destination"],
                target_status=value["target_status"],
                validated_at=self._timestamp(value["validated_at"]),
            )
        if reference_kind == "project_snapshot":
            return ProjectSnapshotReference(
                project_id=value["project_id"],
                snapshot_id=value["snapshot_id"],
                title=value["title"],
                lifecycle=value["lifecycle"],
                project_revision=value["project_revision"],
                workspace_revision=value["workspace_revision"],
                snapshot_digest=value["snapshot_digest"],
                closed_at=self._timestamp(value["closed_at"]),
                destination=value["destination"],
                target_status=value["target_status"],
                validated_at=self._timestamp(value["validated_at"]),
            )
        if reference_kind == "project_artifact":
            return ProjectArtifactReference(
                project_id=value["project_id"],
                artifact_id=value["artifact_id"],
                artifact_version=value["artifact_version"],
                title=value["title"],
                lifecycle=value["lifecycle"],
                project_revision=value["project_revision"],
                workspace_revision=value["workspace_revision"],
                artifact_kind=value["artifact_kind"],
                logical_path=value["logical_path"],
                media_type=value["media_type"],
                inspection_mode=value["inspection_mode"],
                byte_count=value["byte_count"],
                content_digest=value["content_digest"],
                created_at=self._timestamp(value["created_at"]),
                destination=value["destination"],
                target_status=value["target_status"],
                validated_at=self._timestamp(value["validated_at"]),
            )
        provenance = PublicationProvenance(
            published_by=value["provenance"]["published_by"],
            published_at=self._timestamp(value["provenance"]["published_at"]),
            content_reviewed_on=value["provenance"]["content_reviewed_on"],
            educational_use_notice=value["provenance"]["educational_use_notice"],
        )
        common = {
            "placement_id": value["placement_id"],
            "package_id": value["package_id"],
            "package_version": value["package_version"],
            "package_digest": value["package_digest"],
            "title": value["title"],
            "destination": value["destination"],
            "target_status": value["target_status"],
            "provenance": provenance,
            "validated_at": self._timestamp(value["validated_at"]),
        }
        if reference_kind == "learning_opportunity":
            return LearningOpportunityReference(
                opportunity_id=value["opportunity_id"],
                source_fingerprint=value["source_fingerprint"],
                **common,
            )
        return PlacedLessonReference(**common)

    def _validate_workspace_semantics(self, document: Mapping[str, Any]) -> None:
        created_at = self._timestamp(document["created_at"])
        updated_at = self._timestamp(document["updated_at"])
        if updated_at < created_at:
            self._reject("personal_workspace.contract.invalid_time", "updated_at")
        record_ids = [item["record_id"] for item in document["records"]]
        collection_ids = [item["collection_id"] for item in document["collections"]]
        self._unique(record_ids, "records.record_id")
        self._unique(collection_ids, "collections.collection_id")
        if set(record_ids) & set(collection_ids):
            self._reject("personal_workspace.contract.duplicate_id", "workspace")
        known = set(record_ids)
        for item in document["records"]:
            record_created_at = self._timestamp(item["created_at"])
            record_updated_at = self._timestamp(item["updated_at"])
            if record_created_at < created_at or record_updated_at < record_created_at:
                self._reject("personal_workspace.contract.invalid_time", item["record_id"])
            if record_updated_at > updated_at:
                self._reject("personal_workspace.contract.invalid_time", item["record_id"])
            self._validate_reference_semantics(item["target"])
            if self._timestamp(item["target"]["validated_at"]) > record_updated_at:
                self._reject(
                    "personal_workspace.contract.invalid_time",
                    item["record_id"],
                )
        for collection in document["collections"]:
            members = collection["member_record_ids"]
            self._unique(members, f"collections.{collection['collection_id']}.members")
            if not set(members).issubset(known):
                self._reject(
                    "personal_workspace.contract.dangling_member",
                    collection["collection_id"],
                )
            collection_created_at = self._timestamp(collection["created_at"])
            collection_updated_at = self._timestamp(collection["updated_at"])
            if (
                collection_created_at < created_at
                or collection_updated_at < collection_created_at
                or collection_updated_at > updated_at
            ):
                self._reject(
                    "personal_workspace.contract.invalid_time",
                    collection["collection_id"],
                )
        material = dict(document)
        observed = material.pop("workspace_digest")
        if observed != self.canonical_digest(material):
            self._reject(
                "personal_workspace.contract.digest_mismatch",
                "workspace_digest",
            )

    def _validate_mutation_semantics(self, document: Mapping[str, Any]) -> None:
        mutation = document["mutation"]
        if mutation["operation"] in {"create_note", "create_bookmark"}:
            self._validate_reference_semantics(mutation["target"])

    def _validate_reference_semantics(self, value: Mapping[str, Any]) -> None:
        reference_kind = value["reference_kind"]
        validated_at = self._timestamp(value["validated_at"])
        if reference_kind == "project_workspace":
            expected = f"/projects/{value['project_id']}#workspace"
            if value["destination"] != expected:
                self._reject(
                    "personal_workspace.contract.invalid_reference",
                    "destination",
                )
            return
        if reference_kind == "project_snapshot":
            expected = (
                f"/projects/{value['project_id']}#snapshot-{value['snapshot_id']}"
            )
            if value["destination"] != expected:
                self._reject(
                    "personal_workspace.contract.invalid_reference",
                    "destination",
                )
            if self._timestamp(value["closed_at"]) > validated_at:
                self._reject(
                    "personal_workspace.contract.invalid_time",
                    "reference",
                )
            return
        if reference_kind == "project_artifact":
            self._validate_project_logical_path(value["logical_path"])
            expected = (
                f"/projects/{value['project_id']}#artifact-"
                f"{value['artifact_id']}-v{value['artifact_version']}"
            )
            if value["destination"] != expected:
                self._reject(
                    "personal_workspace.contract.invalid_reference",
                    "destination",
                )
            if self._timestamp(value["created_at"]) > validated_at:
                self._reject(
                    "personal_workspace.contract.invalid_time",
                    "reference",
                )
            return
        placement_id = value["placement_id"]
        if value["destination"] != f"/learn/placements/{placement_id}":
            self._reject(
                "personal_workspace.contract.invalid_reference",
                "destination",
            )
        published_at = self._timestamp(value["provenance"]["published_at"])
        if published_at > validated_at:
            self._reject(
                "personal_workspace.contract.invalid_time",
                "reference",
            )

    def _validate_project_logical_path(self, value: str) -> None:
        """Preserve Project's canonical path profile at the copied boundary."""

        if not is_canonical_project_logical_path(value):
            self._reject(
                "personal_workspace.contract.invalid_reference",
                "logical_path",
            )

    def _new_id(
        self,
        issued_id: str | None,
        records: list[WorkspaceRecord],
        collections: list[WorkspaceCollection],
    ) -> str:
        if issued_id is None:
            self._reject("personal_workspace.contract.issued_id_required", "issued_id")
        known = {item.record_id for item in records} | {
            item.collection_id for item in collections
        }
        if issued_id in known:
            self._reject("personal_workspace.contract.duplicate_id", issued_id)
        return issued_id

    def _record(
        self,
        records: list[WorkspaceRecord],
        record_id: str,
    ) -> tuple[int, WorkspaceRecord]:
        for index, record in enumerate(records):
            if record.record_id == record_id:
                return index, record
        self._reject("personal_workspace.contract.record_not_found", record_id)

    def _collection(
        self,
        collections: list[WorkspaceCollection],
        collection_id: str,
    ) -> tuple[int, WorkspaceCollection]:
        for index, collection in enumerate(collections):
            if collection.collection_id == collection_id:
                return index, collection
        self._reject("personal_workspace.contract.collection_not_found", collection_id)

    def _same_unique_ids(
        self,
        values: tuple[str, ...],
        known: set[str],
        reference: str,
        *,
        allow_subset: bool = False,
    ) -> None:
        self._unique(values, reference)
        observed = set(values)
        if (allow_subset and not observed.issubset(known)) or (
            not allow_subset and observed != known
        ):
            self._reject("personal_workspace.contract.invalid_membership", reference)

    def _unique(self, values: Any, reference: str) -> None:
        if len(values) != len(set(values)):
            self._reject("personal_workspace.contract.duplicate_id", reference)

    def _timestamp(self, value: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            self._reject("personal_workspace.contract.invalid_time", "timestamp")
        return self._aware_timestamp(parsed, "timestamp")

    def _aware_timestamp(self, value: datetime, reference: str) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            self._reject("personal_workspace.contract.invalid_time", reference)
        return value.astimezone(timezone.utc)

    def _format_timestamp(self, value: datetime) -> str:
        return self._aware_timestamp(value, "timestamp").isoformat().replace(
            "+00:00", "Z"
        )

    def _portable(self, value: Any) -> Any:
        if isinstance(value, datetime):
            return self._format_timestamp(value)
        if is_dataclass(value):
            return self._portable(asdict(value))
        if isinstance(value, Mapping):
            return {key: self._portable(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._portable(item) for item in value]
        return value

    def _canonical_bytes(self, value: Mapping[str, object]) -> bytes:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def _reject(self, code: str, reference: str) -> Never:
        raise PersonalWorkspaceContractFailure(code, reference)
