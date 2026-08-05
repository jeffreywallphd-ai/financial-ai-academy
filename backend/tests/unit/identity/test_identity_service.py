from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from financial_ai_academy.modules.identity.application.service import IdentityService
from financial_ai_academy.modules.identity.domain.models import (
    IdentityBinding,
    SessionRecord,
)
from financial_ai_academy.modules.identity.ports.repositories import (
    IdentityModeMismatch,
    SingleProfileCandidate,
)
from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    SingleProfileBootstrapRequest,
)


TOKEN_ONE = "a" * 43
TOKEN_TWO = "b" * 43


class MutableClock:
    def __init__(self) -> None:
        self.value = datetime(2026, 8, 5, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.value


class MemoryIdentityRepository:
    def __init__(self) -> None:
        self.binding: IdentityBinding | None = None
        self.sessions: dict[str, SessionRecord] = {}
        self.persisted_mode = "single_profile"
        self.available = True

    def ensure_single_profile(
        self, candidate: SingleProfileCandidate
    ) -> IdentityBinding:
        if not self.available:
            raise RuntimeError("private database detail")
        if self.persisted_mode != "single_profile":
            raise IdentityModeMismatch
        if self.binding is None:
            self.binding = IdentityBinding(
                installation_id=candidate.installation_id,
                binding_id=candidate.binding_id,
                actor_id=candidate.actor_id,
                learner_id=candidate.learner_id,
                mode="single_profile",
            )
        return self.binding

    def revoke_binding_sessions(
        self, binding_id: str, revoked_at: datetime
    ) -> None:
        for token_hash, session in tuple(self.sessions.items()):
            if session.binding.binding_id == binding_id and session.revoked_at is None:
                self.sessions[token_hash] = replace(
                    session, revoked_at=revoked_at
                )

    def create_session(self, session: SessionRecord) -> None:
        self.sessions[session.token_hash] = session

    def resolve_active_session(
        self,
        token_hash: str,
        now: datetime,
        idle_cutoff: datetime,
    ) -> SessionRecord | None:
        session = self.sessions.get(token_hash)
        if (
            session is None
            or session.revoked_at is not None
            or session.absolute_expires_at <= now
            or session.last_seen_at <= idle_cutoff
        ):
            return None
        updated = replace(session, last_seen_at=now)
        self.sessions[token_hash] = updated
        return updated

    def revoke_session(
        self, token_hash: str, revoked_at: datetime
    ) -> None:
        session = self.sessions.get(token_hash)
        if session is not None and session.revoked_at is None:
            self.sessions[token_hash] = replace(
                session, revoked_at=revoked_at
            )

    def health(self) -> bool:
        return self.available


def service_with(
    repository: MemoryIdentityRepository,
    clock: MutableClock,
    tokens: list[str] | None = None,
) -> IdentityService:
    token_values = iter(tokens or [TOKEN_ONE])
    identifiers = iter(f"opaque-{number}" for number in range(20))
    return IdentityService(
        repository,
        configured_mode="single_profile",
        clock=clock,
        token_factory=lambda: next(token_values),
        identifier_factory=lambda: next(identifiers),
    )


def test_bootstrap_requires_explicit_limitation_acknowledgement() -> None:
    service = service_with(MemoryIdentityRepository(), MutableClock())

    with pytest.raises(IdentityError) as captured:
        service.bootstrap_single_profile(
            SingleProfileBootstrapRequest(False)
        )

    assert captured.value.code is IdentityErrorCode.FORBIDDEN


def test_bootstrap_persists_stable_binding_and_rotates_sessions() -> None:
    repository = MemoryIdentityRepository()
    clock = MutableClock()
    service = service_with(repository, clock, [TOKEN_ONE, TOKEN_TWO])

    first = service.bootstrap_single_profile(
        SingleProfileBootstrapRequest(True)
    )
    clock.value += timedelta(minutes=1)
    second = service.bootstrap_single_profile(
        SingleProfileBootstrapRequest(True)
    )

    assert first.context.actor_id == second.context.actor_id
    assert first.context.learner_id == second.context.learner_id
    assert first.context.session_id != second.context.session_id
    assert second.context.authentication_method == "single_profile"
    assert second.context.permissions == ("curriculum.lesson.read",)
    assert all(
        TOKEN_ONE not in session.token_hash
        and TOKEN_TWO not in session.token_hash
        for session in repository.sessions.values()
    )
    with pytest.raises(IdentityError) as captured:
        service.resolve_session(TOKEN_ONE)
    assert captured.value.code is IdentityErrorCode.UNAUTHORIZED
    assert service.resolve_session(TOKEN_TWO) == second.context


@pytest.mark.parametrize(
    "cookie_value",
    [None, "", "short", "x" * 43, TOKEN_ONE + "!"],
)
def test_missing_malformed_or_tampered_cookie_fails_closed(
    cookie_value: str | None,
) -> None:
    service = service_with(MemoryIdentityRepository(), MutableClock())

    with pytest.raises(IdentityError) as captured:
        service.resolve_session(cookie_value)

    assert captured.value.code is IdentityErrorCode.UNAUTHORIZED
    if cookie_value:
        assert cookie_value not in captured.value.safe_message


def test_idle_expired_absolute_expired_and_revoked_sessions_fail_closed() -> None:
    repository = MemoryIdentityRepository()
    clock = MutableClock()
    service = service_with(repository, clock, [TOKEN_ONE])
    service.bootstrap_single_profile(SingleProfileBootstrapRequest(True))

    clock.value += timedelta(minutes=31)
    with pytest.raises(IdentityError) as idle:
        service.resolve_session(TOKEN_ONE)
    assert idle.value.code is IdentityErrorCode.UNAUTHORIZED

    clock.value = datetime(2026, 8, 5, tzinfo=timezone.utc)
    second_service = service_with(repository, clock, [TOKEN_TWO])
    second_service.bootstrap_single_profile(
        SingleProfileBootstrapRequest(True)
    )
    second_service.revoke_session(TOKEN_TWO)
    with pytest.raises(IdentityError) as revoked:
        second_service.resolve_session(TOKEN_TWO)
    assert revoked.value.code is IdentityErrorCode.UNAUTHORIZED


def test_persisted_mode_mismatch_fails_without_session() -> None:
    repository = MemoryIdentityRepository()
    repository.persisted_mode = "oidc"
    service = service_with(repository, MutableClock())

    with pytest.raises(IdentityError) as captured:
        service.bootstrap_single_profile(
            SingleProfileBootstrapRequest(True)
        )

    assert captured.value.code is IdentityErrorCode.MODE_MISMATCH
    assert repository.sessions == {}


def test_storage_failure_is_redacted() -> None:
    repository = MemoryIdentityRepository()
    repository.available = False
    service = service_with(repository, MutableClock())

    with pytest.raises(IdentityError) as captured:
        service.bootstrap_single_profile(
            SingleProfileBootstrapRequest(True)
        )

    assert captured.value.code is IdentityErrorCode.UNAVAILABLE
    assert "private database detail" not in captured.value.safe_message
