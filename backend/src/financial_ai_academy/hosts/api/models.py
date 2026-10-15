"""Validated HTTP models generated into the reviewed OpenAPI snapshot."""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Literal, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from financial_ai_academy.modules.assessment.public import (
    KnowledgeCheckPresentation,
    KnowledgeCheckResult,
)
from financial_ai_academy.modules.content import public as content_public
from financial_ai_academy.modules.curriculum.public import LessonReadingResult
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
