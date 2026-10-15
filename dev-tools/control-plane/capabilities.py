"""Reusable capability grants for repository-local command and path effects."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any

from contracts import ControlError
from store import canonical_bytes


SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
EFFECTS = {"subprocess", "read", "write-generated", "maintenance-action"}


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def normalize_path(value: str) -> str:
    posix = PurePosixPath(value.replace("\\", "/"))
    if posix.is_absolute() or not posix.parts or ".." in posix.parts or re.match(r"^[A-Za-z]:", value):
        raise ControlError("capability.path-invalid", "Capability paths must be normalized repository-relative paths.", {"path": value}, ["Use an exact repository-relative path from the authorized plan."])
    return posix.as_posix()


def parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ControlError("capability.expiry-invalid", "Capability expiry must be an ISO UTC timestamp.", {}, ["Issue a new grant with a valid UTC expiry."]) from error
    if parsed.tzinfo is None:
        raise ControlError("capability.expiry-invalid", "Capability expiry must include a timezone.", {}, ["Issue a new grant with a UTC expiry ending in Z."])
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class CapabilityGrant:
    subject: str
    command_ids: tuple[str, ...]
    path_scopes: tuple[str, ...]
    effects: tuple[str, ...]
    expires_at: str | None = None

    def __post_init__(self) -> None:
        if not SAFE_ID.fullmatch(self.subject):
            raise ValueError("unsafe capability subject")
        if not self.command_ids or any(not SAFE_ID.fullmatch(value) for value in self.command_ids):
            raise ValueError("capability commands must be non-empty stable IDs")
        if not self.effects or any(value not in EFFECTS for value in self.effects):
            raise ValueError("unsupported capability effect")
        normalized = tuple(sorted(set(normalize_path(value) for value in self.path_scopes)))
        commands = tuple(sorted(set(self.command_ids)))
        effects = tuple(sorted(set(self.effects)))
        object.__setattr__(self, "path_scopes", normalized)
        object.__setattr__(self, "command_ids", commands)
        object.__setattr__(self, "effects", effects)
        if self.expires_at:
            parse_time(self.expires_at)

    def contract(self) -> dict[str, Any]:
        return {
            "schema_version": "capability-grant-v1",
            "subject": self.subject,
            "command_ids": list(self.command_ids),
            "path_scopes": list(self.path_scopes),
            "effects": list(self.effects),
            "expires_at": self.expires_at,
        }

    @property
    def grant_digest(self) -> str:
        return digest(self.contract())

    def authorize(self, *, command_id: str, effect: str, paths: list[str], now: datetime | None = None) -> None:
        if self.expires_at and parse_time(self.expires_at) <= (now or datetime.now(timezone.utc)):
            raise ControlError("capability.expired", "The execution capability has expired.", {"subject": self.subject}, ["Regenerate the affected plan and its short-lived grant."])
        if effect not in self.effects:
            raise ControlError("capability.effect-denied", "The requested effect is outside the capability grant.", {"effect": effect}, ["Use the effect explicitly authorized by the selected operation."])
        if command_id not in self.command_ids:
            raise ControlError("capability.command-denied", "The command ID is outside the capability grant.", {"command_id": command_id}, ["Regenerate the plan from the tracked command catalog."])
        normalized = [normalize_path(value) for value in paths]
        escaped = [value for value in normalized if not any(value == scope or value.startswith(scope.rstrip("/") + "/") for scope in self.path_scopes)]
        if escaped:
            raise ControlError("capability.path-denied", "One or more paths are outside the capability grant.", {"path_count": len(escaped)}, ["Regenerate the grant from the exact authorized path set."])
