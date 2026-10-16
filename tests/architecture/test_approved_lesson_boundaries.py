from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock


REPOSITORY = Path(__file__).resolve().parents[2]
BACKEND_SOURCE = REPOSITORY / "backend" / "src" / "financial_ai_academy"
MODULES = BACKEND_SOURCE / "modules"
WEB_SOURCE = REPOSITORY / "apps" / "web" / "src"
WEB_PACKAGE = REPOSITORY / "apps" / "web" / "package.json"
WEB_DIST = REPOSITORY / "apps" / "web" / "dist"
SETUP_SCRIPT = REPOSITORY / "deployments" / "local" / "setup-dev.mjs"
LOCAL_SERVER = REPOSITORY / "deployments" / "local" / "serve.py"
PLACEMENT_ID = "intro-risk-return-primary"


class StubApplication:
    def middleware(self, middleware_kind: str):
        self.middleware_kind = middleware_kind
        return lambda handler: handler


class Record:
    def __init__(self, *args: object, **kwargs: object) -> None:
        self.args = args
        self.__dict__.update(kwargs)


class LessonReference(Record):
    pass


class AssessmentReference(Record):
    pass


def local_services() -> SimpleNamespace:
    content = SimpleNamespace(admit_lesson_package=MagicMock())
    curriculum = SimpleNamespace(
        create_lesson_placement=MagicMock(),
        create_assessment_placement=MagicMock(),
        publish_curriculum_graph=MagicMock(),
        register_lesson_opportunity=MagicMock(),
        rebuild_learning_opportunity_projection=MagicMock(),
    )
    return SimpleNamespace(
        adaptation=object(),
        assessment=object(),
        audit=object(),
        content=content,
        curriculum=curriculum,
        identity=object(),
        learner_model=object(),
        request_policy=object(),
    )


def exercise_local_composition(
    services: SimpleNamespace,
    *,
    seed_approved_fixture: bool,
    seed_discovery_query_fixtures: bool = False,
    create_app: MagicMock | None = None,
) -> tuple[StubApplication, MagicMock]:
    tree = ast.parse(
        LOCAL_SERVER.read_text(encoding="utf-8"),
        filename=str(LOCAL_SERVER),
    )
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "build_local_app"
    )
    isolated_module = ast.Module(
        body=[
            ast.ImportFrom(
                module="__future__",
                names=[ast.alias(name="annotations")],
                level=0,
            ),
            function,
        ],
        type_ignores=[],
    )
    ast.fix_missing_locations(isolated_module)
    app = StubApplication()
    application_factory = create_app or MagicMock(return_value=app)
    namespace = {
        "APPROVED_FIXTURE": REPOSITORY / "contracts",
        "ASSESSMENT_ID": "risk-return-check-1",
        "AdmitLessonPackageRequest": Record,
        "ApiServices": Record,
        "AssessmentActivityReference": AssessmentReference,
        "CreateAssessmentPlacementRequest": Record,
        "CreateLessonPlacementRequest": Record,
        "LOOPBACK_HOSTS": frozenset({"127.0.0.1", "::1", "localhost"}),
        "LessonActivityReference": LessonReference,
        "OpportunityAvailability": SimpleNamespace(AVAILABLE="available"),
        "OpportunityLevel": SimpleNamespace(INTRODUCTORY="introductory"),
        "PLACEMENT_ID": PLACEMENT_ID,
        "PublishCurriculumGraphRequest": Record,
        "QUERY_OPPORTUNITY_FIXTURES": (
            {
                "opportunity_id": "intro-risk-return-quick-review",
                "summary": "A bounded synthetic quick review summary.",
                "topics": ("quick-review", "risk-and-return"),
                "level": "introductory",
                "estimated_minutes": 10,
                "prerequisite_summary": "No prior lesson is required.",
                "availability": "unavailable",
                "availability_reason": "Unavailable in qualification.",
            },
            {
                "opportunity_id": "intro-risk-return-guided-practice",
                "summary": "A bounded synthetic guided practice summary.",
                "topics": ("guided-practice", "risk-and-return"),
                "level": "intermediate",
                "estimated_minutes": 35,
                "prerequisite_summary": "Complete the lesson first.",
                "availability": "planned",
                "availability_reason": "Planned in qualification.",
            },
        ),
        "REPOSITORY": REPOSITORY,
        "RebuildLearningOpportunityProjectionRequest": Record,
        "RegisterLessonOpportunityRequest": Record,
        "SingleProfileApplicationSettings": Record,
        "SingleProfileSecuritySettings": Record,
        "build_application_services": MagicMock(return_value=services),
        "create_app": application_factory,
        "qualification_graph": MagicMock(
            return_value=SimpleNamespace(
                activities=(
                    Record(
                        activity_id="activity-risk-return-lesson",
                        reference=LessonReference(
                            placement_id=PLACEMENT_ID,
                        ),
                    ),
                    Record(
                        activity_id="activity-risk-return-check",
                        reference=AssessmentReference(
                            placement_id=PLACEMENT_ID,
                            assessment_id="risk-return-check-1",
                            assessment_version="1.0.0",
                            definition_digest="b" * 64,
                        ),
                    ),
                    Record(
                        activity_id="activity-diversification-reading",
                        reference=LessonReference(
                            placement_id="diversification-reading",
                        ),
                    ),
                    Record(
                        activity_id="activity-diversification-check",
                        reference=AssessmentReference(
                            placement_id="diversification-check",
                            assessment_id="diversification-check",
                            assessment_version="1.0.0",
                            definition_digest="c" * 64,
                        ),
                    ),
                    Record(
                        activity_id="activity-terms-glossary",
                        reference=LessonReference(
                            placement_id="investing-terms-glossary",
                        ),
                    ),
                )
            )
        ),
    }
    exec(compile(isolated_module, LOCAL_SERVER, "exec"), namespace)
    with tempfile.TemporaryDirectory() as temporary_directory:
        result = namespace["build_local_app"](
            postgres_dsn="postgresql://qualification-only",
            data_root=Path(temporary_directory) / "data",
            web_dist=Path(temporary_directory) / "web",
            host="127.0.0.1",
            port=8765,
            seed_approved_fixture=seed_approved_fixture,
            seed_discovery_query_fixtures=(
                seed_discovery_query_fixtures
            ),
            serve_static=False,
        )
    return result, application_factory


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


class ApprovedLessonArchitectureTests(unittest.TestCase):
    def test_fixture_seed_is_disabled_without_discovery_mutations(self) -> None:
        services = local_services()

        app, create_app = exercise_local_composition(
            services,
            seed_approved_fixture=False,
        )

        self.assertIsInstance(app, StubApplication)
        services.content.admit_lesson_package.assert_not_called()
        services.curriculum.create_lesson_placement.assert_not_called()
        services.curriculum.create_assessment_placement.assert_not_called()
        services.curriculum.publish_curriculum_graph.assert_not_called()
        services.curriculum.register_lesson_opportunity.assert_not_called()
        services.curriculum.rebuild_learning_opportunity_projection.assert_not_called()
        create_app.assert_called_once()

    def test_query_fixture_corpus_is_optional_and_requires_approved_seed(
        self,
    ) -> None:
        services = local_services()

        with self.assertRaisesRegex(
            ValueError,
            "require the explicit approved fixture",
        ):
            exercise_local_composition(
                services,
                seed_approved_fixture=False,
                seed_discovery_query_fixtures=True,
            )

        services.content.admit_lesson_package.assert_not_called()
        services.curriculum.register_lesson_opportunity.assert_not_called()
        services.curriculum.rebuild_learning_opportunity_projection.assert_not_called()

    def test_query_fixture_corpus_registers_before_one_atomic_rebuild(
        self,
    ) -> None:
        services = local_services()
        events: list[str] = []
        accepted = SimpleNamespace(
            package_id="intro-risk-return",
            package_version="1.1.0",
            package_digest="a" * 64,
        )
        placement = SimpleNamespace(placement_id=PLACEMENT_ID)
        services.content.admit_lesson_package.return_value = accepted
        services.curriculum.create_lesson_placement.return_value = placement
        services.curriculum.register_lesson_opportunity.side_effect = (
            lambda request: events.append(
                f"register:{request.opportunity_id}"
            )
        )
        services.curriculum.rebuild_learning_opportunity_projection.side_effect = (
            lambda request: events.append("rebuild")
        )

        exercise_local_composition(
            services,
            seed_approved_fixture=True,
            seed_discovery_query_fixtures=True,
        )

        self.assertEqual(
            events,
            [
                f"register:{PLACEMENT_ID}",
                "register:intro-risk-return-quick-review",
                "register:intro-risk-return-guided-practice",
                "rebuild",
            ],
        )
        services.curriculum.rebuild_learning_opportunity_projection.assert_called_once()

    def test_fixture_seed_uses_exact_public_operation_order(self) -> None:
        services = local_services()
        events: list[str] = []
        accepted = SimpleNamespace(
            package_id="intro-risk-return",
            package_version="1.1.0",
            package_digest="a" * 64,
        )
        services.content.admit_lesson_package.side_effect = (
            lambda request: events.append("admit") or accepted
        )
        services.curriculum.create_lesson_placement.side_effect = (
            lambda request: events.append(
                f"lesson-placement:{request.placement_id}"
            )
        )
        services.curriculum.create_assessment_placement.side_effect = (
            lambda request: events.append(
                f"assessment-placement:{request.assessment_id}"
            )
        )
        services.curriculum.publish_curriculum_graph.side_effect = (
            lambda request: events.append("publish-graph")
        )
        services.curriculum.register_lesson_opportunity.side_effect = (
            lambda request: events.append("register-opportunity")
        )
        services.curriculum.rebuild_learning_opportunity_projection.side_effect = (
            lambda request: events.append("rebuild-projection")
        )
        app = StubApplication()
        create_app = MagicMock(
            side_effect=lambda api_services: events.append("create-app") or app
        )
        result, extracted_create_app = exercise_local_composition(
            services,
            seed_approved_fixture=True,
            create_app=create_app,
        )

        self.assertIs(result, app)
        extracted_create_app.assert_called_once()
        self.assertEqual(
            events,
            [
                "admit",
                f"lesson-placement:{PLACEMENT_ID}",
                "lesson-placement:diversification-reading",
                "lesson-placement:diversification-check",
                "lesson-placement:investing-terms-glossary",
                "assessment-placement:risk-return-check-1",
                "assessment-placement:diversification-check",
                "publish-graph",
                "register-opportunity",
                "rebuild-projection",
                "create-app",
            ],
        )

    def test_fixture_seed_failure_prevents_application_readiness(self) -> None:
        for failure in ("graph", "register", "rebuild"):
            with self.subTest(failure=failure):
                services = local_services()
                accepted = SimpleNamespace(
                    package_id="intro-risk-return",
                    package_version="1.1.0",
                    package_digest="a" * 64,
                )
                placement = SimpleNamespace(placement_id=PLACEMENT_ID)
                services.content.admit_lesson_package.return_value = accepted
                services.curriculum.create_lesson_placement.return_value = placement
                failing_operation = {
                    "graph": services.curriculum.publish_curriculum_graph,
                    "register": services.curriculum.register_lesson_opportunity,
                    "rebuild": services.curriculum.rebuild_learning_opportunity_projection,
                }[failure]
                failing_operation.side_effect = RuntimeError(
                    "deliberate fixture failure"
                )
                create_app = MagicMock(return_value=StubApplication())
                with self.assertRaisesRegex(
                    RuntimeError,
                    "deliberate fixture failure",
                ):
                    exercise_local_composition(
                        services,
                        seed_approved_fixture=True,
                        create_app=create_app,
                    )

                create_app.assert_not_called()
                if failure in {"graph", "register"}:
                    services.curriculum.rebuild_learning_opportunity_projection.assert_not_called()

    def test_all_implemented_domain_layers_point_inward(self) -> None:
        forbidden = {
            "fastapi",
            "jsonschema",
            "markdown_it",
            "psycopg",
            "pydantic",
            "starlette",
            "uvicorn",
            "financial_ai_academy.bootstrap",
            "financial_ai_academy.hosts",
            "financial_ai_academy.platform",
        }
        violations: list[str] = []
        for owner in ("content", "curriculum", "identity"):
            for path in (MODULES / owner / "domain").rglob("*.py"):
                for imported in imports(path):
                    if any(
                        imported == prefix
                        or imported.startswith(prefix + ".")
                        for prefix in forbidden
                    ):
                        violations.append(
                            f"{path.relative_to(REPOSITORY)}: {imported}"
                        )
        self.assertEqual(violations, [])

    def test_cross_module_dependencies_use_public_surfaces(self) -> None:
        owners = {"content", "curriculum", "identity"}
        prefix = "financial_ai_academy.modules."
        violations: list[str] = []
        for owner in owners:
            for path in (MODULES / owner).rglob("*.py"):
                for imported in imports(path):
                    if not imported.startswith(prefix):
                        continue
                    parts = imported.split(".")
                    if len(parts) < 4:
                        continue
                    target = parts[2]
                    if target in owners and target != owner:
                        if imported != f"{prefix}{target}.public":
                            violations.append(
                                f"{path.relative_to(REPOSITORY)}: {imported}"
                            )
        self.assertEqual(violations, [])

    def test_module_repositories_reference_only_owned_schemas(self) -> None:
        violations: list[str] = []
        owners = ("content", "curriculum", "identity")
        for owner in owners:
            path = MODULES / owner / "adapters" / "postgres_repository.py"
            source = path.read_text(encoding="utf-8").casefold()
            for other in owners:
                if other != owner and f"{other}." in source:
                    violations.append(
                        f"{path.relative_to(REPOSITORY)} references {other}"
                    )
        self.assertEqual(violations, [])

    def test_browser_uses_generated_client_and_safe_rendering_boundaries(
        self,
    ) -> None:
        forbidden = (
            "dangerouslysetinnerhtml",
            "document.write",
            "new function",
            "<iframe",
        )
        violations: list[str] = []
        for path in WEB_SOURCE.rglob("*"):
            if path.suffix not in {".ts", ".tsx"}:
                continue
            source = path.read_text(encoding="utf-8")
            folded = source.casefold()
            if "financial_ai_academy" in source or "backend/" in source:
                violations.append(
                    f"{path.relative_to(REPOSITORY)} imports backend authority"
                )
            if "openapi-fetch" in source and (
                "src/generated/api-client/client.ts"
                not in path.as_posix()
            ):
                violations.append(
                    f"{path.relative_to(REPOSITORY)} bypasses generated client"
                )
            for token in forbidden:
                if token in folded:
                    violations.append(
                        f"{path.relative_to(REPOSITORY)} contains {token}"
                    )
        generated = (
            WEB_SOURCE / "generated" / "api-client" / "client.ts"
        ).read_text(encoding="utf-8")
        self.assertIn("// @generated", generated)
        self.assertEqual(violations, [])

    def test_web_manifest_has_no_node_production_server(self) -> None:
        package = json.loads(WEB_PACKAGE.read_text(encoding="utf-8"))
        banned_dependencies = {
            "@react-router/node",
            "express",
            "fastify",
            "next",
        }
        dependencies = set(package.get("dependencies", {}))
        dependencies.update(package.get("devDependencies", {}))
        self.assertEqual(dependencies.intersection(banned_dependencies), set())
        self.assertTrue(
            {"start", "serve", "server"}.isdisjoint(package["scripts"])
        )
        self.assertEqual(package["scripts"]["build"], "vite build")
        server_entries = [
            path.relative_to(REPOSITORY).as_posix()
            for path in WEB_SOURCE.rglob("*")
            if path.is_file()
            and path.stem.casefold() in {"server", "entry.server"}
        ]
        self.assertEqual(server_entries, [])

    def test_development_setup_is_pinned_and_shell_profile_neutral(self) -> None:
        package = json.loads(WEB_PACKAGE.read_text(encoding="utf-8"))
        source = SETUP_SCRIPT.read_text(encoding="utf-8")
        folded = source.casefold()
        self.assertEqual(
            package["scripts"]["setup:dev"],
            "node ../../deployments/local/setup-dev.mjs",
        )
        for token in (
            'const REQUIRED_NODE = "24.14.0"',
            'const REQUIRED_NPM = "10.8.2"',
            'const FNM_PACKAGE = "Schniz.fnm"',
            '"--accept-source-agreements"',
            '"--accept-package-agreements"',
            '"exec"',
            '"dev:full"',
            "shell: false",
        ):
            self.assertIn(token, source)
        for forbidden in (
            ".bashrc",
            ".bash_profile",
            "microsoft.powershell_profile",
            "setx ",
            "curl ",
        ):
            self.assertNotIn(forbidden, folded)

    def test_local_composition_is_loopback_python_and_postgres_only(
        self,
    ) -> None:
        server = (
            REPOSITORY / "deployments" / "local" / "serve.py"
        ).read_text(encoding="utf-8")
        compose = (
            REPOSITORY
            / "deployments"
            / "local"
            / "compose.qualify.yml"
        ).read_text(encoding="utf-8")
        self.assertIn('LOOPBACK_HOSTS = frozenset({"127.0.0.1"', server)
        self.assertIn("import uvicorn", server)
        self.assertIn("services.curriculum.register_lesson_opportunity", server)
        self.assertIn("services.curriculum.publish_curriculum_graph", server)
        self.assertIn(
            "services.curriculum.rebuild_learning_opportunity_projection",
            server,
        )
        self.assertNotIn("PostgresCurriculumRepository", server)
        self.assertNotIn("node", server.casefold())
        self.assertIn("postgres:18.4", compose)
        self.assertIn("127.0.0.1:", compose)
        self.assertNotIn("0.0.0.0", compose)

    def test_static_build_contains_only_browser_artifacts_when_present(
        self,
    ) -> None:
        if not WEB_DIST.is_dir():
            self.skipTest("Static build is inspected after the build command.")
        allowed = {
            ".css",
            ".html",
            ".jpeg",
            ".jpg",
            ".js",
            ".map",
            ".png",
            ".svg",
            ".webp",
        }
        unexpected = [
            path.relative_to(WEB_DIST).as_posix()
            for path in WEB_DIST.rglob("*")
            if path.is_file() and path.suffix.casefold() not in allowed
        ]
        self.assertEqual(unexpected, [])
        self.assertTrue((WEB_DIST / "index.html").is_file())


if __name__ == "__main__":
    unittest.main()
