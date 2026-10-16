"""Closed parser and projector for Project workspace v1."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

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
from ..ports.project_contract import ProjectContractFailure


VERSION = "1.0.0"


class ContractProjectAdapter:
    """Validate bytes and return immutable Project-owned values."""

    def __init__(self, schema_dir: Path) -> None:
        self._validators: dict[str, Draft202012Validator] = {}
        for name in ("brief", "create-intent", "shell"):
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

    def _unique(self, values: list[str], reference: str) -> None:
        if len(values) != len(set(values)):
            self._reject("project.contract.invalid_brief", reference)

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
