"""Provider-neutral Identity application contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol


class IdentityErrorCode(StrEnum):
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    UNSAFE_CONFIGURATION = "unsafe_configuration"
    MODE_MISMATCH = "identity_mode_mismatch"
    UNAVAILABLE = "unavailable"


class IdentityError(RuntimeError):
    def __init__(self, code: IdentityErrorCode, safe_message: str) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message


@dataclass(frozen=True, slots=True)
class LearnerContext:
    actor_id: str
    learner_id: str
    session_id: str
    authenticated_at: datetime
    expires_at: datetime
    authentication_method: str
    permissions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SingleProfileBootstrapRequest:
    limitation_acknowledged: bool


@dataclass(frozen=True, slots=True)
class IssuedSession:
    context: LearnerContext
    cookie_value: str


class IdentityOperations(Protocol):
    def bootstrap_single_profile(
        self, request: SingleProfileBootstrapRequest
    ) -> IssuedSession: ...

    def resolve_session(self, cookie_value: str | None) -> LearnerContext: ...

    def revoke_session(self, cookie_value: str | None) -> None: ...

    def health(self) -> bool: ...
