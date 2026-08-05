"""Validated settings for the private-host single-profile slice."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)


@dataclass(frozen=True, slots=True)
class SingleProfileApplicationSettings:
    postgres_dsn: str
    object_storage_root: Path
    lesson_schema_dir: Path
    migrations_dir: Path
    security: SingleProfileSecuritySettings

    def validate(self) -> SingleProfileRequestPolicy:
        if not self.postgres_dsn.startswith(
            ("postgresql://", "postgres://")
        ):
            raise ValueError("A PostgreSQL DSN is required.")
        if not self.lesson_schema_dir.is_dir():
            raise ValueError("Lesson schema directory is unavailable.")
        if not self.migrations_dir.is_dir():
            raise ValueError("Migration directory is unavailable.")
        return SingleProfileRequestPolicy(self.security)
