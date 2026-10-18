"""Cumulative CAP-0026 contract and portability qualification."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
CONTRACTS = ROOT / "contracts"
AUDIT = ROOT / "backend/src/financial_ai_academy/modules/audit"


def _load(relative: str) -> dict[str, Any]:
    return json.loads((CONTRACTS / relative).read_text(encoding="utf-8"))


def _property_names(value: object) -> set[str]:
    if isinstance(value, list):
        return set().union(*(_property_names(item) for item in value), set())
    if not isinstance(value, dict):
        return set()
    names = set(value.get("properties", {}))
    for child in value.values():
        names.update(_property_names(child))
    return names


def _object_schemas(value: object) -> tuple[dict[str, Any], ...]:
    if isinstance(value, list):
        return tuple(
            schema for item in value for schema in _object_schemas(item)
        )
    if not isinstance(value, dict):
        return ()
    current = (
        (value,)
        if value.get("type") == "object" and "properties" in value
        else ()
    )
    return current + tuple(
        schema for child in value.values() for schema in _object_schemas(child)
    )


def _shared_core_sources() -> tuple[Path, ...]:
    roots = (AUDIT / "domain", AUDIT / "application", AUDIT / "ports")
    return tuple(
        sorted(
            (source for root in roots for source in root.rglob("*.py")),
            key=lambda source: source.as_posix(),
        )
    ) + (AUDIT / "__init__.py", AUDIT / "public.py")


def _resolved_imports(source: Path) -> set[str]:
    relative = source.relative_to(AUDIT)
    package = ["financial_ai_academy", "modules", "audit"]
    package.extend(relative.parent.parts)
    tree = ast.parse(source.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if node.module:
                    imports.add(node.module)
                continue

            retained = len(package) - (node.level - 1)
            prefix = package[: max(retained, 0)]
            module = node.module.split(".") if node.module else []
            if module:
                imports.add(".".join(prefix + module))
            else:
                imports.update(".".join(prefix + [alias.name]) for alias in node.names)
    return imports


def _allowed_internal_prefixes(source: Path) -> tuple[str, ...]:
    relative = source.relative_to(AUDIT)
    base = "financial_ai_academy.modules.audit"
    if relative.parts[0] == "domain":
        return (f"{base}.domain",)
    if relative.parts[0] == "ports":
        return (f"{base}.domain", f"{base}.ports")
    if relative.parts[0] == "application":
        return (
            f"{base}.application",
            f"{base}.domain",
            f"{base}.ports",
            f"{base}.public",
        )
    return (f"{base}.domain", f"{base}.public")


def _is_allowed_internal(imported: str, prefixes: tuple[str, ...]) -> bool:
    return any(
        imported == prefix or imported.startswith(f"{prefix}.")
        for prefix in prefixes
    )


def test_lineage_history_and_owner_reference_bounds_stay_aligned() -> None:
    """History cannot widen the graph and v2 cannot widen one source envelope."""

    v1_envelope = _load("provenance/v1/envelope.schema.json")
    v1_view = _load("provenance/v1/lineage-view.schema.json")
    v2_envelope = _load("provenance/v2/envelope.schema.json")
    history = _load("accountable-history/v1/document.schema.json")

    assert v1_envelope["properties"]["sources"]["maxItems"] == (
        v2_envelope["properties"]["sources"]["maxItems"]
    )
    assert history["properties"]["entries"]["maxItems"] == (
        v1_view["properties"]["nodes"]["maxItems"]
    )
    assert history["properties"]["transformations"]["maxItems"] == (
        v1_view["properties"]["edges"]["maxItems"]
    )
    assert history["properties"]["missing_links"]["maxItems"] == (
        v1_view["properties"]["incomplete_links"]["maxItems"]
    )


def test_retention_seam_is_closed_and_policy_neutral() -> None:
    """Retention policy stays outside provenance identity and portable evidence."""

    schema_paths = (
        "provenance/v1/envelope.schema.json",
        "provenance/v1/lineage-request.schema.json",
        "provenance/v1/lineage-view.schema.json",
        "provenance/v2/envelope.schema.json",
        "accountable-history/v1/request.schema.json",
        "accountable-history/v1/document.schema.json",
        "accountable-history/v1/export.schema.json",
    )
    forbidden_policy_or_storage_fields = {
        "delete_after",
        "expires_at",
        "legal_hold",
        "provider_payload",
        "retained_export_id",
        "retention_class",
        "retention_policy",
        "storage_locator",
        "storage_path",
        "tenant_id",
    }

    for relative in schema_paths:
        schema = _load(relative)
        assert all(
            candidate.get("additionalProperties") is False
            for candidate in _object_schemas(schema)
        ), relative
        assert not (
            _property_names(schema) & forbidden_policy_or_storage_fields
        ), relative

    export = _load("accountable-history/v1/export.schema.json")
    assert set(export["properties"]) == {
        "schema_version",
        "media_type",
        "filename_stem",
        "exported_at",
        "document_digest",
        "document",
    }
    assert set(export["required"]) == set(export["properties"])


def test_shared_provenance_core_dependency_closure_is_adapter_neutral() -> None:
    """Every shared-core file stays inside its layer and pure standard library."""

    effect_roots = {
        "azure",
        "boto3",
        "fastapi",
        "google",
        "httpx",
        "os",
        "pathlib",
        "psycopg",
        "requests",
        "shutil",
        "socket",
        "sqlalchemy",
        "sqlite3",
        "tempfile",
        "urllib",
    }
    core_sources = _shared_core_sources()

    assert core_sources
    for source in core_sources:
        relative = source.relative_to(AUDIT).as_posix()
        allowed_internal = _allowed_internal_prefixes(source)
        for imported in _resolved_imports(source):
            root = imported.split(".", 1)[0]
            assert root not in effect_roots, (relative, imported)
            if imported.startswith("financial_ai_academy."):
                assert _is_allowed_internal(imported, allowed_internal), (
                    relative,
                    imported,
                )
            else:
                assert root in sys.stdlib_module_names, (relative, imported)
