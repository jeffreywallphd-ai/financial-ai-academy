from __future__ import annotations

import ast
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[3]
SOURCE = REPOSITORY / "backend/src/financial_ai_academy"
MODULES = SOURCE / "modules"


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def test_curriculum_imports_only_the_content_public_surface() -> None:
    prohibited: list[str] = []
    content_prefix = "financial_ai_academy.modules.content"
    for path in (MODULES / "curriculum").rglob("*.py"):
        for module in imported_modules(path):
            if module.startswith(content_prefix) and module != (
                "financial_ai_academy.modules.content.public"
            ):
                prohibited.append(f"{path.relative_to(REPOSITORY)}: {module}")
    assert prohibited == []


def test_cross_module_imports_use_only_public_surfaces() -> None:
    violations: list[str] = []
    module_names = {
        "assessment",
        "audit",
        "content",
        "curriculum",
        "identity",
        "learner_model",
    }
    prefix = "financial_ai_academy.modules."
    for owner in module_names:
        for path in (MODULES / owner).rglob("*.py"):
            for imported in imported_modules(path):
                if not imported.startswith(prefix):
                    continue
                segments = imported.split(".")
                if len(segments) < 4:
                    continue
                target = segments[2]
                if target == owner or target not in module_names:
                    continue
                if imported != f"{prefix}{target}.public":
                    violations.append(
                        f"{path.relative_to(REPOSITORY)}: {imported}"
                    )
    assert violations == []


def test_domain_layers_are_framework_and_adapter_free() -> None:
    forbidden_prefixes = {
        "financial_ai_academy.platform",
        "psycopg",
        "jsonschema",
        "markdown_it",
        "fastapi",
        "pydantic",
    }
    violations: list[str] = []
    for module_name in (
        "assessment",
        "audit",
        "content",
        "curriculum",
        "identity",
        "learner_model",
    ):
        for path in (MODULES / module_name / "domain").rglob("*.py"):
            for imported in imported_modules(path):
                if any(
                    imported == prefix or imported.startswith(prefix + ".")
                    for prefix in forbidden_prefixes
                ):
                    violations.append(
                        f"{path.relative_to(REPOSITORY)}: {imported}"
                    )
    assert violations == []


def test_repositories_query_only_their_own_module_schema() -> None:
    content_repository = (
        MODULES / "content/adapters/postgres_repository.py"
    ).read_text(encoding="utf-8")
    curriculum_repository = (
        MODULES / "curriculum/adapters/postgres_repository.py"
    ).read_text(encoding="utf-8")

    assert "curriculum." not in content_repository
    assert "content." not in curriculum_repository
    identity_repository = (
        MODULES / "identity/adapters/postgres_repository.py"
    ).read_text(encoding="utf-8")
    assert "content." not in identity_repository
    assert "curriculum." not in identity_repository
    assessment_repository = (
        MODULES / "assessment/adapters/postgres_repository.py"
    ).read_text(encoding="utf-8")
    assert "content." not in assessment_repository
    assert "curriculum." not in assessment_repository
    assert "identity." not in assessment_repository
    learner_repository = (
        MODULES / "learner_model/adapters/postgres_repository.py"
    ).read_text(encoding="utf-8")
    assert "assessment." not in learner_repository
    assert "content." not in learner_repository
    assert "curriculum." not in learner_repository
    assert "identity." not in learner_repository
    audit_repository = (
        MODULES / "audit/adapters/postgres_repository.py"
    ).read_text(encoding="utf-8")
    assert "assessment." not in audit_repository
    assert "content." not in audit_repository
    assert "curriculum." not in audit_repository
    assert "identity." not in audit_repository
    assert "learner_model." not in audit_repository


def test_curriculum_migration_has_no_cross_module_foreign_key() -> None:
    migration = (
        REPOSITORY
        / "backend/migrations/0002_curriculum_lesson_placements.up.sql"
    ).read_text(encoding="utf-8")
    normalized = migration.casefold()

    assert "references content." not in normalized

    assessment_reference = (
        REPOSITORY
        / "backend/migrations/curriculum/curriculum_0001_assessment_placements.up.sql"
    ).read_text(encoding="utf-8").casefold()
    assert "references content." not in assessment_reference
    assert "references assessment." not in assessment_reference

    assessment_evidence = (
        REPOSITORY
        / "backend/migrations/assessment/assessment_0001_knowledge_check_evidence.up.sql"
    ).read_text(encoding="utf-8").casefold()
    assert "references content." not in assessment_evidence
    assert "references curriculum." not in assessment_evidence
    assert "references identity." not in assessment_evidence

    learner_projection = (
        REPOSITORY
        / "backend/migrations/learner_model/learner_model_0001_completion_projection.up.sql"
    ).read_text(encoding="utf-8").casefold()
    assert "references assessment." not in learner_projection
    assert "references content." not in learner_projection
    assert "references curriculum." not in learner_projection
    assert "references identity." not in learner_projection

    audit_records = (
        REPOSITORY
        / "backend/migrations/audit/audit_0001_assessment_completion_records.up.sql"
    ).read_text(encoding="utf-8").casefold()
    assert "references assessment." not in audit_records
    assert "references content." not in audit_records
    assert "references curriculum." not in audit_records
    assert "references identity." not in audit_records
    assert "references learner_model." not in audit_records


def test_modules_have_public_application_and_port_seams() -> None:
    for module_name in (
        "assessment",
        "audit",
        "content",
        "curriculum",
        "identity",
        "learner_model",
    ):
        root = MODULES / module_name
        assert (root / "public.py").is_file()
        assert (root / "application").is_dir()
        assert (root / "domain").is_dir()
        assert (root / "ports").is_dir()
        assert (root / "adapters").is_dir()


def test_assessment_gateways_import_only_public_module_surfaces() -> None:
    for name, target in (
        ("content_gateway.py", "content"),
        ("curriculum_gateway.py", "curriculum"),
    ):
        path = MODULES / "assessment/adapters" / name
        imported = imported_modules(path)
        prefix = f"financial_ai_academy.modules.{target}"
        assert {
            item for item in imported if item.startswith(prefix)
        } == {f"{prefix}.public"}


def test_assessment_owns_completion_event_and_outbox_meaning() -> None:
    source = (
        MODULES / "assessment/application/service.py"
    ).read_text(encoding="utf-8")
    migration = (
        REPOSITORY
        / "backend/migrations/assessment/assessment_0001_knowledge_check_evidence.up.sql"
    ).read_text(encoding="utf-8")
    assert "assessment.knowledge-check.completed" in source
    assert "assessment.knowledge-check.completed" in migration
    for module_name in ("content", "curriculum", "identity"):
        module_source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (MODULES / module_name).rglob("*.py")
        )
        assert "assessment.knowledge-check.completed" not in module_source


def test_learner_model_consumes_only_the_assessment_public_surface() -> None:
    path = MODULES / "learner_model/adapters/assessment_gateway.py"
    imported = imported_modules(path)
    prefix = "financial_ai_academy.modules.assessment"
    assert {
        item for item in imported if item.startswith(prefix)
    } == {f"{prefix}.public"}


def test_audit_consumes_only_the_assessment_public_surface() -> None:
    path = MODULES / "audit/adapters/assessment_gateway.py"
    imported = imported_modules(path)
    prefix = "financial_ai_academy.modules.assessment"
    assert {
        item for item in imported if item.startswith(prefix)
    } == {f"{prefix}.public"}
