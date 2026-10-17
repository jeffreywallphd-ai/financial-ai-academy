"""Atomic PostgreSQL storage for rebuildable learner projections."""

from __future__ import annotations

from collections.abc import Callable
import json

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from ..domain.models import (
    LessonCompletionProjection,
    PracticeHistoryProjection,
    ProjectCompletionProjection,
)
from ..domain.preferences import (
    LearnerPreferenceProfile,
    PreferenceChange,
    PreferenceHistory,
)
from ..domain.presentation_preferences import (
    PresentationPreferenceChange,
    PresentationPreferenceHistory,
    PresentationPreferenceProfile,
)
from ..ports.preference_contract import LearnerPreferenceContract
from ..ports.presentation_preference_contract import PresentationPreferenceContract
from ..ports.repositories import (
    LearnerPreferenceIdempotencyConflict,
    LearnerPreferenceRevisionConflict,
)


class PostgresCompletionProjectionRepository:
    def __init__(
        self,
        dsn: str,
        *,
        before_projection: Callable[[], None] | None = None,
        before_practice_projection: Callable[[], None] | None = None,
        before_project_projection: Callable[[], None] | None = None,
        preference_contract: LearnerPreferenceContract | None = None,
        before_preference_save: Callable[[], None] | None = None,
        presentation_preference_contract: PresentationPreferenceContract | None = None,
        before_presentation_preference_save: Callable[[], None] | None = None,
    ) -> None:
        self._dsn = dsn
        self._before_projection = before_projection
        self._before_practice_projection = before_practice_projection
        self._before_project_projection = before_project_projection
        self._preference_contract = preference_contract
        self._before_preference_save = before_preference_save
        self._presentation_preference_contract = presentation_preference_contract
        self._before_presentation_preference_save = (
            before_presentation_preference_save
        )

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

    def replace_project_completion(
        self, projection: ProjectCompletionProjection
    ) -> None:
        scope = (projection.learner_id, projection.project_id)
        lock_key = ":".join(scope)
        with psycopg.connect(self._dsn) as connection:
            with connection.transaction():
                connection.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                    (lock_key,),
                )
                connection.execute(
                    """
                    INSERT INTO learner_model.project_completion_projections (
                        learner_id,
                        project_id,
                        completed,
                        history_count,
                        source_digest,
                        rebuilt_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (learner_id, project_id) DO UPDATE SET
                        completed = EXCLUDED.completed,
                        history_count = EXCLUDED.history_count,
                        source_digest = EXCLUDED.source_digest,
                        rebuilt_at = EXCLUDED.rebuilt_at
                    """,
                    (
                        *scope,
                        projection.completed,
                        len(projection.history),
                        projection.source_digest,
                        projection.rebuilt_at,
                    ),
                )
                connection.execute(
                    """
                    DELETE FROM learner_model.project_completion_history
                    WHERE learner_id = %s AND project_id = %s
                    """,
                    scope,
                )
                for item in projection.history:
                    connection.execute(
                        """
                        INSERT INTO learner_model.project_completion_history (
                            learner_id,
                            project_id,
                            occurrence,
                            accepted_sequence,
                            event_id,
                            evidence_id,
                            submission_id,
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
                            milestone_ids,
                            request_fingerprint,
                            supersedes_submission_id,
                            submitted_at,
                            occurred_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            *scope,
                            item.occurrence,
                            item.accepted_sequence,
                            item.event_id,
                            item.evidence_id,
                            item.submission_id,
                            item.snapshot_id,
                            item.snapshot_digest,
                            item.brief_id,
                            item.brief_version,
                            item.brief_digest,
                            item.placement_id,
                            item.placement_version,
                            item.placement_digest,
                            item.policy_id,
                            item.policy_version,
                            Jsonb(list(item.milestone_ids)),
                            item.request_fingerprint,
                            item.supersedes_submission_id,
                            item.submitted_at,
                            item.occurred_at,
                        ),
                    )
                if self._before_project_projection is not None:
                    self._before_project_projection()

    def get_preferences(
        self, learner_id: str
    ) -> LearnerPreferenceProfile | None:
        contract = self._preferences()
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT profile FROM learner_model.preference_profiles
                WHERE learner_id = %s
                """,
                (learner_id,),
            ).fetchone()
        return self._parse_profile(contract, row["profile"]) if row else None

    def get_preference_history(
        self, learner_id: str
    ) -> PreferenceHistory | None:
        contract = self._preferences()
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            profile = connection.execute(
                """
                SELECT profile_id, revision
                FROM learner_model.preference_profiles
                WHERE learner_id = %s
                """,
                (learner_id,),
            ).fetchone()
            if profile is None:
                return None
            changes = connection.execute(
                """
                SELECT change FROM learner_model.preference_changes
                WHERE learner_id = %s ORDER BY revision
                """,
                (learner_id,),
            ).fetchall()
        document = {
            "schema_version": "1.0.0",
            "profile_id": profile["profile_id"],
            "current_revision": profile["revision"],
            "changes": [row["change"] for row in changes],
        }
        return contract.parse_history(self._json_bytes(document))

    def get_preference_replay(
        self, learner_id: str, idempotency_key: str
    ) -> tuple[str, LearnerPreferenceProfile] | None:
        contract = self._preferences()
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT request_fingerprint, accepted_profile
                FROM learner_model.preference_mutations
                WHERE learner_id = %s AND idempotency_key = %s
                """,
                (learner_id, idempotency_key),
            ).fetchone()
        if row is None:
            return None
        return (
            str(row["request_fingerprint"]),
            self._parse_profile(contract, row["accepted_profile"]),
        )

    def save_preferences_if_revision(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_revision: int,
        profile: LearnerPreferenceProfile,
        change: PreferenceChange,
    ) -> LearnerPreferenceProfile:
        contract = self._preferences()
        profile_document = contract.profile_document(profile)
        change_document = contract.history_document(
            PreferenceHistory(
                schema_version="1.0.0",
                profile_id=profile.profile_id,
                current_revision=profile.revision,
                changes=(change,),
            )
        )["changes"][0]
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.transaction():
                connection.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                    (f"learner-preferences:{profile.learner_id}",),
                )
                replay = connection.execute(
                    """
                    SELECT request_fingerprint, accepted_profile
                    FROM learner_model.preference_mutations
                    WHERE learner_id = %s AND idempotency_key = %s
                    """,
                    (profile.learner_id, idempotency_key),
                ).fetchone()
                if replay is not None:
                    if str(replay["request_fingerprint"]) != request_fingerprint:
                        raise LearnerPreferenceIdempotencyConflict()
                    return self._parse_profile(contract, replay["accepted_profile"])
                current = connection.execute(
                    """
                    SELECT profile_id, revision
                    FROM learner_model.preference_profiles
                    WHERE learner_id = %s FOR UPDATE
                    """,
                    (profile.learner_id,),
                ).fetchone()
                current_revision = int(current["revision"]) if current else 1
                if (
                    current_revision != expected_revision
                    or profile.revision != expected_revision + 1
                    or (current and current["profile_id"] != profile.profile_id)
                ):
                    raise LearnerPreferenceRevisionConflict()
                if current is None:
                    connection.execute(
                        """
                        INSERT INTO learner_model.preference_profiles (
                            profile_id, learner_id, revision, profile,
                            profile_digest, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            profile.profile_id,
                            profile.learner_id,
                            profile.revision,
                            Jsonb(profile_document),
                            profile.profile_digest,
                            profile.created_at,
                            profile.updated_at,
                        ),
                    )
                else:
                    connection.execute(
                        """
                        UPDATE learner_model.preference_profiles
                        SET revision = %s, profile = %s, profile_digest = %s,
                            updated_at = %s
                        WHERE learner_id = %s
                        """,
                        (
                            profile.revision,
                            Jsonb(profile_document),
                            profile.profile_digest,
                            profile.updated_at,
                            profile.learner_id,
                        ),
                    )
                connection.execute(
                    """
                    INSERT INTO learner_model.preference_changes (
                        learner_id, revision, change, occurred_at,
                        resulting_profile_digest
                    ) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        profile.learner_id,
                        change.revision,
                        Jsonb(change_document),
                        change.occurred_at,
                        change.resulting_profile_digest,
                    ),
                )
                connection.execute(
                    """
                    DELETE FROM learner_model.preference_changes
                    WHERE learner_id = %s AND revision IN (
                        SELECT revision
                        FROM learner_model.preference_changes
                        WHERE learner_id = %s
                        ORDER BY revision DESC OFFSET 100
                    )
                    """,
                    (profile.learner_id, profile.learner_id),
                )
                if self._before_preference_save is not None:
                    self._before_preference_save()
                connection.execute(
                    """
                    INSERT INTO learner_model.preference_mutations (
                        learner_id, idempotency_key, request_fingerprint,
                        accepted_profile, accepted_revision
                    ) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        profile.learner_id,
                        idempotency_key,
                        request_fingerprint,
                        Jsonb(profile_document),
                        profile.revision,
                    ),
                )
        return profile

    def get_presentation_preferences(
        self, learner_id: str
    ) -> PresentationPreferenceProfile | None:
        contract = self._presentation_preferences()
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT profile FROM learner_model.presentation_preference_profiles
                WHERE learner_id = %s
                """,
                (learner_id,),
            ).fetchone()
        return (
            self._parse_presentation_profile(contract, row["profile"])
            if row
            else None
        )

    def get_presentation_preference_history(
        self, learner_id: str
    ) -> PresentationPreferenceHistory | None:
        contract = self._presentation_preferences()
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            profile = connection.execute(
                """
                SELECT profile_id, revision
                FROM learner_model.presentation_preference_profiles
                WHERE learner_id = %s
                """,
                (learner_id,),
            ).fetchone()
            if profile is None:
                return None
            changes = connection.execute(
                """
                SELECT change FROM learner_model.presentation_preference_changes
                WHERE learner_id = %s ORDER BY revision
                """,
                (learner_id,),
            ).fetchall()
        document = {
            "schema_version": "1.0.0",
            "profile_id": profile["profile_id"],
            "current_revision": profile["revision"],
            "changes": [row["change"] for row in changes],
        }
        return contract.parse_history(self._json_bytes(document))

    def get_presentation_preference_replay(
        self, learner_id: str, idempotency_key: str
    ) -> tuple[str, PresentationPreferenceProfile] | None:
        contract = self._presentation_preferences()
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT request_fingerprint, accepted_profile
                FROM learner_model.presentation_preference_mutations
                WHERE learner_id = %s AND idempotency_key = %s
                """,
                (learner_id, idempotency_key),
            ).fetchone()
        if row is None:
            return None
        return (
            str(row["request_fingerprint"]),
            self._parse_presentation_profile(contract, row["accepted_profile"]),
        )

    def save_presentation_preferences_if_revision(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        expected_revision: int,
        profile: PresentationPreferenceProfile,
        change: PresentationPreferenceChange,
    ) -> PresentationPreferenceProfile:
        contract = self._presentation_preferences()
        profile_document = contract.profile_document(profile)
        change_document = contract.history_document(
            PresentationPreferenceHistory(
                schema_version="1.0.0",
                profile_id=profile.profile_id,
                current_revision=profile.revision,
                changes=(change,),
            )
        )["changes"][0]
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            with connection.transaction():
                connection.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                    (f"learner-presentation-preferences:{profile.learner_id}",),
                )
                replay = connection.execute(
                    """
                    SELECT request_fingerprint, accepted_profile
                    FROM learner_model.presentation_preference_mutations
                    WHERE learner_id = %s AND idempotency_key = %s
                    """,
                    (profile.learner_id, idempotency_key),
                ).fetchone()
                if replay is not None:
                    if str(replay["request_fingerprint"]) != request_fingerprint:
                        raise LearnerPreferenceIdempotencyConflict()
                    return self._parse_presentation_profile(
                        contract, replay["accepted_profile"]
                    )
                current = connection.execute(
                    """
                    SELECT profile_id, revision
                    FROM learner_model.presentation_preference_profiles
                    WHERE learner_id = %s FOR UPDATE
                    """,
                    (profile.learner_id,),
                ).fetchone()
                current_revision = int(current["revision"]) if current else 1
                if (
                    current_revision != expected_revision
                    or profile.revision != expected_revision + 1
                    or (current and current["profile_id"] != profile.profile_id)
                ):
                    raise LearnerPreferenceRevisionConflict()
                if current is None:
                    connection.execute(
                        """
                        INSERT INTO learner_model.presentation_preference_profiles (
                            profile_id, learner_id, revision, profile,
                            profile_digest, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            profile.profile_id,
                            profile.learner_id,
                            profile.revision,
                            Jsonb(profile_document),
                            profile.profile_digest,
                            profile.created_at,
                            profile.updated_at,
                        ),
                    )
                else:
                    connection.execute(
                        """
                        UPDATE learner_model.presentation_preference_profiles
                        SET revision = %s, profile = %s, profile_digest = %s,
                            updated_at = %s
                        WHERE learner_id = %s
                        """,
                        (
                            profile.revision,
                            Jsonb(profile_document),
                            profile.profile_digest,
                            profile.updated_at,
                            profile.learner_id,
                        ),
                    )
                connection.execute(
                    """
                    INSERT INTO learner_model.presentation_preference_changes (
                        learner_id, revision, change, occurred_at,
                        resulting_profile_digest
                    ) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        profile.learner_id,
                        change.revision,
                        Jsonb(change_document),
                        change.occurred_at,
                        change.resulting_profile_digest,
                    ),
                )
                connection.execute(
                    """
                    DELETE FROM learner_model.presentation_preference_changes
                    WHERE learner_id = %s AND revision IN (
                        SELECT revision
                        FROM learner_model.presentation_preference_changes
                        WHERE learner_id = %s
                        ORDER BY revision DESC OFFSET 100
                    )
                    """,
                    (profile.learner_id, profile.learner_id),
                )
                if self._before_presentation_preference_save is not None:
                    self._before_presentation_preference_save()
                connection.execute(
                    """
                    INSERT INTO learner_model.presentation_preference_mutations (
                        learner_id, idempotency_key, request_fingerprint,
                        accepted_profile, accepted_revision
                    ) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        profile.learner_id,
                        idempotency_key,
                        request_fingerprint,
                        Jsonb(profile_document),
                        profile.revision,
                    ),
                )
        return profile

    def _preferences(self) -> LearnerPreferenceContract:
        if self._preference_contract is None:
            raise RuntimeError("Learner preference contract is unavailable.")
        return self._preference_contract

    def _presentation_preferences(self) -> PresentationPreferenceContract:
        if self._presentation_preference_contract is None:
            raise RuntimeError("Presentation preference contract is unavailable.")
        return self._presentation_preference_contract

    @staticmethod
    def _json_bytes(value: object) -> bytes:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")

    def _parse_profile(
        self, contract: LearnerPreferenceContract, value: object
    ) -> LearnerPreferenceProfile:
        return contract.parse_profile(self._json_bytes(value))

    def _parse_presentation_profile(
        self, contract: PresentationPreferenceContract, value: object
    ) -> PresentationPreferenceProfile:
        return contract.parse_profile(self._json_bytes(value))
