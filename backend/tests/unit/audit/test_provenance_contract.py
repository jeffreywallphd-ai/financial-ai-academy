from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.audit.adapters import (
    envelope_from_mapping,
    lineage_view_from_mapping,
    lineage_view_payload,
)
from financial_ai_academy.modules.audit.domain import (
    InvalidProvenance,
    LineageEdge,
    LineageNode,
    LineageRoot,
    OwnerModule,
    ProvenanceEnvelope,
    ProvenanceSource,
    RelationKind,
    ResourceKind,
    ResourceReference,
    RootKind,
    ValidationStatus,
    build_lineage_view,
    validate_envelope,
)


ROOT = Path(__file__).resolve().parents[4]
APPROVED = ROOT / "contracts/compatibility/provenance/v1/approved"
NOW = datetime(2026, 8, 5, 12, tzinfo=timezone.utc)


def _load(name: str) -> dict[str, object]:
    return json.loads((APPROVED / name).read_text(encoding="utf-8"))


def _reference(
    resource_id: str,
    *,
    owner: OwnerModule = OwnerModule.AUDIT,
    kind: ResourceKind = ResourceKind.AUDIT_REFERENCE,
    digest: str = "a" * 64,
    version: str | None = None,
    occurrence: int | None = 1,
) -> ResourceReference:
    return ResourceReference(
        owner_module=owner,
        resource_kind=kind,
        resource_id=resource_id,
        resource_version=version,
        occurrence=occurrence,
        integrity_digest=digest,
        recorded_at=NOW,
        validation_status=ValidationStatus.VALIDATED,
    )


def _envelope(
    resource: ResourceReference,
    *sources: tuple[RelationKind, ResourceReference],
) -> ProvenanceEnvelope:
    return ProvenanceEnvelope(
        schema_version="1.0.0",
        resource=resource,
        producer_id="audit.test",
        producer_version="1.0.0",
        sources=tuple(
            ProvenanceSource(relation=relation, reference=reference)
            for relation, reference in sources
        ),
    )


def test_approved_graph_is_root_distance_ordered_and_digest_bound() -> None:
    admitted = lineage_view_from_mapping(_load("lineage-view.json"))

    assert [node.node_id for node in admitted.nodes] == [
        "evidence",
        "event",
        "audit",
        "definition",
        "lesson",
        "source",
    ]
    assert lineage_view_from_mapping(lineage_view_payload(admitted)) == admitted


def test_unicode_and_incomplete_link_are_valid_without_fabricated_node() -> None:
    admitted = lineage_view_from_mapping(_load("incomplete-lineage-view.json"))

    assert admitted.root.resource.resource_id == "leçon-diversification-été"
    assert len(admitted.nodes) == 1
    assert admitted.incomplete_links[0].target_resource_id.endswith("été")


def test_every_declared_source_is_represented_exactly_once() -> None:
    admitted = lineage_view_from_mapping(_load("lineage-view.json"))
    evidence = next(node for node in admitted.nodes if node.node_id == "evidence")
    audit = next(node for node in admitted.nodes if node.node_id == "audit")
    extra_source = ProvenanceSource(
        RelationKind.DEFINED_BY,
        audit.envelope.resource,
    )
    changed_evidence = replace(
        evidence,
        envelope=replace(
            evidence.envelope,
            sources=(*evidence.envelope.sources, extra_source),
        ),
    )
    with pytest.raises(InvalidProvenance):
        build_lineage_view(
            root=admitted.root,
            nodes=tuple(
                changed_evidence if node.node_id == "evidence" else node
                for node in admitted.nodes
            ),
            edges=admitted.edges,
        )

    incomplete = lineage_view_from_mapping(_load("incomplete-lineage-view.json"))
    incomplete_root = incomplete.nodes[0]
    with pytest.raises(InvalidProvenance):
        build_lineage_view(
            root=incomplete.root,
            nodes=(
                replace(
                    incomplete_root,
                    envelope=replace(incomplete_root.envelope, sources=()),
                ),
            ),
            edges=(),
            incomplete_links=incomplete.incomplete_links,
        )
    with pytest.raises(InvalidProvenance):
        build_lineage_view(
            root=incomplete.root,
            nodes=incomplete.nodes,
            edges=(),
            incomplete_links=(
                replace(
                    incomplete.incomplete_links[0],
                    target_resource_id="fabricated-source",
                ),
            ),
        )


def test_changed_exact_identity_cycle_and_disconnected_graph_fail_closed() -> None:
    admitted = lineage_view_from_mapping(_load("lineage-view.json"))
    changed = replace(
        admitted.nodes[0],
        node_id="changed-evidence",
        envelope=replace(
            admitted.nodes[0].envelope,
            resource=replace(admitted.nodes[0].envelope.resource, integrity_digest="f" * 64),
        ),
    )
    with pytest.raises(InvalidProvenance, match="inconsistent"):
        build_lineage_view(
            root=admitted.root,
            nodes=(*admitted.nodes, changed),
            edges=admitted.edges,
        )

    source = next(node for node in admitted.nodes if node.node_id == "source")
    evidence = next(node for node in admitted.nodes if node.node_id == "evidence")
    cyclic_source = replace(
        source,
        envelope=replace(
            source.envelope,
            sources=(
                ProvenanceSource(RelationKind.RECORDED_AS, evidence.envelope.resource),
            ),
        ),
    )
    cyclic_nodes = tuple(cyclic_source if node.node_id == "source" else node for node in admitted.nodes)
    with pytest.raises(InvalidProvenance):
        build_lineage_view(
            root=admitted.root,
            nodes=cyclic_nodes,
            edges=(*admitted.edges, LineageEdge("source", "evidence", RelationKind.RECORDED_AS)),
        )

    with pytest.raises(InvalidProvenance):
        build_lineage_view(
            root=admitted.root,
            nodes=admitted.nodes,
            edges=admitted.edges[:-1],
        )


def test_graph_collection_and_depth_bounds_do_not_assume_one_fixture_shape() -> None:
    lesson = _reference(
        "root-lesson",
        owner=OwnerModule.CONTENT,
        kind=ResourceKind.PUBLISHED_LESSON,
        digest="1" * 64,
        version="1.0.0",
        occurrence=None,
    )
    audit_references = tuple(
        _reference(f"audit-{index}", digest=f"{index:x}"[-1] * 64)
        for index in range(1, 14)
    )
    nodes: list[LineageNode] = [
        LineageNode(
            "root",
            _envelope(lesson, (RelationKind.RECORDED_AS, audit_references[0])),
        )
    ]
    edges: list[LineageEdge] = []
    for index, reference in enumerate(audit_references):
        next_reference = (
            ((RelationKind.RECORDED_AS, audit_references[index + 1]),)
            if index + 1 < len(audit_references)
            else ()
        )
        nodes.append(LineageNode(f"audit-{index + 1}", _envelope(reference, *next_reference)))
        edges.append(
            LineageEdge(
                "root" if index == 0 else f"audit-{index}",
                f"audit-{index + 1}",
                RelationKind.RECORDED_AS,
            )
        )

    with pytest.raises(InvalidProvenance):
        build_lineage_view(
            root=LineageRoot(RootKind.PUBLISHED_LESSON, lesson),
            nodes=tuple(nodes),
            edges=tuple(edges),
        )

    with pytest.raises(InvalidProvenance):
        build_lineage_view(
            root=LineageRoot(RootKind.PUBLISHED_LESSON, lesson),
            nodes=tuple(nodes[:1] * 65),
            edges=(),
        )


def test_closed_adapter_and_domain_reject_private_keys_and_bad_types() -> None:
    envelope = _load("published-lesson-envelope.json")
    envelope["private_path"] = "C:/private/source.json"
    with pytest.raises(InvalidProvenance):
        envelope_from_mapping(envelope)

    valid = envelope_from_mapping(_load("published-lesson-envelope.json"))
    with pytest.raises(InvalidProvenance):
        validate_envelope(replace(valid, producer_id=7))  # type: ignore[arg-type]
    with pytest.raises(InvalidProvenance):
        validate_envelope(
            replace(
                valid,
                resource=replace(
                    valid.resource,
                    owner_module=OwnerModule.AUDIT,
                ),
            )
        )


def test_kind_specific_identity_timestamp_precision_and_identifiers_fail_closed() -> None:
    lesson_mapping = _load("published-lesson-envelope.json")
    lesson_mapping["resource"]["recorded_at"] = "2026-08-05T12:00:00.1234567Z"  # type: ignore[index]
    with pytest.raises(InvalidProvenance):
        envelope_from_mapping(lesson_mapping)

    lesson = envelope_from_mapping(_load("published-lesson-envelope.json"))
    with pytest.raises(InvalidProvenance):
        validate_envelope(
            replace(
                lesson,
                resource=replace(
                    lesson.resource,
                    resource_version=None,
                    occurrence=1,
                ),
            )
        )

    completion = envelope_from_mapping(_load("knowledge-check-envelope.json"))
    with pytest.raises(InvalidProvenance):
        validate_envelope(
            replace(
                completion,
                resource=replace(
                    completion.resource,
                    resource_version="1.0.0",
                    occurrence=None,
                ),
            )
        )

    for unsafe in ("audit.\x00test", "audit.\u200btest", "\u202etest", "🙂test"):
        with pytest.raises(InvalidProvenance):
            validate_envelope(replace(lesson, producer_id=unsafe))
