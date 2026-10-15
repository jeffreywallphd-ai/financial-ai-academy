"""Atomic append-oriented PostgreSQL Assessment repository."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, Mapping

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from ..domain.models import AssessmentSubmissionCandidate
from ..ports.repositories import (
    KnowledgeCheckAlreadyCompleted,
    SubmissionConflict,
)
from ..public import (
    KnowledgeCheckFeedback,
    KnowledgeCheckResult,
)


class PostgresAssessmentRepository:
    def __init__(
        self,
        dsn: str,
        *,
        before_outbox: Callable[[], None] | None = None,
    ) -> None:
        self._dsn = dsn
        self._before_outbox = before_outbox

    def record_submission(
        self, candidate: AssessmentSubmissionCandidate
    ) -> tuple[KnowledgeCheckResult, bool]:
        result = candidate.result
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.transaction():
                inserted = connection.execute(
                    """
                    INSERT INTO assessment.attempts (
                        attempt_id,
                        learner_id,
                        submission_id,
                        request_fingerprint,
                        placement_id,
                        package_id,
                        package_version,
                        package_digest,
                        assessment_id,
                        assessment_version,
                        definition_digest,
                        item_id,
                        item_version,
                        scoring_policy_id,
                        scoring_policy_version,
                        submitted_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT DO NOTHING
                    RETURNING attempt_id
                    """,
                    (
                        result.attempt_id,
                        result.learner_id,
                        result.submission_id,
                        candidate.request_fingerprint,
                        result.placement_id,
                        result.package_id,
                        result.package_version,
                        result.package_digest,
                        result.assessment_id,
                        result.assessment_version,
                        result.definition_digest,
                        result.item_id,
                        result.item_version,
                        result.scoring_policy_id,
                        result.scoring_policy_version,
                        result.submitted_at,
                    ),
                ).fetchone()
                if inserted is None:
                    return self._resolve_existing(
                        connection,
                        candidate,
                    )
                connection.execute(
                    """
                    INSERT INTO assessment.responses (
                        attempt_id, selected_option_id
                    ) VALUES (%s, %s)
                    """,
                    (result.attempt_id, result.selected_option_id),
                )
                connection.execute(
                    """
                    INSERT INTO assessment.scores (
                        attempt_id,
                        score,
                        max_score,
                        correct,
                        feedback_id,
                        feedback_text
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        result.attempt_id,
                        result.score,
                        result.max_score,
                        result.correct,
                        result.feedback.feedback_id,
                        result.feedback.text,
                    ),
                )
                result_value = self._result_to_dict(result)
                connection.execute(
                    """
                    INSERT INTO assessment.completion_evidence (
                        evidence_id, attempt_id, result, recorded_at
                    ) VALUES (%s, %s, %s, %s)
                    """,
                    (
                        result.evidence_id,
                        result.attempt_id,
                        Jsonb(result_value),
                        result.submitted_at,
                    ),
                )
                if self._before_outbox is not None:
                    self._before_outbox()
                connection.execute(
                    """
                    INSERT INTO assessment.outbox (
                        event_id,
                        evidence_id,
                        event_type,
                        event_version,
                        event_payload,
                        occurred_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        candidate.event_id,
                        result.evidence_id,
                        "assessment.knowledge-check.completed",
                        "1.0.0",
                        Jsonb(dict(candidate.event)),
                        candidate.occurred_at,
                    ),
                )
        return result, True

    def _resolve_existing(
        self,
        connection: psycopg.Connection,
        candidate: AssessmentSubmissionCandidate,
    ) -> tuple[KnowledgeCheckResult, bool]:
        result = candidate.result
        row = connection.execute(
            """
            SELECT a.request_fingerprint, e.result
            FROM assessment.attempts AS a
            JOIN assessment.completion_evidence AS e
              ON e.attempt_id = a.attempt_id
            WHERE a.learner_id = %s AND a.submission_id = %s
            """,
            (result.learner_id, result.submission_id),
        ).fetchone()
        if row is not None:
            if row["request_fingerprint"] != candidate.request_fingerprint:
                raise SubmissionConflict(
                    "Submission identity maps to different input."
                )
            return self._result_from_dict(row["result"]), False
        row = connection.execute(
            """
            SELECT 1
            FROM assessment.attempts
            WHERE learner_id = %s
              AND placement_id = %s
              AND assessment_id = %s
              AND assessment_version = %s
            """,
            (
                result.learner_id,
                result.placement_id,
                result.assessment_id,
                result.assessment_version,
            ),
        ).fetchone()
        if row is not None:
            raise KnowledgeCheckAlreadyCompleted(
                "Knowledge check already has accepted evidence."
            )
        raise RuntimeError("Conflicting submission did not become visible.")

    @staticmethod
    def _result_to_dict(result: KnowledgeCheckResult) -> dict[str, object]:
        return {
            "attempt_id": result.attempt_id,
            "evidence_id": result.evidence_id,
            "learner_id": result.learner_id,
            "submission_id": result.submission_id,
            "placement_id": result.placement_id,
            "package_id": result.package_id,
            "package_version": result.package_version,
            "package_digest": result.package_digest,
            "assessment_id": result.assessment_id,
            "assessment_version": result.assessment_version,
            "definition_digest": result.definition_digest,
            "item_id": result.item_id,
            "item_version": result.item_version,
            "scoring_policy_id": result.scoring_policy_id,
            "scoring_policy_version": result.scoring_policy_version,
            "selected_option_id": result.selected_option_id,
            "score": result.score,
            "max_score": result.max_score,
            "correct": result.correct,
            "feedback": {
                "feedback_id": result.feedback.feedback_id,
                "text": result.feedback.text,
            },
            "submitted_at": result.submitted_at.isoformat(),
        }

    @staticmethod
    def _result_from_dict(value: Mapping[str, Any]) -> KnowledgeCheckResult:
        feedback = value["feedback"]
        if not isinstance(feedback, Mapping):
            raise ValueError("Stored Assessment feedback is invalid.")
        submitted_at = datetime.fromisoformat(str(value["submitted_at"]))
        return KnowledgeCheckResult(
            attempt_id=str(value["attempt_id"]),
            evidence_id=str(value["evidence_id"]),
            learner_id=str(value["learner_id"]),
            submission_id=str(value["submission_id"]),
            placement_id=str(value["placement_id"]),
            package_id=str(value["package_id"]),
            package_version=str(value["package_version"]),
            package_digest=str(value["package_digest"]),
            assessment_id=str(value["assessment_id"]),
            assessment_version=str(value["assessment_version"]),
            definition_digest=str(value["definition_digest"]),
            item_id=str(value["item_id"]),
            item_version=str(value["item_version"]),
            scoring_policy_id=str(value["scoring_policy_id"]),
            scoring_policy_version=str(value["scoring_policy_version"]),
            selected_option_id=str(value["selected_option_id"]),
            score=int(value["score"]),
            max_score=int(value["max_score"]),
            correct=bool(value["correct"]),
            feedback=KnowledgeCheckFeedback(
                feedback_id=str(feedback["feedback_id"]),
                text=str(feedback["text"]),
            ),
            submitted_at=submitted_at,
        )

