"""JSON-safe persistence codec for closed Content public values."""

from __future__ import annotations

from datetime import date, datetime
from typing import Mapping

from ..public import (
    AssetImage,
    BodyNode,
    BulletList,
    CodeBlock,
    EducationalSource,
    Emphasis,
    HardBreak,
    Heading,
    InlineCode,
    InlineNode,
    InlineText,
    ListItem,
    OrderedList,
    Paragraph,
    PassiveAsset,
    PublicationProvenance,
    PublishedLesson,
    SoftBreak,
    SourceLink,
    Strong,
    ThematicBreak,
)


def lesson_to_dict(lesson: PublishedLesson) -> dict[str, object]:
    return {
        "package_id": lesson.package_id,
        "package_version": lesson.package_version,
        "package_digest": lesson.package_digest,
        "title": lesson.title,
        "objectives": list(lesson.objectives),
        "body": [_body_to_dict(node) for node in lesson.body],
        "sources": [
            {
                "source_id": source.source_id,
                "title": source.title,
                "publisher": source.publisher,
                "locator": source.locator,
                "reviewed_on": source.reviewed_on.isoformat(),
                "license_note": source.license_note,
            }
            for source in lesson.sources
        ],
        "assets": [
            {
                "asset_id": asset.asset_id,
                "media_type": asset.media_type,
                "sha256": asset.sha256,
                "alt_text": asset.alt_text,
            }
            for asset in lesson.assets
        ],
        "provenance": {
            "published_by": lesson.provenance.published_by,
            "published_at": lesson.provenance.published_at.isoformat(),
            "content_reviewed_on": (
                lesson.provenance.content_reviewed_on.isoformat()
            ),
            "educational_use_notice": (
                lesson.provenance.educational_use_notice
            ),
        },
    }


def lesson_from_dict(raw: Mapping[str, object]) -> PublishedLesson:
    provenance = _mapping(raw["provenance"])
    return PublishedLesson(
        package_id=str(raw["package_id"]),
        package_version=str(raw["package_version"]),
        package_digest=str(raw["package_digest"]),
        title=str(raw["title"]),
        objectives=tuple(str(item) for item in _list(raw["objectives"])),
        body=tuple(_body_from_dict(_mapping(item)) for item in _list(raw["body"])),
        sources=tuple(
            EducationalSource(
                source_id=str(item["source_id"]),
                title=str(item["title"]),
                publisher=str(item["publisher"]),
                locator=str(item["locator"]),
                reviewed_on=date.fromisoformat(str(item["reviewed_on"])),
                license_note=(
                    str(item["license_note"])
                    if item.get("license_note") is not None
                    else None
                ),
            )
            for item in (_mapping(value) for value in _list(raw["sources"]))
        ),
        assets=tuple(
            PassiveAsset(
                asset_id=str(item["asset_id"]),
                media_type=str(item["media_type"]),
                sha256=str(item["sha256"]),
                alt_text=str(item["alt_text"]),
            )
            for item in (_mapping(value) for value in _list(raw["assets"]))
        ),
        provenance=PublicationProvenance(
            published_by=str(provenance["published_by"]),
            published_at=datetime.fromisoformat(
                str(provenance["published_at"])
            ),
            content_reviewed_on=date.fromisoformat(
                str(provenance["content_reviewed_on"])
            ),
            educational_use_notice=str(
                provenance["educational_use_notice"]
            ),
        ),
    )


def _inline_to_dict(node: InlineNode) -> dict[str, object]:
    if isinstance(node, InlineText):
        return {"kind": "text", "value": node.value}
    if isinstance(node, InlineCode):
        return {"kind": "code", "value": node.value}
    if isinstance(node, SoftBreak):
        return {"kind": "soft_break"}
    if isinstance(node, HardBreak):
        return {"kind": "hard_break"}
    if isinstance(node, Emphasis):
        return {
            "kind": "emphasis",
            "children": [_inline_to_dict(child) for child in node.children],
        }
    if isinstance(node, Strong):
        return {
            "kind": "strong",
            "children": [_inline_to_dict(child) for child in node.children],
        }
    if isinstance(node, SourceLink):
        return {
            "kind": "source_link",
            "children": [_inline_to_dict(child) for child in node.children],
            "href": node.href,
            "source_id": node.source_id,
        }
    if isinstance(node, AssetImage):
        return {
            "kind": "asset_image",
            "asset_id": node.asset_id,
            "alt_text": node.alt_text,
        }
    raise TypeError("Unsupported inline node.")


def _inline_from_dict(raw: Mapping[str, object]) -> InlineNode:
    kind = str(raw["kind"])
    if kind == "text":
        return InlineText(str(raw["value"]))
    if kind == "code":
        return InlineCode(str(raw["value"]))
    if kind == "soft_break":
        return SoftBreak()
    if kind == "hard_break":
        return HardBreak()
    if kind in {"emphasis", "strong"}:
        children = tuple(
            _inline_from_dict(_mapping(item))
            for item in _list(raw["children"])
        )
        return Emphasis(children) if kind == "emphasis" else Strong(children)
    if kind == "source_link":
        return SourceLink(
            children=tuple(
                _inline_from_dict(_mapping(item))
                for item in _list(raw["children"])
            ),
            href=str(raw["href"]),
            source_id=str(raw["source_id"]),
        )
    if kind == "asset_image":
        return AssetImage(
            asset_id=str(raw["asset_id"]),
            alt_text=str(raw["alt_text"]),
        )
    raise ValueError("Unsupported persisted inline node.")


def _body_to_dict(node: BodyNode) -> dict[str, object]:
    if isinstance(node, Heading):
        return {
            "kind": "heading",
            "level": node.level,
            "children": [_inline_to_dict(child) for child in node.children],
        }
    if isinstance(node, Paragraph):
        return {
            "kind": "paragraph",
            "children": [_inline_to_dict(child) for child in node.children],
        }
    if isinstance(node, CodeBlock):
        return {
            "kind": "code_block",
            "code": node.code,
            "language": node.language,
        }
    if isinstance(node, ThematicBreak):
        return {"kind": "thematic_break"}
    if isinstance(node, (BulletList, OrderedList)):
        result: dict[str, object] = {
            "kind": "bullet_list"
            if isinstance(node, BulletList)
            else "ordered_list",
            "items": [
                [_body_to_dict(block) for block in item.blocks]
                for item in node.items
            ],
        }
        if isinstance(node, OrderedList):
            result["start"] = node.start
        return result
    raise TypeError("Unsupported body node.")


def _body_from_dict(raw: Mapping[str, object]) -> BodyNode:
    kind = str(raw["kind"])
    if kind in {"heading", "paragraph"}:
        children = tuple(
            _inline_from_dict(_mapping(item))
            for item in _list(raw["children"])
        )
        if kind == "heading":
            return Heading(level=int(raw["level"]), children=children)
        return Paragraph(children=children)
    if kind == "code_block":
        language = raw.get("language")
        return CodeBlock(
            code=str(raw["code"]),
            language=str(language) if language is not None else None,
        )
    if kind == "thematic_break":
        return ThematicBreak()
    if kind in {"bullet_list", "ordered_list"}:
        items = tuple(
            ListItem(
                blocks=tuple(
                    _body_from_dict(_mapping(block))
                    for block in _list(item)
                )
            )
            for item in _list(raw["items"])
        )
        if kind == "bullet_list":
            return BulletList(items=items)
        return OrderedList(start=int(raw["start"]), items=items)
    raise ValueError("Unsupported persisted body node.")


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("Persisted lesson value is not an object.")
    return value


def _list(value: object) -> list[object]:
    if not isinstance(value, list):
        raise ValueError("Persisted lesson value is not an array.")
    return value
