"""Loopback-only Python composition for local approved-lesson qualification."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Awaitable, Callable
from dataclasses import replace
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse


REPOSITORY = Path(__file__).resolve().parents[2]
BACKEND_SOURCE = REPOSITORY / "backend" / "src"
if str(BACKEND_SOURCE) not in sys.path:
    sys.path.insert(0, str(BACKEND_SOURCE))

from financial_ai_academy.bootstrap.composition import (  # noqa: E402
    build_application_services,
)
from financial_ai_academy.bootstrap.settings import (  # noqa: E402
    SingleProfileApplicationSettings,
)
from financial_ai_academy.hosts.api.app import (  # noqa: E402
    ApiServices,
    create_app,
)
from financial_ai_academy.modules.content.public import (  # noqa: E402
    AdmitLessonPackageRequest,
)
from financial_ai_academy.modules.curriculum.public import (  # noqa: E402
    AssessmentActivityReference,
    CreateAssessmentPlacementRequest,
    CreateLessonPlacementRequest,
    CurriculumGraph,
    LessonActivityReference,
    OpportunityAvailability,
    OpportunityLevel,
    PublishCurriculumGraphRequest,
    RebuildLearningOpportunityProjectionRequest,
    RegisterLessonOpportunityRequest,
    curriculum_graph_digest,
    curriculum_graph_from_mapping,
)
from financial_ai_academy.platform.security.single_profile_policy import (  # noqa: E402
    SingleProfileSecuritySettings,
)


LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})
PLACEMENT_ID = "intro-risk-return-primary"
APPROVED_FIXTURE = (
    REPOSITORY
    / "contracts"
    / "compatibility"
    / "lesson-package"
    / "v1"
    / "approved"
    / "intro-risk-return-knowledge-check"
)
CURRICULUM_GRAPH_FIXTURE = (
    REPOSITORY
    / "contracts"
    / "compatibility"
    / "curriculum-graph"
    / "v1"
    / "approved"
    / "graph.json"
)

ASSESSMENT_ID = "risk-return-check-1"
QUERY_OPPORTUNITY_FIXTURES = (
    {
        "opportunity_id": "intro-risk-return-quick-review",
        "summary": (
            "Review the central risk and return relationship in a short "
            "educational refresher."
        ),
        "topics": ("quick-review", "risk-and-return"),
        "level": OpportunityLevel.INTRODUCTORY,
        "estimated_minutes": 10,
        "prerequisite_summary": "No prior lesson is required.",
        "availability": OpportunityAvailability.UNAVAILABLE,
        "availability_reason": (
            "This synthetic quick review is unavailable in qualification."
        ),
    },
    {
        "opportunity_id": "intro-risk-return-guided-practice",
        "summary": (
            "Practice comparing risk and return with a guided educational "
            "scenario."
        ),
        "topics": ("guided-practice", "risk-and-return"),
        "level": OpportunityLevel.INTERMEDIATE,
        "estimated_minutes": 35,
        "prerequisite_summary": (
            "Complete the introductory risk and return lesson first."
        ),
        "availability": OpportunityAvailability.PLANNED,
        "availability_reason": (
            "This synthetic guided practice remains planned in qualification."
        ),
    },
)


def qualification_graph(
    *,
    package_id: str,
    package_version: str,
    package_digest: str,
) -> CurriculumGraph:
    """Bind the reviewed graph shape to the admitted qualification package."""
    source = json.loads(CURRICULUM_GRAPH_FIXTURE.read_text(encoding="utf-8"))
    graph = curriculum_graph_from_mapping(source)
    activities = tuple(
        replace(
            activity,
            reference=replace(
                activity.reference,
                package_id=package_id,
                package_version=package_version,
                package_digest=package_digest,
            ),
        )
        if isinstance(activity.reference, LessonActivityReference)
        else activity
        for activity in graph.activities
    )
    branches = tuple(
        replace(
            branch,
            activity_ids=(
                *branch.activity_ids,
                "activity-diversification-reading",
            ),
        )
        if branch.branch_id == "branch-practice"
        else branch
        for branch in graph.branches
    )
    candidate = replace(
        graph,
        source_references=(
            f"content:{package_id}@{package_version}",
            f"curriculum:{graph.curriculum_id}@{graph.curriculum_version}",
        ),
        activities=activities,
        branches=branches,
        graph_digest="0" * 64,
    )
    return replace(
        candidate,
        graph_digest=curriculum_graph_digest(candidate),
    )


def build_local_app(
    *,
    postgres_dsn: str,
    data_root: Path,
    web_dist: Path,
    host: str,
    port: int,
    seed_approved_fixture: bool,
    seed_discovery_query_fixtures: bool = False,
    serve_static: bool = True,
    public_origin: str | None = None,
    allowed_hosts: tuple[str, ...] | None = None,
) -> FastAPI:
    """Compose the reviewed loopback API with optional static SPA serving."""
    if host not in LOOPBACK_HOSTS:
        raise ValueError("The community single-profile host must be loopback.")
    if not 1 <= port <= 65_535:
        raise ValueError("The application port is outside the valid range.")
    if seed_discovery_query_fixtures and not seed_approved_fixture:
        raise ValueError(
            "Discovery query fixtures require the explicit approved fixture."
        )
    index_file = web_dist / "index.html"
    asset_directory = web_dist / "assets"
    if serve_static and (
        not index_file.is_file() or not asset_directory.is_dir()
    ):
        raise ValueError(
            "Static web artifacts are unavailable; run the reviewed web build."
        )
    data_root.mkdir(parents=True, exist_ok=True)

    origin_host = "127.0.0.1" if host in {"localhost", "::1"} else host
    configured_public_origin = (
        public_origin or f"http://{origin_host}:{port}"
    )
    configured_allowed_hosts = allowed_hosts or (f"{origin_host}:{port}",)
    settings = SingleProfileApplicationSettings(
        postgres_dsn=postgres_dsn,
        object_storage_root=data_root / "objects",
        lesson_schema_dir=(
            REPOSITORY / "contracts" / "learning" / "lesson-package" / "v1"
        ),
        migrations_dir=REPOSITORY / "backend" / "migrations",
        security=SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host=host,
            public_origin=configured_public_origin,
            allowed_hosts=configured_allowed_hosts,
            secure_cookie=False,
        ),
    )
    services = build_application_services(settings, apply_migrations=True)
    if seed_approved_fixture:
        accepted = services.content.admit_lesson_package(
            AdmitLessonPackageRequest(APPROVED_FIXTURE)
        )
        graph = qualification_graph(
            package_id=accepted.package_id,
            package_version=accepted.package_version,
            package_digest=accepted.package_digest,
        )
        placement_ids: set[str] = set()
        for activity in graph.activities:
            reference = activity.reference
            if reference.placement_id in placement_ids:
                continue
            services.curriculum.create_lesson_placement(
                CreateLessonPlacementRequest(
                    placement_id=reference.placement_id,
                    package_id=accepted.package_id,
                    package_version=accepted.package_version,
                    package_digest=accepted.package_digest,
                )
            )
            placement_ids.add(reference.placement_id)
        for activity in graph.activities:
            reference = activity.reference
            if not isinstance(reference, AssessmentActivityReference):
                continue
            primary = reference.assessment_id == ASSESSMENT_ID
            services.curriculum.create_assessment_placement(
                CreateAssessmentPlacementRequest(
                    placement_id=reference.placement_id,
                    package_id=accepted.package_id,
                    package_version=accepted.package_version,
                    package_digest=accepted.package_digest,
                    assessment_id=reference.assessment_id,
                    assessment_version=reference.assessment_version,
                    definition_digest=reference.definition_digest,
                    item_id=(
                        "risk-return-tradeoff"
                        if primary
                        else f"{reference.assessment_id}-item"
                    ),
                    item_version="1.0.0",
                    scoring_policy_id="single-select-exact-match",
                    scoring_policy_version="1.0.0",
                )
            )
        services.curriculum.publish_curriculum_graph(
            PublishCurriculumGraphRequest(graph=graph)
        )
        services.curriculum.register_lesson_opportunity(
            RegisterLessonOpportunityRequest(
                opportunity_id=PLACEMENT_ID,
                placement_id=PLACEMENT_ID,
                summary=(
                    "Build a foundational understanding of how potential "
                    "return and risk relate before comparing investments."
                ),
                topics=("investment-basics", "risk-and-return"),
                level=OpportunityLevel.INTRODUCTORY,
                estimated_minutes=20,
                prerequisite_summary="No prior lesson is required.",
                availability=OpportunityAvailability.AVAILABLE,
                availability_reason=(
                    "The exact reviewed lesson is available in this local "
                    "catalog."
                ),
            )
        )
        if seed_discovery_query_fixtures:
            for fixture in QUERY_OPPORTUNITY_FIXTURES:
                services.curriculum.register_lesson_opportunity(
                    RegisterLessonOpportunityRequest(
                        placement_id=PLACEMENT_ID,
                        **fixture,
                    )
                )
        services.curriculum.rebuild_learning_opportunity_projection(
            RebuildLearningOpportunityProjectionRequest()
        )

    app = create_app(
        ApiServices(
            identity=services.identity,
            curriculum=services.curriculum,
            request_policy=services.request_policy,
            assessment=services.assessment,
            learner_model=services.learner_model,
            adaptation=services.adaptation,
            audit=services.audit,
        )
    )

    @app.middleware("http")
    async def add_browser_security_headers(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; base-uri 'none'; frame-ancestors 'none'; "
            "form-action 'self'; img-src 'self'; object-src 'none'; "
            "script-src 'self'; style-src 'self'; connect-src 'self'"
        )
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    if serve_static:
        from fastapi.staticfiles import StaticFiles

        app.mount(
            "/assets",
            StaticFiles(directory=asset_directory, check_dir=True),
            name="static-assets",
        )

        @app.get("/", include_in_schema=False)
        @app.get("/{browser_path:path}", include_in_schema=False)
        def browser_application(browser_path: str = "") -> FileResponse:
            if browser_path == "api" or browser_path.startswith("api/"):
                raise HTTPException(status_code=404)
            return FileResponse(index_file)

    return app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve the loopback-only local qualification profile."
    )
    parser.add_argument("--postgres-dsn", required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument(
        "--web-dist",
        type=Path,
        default=REPOSITORY / "apps" / "web" / "dist",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--seed-approved-fixture", action="store_true")
    parser.add_argument(
        "--seed-discovery-query-fixtures",
        action="store_true",
        help=(
            "Add the bounded synthetic multi-page query corpus; requires "
            "--seed-approved-fixture."
        ),
    )
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Serve only the API so a loopback Vite development proxy can serve the SPA.",
    )
    parser.add_argument(
        "--public-origin",
        help="Exact loopback browser origin used for state-changing request checks.",
    )
    parser.add_argument(
        "--allowed-host",
        action="append",
        dest="allowed_hosts",
        help="Allowed Host header; repeat when both proxy and direct readiness access are needed.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = build_local_app(
        postgres_dsn=args.postgres_dsn,
        data_root=args.data_root.resolve(),
        web_dist=args.web_dist.resolve(),
        host=args.host,
        port=args.port,
        seed_approved_fixture=args.seed_approved_fixture,
        seed_discovery_query_fixtures=(
            args.seed_discovery_query_fixtures
        ),
        serve_static=not args.api_only,
        public_origin=args.public_origin,
        allowed_hosts=(
            tuple(args.allowed_hosts) if args.allowed_hosts else None
        ),
    )

    import uvicorn

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        access_log=False,
        server_header=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
