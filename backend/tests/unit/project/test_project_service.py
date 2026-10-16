from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from financial_ai_academy.modules.curriculum.public import ProjectBriefPlacement
from financial_ai_academy.modules.project.adapters.project_contract import (
    ContractProjectAdapter,
)
from financial_ai_academy.modules.project.application.service import ProjectService
from financial_ai_academy.modules.project.domain.project import (
    IndependentProjectOrigin,
    LearningProjectOrigin,
    ProjectCreateIntent,
    ProjectShell,
)
from financial_ai_academy.modules.project.ports.repositories import (
    ProjectIdempotencyConflict,
)
from financial_ai_academy.modules.project.public import (
    CreateProjectRequest,
    ListProjectsRequest,
    OpenProjectRequest,
    ProjectError,
    ProjectErrorCode,
)


ROOT = Path(__file__).resolve().parents[4]
SCHEMAS = ROOT / "contracts/learning/project/v1"
BRIEF = (
    ROOT
    / "contracts/compatibility/lesson-package/v1/approved"
    / "intro-risk-return-project/projects/project-1.json"
)
NOW = datetime(2026, 10, 16, 12, 30, tzinfo=timezone.utc)


class MemoryRepository:
    def __init__(self) -> None:
        self.rows: dict[str, tuple[str, str, ProjectShell]] = {}

    def get_by_idempotency(
        self, learner_id: str, idempotency_key: str
    ) -> tuple[str, ProjectShell] | None:
        value = self.rows.get(f"{learner_id}:{idempotency_key}")
        return (value[0], value[2]) if value else None

    def create_if_absent(
        self,
        *,
        idempotency_key: str,
        request_fingerprint: str,
        shell: ProjectShell,
    ) -> tuple[ProjectShell, bool]:
        key = f"{shell.learner_id}:{idempotency_key}"
        existing = self.rows.get(key)
        if existing is not None:
            fingerprint, _project_id, stored = existing
            if fingerprint != request_fingerprint:
                raise ProjectIdempotencyConflict
            return stored, False
        self.rows[key] = (request_fingerprint, shell.project_id, shell)
        return shell, True

    def get_for_learner(
        self, learner_id: str, project_id: str
    ) -> ProjectShell | None:
        return next(
            (
                shell
                for _fingerprint, _identity, shell in self.rows.values()
                if shell.learner_id == learner_id
                and shell.project_id == project_id
            ),
            None,
        )

    def list_for_learner(self, learner_id: str) -> tuple[ProjectShell, ...]:
        return tuple(
            sorted(
                (
                    shell
                    for _fingerprint, _identity, shell in self.rows.values()
                    if shell.learner_id == learner_id
                ),
                key=lambda shell: (shell.created_at, shell.project_id),
            )
        )


class Clock:
    def now(self) -> datetime:
        return NOW


class Identifiers:
    def __init__(self) -> None:
        self.value = 0

    def new(self) -> str:
        self.value += 1
        return f"project-{self.value:04d}"


class Briefs:
    def __init__(self, brief: object) -> None:
        self.brief = brief
        self.calls = 0

    def resolve(self, _origin: object) -> object:
        self.calls += 1
        return self.brief


class Placements:
    def __init__(self, placement: ProjectBriefPlacement) -> None:
        self.placement = placement
        self.calls = 0

    def resolve(self, _placement_id: str) -> ProjectBriefPlacement:
        self.calls += 1
        return self.placement


def learning_setup() -> tuple[object, ProjectBriefPlacement, LearningProjectOrigin]:
    brief = ContractProjectAdapter(SCHEMAS).parse_brief(BRIEF.read_bytes())
    placement = ProjectBriefPlacement(
        placement_id="risk-return-project-primary",
        placement_version="1.0.0",
        placement_digest="b" * 64,
        curriculum_id="financial-foundations",
        curriculum_version="1.0.0",
        curriculum_digest="c" * 64,
        package_id="intro-risk-return-project",
        package_version="1.0.0",
        package_digest="d" * 64,
        brief_id=brief.brief_id,
        brief_version=brief.brief_version,
        brief_digest=brief.brief_digest,
        project_brief_schema_version=brief.schema_version,
        created_at=NOW,
    )
    origin = LearningProjectOrigin(
        project_brief_schema_version=brief.schema_version,
        package_id=placement.package_id,
        package_version=placement.package_version,
        package_digest=placement.package_digest,
        brief_id=brief.brief_id,
        brief_version=brief.brief_version,
        brief_digest=brief.brief_digest,
        curriculum_id=placement.curriculum_id,
        curriculum_version=placement.curriculum_version,
        curriculum_digest=placement.curriculum_digest,
        placement_id=placement.placement_id,
        placement_version=placement.placement_version,
        placement_digest=placement.placement_digest,
        brief_title=brief.title,
        brief_purpose=brief.purpose,
    )
    return brief, placement, origin


def build_service() -> tuple[ProjectService, MemoryRepository, Briefs, Placements]:
    brief, placement, _origin = learning_setup()
    repository = MemoryRepository()
    briefs = Briefs(brief)
    placements = Placements(placement)
    return (
        ProjectService(
            repository,
            ContractProjectAdapter(SCHEMAS),
            briefs,  # type: ignore[arg-type]
            placements,
            Clock(),
            Identifiers(),
        ),
        repository,
        briefs,
        placements,
    )


@pytest.mark.parametrize(
    ("title", "charter"),
    [
        ("A", "One clear outcome."),
        ("Unicode café", "Compare evidence across several valid sources."),
        ("T" * 120, "C" * 4000),
    ],
)
def test_independent_create_retry_read_and_list_allow_varied_valid_meaning(
    title: str, charter: str
) -> None:
    service, _repository, briefs, placements = build_service()
    intent = ProjectCreateIntent(
        schema_version="1.0.0",
        idempotency_key="independent-1",
        title=title,
        charter=charter,
        origin=IndependentProjectOrigin(),
    )

    created = service.create_project(CreateProjectRequest("learner-1", intent))
    replay = service.create_project(CreateProjectRequest("learner-1", intent))

    assert replay == created
    assert service.open_project(
        OpenProjectRequest("learner-1", created.project_id)
    ) == created
    assert service.list_projects(ListProjectsRequest("learner-1")) == (created,)
    assert briefs.calls == placements.calls == 0


def test_changed_idempotency_key_meaning_conflicts_without_second_row() -> None:
    service, repository, _briefs, _placements = build_service()
    intent = ProjectCreateIntent(
        "1.0.0",
        "same-key",
        "First title",
        "First charter.",
        IndependentProjectOrigin(),
    )
    service.create_project(CreateProjectRequest("learner-1", intent))

    with pytest.raises(ProjectError) as captured:
        service.create_project(
            CreateProjectRequest(
                "learner-1", replace(intent, title="Changed title")
            )
        )

    assert captured.value.code is ProjectErrorCode.IMMUTABLE_CONFLICT
    assert len(repository.rows) == 1


def test_learning_create_retains_exact_source_and_rejects_stale_placement() -> None:
    service, repository, briefs, placements = build_service()
    _brief, _placement, origin = learning_setup()
    intent = ProjectCreateIntent(
        "1.0.0",
        "learning-1",
        "My comparison",
        "Apply the approved brief without making a recommendation.",
        origin,
    )

    created = service.create_project(CreateProjectRequest("learner-1", intent))
    replay = service.create_project(CreateProjectRequest("learner-1", intent))
    assert created.origin == origin
    assert replay == created
    assert briefs.calls == placements.calls == 1

    stale = replace(
        intent,
        idempotency_key="learning-stale",
        origin=replace(origin, placement_digest="e" * 64),
    )
    with pytest.raises(ProjectError) as captured:
        service.create_project(CreateProjectRequest("learner-1", stale))
    assert captured.value.code is ProjectErrorCode.INVALID_REQUEST
    assert len(repository.rows) == 1


def test_cross_learner_open_is_indistinguishable_from_unknown_project() -> None:
    service, _repository, _briefs, _placements = build_service()
    intent = ProjectCreateIntent(
        "1.0.0",
        "private-1",
        "Private Project",
        "Keep ownership server-derived.",
        IndependentProjectOrigin(),
    )
    created = service.create_project(CreateProjectRequest("learner-1", intent))

    with pytest.raises(ProjectError) as captured:
        service.open_project(OpenProjectRequest("learner-2", created.project_id))

    assert captured.value.code is ProjectErrorCode.NOT_FOUND
