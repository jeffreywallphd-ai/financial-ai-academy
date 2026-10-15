from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import FastAPI

from deployments.local import serve


REPOSITORY = Path(__file__).resolve().parents[2]
BACKEND_SOURCE = REPOSITORY / "backend" / "src" / "financial_ai_academy"
MODULES = BACKEND_SOURCE / "modules"
WEB_SOURCE = REPOSITORY / "apps" / "web" / "src"
WEB_PACKAGE = REPOSITORY / "apps" / "web" / "package.json"
WEB_DIST = REPOSITORY / "apps" / "web" / "dist"
SETUP_SCRIPT = REPOSITORY / "deployments" / "local" / "setup-dev.mjs"


def local_services() -> SimpleNamespace:
    content = SimpleNamespace(admit_lesson_package=MagicMock())
    curriculum = SimpleNamespace(
        create_lesson_placement=MagicMock(),
        create_assessment_placement=MagicMock(),
        register_lesson_opportunity=MagicMock(),
        rebuild_learning_opportunity_projection=MagicMock(),
    )
    return SimpleNamespace(
        assessment=object(),
        audit=object(),
        content=content,
        curriculum=curriculum,
        identity=object(),
        learner_model=object(),
        request_policy=object(),
    )


def build_local_app(
    services: SimpleNamespace,
    *,
    seed_approved_fixture: bool,
) -> tuple[FastAPI, MagicMock]:
    app = FastAPI()
    create_app = MagicMock(return_value=app)
    with tempfile.TemporaryDirectory() as temporary_directory:
        with (
            patch.object(
                serve,
                "build_application_services",
                return_value=services,
            ),
            patch.object(serve, "create_app", create_app),
        ):
            result = serve.build_local_app(
                postgres_dsn="postgresql://qualification-only",
                data_root=Path(temporary_directory) / "data",
                web_dist=Path(temporary_directory) / "web",
                host="127.0.0.1",
                port=8765,
                seed_approved_fixture=seed_approved_fixture,
                serve_static=False,
            )
    return result, create_app


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

        app, create_app = build_local_app(
            services,
            seed_approved_fixture=False,
        )

        self.assertIsInstance(app, FastAPI)
        services.content.admit_lesson_package.assert_not_called()
        services.curriculum.create_lesson_placement.assert_not_called()
        services.curriculum.create_assessment_placement.assert_not_called()
        services.curriculum.register_lesson_opportunity.assert_not_called()
        services.curriculum.rebuild_learning_opportunity_projection.assert_not_called()
        create_app.assert_called_once()

    def test_fixture_seed_uses_exact_public_operation_order(self) -> None:
        services = local_services()
        events: list[str] = []
        accepted = SimpleNamespace(
            package_id="intro-risk-return",
            package_version="1.1.0",
            package_digest="a" * 64,
        )
        placement = SimpleNamespace(placement_id=serve.PLACEMENT_ID)
        services.content.admit_lesson_package.side_effect = (
            lambda request: events.append("admit") or accepted
        )
        services.curriculum.create_lesson_placement.side_effect = (
            lambda request: events.append("lesson-placement") or placement
        )
        services.curriculum.create_assessment_placement.side_effect = (
            lambda request: events.append("assessment-placement")
        )
        services.curriculum.register_lesson_opportunity.side_effect = (
            lambda request: events.append("register-opportunity")
        )
        services.curriculum.rebuild_learning_opportunity_projection.side_effect = (
            lambda request: events.append("rebuild-projection")
        )
        app = FastAPI()
        create_app = MagicMock(
            side_effect=lambda api_services: events.append("create-app") or app
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            with (
                patch.object(
                    serve,
                    "build_application_services",
                    return_value=services,
                ),
                patch.object(serve, "create_app", create_app),
            ):
                result = serve.build_local_app(
                    postgres_dsn="postgresql://qualification-only",
                    data_root=Path(temporary_directory) / "data",
                    web_dist=Path(temporary_directory) / "web",
                    host="127.0.0.1",
                    port=8765,
                    seed_approved_fixture=True,
                    serve_static=False,
                )

        self.assertIs(result, app)
        self.assertEqual(
            events,
            [
                "admit",
                "lesson-placement",
                "assessment-placement",
                "register-opportunity",
                "rebuild-projection",
                "create-app",
            ],
        )

    def test_fixture_seed_failure_prevents_application_readiness(self) -> None:
        for failure in ("register", "rebuild"):
            with self.subTest(failure=failure):
                services = local_services()
                accepted = SimpleNamespace(
                    package_id="intro-risk-return",
                    package_version="1.1.0",
                    package_digest="a" * 64,
                )
                placement = SimpleNamespace(placement_id=serve.PLACEMENT_ID)
                services.content.admit_lesson_package.return_value = accepted
                services.curriculum.create_lesson_placement.return_value = placement
                failing_operation = (
                    services.curriculum.register_lesson_opportunity
                    if failure == "register"
                    else services.curriculum.rebuild_learning_opportunity_projection
                )
                failing_operation.side_effect = RuntimeError(
                    "deliberate fixture failure"
                )
                create_app = MagicMock(return_value=FastAPI())

                with tempfile.TemporaryDirectory() as temporary_directory:
                    with (
                        patch.object(
                            serve,
                            "build_application_services",
                            return_value=services,
                        ),
                        patch.object(serve, "create_app", create_app),
                    ):
                        with self.assertRaisesRegex(
                            RuntimeError,
                            "deliberate fixture failure",
                        ):
                            serve.build_local_app(
                                postgres_dsn="postgresql://qualification-only",
                                data_root=(
                                    Path(temporary_directory) / "data"
                                ),
                                web_dist=Path(temporary_directory) / "web",
                                host="127.0.0.1",
                                port=8765,
                                seed_approved_fixture=True,
                                serve_static=False,
                            )

                create_app.assert_not_called()
                if failure == "register":
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
