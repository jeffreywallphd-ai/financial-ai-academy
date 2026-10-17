"""Closed Project-submission parser, policy, and safe projectors."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker

from ..domain.project_submission import (
    AcceptedProjectSubmission,
    LearningOrigin,
    MilestoneEvidence,
    ProjectCompletionEvent,
    ProjectCompletionEvidence,
    ProjectEvidenceMetadata,
    ProjectHistory,
    ProjectMilestone,
    ProjectSnapshotCandidate,
    ProjectSource,
    ProjectSubmission,
    ProjectValidationIssue,
    ProjectValidationResult,
    SnapshotResource,
)
from ..ports.project_submission import ProjectSubmissionContractFailure


VERSION = "1.0.0"
POLICY_ID = "assessment-project-closure"
EVENT_TYPE = "assessment.project.completed"


class ContractProjectSubmissionAdapter:
    """Implements Project evidence meaning without runtime dependencies."""

    def __init__(self, schema_dir: Path) -> None:
        self._validators: dict[str, Draft202012Validator] = {}
        for name in (
            "snapshot-candidate",
            "submission",
            "validation-result",
            "evidence",
            "completion-event",
            "history",
        ):
            schema = json.loads(
                (schema_dir / f"{name}.schema.json").read_text(encoding="utf-8")
            )
            Draft202012Validator.check_schema(schema)
            self._validators[name] = Draft202012Validator(
                schema, format_checker=FormatChecker()
            )

    def parse_candidate(self, value: bytes) -> ProjectSnapshotCandidate:
        document = self._document(value, "snapshot_candidate")
        self._shape("snapshot-candidate", document)
        self._version(document)
        project = document["project"]
        origin = document["origin"]
        candidate = ProjectSnapshotCandidate(
            schema_version=document["schema_version"],
            project=ProjectSource(
                project_id=project["project_id"],
                project_revision=project["project_revision"],
                project_shell_digest=project["project_shell_digest"],
                snapshot_id=project["snapshot_id"],
                snapshot_digest=project["snapshot_digest"],
                workspace_revision=project["workspace_revision"],
                closed_at=self._timestamp(
                    project["closed_at"], "project.closed_at"
                ),
            ),
            origin=LearningOrigin(**origin),
            policy_id=document["policy_id"],
            policy_version=document["policy_version"],
            milestones=tuple(
                ProjectMilestone(**milestone) for milestone in document["milestones"]
            ),
            resources=tuple(
                self._resource(resource) for resource in document["resources"]
            ),
        )
        self._validate_candidate_semantics(candidate)
        return candidate

    def parse_submission(self, value: bytes) -> ProjectSubmission:
        document = self._document(value, "submission")
        self._shape("submission", document)
        self._version(document)
        source = document["source"]
        return ProjectSubmission(
            schema_version=document["schema_version"],
            submission_id=document["submission_id"],
            project_id=source["project_id"],
            snapshot_id=source["snapshot_id"],
            snapshot_digest=source["snapshot_digest"],
            brief_id=source["brief_id"],
            brief_version=source["brief_version"],
            brief_digest=source["brief_digest"],
            placement_id=source["placement_id"],
            placement_version=source["placement_version"],
            placement_digest=source["placement_digest"],
            policy_id=document["policy_id"],
            policy_version=document["policy_version"],
            milestone_evidence=tuple(
                MilestoneEvidence(
                    milestone_id=mapping["milestone_id"],
                    resources=tuple(
                        self._resource(resource)
                        for resource in mapping["resources"]
                    ),
                )
                for mapping in document["milestone_evidence"]
            ),
        )

    def validate(
        self,
        candidate: ProjectSnapshotCandidate,
        submission: ProjectSubmission,
    ) -> ProjectValidationResult:
        issues: list[ProjectValidationIssue] = []
        self._source_issues(candidate, submission, issues)

        expected = {item.milestone_id: item for item in candidate.milestones}
        seen: set[str] = set()
        candidate_resources = {item.identity: item for item in candidate.resources}
        candidate_resource_ids = {
            (item.resource_kind, item.resource_id) for item in candidate.resources
        }

        for mapping in submission.milestone_evidence:
            if mapping.milestone_id in seen:
                self._issue(
                    issues,
                    "assessment.project.duplicate_milestone",
                    mapping.milestone_id,
                    "Map each milestone once.",
                )
                continue
            seen.add(mapping.milestone_id)
            if mapping.milestone_id not in expected:
                self._issue(
                    issues,
                    "assessment.project.unknown_milestone",
                    mapping.milestone_id,
                    "Choose a milestone from this project brief.",
                )
            resource_seen: set[tuple[object, ...]] = set()
            for resource in mapping.resources:
                identity = resource.identity
                if identity in resource_seen:
                    self._issue(
                        issues,
                        "assessment.project.duplicate_resource",
                        mapping.milestone_id,
                        "Use each snapshot item once per milestone.",
                    )
                    continue
                resource_seen.add(identity)
                if identity in candidate_resources:
                    continue
                safe_ref = f"{mapping.milestone_id}:{resource.resource_kind}:{resource.resource_id}"
                if (resource.resource_kind, resource.resource_id) in candidate_resource_ids:
                    self._issue(
                        issues,
                        "assessment.project.stale_resource",
                        safe_ref,
                        "Choose the version included in this snapshot.",
                    )
                else:
                    self._issue(
                        issues,
                        "assessment.project.unknown_resource",
                        safe_ref,
                        "Choose an item included in this snapshot.",
                    )

        for milestone in candidate.milestones:
            if milestone.milestone_id not in seen:
                self._issue(
                    issues,
                    "assessment.project.missing_milestone",
                    milestone.milestone_id,
                    "Add snapshot evidence for this milestone.",
                )

        if issues:
            result = ProjectValidationResult(
                status="refused",
                request_fingerprint=None,
                issues=tuple(issues),
                accepted=None,
            )
        else:
            fingerprint = self.submission_fingerprint(candidate, submission)
            accepted = AcceptedProjectSubmission(candidate, submission, fingerprint)
            result = ProjectValidationResult(
                status="accepted",
                request_fingerprint=fingerprint,
                issues=(),
                accepted=accepted,
            )
        self._shape("validation-result", self.project_validation(result))
        return result

    def project_validation(
        self, result: ProjectValidationResult
    ) -> dict[str, Any]:
        document: dict[str, Any] = {
            "schema_version": VERSION,
            "status": result.status,
            "issues": [asdict(issue) for issue in result.issues],
        }
        if result.request_fingerprint is not None:
            document["request_fingerprint"] = result.request_fingerprint
        return document

    def project_evidence(
        self,
        accepted: AcceptedProjectSubmission,
        metadata: ProjectEvidenceMetadata,
    ) -> ProjectCompletionEvidence:
        validation = self.validate(accepted.candidate, accepted.submission)
        if (
            validation.accepted is None
            or validation.request_fingerprint != accepted.request_fingerprint
        ):
            self._reject(
                "assessment.project.inconsistent_evidence",
                "request_fingerprint",
            )
        self._metadata(metadata)
        evidence = ProjectCompletionEvidence(
            schema_version=VERSION,
            evidence_id=metadata.evidence_id,
            learner_id=metadata.learner_id,
            occurrence=metadata.occurrence,
            accepted_sequence=metadata.accepted_sequence,
            submitted_at=metadata.submitted_at,
            supersedes_submission_id=metadata.supersedes_submission_id,
            accepted=accepted,
        )
        self._shape("evidence", self.to_evidence_document(evidence))
        return evidence

    def project_event(
        self,
        evidence: ProjectCompletionEvidence,
        *,
        event_id: str,
        occurred_at: datetime,
    ) -> ProjectCompletionEvent:
        occurred_at = self._aware_timestamp(occurred_at, "occurred_at")
        if occurred_at < evidence.submitted_at:
            self._reject("assessment.project.invalid_server_metadata", "occurred_at")
        event = ProjectCompletionEvent(
            schema_version=VERSION,
            event_id=event_id,
            event_type=EVENT_TYPE,
            event_version=VERSION,
            occurred_at=occurred_at,
            evidence=evidence,
        )
        self._shape("completion-event", self.to_event_document(event))
        return event

    def project_history(
        self, evidence: Sequence[ProjectCompletionEvidence]
    ) -> ProjectHistory:
        if not evidence:
            self._reject("assessment.project.invalid_history", "items")
        items = tuple(sorted(evidence, key=lambda item: item.occurrence))
        for item in items:
            validation = self.validate(
                item.accepted.candidate, item.accepted.submission
            )
            if (
                validation.accepted is None
                or validation.request_fingerprint
                != item.accepted.request_fingerprint
            ):
                self._reject(
                    "assessment.project.inconsistent_evidence",
                    "request_fingerprint",
                )
            self._metadata(
                ProjectEvidenceMetadata(
                    evidence_id=item.evidence_id,
                    learner_id=item.learner_id,
                    occurrence=item.occurrence,
                    accepted_sequence=item.accepted_sequence,
                    submitted_at=item.submitted_at,
                    supersedes_submission_id=item.supersedes_submission_id,
                )
            )
            self._shape("evidence", self.to_evidence_document(item))
        project_ids = {item.accepted.candidate.project.project_id for item in items}
        if len(project_ids) != 1:
            self._reject("assessment.project.invalid_history", "project_id")
        learner_ids = {item.learner_id for item in items}
        if len(learner_ids) != 1:
            self._reject("assessment.project.invalid_history", "learner_id")
        evidence_ids = [item.evidence_id for item in items]
        submission_ids = [item.accepted.submission.submission_id for item in items]
        if len(evidence_ids) != len(set(evidence_ids)):
            self._reject("assessment.project.invalid_history", "evidence_id")
        if len(submission_ids) != len(set(submission_ids)):
            self._reject("assessment.project.invalid_history", "submission_id")
        ids: set[str] = set()
        prior_sequence = 0
        prior_time: datetime | None = None
        for expected_occurrence, item in enumerate(items, start=1):
            if item.occurrence != expected_occurrence:
                self._reject("assessment.project.invalid_history", "occurrence")
            if item.accepted_sequence <= prior_sequence:
                self._reject(
                    "assessment.project.invalid_history", "accepted_sequence"
                )
            if prior_time is not None and item.submitted_at < prior_time:
                self._reject("assessment.project.invalid_history", "submitted_at")
            prior = item.supersedes_submission_id
            if expected_occurrence == 1 and prior is not None:
                self._reject(
                    "assessment.project.invalid_history", "supersedes_submission_id"
                )
            if expected_occurrence > 1 and prior not in ids:
                self._reject(
                    "assessment.project.invalid_history", "supersedes_submission_id"
                )
            ids.add(item.accepted.submission.submission_id)
            prior_sequence = item.accepted_sequence
            prior_time = item.submitted_at
        history = ProjectHistory(VERSION, next(iter(project_ids)), items)
        self._shape("history", self.to_history_document(history))
        return history

    def submission_fingerprint(
        self,
        candidate: ProjectSnapshotCandidate,
        submission: ProjectSubmission,
    ) -> str:
        milestone_order = {
            item.milestone_id: item.sequence for item in candidate.milestones
        }
        normalized = self.to_submission_document(submission)
        normalized["milestone_evidence"] = sorted(
            normalized["milestone_evidence"],
            key=lambda item: (milestone_order.get(item["milestone_id"], 10_000), item["milestone_id"]),
        )
        for mapping in normalized["milestone_evidence"]:
            mapping["resources"] = sorted(
                mapping["resources"], key=self._canonical_resource_key
            )
        return hashlib.sha256(self._canonical_bytes(normalized)).hexdigest()

    def to_candidate_document(
        self, candidate: ProjectSnapshotCandidate
    ) -> dict[str, Any]:
        return self._portable(candidate)

    def to_submission_document(self, submission: ProjectSubmission) -> dict[str, Any]:
        return {
            "schema_version": VERSION,
            "submission_id": submission.submission_id,
            "source": {
                key: getattr(submission, key)
                for key in (
                    "project_id",
                    "snapshot_id",
                    "snapshot_digest",
                    "brief_id",
                    "brief_version",
                    "brief_digest",
                    "placement_id",
                    "placement_version",
                    "placement_digest",
                )
            },
            "policy_id": submission.policy_id,
            "policy_version": submission.policy_version,
            "milestone_evidence": [
                {
                    "milestone_id": item.milestone_id,
                    "resources": [self._resource_document(resource) for resource in item.resources],
                }
                for item in submission.milestone_evidence
            ],
        }

    def to_evidence_document(
        self, evidence: ProjectCompletionEvidence
    ) -> dict[str, Any]:
        accepted = evidence.accepted
        candidate = accepted.candidate
        submission = accepted.submission
        document: dict[str, Any] = {
            "schema_version": VERSION,
            "evidence_id": evidence.evidence_id,
            "learner_id": evidence.learner_id,
            "submission_id": submission.submission_id,
            "project_id": submission.project_id,
            "snapshot_id": submission.snapshot_id,
            "snapshot_digest": submission.snapshot_digest,
            "brief_id": submission.brief_id,
            "brief_version": submission.brief_version,
            "brief_digest": submission.brief_digest,
            "placement_id": submission.placement_id,
            "placement_version": submission.placement_version,
            "placement_digest": submission.placement_digest,
            "policy_id": submission.policy_id,
            "policy_version": submission.policy_version,
            "milestone_evidence": self.to_submission_document(submission)[
                "milestone_evidence"
            ],
            "milestone_ids": [item.milestone_id for item in candidate.milestones],
            "request_fingerprint": accepted.request_fingerprint,
            "occurrence": evidence.occurrence,
            "accepted_sequence": evidence.accepted_sequence,
            "submitted_at": self._format_timestamp(evidence.submitted_at),
        }
        if evidence.supersedes_submission_id is not None:
            document["supersedes_submission_id"] = evidence.supersedes_submission_id
        return document

    def to_event_document(self, event: ProjectCompletionEvent) -> dict[str, Any]:
        evidence = self.to_evidence_document(event.evidence)
        payload_keys = (
            "evidence_id",
            "submission_id",
            "project_id",
            "snapshot_id",
            "snapshot_digest",
            "brief_id",
            "brief_version",
            "brief_digest",
            "placement_id",
            "placement_version",
            "placement_digest",
            "policy_id",
            "policy_version",
            "milestone_ids",
            "request_fingerprint",
            "occurrence",
            "submitted_at",
        )
        payload = {key: evidence[key] for key in payload_keys}
        if "supersedes_submission_id" in evidence:
            payload["supersedes_submission_id"] = evidence[
                "supersedes_submission_id"
            ]
        return {
            "schema_version": VERSION,
            "event_id": event.event_id,
            "event_type": EVENT_TYPE,
            "event_version": VERSION,
            "occurred_at": self._format_timestamp(event.occurred_at),
            "payload": payload,
        }

    def to_history_document(self, history: ProjectHistory) -> dict[str, Any]:
        items = []
        for evidence in history.items:
            projected = self.to_evidence_document(evidence)
            item = {
                key: projected[key]
                for key in (
                    "evidence_id",
                    "submission_id",
                    "snapshot_id",
                    "snapshot_digest",
                    "request_fingerprint",
                    "occurrence",
                    "submitted_at",
                )
            }
            if "supersedes_submission_id" in projected:
                item["supersedes_submission_id"] = projected[
                    "supersedes_submission_id"
                ]
            items.append(item)
        return {
            "schema_version": VERSION,
            "project_id": history.project_id,
            "items": items,
        }

    def _validate_candidate_semantics(
        self, candidate: ProjectSnapshotCandidate
    ) -> None:
        if candidate.policy_id != POLICY_ID or candidate.policy_version != VERSION:
            self._reject("assessment.project.unsupported_policy", "policy_id")
        milestone_ids = [item.milestone_id for item in candidate.milestones]
        if len(milestone_ids) != len(set(milestone_ids)):
            self._reject("assessment.project.invalid_candidate", "milestones")
        sequences = [item.sequence for item in candidate.milestones]
        if sequences != list(range(1, len(sequences) + 1)):
            self._reject("assessment.project.invalid_candidate", "milestones.sequence")
        resource_ids = [item.identity for item in candidate.resources]
        if len(resource_ids) != len(set(resource_ids)):
            self._reject("assessment.project.invalid_candidate", "resources")

    def _source_issues(
        self,
        candidate: ProjectSnapshotCandidate,
        submission: ProjectSubmission,
        issues: list[ProjectValidationIssue],
    ) -> None:
        expected = (
            candidate.project.project_id,
            candidate.project.snapshot_id,
            candidate.project.snapshot_digest,
            candidate.origin.brief_id,
            candidate.origin.brief_version,
            candidate.origin.brief_digest,
            candidate.origin.placement_id,
            candidate.origin.placement_version,
            candidate.origin.placement_digest,
            candidate.policy_id,
            candidate.policy_version,
        )
        actual = (
            submission.project_id,
            submission.snapshot_id,
            submission.snapshot_digest,
            submission.brief_id,
            submission.brief_version,
            submission.brief_digest,
            submission.placement_id,
            submission.placement_version,
            submission.placement_digest,
            submission.policy_id,
            submission.policy_version,
        )
        if actual != expected:
            self._issue(
                issues,
                "assessment.project.source_mismatch",
                "source",
                "Refresh the project snapshot before submitting.",
            )

    @staticmethod
    def _issue(
        issues: list[ProjectValidationIssue],
        code: str,
        reference: str,
        message: str,
    ) -> None:
        issues.append(ProjectValidationIssue(code, reference[:120], message))

    def _metadata(self, metadata: ProjectEvidenceMetadata) -> None:
        self._aware_timestamp(metadata.submitted_at, "submitted_at")
        if metadata.occurrence < 1 or metadata.accepted_sequence < 1:
            self._reject("assessment.project.invalid_server_metadata", "sequence")
        if metadata.occurrence == 1 and metadata.supersedes_submission_id is not None:
            self._reject(
                "assessment.project.invalid_server_metadata",
                "supersedes_submission_id",
            )
        if metadata.occurrence > 1 and metadata.supersedes_submission_id is None:
            self._reject(
                "assessment.project.invalid_server_metadata",
                "supersedes_submission_id",
            )

    @staticmethod
    def _resource(value: Mapping[str, Any]) -> SnapshotResource:
        return SnapshotResource(
            resource_kind=value["resource_kind"],
            resource_id=value["resource_id"],
            resource_version=value.get("resource_version"),
            resource_as_of=(
                ContractProjectSubmissionAdapter._timestamp(
                    value["resource_as_of"], "resource_as_of"
                )
                if value.get("resource_as_of") is not None
                else None
            ),
            record_digest=value["record_digest"],
            content_digest=value.get("content_digest"),
            byte_count=value.get("byte_count"),
            owner_reference_digest=value.get("owner_reference_digest"),
        )

    @classmethod
    def _resource_document(cls, resource: SnapshotResource) -> dict[str, Any]:
        document: dict[str, Any] = {
            "resource_kind": resource.resource_kind,
            "resource_id": resource.resource_id,
            "record_digest": resource.record_digest,
        }
        for key in (
            "resource_version",
            "content_digest",
            "byte_count",
            "owner_reference_digest",
        ):
            value = getattr(resource, key)
            if value is not None:
                document[key] = value
        if resource.resource_as_of is not None:
            document["resource_as_of"] = cls._format_timestamp(
                resource.resource_as_of
            )
        return document

    @staticmethod
    def _canonical_resource_key(value: Mapping[str, Any]) -> bytes:
        return ContractProjectSubmissionAdapter._canonical_bytes(value)

    @classmethod
    def _portable(cls, value: object) -> dict[str, Any]:
        projected = cls._portable_value(asdict(value))
        if not isinstance(projected, dict):
            raise TypeError("Project submission projection requires an object.")
        return projected

    @classmethod
    def _portable_value(cls, value: object) -> object:
        if isinstance(value, datetime):
            return cls._format_timestamp(value)
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
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")

    @staticmethod
    def _document(value: bytes, reference: str) -> dict[str, Any]:
        try:
            document = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ProjectSubmissionContractFailure(
                "assessment.project.schema_invalid", reference
            ) from error
        if not isinstance(document, dict):
            raise ProjectSubmissionContractFailure(
                "assessment.project.schema_invalid", reference
            )
        return document

    def _version(self, document: Mapping[str, Any]) -> None:
        if document.get("schema_version") != VERSION:
            self._reject("assessment.project.unsupported_version", "schema_version")

    def _shape(self, kind: str, document: Mapping[str, Any]) -> None:
        error = next(iter(self._validators[kind].iter_errors(document)), None)
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            self._reject("assessment.project.schema_invalid", reference or kind)

    @staticmethod
    def _timestamp(value: str, reference: str = "timestamp") -> datetime:
        try:
            return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
        except (TypeError, ValueError) as error:
            raise ProjectSubmissionContractFailure(
                "assessment.project.schema_invalid", reference
            ) from error

    @staticmethod
    def _aware_timestamp(value: datetime, reference: str) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ProjectSubmissionContractFailure(
                "assessment.project.invalid_server_metadata", reference
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
        raise ProjectSubmissionContractFailure(code, reference)
