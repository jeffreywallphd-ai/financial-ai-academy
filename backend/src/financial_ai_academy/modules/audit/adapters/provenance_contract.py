"""Strict mapping adapter for provenance-envelope v1."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any, Mapping

from ..domain import (
    IncompleteLink,
    IncompleteReason,
    InvalidProvenance,
    LineageEdge,
    LineageNode,
    LineageRoot,
    LineageView,
    OwnerModule,
    ProvenanceEnvelope,
    ProvenanceSource,
    RelationKind,
    ResourceKind,
    ResourceReference,
    RootKind,
    ValidationStatus,
    envelope_payload,
    lineage_view_payload,
    validate_envelope,
    validate_lineage_view,
)


_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$"
)


def _reject(reference: str) -> None:
    raise InvalidProvenance(reference)


def _mapping(value: object, reference: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        _reject(reference)
    return value


def _exact_keys(
    value: Mapping[str, Any],
    required: set[str],
    optional: set[str],
    reference: str,
) -> None:
    keys = set(value)
    if not required <= keys or not keys <= required | optional:
        _reject(reference)


def _sequence(value: object, reference: str) -> tuple[Any, ...]:
    if not isinstance(value, list):
        _reject(reference)
    return tuple(value)


def _enum(enum_type, value: object, reference: str):
    try:
        return enum_type(value)
    except (TypeError, ValueError):
        _reject(reference)


def _timestamp(value: object, reference: str) -> datetime:
    if not isinstance(value, str) or _TIMESTAMP.fullmatch(value) is None:
        _reject(reference)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _reject(reference)


def reference_from_mapping(value: object, reference: str) -> ResourceReference:
    item = _mapping(value, reference)
    _exact_keys(
        item,
        {
            "owner_module",
            "resource_kind",
            "resource_id",
            "integrity_digest",
            "recorded_at",
            "validation_status",
        },
        {"resource_version", "occurrence"},
        reference,
    )
    return ResourceReference(
        owner_module=_enum(OwnerModule, item["owner_module"], f"{reference}.owner_module"),
        resource_kind=_enum(ResourceKind, item["resource_kind"], f"{reference}.resource_kind"),
        resource_id=item["resource_id"],
        resource_version=item.get("resource_version"),
        occurrence=item.get("occurrence"),
        integrity_digest=item["integrity_digest"],
        recorded_at=_timestamp(item["recorded_at"], f"{reference}.recorded_at"),
        validation_status=_enum(
            ValidationStatus,
            item["validation_status"],
            f"{reference}.validation_status",
        ),
    )


def envelope_from_mapping(value: Mapping[str, Any]) -> ProvenanceEnvelope:
    item = _mapping(value, "envelope")
    _exact_keys(
        item,
        {"schema_version", "resource", "producer", "sources"},
        set(),
        "envelope",
    )
    producer = _mapping(item["producer"], "producer")
    _exact_keys(
        producer,
        {"producer_id", "producer_version"},
        set(),
        "producer",
    )
    sources: list[ProvenanceSource] = []
    for index, value in enumerate(_sequence(item["sources"], "sources")):
        source = _mapping(value, f"sources.{index}")
        _exact_keys(
            source,
            {"relation", "reference"},
            set(),
            f"sources.{index}",
        )
        sources.append(
            ProvenanceSource(
                relation=_enum(
                    RelationKind,
                    source["relation"],
                    f"sources.{index}.relation",
                ),
                reference=reference_from_mapping(
                    source["reference"], f"sources.{index}.reference"
                ),
            )
        )
    return validate_envelope(
        ProvenanceEnvelope(
            schema_version=item["schema_version"],
            resource=reference_from_mapping(item["resource"], "resource"),
            producer_id=producer["producer_id"],
            producer_version=producer["producer_version"],
            sources=tuple(sources),
        )
    )


def lineage_view_from_mapping(value: Mapping[str, Any]) -> LineageView:
    item = _mapping(value, "lineage_view")
    _exact_keys(
        item,
        {
            "schema_version",
            "root",
            "nodes",
            "edges",
            "incomplete_links",
            "truncated",
            "view_digest",
        },
        set(),
        "lineage_view",
    )
    root_value = _mapping(item["root"], "root")
    _exact_keys(root_value, {"root_kind", "resource"}, set(), "root")
    root = LineageRoot(
        root_kind=_enum(RootKind, root_value["root_kind"], "root.root_kind"),
        resource=reference_from_mapping(root_value["resource"], "root.resource"),
    )
    nodes: list[LineageNode] = []
    for index, value in enumerate(_sequence(item["nodes"], "nodes")):
        node = _mapping(value, f"nodes.{index}")
        _exact_keys(node, {"node_id", "envelope"}, set(), f"nodes.{index}")
        nodes.append(
            LineageNode(
                node_id=node["node_id"],
                envelope=envelope_from_mapping(node["envelope"]),
            )
        )
    edges: list[LineageEdge] = []
    for index, value in enumerate(_sequence(item["edges"], "edges")):
        edge = _mapping(value, f"edges.{index}")
        _exact_keys(
            edge,
            {"source_node_id", "target_node_id", "relation"},
            set(),
            f"edges.{index}",
        )
        edges.append(
            LineageEdge(
                source_node_id=edge["source_node_id"],
                target_node_id=edge["target_node_id"],
                relation=_enum(
                    RelationKind,
                    edge["relation"],
                    f"edges.{index}.relation",
                ),
            )
        )
    incomplete: list[IncompleteLink] = []
    for index, value in enumerate(
        _sequence(item["incomplete_links"], "incomplete_links")
    ):
        link = _mapping(value, f"incomplete_links.{index}")
        _exact_keys(
            link,
            {
                "source_node_id",
                "relation",
                "target_owner_module",
                "target_resource_kind",
                "target_resource_id",
                "reason",
            },
            set(),
            f"incomplete_links.{index}",
        )
        incomplete.append(
            IncompleteLink(
                source_node_id=link["source_node_id"],
                relation=_enum(
                    RelationKind,
                    link["relation"],
                    f"incomplete_links.{index}.relation",
                ),
                target_owner_module=_enum(
                    OwnerModule,
                    link["target_owner_module"],
                    f"incomplete_links.{index}.target_owner_module",
                ),
                target_resource_kind=_enum(
                    ResourceKind,
                    link["target_resource_kind"],
                    f"incomplete_links.{index}.target_resource_kind",
                ),
                target_resource_id=link["target_resource_id"],
                reason=_enum(
                    IncompleteReason,
                    link["reason"],
                    f"incomplete_links.{index}.reason",
                ),
            )
        )
    if not isinstance(item["truncated"], bool):
        _reject("truncated")
    return validate_lineage_view(
        LineageView(
            schema_version=item["schema_version"],
            root=root,
            nodes=tuple(nodes),
            edges=tuple(edges),
            incomplete_links=tuple(incomplete),
            truncated=item["truncated"],
            view_digest=item["view_digest"],
        )
    )


__all__ = [
    "envelope_from_mapping",
    "envelope_payload",
    "lineage_view_from_mapping",
    "lineage_view_payload",
    "reference_from_mapping",
]
