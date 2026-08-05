"""Loopback-only request and cookie policy for single-profile mode."""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlsplit


class RequestPolicyViolation(RuntimeError):
    def __init__(self, safe_message: str) -> None:
        super().__init__(safe_message)
        self.safe_message = safe_message


@dataclass(frozen=True, slots=True)
class SingleProfileSecuritySettings:
    identity_mode: str
    bind_host: str
    public_origin: str
    allowed_hosts: tuple[str, ...]
    secure_cookie: bool
    cookie_name: str = "financial_ai_academy_session"
    absolute_session_seconds: int = 8 * 60 * 60


class SingleProfileRequestPolicy:
    _CLIENT_IDENTITY_HEADERS = {
        "x-actor-id",
        "x-learner-id",
        "x-session-id",
        "x-identity-provider",
    }

    def __init__(self, settings: SingleProfileSecuritySettings) -> None:
        if settings.identity_mode != "single_profile":
            raise RequestPolicyViolation(
                "Only single-profile identity is available in this build."
            )
        if not self._is_loopback_host(settings.bind_host):
            raise RequestPolicyViolation(
                "Single-profile mode must bind to a loopback host."
            )
        parsed = urlsplit(settings.public_origin)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
            or not self._is_loopback_host(parsed.hostname)
        ):
            raise RequestPolicyViolation(
                "Single-profile public origin must be an exact loopback origin."
            )
        if parsed.scheme == "http" and settings.secure_cookie:
            raise RequestPolicyViolation(
                "Loopback HTTP development cannot issue a Secure cookie."
            )
        if parsed.scheme == "https" and not settings.secure_cookie:
            raise RequestPolicyViolation(
                "HTTPS operation requires a Secure cookie."
            )
        if (
            not settings.cookie_name
            or any(character.isspace() for character in settings.cookie_name)
            or settings.absolute_session_seconds <= 0
        ):
            raise RequestPolicyViolation(
                "Session cookie configuration is invalid."
            )
        allowed_hosts = tuple(
            self._normalize_host(value) for value in settings.allowed_hosts
        )
        if not allowed_hosts or any(not value for value in allowed_hosts):
            raise RequestPolicyViolation("At least one allowed Host is required.")
        self.settings = settings
        self._origin = settings.public_origin.rstrip("/")
        self._allowed_hosts = frozenset(allowed_hosts)

    def verify(
        self,
        headers: Mapping[str, str],
        *,
        state_changing: bool,
    ) -> None:
        normalized = {
            str(key).casefold(): str(value) for key, value in headers.items()
        }
        if self._CLIENT_IDENTITY_HEADERS.intersection(normalized):
            raise RequestPolicyViolation(
                "Client-selected identity context is prohibited."
            )
        host = self._normalize_host(normalized.get("host", ""))
        if host not in self._allowed_hosts:
            raise RequestPolicyViolation("Request Host is not allowed.")
        if state_changing:
            origin = normalized.get("origin", "").rstrip("/")
            if origin != self._origin:
                raise RequestPolicyViolation(
                    "State-changing requests require the configured Origin."
                )
            fetch_site = normalized.get("sec-fetch-site")
            if fetch_site is not None and fetch_site != "same-origin":
                raise RequestPolicyViolation(
                    "Cross-site state-changing requests are prohibited."
                )

    @staticmethod
    def _normalize_host(value: str) -> str:
        return value.strip().casefold().rstrip(".")

    @staticmethod
    def _is_loopback_host(value: str) -> bool:
        normalized = value.strip().strip("[]").casefold()
        if normalized == "localhost":
            return True
        try:
            return ipaddress.ip_address(normalized).is_loopback
        except ValueError:
            return False
