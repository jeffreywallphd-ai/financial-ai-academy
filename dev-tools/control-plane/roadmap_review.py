"""Project-neutral dynamic roadmap review projection."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping

from contracts import ControlError


CATALOG_SCHEMA = "capability-catalog-v1"
REVIEW_SCHEMA = "roadmap-review-v1"
KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LIST_RE = re.compile(r"^\s*(?:[-*+] |\d+[.)] )(.*)$")


def _failure(code: str, message: str, data: dict[str, Any], remediation: str) -> ControlError:
    return ControlError(code, message, data, [remediation])


def _safe_source(value: object) -> str:
    source = str(value or "").strip().replace("\\", "/")
    path = PurePosixPath(source)
    if not source or path.is_absolute() or ".." in path.parts:
        raise _failure(
            "roadmap.source-invalid",
            "Roadmap sources must be confined repository-relative paths.",
            {"source": source},
            "Use a repository-relative source from the project adapter allowlist.",
        )
    return source


def validate_catalog(value: object, *, expected_count: int | None = None) -> list[dict[str, Any]]:
    if not isinstance(value, dict) or value.get("schema_version") != CATALOG_SCHEMA:
        raise _failure(
            "roadmap.catalog-incompatible",
            "The capability catalog contract is missing or incompatible.",
            {"schema_version": value.get("schema_version") if isinstance(value, dict) else None},
            f"Provide a {CATALOG_SCHEMA} object.",
        )
    raw_items = value.get("capabilities")
    if not isinstance(raw_items, list):
        raise _failure(
            "roadmap.catalog-invalid",
            "The capability catalog must contain a capabilities array.",
            {},
            "Add the ordered capabilities array and retry.",
        )
    if expected_count is not None and len(raw_items) != expected_count:
        raise _failure(
            "roadmap.catalog-count",
            "The capability catalog contains an unexpected number of entries.",
            {"expected": expected_count, "actual": len(raw_items)},
            "Reconcile the machine catalog with the governed product catalog.",
        )

    normalized: list[dict[str, Any]] = []
    keys: set[str] = set()
    orders: set[int] = set()
    planning_ids: set[str] = set()
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            raise _failure(
                "roadmap.catalog-entry-invalid",
                "Every catalog entry must be an object.",
                {"index": index},
                "Replace the malformed entry with the documented fields.",
            )
        key = str(raw.get("key", "")).strip()
        title = str(raw.get("title", "")).strip()
        description = str(raw.get("description", "")).strip()
        order = raw.get("order")
        planning_id = raw.get("planning_id")
        planning_id = str(planning_id).strip() if planning_id is not None else None
        if not KEY_RE.fullmatch(key) or not title or not description or not isinstance(order, int) or order < 1:
            raise _failure(
                "roadmap.catalog-entry-invalid",
                "A catalog entry has an invalid key, order, title, or description.",
                {"index": index, "key": key, "order": order},
                "Provide a stable kebab-case key, positive order, title, and description.",
            )
        if key in keys or order in orders or (planning_id is not None and planning_id in planning_ids):
            raise _failure(
                "roadmap.catalog-duplicate",
                "Catalog keys, order positions, and formal planning mappings must be unique.",
                {"key": key, "order": order, "planning_id": planning_id},
                "Keep each candidate and formal capability mapping unique.",
            )
        keys.add(key)
        orders.add(order)
        if planning_id is not None:
            planning_ids.add(planning_id)
        normalized.append(
            {
                "key": key,
                "order": order,
                "title": title,
                "description": description,
                "planning_id": planning_id,
            }
        )
    expected_orders = set(range(1, len(normalized) + 1))
    if orders != expected_orders:
        raise _failure(
            "roadmap.catalog-order-invalid",
            "Catalog order positions must be contiguous and one-based.",
            {"orders": sorted(orders)},
            "Number candidates contiguously from one through the catalog count.",
        )
    return sorted(normalized, key=lambda item: item["order"])


def safe_document(text: str, *, source: str) -> dict[str, Any]:
    """Parse an inert Markdown subset without producing executable HTML."""

    safe_source = _safe_source(source)
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        try:
            end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
            lines = lines[end + 1 :]
        except StopIteration:
            lines = []

    blocks: list[dict[str, Any]] = []
    paragraph: list[str] = []
    code: list[str] = []
    in_code = False

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append({"type": "paragraph", "text": " ".join(item.strip() for item in paragraph)})
            paragraph.clear()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            if in_code:
                blocks.append({"type": "code", "text": "\n".join(code)})
                code.clear()
            in_code = not in_code
            continue
        if in_code:
            code.append(line)
            continue
        heading = HEADING_RE.match(line)
        if heading:
            flush_paragraph()
            blocks.append({"type": "heading", "level": len(heading.group(1)), "text": heading.group(2)})
            continue
        listed = LIST_RE.match(line)
        if listed:
            flush_paragraph()
            blocks.append({"type": "list-item", "text": listed.group(1).strip()})
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if not all(cell and set(cell) <= {"-", ":"} for cell in cells):
                blocks.append({"type": "table-row", "cells": cells})
            continue
        if not stripped:
            flush_paragraph()
            continue
        paragraph.append(line)
    flush_paragraph()
    if code:
        blocks.append({"type": "code", "text": "\n".join(code)})
    return {"source": safe_source, "blocks": blocks}


def _public_node(node: Mapping[str, Any], document: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "id": str(node.get("id", "")),
        "kind": str(node.get("kind", "")),
        "status": str(node.get("status", "unknown")),
        "title": str(node.get("title", node.get("id", ""))),
        "source": _safe_source(node.get("source")),
        "parent": str(node.get("parent")) if node.get("parent") else None,
        "dependencies": [
            {"target": str(item.get("target", "")), "type": str(item.get("type", "hard"))}
            for item in node.get("dependencies", [])
            if isinstance(item, dict) and item.get("target")
        ],
        "manifest": [str(item) for item in node.get("manifest", [])],
        "decision_gates": [str(item) for item in node.get("decision_gates", [])],
        "document": document,
    }


def _digest(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def build_projection(
    *,
    catalog: object,
    planning_nodes: Iterable[Mapping[str, Any]],
    documents: Mapping[str, Mapping[str, str]],
    graph: Mapping[str, Any],
    ordering: Mapping[str, Any],
    compatibility: Mapping[str, Any],
    expected_catalog_count: int | None = None,
) -> dict[str, Any]:
    catalog_items = validate_catalog(catalog, expected_count=expected_catalog_count)
    nodes = [dict(item) for item in planning_nodes]
    by_id = {str(item.get("id")): item for item in nodes}
    if len(by_id) != len(nodes):
        raise _failure(
            "roadmap.node-duplicate",
            "Planning node IDs must be unique.",
            {},
            "Resolve duplicate planning artifacts before projecting the roadmap.",
        )

    parsed_documents: dict[str, dict[str, Any]] = {}
    for node_id, value in documents.items():
        if not isinstance(value, Mapping):
            continue
        parsed_documents[str(node_id)] = safe_document(str(value.get("text", "")), source=str(value.get("source", "")))

    mapped_ids = {item["planning_id"] for item in catalog_items if item["planning_id"]}
    missing_mappings = sorted(item for item in mapped_ids if item not in by_id or str(by_id[item].get("kind")) != "capability")
    if missing_mappings:
        raise _failure(
            "roadmap.catalog-mapping-missing",
            "A catalog entry maps to a missing or non-capability planning artifact.",
            {"planning_ids": missing_mappings},
            "Correct the explicit mapping or restore the named CAP artifact.",
        )

    work_by_parent: dict[str, list[str]] = {}
    for node in nodes:
        if str(node.get("kind")) != "work" or not node.get("parent"):
            continue
        work_by_parent.setdefault(str(node["parent"]), []).append(str(node["id"]))
    for values in work_by_parent.values():
        values.sort()

    public_nodes = {
        node_id: _public_node(node, parsed_documents.get(node_id))
        for node_id, node in sorted(by_id.items())
    }
    diagnostics: list[dict[str, Any]] = []

    def capability_slices(capability: Mapping[str, Any]) -> list[dict[str, Any]]:
        slices: list[dict[str, Any]] = []
        for slice_id in capability["manifest"]:
            slice_node = public_nodes.get(slice_id)
            if slice_node is None:
                slices.append({"id": slice_id, "refined": False, "work": []})
                diagnostics.append(
                    {
                        "code": "roadmap.slice-not-refined",
                        "subject": slice_id,
                        "parent": capability["id"],
                        "blocking": False,
                    }
                )
                continue
            slices.append(
                {
                    **slice_node,
                    "refined": True,
                    "work": [public_nodes[work_id] for work_id in work_by_parent.get(slice_id, [])],
                }
            )
        return slices

    candidates: list[dict[str, Any]] = []
    for item in catalog_items:
        planning_id = item["planning_id"]
        capability = public_nodes.get(planning_id) if planning_id else None
        slices = capability_slices(capability) if capability else []
        candidates.append({**item, "planned": capability is not None, "capability": capability, "slices": slices})

    internal_capabilities = [
        {**public_nodes[node_id], "slices": capability_slices(public_nodes[node_id])}
        for node_id, node in sorted(by_id.items())
        if str(node.get("kind")) == "capability" and node_id not in mapped_ids
    ]
    payload: dict[str, Any] = {
        "schema_version": REVIEW_SCHEMA,
        "catalog_count": len(candidates),
        "candidates": candidates,
        "internal_capabilities": internal_capabilities,
        "ordering": dict(ordering),
        "compatibility": dict(compatibility),
        "graph_issues": list(graph.get("issues", [])),
        "diagnostics": diagnostics,
    }
    payload["source_fingerprint"] = _digest(payload)
    return payload
