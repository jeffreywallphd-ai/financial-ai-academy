from __future__ import annotations

import json
import os
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import pytest

from financial_ai_academy.modules.curriculum.adapters.postgres_repository import (
    PostgresCurriculumRepository,
)
from financial_ai_academy.modules.curriculum.application.service import (
    CurriculumService,
)
from financial_ai_academy.modules.curriculum.public import (
    AssessmentActivityReference,
    AssessmentPlacement,
    CurriculumGraph,
    CurriculumGraphError,
    CurriculumGraphErrorCode,
    LessonActivityReference,
    LessonPlacement,
    OpenCurriculumGraphRequest,
    PublishCurriculumGraphRequest,
    curriculum_graph_digest,
    curriculum_graph_from_mapping,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)


REPOSITORY = Path(__file__).resolve().parents[4]
MIGRATIONS = REPOSITORY / "backend/migrations"
APPROVED = (
    REPOSITORY
    / "contracts/compatibility/curriculum-graph/v1/approved/graph.json"
)
POSTGRES_DSN = os.environ.get("FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN")
NOW = datetime(2026, 10, 15, tzinfo=timezone.utc)

pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(
        POSTGRES_DSN is None,
        reason="FINANCIAL_AI_ACADEMY_TEST_POSTGRES_DSN is not configured",
    ),
]


class UnusedContentGateway:
    def get_exact(self, *_args: object) -> object:
        raise AssertionError("graph operations must not read Content")


def approved_graph() -> CurriculumGraph:
    return curriculum_graph_from_mapping(
        json.loads(APPROVED.read_text(encoding="utf-8"))
    )


def shared_optional_activity_graph() -> CurriculumGraph:
    graph = approved_graph()
    shared_activity_id = "activity-diversification-reading"
    branches = tuple(
        replace(
            branch,
            activity_ids=branch.activity_ids + (shared_activity_id,),
        )
        if branch.branch_id == "branch-practice"
        else branch
        for branch in graph.branches
    )
    flexible = replace(
        graph,
        branches=branches,
        presentation_order=None,
        graph_digest="0" * 64,
    )
    return replace(flexible, graph_digest=curriculum_graph_digest(flexible))


@pytest.fixture(scope="module", autouse=True)
def migrated_database() -> object:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as connection:
        connection.execute("DROP SCHEMA IF EXISTS curriculum CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS content CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS platform CASCADE")
    root = PostgresMigrationRunner(POSTGRES_DSN, MIGRATIONS)
    curriculum = PostgresMigrationRunner(
        POSTGRES_DSN,
        MIGRATIONS / "curriculum",
    )
    root.apply_all()
    statuses = curriculum.apply_all()
    identifiers = {status.migration_id for status in statuses}
    assert "curriculum_0003_curriculum_graphs" in identifiers
    assert curriculum.apply_all() == statuses
    yield
    with psycopg.connect(POSTGRES_DSN) as connection:
        for migration_id in (
            "curriculum_0006_project_brief_placements",
            "curriculum_0005_practice_review_targets",
            "curriculum_0004_practice_placements",
            "curriculum_0003_curriculum_graphs",
            "curriculum_0002_discovery_projection",
            "curriculum_0001_assessment_placements",
        ):
            connection.execute(
                (
                    MIGRATIONS / f"curriculum/{migration_id}.down.sql"
                ).read_text(encoding="utf-8")
            )
            connection.execute(
                """
                DELETE FROM platform.schema_migrations
                WHERE migration_id = %s
                """,
                (migration_id,),
            )
    root.rollback_all()


@pytest.fixture(autouse=True)
def empty_tables(migrated_database: object) -> None:
    assert POSTGRES_DSN is not None
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                curriculum.curriculum_graph_versions,
                curriculum.assessment_placements,
                curriculum.lesson_placements
            CASCADE
            """
        )


def service() -> CurriculumService:
    assert POSTGRES_DSN is not None
    return CurriculumService(
        PostgresCurriculumRepository(POSTGRES_DSN),
        UnusedContentGateway(),  # type: ignore[arg-type]
    )


def seed_exact_placements(graph: CurriculumGraph) -> None:
    assert POSTGRES_DSN is not None
    repository = PostgresCurriculumRepository(POSTGRES_DSN)
    lessons: dict[str, LessonPlacement] = {}
    for activity in graph.activities:
        reference = activity.reference
        if isinstance(reference, LessonActivityReference):
            lessons[reference.placement_id] = LessonPlacement(
                placement_id=reference.placement_id,
                package_id=reference.package_id,
                package_version=reference.package_version,
                package_digest=reference.package_digest,
                created_at=NOW,
            )
        elif isinstance(reference, AssessmentActivityReference):
            lessons.setdefault(
                reference.placement_id,
                LessonPlacement(
                    placement_id=reference.placement_id,
                    package_id="supporting-package",
                    package_version="1.0.0",
                    package_digest="f" * 64,
                    created_at=NOW,
                ),
            )
    for lesson in lessons.values():
        repository.save_if_absent(lesson)
    for activity in graph.activities:
        reference = activity.reference
        if isinstance(reference, AssessmentActivityReference):
            lesson = lessons[reference.placement_id]
            repository.save_assessment_if_absent(
                AssessmentPlacement(
                    placement_id=reference.placement_id,
                    package_id=lesson.package_id,
                    package_version=lesson.package_version,
                    package_digest=lesson.package_digest,
                    assessment_id=reference.assessment_id,
                    assessment_version=reference.assessment_version,
                    definition_digest=reference.definition_digest,
                    item_id="supporting-item",
                    item_version="1.0.0",
                    scoring_policy_id="single-select-exact-match",
                    scoring_policy_version="1.0.0",
                    created_at=NOW,
                )
            )


def test_publish_replay_and_flexible_round_trip_are_stable() -> None:
    flexible = shared_optional_activity_graph()
    seed_exact_placements(flexible)
    first_service = service()

    first = first_service.publish_curriculum_graph(
        PublishCurriculumGraphRequest(flexible)
    )
    replay = first_service.publish_curriculum_graph(
        PublishCurriculumGraphRequest(flexible)
    )
    reopened = service().open_curriculum_graph(
        OpenCurriculumGraphRequest(
            flexible.curriculum_id,
            flexible.curriculum_version,
        )
    )

    assert first == replay == reopened == flexible
    assert reopened.presentation_order is None
    assert [
        branch.branch_id
        for branch in reopened.branches
        if "activity-diversification-reading" in branch.activity_ids
    ] == ["branch-explore", "branch-practice"]


def test_conflict_and_exact_version_read_never_replace_or_fall_forward() -> None:
    graph = approved_graph()
    seed_exact_placements(graph)
    first_service = service()
    first_service.publish_curriculum_graph(PublishCurriculumGraphRequest(graph))
    changed = replace(graph, title="Changed title", graph_digest="0" * 64)
    changed = replace(changed, graph_digest=curriculum_graph_digest(changed))

    with pytest.raises(CurriculumGraphError) as conflict:
        first_service.publish_curriculum_graph(
            PublishCurriculumGraphRequest(changed)
        )
    assert conflict.value.code is CurriculumGraphErrorCode.IMMUTABLE_CONFLICT
    assert first_service.open_curriculum_graph(
        OpenCurriculumGraphRequest(graph.curriculum_id, "1.0.0")
    ) == graph

    with pytest.raises(CurriculumGraphError) as missing:
        first_service.open_curriculum_graph(
            OpenCurriculumGraphRequest(graph.curriculum_id, "1.1.0")
        )
    assert missing.value.code is CurriculumGraphErrorCode.NOT_FOUND


def test_database_rejects_ordinary_update_and_delete() -> None:
    assert POSTGRES_DSN is not None
    graph = approved_graph()
    seed_exact_placements(graph)
    service().publish_curriculum_graph(PublishCurriculumGraphRequest(graph))

    for statement in (
        "UPDATE curriculum.curriculum_graph_versions SET stored_at = now()",
        "DELETE FROM curriculum.curriculum_graph_versions",
    ):
        with pytest.raises(psycopg.errors.ObjectNotInPrerequisiteState):
            with psycopg.connect(POSTGRES_DSN) as connection:
                connection.execute(statement)
    assert service().open_curriculum_graph(
        OpenCurriculumGraphRequest(graph.curriculum_id, graph.curriculum_version)
    ) == graph


def test_corrupt_stored_payload_fails_closed() -> None:
    assert POSTGRES_DSN is not None
    graph = approved_graph()
    seed_exact_placements(graph)
    service().publish_curriculum_graph(PublishCurriculumGraphRequest(graph))
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """
            ALTER TABLE curriculum.curriculum_graph_versions
            DISABLE TRIGGER curriculum_graph_versions_append_only
            """
        )
        connection.execute(
            """
            UPDATE curriculum.curriculum_graph_versions
            SET graph_payload = jsonb_set(
                graph_payload,
                '{title}',
                '"Corrupted title"'::jsonb
            )
            """
        )
        connection.execute(
            """
            ALTER TABLE curriculum.curriculum_graph_versions
            ENABLE TRIGGER curriculum_graph_versions_append_only
            """
        )

    with pytest.raises(CurriculumGraphError) as captured:
        service().open_curriculum_graph(
            OpenCurriculumGraphRequest(graph.curriculum_id, graph.curriculum_version)
        )
    assert captured.value.code is CurriculumGraphErrorCode.GRAPH_DIGEST_MISMATCH
