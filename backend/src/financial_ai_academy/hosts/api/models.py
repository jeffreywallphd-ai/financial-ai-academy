"""Validated HTTP models generated into the reviewed OpenAPI snapshot."""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from financial_ai_academy.modules.content import public as content_public
from financial_ai_academy.modules.curriculum.public import LessonReadingResult


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
