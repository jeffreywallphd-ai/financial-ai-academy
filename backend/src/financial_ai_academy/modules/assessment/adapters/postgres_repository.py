"""Atomic append-oriented PostgreSQL Assessment repository."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
import hashlib
import json
from typing import Any, Mapping

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from ..domain.models import AssessmentSubmissionCandidate
from ..domain.practice import (
    MultipleSelectPracticeResponse,
    NumericEntryPracticeResponse,
    PracticeDraft,
    PracticeDraftSave,
    PracticeFeedback,
    PracticeItemOutcome,
    PracticeResult,
    PracticeScope,
    PracticeSubmissionCandidate,
    SingleSelectPracticeResponse,
)
from ..ports.repositories import (
    KnowledgeCheckAlreadyCompleted,
    PracticeAttemptLimitReached,
    PracticeDraftConflict,
    PracticeSubmissionConflict,
    StoredPracticeCompletionEvent,
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

    def list_completion_event_documents(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[Mapping[str, Any], ...]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            rows = connection.execute(
                """
                SELECT o.event_payload
                FROM assessment.outbox AS o
                JOIN assessment.completion_evidence AS e
                  ON e.evidence_id = o.evidence_id
                JOIN assessment.attempts AS a
                  ON a.attempt_id = e.attempt_id
                WHERE a.learner_id = %s
                  AND a.placement_id = %s
                ORDER BY o.occurred_at, o.event_id
                """,
                (learner_id, placement_id),
            ).fetchall()
        return tuple(row["event_payload"] for row in rows)

    def record_practice_submission(
        self, candidate: PracticeSubmissionCandidate, *, max_attempts: int
    ) -> tuple[PracticeResult, bool]:
        if not 1 <= max_attempts <= 10:
            raise ValueError("Practice attempt limit is outside the contract.")
        result = candidate.result
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.transaction():
                existing = self._find_existing_practice(connection, candidate)
                if existing is not None:
                    return existing, False
                self._lock_practice_scope(connection, result)
                existing = self._find_existing_practice(connection, candidate)
                if existing is not None:
                    return existing, False
                row = connection.execute(
                    """
                    SELECT COALESCE(MAX(attempt_order), 0) AS last_order
                    FROM assessment.practice_attempts
                    WHERE learner_id = %s
                      AND placement_id = %s
                      AND package_id = %s
                      AND package_version = %s
                      AND package_digest = %s
                      AND definition_digest = %s
                      AND practice_id = %s
                      AND practice_version = %s
                      AND attempt_policy_id = %s
                      AND attempt_policy_version = %s
                    """,
                    self._scope_values(result.learner_id, self._result_scope(result)),
                ).fetchone()
                last_order = int(row["last_order"])
                if last_order >= max_attempts:
                    raise PracticeAttemptLimitReached(
                        "Practice attempt limit has been reached."
                    )
                attempt_order = last_order + 1
                inserted = connection.execute(
                    """
                    INSERT INTO assessment.practice_attempts (
                        attempt_id,
                        learner_id,
                        submission_id,
                        request_fingerprint,
                        placement_id,
                        package_id,
                        package_version,
                        package_digest,
                        definition_digest,
                        practice_id,
                        practice_version,
                        attempt_policy_id,
                        attempt_policy_version,
                        score,
                        max_score,
                        outcome,
                        attempt_order,
                        submitted_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
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
                        result.definition_digest,
                        result.practice_id,
                        result.practice_version,
                        result.attempt_policy_id,
                        result.attempt_policy_version,
                        result.score,
                        result.max_score,
                        result.outcome,
                        attempt_order,
                        result.submitted_at,
                    ),
                ).fetchone()
                if inserted is None:
                    existing = self._find_existing_practice(connection, candidate)
                    if existing is not None:
                        return existing, False
                    raise RuntimeError(
                        "Conflicting practice submission did not become visible."
                    )
                for position, item in enumerate(result.item_results):
                    response = self._practice_response_to_dict(item)
                    connection.execute(
                        """
                        INSERT INTO assessment.practice_responses (
                            attempt_id,
                            item_position,
                            item_id,
                            item_version,
                            item_type,
                            scoring_policy_id,
                            scoring_policy_version,
                            response
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            result.attempt_id,
                            position,
                            item.response.item_id,
                            item.response.item_version,
                            item.response.item_type,
                            item.response.scoring_policy_id,
                            item.response.scoring_policy_version,
                            Jsonb(response),
                        ),
                    )
                    connection.execute(
                        """
                        INSERT INTO assessment.practice_scores (
                            attempt_id,
                            item_position,
                            item_id,
                            score,
                            max_score,
                            correct,
                            feedback_id,
                            feedback_text,
                            review_reference_ids
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            result.attempt_id,
                            position,
                            item.response.item_id,
                            item.score,
                            item.max_score,
                            item.correct,
                            item.feedback.feedback_id,
                            item.feedback.text,
                            Jsonb(list(item.feedback.review_reference_ids)),
                        ),
                    )
                connection.execute(
                    """
                    INSERT INTO assessment.practice_completion_evidence (
                        evidence_id, attempt_id, result, recorded_at
                    ) VALUES (%s, %s, %s, %s)
                    """,
                    (
                        result.evidence_id,
                        result.attempt_id,
                        Jsonb(self._practice_result_to_dict(result)),
                        result.submitted_at,
                    ),
                )
                if self._before_outbox is not None:
                    self._before_outbox()
                connection.execute(
                    """
                    INSERT INTO assessment.practice_outbox (
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
                        "assessment.practice.completed",
                        "1.0.0",
                        Jsonb(dict(candidate.event)),
                        candidate.occurred_at,
                    ),
                )
                connection.execute(
                    """
                    DELETE FROM assessment.practice_drafts
                    WHERE learner_id = %s
                      AND placement_id = %s
                      AND package_id = %s
                      AND package_version = %s
                      AND package_digest = %s
                      AND definition_digest = %s
                      AND practice_id = %s
                      AND practice_version = %s
                      AND attempt_policy_id = %s
                      AND attempt_policy_version = %s
                    """,
                    self._scope_values(
                        result.learner_id, self._result_scope(result)
                    ),
                )
        return result, True

    def read_practice_draft(
        self, *, learner_id: str, scope: PracticeScope
    ) -> PracticeDraft | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT responses, response_fingerprint, revision, saved_at
                FROM assessment.practice_drafts
                WHERE learner_id = %s
                  AND placement_id = %s
                  AND package_id = %s
                  AND package_version = %s
                  AND package_digest = %s
                  AND definition_digest = %s
                  AND practice_id = %s
                  AND practice_version = %s
                  AND attempt_policy_id = %s
                  AND attempt_policy_version = %s
                """,
                self._scope_values(learner_id, scope),
            ).fetchone()
        return None if row is None else self._draft_from_row(scope, row)

    def save_practice_draft(
        self,
        *,
        learner_id: str,
        draft: PracticeDraftSave,
        saved_at: datetime,
    ) -> PracticeDraft:
        scope = draft.scope
        response_values = [
            self._practice_response_value(response) for response in draft.responses
        ]
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.transaction():
                self._lock_scope(connection, learner_id, scope)
                row = connection.execute(
                    """
                    SELECT responses, response_fingerprint, revision, saved_at
                    FROM assessment.practice_drafts
                    WHERE learner_id = %s
                      AND placement_id = %s
                      AND package_id = %s
                      AND package_version = %s
                      AND package_digest = %s
                      AND definition_digest = %s
                      AND practice_id = %s
                      AND practice_version = %s
                      AND attempt_policy_id = %s
                      AND attempt_policy_version = %s
                    FOR UPDATE
                    """,
                    self._scope_values(learner_id, scope),
                ).fetchone()
                if row is None:
                    if draft.expected_revision != 0:
                        raise PracticeDraftConflict(
                            "Practice draft revision is stale."
                        )
                    revision = 1
                    connection.execute(
                        """
                        INSERT INTO assessment.practice_drafts (
                            learner_id,
                            placement_id,
                            package_id,
                            package_version,
                            package_digest,
                            definition_digest,
                            practice_id,
                            practice_version,
                            attempt_policy_id,
                            attempt_policy_version,
                            responses,
                            response_fingerprint,
                            revision,
                            saved_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            *self._scope_values(learner_id, scope),
                            Jsonb(response_values),
                            draft.response_fingerprint,
                            revision,
                            saved_at,
                        ),
                    )
                elif row["response_fingerprint"] == draft.response_fingerprint:
                    return self._draft_from_row(scope, row)
                else:
                    if int(row["revision"]) != draft.expected_revision:
                        raise PracticeDraftConflict(
                            "Practice draft revision is stale."
                        )
                    revision = int(row["revision"]) + 1
                    connection.execute(
                        """
                        UPDATE assessment.practice_drafts
                        SET responses = %s,
                            response_fingerprint = %s,
                            revision = %s,
                            saved_at = %s
                        WHERE learner_id = %s
                          AND placement_id = %s
                          AND package_id = %s
                          AND package_version = %s
                          AND package_digest = %s
                          AND definition_digest = %s
                          AND practice_id = %s
                          AND practice_version = %s
                          AND attempt_policy_id = %s
                          AND attempt_policy_version = %s
                        """,
                        (
                            Jsonb(response_values),
                            draft.response_fingerprint,
                            revision,
                            saved_at,
                            *self._scope_values(learner_id, scope),
                        ),
                    )
        return PracticeDraft(
            scope=scope,
            responses=draft.responses,
            revision=revision,
            saved_at=saved_at,
            response_fingerprint=draft.response_fingerprint,
        )

    def count_practice_attempts(
        self, *, learner_id: str, scope: PracticeScope
    ) -> int:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT count(*) AS attempts_used
                FROM assessment.practice_attempts
                WHERE learner_id = %s
                  AND placement_id = %s
                  AND package_id = %s
                  AND package_version = %s
                  AND package_digest = %s
                  AND definition_digest = %s
                  AND practice_id = %s
                  AND practice_version = %s
                  AND attempt_policy_id = %s
                  AND attempt_policy_version = %s
                """,
                self._scope_values(learner_id, scope),
            ).fetchone()
        return int(row["attempts_used"])

    def list_practice_completion_event_documents(
        self, *, learner_id: str, scope: PracticeScope
    ) -> tuple[StoredPracticeCompletionEvent, ...]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            rows = connection.execute(
                """
                SELECT
                    o.event_id,
                    a.attempt_id,
                    e.evidence_id,
                    a.submission_id,
                    a.attempt_order,
                    o.event_payload
                FROM assessment.practice_outbox AS o
                JOIN assessment.practice_completion_evidence AS e
                  ON e.evidence_id = o.evidence_id
                JOIN assessment.practice_attempts AS a
                  ON a.attempt_id = e.attempt_id
                WHERE a.learner_id = %s
                  AND a.placement_id = %s
                  AND a.package_id = %s
                  AND a.package_version = %s
                  AND a.package_digest = %s
                  AND a.definition_digest = %s
                  AND a.practice_id = %s
                  AND a.practice_version = %s
                  AND a.attempt_policy_id = %s
                  AND a.attempt_policy_version = %s
                ORDER BY a.attempt_order, o.event_id
                """,
                self._scope_values(learner_id, scope),
            ).fetchall()
        return tuple(
            StoredPracticeCompletionEvent(
                event_id=str(row["event_id"]),
                attempt_id=str(row["attempt_id"]),
                evidence_id=str(row["evidence_id"]),
                submission_id=str(row["submission_id"]),
                attempt_order=int(row["attempt_order"]),
                document=row["event_payload"],
            )
            for row in rows
        )

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

    def _find_existing_practice(
        self,
        connection: psycopg.Connection,
        candidate: PracticeSubmissionCandidate,
    ) -> PracticeResult | None:
        result = candidate.result
        row = connection.execute(
            """
            SELECT a.request_fingerprint, e.result
            FROM assessment.practice_attempts AS a
            JOIN assessment.practice_completion_evidence AS e
              ON e.attempt_id = a.attempt_id
            WHERE a.learner_id = %s AND a.submission_id = %s
            """,
            (result.learner_id, result.submission_id),
        ).fetchone()
        if row is not None:
            if row["request_fingerprint"] != candidate.request_fingerprint:
                raise PracticeSubmissionConflict(
                    "Submission identity maps to different input."
                )
            return self._practice_result_from_dict(row["result"])
        return None

    def _lock_practice_scope(
        self,
        connection: psycopg.Connection,
        result: PracticeResult,
    ) -> None:
        self._lock_scope(
            connection, result.learner_id, self._result_scope(result)
        )

    def _lock_scope(
        self,
        connection: psycopg.Connection,
        learner_id: str,
        scope: PracticeScope,
    ) -> None:
        values = self._scope_values(learner_id, scope)
        connection.execute(
            """
            INSERT INTO assessment.practice_retry_scopes (
                learner_id,
                placement_id,
                package_id,
                package_version,
                package_digest,
                definition_digest,
                practice_id,
                practice_version,
                attempt_policy_id,
                attempt_policy_version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            values,
        )
        connection.execute(
            """
            SELECT 1
            FROM assessment.practice_retry_scopes
            WHERE learner_id = %s
              AND placement_id = %s
              AND package_id = %s
              AND package_version = %s
              AND package_digest = %s
              AND definition_digest = %s
              AND practice_id = %s
              AND practice_version = %s
              AND attempt_policy_id = %s
              AND attempt_policy_version = %s
            FOR UPDATE
            """,
            values,
        ).fetchone()

    @staticmethod
    def _result_scope(result: PracticeResult) -> PracticeScope:
        return PracticeScope(
            placement_id=result.placement_id,
            package_id=result.package_id,
            package_version=result.package_version,
            package_digest=result.package_digest,
            definition_digest=result.definition_digest,
            practice_id=result.practice_id,
            practice_version=result.practice_version,
            attempt_policy_id=result.attempt_policy_id,
            attempt_policy_version=result.attempt_policy_version,
        )

    @staticmethod
    def _scope_values(
        learner_id: str, scope: PracticeScope
    ) -> tuple[str, ...]:
        return (
            learner_id,
            scope.placement_id,
            scope.package_id,
            scope.package_version,
            scope.package_digest,
            scope.definition_digest,
            scope.practice_id,
            scope.practice_version,
            scope.attempt_policy_id,
            scope.attempt_policy_version,
        )

    @classmethod
    def _draft_from_row(
        cls, scope: PracticeScope, row: Mapping[str, Any]
    ) -> PracticeDraft:
        values = row["responses"]
        if not isinstance(values, list):
            raise ValueError("Stored practice draft responses are invalid.")
        responses = tuple(
            cls._practice_response_from_dict(value, strict=True)
            for value in values
        )
        fingerprint = cls._draft_response_fingerprint(responses)
        if fingerprint != row["response_fingerprint"]:
            raise ValueError("Stored practice draft fingerprint is invalid.")
        return PracticeDraft(
            scope=scope,
            responses=responses,
            revision=int(row["revision"]),
            saved_at=row["saved_at"],
            response_fingerprint=fingerprint,
        )

    @classmethod
    def _draft_response_fingerprint(
        cls,
        responses: tuple[
            SingleSelectPracticeResponse
            | MultipleSelectPracticeResponse
            | NumericEntryPracticeResponse,
            ...,
        ],
    ) -> str:
        canonical = [cls._practice_response_value(item) for item in responses]
        for response in canonical:
            selected = response.get("selected_option_ids")
            if isinstance(selected, list):
                response["selected_option_ids"] = sorted(selected)
        canonical.sort(key=lambda item: str(item.get("item_id", "")))
        value = json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(value).hexdigest()

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

    @staticmethod
    def _practice_response_to_dict(
        item: PracticeItemOutcome,
    ) -> dict[str, object]:
        return PostgresAssessmentRepository._practice_response_value(
            item.response
        )

    @staticmethod
    def _practice_response_value(
        response: (
            SingleSelectPracticeResponse
            | MultipleSelectPracticeResponse
            | NumericEntryPracticeResponse
        ),
    ) -> dict[str, object]:
        value: dict[str, object] = {
            "item_id": response.item_id,
            "item_version": response.item_version,
            "item_type": response.item_type,
            "scoring_policy_id": response.scoring_policy_id,
            "scoring_policy_version": response.scoring_policy_version,
        }
        if isinstance(response, SingleSelectPracticeResponse):
            value["selected_option_id"] = response.selected_option_id
        elif isinstance(response, MultipleSelectPracticeResponse):
            value["selected_option_ids"] = list(response.selected_option_ids)
        else:
            value["entered_value"] = response.entered_value
        return value

    @staticmethod
    def _practice_response_from_dict(
        raw: Mapping[str, Any], *, strict: bool = False
    ) -> (
        SingleSelectPracticeResponse
        | MultipleSelectPracticeResponse
        | NumericEntryPracticeResponse
    ):
        item_type = str(raw.get("item_type", ""))
        expected_keys = {
            "item_id",
            "item_version",
            "item_type",
            "scoring_policy_id",
            "scoring_policy_version",
            {
                "single_select": "selected_option_id",
                "multiple_select": "selected_option_ids",
                "numeric_entry": "entered_value",
            }.get(item_type, "invalid"),
        }
        if strict and set(raw) != expected_keys:
            raise ValueError("Stored practice response shape is invalid.")
        common = {
            "item_id": str(raw["item_id"]),
            "item_version": str(raw["item_version"]),
            "item_type": item_type,
            "scoring_policy_id": str(raw["scoring_policy_id"]),
            "scoring_policy_version": str(raw["scoring_policy_version"]),
        }
        if common["item_type"] == "single_select":
            return SingleSelectPracticeResponse(
                **common,
                selected_option_id=str(raw["selected_option_id"]),
            )
        if common["item_type"] == "multiple_select":
            selected = raw["selected_option_ids"]
            if not isinstance(selected, list):
                raise ValueError("Stored multiple selection is invalid.")
            return MultipleSelectPracticeResponse(
                **common,
                selected_option_ids=tuple(str(item) for item in selected),
            )
        if common["item_type"] == "numeric_entry":
            return NumericEntryPracticeResponse(
                **common,
                entered_value=str(raw["entered_value"]),
            )
        raise ValueError("Stored practice response type is invalid.")

    @classmethod
    def _practice_result_to_dict(
        cls, result: PracticeResult
    ) -> dict[str, object]:
        return {
            "schema_version": result.schema_version,
            "attempt_id": result.attempt_id,
            "evidence_id": result.evidence_id,
            "learner_id": result.learner_id,
            "submission_id": result.submission_id,
            "request_fingerprint": result.request_fingerprint,
            "placement_id": result.placement_id,
            "package_id": result.package_id,
            "package_version": result.package_version,
            "package_digest": result.package_digest,
            "definition_digest": result.definition_digest,
            "practice_id": result.practice_id,
            "practice_version": result.practice_version,
            "attempt_policy_id": result.attempt_policy_id,
            "attempt_policy_version": result.attempt_policy_version,
            "score": result.score,
            "max_score": result.max_score,
            "outcome": result.outcome,
            "review_reference_ids": list(result.review_reference_ids),
            "item_results": [
                {
                    **cls._practice_response_to_dict(item),
                    "score": item.score,
                    "max_score": item.max_score,
                    "correct": item.correct,
                    "feedback": {
                        "feedback_id": item.feedback.feedback_id,
                        "text": item.feedback.text,
                        "review_reference_ids": list(
                            item.feedback.review_reference_ids
                        ),
                    },
                }
                for item in result.item_results
            ],
            "submitted_at": result.submitted_at.isoformat().replace(
                "+00:00", "Z"
            ),
        }

    @staticmethod
    def _practice_result_from_dict(value: Mapping[str, Any]) -> PracticeResult:
        items: list[PracticeItemOutcome] = []
        raw_items = value["item_results"]
        if not isinstance(raw_items, list):
            raise ValueError("Stored practice item results are invalid.")
        for raw in raw_items:
            if not isinstance(raw, Mapping):
                raise ValueError("Stored practice item result is invalid.")
            response = PostgresAssessmentRepository._practice_response_from_dict(
                raw
            )
            feedback = raw["feedback"]
            if not isinstance(feedback, Mapping):
                raise ValueError("Stored practice feedback is invalid.")
            references = feedback["review_reference_ids"]
            if not isinstance(references, list):
                raise ValueError("Stored practice references are invalid.")
            items.append(
                PracticeItemOutcome(
                    response=response,
                    score=int(raw["score"]),
                    max_score=int(raw["max_score"]),
                    correct=bool(raw["correct"]),
                    feedback=PracticeFeedback(
                        feedback_id=str(feedback["feedback_id"]),
                        text=str(feedback["text"]),
                        review_reference_ids=tuple(
                            str(item) for item in references
                        ),
                    ),
                )
            )
        references = value["review_reference_ids"]
        if not isinstance(references, list):
            raise ValueError("Stored practice references are invalid.")
        return PracticeResult(
            schema_version=str(value["schema_version"]),
            attempt_id=str(value["attempt_id"]),
            evidence_id=str(value["evidence_id"]),
            learner_id=str(value["learner_id"]),
            submission_id=str(value["submission_id"]),
            request_fingerprint=str(value["request_fingerprint"]),
            placement_id=str(value["placement_id"]),
            package_id=str(value["package_id"]),
            package_version=str(value["package_version"]),
            package_digest=str(value["package_digest"]),
            definition_digest=str(value["definition_digest"]),
            practice_id=str(value["practice_id"]),
            practice_version=str(value["practice_version"]),
            attempt_policy_id=str(value["attempt_policy_id"]),
            attempt_policy_version=str(value["attempt_policy_version"]),
            score=int(value["score"]),
            max_score=int(value["max_score"]),
            outcome=str(value["outcome"]),  # type: ignore[arg-type]
            review_reference_ids=tuple(str(item) for item in references),
            item_results=tuple(items),
            submitted_at=datetime.fromisoformat(str(value["submitted_at"])),
        )

