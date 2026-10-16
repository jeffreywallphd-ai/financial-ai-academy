"""Atomic append-oriented PostgreSQL Assessment repository."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, Mapping

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from ..domain.models import AssessmentSubmissionCandidate
from ..domain.practice import (
    MultipleSelectPracticeResponse,
    NumericEntryPracticeResponse,
    PracticeFeedback,
    PracticeItemOutcome,
    PracticeResult,
    PracticeSubmissionCandidate,
    SingleSelectPracticeResponse,
)
from ..ports.repositories import (
    KnowledgeCheckAlreadyCompleted,
    PracticeAlreadyCompleted,
    PracticeSubmissionConflict,
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
        self, candidate: PracticeSubmissionCandidate
    ) -> tuple[PracticeResult, bool]:
        result = candidate.result
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.transaction():
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
                        submitted_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
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
                        result.definition_digest,
                        result.practice_id,
                        result.practice_version,
                        result.attempt_policy_id,
                        result.attempt_policy_version,
                        result.score,
                        result.max_score,
                        result.outcome,
                        result.submitted_at,
                    ),
                ).fetchone()
                if inserted is None:
                    return self._resolve_existing_practice(
                        connection, candidate
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

    def _resolve_existing_practice(
        self,
        connection: psycopg.Connection,
        candidate: PracticeSubmissionCandidate,
    ) -> tuple[PracticeResult, bool]:
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
            return self._practice_result_from_dict(row["result"]), False
        row = connection.execute(
            """
            SELECT 1
            FROM assessment.practice_attempts
            WHERE learner_id = %s
              AND placement_id = %s
              AND practice_id = %s
              AND practice_version = %s
            """,
            (
                result.learner_id,
                result.placement_id,
                result.practice_id,
                result.practice_version,
            ),
        ).fetchone()
        if row is not None:
            raise PracticeAlreadyCompleted(
                "Practice activity already has accepted evidence."
            )
        raise RuntimeError("Conflicting practice submission did not become visible.")

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
        response = item.response
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
            common = {
                "item_id": str(raw["item_id"]),
                "item_version": str(raw["item_version"]),
                "item_type": str(raw["item_type"]),
                "scoring_policy_id": str(raw["scoring_policy_id"]),
                "scoring_policy_version": str(
                    raw["scoring_policy_version"]
                ),
            }
            if common["item_type"] == "single_select":
                response = SingleSelectPracticeResponse(
                    **common,
                    selected_option_id=str(raw["selected_option_id"]),
                )
            elif common["item_type"] == "multiple_select":
                selected = raw["selected_option_ids"]
                if not isinstance(selected, list):
                    raise ValueError("Stored multiple selection is invalid.")
                response = MultipleSelectPracticeResponse(
                    **common,
                    selected_option_ids=tuple(str(item) for item in selected),
                )
            elif common["item_type"] == "numeric_entry":
                response = NumericEntryPracticeResponse(
                    **common,
                    entered_value=str(raw["entered_value"]),
                )
            else:
                raise ValueError("Stored practice response type is invalid.")
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

