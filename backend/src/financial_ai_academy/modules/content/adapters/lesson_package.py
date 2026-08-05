"""Runtime adapter for the executable lesson-package v1 contract."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from typing import Iterable, Mapping, Sequence
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker
from markdown_it import MarkdownIt
from markdown_it.token import Token
from referencing import Registry, Resource

from ..domain.models import ValidatedLessonPackage
from ..ports.package_validator import PackageValidationFailure
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


SUPPORTED_SCHEMA_VERSION = "1.0.0"
SUPPORTED_CAPABILITIES = {
    "lesson.commonmark.v1",
    "asset.raster.v1",
    "assessment.reference.v1",
}
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
MARKDOWN_DESTINATION_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)")
WINDOWS_RESERVED = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}


@dataclass(frozen=True, slots=True)
class PackageLimits:
    max_files: int = 128
    max_total_bytes: int = 32 * 1024 * 1024
    max_file_bytes: int = 8 * 1024 * 1024
    max_manifest_bytes: int = 256 * 1024
    max_lesson_bytes: int = 1024 * 1024
    max_image_pixels: int = 16_000_000
    max_markdown_nesting: int = 32


def _reject(code: str, reference: object, message: str) -> None:
    raise PackageValidationFailure(code, str(reference), message)


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_index_bytes(entries: Iterable[Mapping[str, object]]) -> bytes:
    ordered = sorted(
        (dict(entry) for entry in entries),
        key=lambda entry: str(entry["path"]).encode("utf-8"),
    )
    return json.dumps(
        ordered,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _normalize_logical_path(raw: object) -> str:
    value = str(raw)
    if not value or len(value) > 240:
        _reject("package.path_invalid", value, "Package path length is invalid.")
    if (
        chr(92) in value
        or chr(0) in value
        or unicodedata.normalize("NFC", value) != value
    ):
        _reject(
            "package.path_invalid",
            value,
            "Package path is not in the portable profile.",
        )
    if value.startswith(("/", "//")) or re.match(r"^[A-Za-z]:", value):
        _reject(
            "package.path_invalid",
            value,
            "Absolute package paths are prohibited.",
        )
    path = PurePosixPath(value)
    if path.is_absolute() or str(path) != value or not path.parts:
        _reject("package.path_invalid", value, "Package path is not normalized.")
    for part in path.parts:
        stem = part.split(".", 1)[0].casefold()
        if (
            part in {".", ".."}
            or part.startswith(".")
            or part.endswith((" ", "."))
            or stem in WINDOWS_RESERVED
            or any(ord(character) < 32 for character in part)
        ):
            _reject(
                "package.path_invalid",
                value,
                "Package path contains a prohibited segment.",
            )
    return value


def _image_dimensions(
    media_type: str, value: bytes
) -> tuple[int, int] | None:
    if (
        media_type == "image/png"
        and value.startswith(b"\x89PNG\r\n\x1a\n")
        and len(value) >= 24
    ):
        return struct.unpack(">II", value[16:24])
    if (
        media_type == "image/webp"
        and len(value) >= 30
        and value[:4] == b"RIFF"
        and value[8:12] == b"WEBP"
        and value[12:16] == b"VP8X"
    ):
        return (
            1 + int.from_bytes(value[24:27], "little"),
            1 + int.from_bytes(value[27:30], "little"),
        )
    if media_type == "image/jpeg" and value.startswith(b"\xff\xd8"):
        offset = 2
        while offset + 9 <= len(value):
            if value[offset] != 0xFF:
                offset += 1
                continue
            marker = value[offset + 1]
            if marker in {0xD8, 0xD9}:
                offset += 2
                continue
            length = int.from_bytes(value[offset + 2 : offset + 4], "big")
            if length < 2 or offset + 2 + length > len(value):
                return None
            if marker in {
                0xC0,
                0xC1,
                0xC2,
                0xC3,
                0xC5,
                0xC6,
                0xC7,
                0xC9,
                0xCA,
                0xCB,
                0xCD,
                0xCE,
                0xCF,
            }:
                return (
                    int.from_bytes(value[offset + 7 : offset + 9], "big"),
                    int.from_bytes(value[offset + 5 : offset + 7], "big"),
                )
            offset += 2 + length
    return None


def _sniff_media_type(path: str, value: bytes) -> str:
    suffix = PurePosixPath(path).suffix.casefold()
    if value.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if value.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if (
        len(value) >= 12
        and value[:4] == b"RIFF"
        and value[8:12] == b"WEBP"
    ):
        return "image/webp"
    if suffix == ".json":
        try:
            json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return "application/octet-stream"
        return "application/json"
    if suffix in {".md", ".markdown"}:
        try:
            value.decode("utf-8")
        except UnicodeDecodeError:
            return "application/octet-stream"
        return "text/markdown"
    return "application/octet-stream"


def _json_depth(value: object, current: int = 0) -> int:
    if isinstance(value, dict):
        return max(
            (_json_depth(item, current + 1) for item in value.values()),
            default=current,
        )
    if isinstance(value, list):
        return max(
            (_json_depth(item, current + 1) for item in value),
            default=current,
        )
    return current


def _load_schema_validator(schema_dir: Path) -> Draft202012Validator:
    resources: list[tuple[str, Resource[object]]] = []
    manifest_schema: dict[str, object] | None = None
    for path in sorted(schema_dir.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        resources.append((str(schema["$id"]), Resource.from_contents(schema)))
        if path.name == "manifest.schema.json":
            manifest_schema = schema
    if manifest_schema is None:
        raise RuntimeError("Manifest schema is missing.")
    return Draft202012Validator(
        manifest_schema,
        registry=Registry().with_resources(resources),
        format_checker=FormatChecker(),
    )


def _declarations(manifest: Mapping[str, object]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    lesson = manifest.get("lesson")
    if isinstance(lesson, dict):
        result.append(dict(lesson))
    for field in ("assessments", "assets"):
        records = manifest.get(field)
        if isinstance(records, list):
            result.extend(
                dict(record) for record in records if isinstance(record, dict)
            )
    return result


class ContractLessonPackageValidator:
    """Applies WRK-0001 schemas and compatibility-sensitive semantic rules."""

    def __init__(
        self, schema_dir: Path, limits: PackageLimits | None = None
    ) -> None:
        self._schema_dir = schema_dir
        self._limits = limits or PackageLimits()
        self._schema_validator = _load_schema_validator(schema_dir)

    def validate_directory(self, root: Path) -> ValidatedLessonPackage:
        if root.is_symlink():
            _reject(
                "package.path_invalid",
                "package",
                "Linked package roots are prohibited.",
            )
        resolved = root.resolve()
        if not resolved.is_dir():
            _reject(
                "package.not_found",
                "package",
                "Package directory does not exist.",
            )
        files: dict[str, bytes] = {}
        for path in resolved.rglob("*"):
            if path.is_symlink():
                _reject(
                    "package.path_invalid",
                    path.name,
                    "Linked package entries are prohibited.",
                )
            if path.is_file():
                files[path.relative_to(resolved).as_posix()] = path.read_bytes()
        return self.validate_files(files)

    def validate_files(
        self, files: Mapping[str, bytes]
    ) -> ValidatedLessonPackage:
        measured: dict[str, bytes] = {}
        casefolded: dict[str, str] = {}
        for raw_path, raw_value in files.items():
            logical = _normalize_logical_path(raw_path)
            folded = logical.casefold()
            if folded in casefolded and casefolded[folded] != logical:
                _reject(
                    "package.path_invalid",
                    logical,
                    "Case-colliding paths are prohibited.",
                )
            casefolded[folded] = logical
            value = bytes(raw_value)
            if len(value) > self._limits.max_file_bytes:
                _reject(
                    "package.limit_exceeded",
                    logical,
                    "File exceeds the accepted size limit.",
                )
            measured[logical] = value
        if len(measured) > self._limits.max_files:
            _reject(
                "package.limit_exceeded",
                "package",
                "Package contains too many files.",
            )
        if sum(map(len, measured.values())) > self._limits.max_total_bytes:
            _reject(
                "package.limit_exceeded",
                "package",
                "Package exceeds the accepted total size.",
            )
        manifest_bytes = measured.get("manifest.json")
        if manifest_bytes is None:
            _reject(
                "package.file_set_mismatch",
                "manifest.json",
                "Package manifest is missing.",
            )
        if len(manifest_bytes) > self._limits.max_manifest_bytes:
            _reject(
                "package.limit_exceeded",
                "manifest.json",
                "Manifest exceeds the accepted size.",
            )
        try:
            manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            _reject(
                "schema.invalid",
                "manifest.json",
                "Manifest is not valid UTF-8 JSON.",
            )
        if not isinstance(manifest, dict) or _json_depth(manifest) > 32:
            _reject(
                "schema.invalid",
                "manifest.json",
                "Manifest structure is invalid.",
            )
        errors = sorted(
            self._schema_validator.iter_errors(manifest),
            key=lambda error: tuple(str(item) for item in error.absolute_path),
        )
        if errors:
            reference = (
                ".".join(str(item) for item in errors[0].absolute_path)
                or "manifest.json"
            )
            _reject(
                "schema.invalid",
                reference,
                "Manifest does not satisfy lesson-package v1.",
            )
        if manifest["schema_version"] != SUPPORTED_SCHEMA_VERSION:
            _reject(
                "package.unsupported_version",
                "schema_version",
                "Schema version is unsupported.",
            )
        unknown = set(manifest["capabilities"]) - SUPPORTED_CAPABILITIES
        if unknown:
            _reject(
                "package.unsupported_capability",
                sorted(unknown)[0],
                "Capability is unsupported.",
            )

        declared: dict[str, dict[str, object]] = {}
        declared_folded: set[str] = set()
        for declaration in _declarations(manifest):
            logical = _normalize_logical_path(declaration.get("path"))
            if logical == "manifest.json":
                _reject(
                    "package.path_invalid",
                    logical,
                    "Manifest is implicit and cannot self-declare.",
                )
            if logical in declared or logical.casefold() in declared_folded:
                _reject(
                    "package.path_invalid",
                    logical,
                    "Declared paths must be unique.",
                )
            declared[logical] = declaration
            declared_folded.add(logical.casefold())
        expected = {"manifest.json", *declared}
        if set(measured) != expected:
            missing = sorted(expected - set(measured))
            extra = sorted(set(measured) - expected)
            _reject(
                "package.file_set_mismatch",
                (missing or extra or ["package"])[0],
                "Declared and measured package files do not match.",
            )

        lesson_path = str(manifest["lesson"]["path"])
        if len(measured[lesson_path]) > self._limits.max_lesson_bytes:
            _reject(
                "package.limit_exceeded",
                lesson_path,
                "Lesson exceeds the accepted size.",
            )
        for logical, declaration in declared.items():
            value = measured[logical]
            if (
                int(declaration["size_bytes"]) != len(value)
                or not SHA256_RE.match(str(declaration["sha256"]))
                or _sha256(value) != str(declaration["sha256"])
            ):
                _reject(
                    "package.integrity_mismatch",
                    logical,
                    "Declared size or digest does not match.",
                )
            media_type = _sniff_media_type(logical, value)
            if media_type != str(declaration["media_type"]):
                _reject(
                    "package.media_mismatch",
                    logical,
                    "Declared and measured media types differ.",
                )
            if media_type.startswith("image/"):
                dimensions = _image_dimensions(media_type, value)
                if not dimensions:
                    _reject(
                        "package.media_mismatch",
                        logical,
                        "Image header is invalid.",
                    )
                width, height = dimensions
                if (
                    width <= 0
                    or height <= 0
                    or width * height > self._limits.max_image_pixels
                ):
                    _reject(
                        "package.limit_exceeded",
                        logical,
                        "Image dimensions exceed the accepted limit.",
                    )

        try:
            lesson_text = measured[lesson_path].decode("utf-8")
        except UnicodeDecodeError:
            _reject(
                "package.media_mismatch",
                lesson_path,
                "Lesson is not UTF-8 CommonMark.",
            )
        lesson = self._build_lesson(manifest, lesson_text)
        entries = tuple(
            {
                "path": logical,
                "media_type": _sniff_media_type(logical, value),
                "size_bytes": len(value),
                "sha256": _sha256(value),
            }
            for logical, value in sorted(
                measured.items(), key=lambda item: item[0].encode("utf-8")
            )
        )
        digest = _sha256(_canonical_index_bytes(entries))
        return ValidatedLessonPackage(
            lesson=PublishedLesson(
                package_id=lesson.package_id,
                package_version=lesson.package_version,
                package_digest=digest,
                title=lesson.title,
                objectives=lesson.objectives,
                body=lesson.body,
                sources=lesson.sources,
                assets=lesson.assets,
                provenance=lesson.provenance,
            ),
            files=measured,
            index=entries,
        )

    def _build_lesson(
        self,
        manifest: Mapping[str, object],
        lesson_text: str,
    ) -> PublishedLesson:
        sources = tuple(
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
            for item in manifest["sources"]
        )
        assets = tuple(
            PassiveAsset(
                asset_id=str(item["asset_id"]),
                media_type=str(item["media_type"]),
                sha256=str(item["sha256"]),
                alt_text=str(item["alt_text"]),
            )
            for item in manifest["assets"]
        )
        source_by_url = {source.locator: source.source_id for source in sources}
        asset_by_path = {
            str(item["path"]): (str(item["asset_id"]), str(item["alt_text"]))
            for item in manifest["assets"]
        }
        body = _parse_commonmark(
            lesson_text,
            source_by_url,
            asset_by_path,
            self._limits,
        )
        provenance = manifest["provenance"]
        published_at = datetime.fromisoformat(
            str(provenance["published_at"]).replace("Z", "+00:00")
        )
        return PublishedLesson(
            package_id=str(manifest["package_id"]),
            package_version=str(manifest["package_version"]),
            package_digest="",
            title=str(manifest["title"]),
            objectives=tuple(str(item) for item in manifest["objectives"]),
            body=body,
            sources=sources,
            assets=assets,
            provenance=PublicationProvenance(
                published_by=str(provenance["published_by"]),
                published_at=published_at,
                content_reviewed_on=date.fromisoformat(
                    str(provenance["content_reviewed_on"])
                ),
                educational_use_notice=str(
                    provenance["educational_use_notice"]
                ),
            ),
        )


def _parse_commonmark(
    value: str,
    source_by_url: Mapping[str, str],
    asset_by_path: Mapping[str, tuple[str, str]],
    limits: PackageLimits,
) -> tuple[BodyNode, ...]:
    if re.search(r"<[A-Za-z!/][^>]*>", value):
        _reject("markup.unsafe_html", "lesson", "Raw HTML is not accepted.")
    for match in MARKDOWN_DESTINATION_RE.finditer(value):
        destination = match.group(1).strip("<>")
        if match.group(0).startswith("!"):
            normalized = _normalize_logical_path(destination)
            if normalized not in asset_by_path:
                _reject(
                    "markup.undeclared_asset",
                    normalized,
                    "Lesson images must reference a declared passive asset.",
                )
        else:
            parsed = urlsplit(destination)
            if (
                parsed.scheme.casefold() != "https"
                or not parsed.netloc
                or destination not in source_by_url
            ):
                _reject(
                    "markup.unsafe_url",
                    destination,
                    "Lesson links must match a declared HTTPS source.",
                )

    tokens = MarkdownIt("commonmark", {"html": True}).parse(value)
    allowed_blocks = {
        "heading_open",
        "heading_close",
        "paragraph_open",
        "paragraph_close",
        "bullet_list_open",
        "bullet_list_close",
        "ordered_list_open",
        "ordered_list_close",
        "list_item_open",
        "list_item_close",
        "inline",
        "fence",
        "code_block",
        "hr",
    }
    allowed_inline = {
        "text",
        "softbreak",
        "hardbreak",
        "em_open",
        "em_close",
        "strong_open",
        "strong_close",
        "code_inline",
        "link_open",
        "link_close",
        "image",
    }
    for token in tokens:
        if token.level > limits.max_markdown_nesting:
            _reject(
                "package.limit_exceeded",
                "lesson",
                "Lesson nesting exceeds the accepted limit.",
            )
        if token.type.startswith("html_"):
            _reject("markup.unsafe_html", "lesson", "Raw HTML is not accepted.")
        if token.type not in allowed_blocks:
            _reject(
                "markup.unsupported_node",
                token.type,
                "Lesson node is not in the version 1 profile.",
            )
        for child in token.children or ():
            if child.type.startswith("html_"):
                _reject(
                    "markup.unsafe_html",
                    "lesson",
                    "Raw HTML is not accepted.",
                )
            if child.type not in allowed_inline:
                _reject(
                    "markup.unsupported_node",
                    child.type,
                    "Inline node is not in the version 1 profile.",
                )
            if child.type == "link_open":
                href = child.attrGet("href") or ""
                parsed = urlsplit(href)
                if (
                    parsed.scheme.casefold() != "https"
                    or not parsed.netloc
                    or href not in source_by_url
                ):
                    _reject(
                        "markup.unsafe_url",
                        href,
                        "Link is not a declared HTTPS source.",
                    )
            if child.type == "image":
                source = _normalize_logical_path(child.attrGet("src") or "")
                if source not in asset_by_path:
                    _reject(
                        "markup.undeclared_asset",
                        source,
                        "Image asset is not declared.",
                    )
                if not (child.content or "").strip():
                    _reject(
                        "markup.invalid_asset",
                        source,
                        "Image alternative text is required.",
                    )

    nodes, offset = _parse_blocks(
        tokens, 0, None, source_by_url, asset_by_path
    )
    if offset != len(tokens):
        _reject(
            "markup.unsupported_node",
            tokens[offset].type,
            "Lesson block structure is invalid.",
        )
    return nodes


def _parse_blocks(
    tokens: Sequence[Token],
    offset: int,
    stop_type: str | None,
    source_by_url: Mapping[str, str],
    asset_by_path: Mapping[str, tuple[str, str]],
) -> tuple[tuple[BodyNode, ...], int]:
    result: list[BodyNode] = []
    while offset < len(tokens):
        token = tokens[offset]
        if stop_type is not None and token.type == stop_type:
            return tuple(result), offset + 1
        if token.type == "heading_open":
            inline = _expected_inline(tokens, offset)
            result.append(
                Heading(
                    level=int(token.tag.removeprefix("h")),
                    children=_parse_inline(
                        inline.children or (),
                        source_by_url,
                        asset_by_path,
                    ),
                )
            )
            offset += 3
            continue
        if token.type == "paragraph_open":
            inline = _expected_inline(tokens, offset)
            result.append(
                Paragraph(
                    children=_parse_inline(
                        inline.children or (),
                        source_by_url,
                        asset_by_path,
                    )
                )
            )
            offset += 3
            continue
        if token.type in {"fence", "code_block"}:
            language = (
                token.info.strip().split(maxsplit=1)[0]
                if token.info.strip()
                else None
            )
            result.append(CodeBlock(code=token.content, language=language))
            offset += 1
            continue
        if token.type == "hr":
            result.append(ThematicBreak())
            offset += 1
            continue
        if token.type in {"bullet_list_open", "ordered_list_open"}:
            list_node, offset = _parse_list(
                tokens, offset, source_by_url, asset_by_path
            )
            result.append(list_node)
            continue
        _reject(
            "markup.unsupported_node",
            token.type,
            "Lesson block structure is invalid.",
        )
    if stop_type is not None:
        _reject(
            "markup.unsupported_node",
            stop_type,
            "Lesson block structure is incomplete.",
        )
    return tuple(result), offset


def _expected_inline(tokens: Sequence[Token], offset: int) -> Token:
    if (
        offset + 2 >= len(tokens)
        or tokens[offset + 1].type != "inline"
        or tokens[offset + 2].type
        != tokens[offset].type.replace("_open", "_close")
    ):
        _reject(
            "markup.unsupported_node",
            tokens[offset].type,
            "Lesson block structure is invalid.",
        )
    return tokens[offset + 1]


def _parse_list(
    tokens: Sequence[Token],
    offset: int,
    source_by_url: Mapping[str, str],
    asset_by_path: Mapping[str, tuple[str, str]],
) -> tuple[BodyNode, int]:
    opening = tokens[offset]
    closing = opening.type.replace("_open", "_close")
    offset += 1
    items: list[ListItem] = []
    while offset < len(tokens) and tokens[offset].type != closing:
        if tokens[offset].type != "list_item_open":
            _reject(
                "markup.unsupported_node",
                tokens[offset].type,
                "Lesson list structure is invalid.",
            )
        blocks, offset = _parse_blocks(
            tokens,
            offset + 1,
            "list_item_close",
            source_by_url,
            asset_by_path,
        )
        items.append(ListItem(blocks=blocks))
    if offset >= len(tokens) or tokens[offset].type != closing:
        _reject(
            "markup.unsupported_node",
            opening.type,
            "Lesson list structure is incomplete.",
        )
    offset += 1
    if opening.type == "bullet_list_open":
        return BulletList(items=tuple(items)), offset
    start = int(opening.attrGet("start") or "1")
    return OrderedList(start=start, items=tuple(items)), offset


def _parse_inline(
    tokens: Sequence[Token],
    source_by_url: Mapping[str, str],
    asset_by_path: Mapping[str, tuple[str, str]],
) -> tuple[InlineNode, ...]:
    result, offset = _parse_inline_until(
        tokens, 0, None, source_by_url, asset_by_path
    )
    if offset != len(tokens):
        _reject(
            "markup.unsupported_node",
            tokens[offset].type,
            "Inline structure is invalid.",
        )
    return result


def _parse_inline_until(
    tokens: Sequence[Token],
    offset: int,
    stop_type: str | None,
    source_by_url: Mapping[str, str],
    asset_by_path: Mapping[str, tuple[str, str]],
) -> tuple[tuple[InlineNode, ...], int]:
    result: list[InlineNode] = []
    while offset < len(tokens):
        token = tokens[offset]
        if stop_type is not None and token.type == stop_type:
            return tuple(result), offset + 1
        if token.type == "text":
            result.append(InlineText(token.content))
            offset += 1
        elif token.type == "code_inline":
            result.append(InlineCode(token.content))
            offset += 1
        elif token.type == "softbreak":
            result.append(SoftBreak())
            offset += 1
        elif token.type == "hardbreak":
            result.append(HardBreak())
            offset += 1
        elif token.type in {"em_open", "strong_open", "link_open"}:
            closing = token.type.replace("_open", "_close")
            children, offset = _parse_inline_until(
                tokens,
                offset + 1,
                closing,
                source_by_url,
                asset_by_path,
            )
            if token.type == "em_open":
                result.append(Emphasis(children))
            elif token.type == "strong_open":
                result.append(Strong(children))
            else:
                href = token.attrGet("href") or ""
                result.append(
                    SourceLink(
                        children=children,
                        href=href,
                        source_id=source_by_url[href],
                    )
                )
        elif token.type == "image":
            path = _normalize_logical_path(token.attrGet("src") or "")
            asset_id, _manifest_alt = asset_by_path[path]
            result.append(AssetImage(asset_id, token.content))
            offset += 1
        else:
            _reject(
                "markup.unsupported_node",
                token.type,
                "Inline structure is invalid.",
            )
    if stop_type is not None:
        _reject(
            "markup.unsupported_node",
            stop_type,
            "Inline structure is incomplete.",
        )
    return tuple(result), offset
