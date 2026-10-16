"""Stable transport-neutral Project workspace operations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from .domain.project import (
    IndependentProjectOrigin,
    LearningProjectBrief,
    LearningProjectOrigin,
    ProjectCreateIntent,
    ProjectOrigin,
    ProjectShell,
)


class ProjectErrorCode(StrEnum):
    INVALID_REQUEST = "invalid_request"
    IMMUTABLE_CONFLICT = "immutable_conflict"
    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"


class ProjectError(RuntimeError):
    """Bounded Project error without persistence or provider details."""

    def __init__(
        self,
        code: ProjectErrorCode,
        message: str,
        *,
        reference: str = "project",
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code.value,
            "message": self.message,
            "reference": self.reference,
        }


@dataclass(frozen=True, slots=True)
class CreateProjectRequest:
    learner_id: str
    intent: ProjectCreateIntent


@dataclass(frozen=True, slots=True)
class ListProjectsRequest:
    learner_id: str


@dataclass(frozen=True, slots=True)
class OpenProjectRequest:
    learner_id: str
    project_id: str


class ProjectOperations(Protocol):
    def create_project(self, request: CreateProjectRequest) -> ProjectShell: ...

    def list_projects(
        self, request: ListProjectsRequest
    ) -> tuple[ProjectShell, ...]: ...

    def open_project(self, request: OpenProjectRequest) -> ProjectShell: ...


__all__ = [
    "CreateProjectRequest",
    "IndependentProjectOrigin",
    "LearningProjectBrief",
    "LearningProjectOrigin",
    "ListProjectsRequest",
    "OpenProjectRequest",
    "ProjectCreateIntent",
    "ProjectError",
    "ProjectErrorCode",
    "ProjectOperations",
    "ProjectOrigin",
    "ProjectShell",
]
