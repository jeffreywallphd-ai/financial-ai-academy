"""Adapters from public Project, Content, and Curriculum operations."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from financial_ai_academy.modules.content.public import (
    ContentOperations,
    GetPublishedProjectBriefRequest,
)
from financial_ai_academy.modules.curriculum.public import (
    CurriculumOperations,
    ResolveProjectBriefPlacementRequest,
)
from financial_ai_academy.modules.project.public import (
    OpenProjectLearningSnapshotRequest,
    ProjectOperations,
)

from ..ports.project_submission import (
    ProjectSubmissionContract,
    ProjectSubmissionContractFailure,
)
from ..ports.project_submission_gateways import (
    ProjectSubmissionSourceFailure,
)


class PublicProjectSubmissionSource:
    """Assemble one closed candidate without reading another module's storage."""

    def __init__(
        self,
        project: ProjectOperations,
        content: ContentOperations,
        curriculum: CurriculumOperations,
        contract: ProjectSubmissionContract,
        project_schema_dir: Path,
    ) -> None:
        self._project = project
        self._content = content
        self._curriculum = curriculum
        self._contract = contract
        schema = json.loads(
            (project_schema_dir / "brief.schema.json").read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)
        self._brief_validator = Draft202012Validator(
            schema, format_checker=FormatChecker()
        )

    def resolve(
        self, *, learner_id: str, project_id: str, snapshot_id: str
    ):
        try:
            source = self._project.open_learning_snapshot(
                OpenProjectLearningSnapshotRequest(
                    learner_id=learner_id,
                    project_id=project_id,
                    snapshot_id=snapshot_id,
                )
            )
            origin = source.origin
            placement = self._curriculum.resolve_project_brief_placement(
                ResolveProjectBriefPlacementRequest(origin.placement_id)
            )
            published = self._content.get_published_project_brief(
                GetPublishedProjectBriefRequest(
                    package_id=origin.package_id,
                    package_version=origin.package_version,
                    package_digest=origin.package_digest,
                    brief_id=origin.brief_id,
                )
            )
            brief_document = self._document(published.value)
            errors = sorted(
                self._brief_validator.iter_errors(brief_document),
                key=lambda item: tuple(str(part) for part in item.absolute_path),
            )
            if errors:
                self._fail("assessment.project.invalid_source", "brief")
            brief = brief_document["brief"]
            self._exact_source(origin, placement, published, brief_document, brief)
            snapshot = source.snapshot
            candidate = {
                "schema_version": "1.0.0",
                "project": {
                    "project_id": snapshot.snapshot.project_id,
                    "project_revision": snapshot.snapshot.project_revision,
                    "project_shell_digest": snapshot.snapshot.project_shell_digest,
                    "snapshot_id": snapshot.snapshot_id,
                    "snapshot_digest": snapshot.snapshot_digest,
                    "workspace_revision": snapshot.snapshot.workspace_revision,
                    "closed_at": self._timestamp(snapshot.closed_at),
                },
                "origin": {
                    "package_id": origin.package_id,
                    "package_version": origin.package_version,
                    "package_digest": origin.package_digest,
                    "brief_id": origin.brief_id,
                    "brief_version": origin.brief_version,
                    "brief_digest": origin.brief_digest,
                    "curriculum_id": origin.curriculum_id,
                    "curriculum_version": origin.curriculum_version,
                    "curriculum_digest": origin.curriculum_digest,
                    "placement_id": origin.placement_id,
                    "placement_version": origin.placement_version,
                    "placement_digest": origin.placement_digest,
                },
                "policy_id": "assessment-project-closure",
                "policy_version": "1.0.0",
                "milestones": [
                    {
                        "milestone_id": item["milestone_id"],
                        "milestone_version": origin.brief_version,
                        "sequence": sequence,
                        "title": self._milestone_title(item["description"]),
                    }
                    for sequence, item in enumerate(brief["milestones"], start=1)
                ],
                "resources": [self._resource(item) for item in source.resources],
            }
            return self._contract.parse_candidate(
                json.dumps(
                    candidate,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode("utf-8")
            )
        except ProjectSubmissionSourceFailure:
            raise
        except ProjectSubmissionContractFailure as error:
            raise ProjectSubmissionSourceFailure(
                "assessment.project.invalid_source", error.reference
            ) from error
        except Exception as error:
            code = getattr(getattr(error, "code", None), "value", None)
            if code in {"not_found", "invalid_request"}:
                mapped = "assessment.project.not_found"
            elif code in {"immutable_conflict", "stale_revision"}:
                mapped = "assessment.project.stale_source"
            elif code in {"integrity_failure", "invalid_package"}:
                mapped = "assessment.project.invalid_source"
            else:
                mapped = "assessment.project.source_unavailable"
            raise ProjectSubmissionSourceFailure(mapped, "project_snapshot") from error

    @classmethod
    def _exact_source(
        cls,
        origin,
        placement,
        published,
        document: Mapping[str, Any],
        brief: Mapping[str, Any],
    ) -> None:
        values = (
            placement.package_id == origin.package_id,
            placement.package_version == origin.package_version,
            placement.package_digest == origin.package_digest,
            placement.brief_id == origin.brief_id,
            placement.brief_version == origin.brief_version,
            placement.brief_digest == origin.brief_digest,
            placement.project_brief_schema_version
            == origin.project_brief_schema_version,
            placement.curriculum_id == origin.curriculum_id,
            placement.curriculum_version == origin.curriculum_version,
            placement.curriculum_digest == origin.curriculum_digest,
            placement.placement_id == origin.placement_id,
            placement.placement_version == origin.placement_version,
            placement.placement_digest == origin.placement_digest,
            published.package_id == origin.package_id,
            published.package_version == origin.package_version,
            published.package_digest == origin.package_digest,
            published.brief_id == origin.brief_id,
            published.brief_version == origin.brief_version,
            published.brief_digest == origin.brief_digest,
            published.schema_version == origin.project_brief_schema_version,
            document.get("schema_version") == origin.project_brief_schema_version,
            document.get("brief_digest") == origin.brief_digest,
            brief.get("brief_id") == origin.brief_id,
            brief.get("brief_version") == origin.brief_version,
            brief.get("title") == origin.brief_title,
            brief.get("purpose") == origin.brief_purpose,
        )
        if not all(values):
            cls._fail("assessment.project.stale_source", "learning_origin")

    @staticmethod
    def _resource(value) -> dict[str, Any]:
        result: dict[str, Any] = {
            "resource_kind": value.resource_kind,
            "resource_id": value.resource_id,
            "record_digest": value.record_digest,
        }
        if value.resource_version is not None:
            result["resource_version"] = value.resource_version
        if value.resource_as_of is not None:
            result["resource_as_of"] = PublicProjectSubmissionSource._timestamp(
                value.resource_as_of
            )
        if value.content_digest is not None:
            result["content_digest"] = value.content_digest
        if value.byte_count is not None:
            result["byte_count"] = value.byte_count
        if value.owner_reference_digest is not None:
            result["owner_reference_digest"] = value.owner_reference_digest
        return result

    @staticmethod
    def _document(value: bytes) -> dict[str, Any]:
        try:
            document = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ProjectSubmissionSourceFailure(
                "assessment.project.invalid_source", "brief"
            ) from error
        if not isinstance(document, dict):
            PublicProjectSubmissionSource._fail(
                "assessment.project.invalid_source", "brief"
            )
        return document

    @staticmethod
    def _timestamp(value: datetime) -> str:
        if value.tzinfo is None or value.utcoffset() is None:
            PublicProjectSubmissionSource._fail(
                "assessment.project.invalid_source", "timestamp"
            )
        rendered = (
            value.astimezone(timezone.utc)
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z")
        )
        return rendered.replace(".000000Z", "Z")

    @staticmethod
    def _milestone_title(description: str) -> str:
        """Project short display text into the assessment contract's title field."""

        if len(description) <= 160:
            return description
        return f"{description[:157]}..."

    @staticmethod
    def _fail(code: str, reference: str) -> None:
        raise ProjectSubmissionSourceFailure(code, reference)
