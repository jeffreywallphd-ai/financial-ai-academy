from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from financial_ai_academy.modules.content.public import (
    LessonErrorCode,
    LessonReadError,
    PublishedProjectBrief,
)
from financial_ai_academy.modules.curriculum.application.service import (
    CurriculumService,
)
from financial_ai_academy.modules.curriculum.ports.repositories import (
    PlacementConflict,
)
from financial_ai_academy.modules.curriculum.public import (
    CreateProjectBriefPlacementRequest,
    LessonActivityReference,
    ListProjectBriefPlacementsRequest,
    ProjectBriefPlacement,
    ResolveProjectBriefPlacementRequest,
)


NOW = datetime(2026, 10, 16, tzinfo=timezone.utc)


class Content:
    def get_project_brief_exact(
        self,
        package_id: str,
        package_version: str,
        package_digest: str,
        brief_id: str,
    ) -> PublishedProjectBrief:
        return PublishedProjectBrief(
            package_id,
            package_version,
            package_digest,
            brief_id,
            "1.0.0",
            "b" * 64,
            "1.0.0",
            "f" * 64,
            b"{}",
        )


class Repository:
    def __init__(self) -> None:
        self.value: ProjectBriefPlacement | None = None
        self.graph = SimpleNamespace(
            graph_digest="c" * 64,
            activities=(
                SimpleNamespace(
                    activity_id="activity-risk-return-project",
                    reference=LessonActivityReference(
                        placement_id="risk-return-project-source",
                        package_id="intro-risk-return-project",
                        package_version="1.0.0",
                        package_digest="a" * 64,
                    ),
                ),
            ),
        )

    def get_graph_exact(
        self, curriculum_id: str, curriculum_version: str
    ) -> object | None:
        if (
            curriculum_id,
            curriculum_version,
        ) == ("financial-foundations", "1.0.0"):
            return self.graph
        return None

    def save_project_brief_if_absent(
        self, placement: ProjectBriefPlacement
    ) -> tuple[ProjectBriefPlacement, bool]:
        if self.value is None:
            self.value = placement
            return placement, True
        if self.value.placement_digest != placement.placement_digest:
            raise PlacementConflict
        return self.value, False

    def get_project_brief(
        self, placement_id: str
    ) -> ProjectBriefPlacement | None:
        if self.value and self.value.placement_id == placement_id:
            return self.value
        return None

    def list_project_briefs(self) -> tuple[ProjectBriefPlacement, ...]:
        return () if self.value is None else (self.value,)


def request() -> CreateProjectBriefPlacementRequest:
    return CreateProjectBriefPlacementRequest(
        placement_id="risk-return-project-primary",
        placement_version="1.0.0",
        curriculum_id="financial-foundations",
        curriculum_version="1.0.0",
        curriculum_digest="c" * 64,
        activity_id="activity-risk-return-project",
        package_id="intro-risk-return-project",
        package_version="1.0.0",
        package_digest="a" * 64,
        brief_id="risk-return-project",
        brief_version="1.0.0",
        brief_digest="b" * 64,
        project_brief_schema_version="1.0.0",
    )


def service(repository: Repository | None = None) -> CurriculumService:
    return CurriculumService(
        repository or Repository(),  # type: ignore[arg-type]
        Content(),  # type: ignore[arg-type]
        clock=lambda: NOW,
    )


def test_exact_project_brief_placement_is_idempotent_and_resolvable() -> None:
    selected = Repository()
    subject = service(selected)

    created = subject.create_project_brief_placement(request())
    replay = subject.create_project_brief_placement(request())
    resolved = subject.resolve_project_brief_placement(
        ResolveProjectBriefPlacementRequest(created.placement_id)
    )

    assert created == replay == resolved
    assert created.created_at == NOW
    assert len(created.placement_digest) == 64
    assert subject.list_project_brief_placements(
        ListProjectBriefPlacementsRequest()
    ) == (created,)


def test_stale_brief_reference_fails_before_placement_persistence() -> None:
    selected = Repository()
    subject = service(selected)
    stale = replace(request(), brief_digest="d" * 64)

    with pytest.raises(LessonReadError) as captured:
        subject.create_project_brief_placement(stale)

    assert captured.value.code is LessonErrorCode.INVALID_PACKAGE
    assert selected.value is None


@pytest.mark.parametrize(
    "change",
    (
        {"curriculum_digest": "d" * 64},
        {"activity_id": "activity-missing-project"},
        {"package_digest": "e" * 64},
    ),
)
def test_stale_curriculum_or_activity_fails_before_persistence(
    change: dict[str, str],
) -> None:
    selected = Repository()
    subject = service(selected)

    with pytest.raises(LessonReadError) as captured:
        subject.create_project_brief_placement(replace(request(), **change))

    assert captured.value.code is LessonErrorCode.INVALID_PACKAGE
    assert selected.value is None


def test_missing_project_brief_placement_is_bounded_not_found() -> None:
    with pytest.raises(LessonReadError) as captured:
        service().resolve_project_brief_placement(
            ResolveProjectBriefPlacementRequest("missing-placement")
        )

    assert captured.value.code is LessonErrorCode.NOT_FOUND
