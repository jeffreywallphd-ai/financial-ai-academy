"""Single-profile binding and opaque server-side session lifecycle."""

from __future__ import annotations

import hashlib
import re
import secrets
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from ..domain.models import SessionRecord
from ..ports.repositories import (
    IdentityModeMismatch,
    IdentityRepositoryPort,
    SingleProfileCandidate,
)
from ..public import (
    IdentityError,
    IdentityErrorCode,
    IssuedSession,
    LearnerContext,
    SingleProfileBootstrapRequest,
)


_COOKIE_TOKEN = re.compile(r"^[A-Za-z0-9_-]{40,128}$")
_READ_PERMISSION = "curriculum.lesson.read"


class IdentityService:
    def __init__(
        self,
        repository: IdentityRepositoryPort,
        *,
        configured_mode: str,
        idle_ttl: timedelta = timedelta(minutes=30),
        absolute_ttl: timedelta = timedelta(hours=8),
        clock: Callable[[], datetime] | None = None,
        token_factory: Callable[[], str] | None = None,
        identifier_factory: Callable[[], str] | None = None,
    ) -> None:
        if configured_mode != "single_profile":
            raise IdentityError(
                IdentityErrorCode.UNSAFE_CONFIGURATION,
                "The configured identity mode is not available in this build.",
            )
        if idle_ttl <= timedelta(0) or absolute_ttl <= idle_ttl:
            raise IdentityError(
                IdentityErrorCode.UNSAFE_CONFIGURATION,
                "Session lifetime configuration is invalid.",
            )
        self._repository = repository
        self._idle_ttl = idle_ttl
        self._absolute_ttl = absolute_ttl
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._token_factory = token_factory or (
            lambda: secrets.token_urlsafe(32)
        )
        self._identifier_factory = identifier_factory or (
            lambda: str(uuid4())
        )

    def bootstrap_single_profile(
        self, request: SingleProfileBootstrapRequest
    ) -> IssuedSession:
        if request.limitation_acknowledged is not True:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "Single-profile limitations must be acknowledged.",
            )
        now = self._utc_now()
        candidate = SingleProfileCandidate(
            installation_id=self._identifier_factory(),
            binding_id=self._identifier_factory(),
            actor_id=self._identifier_factory(),
            learner_id=self._identifier_factory(),
            created_at=now,
        )
        try:
            binding = self._repository.ensure_single_profile(candidate)
            self._repository.revoke_binding_sessions(binding.binding_id, now)
            cookie_value = self._token_factory()
            if not _COOKIE_TOKEN.fullmatch(cookie_value):
                raise IdentityError(
                    IdentityErrorCode.UNAVAILABLE,
                    "A secure session could not be issued.",
                )
            session = SessionRecord(
                session_id=self._identifier_factory(),
                binding=binding,
                token_hash=self._token_hash(cookie_value),
                authenticated_at=now,
                last_seen_at=now,
                absolute_expires_at=now + self._absolute_ttl,
                revoked_at=None,
            )
            self._repository.create_session(session)
        except IdentityModeMismatch as error:
            raise IdentityError(
                IdentityErrorCode.MODE_MISMATCH,
                "The persisted identity mode does not match configuration.",
            ) from error
        except IdentityError:
            raise
        except Exception as error:
            raise IdentityError(
                IdentityErrorCode.UNAVAILABLE,
                "Identity storage is unavailable.",
            ) from error
        return IssuedSession(
            context=self._context(session),
            cookie_value=cookie_value,
        )

    def resolve_session(self, cookie_value: str | None) -> LearnerContext:
        if not cookie_value or not _COOKIE_TOKEN.fullmatch(cookie_value):
            raise self._unauthorized()
        now = self._utc_now()
        try:
            session = self._repository.resolve_active_session(
                self._token_hash(cookie_value),
                now,
                now - self._idle_ttl,
            )
        except Exception as error:
            raise IdentityError(
                IdentityErrorCode.UNAVAILABLE,
                "Identity storage is unavailable.",
            ) from error
        if session is None:
            raise self._unauthorized()
        return self._context(session)

    def revoke_session(self, cookie_value: str | None) -> None:
        if not cookie_value or not _COOKIE_TOKEN.fullmatch(cookie_value):
            return
        try:
            self._repository.revoke_session(
                self._token_hash(cookie_value), self._utc_now()
            )
        except Exception as error:
            raise IdentityError(
                IdentityErrorCode.UNAVAILABLE,
                "Identity storage is unavailable.",
            ) from error

    def health(self) -> bool:
        try:
            return self._repository.health()
        except Exception:
            return False

    @staticmethod
    def _token_hash(cookie_value: str) -> str:
        return hashlib.sha256(cookie_value.encode("utf-8")).hexdigest()

    @staticmethod
    def _context(session: SessionRecord) -> LearnerContext:
        return LearnerContext(
            actor_id=session.binding.actor_id,
            learner_id=session.binding.learner_id,
            session_id=session.session_id,
            authenticated_at=session.authenticated_at,
            expires_at=session.absolute_expires_at,
            authentication_method="single_profile",
            permissions=(_READ_PERMISSION,),
        )

    def _utc_now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise IdentityError(
                IdentityErrorCode.UNSAFE_CONFIGURATION,
                "Identity clock must be timezone-aware.",
            )
        return value.astimezone(timezone.utc)

    @staticmethod
    def _unauthorized() -> IdentityError:
        return IdentityError(
            IdentityErrorCode.UNAUTHORIZED,
            "A valid learner session is required.",
        )
