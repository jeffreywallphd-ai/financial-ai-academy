"""Dependency-light conformance runner for Project workspace v1."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping
import unicodedata
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker


VERSION = "1.0.0"
FORBIDDEN_KEYS = {
    "answer",
    "completion",
    "credential",
    "execution",
    "host_path",
    "mastery",
    "portfolio",
    "provider_payload",
    "score",
    "storage_key",
    "kernel",
    "network",
    "secret",
    "subprocess",
}


class ProjectConformanceFailure(ValueError):
    def __init__(self, code: str, reference: str) -> None:
        super().__init__("Project contract input was rejected.")
        self.code = code
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def schema_dir() -> Path:
    return repository_root() / "contracts/learning/project/v1"


def corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/project-workspace/v1"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_brief_bytes(brief: Mapping[str, Any]) -> bytes:
    return json.dumps(
        brief,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def brief_digest(document: Mapping[str, Any]) -> str:
    brief = document.get("brief")
    if not isinstance(brief, Mapping):
        raise ProjectConformanceFailure(
            "project.contract.schema_invalid",
            "brief",
        )
    return hashlib.sha256(canonical_brief_bytes(brief)).hexdigest()


def canonical_digest(document: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_brief_bytes(document)).hexdigest()


class ProjectContractValidator:
    def __init__(self, schemas: Path | None = None) -> None:
        root = schemas or schema_dir()
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
            schema = load_json(root / f"{name}.schema.json")
            Draft202012Validator.check_schema(schema)
            self._validators[name] = Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            )

    def validate_brief(self, document: Mapping[str, Any]) -> None:
        self._version(document)
        self._shape("brief", document)
        if brief_digest(document) != document["brief_digest"]:
            self._reject(
                "project.contract.brief_digest_mismatch",
                "brief_digest",
            )
        brief = document["brief"]
        self._unique(
            [item["milestone_id"] for item in brief["milestones"]],
            "brief.milestones",
        )
        self._unique(
            [item["resource_id"] for item in brief["source_references"]],
            "brief.source_references",
        )
        self._confidential(document)

    def validate_intent(
        self,
        document: Mapping[str, Any],
        approved_brief: Mapping[str, Any] | None = None,
    ) -> None:
        self._version(document)
        self._shape("create-intent", document)
        origin = document["origin"]
        if origin["origin_type"] == "learning":
            if approved_brief is None:
                self._reject(
                    "project.contract.learning_brief_required",
                    "origin.brief_id",
                )
            self.validate_brief(approved_brief)
            brief = approved_brief["brief"]
            expected = (
                approved_brief["schema_version"],
                brief["brief_id"],
                brief["brief_version"],
                approved_brief["brief_digest"],
                brief["title"],
                brief["purpose"],
            )
            actual = (
                origin["project_brief_schema_version"],
                origin["brief_id"],
                origin["brief_version"],
                origin["brief_digest"],
                origin["brief_title"],
                origin["brief_purpose"],
            )
            if actual != expected:
                self._reject(
                    "project.contract.stale_learning_reference",
                    "origin.brief_id",
                )
        self._confidential(document)

    def validate_shell(self, document: Mapping[str, Any]) -> None:
        self._version(document)
        self._shape("shell", document)
        created = self._timestamp(document["created_at"])
        updated = self._timestamp(document["updated_at"])
        if updated < created:
            self._reject("project.contract.invalid_shell", "updated_at")
        self._confidential(document)

    def validate_workspace(self, document: Mapping[str, Any]) -> None:
        self._version(document)
        self._shape("workspace", document)
        if self._timestamp(document["updated_at"]) < self._timestamp(
            document["created_at"]
        ):
            self._reject("project.contract.invalid_workspace", "updated_at")
        self._unique_workspace(document)
        for note in document["notes"]:
            if self._timestamp(note["updated_at"]) < self._timestamp(
                note["created_at"]
            ):
                self._reject("project.contract.invalid_workspace", "notes")
        for reference in document["references"]:
            self._validate_url(reference["url"], "references.url")
            if self._timestamp(reference["updated_at"]) < self._timestamp(
                reference["created_at"]
            ):
                self._reject("project.contract.invalid_workspace", "references")
        for artifact in document["artifacts"]:
            self._artifact_semantics(artifact)
        self._confidential(document)

    def validate_workspace_mutation_intent(
        self,
        document: Mapping[str, Any],
    ) -> None:
        self._version(document)
        self._shape("workspace-mutation-intent", document)
        mutation = document["mutation"]
        if mutation["operation"] in {"add_reference", "replace_reference"}:
            self._validate_url(mutation["url"], "mutation.url")
        if mutation["operation"] == "add_artifact":
            self._artifact_semantics(mutation["artifact"])
        self._confidential(document)

    def validate_snapshot_close_intent(
        self,
        document: Mapping[str, Any],
    ) -> None:
        self._version(document)
        self._shape("snapshot-close-intent", document)
        self._confidential(document)

    def validate_snapshot(self, document: Mapping[str, Any]) -> None:
        self._version(document)
        self._shape("snapshot", document)
        snapshot = document["snapshot"]
        if canonical_digest(snapshot) != document["snapshot_digest"]:
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
            self._reject("project.contract.invalid_snapshot", "closed_at")
        for key, identity in (
            ("notes", "record_id"),
            ("references", "record_id"),
            ("artifacts", "artifact_id"),
            ("domain_links", "link_id"),
        ):
            self._unique(
                [item[identity] for item in snapshot[key]],
                f"snapshot.{key}",
                "project.contract.duplicate_snapshot_reference",
            )
        self._confidential(document)

    def validate_evidence_export(self, document: Mapping[str, Any]) -> None:
        self._version(document)
        self._shape("evidence-export", document)
        exported = document["export"]
        self.validate_snapshot(exported["snapshot_record"])
        self.validate_workspace(exported["workspace_record"])
        if canonical_digest(exported) != document["export_digest"]:
            self._reject(
                "project.contract.export_digest_mismatch",
                "export_digest",
            )
        included = [
            (item["artifact_id"], item["artifact_version"])
            for item in exported["artifact_files"]
        ]
        excluded = [
            (item["artifact_id"], item["artifact_version"])
            for item in exported["excluded_artifacts"]
        ]
        if len(included) != len(set(included)) or len(excluded) != len(
            set(excluded)
        ):
            self._reject(
                "project.contract.duplicate_export_artifact",
                "export",
            )
        if set(included) & set(excluded):
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
            self._reject("project.contract.export_snapshot_mismatch", "export")
        self._validate_export_record_bindings(snapshot, workspace)
        artifact_records = {
            (item["artifact_id"], item["artifact_version"]): item
            for item in workspace["artifacts"]
        }
        expected = {
            (item["artifact_id"], item["artifact_version"])
            for item in snapshot["artifacts"]
        }
        if set(included) | set(excluded) != expected:
            self._reject("project.contract.incomplete_export_coverage", "export")
        for item in exported["artifact_files"]:
            identity = (item["artifact_id"], item["artifact_version"])
            artifact = artifact_records.get(identity)
            if artifact is None or (
                item["manifest_digest"] != canonical_digest(artifact)
                or item["logical_path"] != artifact["logical_path"]
                or item["media_type"] != artifact["media_type"]
                or item["byte_count"] != artifact["byte_count"]
                or item["content_digest"] != artifact["content_digest"]
            ):
                self._reject("project.contract.export_artifact_mismatch", "export")
        self._confidential(document)

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
                if (
                    reference_identity != record_identity
                    or reference[digest_key] != canonical_digest(record)
                ):
                    self._reject(
                        "project.contract.export_record_mismatch",
                        f"export.{key}",
                    )

    def validate_approved(self, corpus: Path | None = None) -> None:
        approved = (corpus or corpus_dir()) / "approved"
        brief = load_json(approved / "brief.json")
        self.validate_brief(brief)
        self.validate_intent(load_json(approved / "independent-intent.json"))
        self.validate_intent(
            load_json(approved / "learning-intent.json"),
            brief,
        )
        self.validate_shell(load_json(approved / "independent-shell.json"))
        self.validate_shell(load_json(approved / "learning-shell.json"))
        self.validate_workspace(load_json(approved / "workspace.json"))
        self.validate_workspace_mutation_intent(
            load_json(approved / "workspace-mutation-intent.json")
        )
        self.validate_snapshot_close_intent(
            load_json(approved / "snapshot-close-intent.json")
        )
        self.validate_snapshot(load_json(approved / "snapshot.json"))
        self.validate_evidence_export(
            load_json(approved / "evidence-export.json")
        )

    def _unique_workspace(self, document: Mapping[str, Any]) -> None:
        for key, identity in (
            ("notes", "note_id"),
            ("references", "reference_id"),
            ("artifacts", "artifact_id"),
            ("domain_links", "link_id"),
        ):
            self._unique(
                [item[identity] for item in document[key]],
                key,
                "project.contract.duplicate_workspace_record",
            )
        self._unique(
            [item["logical_path"] for item in document["artifacts"]],
            "artifacts.logical_path",
            "project.contract.duplicate_workspace_record",
        )
        self._unique(
            [
                self._logical_path_key(item["logical_path"])
                for item in document["artifacts"]
            ],
            "artifacts.logical_path",
            "project.contract.duplicate_workspace_record",
        )

    def _artifact_semantics(self, artifact: Mapping[str, Any]) -> None:
        self._validate_logical_path(artifact["logical_path"])
        classification = artifact.get("result_classification")
        if artifact["artifact_kind"] == "result" and classification is None:
            self._reject(
                "project.contract.result_classification_required",
                "result_classification",
            )
        if artifact["artifact_kind"] != "result" and classification not in (
            None,
            "narrative",
        ):
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

    def _shape(self, kind: str, document: Mapping[str, Any]) -> None:
        error = next(iter(self._validators[kind].iter_errors(document)), None)
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            self._reject(
                "project.contract.schema_invalid",
                reference or kind,
            )

    def _version(self, document: Mapping[str, Any]) -> None:
        if document.get("schema_version") != VERSION:
            self._reject(
                "project.contract.unsupported_version",
                "schema_version",
            )

    def _unique(
        self,
        values: list[str],
        reference: str,
        code: str = "project.contract.invalid_brief",
    ) -> None:
        if len(values) != len(set(values)):
            self._reject(code, reference)

    def _confidential(self, value: object, reference: str = "record") -> None:
        if isinstance(value, Mapping):
            for key, nested in value.items():
                if key in FORBIDDEN_KEYS:
                    self._reject(
                        "project.contract.private_field",
                        f"{reference}.{key}",
                    )
                self._confidential(nested, f"{reference}.{key}")
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                self._confidential(nested, f"{reference}.{index}")

    @staticmethod
    def _timestamp(value: str) -> datetime:
        return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")

    @staticmethod
    def _reject(code: str, reference: str) -> None:
        raise ProjectConformanceFailure(code, reference)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schemas", type=Path, default=schema_dir())
    parser.add_argument("--corpus", type=Path, default=corpus_dir())
    arguments = parser.parse_args()
    ProjectContractValidator(arguments.schemas).validate_approved(arguments.corpus)
    print("PASS project workspace v1 compatibility")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
