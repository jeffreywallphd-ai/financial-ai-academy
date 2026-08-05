"""PostgreSQL Identity binding and session repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row

from ..domain.models import IdentityBinding, SessionRecord
from ..ports.repositories import IdentityModeMismatch, SingleProfileCandidate


class PostgresIdentityRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def ensure_single_profile(
        self, candidate: SingleProfileCandidate
    ) -> IdentityBinding:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            installation = connection.execute(
                """
                SELECT installation_id, mode
                FROM identity.installations
                WHERE singleton_key = true
                FOR UPDATE
                """
            ).fetchone()
            if installation is None:
                installation = connection.execute(
                    """
                    INSERT INTO identity.installations (
                        singleton_key,
                        installation_id,
                        mode,
                        limitation_acknowledged,
                        created_at
                    )
                    VALUES (true, %s, 'single_profile', true, %s)
                    RETURNING installation_id, mode
                    """,
                    (candidate.installation_id, candidate.created_at),
                ).fetchone()
            if installation is None:
                raise RuntimeError("Installation did not become visible.")
            if str(installation["mode"]) != "single_profile":
                raise IdentityModeMismatch
            installation_id = str(installation["installation_id"])
            binding = connection.execute(
                """
                SELECT
                    installation_id,
                    binding_id,
                    actor_id,
                    learner_id,
                    provider_mode
                FROM identity.bindings
                WHERE installation_id = %s
                  AND provider_mode = 'single_profile'
                  AND provider_subject = 'local-primary'
                """,
                (installation_id,),
            ).fetchone()
            if binding is None:
                binding = connection.execute(
                    """
                    INSERT INTO identity.bindings (
                        binding_id,
                        installation_id,
                        actor_id,
                        learner_id,
                        provider_mode,
                        provider_subject,
                        status,
                        created_at
                    )
                    VALUES (
                        %s, %s, %s, %s,
                        'single_profile',
                        'local-primary',
                        'active',
                        %s
                    )
                    RETURNING
                        installation_id,
                        binding_id,
                        actor_id,
                        learner_id,
                        provider_mode
                    """,
                    (
                        candidate.binding_id,
                        installation_id,
                        candidate.actor_id,
                        candidate.learner_id,
                        candidate.created_at,
                    ),
                ).fetchone()
        if binding is None:
            raise RuntimeError("Identity binding did not become visible.")
        return self._binding(binding)

    def revoke_binding_sessions(
        self, binding_id: str, revoked_at: datetime
    ) -> None:
        with psycopg.connect(self._dsn) as connection:
            connection.execute(
                """
                UPDATE identity.sessions
                SET revoked_at = %s
                WHERE binding_id = %s AND revoked_at IS NULL
                """,
                (revoked_at, binding_id),
            )

    def create_session(self, session: SessionRecord) -> None:
        with psycopg.connect(self._dsn) as connection:
            connection.execute(
                """
                INSERT INTO identity.sessions (
                    session_id,
                    binding_id,
                    token_hash,
                    authenticated_at,
                    last_seen_at,
                    absolute_expires_at,
                    revoked_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, NULL)
                """,
                (
                    session.session_id,
                    session.binding.binding_id,
                    session.token_hash,
                    session.authenticated_at,
                    session.last_seen_at,
                    session.absolute_expires_at,
                ),
            )

    def resolve_active_session(
        self,
        token_hash: str,
        now: datetime,
        idle_cutoff: datetime,
    ) -> SessionRecord | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                UPDATE identity.sessions AS session
                SET last_seen_at = %s
                FROM identity.bindings AS binding
                WHERE session.binding_id = binding.binding_id
                  AND session.token_hash = %s
                  AND session.revoked_at IS NULL
                  AND session.absolute_expires_at > %s
                  AND session.last_seen_at > %s
                  AND binding.status = 'active'
                RETURNING
                    session.session_id,
                    session.token_hash,
                    session.authenticated_at,
                    session.last_seen_at,
                    session.absolute_expires_at,
                    session.revoked_at,
                    binding.installation_id,
                    binding.binding_id,
                    binding.actor_id,
                    binding.learner_id,
                    binding.provider_mode
                """,
                (now, token_hash, now, idle_cutoff),
            ).fetchone()
        return self._session(row) if row else None

    def revoke_session(
        self, token_hash: str, revoked_at: datetime
    ) -> None:
        with psycopg.connect(self._dsn) as connection:
            connection.execute(
                """
                UPDATE identity.sessions
                SET revoked_at = %s
                WHERE token_hash = %s AND revoked_at IS NULL
                """,
                (revoked_at, token_hash),
            )

    def health(self) -> bool:
        with psycopg.connect(self._dsn) as connection:
            row = connection.execute("SELECT 1").fetchone()
        return row == (1,)

    @staticmethod
    def _binding(row: dict[str, Any]) -> IdentityBinding:
        return IdentityBinding(
            installation_id=str(row["installation_id"]),
            binding_id=str(row["binding_id"]),
            actor_id=str(row["actor_id"]),
            learner_id=str(row["learner_id"]),
            mode=str(row["provider_mode"]),
        )

    @classmethod
    def _session(cls, row: dict[str, Any]) -> SessionRecord:
        return SessionRecord(
            session_id=str(row["session_id"]),
            binding=cls._binding(row),
            token_hash=str(row["token_hash"]),
            authenticated_at=row["authenticated_at"],
            last_seen_at=row["last_seen_at"],
            absolute_expires_at=row["absolute_expires_at"],
            revoked_at=row["revoked_at"],
        )
