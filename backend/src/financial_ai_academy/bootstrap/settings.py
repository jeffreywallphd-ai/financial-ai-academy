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

    @property
    def assessment_schema_dir(self) -> Path:
        """Return the Assessment v1 schema beside the lesson-package schema."""
        return self.lesson_schema_dir.parents[1] / "assessment" / "v1"

    @property
    def practice_schema_dir(self) -> Path:
        """Return the Assessment practice v1 schema directory."""
        return self.lesson_schema_dir.parents[1] / "assessment" / "practice" / "v1"

    @property
    def assessment_event_schema_dir(self) -> Path:
        """Return the Assessment v1 event schema from the contract root."""
        return (
            self.lesson_schema_dir.parents[2]
            / "events"
            / "assessment"
            / "v1"
        )

    @property
    def project_schema_dir(self) -> Path:
        """Return the Project workspace v1 schema directory."""
        return self.lesson_schema_dir.parents[1] / "project" / "v1"

    @property
    def assessment_project_schema_dir(self) -> Path:
        """Return the Assessment Project-submission v1 schema directory."""
        return (
            self.lesson_schema_dir.parents[1]
            / "assessment"
            / "project"
            / "v1"
        )

    def validate(self) -> SingleProfileRequestPolicy:
        if not self.postgres_dsn.startswith(
            ("postgresql://", "postgres://")
        ):
            raise ValueError("A PostgreSQL DSN is required.")
        if not self.lesson_schema_dir.is_dir():
            raise ValueError("Lesson schema directory is unavailable.")
        if not self.assessment_schema_dir.is_dir():
            raise ValueError("Assessment schema directory is unavailable.")
        if not self.practice_schema_dir.is_dir():
            raise ValueError("Practice schema directory is unavailable.")
        if not self.assessment_event_schema_dir.is_dir():
            raise ValueError("Assessment event schema directory is unavailable.")
        if not self.project_schema_dir.is_dir():
            raise ValueError("Project schema directory is unavailable.")
        if not self.assessment_project_schema_dir.is_dir():
            raise ValueError(
                "Assessment Project-submission schema directory is unavailable."
            )
        if not self.migrations_dir.is_dir():
            raise ValueError("Migration directory is unavailable.")
        return SingleProfileRequestPolicy(self.security)
