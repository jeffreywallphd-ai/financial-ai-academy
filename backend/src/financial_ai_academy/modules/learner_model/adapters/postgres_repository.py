"""Atomic PostgreSQL storage for rebuildable learner projections."""

from __future__ import annotations

from collections.abc import Callable

import psycopg

from ..domain.models import LessonCompletionProjection


class PostgresCompletionProjectionRepository:
    def __init__(
        self,
        dsn: str,
        *,
        before_projection: Callable[[], None] | None = None,
    ) -> None:
        self._dsn = dsn
        self._before_projection = before_projection

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
