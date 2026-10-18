"""Pure composition for the first bounded learning-lineage roots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json

from .models import AssessmentCompletionAuditRecord, AuditableAssessmentEvent
from .provenance import (
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
    build_lineage_view,
    validate_envelope,
)


class InvalidLearningLineage(ValueError):
    def __init__(self, reference: str) -> None:
        super().__init__("Learning lineage facts are inconsistent.")
        self.reference = reference


@dataclass(frozen=True, slots=True)
class ContentLineageFragment:
    lesson: ProvenanceEnvelope
    sources: tuple[ProvenanceEnvelope, ...]


def compose_published_lesson_lineage(
    fragment: ContentLineageFragment,
) -> LineageView:
    lesson, sources = _validate_content_fragment(fragment)
    nodes = (
        LineageNode(_node_id("lesson", lesson.resource.resource_id), lesson),
        *(
            LineageNode(_node_id("source", source.resource.resource_id), source)
            for source in sources
        ),
    )
    edges = tuple(
        LineageEdge(
            nodes[0].node_id,
            _node_id("source", source.resource.resource_id),
            RelationKind.PUBLISHED_FROM,
        )
        for source in sources
    )
    return build_lineage_view(
        root=LineageRoot(RootKind.PUBLISHED_LESSON, lesson.resource),
        nodes=nodes,
        edges=edges,
    )


def compose_knowledge_check_completion_lineage(
    *,
    event: AuditableAssessmentEvent,
    retained: AssessmentCompletionAuditRecord,
    occurrence: int,
    content: ContentLineageFragment,
) -> LineageView:
    lesson, source_envelopes = _validate_content_fragment(content)
    _validate_completion_correlation(event, retained, occurrence, lesson)

    event_reference = ResourceReference(
        owner_module=OwnerModule.ASSESSMENT,
        resource_kind=ResourceKind.KNOWLEDGE_CHECK_EVENT,
        resource_id=event.event_id,
        resource_version=None,
        occurrence=occurrence,
        integrity_digest=retained.integrity_digest,
        recorded_at=event.occurred_at,
        validation_status=ValidationStatus.VALIDATED,
    )
    evidence_reference = ResourceReference(
        owner_module=OwnerModule.ASSESSMENT,
        resource_kind=ResourceKind.COMPLETION_EVIDENCE,
        resource_id=event.evidence_id,
        resource_version=None,
        occurrence=occurrence,
        integrity_digest=_digest(
            {
                "kind": "completion_evidence",
                "evidence_id": event.evidence_id,
                "event_integrity_digest": retained.integrity_digest,
            }
        ),
        recorded_at=event.completed_at,
        validation_status=ValidationStatus.VALIDATED,
    )
    definition_reference = ResourceReference(
        owner_module=OwnerModule.ASSESSMENT,
        resource_kind=ResourceKind.ASSESSMENT_DEFINITION,
        resource_id=event.assessment_id,
        resource_version=event.assessment_version,
        occurrence=None,
        integrity_digest=event.definition_digest,
        recorded_at=event.occurred_at,
        validation_status=ValidationStatus.VALIDATED,
    )
    audit_reference = ResourceReference(
        owner_module=OwnerModule.AUDIT,
        resource_kind=ResourceKind.AUDIT_REFERENCE,
        resource_id=retained.audit_id,
        resource_version=None,
        occurrence=occurrence,
        integrity_digest=_digest(
            {
                "kind": "audit_reference",
                "audit_id": retained.audit_id,
                "event_integrity_digest": retained.integrity_digest,
                "recorded_at": _timestamp(retained.recorded_at),
            }
        ),
        recorded_at=retained.recorded_at,
        validation_status=ValidationStatus.VALIDATED,
    )

    evidence = validate_envelope(
        ProvenanceEnvelope(
            "1.0.0",
            evidence_reference,
            "assessment.knowledge-check",
            "1.0.0",
            (
                ProvenanceSource(RelationKind.PRODUCED, event_reference),
                ProvenanceSource(RelationKind.RECORDED_AS, audit_reference),
            ),
        )
    )
    event_envelope = validate_envelope(
        ProvenanceEnvelope(
            "1.0.0",
            event_reference,
            "assessment.knowledge-check",
            event.event_version,
            (ProvenanceSource(RelationKind.DEFINED_BY, definition_reference),),
        )
    )
    definition = validate_envelope(
        ProvenanceEnvelope(
            "1.0.0",
            definition_reference,
            "assessment.definition",
            "1.0.0",
            (ProvenanceSource(RelationKind.DEFINED_BY, lesson.resource),),
        )
    )
    audit = validate_envelope(
        ProvenanceEnvelope(
            "1.0.0",
            audit_reference,
            "audit.reconciliation",
            "1.0.0",
            (),
        )
    )

    nodes = (
        LineageNode(_node_id("evidence", event.evidence_id), evidence),
        LineageNode(_node_id("event", event.event_id), event_envelope),
        LineageNode(_node_id("audit", retained.audit_id), audit),
        LineageNode(_node_id("definition", event.assessment_id), definition),
        LineageNode(_node_id("lesson", lesson.resource.resource_id), lesson),
        *(
            LineageNode(_node_id("source", source.resource.resource_id), source)
            for source in source_envelopes
        ),
    )
    edges = (
        LineageEdge(nodes[0].node_id, nodes[1].node_id, RelationKind.PRODUCED),
        LineageEdge(nodes[0].node_id, nodes[2].node_id, RelationKind.RECORDED_AS),
        LineageEdge(nodes[1].node_id, nodes[3].node_id, RelationKind.DEFINED_BY),
        LineageEdge(nodes[3].node_id, nodes[4].node_id, RelationKind.DEFINED_BY),
        *(
            LineageEdge(
                nodes[4].node_id,
                _node_id("source", source.resource.resource_id),
                RelationKind.PUBLISHED_FROM,
            )
            for source in source_envelopes
        ),
    )
    return build_lineage_view(
        root=LineageRoot(RootKind.KNOWLEDGE_CHECK_COMPLETION, evidence_reference),
        nodes=nodes,
        edges=edges,
    )


def _validate_content_fragment(
    fragment: ContentLineageFragment,
) -> tuple[ProvenanceEnvelope, tuple[ProvenanceEnvelope, ...]]:
    lesson = validate_envelope(fragment.lesson)
    sources = tuple(validate_envelope(source) for source in fragment.sources)
    if lesson.resource.resource_kind is not ResourceKind.PUBLISHED_LESSON:
        raise InvalidLearningLineage("lesson.resource_kind")
    declared = {
        source.reference
        for source in lesson.sources
        if source.relation is RelationKind.PUBLISHED_FROM
    }
    actual = {source.resource for source in sources}
    if len(actual) != len(sources) or declared != actual:
        raise InvalidLearningLineage("lesson.sources")
    return lesson, tuple(sorted(sources, key=lambda item: item.resource.resource_id))


def _validate_completion_correlation(
    event: AuditableAssessmentEvent,
    retained: AssessmentCompletionAuditRecord,
    occurrence: int,
    lesson: ProvenanceEnvelope,
) -> None:
    if occurrence < 1:
        raise InvalidLearningLineage("occurrence")
    pairs = (
        (retained.event_id, event.event_id),
        (retained.evidence_id, event.evidence_id),
        (retained.attempt_id, event.attempt_id),
        (retained.actor_id, event.learner_id),
        (retained.placement_id, event.placement_id),
        (retained.package_id, event.package_id),
        (retained.package_version, event.package_version),
        (retained.package_digest, event.package_digest),
        (retained.assessment_id, event.assessment_id),
        (retained.assessment_version, event.assessment_version),
        (retained.definition_digest, event.definition_digest),
        (retained.occurred_at, event.occurred_at),
        (lesson.resource.resource_id, event.package_id),
        (lesson.resource.resource_version, event.package_version),
        (lesson.resource.integrity_digest, event.package_digest),
    )
    if any(left != right for left, right in pairs):
        raise InvalidLearningLineage("completion_correlation")


def _node_id(kind: str, resource_id: str) -> str:
    digest = hashlib.sha256(resource_id.encode("utf-8")).hexdigest()[:24]
    return f"{kind}.{digest}"


def _digest(value: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


__all__ = [
    "ContentLineageFragment",
    "InvalidLearningLineage",
    "compose_knowledge_check_completion_lineage",
    "compose_published_lesson_lineage",
]
