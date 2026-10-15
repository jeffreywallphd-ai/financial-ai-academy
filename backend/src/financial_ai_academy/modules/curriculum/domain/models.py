"""Curriculum exact-version references, graph policy, and digest rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import re
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class PlacementReference:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str


class CurriculumActivityKind(StrEnum):
    LESSON = "lesson"
    ASSESSMENT = "assessment"


class CurriculumBranchKind(StrEnum):
    REQUIRED = "required"
    OPTIONAL = "optional"


class CurriculumRelationshipKind(StrEnum):
    OBJECTIVE_COMPETENCY = "objective_competency"
    ACTIVITY_DEVELOPS_COMPETENCY = "activity_develops_competency"
    ACTIVITY_ASSESSES_COMPETENCY = "activity_assesses_competency"
    COMPETENCY_PREREQUISITE = "competency_prerequisite"
    ACTIVITY_PREREQUISITE = "activity_prerequisite"


class CurriculumGraphErrorCode(StrEnum):
    INVALID_RECORD = "invalid_record"
    UNSUPPORTED_VERSION = "unsupported_version"
    DUPLICATE_IDENTITY = "duplicate_identity"
    DANGLING_REFERENCE = "dangling_reference"
    INVALID_RELATIONSHIP = "invalid_relationship"
    DUPLICATE_BRANCH_MEMBERSHIP = "duplicate_branch_membership"
    AMBIGUOUS_BRANCH_MEMBERSHIP = "ambiguous_branch_membership"
    PREREQUISITE_CYCLE = "prerequisite_cycle"
    REFERENCE_KIND_MISMATCH = "reference_kind_mismatch"
    GRAPH_DIGEST_MISMATCH = "graph_digest_mismatch"


class CurriculumGraphError(ValueError):
    """Bounded graph error without source payload or adapter details."""

    def __init__(
        self,
        code: CurriculumGraphErrorCode,
        message: str,
        *,
        reference: str = "curriculum-graph",
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code.value,
            "message": self.message,
            "reference": self.reference,
        }


@dataclass(frozen=True, slots=True)
class CurriculumObjective:
    objective_id: str
    title: str
    description: str


@dataclass(frozen=True, slots=True)
class CurriculumCompetency:
    competency_id: str
    title: str
    description: str


@dataclass(frozen=True, slots=True)
class LessonActivityReference:
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str


@dataclass(frozen=True, slots=True)
class AssessmentActivityReference:
    placement_id: str
    assessment_id: str
    assessment_version: str
    definition_digest: str


type CurriculumActivityReference = (
    LessonActivityReference | AssessmentActivityReference
)


@dataclass(frozen=True, slots=True)
class CurriculumActivity:
    activity_id: str
    title: str
    kind: CurriculumActivityKind
    reference: CurriculumActivityReference


@dataclass(frozen=True, slots=True)
class CurriculumBranch:
    branch_id: str
    title: str
    kind: CurriculumBranchKind
    activity_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CurriculumRelationship:
    relationship_id: str
    kind: CurriculumRelationshipKind
    source_id: str
    target_id: str


@dataclass(frozen=True, slots=True)
class CurriculumPresentationOrder:
    objective_ids: tuple[str, ...] = ()
    competency_ids: tuple[str, ...] = ()
    activity_ids: tuple[str, ...] = ()
    branch_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CurriculumGraph:
    schema_version: str
    curriculum_id: str
    curriculum_version: str
    title: str
    summary: str
    publication_state: str
    published_at: datetime
    source_references: tuple[str, ...]
    objectives: tuple[CurriculumObjective, ...]
    competencies: tuple[CurriculumCompetency, ...]
    activities: tuple[CurriculumActivity, ...]
    branches: tuple[CurriculumBranch, ...]
    relationships: tuple[CurriculumRelationship, ...]
    graph_digest: str
    presentation_order: CurriculumPresentationOrder | None = None


_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
_VERSION = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$"
)
_DIGEST = re.compile(r"^[a-f0-9]{64}$")
_SOURCE_REFERENCE = re.compile(r"^[a-z][a-z0-9+.-]{1,31}:[^\s]{1,255}$")


def _invalid(
    code: CurriculumGraphErrorCode,
    reference: str,
    message: str,
) -> None:
    raise CurriculumGraphError(code, message, reference=reference)


def _validate_identifier(value: str, reference: str) -> None:
    if _IDENTIFIER.fullmatch(value) is None:
        _invalid(
            CurriculumGraphErrorCode.INVALID_RECORD,
            reference,
            "Curriculum graph identifier is invalid.",
        )


def _validate_version(value: str, reference: str) -> None:
    if _VERSION.fullmatch(value) is None:
        _invalid(
            CurriculumGraphErrorCode.INVALID_RECORD,
            reference,
            "Curriculum graph version is invalid.",
        )


def _validate_digest(value: str, reference: str) -> None:
    if _DIGEST.fullmatch(value) is None:
        _invalid(
            CurriculumGraphErrorCode.INVALID_RECORD,
            reference,
            "Curriculum graph digest is invalid.",
        )


def _validate_text(
    value: str,
    reference: str,
    *,
    minimum: int,
    maximum: int,
) -> None:
    if not minimum <= len(value) <= maximum:
        _invalid(
            CurriculumGraphErrorCode.INVALID_RECORD,
            reference,
            "Curriculum graph text is invalid.",
        )


def _datetime_text(value: datetime) -> str:
    normalized = value.astimezone(timezone.utc).isoformat()
    return normalized.removesuffix("+00:00") + "Z"


def curriculum_graph_payload(graph: CurriculumGraph) -> dict[str, object]:
    """Return the portable JSON shape without interpreting eligibility."""

    presentation = graph.presentation_order
    value: dict[str, object] = {
        "schema_version": graph.schema_version,
        "curriculum_id": graph.curriculum_id,
        "curriculum_version": graph.curriculum_version,
        "title": graph.title,
        "summary": graph.summary,
        "publication_state": graph.publication_state,
        "published_at": _datetime_text(graph.published_at),
        "source_references": list(graph.source_references),
        "objectives": [
            {
                "objective_id": item.objective_id,
                "title": item.title,
                "description": item.description,
            }
            for item in graph.objectives
        ],
        "competencies": [
            {
                "competency_id": item.competency_id,
                "title": item.title,
                "description": item.description,
            }
            for item in graph.competencies
        ],
        "activities": [
            {
                "activity_id": item.activity_id,
                "title": item.title,
                "kind": item.kind.value,
                "reference": (
                    {
                        "reference_kind": "lesson_placement",
                        "placement_id": item.reference.placement_id,
                        "package_id": item.reference.package_id,
                        "package_version": item.reference.package_version,
                        "package_digest": item.reference.package_digest,
                    }
                    if isinstance(item.reference, LessonActivityReference)
                    else {
                        "reference_kind": "assessment_placement",
                        "placement_id": item.reference.placement_id,
                        "assessment_id": item.reference.assessment_id,
                        "assessment_version": item.reference.assessment_version,
                        "definition_digest": item.reference.definition_digest,
                    }
                ),
            }
            for item in graph.activities
        ],
        "branches": [
            {
                "branch_id": item.branch_id,
                "title": item.title,
                "kind": item.kind.value,
                "activity_ids": list(item.activity_ids),
            }
            for item in graph.branches
        ],
        "relationships": [
            {
                "relationship_id": item.relationship_id,
                "kind": item.kind.value,
                "source_id": item.source_id,
                "target_id": item.target_id,
            }
            for item in graph.relationships
        ],
        "graph_digest": graph.graph_digest,
    }
    if presentation is not None:
        order: dict[str, object] = {}
        if presentation.objective_ids:
            order["objective_ids"] = list(presentation.objective_ids)
        if presentation.competency_ids:
            order["competency_ids"] = list(presentation.competency_ids)
        if presentation.activity_ids:
            order["activity_ids"] = list(presentation.activity_ids)
        if presentation.branch_ids:
            order["branch_ids"] = list(presentation.branch_ids)
        value["presentation_order"] = order
    return value


def canonical_curriculum_graph_bytes(graph: CurriculumGraph) -> bytes:
    payload = curriculum_graph_payload(graph)
    payload.pop("graph_digest")
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def curriculum_graph_digest(graph: CurriculumGraph) -> str:
    return hashlib.sha256(canonical_curriculum_graph_bytes(graph)).hexdigest()


def _require_unique(values: Sequence[str], reference: str) -> None:
    if len(values) != len(set(values)):
        _invalid(
            CurriculumGraphErrorCode.DUPLICATE_IDENTITY,
            reference,
            "Curriculum graph identities must be unique.",
        )


def _has_cycle(nodes: set[str], edges: Sequence[tuple[str, str]]) -> bool:
    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for source, target in edges:
        outgoing[source].append(target)
        indegree[target] += 1
    ready = [node for node, count in indegree.items() if count == 0]
    visited = 0
    while ready:
        node = ready.pop()
        visited += 1
        for target in outgoing[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    return visited != len(nodes)


def validate_curriculum_graph(graph: CurriculumGraph) -> CurriculumGraph:
    """Validate immutable graph meaning without persistence or UI coupling."""

    if graph.schema_version != "1.0.0":
        _invalid(
            CurriculumGraphErrorCode.UNSUPPORTED_VERSION,
            "schema_version",
            "Curriculum graph version is unsupported.",
        )
    if graph.publication_state != "approved":
        _invalid(
            CurriculumGraphErrorCode.INVALID_RECORD,
            "publication_state",
            "Curriculum graph publication state is invalid.",
        )
    _validate_identifier(graph.curriculum_id, "curriculum_id")
    _validate_version(graph.curriculum_version, "curriculum_version")
    _validate_text(graph.title, "title", minimum=1, maximum=240)
    _validate_text(graph.summary, "summary", minimum=20, maximum=500)
    if graph.published_at.tzinfo is None:
        _invalid(
            CurriculumGraphErrorCode.INVALID_RECORD,
            "published_at",
            "Curriculum graph publication time is invalid.",
        )
    if not 1 <= len(graph.source_references) <= 20 or any(
        _SOURCE_REFERENCE.fullmatch(item) is None
        for item in graph.source_references
    ):
        _invalid(
            CurriculumGraphErrorCode.INVALID_RECORD,
            "source_references",
            "Curriculum graph source references are invalid.",
        )
    if len(graph.source_references) != len(set(graph.source_references)):
        _invalid(
            CurriculumGraphErrorCode.DUPLICATE_IDENTITY,
            "source_references",
            "Curriculum graph source references must be unique.",
        )
    collection_bounds = (
        (graph.objectives, 1, 100, "objectives"),
        (graph.competencies, 1, 200, "competencies"),
        (graph.activities, 1, 500, "activities"),
        (graph.branches, 0, 100, "branches"),
        (graph.relationships, 0, 2000, "relationships"),
    )
    for values, minimum, maximum, reference in collection_bounds:
        if not minimum <= len(values) <= maximum:
            _invalid(
                CurriculumGraphErrorCode.INVALID_RECORD,
                reference,
                "Curriculum graph collection size is invalid.",
            )

    objective_ids = {item.objective_id for item in graph.objectives}
    competency_ids = {item.competency_id for item in graph.competencies}
    activity_ids = {item.activity_id for item in graph.activities}
    branch_ids = {item.branch_id for item in graph.branches}
    identity_values = [
        *(item.objective_id for item in graph.objectives),
        *(item.competency_id for item in graph.competencies),
        *(item.activity_id for item in graph.activities),
        *(item.branch_id for item in graph.branches),
        *(item.relationship_id for item in graph.relationships),
    ]
    _require_unique(identity_values, "records")
    for identity in identity_values:
        _validate_identifier(identity, identity)

    for item in (*graph.objectives, *graph.competencies):
        _validate_text(item.title, "title", minimum=1, maximum=240)
        _validate_text(
            item.description,
            "description",
            minimum=1,
            maximum=1000,
        )
    for activity in graph.activities:
        _validate_text(activity.title, activity.activity_id, minimum=1, maximum=240)
        reference = activity.reference
        expected_lesson = activity.kind is CurriculumActivityKind.LESSON
        if expected_lesson != isinstance(reference, LessonActivityReference):
            _invalid(
                CurriculumGraphErrorCode.REFERENCE_KIND_MISMATCH,
                activity.activity_id,
                "Curriculum activity reference kind does not match.",
            )
        _validate_identifier(reference.placement_id, activity.activity_id)
        if isinstance(reference, LessonActivityReference):
            _validate_identifier(reference.package_id, activity.activity_id)
            _validate_version(reference.package_version, activity.activity_id)
            _validate_digest(reference.package_digest, activity.activity_id)
        else:
            _validate_identifier(reference.assessment_id, activity.activity_id)
            _validate_version(reference.assessment_version, activity.activity_id)
            _validate_digest(reference.definition_digest, activity.activity_id)

    membership_kinds: dict[str, set[CurriculumBranchKind]] = {}
    for branch in graph.branches:
        _validate_text(branch.title, branch.branch_id, minimum=1, maximum=240)
        if not 1 <= len(branch.activity_ids) <= 500:
            _invalid(
                CurriculumGraphErrorCode.INVALID_RECORD,
                branch.branch_id,
                "Curriculum branch membership is invalid.",
            )
        if len(branch.activity_ids) != len(set(branch.activity_ids)):
            _invalid(
                CurriculumGraphErrorCode.DUPLICATE_BRANCH_MEMBERSHIP,
                branch.branch_id,
                "Curriculum branch membership must be unique.",
            )
        for activity_id in branch.activity_ids:
            if activity_id not in activity_ids:
                _invalid(
                    CurriculumGraphErrorCode.DANGLING_REFERENCE,
                    branch.branch_id,
                    "Curriculum branch references an unknown activity.",
                )
            prior_kinds = membership_kinds.setdefault(activity_id, set())
            if prior_kinds and (
                branch.kind is CurriculumBranchKind.REQUIRED
                or CurriculumBranchKind.REQUIRED in prior_kinds
            ):
                _invalid(
                    CurriculumGraphErrorCode.AMBIGUOUS_BRANCH_MEMBERSHIP,
                    activity_id,
                    "Curriculum activity has ambiguous required branch meaning.",
                )
            prior_kinds.add(branch.kind)

    endpoint_sets = {
        CurriculumRelationshipKind.OBJECTIVE_COMPETENCY: (
            objective_ids,
            competency_ids,
        ),
        CurriculumRelationshipKind.ACTIVITY_DEVELOPS_COMPETENCY: (
            activity_ids,
            competency_ids,
        ),
        CurriculumRelationshipKind.ACTIVITY_ASSESSES_COMPETENCY: (
            activity_ids,
            competency_ids,
        ),
        CurriculumRelationshipKind.COMPETENCY_PREREQUISITE: (
            competency_ids,
            competency_ids,
        ),
        CurriculumRelationshipKind.ACTIVITY_PREREQUISITE: (
            activity_ids,
            activity_ids,
        ),
    }
    all_nodes = objective_ids | competency_ids | activity_ids | branch_ids
    competency_edges: list[tuple[str, str]] = []
    activity_edges: list[tuple[str, str]] = []
    activities_by_id = {item.activity_id: item for item in graph.activities}
    for relationship in graph.relationships:
        if (
            relationship.source_id not in all_nodes
            or relationship.target_id not in all_nodes
        ):
            _invalid(
                CurriculumGraphErrorCode.DANGLING_REFERENCE,
                relationship.relationship_id,
                "Curriculum relationship references an unknown node.",
            )
        sources, targets = endpoint_sets[relationship.kind]
        if (
            relationship.source_id not in sources
            or relationship.target_id not in targets
        ):
            _invalid(
                CurriculumGraphErrorCode.INVALID_RELATIONSHIP,
                relationship.relationship_id,
                "Curriculum relationship endpoint type is invalid.",
            )
        if (
            relationship.kind
            is CurriculumRelationshipKind.ACTIVITY_ASSESSES_COMPETENCY
            and activities_by_id[relationship.source_id].kind
            is not CurriculumActivityKind.ASSESSMENT
        ):
            _invalid(
                CurriculumGraphErrorCode.INVALID_RELATIONSHIP,
                relationship.relationship_id,
                "Only an assessment activity may assess a competency.",
            )
        if (
            relationship.kind
            is CurriculumRelationshipKind.COMPETENCY_PREREQUISITE
        ):
            competency_edges.append(
                (relationship.source_id, relationship.target_id)
            )
        if (
            relationship.kind
            is CurriculumRelationshipKind.ACTIVITY_PREREQUISITE
        ):
            activity_edges.append(
                (relationship.source_id, relationship.target_id)
            )
    if _has_cycle(competency_ids, competency_edges) or _has_cycle(
        activity_ids, activity_edges
    ):
        _invalid(
            CurriculumGraphErrorCode.PREREQUISITE_CYCLE,
            "relationships",
            "Curriculum prerequisite relationships must be acyclic.",
        )

    presentation = graph.presentation_order
    if presentation is not None:
        presentation_sets = (
            (presentation.objective_ids, objective_ids, "objective_ids"),
            (presentation.competency_ids, competency_ids, "competency_ids"),
            (presentation.activity_ids, activity_ids, "activity_ids"),
            (presentation.branch_ids, branch_ids, "branch_ids"),
        )
        for ordered, allowed, reference in presentation_sets:
            if len(ordered) != len(set(ordered)):
                _invalid(
                    CurriculumGraphErrorCode.DUPLICATE_IDENTITY,
                    reference,
                    "Curriculum presentation identities must be unique.",
                )
            if any(identity not in allowed for identity in ordered):
                _invalid(
                    CurriculumGraphErrorCode.DANGLING_REFERENCE,
                    reference,
                    "Curriculum presentation references an unknown record.",
                )

    _validate_digest(graph.graph_digest, "graph_digest")
    if curriculum_graph_digest(graph) != graph.graph_digest:
        _invalid(
            CurriculumGraphErrorCode.GRAPH_DIGEST_MISMATCH,
            "graph_digest",
            "Curriculum graph digest does not match.",
        )
    return graph


def _record(value: object, reference: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _invalid(
            CurriculumGraphErrorCode.INVALID_RECORD,
            reference,
            "Curriculum graph record is invalid.",
        )
    return value


def _text(value: object, reference: str) -> str:
    if not isinstance(value, str):
        _invalid(
            CurriculumGraphErrorCode.INVALID_RECORD,
            reference,
            "Curriculum graph text is invalid.",
        )
    return value


def _records(value: object, reference: str) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, list):
        _invalid(
            CurriculumGraphErrorCode.INVALID_RECORD,
            reference,
            "Curriculum graph collection is invalid.",
        )
    return tuple(_record(item, reference) for item in value)


def _texts(value: object, reference: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        _invalid(
            CurriculumGraphErrorCode.INVALID_RECORD,
            reference,
            "Curriculum graph collection is invalid.",
        )
    return tuple(_text(item, reference) for item in value)


def _exact_keys(
    value: Mapping[str, object],
    required: set[str],
    reference: str,
    *,
    optional: set[str] | None = None,
) -> None:
    optional_keys = optional or set()
    keys = {str(key) for key in value}
    if not required <= keys or not keys <= required | optional_keys:
        _invalid(
            CurriculumGraphErrorCode.INVALID_RECORD,
            reference,
            "Curriculum graph record fields are invalid.",
        )


def curriculum_graph_from_mapping(value: Mapping[str, object]) -> CurriculumGraph:
    """Convert the portable shape to public types and apply domain policy."""

    try:
        _exact_keys(
            value,
            {
                "schema_version",
                "curriculum_id",
                "curriculum_version",
                "title",
                "summary",
                "publication_state",
                "published_at",
                "source_references",
                "objectives",
                "competencies",
                "activities",
                "branches",
                "relationships",
                "graph_digest",
            },
            "curriculum-graph",
            optional={"presentation_order"},
        )
        schema_version = _text(value["schema_version"], "schema_version")
        if schema_version != "1.0.0":
            _invalid(
                CurriculumGraphErrorCode.UNSUPPORTED_VERSION,
                "schema_version",
                "Curriculum graph version is unsupported.",
            )
        published_text = _text(value["published_at"], "published_at")
        published_at = datetime.fromisoformat(
            published_text.removesuffix("Z") + (
                "+00:00" if published_text.endswith("Z") else ""
            )
        )
        objective_records = _records(value["objectives"], "objectives")
        for item in objective_records:
            _exact_keys(
                item,
                {"objective_id", "title", "description"},
                "objective",
            )
        objectives = tuple(
            CurriculumObjective(
                objective_id=_text(item["objective_id"], "objective_id"),
                title=_text(item["title"], "title"),
                description=_text(item["description"], "description"),
            )
            for item in objective_records
        )
        competency_records = _records(value["competencies"], "competencies")
        for item in competency_records:
            _exact_keys(
                item,
                {"competency_id", "title", "description"},
                "competency",
            )
        competencies = tuple(
            CurriculumCompetency(
                competency_id=_text(item["competency_id"], "competency_id"),
                title=_text(item["title"], "title"),
                description=_text(item["description"], "description"),
            )
            for item in competency_records
        )
        activities: list[CurriculumActivity] = []
        for item in _records(value["activities"], "activities"):
            _exact_keys(
                item,
                {"activity_id", "title", "kind", "reference"},
                "activity",
            )
            kind = CurriculumActivityKind(_text(item["kind"], "kind"))
            reference = _record(item["reference"], "reference")
            reference_kind = _text(
                reference["reference_kind"], "reference_kind"
            )
            if reference_kind == "lesson_placement":
                _exact_keys(
                    reference,
                    {
                        "reference_kind",
                        "placement_id",
                        "package_id",
                        "package_version",
                        "package_digest",
                    },
                    "lesson-reference",
                )
                activity_reference: CurriculumActivityReference = (
                    LessonActivityReference(
                        placement_id=_text(
                            reference["placement_id"], "placement_id"
                        ),
                        package_id=_text(reference["package_id"], "package_id"),
                        package_version=_text(
                            reference["package_version"], "package_version"
                        ),
                        package_digest=_text(
                            reference["package_digest"], "package_digest"
                        ),
                    )
                )
            elif reference_kind == "assessment_placement":
                _exact_keys(
                    reference,
                    {
                        "reference_kind",
                        "placement_id",
                        "assessment_id",
                        "assessment_version",
                        "definition_digest",
                    },
                    "assessment-reference",
                )
                activity_reference = AssessmentActivityReference(
                    placement_id=_text(
                        reference["placement_id"], "placement_id"
                    ),
                    assessment_id=_text(
                        reference["assessment_id"], "assessment_id"
                    ),
                    assessment_version=_text(
                        reference["assessment_version"],
                        "assessment_version",
                    ),
                    definition_digest=_text(
                        reference["definition_digest"], "definition_digest"
                    ),
                )
            else:
                _invalid(
                    CurriculumGraphErrorCode.INVALID_RECORD,
                    "reference_kind",
                    "Curriculum activity reference is invalid.",
                )
            activities.append(
                CurriculumActivity(
                    activity_id=_text(item["activity_id"], "activity_id"),
                    title=_text(item["title"], "title"),
                    kind=kind,
                    reference=activity_reference,
                )
            )
        branch_records = _records(value["branches"], "branches")
        for item in branch_records:
            _exact_keys(
                item,
                {"branch_id", "title", "kind", "activity_ids"},
                "branch",
            )
        branches = tuple(
            CurriculumBranch(
                branch_id=_text(item["branch_id"], "branch_id"),
                title=_text(item["title"], "title"),
                kind=CurriculumBranchKind(_text(item["kind"], "kind")),
                activity_ids=_texts(item["activity_ids"], "activity_ids"),
            )
            for item in branch_records
        )
        relationship_records = _records(
            value["relationships"], "relationships"
        )
        for item in relationship_records:
            _exact_keys(
                item,
                {"relationship_id", "kind", "source_id", "target_id"},
                "relationship",
            )
        relationships = tuple(
            CurriculumRelationship(
                relationship_id=_text(
                    item["relationship_id"], "relationship_id"
                ),
                kind=CurriculumRelationshipKind(
                    _text(item["kind"], "kind")
                ),
                source_id=_text(item["source_id"], "source_id"),
                target_id=_text(item["target_id"], "target_id"),
            )
            for item in relationship_records
        )
        raw_presentation = value.get("presentation_order")
        presentation = None
        if raw_presentation is not None:
            order = _record(raw_presentation, "presentation_order")
            _exact_keys(
                order,
                set(),
                "presentation_order",
                optional={
                    "objective_ids",
                    "competency_ids",
                    "activity_ids",
                    "branch_ids",
                },
            )
            presentation = CurriculumPresentationOrder(
                objective_ids=_texts(
                    order.get("objective_ids", []), "objective_ids"
                ),
                competency_ids=_texts(
                    order.get("competency_ids", []), "competency_ids"
                ),
                activity_ids=_texts(
                    order.get("activity_ids", []), "activity_ids"
                ),
                branch_ids=_texts(order.get("branch_ids", []), "branch_ids"),
            )
        graph = CurriculumGraph(
            schema_version=schema_version,
            curriculum_id=_text(value["curriculum_id"], "curriculum_id"),
            curriculum_version=_text(
                value["curriculum_version"], "curriculum_version"
            ),
            title=_text(value["title"], "title"),
            summary=_text(value["summary"], "summary"),
            publication_state=_text(
                value["publication_state"], "publication_state"
            ),
            published_at=published_at,
            source_references=_texts(
                value["source_references"], "source_references"
            ),
            objectives=objectives,
            competencies=competencies,
            activities=tuple(activities),
            branches=branches,
            relationships=relationships,
            graph_digest=_text(value["graph_digest"], "graph_digest"),
            presentation_order=presentation,
        )
    except CurriculumGraphError:
        raise
    except (KeyError, TypeError, ValueError) as error:
        raise CurriculumGraphError(
            CurriculumGraphErrorCode.INVALID_RECORD,
            "Curriculum graph record is invalid.",
        ) from error
    return validate_curriculum_graph(graph)


def canonical_discovery_bytes(value: Mapping[str, object]) -> bytes:
    """Serialize discovery meaning for stable source/generation digests."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def discovery_digest(value: Mapping[str, object]) -> str:
    return hashlib.sha256(canonical_discovery_bytes(value)).hexdigest()


def projection_generation(
    records: Sequence[Mapping[str, object]],
) -> str:
    return hashlib.sha256(
        json.dumps(
            list(records),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
