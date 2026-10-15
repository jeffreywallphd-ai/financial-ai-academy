"""Append-only PostgreSQL Audit record storage."""

from __future__ import annotations

from collections.abc import Callable

import psycopg
from psycopg.rows import dict_row

from ..domain.models import AssessmentCompletionAuditRecord
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
