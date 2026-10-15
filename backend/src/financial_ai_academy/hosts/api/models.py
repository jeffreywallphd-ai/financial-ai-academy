"""Validated HTTP models generated into the reviewed OpenAPI snapshot."""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Literal, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from financial_ai_academy.modules.assessment.public import (
    KnowledgeCheckPresentation,
    KnowledgeCheckResult,
)
from financial_ai_academy.modules.content import public as content_public
from financial_ai_academy.modules.curriculum.public import (
    AppliedLearningOpportunityQuery,
    CurriculumGraph,
    LearningOpportunityBrowse,
    LearningOpportunityQueryPage,
    LearningOpportunityRecord,
    LessonReadingResult,
    curriculum_graph_payload,
)
from financial_ai_academy.modules.learner_model.public import (
    LessonCompletionView,
)


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ApiErrorEnvelope(ApiModel):
    error_version: Literal["1.0"] = "1.0"
    code: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=240)
    correlation_id: str = Field(min_length=36, max_length=36)


class SessionBootstrapRequestModel(ApiModel):
    limitation_acknowledged: Literal[True]


class SessionBootstrapResponseModel(ApiModel):
    status: Literal["ready"] = "ready"
    authentication_method: Literal["single_profile"] = "single_profile"
    expires_at: datetime


class InlineTextModel(ApiModel):
    kind: Literal["text"] = "text"
    value: str


class InlineCodeModel(ApiModel):
    kind: Literal["code"] = "code"
    value: str


class SoftBreakModel(ApiModel):
    kind: Literal["soft_break"] = "soft_break"


class HardBreakModel(ApiModel):
    kind: Literal["hard_break"] = "hard_break"


class EmphasisModel(ApiModel):
    kind: Literal["emphasis"] = "emphasis"
    children: list["InlineNodeModel"]


class StrongModel(ApiModel):
    kind: Literal["strong"] = "strong"
    children: list["InlineNodeModel"]


class SourceLinkModel(ApiModel):
    kind: Literal["source_link"] = "source_link"
    children: list["InlineNodeModel"]
    href: str
    source_id: str


class AssetImageModel(ApiModel):
    kind: Literal["asset_image"] = "asset_image"
    asset_id: str
    alt_text: str


InlineNodeModel = Annotated[
    Union[
        InlineTextModel,
        InlineCodeModel,
        SoftBreakModel,
        HardBreakModel,
        EmphasisModel,
        StrongModel,
        SourceLinkModel,
        AssetImageModel,
    ],
    Field(discriminator="kind"),
]


class HeadingModel(ApiModel):
    kind: Literal["heading"] = "heading"
    level: int = Field(ge=1, le=6)
    children: list[InlineNodeModel]


class ParagraphModel(ApiModel):
    kind: Literal["paragraph"] = "paragraph"
    children: list[InlineNodeModel]


class CodeBlockModel(ApiModel):
    kind: Literal["code_block"] = "code_block"
    code: str
    language: str | None


class ThematicBreakModel(ApiModel):
    kind: Literal["thematic_break"] = "thematic_break"


class ListItemModel(ApiModel):
    blocks: list["BodyNodeModel"]


class BulletListModel(ApiModel):
    kind: Literal["bullet_list"] = "bullet_list"
    items: list[ListItemModel]


class OrderedListModel(ApiModel):
    kind: Literal["ordered_list"] = "ordered_list"
    start: int = Field(ge=1)
    items: list[ListItemModel]


BodyNodeModel = Annotated[
    Union[
        HeadingModel,
        ParagraphModel,
        CodeBlockModel,
        ThematicBreakModel,
        BulletListModel,
        OrderedListModel,
    ],
    Field(discriminator="kind"),
]


class EducationalSourceModel(ApiModel):
    source_id: str
    title: str
    publisher: str
    locator: str
    reviewed_on: date
    license_note: str | None


class PassiveAssetModel(ApiModel):
    asset_id: str
    media_type: Literal["image/png", "image/jpeg", "image/webp"]
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    alt_text: str
    locator: str


class PublicationProvenanceModel(ApiModel):
    published_by: str
    published_at: datetime
    content_reviewed_on: date
    educational_use_notice: str


class LessonReadingResponseModel(ApiModel):
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    title: str
    objectives: list[str]
    body: list[BodyNodeModel]
    sources: list[EducationalSourceModel]
    assets: list[PassiveAssetModel]
    provenance: PublicationProvenanceModel


GraphIdentifier = Annotated[
    str,
    Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    ),
]
GraphVersion = Annotated[
    str,
    Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
            r"(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$"
        )
    ),
]
GraphDigest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]


class CurriculumObjectiveResponseModel(ApiModel):
    objective_id: GraphIdentifier
    title: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=1, max_length=1000)


class CurriculumCompetencyResponseModel(ApiModel):
    competency_id: GraphIdentifier
    title: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=1, max_length=1000)


class LessonActivityReferenceResponseModel(ApiModel):
    reference_kind: Literal["lesson_placement"]
    placement_id: GraphIdentifier
    package_id: GraphIdentifier
    package_version: GraphVersion
    package_digest: GraphDigest


class AssessmentActivityReferenceResponseModel(ApiModel):
    reference_kind: Literal["assessment_placement"]
    placement_id: GraphIdentifier
    assessment_id: GraphIdentifier
    assessment_version: GraphVersion
    definition_digest: GraphDigest


CurriculumActivityReferenceResponseModel = Annotated[
    Union[
        LessonActivityReferenceResponseModel,
        AssessmentActivityReferenceResponseModel,
    ],
    Field(discriminator="reference_kind"),
]


class CurriculumActivityResponseModel(ApiModel):
    activity_id: GraphIdentifier
    title: str = Field(min_length=1, max_length=240)
    kind: Literal["lesson", "assessment"]
    reference: CurriculumActivityReferenceResponseModel


class CurriculumBranchResponseModel(ApiModel):
    branch_id: GraphIdentifier
    title: str = Field(min_length=1, max_length=240)
    kind: Literal["required", "optional"]
    activity_ids: list[GraphIdentifier] = Field(
        min_length=1,
        max_length=500,
        json_schema_extra={"uniqueItems": True},
    )


class CurriculumRelationshipResponseModel(ApiModel):
    relationship_id: GraphIdentifier
    kind: Literal[
        "objective_competency",
        "activity_develops_competency",
        "activity_assesses_competency",
        "competency_prerequisite",
        "activity_prerequisite",
    ]
    source_id: GraphIdentifier
    target_id: GraphIdentifier


class CurriculumPresentationOrderResponseModel(ApiModel):
    objective_ids: list[GraphIdentifier] = Field(
        default_factory=list,
        max_length=100,
        json_schema_extra={"uniqueItems": True},
    )
    competency_ids: list[GraphIdentifier] = Field(
        default_factory=list,
        max_length=200,
        json_schema_extra={"uniqueItems": True},
    )
    activity_ids: list[GraphIdentifier] = Field(
        default_factory=list,
        max_length=500,
        json_schema_extra={"uniqueItems": True},
    )
    branch_ids: list[GraphIdentifier] = Field(
        default_factory=list,
        max_length=100,
        json_schema_extra={"uniqueItems": True},
    )


class CurriculumGraphResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    curriculum_id: GraphIdentifier
    curriculum_version: GraphVersion
    title: str = Field(min_length=1, max_length=240)
    summary: str = Field(min_length=20, max_length=500)
    publication_state: Literal["approved"]
    published_at: datetime
    source_references: list[str] = Field(
        min_length=1,
        max_length=20,
        json_schema_extra={"uniqueItems": True},
    )
    presentation_order: CurriculumPresentationOrderResponseModel | None = None
    objectives: list[CurriculumObjectiveResponseModel] = Field(
        min_length=1,
        max_length=100,
    )
    competencies: list[CurriculumCompetencyResponseModel] = Field(
        min_length=1,
        max_length=200,
    )
    activities: list[CurriculumActivityResponseModel] = Field(
        min_length=1,
        max_length=500,
    )
    branches: list[CurriculumBranchResponseModel] = Field(max_length=100)
    relationships: list[CurriculumRelationshipResponseModel] = Field(
        max_length=2000
    )
    graph_digest: GraphDigest


class DiscoveryProvenanceResponseModel(ApiModel):
    published_by: str = Field(min_length=1, max_length=160)
    published_at: datetime
    content_reviewed_on: date
    educational_use_notice: str = Field(min_length=1, max_length=500)


DiscoveryObjective = Annotated[str, Field(min_length=1, max_length=500)]
DiscoveryTopic = Annotated[
    str,
    Field(pattern=r"^[a-z0-9][a-z0-9-]{1,49}$"),
]


class LearningOpportunityResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    opportunity_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    placement_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    destination: str = Field(
        pattern=r"^/learn/placements/[a-z0-9][a-z0-9._-]{2,63}$",
    )
    kind: Literal["course", "lesson", "lab", "project"]
    title: str = Field(min_length=1, max_length=240)
    summary: str = Field(min_length=20, max_length=500)
    objectives: list[DiscoveryObjective] = Field(
        min_length=1,
        max_length=20,
        json_schema_extra={"uniqueItems": True},
    )
    topics: list[DiscoveryTopic] = Field(
        min_length=1,
        max_length=8,
        json_schema_extra={"uniqueItems": True},
    )
    level: Literal["introductory", "intermediate", "advanced"]
    estimated_minutes: int = Field(ge=1, le=1440)
    prerequisite_summary: str = Field(min_length=2, max_length=500)
    availability: Literal["available", "unavailable", "planned"]
    availability_reason: str = Field(min_length=10, max_length=500)
    package_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    package_version: str = Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
            r"(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$"
        )
    )
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    provenance: DiscoveryProvenanceResponseModel
    source_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    projected_at: datetime

    @field_validator("objectives", "topics")
    @classmethod
    def require_unique_values(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("Discovery list values must be unique.")
        return values


class LearningOpportunityBrowseResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    projection_generation: str = Field(pattern=r"^[a-f0-9]{64}$")
    projected_at: datetime
    records: list[LearningOpportunityResponseModel] = Field(max_length=500)


class AppliedLearningOpportunityQueryResponseModel(ApiModel):
    query: str | None = Field(min_length=1, max_length=100)
    prerequisite_query: str | None = Field(
        min_length=1,
        max_length=100,
    )
    topics: list[DiscoveryTopic] = Field(
        max_length=8,
        json_schema_extra={"uniqueItems": True},
    )
    levels: list[
        Literal["introductory", "intermediate", "advanced"]
    ] = Field(max_length=8, json_schema_extra={"uniqueItems": True})
    kinds: list[Literal["course", "lesson", "lab", "project"]] = Field(
        max_length=8,
        json_schema_extra={"uniqueItems": True},
    )
    availabilities: list[
        Literal["available", "unavailable", "planned"]
    ] = Field(max_length=8, json_schema_extra={"uniqueItems": True})
    minimum_minutes: int | None = Field(ge=1, le=1440)
    maximum_minutes: int | None = Field(ge=1, le=1440)
    sort: Literal[
        "catalog",
        "title",
        "duration_ascending",
        "duration_descending",
    ]
    page_size: int = Field(ge=1, le=50)

    @field_validator("topics", "levels", "kinds", "availabilities")
    @classmethod
    def require_unique_filters(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("Discovery query filters must be unique.")
        return values


class LearningOpportunityQueryPageResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    projection_generation: str = Field(pattern=r"^[a-f0-9]{64}$")
    projected_at: datetime
    applied_query: AppliedLearningOpportunityQueryResponseModel
    total_matches: int = Field(ge=0, le=500)
    records: list[LearningOpportunityResponseModel] = Field(max_length=50)
    next_cursor: str | None = Field(
        min_length=1,
        max_length=1024,
        pattern=r"^[A-Za-z0-9_-]+\.[a-f0-9]{64}$",
    )


class KnowledgeCheckOptionModel(ApiModel):
    option_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    label: str = Field(min_length=1, max_length=160)


class KnowledgeCheckPresentationResponseModel(ApiModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    placement_id: str
    package_id: str
    package_version: Literal["1.1.0"]
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    assessment_id: str
    assessment_version: Literal["1.0.0"]
    definition_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    item_type: Literal["single_select"]
    item_id: str
    item_version: Literal["1.0.0"]
    scoring_policy_id: Literal["single-select-exact-match"]
    scoring_policy_version: Literal["1.0.0"]
    prompt: str = Field(min_length=1, max_length=400)
    options: list[KnowledgeCheckOptionModel] = Field(
        min_length=2, max_length=6
    )


class KnowledgeCheckSubmissionRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    submission_id: UUID
    placement_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    package_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    package_version: Literal["1.1.0"]
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    assessment_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    assessment_version: Literal["1.0.0"]
    definition_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    item_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    item_version: Literal["1.0.0"]
    scoring_policy_id: Literal["single-select-exact-match"]
    scoring_policy_version: Literal["1.0.0"]
    selected_option_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )


class KnowledgeCheckFeedbackModel(ApiModel):
    feedback_id: str
    text: str = Field(min_length=1, max_length=400)


class KnowledgeCheckResultResponseModel(ApiModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    attempt_id: UUID
    evidence_id: UUID
    submission_id: UUID
    placement_id: str
    package_id: str
    package_version: Literal["1.1.0"]
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    assessment_id: str
    assessment_version: Literal["1.0.0"]
    definition_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    item_id: str
    item_version: Literal["1.0.0"]
    scoring_policy_id: Literal["single-select-exact-match"]
    scoring_policy_version: Literal["1.0.0"]
    score: int = Field(ge=0, le=1)
    max_score: Literal[1]
    correct: bool
    feedback: KnowledgeCheckFeedbackModel
    submitted_at: datetime


class LessonCompletionHistoryEntryModel(ApiModel):
    event_id: UUID
    attempt_id: UUID
    evidence_id: UUID
    package_id: str
    package_version: Literal["1.1.0"]
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    assessment_id: str
    assessment_version: Literal["1.0.0"]
    definition_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    item_id: str
    item_version: Literal["1.0.0"]
    scoring_policy_id: Literal["single-select-exact-match"]
    scoring_policy_version: Literal["1.0.0"]
    score: int = Field(ge=0, le=1)
    max_score: Literal[1]
    completed_at: datetime


class LessonCompletionResponseModel(ApiModel):
    projection_version: Literal["1.0.0"] = "1.0.0"
    placement_id: str
    completed: bool
    completion_meaning: Literal[
        "not_completed", "bounded_knowledge_check_completed"
    ]
    source_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    rebuilt_at: datetime
    history: list[LessonCompletionHistoryEntryModel]


class HealthResponseModel(ApiModel):
    status: Literal["ok", "ready", "not_ready"]


_MODEL_NAMESPACE = {
    "InlineNodeModel": InlineNodeModel,
    "BodyNodeModel": BodyNodeModel,
}
for _model in (
    EmphasisModel,
    StrongModel,
    SourceLinkModel,
    ListItemModel,
    BulletListModel,
    OrderedListModel,
    LessonReadingResponseModel,
):
    _model.model_rebuild(_types_namespace=_MODEL_NAMESPACE)


def lesson_response(
    reading: LessonReadingResult,
) -> LessonReadingResponseModel:
    return LessonReadingResponseModel(
        placement_id=reading.placement_id,
        package_id=reading.package_id,
        package_version=reading.package_version,
        package_digest=reading.package_digest,
        title=reading.title,
        objectives=list(reading.objectives),
        body=[_body_node(node) for node in reading.body],
        sources=[
            EducationalSourceModel(
                source_id=source.source_id,
                title=source.title,
                publisher=source.publisher,
                locator=source.locator,
                reviewed_on=source.reviewed_on,
                license_note=source.license_note,
            )
            for source in reading.sources
        ],
        assets=[
            PassiveAssetModel(
                asset_id=asset.asset_id,
                media_type=asset.media_type,
                sha256=asset.sha256,
                alt_text=asset.alt_text,
                locator=f"/api/v1/content/assets/{asset.asset_id}",
            )
            for asset in reading.assets
        ],
        provenance=PublicationProvenanceModel(
            published_by=reading.provenance.published_by,
            published_at=reading.provenance.published_at,
            content_reviewed_on=reading.provenance.content_reviewed_on,
            educational_use_notice=(
                reading.provenance.educational_use_notice
            ),
        ),
    )


def curriculum_graph_response(
    graph: CurriculumGraph,
) -> CurriculumGraphResponseModel:
    return CurriculumGraphResponseModel.model_validate(
        curriculum_graph_payload(graph)
    )


def learning_opportunity_browse_response(
    browse: LearningOpportunityBrowse,
) -> LearningOpportunityBrowseResponseModel:
    return LearningOpportunityBrowseResponseModel(
        schema_version=browse.schema_version,  # type: ignore[arg-type]
        projection_generation=browse.projection_generation,
        projected_at=browse.projected_at,
        records=[
            learning_opportunity_response(record)
            for record in browse.records
        ],
    )


def learning_opportunity_query_page_response(
    page: LearningOpportunityQueryPage,
) -> LearningOpportunityQueryPageResponseModel:
    return LearningOpportunityQueryPageResponseModel(
        schema_version=page.schema_version,  # type: ignore[arg-type]
        projection_generation=page.projection_generation,
        projected_at=page.projected_at,
        applied_query=applied_learning_opportunity_query_response(
            page.applied_query
        ),
        total_matches=page.total_matches,
        records=[
            learning_opportunity_response(record)
            for record in page.records
        ],
        next_cursor=page.next_cursor,
    )


def applied_learning_opportunity_query_response(
    query: AppliedLearningOpportunityQuery,
) -> AppliedLearningOpportunityQueryResponseModel:
    return AppliedLearningOpportunityQueryResponseModel(
        query=query.query,
        prerequisite_query=query.prerequisite_query,
        topics=list(query.topics),
        levels=[level.value for level in query.levels],  # type: ignore[list-item]
        kinds=[kind.value for kind in query.kinds],  # type: ignore[list-item]
        availabilities=[
            availability.value for availability in query.availabilities
        ],  # type: ignore[list-item]
        minimum_minutes=query.minimum_minutes,
        maximum_minutes=query.maximum_minutes,
        sort=query.sort.value,  # type: ignore[arg-type]
        page_size=query.page_size,
    )


def learning_opportunity_response(
    record: LearningOpportunityRecord,
) -> LearningOpportunityResponseModel:
    return LearningOpportunityResponseModel(
        schema_version=record.schema_version,  # type: ignore[arg-type]
        opportunity_id=record.opportunity_id,
        placement_id=record.placement_id,
        destination=record.destination,
        kind=record.kind.value,  # type: ignore[arg-type]
        title=record.title,
        summary=record.summary,
        objectives=list(record.objectives),
        topics=list(record.topics),
        level=record.level.value,  # type: ignore[arg-type]
        estimated_minutes=record.estimated_minutes,
        prerequisite_summary=record.prerequisite_summary,
        availability=record.availability.value,  # type: ignore[arg-type]
        availability_reason=record.availability_reason,
        package_id=record.package_id,
        package_version=record.package_version,
        package_digest=record.package_digest,
        provenance=DiscoveryProvenanceResponseModel(
            published_by=record.provenance.published_by,
            published_at=record.provenance.published_at,
            content_reviewed_on=record.provenance.content_reviewed_on,
            educational_use_notice=(
                record.provenance.educational_use_notice
            ),
        ),
        source_fingerprint=record.source_fingerprint,
        projected_at=record.projected_at,
    )


def knowledge_check_presentation_response(
    presentation: KnowledgeCheckPresentation,
) -> KnowledgeCheckPresentationResponseModel:
    return KnowledgeCheckPresentationResponseModel(
        placement_id=presentation.placement_id,
        package_id=presentation.package_id,
        package_version=presentation.package_version,  # type: ignore[arg-type]
        package_digest=presentation.package_digest,
        assessment_id=presentation.assessment_id,
        assessment_version=presentation.assessment_version,  # type: ignore[arg-type]
        definition_digest=presentation.definition_digest,
        item_type=presentation.item_type,  # type: ignore[arg-type]
        item_id=presentation.item_id,
        item_version=presentation.item_version,  # type: ignore[arg-type]
        scoring_policy_id=presentation.scoring_policy_id,  # type: ignore[arg-type]
        scoring_policy_version=presentation.scoring_policy_version,  # type: ignore[arg-type]
        prompt=presentation.prompt,
        options=[
            KnowledgeCheckOptionModel(
                option_id=option.option_id,
                label=option.label,
            )
            for option in presentation.options
        ],
    )


def knowledge_check_result_response(
    result: KnowledgeCheckResult,
) -> KnowledgeCheckResultResponseModel:
    return KnowledgeCheckResultResponseModel(
        attempt_id=result.attempt_id,
        evidence_id=result.evidence_id,
        submission_id=result.submission_id,
        placement_id=result.placement_id,
        package_id=result.package_id,
        package_version=result.package_version,  # type: ignore[arg-type]
        package_digest=result.package_digest,
        assessment_id=result.assessment_id,
        assessment_version=result.assessment_version,  # type: ignore[arg-type]
        definition_digest=result.definition_digest,
        item_id=result.item_id,
        item_version=result.item_version,  # type: ignore[arg-type]
        scoring_policy_id=result.scoring_policy_id,  # type: ignore[arg-type]
        scoring_policy_version=result.scoring_policy_version,  # type: ignore[arg-type]
        score=result.score,
        max_score=result.max_score,  # type: ignore[arg-type]
        correct=result.correct,
        feedback=KnowledgeCheckFeedbackModel(
            feedback_id=result.feedback.feedback_id,
            text=result.feedback.text,
        ),
        submitted_at=result.submitted_at,
    )


def lesson_completion_response(
    view: LessonCompletionView,
) -> LessonCompletionResponseModel:
    return LessonCompletionResponseModel(
        placement_id=view.placement_id,
        completed=view.completed,
        completion_meaning=view.completion_meaning,  # type: ignore[arg-type]
        source_digest=view.source_digest,
        rebuilt_at=view.rebuilt_at,
        history=[
            LessonCompletionHistoryEntryModel(
                event_id=entry.event_id,
                attempt_id=entry.attempt_id,
                evidence_id=entry.evidence_id,
                package_id=entry.package_id,
                package_version=entry.package_version,  # type: ignore[arg-type]
                package_digest=entry.package_digest,
                assessment_id=entry.assessment_id,
                assessment_version=entry.assessment_version,  # type: ignore[arg-type]
                definition_digest=entry.definition_digest,
                item_id=entry.item_id,
                item_version=entry.item_version,  # type: ignore[arg-type]
                scoring_policy_id=entry.scoring_policy_id,  # type: ignore[arg-type]
                scoring_policy_version=entry.scoring_policy_version,  # type: ignore[arg-type]
                score=entry.score,
                max_score=entry.max_score,  # type: ignore[arg-type]
                completed_at=entry.completed_at,
            )
            for entry in view.history
        ],
    )


def _inline_node(node: content_public.InlineNode) -> InlineNodeModel:
    if isinstance(node, content_public.InlineText):
        return InlineTextModel(value=node.value)
    if isinstance(node, content_public.InlineCode):
        return InlineCodeModel(value=node.value)
    if isinstance(node, content_public.SoftBreak):
        return SoftBreakModel()
    if isinstance(node, content_public.HardBreak):
        return HardBreakModel()
    if isinstance(node, content_public.Emphasis):
        return EmphasisModel(
            children=[_inline_node(child) for child in node.children]
        )
    if isinstance(node, content_public.Strong):
        return StrongModel(
            children=[_inline_node(child) for child in node.children]
        )
    if isinstance(node, content_public.SourceLink):
        return SourceLinkModel(
            children=[_inline_node(child) for child in node.children],
            href=node.href,
            source_id=node.source_id,
        )
    if isinstance(node, content_public.AssetImage):
        return AssetImageModel(
            asset_id=node.asset_id, alt_text=node.alt_text
        )
    raise TypeError("Unsupported public inline node.")


def _body_node(node: content_public.BodyNode) -> BodyNodeModel:
    if isinstance(node, content_public.Heading):
        return HeadingModel(
            level=node.level,
            children=[_inline_node(child) for child in node.children],
        )
    if isinstance(node, content_public.Paragraph):
        return ParagraphModel(
            children=[_inline_node(child) for child in node.children]
        )
    if isinstance(node, content_public.CodeBlock):
        return CodeBlockModel(code=node.code, language=node.language)
    if isinstance(node, content_public.ThematicBreak):
        return ThematicBreakModel()
    if isinstance(node, content_public.BulletList):
        return BulletListModel(
            items=[
                ListItemModel(
                    blocks=[_body_node(block) for block in item.blocks]
                )
                for item in node.items
            ]
        )
    if isinstance(node, content_public.OrderedList):
        return OrderedListModel(
            start=node.start,
            items=[
                ListItemModel(
                    blocks=[_body_node(block) for block in item.blocks]
                )
                for item in node.items
            ],
        )
    raise TypeError("Unsupported public body node.")
