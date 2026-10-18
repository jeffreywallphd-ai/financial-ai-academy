"""Append-only PostgreSQL Audit record storage."""

from __future__ import annotations

from collections.abc import Callable

import psycopg
from psycopg.rows import dict_row

from ..domain.models import (
    AssessmentCompletionAuditRecord,
    ProjectCompletionAuditRecord,
)
from ..ports.repositories import AuditRecordConflict


class PostgresAuditRepository:
    def __init__(
        self,
        dsn: str,
        *,
        before_commit: Callable[[], None] | None = None,
    ) -> None:
        self._dsn = dsn
        self._before_commit = before_commit

    def append_assessment_completion_records(
        self, records: tuple[AssessmentCompletionAuditRecord, ...]
    ) -> None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.transaction():
                for record in records:
                    inserted = connection.execute(
                        """
                        INSERT INTO audit.assessment_completion_records (
                            audit_id,
                            event_id,
                            evidence_id,
                            attempt_id,
                            actor_id,
                            action,
                            placement_id,
                            package_id,
                            package_version,
                            package_digest,
                            assessment_id,
                            assessment_version,
                            definition_digest,
                            occurred_at,
                            integrity_digest,
                            recorded_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (event_id) DO NOTHING
                        RETURNING event_id
                        """,
                        (
                            record.audit_id,
                            record.event_id,
                            record.evidence_id,
                            record.attempt_id,
                            record.actor_id,
                            record.action,
                            record.placement_id,
                            record.package_id,
                            record.package_version,
                            record.package_digest,
                            record.assessment_id,
                            record.assessment_version,
                            record.definition_digest,
                            record.occurred_at,
                            record.integrity_digest,
                            record.recorded_at,
                        ),
                    ).fetchone()
                    if inserted is None:
                        self._assert_same(connection, record)
                if self._before_commit is not None:
                    self._before_commit()

    def append_project_completion_records(
        self, records: tuple[ProjectCompletionAuditRecord, ...]
    ) -> None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.transaction():
                for record in records:
                    inserted = connection.execute(
                        """
                        INSERT INTO audit.project_completion_records (
                            audit_id,
                            event_id,
                            evidence_id,
                            submission_id,
                            actor_id,
                            action,
                            project_id,
                            snapshot_id,
                            snapshot_digest,
                            brief_id,
                            brief_version,
                            brief_digest,
                            placement_id,
                            placement_version,
                            placement_digest,
                            policy_id,
                            policy_version,
                            occurrence,
                            supersedes_submission_id,
                            occurred_at,
                            integrity_digest,
                            recorded_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (event_id) DO NOTHING
                        RETURNING event_id
                        """,
                        (
                            record.audit_id,
                            record.event_id,
                            record.evidence_id,
                            record.submission_id,
                            record.actor_id,
                            record.action,
                            record.project_id,
                            record.snapshot_id,
                            record.snapshot_digest,
                            record.brief_id,
                            record.brief_version,
                            record.brief_digest,
                            record.placement_id,
                            record.placement_version,
                            record.placement_digest,
                            record.policy_id,
                            record.policy_version,
                            record.occurrence,
                            record.supersedes_submission_id,
                            record.occurred_at,
                            record.integrity_digest,
                            record.recorded_at,
                        ),
                    ).fetchone()
                    if inserted is None:
                        self._assert_same_project(connection, record)
                if self._before_commit is not None:
                    self._before_commit()

    def read_assessment_completion_record(
        self,
        *,
        actor_id: str,
        placement_id: str,
        evidence_id: str,
    ) -> AssessmentCompletionAuditRecord | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT
                    audit_id,
                    event_id,
                    evidence_id,
                    attempt_id,
                    actor_id,
                    action,
                    placement_id,
                    package_id,
                    package_version,
                    package_digest,
                    assessment_id,
                    assessment_version,
                    definition_digest,
                    occurred_at,
                    integrity_digest,
                    recorded_at
                FROM audit.assessment_completion_records
                WHERE actor_id = %s
                  AND placement_id = %s
                  AND evidence_id = %s
                """,
                (actor_id, placement_id, evidence_id),
            ).fetchone()
        if row is None:
            return None
        return AssessmentCompletionAuditRecord(
            audit_id=str(row["audit_id"]),
            event_id=str(row["event_id"]),
            evidence_id=str(row["evidence_id"]),
            attempt_id=str(row["attempt_id"]),
            actor_id=str(row["actor_id"]),
            action=str(row["action"]),
            placement_id=str(row["placement_id"]),
            package_id=str(row["package_id"]),
            package_version=str(row["package_version"]),
            package_digest=str(row["package_digest"]),
            assessment_id=str(row["assessment_id"]),
            assessment_version=str(row["assessment_version"]),
            definition_digest=str(row["definition_digest"]),
            occurred_at=row["occurred_at"],
            integrity_digest=str(row["integrity_digest"]),
            recorded_at=row["recorded_at"],
        )

    @staticmethod
    def _assert_same(
        connection: psycopg.Connection,
        record: AssessmentCompletionAuditRecord,
    ) -> None:
        existing = connection.execute(
            """
            SELECT
                audit_id,
                evidence_id,
                attempt_id,
                actor_id,
                action,
                integrity_digest
            FROM audit.assessment_completion_records
            WHERE event_id = %s
            """,
            (record.event_id,),
        ).fetchone()
        expected = {
            "audit_id": record.audit_id,
            "evidence_id": record.evidence_id,
            "attempt_id": record.attempt_id,
            "actor_id": record.actor_id,
            "action": record.action,
            "integrity_digest": record.integrity_digest,
        }
        actual = None
        if existing is not None:
            actual = {
                "audit_id": str(existing["audit_id"]),
                "evidence_id": str(existing["evidence_id"]),
                "attempt_id": str(existing["attempt_id"]),
                "actor_id": str(existing["actor_id"]),
                "action": str(existing["action"]),
                "integrity_digest": str(existing["integrity_digest"]),
            }
        if actual != expected:
            raise AuditRecordConflict(
                "Audit event identity maps to different source evidence."
            )

    @staticmethod
    def _assert_same_project(
        connection: psycopg.Connection,
        record: ProjectCompletionAuditRecord,
    ) -> None:
        existing = connection.execute(
            """
            SELECT
                audit_id,
                evidence_id,
                submission_id,
                actor_id,
                action,
                integrity_digest
            FROM audit.project_completion_records
            WHERE event_id = %s
            """,
            (record.event_id,),
        ).fetchone()
        expected = {
            "audit_id": record.audit_id,
            "evidence_id": record.evidence_id,
            "submission_id": record.submission_id,
            "actor_id": record.actor_id,
            "action": record.action,
            "integrity_digest": record.integrity_digest,
        }
        actual = None
        if existing is not None:
            actual = {
                "audit_id": str(existing["audit_id"]),
                "evidence_id": str(existing["evidence_id"]),
                "submission_id": str(existing["submission_id"]),
                "actor_id": str(existing["actor_id"]),
                "action": str(existing["action"]),
                "integrity_digest": str(existing["integrity_digest"]),
            }
        if actual != expected:
            raise AuditRecordConflict(
                "Audit event identity maps to different source evidence."
            )
