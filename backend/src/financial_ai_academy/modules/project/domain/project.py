"""Immutable Project shell, origin, and learning-brief values."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, TypeAlias


@dataclass(frozen=True, slots=True)
class ProjectMilestone:
    milestone_id: str
    description: str


@dataclass(frozen=True, slots=True)
class ProjectSourceReference:
    resource_id: str
    resource_version: str
    resource_digest: str
    title: str


@dataclass(frozen=True, slots=True)
class LearningProjectBrief:
    schema_version: str
    brief_id: str
    brief_version: str
    brief_digest: str
    title: str
    purpose: str
    milestones: tuple[ProjectMilestone, ...]
    source_references: tuple[ProjectSourceReference, ...]


@dataclass(frozen=True, slots=True)
class IndependentProjectOrigin:
    origin_type: Literal["independent"] = "independent"


@dataclass(frozen=True, slots=True)
class LearningProjectOrigin:
    project_brief_schema_version: str
    package_id: str
    package_version: str
    package_digest: str
    brief_id: str
    brief_version: str
    brief_digest: str
    curriculum_id: str
    curriculum_version: str
    curriculum_digest: str
    placement_id: str
    placement_version: str
    placement_digest: str
    brief_title: str
    brief_purpose: str
    origin_type: Literal["learning"] = "learning"


ProjectOrigin: TypeAlias = IndependentProjectOrigin | LearningProjectOrigin


@dataclass(frozen=True, slots=True)
class ProjectCreateIntent:
    schema_version: str
    idempotency_key: str
    title: str
    charter: str
    origin: ProjectOrigin


@dataclass(frozen=True, slots=True)
class ProjectShell:
    schema_version: str
    project_id: str
    learner_id: str
    title: str
    charter: str
    origin: ProjectOrigin
    lifecycle: Literal["active"]
    revision: int
    created_at: datetime
    updated_at: datetime
