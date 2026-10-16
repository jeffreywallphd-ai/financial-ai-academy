"""Atomic PostgreSQL storage for rebuildable learner projections."""

from __future__ import annotations

from collections.abc import Callable

import psycopg
from psycopg.types.json import Jsonb

from ..domain.models import LessonCompletionProjection, PracticeHistoryProjection


class PostgresCompletionProjectionRepository:
    def __init__(
        self,
        dsn: str,
        *,
        before_projection: Callable[[], None] | None = None,
        before_practice_projection: Callable[[], None] | None = None,
    ) -> None:
        self._dsn = dsn
        self._before_projection = before_projection
        self._before_practice_projection = before_practice_projection

    def replace(self, projection: LessonCompletionProjection) -> None:
        lock_key = f"{projection.learner_id}:{projection.placement_id}"
        with psycopg.connect(self._dsn) as connection:
            with connection.transaction():
                connection.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                    (lock_key,),
                )
                connection.execute(
                    """
                    DELETE FROM learner_model.lesson_completion_history
                    WHERE learner_id = %s AND placement_id = %s
                    """,
                    (projection.learner_id, projection.placement_id),
                )
                for item in projection.history:
                    connection.execute(
                        """
                        INSERT INTO learner_model.lesson_completion_history (
                            event_id,
                            learner_id,
                            placement_id,
                            attempt_id,
                            evidence_id,
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
                            score,
                            max_score,
                            completed_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            item.event_id,
                            item.learner_id,
                            item.placement_id,
                            item.attempt_id,
                            item.evidence_id,
                            item.package_id,
                            item.package_version,
                            item.package_digest,
                            item.assessment_id,
                            item.assessment_version,
                            item.definition_digest,
                            item.item_id,
                            item.item_version,
                            item.scoring_policy_id,
                            item.scoring_policy_version,
                            item.score,
                            item.max_score,
                            item.completed_at,
                        ),
                    )
                if self._before_projection is not None:
                    self._before_projection()
                connection.execute(
                    """
                    INSERT INTO learner_model.lesson_completion_projections (
                        learner_id,
                        placement_id,
                        completed,
                        history_count,
                        source_digest,
                        rebuilt_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (learner_id, placement_id) DO UPDATE SET
                        completed = EXCLUDED.completed,
                        history_count = EXCLUDED.history_count,
                        source_digest = EXCLUDED.source_digest,
                        rebuilt_at = EXCLUDED.rebuilt_at
                    """,
                    (
                        projection.learner_id,
                        projection.placement_id,
                        projection.completed,
                        len(projection.history),
                        projection.source_digest,
                        projection.rebuilt_at,
                    ),
                )

    def replace_practice_history(
        self, projection: PracticeHistoryProjection
    ) -> None:
        scope = (
            projection.learner_id,
            projection.placement_id,
            projection.package_id,
            projection.package_version,
            projection.package_digest,
            projection.definition_digest,
            projection.practice_id,
            projection.practice_version,
            projection.attempt_policy_id,
            projection.attempt_policy_version,
        )
        lock_key = ":".join(scope)
        with psycopg.connect(self._dsn) as connection:
            with connection.transaction():
                connection.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                    (lock_key,),
                )
                connection.execute(
                    """
                    INSERT INTO learner_model.practice_history_projections (
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
                        source_digest,
                        attempt_count,
                        rebuilt_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (
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
                    ) DO UPDATE SET
                        source_digest = EXCLUDED.source_digest,
                        attempt_count = EXCLUDED.attempt_count,
                        rebuilt_at = EXCLUDED.rebuilt_at
                    """,
                    (*scope, projection.source_digest, len(projection.attempts), projection.rebuilt_at),
                )
                connection.execute(
                    """
                    DELETE FROM learner_model.practice_history_attempts
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
                    scope,
                )
                for attempt in projection.attempts:
                    connection.execute(
                        """
                        INSERT INTO learner_model.practice_history_attempts (
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
                            attempt_order,
                            event_id,
                            attempt_id,
                            evidence_id,
                            submission_id,
                            score,
                            max_score,
                            outcome,
                            item_summaries,
                            completed_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            *scope,
                            attempt.attempt_order,
                            attempt.event_id,
                            attempt.attempt_id,
                            attempt.evidence_id,
                            attempt.submission_id,
                            attempt.score,
                            attempt.max_score,
                            attempt.outcome,
                            Jsonb(
                                [
                                    {
                                        "item_id": item.item_id,
                                        "item_version": item.item_version,
                                        "item_type": item.item_type,
                                        "scoring_policy_id": (
                                            item.scoring_policy_id
                                        ),
                                        "scoring_policy_version": (
                                            item.scoring_policy_version
                                        ),
                                        "score": item.score,
                                        "max_score": item.max_score,
                                        "correct": item.correct,
                                        "review_reference_ids": list(
                                            item.review_reference_ids
                                        ),
                                    }
                                    for item in attempt.item_summaries
                                ]
                            ),
                            attempt.completed_at,
                        ),
                    )
                if self._before_practice_projection is not None:
                    self._before_practice_projection()
