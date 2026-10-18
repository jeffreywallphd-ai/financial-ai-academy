"""Cumulative CAP-0026 contract and portability qualification."""

from __future__ import annotations

import ast
import json
from pathlib import Path
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


def _import_roots(relative: str) -> set[str]:
    tree = ast.parse((AUDIT / relative).read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


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


def test_shared_provenance_core_has_no_deployment_or_provider_import() -> None:
    """Local and future cloud profiles must reuse the same framework-free core."""

    core_sources = (
        "domain/provenance.py",
        "domain/cross_domain_provenance.py",
        "domain/accountable_history.py",
        "application/cross_domain_conformance.py",
    )
    deployment_or_effect_roots = {
        "azure",
        "boto3",
        "fastapi",
        "google",
        "httpx",
        "psycopg",
        "requests",
        "sqlalchemy",
    }

    for relative in core_sources:
        assert not (_import_roots(relative) & deployment_or_effect_roots), relative

    core_text = "\n".join(
        (AUDIT / relative).read_text(encoding="utf-8") for relative in core_sources
    )
    for policy_or_authority in (
        "tenant_id",
        "retention_until",
        "legal_hold",
        "provider_payload",
    ):
        assert policy_or_authority not in core_text
