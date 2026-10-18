"""Provider-neutral provenance envelopes and bounded lineage values."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import re
import unicodedata


_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,79}$")
_DIGEST = re.compile(r"^[a-f0-9]{64}$")
_MAX_DEPTH = 12


class InvalidProvenance(ValueError):
    def __init__(self, reference: str) -> None:
        super().__init__("Provenance record is inconsistent.")
        self.reference = reference


class OwnerModule(StrEnum):
    CONTENT = "content"
    ASSESSMENT = "assessment"
    AUDIT = "audit"


class ResourceKind(StrEnum):
    EDUCATIONAL_SOURCE = "educational_source"
    PUBLISHED_LESSON = "published_lesson"
    ASSESSMENT_DEFINITION = "assessment_definition"
    KNOWLEDGE_CHECK_EVENT = "knowledge_check_event"
    COMPLETION_EVIDENCE = "completion_evidence"
    AUDIT_REFERENCE = "audit_reference"


_OWNER_KINDS = {
    OwnerModule.CONTENT: {
        ResourceKind.EDUCATIONAL_SOURCE,
        ResourceKind.PUBLISHED_LESSON,
    },
    OwnerModule.ASSESSMENT: {
        ResourceKind.ASSESSMENT_DEFINITION,
        ResourceKind.KNOWLEDGE_CHECK_EVENT,
        ResourceKind.COMPLETION_EVIDENCE,
    },
    OwnerModule.AUDIT: {ResourceKind.AUDIT_REFERENCE},
}

_VERSIONED_KINDS = {
    ResourceKind.EDUCATIONAL_SOURCE,
    ResourceKind.PUBLISHED_LESSON,
    ResourceKind.ASSESSMENT_DEFINITION,
}
_OCCURRENCE_KINDS = {
    ResourceKind.KNOWLEDGE_CHECK_EVENT,
    ResourceKind.COMPLETION_EVIDENCE,
    ResourceKind.AUDIT_REFERENCE,
}


class ValidationStatus(StrEnum):
    VALIDATED = "validated"
    INCOMPLETE = "incomplete"


class RelationKind(StrEnum):
    PUBLISHED_FROM = "published_from"
    DEFINED_BY = "defined_by"
    PRODUCED = "produced"
    RECORDED_AS = "recorded_as"


class RootKind(StrEnum):
    PUBLISHED_LESSON = "published_lesson"
    KNOWLEDGE_CHECK_COMPLETION = "knowledge_check_completion"


class IncompleteReason(StrEnum):
    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"
    REDACTED = "redacted"


@dataclass(frozen=True, slots=True)
class ResourceReference:
    owner_module: OwnerModule
    resource_kind: ResourceKind
    resource_id: str
    resource_version: str | None
    occurrence: int | None
    integrity_digest: str
    recorded_at: datetime
    validation_status: ValidationStatus


@dataclass(frozen=True, slots=True)
class ProvenanceSource:
    relation: RelationKind
    reference: ResourceReference


@dataclass(frozen=True, slots=True)
class ProvenanceEnvelope:
    schema_version: str
    resource: ResourceReference
    producer_id: str
    producer_version: str
    sources: tuple[ProvenanceSource, ...]


@dataclass(frozen=True, slots=True)
class LineageRoot:
    root_kind: RootKind
    resource: ResourceReference


@dataclass(frozen=True, slots=True)
class LineageNode:
    node_id: str
    envelope: ProvenanceEnvelope


@dataclass(frozen=True, slots=True)
class LineageEdge:
    source_node_id: str
    target_node_id: str
    relation: RelationKind


@dataclass(frozen=True, slots=True)
class IncompleteLink:
    source_node_id: str
    relation: RelationKind
    target_owner_module: OwnerModule
    target_resource_kind: ResourceKind
    target_resource_id: str
    reason: IncompleteReason


@dataclass(frozen=True, slots=True)
class LineageView:
    schema_version: str
    root: LineageRoot
    nodes: tuple[LineageNode, ...]
    edges: tuple[LineageEdge, ...]
    incomplete_links: tuple[IncompleteLink, ...]
    truncated: bool
    view_digest: str


def validate_envelope(value: ProvenanceEnvelope) -> ProvenanceEnvelope:
    if value.schema_version != "1.0.0":
        raise InvalidProvenance("schema_version")
    _validate_reference(value.resource, "resource")
    if not _valid_identifier(value.producer_id):
        raise InvalidProvenance("producer_id")
    if (
        not isinstance(value.producer_version, str)
        or _VERSION.fullmatch(value.producer_version) is None
    ):
        raise InvalidProvenance("producer_version")
    if not isinstance(value.sources, tuple) or len(value.sources) > 20:
        raise InvalidProvenance("sources")
    keys: set[tuple[str, ...]] = set()
    for index, source in enumerate(value.sources):
        if not isinstance(source.relation, RelationKind):
            raise InvalidProvenance(f"sources.{index}.relation")
        _validate_reference(source.reference, f"sources.{index}.reference")
        key = (source.relation.value, *_reference_key(source.reference))
        if key in keys or source.reference == value.resource:
            raise InvalidProvenance(f"sources.{index}")
        keys.add(key)
    return replace(value, sources=tuple(sorted(value.sources, key=_source_key)))


def validate_identifier(value: object, reference: str) -> str:
    if not _valid_identifier(value):
        raise InvalidProvenance(reference)
    assert isinstance(value, str)
    return value


def build_lineage_view(
    *,
    root: LineageRoot,
    nodes: tuple[LineageNode, ...],
    edges: tuple[LineageEdge, ...],
    incomplete_links: tuple[IncompleteLink, ...] = (),
    truncated: bool = False,
) -> LineageView:
    provisional = LineageView(
        schema_version="1.0.0",
        root=root,
        nodes=nodes,
        edges=edges,
        incomplete_links=incomplete_links,
        truncated=truncated,
        view_digest="0" * 64,
    )
    normalized = _normalize_view(provisional)
    return replace(normalized, view_digest=lineage_view_digest(normalized))


def validate_lineage_view(value: LineageView) -> LineageView:
    normalized = _normalize_view(value)
    if _DIGEST.fullmatch(value.view_digest) is None:
        raise InvalidProvenance("view_digest")
    if lineage_view_digest(normalized) != value.view_digest:
        raise InvalidProvenance("view_digest")
    return replace(normalized, view_digest=value.view_digest)


def lineage_view_digest(value: LineageView) -> str:
    return hashlib.sha256(
        json.dumps(
            lineage_view_payload(value, include_digest=False),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def envelope_payload(value: ProvenanceEnvelope) -> dict[str, object]:
    admitted = validate_envelope(value)
    return {
        "schema_version": admitted.schema_version,
        "resource": _reference_payload(admitted.resource),
        "producer": {
            "producer_id": admitted.producer_id,
            "producer_version": admitted.producer_version,
        },
        "sources": [
            {
                "relation": source.relation.value,
                "reference": _reference_payload(source.reference),
            }
            for source in admitted.sources
        ],
    }


def lineage_view_payload(
    value: LineageView, *, include_digest: bool = True
) -> dict[str, object]:
    normalized = validate_lineage_view(value) if include_digest else _normalize_view(value)
    result: dict[str, object] = {
        "schema_version": normalized.schema_version,
        "root": {
            "root_kind": normalized.root.root_kind.value,
            "resource": _reference_payload(normalized.root.resource),
        },
        "nodes": [
            {"node_id": node.node_id, "envelope": envelope_payload(node.envelope)}
            for node in normalized.nodes
        ],
        "edges": [
            {
                "source_node_id": edge.source_node_id,
                "target_node_id": edge.target_node_id,
                "relation": edge.relation.value,
            }
            for edge in normalized.edges
        ],
        "incomplete_links": [
            {
                "source_node_id": link.source_node_id,
                "relation": link.relation.value,
                "target_owner_module": link.target_owner_module.value,
                "target_resource_kind": link.target_resource_kind.value,
                "target_resource_id": link.target_resource_id,
                "reason": link.reason.value,
            }
            for link in normalized.incomplete_links
        ],
        "truncated": normalized.truncated,
    }
    if include_digest:
        result["view_digest"] = normalized.view_digest
    return result


def _normalize_view(value: LineageView) -> LineageView:
    if value.schema_version != "1.0.0":
        raise InvalidProvenance("schema_version")
    if not isinstance(value.root.root_kind, RootKind):
        raise InvalidProvenance("root.root_kind")
    _validate_reference(value.root.resource, "root.resource")
    expected_kind = {
        RootKind.PUBLISHED_LESSON: ResourceKind.PUBLISHED_LESSON,
        RootKind.KNOWLEDGE_CHECK_COMPLETION: ResourceKind.COMPLETION_EVIDENCE,
    }[value.root.root_kind]
    if value.root.resource.resource_kind is not expected_kind:
        raise InvalidProvenance("root.root_kind")
    if not isinstance(value.nodes, tuple) or not isinstance(value.edges, tuple):
        raise InvalidProvenance("lineage_collections")
    if not isinstance(value.incomplete_links, tuple):
        raise InvalidProvenance("incomplete_links")
    if not 1 <= len(value.nodes) <= 64 or len(value.edges) > 128:
        raise InvalidProvenance("lineage_bounds")
    if len(value.incomplete_links) > 32:
        raise InvalidProvenance("incomplete_links")
    if not isinstance(value.truncated, bool):
        raise InvalidProvenance("truncated")
    nodes: list[LineageNode] = []
    node_ids: set[str] = set()
    references: set[tuple[str, ...]] = set()
    exact_identities: dict[tuple[str, ...], str] = {}
    root_node_id: str | None = None
    for index, node in enumerate(value.nodes):
        if (
            not isinstance(node.node_id, str)
            or not _valid_identifier(node.node_id)
            or node.node_id in node_ids
        ):
            raise InvalidProvenance(f"nodes.{index}.node_id")
        envelope = validate_envelope(node.envelope)
        reference = _reference_key(envelope.resource)
        if reference in references:
            raise InvalidProvenance(f"nodes.{index}.resource")
        exact_identity = _exact_identity_key(envelope.resource)
        prior_digest = exact_identities.get(exact_identity)
        if prior_digest is not None and prior_digest != envelope.resource.integrity_digest:
            raise InvalidProvenance(f"nodes.{index}.resource_conflict")
        node_ids.add(node.node_id)
        references.add(reference)
        exact_identities[exact_identity] = envelope.resource.integrity_digest
        nodes.append(replace(node, envelope=envelope))
        if envelope.resource == value.root.resource:
            root_node_id = node.node_id
    if root_node_id is None:
        raise InvalidProvenance("root.resource")
    nodes_by_id = {node.node_id: node for node in nodes}
    edge_keys: set[tuple[str, str, str]] = set()
    represented_sources: set[tuple[str, ...]] = set()
    for index, edge in enumerate(value.edges):
        if (
            not isinstance(edge.source_node_id, str)
            or not isinstance(edge.target_node_id, str)
            or not isinstance(edge.relation, RelationKind)
        ):
            raise InvalidProvenance(f"edges.{index}.relation")
        key = (edge.source_node_id, edge.target_node_id, edge.relation.value)
        if (
            edge.source_node_id not in node_ids
            or edge.target_node_id not in node_ids
            or edge.source_node_id == edge.target_node_id
            or key in edge_keys
        ):
            raise InvalidProvenance(f"edges.{index}")
        source = nodes_by_id[edge.source_node_id]
        target = nodes_by_id[edge.target_node_id]
        matching_sources = [
            item
            for item in source.envelope.sources
            if (
                item.relation is edge.relation
                and item.reference == target.envelope.resource
            )
        ]
        if (
            len(matching_sources) != 1
            or matching_sources[0].reference.validation_status
            is not ValidationStatus.VALIDATED
        ):
            raise InvalidProvenance(f"edges.{index}.source_reference")
        represented_sources.add(
            (
                edge.source_node_id,
                edge.relation.value,
                *_reference_key(matching_sources[0].reference),
            )
        )
        edge_keys.add(key)
    _reject_cycle(node_ids, value.edges)
    depths = _validate_reachability(root_node_id, node_ids, value.edges)
    incomplete_keys: set[tuple[str, ...]] = set()
    represented_incomplete_sources: set[tuple[str, ...]] = set()
    for index, link in enumerate(value.incomplete_links):
        if (
            not isinstance(link.source_node_id, str)
            or link.source_node_id not in node_ids
            or not isinstance(link.relation, RelationKind)
            or not isinstance(link.target_owner_module, OwnerModule)
            or not isinstance(link.target_resource_kind, ResourceKind)
            or link.target_resource_kind not in _OWNER_KINDS[link.target_owner_module]
            or not isinstance(link.target_resource_id, str)
            or not _valid_identifier(link.target_resource_id)
            or not isinstance(link.reason, IncompleteReason)
        ):
            raise InvalidProvenance(f"incomplete_links.{index}")
        key = (
            link.source_node_id,
            link.relation.value,
            link.target_owner_module.value,
            link.target_resource_kind.value,
            link.target_resource_id,
        )
        if key in incomplete_keys:
            raise InvalidProvenance(f"incomplete_links.{index}")
        if any(
            edge.source_node_id == link.source_node_id
            and edge.relation is link.relation
            and nodes_by_id[edge.target_node_id].envelope.resource.owner_module
            is link.target_owner_module
            and nodes_by_id[edge.target_node_id].envelope.resource.resource_kind
            is link.target_resource_kind
            and nodes_by_id[edge.target_node_id].envelope.resource.resource_id
            == link.target_resource_id
            for edge in value.edges
        ):
            raise InvalidProvenance(f"incomplete_links.{index}")
        source = nodes_by_id[link.source_node_id]
        matching_sources = [
            item
            for item in source.envelope.sources
            if item.relation is link.relation
            and item.reference.owner_module is link.target_owner_module
            and item.reference.resource_kind is link.target_resource_kind
            and item.reference.resource_id == link.target_resource_id
            and item.reference.validation_status is ValidationStatus.INCOMPLETE
        ]
        if len(matching_sources) != 1:
            raise InvalidProvenance(f"incomplete_links.{index}.source_reference")
        source_key = (
            link.source_node_id,
            link.relation.value,
            *_reference_key(matching_sources[0].reference),
        )
        if source_key in represented_sources or source_key in represented_incomplete_sources:
            raise InvalidProvenance(f"incomplete_links.{index}.source_reference")
        represented_incomplete_sources.add(source_key)
        incomplete_keys.add(key)
    for node in nodes:
        for source in node.envelope.sources:
            source_key = (
                node.node_id,
                source.relation.value,
                *_reference_key(source.reference),
            )
            expected = (
                represented_sources
                if source.reference.validation_status is ValidationStatus.VALIDATED
                else represented_incomplete_sources
            )
            if source_key not in expected:
                raise InvalidProvenance(f"nodes.{node.node_id}.sources")
    return replace(
        value,
        nodes=tuple(
            sorted(nodes, key=lambda node: (depths[node.node_id], *_node_key(node)))
        ),
        edges=tuple(
            sorted(
                value.edges,
                key=lambda edge: (
                    depths[edge.source_node_id],
                    depths[edge.target_node_id],
                    *_edge_key(edge),
                ),
            )
        ),
        incomplete_links=tuple(
            sorted(
                value.incomplete_links,
                key=lambda link: (depths[link.source_node_id], *_incomplete_key(link)),
            )
        ),
    )


def _validate_reference(value: ResourceReference, reference: str) -> None:
    if (
        not isinstance(value.owner_module, OwnerModule)
        or not isinstance(value.resource_kind, ResourceKind)
        or value.resource_kind not in _OWNER_KINDS[value.owner_module]
    ):
        raise InvalidProvenance(f"{reference}.owner_kind")
    if not _valid_identifier(value.resource_id):
        raise InvalidProvenance(f"{reference}.resource_id")
    if value.resource_kind in _VERSIONED_KINDS:
        if (
            not isinstance(value.resource_version, str)
            or _VERSION.fullmatch(value.resource_version) is None
            or value.occurrence is not None
        ):
            raise InvalidProvenance(f"{reference}.exact_identity")
    elif value.resource_kind in _OCCURRENCE_KINDS:
        if (
            not isinstance(value.occurrence, int)
            or isinstance(value.occurrence, bool)
            or value.occurrence < 1
            or value.resource_version is not None
        ):
            raise InvalidProvenance(f"{reference}.exact_identity")
    else:
        raise InvalidProvenance(f"{reference}.exact_identity")
    if (
        not isinstance(value.integrity_digest, str)
        or _DIGEST.fullmatch(value.integrity_digest) is None
    ):
        raise InvalidProvenance(f"{reference}.integrity_digest")
    if (
        not isinstance(value.recorded_at, datetime)
        or value.recorded_at.tzinfo is None
        or value.recorded_at.utcoffset() is None
    ):
        raise InvalidProvenance(f"{reference}.recorded_at")
    if not isinstance(value.validation_status, ValidationStatus):
        raise InvalidProvenance(f"{reference}.validation_status")


def _reject_cycle(node_ids: set[str], edges: tuple[LineageEdge, ...]) -> None:
    outgoing = {node_id: [] for node_id in node_ids}
    for edge in edges:
        outgoing[edge.source_node_id].append(edge.target_node_id)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise InvalidProvenance("edges.cycle")
        if node_id in visited:
            return
        visiting.add(node_id)
        for target in outgoing[node_id]:
            visit(target)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in sorted(node_ids):
        visit(node_id)


def _valid_identifier(value: object) -> bool:
    if not isinstance(value, str) or not 1 <= len(value) <= 128:
        return False
    if not value[0].isalnum():
        return False
    return all(
        character.isprintable()
        and not character.isspace()
        and not unicodedata.category(character).startswith("C")
        and character not in "/\\?#"
        for character in value
    )


def _validate_reachability(
    root_node_id: str,
    node_ids: set[str],
    edges: tuple[LineageEdge, ...],
) -> dict[str, int]:
    outgoing = {node_id: [] for node_id in node_ids}
    for edge in edges:
        outgoing[edge.source_node_id].append(edge.target_node_id)
    shortest = {root_node_id: 0}
    pending = [root_node_id]
    while pending:
        source = pending.pop()
        for target in outgoing[source]:
            depth = shortest[source] + 1
            prior = shortest.get(target)
            if prior is None or depth < prior:
                shortest[target] = depth
                pending.append(target)
    if set(shortest) != node_ids:
        raise InvalidProvenance("lineage_disconnected")

    longest = {root_node_id: 0}
    pending = [root_node_id]
    while pending:
        source = pending.pop()
        for target in outgoing[source]:
            depth = longest[source] + 1
            if depth > _MAX_DEPTH:
                raise InvalidProvenance("lineage_depth")
            if depth > longest.get(target, -1):
                longest[target] = depth
                pending.append(target)
    return shortest


def _reference_payload(value: ResourceReference) -> dict[str, object]:
    result: dict[str, object] = {
        "owner_module": value.owner_module.value,
        "resource_kind": value.resource_kind.value,
        "resource_id": value.resource_id,
        "integrity_digest": value.integrity_digest,
        "recorded_at": value.recorded_at.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "validation_status": value.validation_status.value,
    }
    if value.resource_version is not None:
        result["resource_version"] = value.resource_version
    if value.occurrence is not None:
        result["occurrence"] = value.occurrence
    return result


def _reference_key(value: ResourceReference) -> tuple[str, ...]:
    return (
        value.owner_module.value,
        value.resource_kind.value,
        value.resource_id,
        value.resource_version or "",
        str(value.occurrence or 0),
        value.integrity_digest,
    )


def _exact_identity_key(value: ResourceReference) -> tuple[str, ...]:
    return (
        value.owner_module.value,
        value.resource_kind.value,
        value.resource_id,
        value.resource_version or "",
        str(value.occurrence or 0),
    )


def _source_key(value: ProvenanceSource) -> tuple[str, ...]:
    return (value.relation.value, *_reference_key(value.reference))


def _node_key(value: LineageNode) -> tuple[str, ...]:
    return (*_reference_key(value.envelope.resource), value.node_id)


def _edge_key(value: LineageEdge) -> tuple[str, str, str]:
    return (value.source_node_id, value.target_node_id, value.relation.value)


def _incomplete_key(value: IncompleteLink) -> tuple[str, ...]:
    return (
        value.source_node_id,
        value.relation.value,
        value.target_owner_module.value,
        value.target_resource_kind.value,
        value.target_resource_id,
        value.reason.value,
    )
