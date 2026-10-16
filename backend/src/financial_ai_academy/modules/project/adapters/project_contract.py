"""Closed parser and projector for Project workspace v1."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping
import unicodedata
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker

from ..domain.project import (
    IndependentProjectOrigin,
    LearningProjectBrief,
    LearningProjectOrigin,
    ProjectCreateIntent,
    ProjectMilestone,
    ProjectOrigin,
    ProjectShell,
    ProjectSourceReference,
)
from ..domain.workspace import (
    AddArtifactMutation,
    AddDomainLinkMutation,
    AddNoteMutation,
    AddReferenceMutation,
    ArtifactKind,
    ArtifactProvenance,
    DomainLinkType,
    EvidenceArtifactFile,
    EvidenceClassification,
    ExcludedEvidenceArtifact,
    InspectionMode,
    ProjectArtifact,
    ProjectArtifactInput,
    ProjectArtifactReference,
    ProjectDomainLink,
    ProjectDomainLinkInput,
    ProjectDomainLinkReference,
    ProjectEnvironment,
    ProjectEvidenceExport,
    ProjectEvidenceExportMaterial,
    ProjectNote,
    ProjectReference,
    ProjectSnapshot,
    ProjectSnapshotCloseIntent,
    ProjectSnapshotMaterial,
    ProjectVersionReference,
    ProjectWorkspace,
    ProvenanceSourceType,
    RemoveDomainLinkMutation,
    ReplaceNoteMutation,
    ReplaceReferenceMutation,
    WorkspaceMutationIntent,
)
from ..ports.project_contract import ProjectContractFailure


VERSION = "1.0.0"


class ContractProjectAdapter:
    """Validate bytes and return immutable Project-owned values."""

    def __init__(self, schema_dir: Path) -> None:
        self._validators: dict[str, Draft202012Validator] = {}
        for name in (
            "brief",
            "create-intent",
            "shell",
            "workspace",
            "workspace-mutation-intent",
            "snapshot-close-intent",
            "snapshot",
            "evidence-export",
        ):
            schema = json.loads(
                (schema_dir / f"{name}.schema.json").read_text(encoding="utf-8")
            )
            Draft202012Validator.check_schema(schema)
            self._validators[name] = Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            )

    def parse_brief(self, value: bytes) -> LearningProjectBrief:
        document = self._document(value, "brief")
        self._version(document)
        self._validate_brief_document(document)
        brief = document["brief"]
        return LearningProjectBrief(
            schema_version=document["schema_version"],
            brief_id=brief["brief_id"],
            brief_version=brief["brief_version"],
            brief_digest=document["brief_digest"],
            title=brief["title"],
            purpose=brief["purpose"],
            milestones=tuple(
                ProjectMilestone(
                    milestone_id=item["milestone_id"],
                    description=item["description"],
                )
                for item in brief["milestones"]
            ),
            source_references=tuple(
                ProjectSourceReference(
                    resource_id=item["resource_id"],
                    resource_version=item["resource_version"],
                    resource_digest=item["resource_digest"],
                    title=item["title"],
                )
                for item in brief["source_references"]
            ),
        )

    def parse_intent(
        self,
        value: bytes,
        *,
        approved_brief: LearningProjectBrief | None = None,
    ) -> ProjectCreateIntent:
        document = self._document(value, "create-intent")
        self._version(document)
        self._shape("create-intent", document)
        origin = self._origin(document["origin"])
        if isinstance(origin, LearningProjectOrigin):
            if approved_brief is None:
                self._reject(
                    "project.contract.learning_brief_required",
                    "origin.brief_id",
                )
            self._correlate_brief(origin, approved_brief)
        return ProjectCreateIntent(
            schema_version=document["schema_version"],
            idempotency_key=document["idempotency_key"],
            title=document["title"],
            charter=document["charter"],
            origin=origin,
        )

    def parse_shell(self, value: bytes) -> ProjectShell:
        document = self._document(value, "shell")
        self._version(document)
        self._shape("shell", document)
        created_at = self._timestamp(document["created_at"])
        updated_at = self._timestamp(document["updated_at"])
        if updated_at < created_at:
            self._reject("project.contract.invalid_shell", "updated_at")
        return ProjectShell(
            schema_version=document["schema_version"],
            project_id=document["project_id"],
            learner_id=document["learner_id"],
            title=document["title"],
            charter=document["charter"],
            origin=self._origin(document["origin"]),
            lifecycle=document["lifecycle"],
            revision=document["revision"],
            created_at=created_at,
            updated_at=updated_at,
        )

    def parse_workspace(self, value: bytes) -> ProjectWorkspace:
        document = self._document(value, "workspace")
        self._version(document)
        self._validate_workspace_document(document)
        return ProjectWorkspace(
            schema_version=document["schema_version"],
            project_id=document["project_id"],
            learner_id=document["learner_id"],
            workspace_revision=document["workspace_revision"],
            notes=tuple(self._note(item) for item in document["notes"]),
            references=tuple(
                self._reference(item) for item in document["references"]
            ),
            artifacts=tuple(
                self._artifact(item) for item in document["artifacts"]
            ),
            domain_links=tuple(
                self._domain_link(item) for item in document["domain_links"]
            ),
            created_at=self._timestamp(document["created_at"]),
            updated_at=self._timestamp(document["updated_at"]),
        )

    def parse_workspace_mutation_intent(
        self,
        value: bytes,
    ) -> WorkspaceMutationIntent:
        document = self._document(value, "workspace-mutation-intent")
        self._version(document)
        self._shape("workspace-mutation-intent", document)
        mutation = document["mutation"]
        operation = mutation["operation"]
        if operation == "add_note":
            parsed = AddNoteMutation(
                title=mutation["title"],
                body=mutation["body"],
            )
        elif operation == "replace_note":
            parsed = ReplaceNoteMutation(
                note_id=mutation["note_id"],
                expected_note_version=mutation["expected_note_version"],
                title=mutation["title"],
                body=mutation["body"],
            )
        elif operation == "add_reference":
            self._validate_url(mutation["url"], "mutation.url")
            parsed = self._reference_mutation(mutation, replacement=False)
        elif operation == "replace_reference":
            self._validate_url(mutation["url"], "mutation.url")
            parsed = self._reference_mutation(mutation, replacement=True)
        elif operation == "add_artifact":
            artifact = self._artifact_input(mutation["artifact"])
            self._validate_artifact_semantics(mutation["artifact"])
            parsed = AddArtifactMutation(artifact=artifact)
        elif operation == "add_domain_link":
            parsed = AddDomainLinkMutation(
                link=self._domain_link_input(mutation["link"])
            )
        else:
            parsed = RemoveDomainLinkMutation(link_id=mutation["link_id"])
        return WorkspaceMutationIntent(
            schema_version=document["schema_version"],
            idempotency_key=document["idempotency_key"],
            expected_workspace_revision=document["expected_workspace_revision"],
            mutation=parsed,
        )

    def parse_snapshot_close_intent(
        self,
        value: bytes,
    ) -> ProjectSnapshotCloseIntent:
        document = self._document(value, "snapshot-close-intent")
        self._version(document)
        self._shape("snapshot-close-intent", document)
        return ProjectSnapshotCloseIntent(
            schema_version=document["schema_version"],
            idempotency_key=document["idempotency_key"],
            expected_project_revision=document["expected_project_revision"],
            expected_workspace_revision=document["expected_workspace_revision"],
        )

    def parse_snapshot(self, value: bytes) -> ProjectSnapshot:
        document = self._document(value, "snapshot")
        self._version(document)
        self._validate_snapshot_document(document)
        snapshot = document["snapshot"]
        return ProjectSnapshot(
            schema_version=document["schema_version"],
            snapshot_id=document["snapshot_id"],
            snapshot_digest=document["snapshot_digest"],
            snapshot=ProjectSnapshotMaterial(
                project_id=snapshot["project_id"],
                learner_id=snapshot["learner_id"],
                project_revision=snapshot["project_revision"],
                project_shell_digest=snapshot["project_shell_digest"],
                workspace_revision=snapshot["workspace_revision"],
                workspace_created_at=self._timestamp(
                    snapshot["workspace_created_at"]
                ),
                workspace_updated_at=self._timestamp(
                    snapshot["workspace_updated_at"]
                ),
                notes=tuple(
                    ProjectVersionReference(**item) for item in snapshot["notes"]
                ),
                references=tuple(
                    ProjectVersionReference(**item)
                    for item in snapshot["references"]
                ),
                artifacts=tuple(
                    ProjectArtifactReference(**item)
                    for item in snapshot["artifacts"]
                ),
                domain_links=tuple(
                    ProjectDomainLinkReference(**item)
                    for item in snapshot["domain_links"]
                ),
            ),
            closed_at=self._timestamp(document["closed_at"]),
        )

    def parse_evidence_export(self, value: bytes) -> ProjectEvidenceExport:
        document = self._document(value, "evidence-export")
        self._version(document)
        self._validate_evidence_export_document(document)
        exported = document["export"]
        return ProjectEvidenceExport(
            schema_version=document["schema_version"],
            export_id=document["export_id"],
            export_digest=document["export_digest"],
            export=ProjectEvidenceExportMaterial(
                project_id=exported["project_id"],
                snapshot_id=exported["snapshot_id"],
                snapshot_digest=exported["snapshot_digest"],
                snapshot_record=self.parse_snapshot(
                    self._canonical_bytes(exported["snapshot_record"])
                ),
                workspace_record=self.parse_workspace(
                    self._canonical_bytes(exported["workspace_record"])
                ),
                artifact_files=tuple(
                    EvidenceArtifactFile(**item)
                    for item in exported["artifact_files"]
                ),
                excluded_artifacts=tuple(
                    ExcludedEvidenceArtifact(**item)
                    for item in exported["excluded_artifacts"]
                ),
            ),
            generated_at=self._timestamp(document["generated_at"]),
        )

    def brief_document(self, value: LearningProjectBrief) -> dict[str, object]:
        brief = {
            "brief_id": value.brief_id,
            "brief_version": value.brief_version,
            "title": value.title,
            "purpose": value.purpose,
            "milestones": [asdict(item) for item in value.milestones],
            "source_references": [
                asdict(item) for item in value.source_references
            ],
        }
        document: dict[str, object] = {
            "schema_version": value.schema_version,
            "brief_digest": value.brief_digest,
            "brief": brief,
        }
        self._validate_brief_document(document)
        return document

    def intent_document(self, value: ProjectCreateIntent) -> dict[str, object]:
        document: dict[str, object] = {
            "schema_version": value.schema_version,
            "idempotency_key": value.idempotency_key,
            "title": value.title,
            "charter": value.charter,
            "origin": asdict(value.origin),
        }
        self._shape("create-intent", document)
        return document

    def shell_document(self, value: ProjectShell) -> dict[str, object]:
        created_at = self._aware_timestamp(value.created_at, "created_at")
        updated_at = self._aware_timestamp(value.updated_at, "updated_at")
        if updated_at < created_at:
            self._reject("project.contract.invalid_shell", "updated_at")
        document: dict[str, object] = {
            "schema_version": value.schema_version,
            "project_id": value.project_id,
            "learner_id": value.learner_id,
            "title": value.title,
            "charter": value.charter,
            "origin": asdict(value.origin),
            "lifecycle": value.lifecycle,
            "revision": value.revision,
            "created_at": self._format_timestamp(created_at),
            "updated_at": self._format_timestamp(updated_at),
        }
        self._shape("shell", document)
        return document

    def workspace_document(self, value: ProjectWorkspace) -> dict[str, object]:
        document = self._portable(value)
        self._validate_workspace_document(document)
        return document

    def workspace_mutation_intent_document(
        self,
        value: WorkspaceMutationIntent,
    ) -> dict[str, object]:
        document = self._portable(value)
        self._shape("workspace-mutation-intent", document)
        mutation = document["mutation"]
        if mutation["operation"] in {"add_reference", "replace_reference"}:
            self._validate_url(mutation["url"], "mutation.url")
        if mutation["operation"] == "add_artifact":
            self._validate_artifact_semantics(mutation["artifact"])
        return document

    def snapshot_close_intent_document(
        self,
        value: ProjectSnapshotCloseIntent,
    ) -> dict[str, object]:
        document = self._portable(value)
        self._shape("snapshot-close-intent", document)
        return document

    def snapshot_document(self, value: ProjectSnapshot) -> dict[str, object]:
        document = self._portable(value)
        self._validate_snapshot_document(document)
        return document

    def evidence_export_document(
        self,
        value: ProjectEvidenceExport,
    ) -> dict[str, object]:
        document = self._portable(value)
        self._validate_evidence_export_document(document)
        return document

    def canonical_digest(self, value: Mapping[str, object]) -> str:
        return hashlib.sha256(self._canonical_bytes(value)).hexdigest()

    def _validate_workspace_document(self, document: Mapping[str, Any]) -> None:
        self._shape("workspace", document)
        created_at = self._timestamp(document["created_at"])
        updated_at = self._timestamp(document["updated_at"])
        if updated_at < created_at:
            self._reject("project.contract.invalid_workspace", "updated_at")
        self._unique(
            [item["note_id"] for item in document["notes"]],
            "notes",
            code="project.contract.duplicate_workspace_record",
        )
        self._unique(
            [item["reference_id"] for item in document["references"]],
            "references",
            code="project.contract.duplicate_workspace_record",
        )
        self._unique(
            [item["artifact_id"] for item in document["artifacts"]],
            "artifacts",
            code="project.contract.duplicate_workspace_record",
        )
        self._unique(
            [item["logical_path"] for item in document["artifacts"]],
            "artifacts.logical_path",
            code="project.contract.duplicate_workspace_record",
        )
        self._unique(
            [
                self._logical_path_key(item["logical_path"])
                for item in document["artifacts"]
            ],
            "artifacts.logical_path",
            code="project.contract.duplicate_workspace_record",
        )
        self._unique(
            [item["link_id"] for item in document["domain_links"]],
            "domain_links",
            code="project.contract.duplicate_workspace_record",
        )
        for note in document["notes"]:
            if self._timestamp(note["updated_at"]) < self._timestamp(
                note["created_at"]
            ):
                self._reject(
                    "project.contract.invalid_workspace",
                    f"notes.{note['note_id']}.updated_at",
                )
        for reference in document["references"]:
            self._validate_url(reference["url"], "references.url")
            if self._timestamp(reference["updated_at"]) < self._timestamp(
                reference["created_at"]
            ):
                self._reject(
                    "project.contract.invalid_workspace",
                    f"references.{reference['reference_id']}.updated_at",
                )
        for artifact in document["artifacts"]:
            self._validate_artifact_semantics(artifact)

    def _validate_artifact_semantics(self, artifact: Mapping[str, Any]) -> None:
        self._validate_logical_path(artifact["logical_path"])
        kind = artifact["artifact_kind"]
        classification = artifact.get("result_classification")
        if kind == "result" and classification is None:
            self._reject(
                "project.contract.result_classification_required",
                "result_classification",
            )
        if kind != "result" and classification not in (None, "narrative"):
            self._reject(
                "project.contract.invalid_artifact_classification",
                "result_classification",
            )
        if artifact["inspection_mode"] == "plain_text" and not str(
            artifact["media_type"]
        ).startswith("text/"):
            self._reject(
                "project.contract.unsafe_inspection_mode",
                "inspection_mode",
            )
        provenance = artifact["provenance"]
        if provenance.get("source_url") is not None:
            self._validate_url(provenance["source_url"], "provenance.source_url")
        if provenance["source_type"] in {"supplied", "external"} and not (
            provenance.get("source_version")
            or provenance.get("source_digest")
        ):
            self._reject(
                "project.contract.incomplete_provenance",
                "provenance",
            )

    def _validate_snapshot_document(self, document: Mapping[str, Any]) -> None:
        self._shape("snapshot", document)
        snapshot = document["snapshot"]
        measured = self.canonical_digest(snapshot)
        if measured != document["snapshot_digest"]:
            self._reject(
                "project.contract.snapshot_digest_mismatch",
                "snapshot_digest",
            )
        if self._timestamp(snapshot["workspace_updated_at"]) < self._timestamp(
            snapshot["workspace_created_at"]
        ):
            self._reject(
                "project.contract.invalid_snapshot",
                "snapshot.workspace_updated_at",
            )
        if self._timestamp(document["closed_at"]) < self._timestamp(
            snapshot["workspace_updated_at"]
        ):
            self._reject(
                "project.contract.invalid_snapshot",
                "closed_at",
            )
        self._unique(
            [item["record_id"] for item in snapshot["notes"]],
            "snapshot.notes",
            code="project.contract.duplicate_snapshot_reference",
        )
        self._unique(
            [item["record_id"] for item in snapshot["references"]],
            "snapshot.references",
            code="project.contract.duplicate_snapshot_reference",
        )
        self._unique(
            [item["artifact_id"] for item in snapshot["artifacts"]],
            "snapshot.artifacts",
            code="project.contract.duplicate_snapshot_reference",
        )
        self._unique(
            [item["link_id"] for item in snapshot["domain_links"]],
            "snapshot.domain_links",
            code="project.contract.duplicate_snapshot_reference",
        )

    def _validate_evidence_export_document(
        self,
        document: Mapping[str, Any],
    ) -> None:
        self._shape("evidence-export", document)
        exported = document["export"]
        self._validate_snapshot_document(exported["snapshot_record"])
        self._validate_workspace_document(exported["workspace_record"])
        measured = self.canonical_digest(exported)
        if measured != document["export_digest"]:
            self._reject(
                "project.contract.export_digest_mismatch",
                "export_digest",
            )
        included = {
            (item["artifact_id"], item["artifact_version"])
            for item in exported["artifact_files"]
        }
        excluded = {
            (item["artifact_id"], item["artifact_version"])
            for item in exported["excluded_artifacts"]
        }
        if len(included) != len(exported["artifact_files"]):
            self._reject(
                "project.contract.duplicate_export_artifact",
                "export.artifact_files",
            )
        if len(excluded) != len(exported["excluded_artifacts"]):
            self._reject(
                "project.contract.duplicate_export_artifact",
                "export.excluded_artifacts",
            )
        if included & excluded:
            self._reject(
                "project.contract.contradictory_export_artifact",
                "export",
            )
        snapshot_record = exported["snapshot_record"]
        snapshot = snapshot_record["snapshot"]
        workspace = exported["workspace_record"]
        if (
            exported["project_id"] != snapshot["project_id"]
            or exported["project_id"] != workspace["project_id"]
            or exported["snapshot_id"] != snapshot_record["snapshot_id"]
            or exported["snapshot_digest"] != snapshot_record["snapshot_digest"]
            or snapshot["learner_id"] != workspace["learner_id"]
            or snapshot["workspace_revision"] != workspace["workspace_revision"]
            or snapshot["workspace_created_at"] != workspace["created_at"]
            or snapshot["workspace_updated_at"] != workspace["updated_at"]
        ):
            self._reject(
                "project.contract.export_snapshot_mismatch",
                "export.snapshot_record",
            )
        self._validate_export_record_bindings(snapshot, workspace)
        artifact_records = {
            (item["artifact_id"], item["artifact_version"]): item
            for item in workspace["artifacts"]
        }
        expected = {
            (item["artifact_id"], item["artifact_version"])
            for item in snapshot["artifacts"]
        }
        if included | excluded != expected:
            self._reject(
                "project.contract.incomplete_export_coverage",
                "export",
            )
        for item in exported["artifact_files"]:
            identity = (item["artifact_id"], item["artifact_version"])
            artifact = artifact_records.get(identity)
            if artifact is None or (
                item["manifest_digest"] != self.canonical_digest(artifact)
                or item["logical_path"] != artifact["logical_path"]
                or item["media_type"] != artifact["media_type"]
                or item["byte_count"] != artifact["byte_count"]
                or item["content_digest"] != artifact["content_digest"]
            ):
                self._reject(
                    "project.contract.export_artifact_mismatch",
                    "export.artifact_files",
                )

    def _validate_export_record_bindings(
        self,
        snapshot: Mapping[str, Any],
        workspace: Mapping[str, Any],
    ) -> None:
        bindings = (
            (
                "notes",
                "note_id",
                "note_version",
                "record_id",
                "record_version",
                "record_digest",
            ),
            (
                "references",
                "reference_id",
                "reference_version",
                "record_id",
                "record_version",
                "record_digest",
            ),
            (
                "artifacts",
                "artifact_id",
                "artifact_version",
                "artifact_id",
                "artifact_version",
                "manifest_digest",
            ),
            ("domain_links", "link_id", None, "link_id", None, "record_digest"),
        )
        for (
            key,
            record_id,
            record_version,
            ref_id,
            ref_version,
            digest_key,
        ) in bindings:
            records = workspace[key]
            references = snapshot[key]
            if len(records) != len(references):
                self._reject(
                    "project.contract.export_record_mismatch",
                    f"export.{key}",
                )
            for reference, record in zip(references, records, strict=True):
                reference_identity = (
                    reference[ref_id],
                    reference[ref_version] if ref_version else None,
                )
                record_identity = (
                    record[record_id],
                    record[record_version] if record_version else None,
                )
                if reference_identity != record_identity or reference[
                    digest_key
                ] != self.canonical_digest(record):
                    self._reject(
                        "project.contract.export_record_mismatch",
                        f"export.{key}",
                    )

    def _validate_logical_path(self, value: str) -> None:
        if unicodedata.normalize("NFC", value) != value:
            self._reject(
                "project.contract.noncanonical_logical_path",
                "logical_path",
            )
        segments = value.split("/")
        reserved = re.compile(
            r"^(?:con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?:\..*)?$",
            re.IGNORECASE,
        )
        if any(
            not segment
            or segment in {".", ".."}
            or segment != segment.strip()
            or segment.endswith(".")
            or any(
                ord(character) < 32 or character in '<>:"|?*'
                for character in segment
            )
            or reserved.fullmatch(segment)
            for segment in segments
        ):
            self._reject(
                "project.contract.noncanonical_logical_path",
                "logical_path",
            )

    @staticmethod
    def _logical_path_key(value: str) -> str:
        return unicodedata.normalize("NFC", value).casefold()

    def _validate_url(self, value: str, reference: str) -> None:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "https"
            or parsed.hostname is None
            or parsed.username is not None
            or parsed.password is not None
        ):
            self._reject("project.contract.unsafe_url", reference)

    def _note(self, value: Mapping[str, Any]) -> ProjectNote:
        return ProjectNote(
            note_id=value["note_id"],
            note_version=value["note_version"],
            title=value["title"],
            body=value["body"],
            created_at=self._timestamp(value["created_at"]),
            updated_at=self._timestamp(value["updated_at"]),
        )

    def _reference(self, value: Mapping[str, Any]) -> ProjectReference:
        return ProjectReference(
            reference_id=value["reference_id"],
            reference_version=value["reference_version"],
            title=value["title"],
            url=value["url"],
            source_name=value["source_name"],
            source_version=value.get("source_version"),
            source_digest=value.get("source_digest"),
            license=value.get("license"),
            use_constraints=value.get("use_constraints"),
            created_at=self._timestamp(value["created_at"]),
            updated_at=self._timestamp(value["updated_at"]),
        )

    def _provenance(self, value: Mapping[str, Any]) -> ArtifactProvenance:
        return ArtifactProvenance(
            source_type=ProvenanceSourceType(value["source_type"]),
            source_title=value["source_title"],
            source_version=value.get("source_version"),
            source_url=value.get("source_url"),
            source_digest=value.get("source_digest"),
            license=value.get("license"),
            use_constraints=value.get("use_constraints"),
        )

    def _environment(
        self,
        value: Mapping[str, Any] | None,
    ) -> ProjectEnvironment | None:
        if value is None:
            return None
        return ProjectEnvironment(
            name=value["name"],
            version=value["version"],
            dependency_digest=value.get("dependency_digest"),
        )

    def _artifact_input(self, value: Mapping[str, Any]) -> ProjectArtifactInput:
        return ProjectArtifactInput(
            artifact_kind=ArtifactKind(value["artifact_kind"]),
            logical_path=value["logical_path"],
            media_type=value["media_type"],
            inspection_mode=InspectionMode(value["inspection_mode"]),
            byte_count=value["byte_count"],
            content_digest=value["content_digest"],
            result_classification=(
                EvidenceClassification(value["result_classification"])
                if value.get("result_classification") is not None
                else None
            ),
            provenance=self._provenance(value["provenance"]),
            environment=self._environment(value.get("environment")),
            assumptions=tuple(value["assumptions"]),
        )

    def _artifact(self, value: Mapping[str, Any]) -> ProjectArtifact:
        artifact = self._artifact_input(value)
        return ProjectArtifact(
            artifact_kind=artifact.artifact_kind,
            logical_path=artifact.logical_path,
            media_type=artifact.media_type,
            inspection_mode=artifact.inspection_mode,
            byte_count=artifact.byte_count,
            content_digest=artifact.content_digest,
            result_classification=artifact.result_classification,
            provenance=artifact.provenance,
            environment=artifact.environment,
            assumptions=artifact.assumptions,
            artifact_id=value["artifact_id"],
            artifact_version=value["artifact_version"],
            created_at=self._timestamp(value["created_at"]),
        )

    def _domain_link_input(
        self,
        value: Mapping[str, Any],
    ) -> ProjectDomainLinkInput:
        return ProjectDomainLinkInput(
            link_type=DomainLinkType(value["link_type"]),
            owner_module=value["owner_module"],
            resource_type=value["resource_type"],
            resource_id=value["resource_id"],
            resource_version=value.get("resource_version"),
            resource_as_of=(
                self._timestamp(value["resource_as_of"])
                if value.get("resource_as_of") is not None
                else None
            ),
            provenance=value["provenance"],
        )

    def _domain_link(self, value: Mapping[str, Any]) -> ProjectDomainLink:
        link = self._domain_link_input(value)
        return ProjectDomainLink(
            link_type=link.link_type,
            owner_module=link.owner_module,
            resource_type=link.resource_type,
            resource_id=link.resource_id,
            resource_version=link.resource_version,
            resource_as_of=link.resource_as_of,
            provenance=link.provenance,
            link_id=value["link_id"],
            owner_reference_digest=value["owner_reference_digest"],
            target_status=value["target_status"],
            validated_at=self._timestamp(value["validated_at"]),
            created_at=self._timestamp(value["created_at"]),
        )

    def _reference_mutation(
        self,
        value: Mapping[str, Any],
        *,
        replacement: bool,
    ) -> AddReferenceMutation | ReplaceReferenceMutation:
        common = {
            "title": value["title"],
            "url": value["url"],
            "source_name": value["source_name"],
            "source_version": value.get("source_version"),
            "source_digest": value.get("source_digest"),
            "license": value.get("license"),
            "use_constraints": value.get("use_constraints"),
        }
        if replacement:
            return ReplaceReferenceMutation(
                reference_id=value["reference_id"],
                expected_reference_version=value["expected_reference_version"],
                **common,
            )
        return AddReferenceMutation(**common)

    @classmethod
    def _portable(cls, value: object) -> dict[str, Any]:
        if not is_dataclass(value):
            raise TypeError("Project contract projection requires a dataclass.")
        projected = cls._portable_value(asdict(value))
        if not isinstance(projected, dict):
            raise TypeError("Project contract projection requires an object.")
        return projected

    @classmethod
    def _portable_value(cls, value: object) -> object:
        if isinstance(value, datetime):
            return cls._format_timestamp(cls._aware_timestamp(value, "time"))
        if isinstance(value, Mapping):
            return {
                key: cls._portable_value(nested)
                for key, nested in value.items()
                if nested is not None
            }
        if isinstance(value, (list, tuple)):
            return [cls._portable_value(nested) for nested in value]
        return value

    @staticmethod
    def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

    @staticmethod
    def _document(value: bytes, reference: str) -> dict[str, Any]:
        try:
            document = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ProjectContractFailure(
                "project.contract.schema_invalid",
                reference,
            ) from error
        if not isinstance(document, dict):
            raise ProjectContractFailure(
                "project.contract.schema_invalid",
                reference,
            )
        return document

    def _version(self, document: Mapping[str, Any]) -> None:
        if document.get("schema_version") != VERSION:
            self._reject(
                "project.contract.unsupported_version",
                "schema_version",
            )

    def _shape(self, kind: str, document: Mapping[str, Any]) -> None:
        error = next(iter(self._validators[kind].iter_errors(document)), None)
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            self._reject(
                "project.contract.schema_invalid",
                reference or kind,
            )

    def _validate_brief_document(self, document: Mapping[str, Any]) -> None:
        self._shape("brief", document)
        brief = document["brief"]
        measured = hashlib.sha256(self._canonical_bytes(brief)).hexdigest()
        if measured != document["brief_digest"]:
            self._reject(
                "project.contract.brief_digest_mismatch",
                "brief_digest",
            )
        self._unique(
            [item["milestone_id"] for item in brief["milestones"]],
            "brief.milestones",
        )
        self._unique(
            [item["resource_id"] for item in brief["source_references"]],
            "brief.source_references",
        )

    def _unique(
        self,
        values: list[str],
        reference: str,
        *,
        code: str = "project.contract.invalid_brief",
    ) -> None:
        if len(values) != len(set(values)):
            self._reject(code, reference)

    @staticmethod
    def _origin(value: Mapping[str, Any]) -> ProjectOrigin:
        if value["origin_type"] == "independent":
            return IndependentProjectOrigin()
        return LearningProjectOrigin(
            project_brief_schema_version=value["project_brief_schema_version"],
            package_id=value["package_id"],
            package_version=value["package_version"],
            package_digest=value["package_digest"],
            brief_id=value["brief_id"],
            brief_version=value["brief_version"],
            brief_digest=value["brief_digest"],
            curriculum_id=value["curriculum_id"],
            curriculum_version=value["curriculum_version"],
            curriculum_digest=value["curriculum_digest"],
            placement_id=value["placement_id"],
            placement_version=value["placement_version"],
            placement_digest=value["placement_digest"],
            brief_title=value["brief_title"],
            brief_purpose=value["brief_purpose"],
        )

    def _correlate_brief(
        self,
        origin: LearningProjectOrigin,
        brief: LearningProjectBrief,
    ) -> None:
        expected = (
            brief.schema_version,
            brief.brief_id,
            brief.brief_version,
            brief.brief_digest,
            brief.title,
            brief.purpose,
        )
        actual = (
            origin.project_brief_schema_version,
            origin.brief_id,
            origin.brief_version,
            origin.brief_digest,
            origin.brief_title,
            origin.brief_purpose,
        )
        if actual != expected:
            self._reject(
                "project.contract.stale_learning_reference",
                "origin.brief_id",
            )

    @staticmethod
    def _timestamp(value: str) -> datetime:
        return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")

    @staticmethod
    def _aware_timestamp(value: datetime, reference: str) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ProjectContractFailure(
                "project.contract.invalid_shell",
                reference,
            )
        return value

    @staticmethod
    def _format_timestamp(value: datetime) -> str:
        normalized = value.astimezone(timezone.utc)
        if normalized.microsecond:
            rendered = normalized.strftime("%Y-%m-%dT%H:%M:%S.%f").rstrip("0")
        else:
            rendered = normalized.strftime("%Y-%m-%dT%H:%M:%S")
        return f"{rendered}Z"

    @staticmethod
    def _reject(code: str, reference: str) -> None:
        raise ProjectContractFailure(code, reference)
