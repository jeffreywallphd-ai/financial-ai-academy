from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]
BACKEND_SOURCE = REPOSITORY / "backend" / "src" / "financial_ai_academy"
MODULES = BACKEND_SOURCE / "modules"
WEB_SOURCE = REPOSITORY / "apps" / "web" / "src"
WEB_PACKAGE = REPOSITORY / "apps" / "web" / "package.json"
WEB_DIST = REPOSITORY / "apps" / "web" / "dist"
SETUP_SCRIPT = REPOSITORY / "deployments" / "local" / "setup-dev.mjs"


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
