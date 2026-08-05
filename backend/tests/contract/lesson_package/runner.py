#!/usr/bin/env python3
"""Dependency-light conformance runner for lesson-package contract version 1."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Iterable, Mapping, Sequence
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker
from markdown_it import MarkdownIt
from referencing import Registry, Resource


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


@dataclass(frozen=True)
class PackageLimits:
    max_files: int = 128
    max_total_bytes: int = 32 * 1024 * 1024
    max_file_bytes: int = 8 * 1024 * 1024
    max_manifest_bytes: int = 256 * 1024
    max_lesson_bytes: int = 1024 * 1024
    max_image_pixels: int = 16_000_000
    max_markdown_nesting: int = 32


@dataclass(frozen=True)
class Diagnostic:
    code: str
    reference: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "reference": bounded_reference(self.reference),
            "message": self.message,
        }


class ConformanceError(ValueError):
    """A safe, stable package-boundary rejection."""

    def __init__(self, code: str, reference: str, message: str) -> None:
        super().__init__(message)
        self.diagnostic = Diagnostic(code, bounded_reference(reference), message)


@dataclass(frozen=True)
class ValidatedPackage:
    manifest: dict[str, object]
    index: tuple[dict[str, object], ...]
    index_bytes: bytes
    package_digest: str


def bounded_reference(value: object) -> str:
    text = str(value).replace(chr(0), "").replace("\r", " ").replace("\n", " ")
    return text[:120]


def reject(code: str, reference: object, message: str) -> None:
    raise ConformanceError(code, bounded_reference(reference), message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_index_bytes(entries: Iterable[Mapping[str, object]]) -> bytes:
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


def package_digest(entries: Iterable[Mapping[str, object]]) -> str:
    return sha256_bytes(canonical_index_bytes(entries))


def immutable_conflict(
    accepted_package_id: str,
    accepted_version: str,
    accepted_digest: str,
    candidate_package_id: str,
    candidate_version: str,
    candidate_digest: str,
) -> Diagnostic | None:
    if (
        accepted_package_id == candidate_package_id
        and accepted_version == candidate_version
        and accepted_digest != candidate_digest
    ):
        return Diagnostic(
            "package.immutable_conflict",
            f"{candidate_package_id}@{candidate_version}",
            "The package identity and version already map to different bytes.",
        )
    return None


def normalize_logical_path(raw: object) -> str:
    value = str(raw)
    if not value or len(value) > 240:
        reject("package.path_invalid", value, "Package path length is invalid.")
    if chr(92) in value or chr(0) in value or unicodedata.normalize("NFC", value) != value:
        reject("package.path_invalid", value, "Package path is not in the portable profile.")
    if value.startswith(("/", "//")) or re.match(r"^[A-Za-z]:", value):
        reject("package.path_invalid", value, "Absolute package paths are prohibited.")
    path = PurePosixPath(value)
    if path.is_absolute() or str(path) != value:
        reject("package.path_invalid", value, "Package path is not normalized.")
    if not path.parts:
        reject("package.path_invalid", value, "Package path is empty.")
    for part in path.parts:
        stem = part.split(".", 1)[0].casefold()
        if (
            part in {".", ".."}
            or part.startswith(".")
            or part.endswith((" ", "."))
            or stem in WINDOWS_RESERVED
            or any(ord(character) < 32 for character in part)
        ):
            reject("package.path_invalid", value, "Package path contains a prohibited segment.")
    return value


def image_dimensions(media_type: str, value: bytes) -> tuple[int, int] | None:
    if media_type == "image/png" and value.startswith(b"\x89PNG\r\n\x1a\n") and len(value) >= 24:
        return struct.unpack(">II", value[16:24])
    if media_type == "image/webp" and len(value) >= 30 and value[:4] == b"RIFF" and value[8:12] == b"WEBP":
        if value[12:16] == b"VP8X":
            width = 1 + int.from_bytes(value[24:27], "little")
            height = 1 + int.from_bytes(value[27:30], "little")
            return width, height
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
                0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
            }:
                height = int.from_bytes(value[offset + 5 : offset + 7], "big")
                width = int.from_bytes(value[offset + 7 : offset + 9], "big")
                return width, height
            offset += 2 + length
    return None


def sniff_media_type(path: str, value: bytes) -> str:
    suffix = PurePosixPath(path).suffix.casefold()
    if value.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if value.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if len(value) >= 12 and value[:4] == b"RIFF" and value[8:12] == b"WEBP":
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
        return max((_json_depth(item, current + 1) for item in value.values()), default=current)
    if isinstance(value, list):
        return max((_json_depth(item, current + 1) for item in value), default=current)
    return current


def load_schema_validator(schema_dir: Path) -> Draft202012Validator:
    resources: list[tuple[str, Resource[object]]] = []
    manifest_schema: dict[str, object] | None = None
    for path in sorted(schema_dir.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        schema_id = str(schema["$id"])
        resources.append((schema_id, Resource.from_contents(schema)))
        if path.name == "manifest.schema.json":
            manifest_schema = schema
    if manifest_schema is None:
        raise RuntimeError("manifest schema is missing")
    registry = Registry().with_resources(resources)
    return Draft202012Validator(
        manifest_schema,
        registry=registry,
        format_checker=FormatChecker(),
    )


def declaration_records(manifest: Mapping[str, object]) -> list[dict[str, object]]:
    lesson = manifest.get("lesson")
    records: list[dict[str, object]] = []
    if isinstance(lesson, dict):
        records.append(dict(lesson))
    for field in ("assessments", "assets"):
        value = manifest.get(field)
        if isinstance(value, list):
            records.extend(dict(item) for item in value if isinstance(item, dict))
    return records


def validate_markup(
    value: str,
    source_urls: set[str],
    asset_paths: set[str],
    limits: PackageLimits,
) -> None:
    if re.search(r"<[A-Za-z!/][^>]*>", value):
        reject("markup.unsafe_html", "lesson", "Raw HTML is not accepted.")
    for match in MARKDOWN_DESTINATION_RE.finditer(value):
        destination = match.group(1).strip("<>")
        is_image = match.group(0).startswith("!")
        if is_image:
            normalized = normalize_logical_path(destination)
            if normalized not in asset_paths:
                reject(
                    "markup.undeclared_asset",
                    normalized,
                    "Lesson images must reference a declared passive asset.",
                )
            continue
        parsed = urlsplit(destination)
        if parsed.scheme.casefold() != "https" or not parsed.netloc or destination not in source_urls:
            reject(
                "markup.unsafe_url",
                destination,
                "Lesson links must match a declared HTTPS educational source.",
            )

    parser = MarkdownIt("commonmark", {"html": True})
    tokens = parser.parse(value)
    allowed_blocks = {
        "heading_open", "heading_close", "paragraph_open", "paragraph_close",
        "bullet_list_open", "bullet_list_close", "ordered_list_open",
        "ordered_list_close", "list_item_open", "list_item_close",
        "inline", "fence", "code_block", "hr",
    }
    allowed_inline = {
        "text", "softbreak", "hardbreak", "em_open", "em_close",
        "strong_open", "strong_close", "code_inline", "link_open",
        "link_close", "image",
    }
    for token in tokens:
        if token.level > limits.max_markdown_nesting:
            reject("package.limit_exceeded", "lesson", "Lesson nesting exceeds the accepted limit.")
        if token.type.startswith("html_"):
            reject("markup.unsafe_html", "lesson", "Raw HTML is not accepted.")
        if token.type not in allowed_blocks:
            reject("markup.unsupported_node", token.type, "Lesson node is not in the version 1 profile.")
        for child in token.children or []:
            if child.type.startswith("html_"):
                reject("markup.unsafe_html", "lesson", "Raw HTML is not accepted.")
            if child.type not in allowed_inline:
                reject("markup.unsupported_node", child.type, "Inline node is not in the version 1 profile.")
            if child.type == "link_open":
                href = child.attrGet("href") or ""
                parsed = urlsplit(href)
                if parsed.scheme.casefold() != "https" or not parsed.netloc or href not in source_urls:
                    reject("markup.unsafe_url", href, "Link is not a declared HTTPS source.")
            if child.type == "image":
                source = normalize_logical_path(child.attrGet("src") or "")
                if source not in asset_paths:
                    reject("markup.undeclared_asset", source, "Image asset is not declared.")
                if not (child.content or "").strip():
                    reject("markup.invalid_asset", source, "Image alternative text is required.")


class LessonPackageValidator:
    def __init__(self, schema_dir: Path, limits: PackageLimits | None = None) -> None:
        self.schema_dir = schema_dir
        self.limits = limits or PackageLimits()
        self.schema_validator = load_schema_validator(schema_dir)

    def with_limits(self, **updates: int) -> "LessonPackageValidator":
        return LessonPackageValidator(self.schema_dir, replace(self.limits, **updates))

    def validate(self, root: Path) -> ValidatedPackage:
        root = root.resolve()
        if not root.is_dir():
            reject("package.not_found", "package", "Package directory does not exist.")
        files: dict[str, bytes] = {}
        casefolded: dict[str, str] = {}
        for path in root.rglob("*"):
            if path.is_symlink():
                reject("package.path_invalid", path.name, "Linked package entries are prohibited.")
            if not path.is_file():
                continue
            logical = normalize_logical_path(path.relative_to(root).as_posix())
            folded = logical.casefold()
            if folded in casefolded and casefolded[folded] != logical:
                reject("package.path_invalid", logical, "Case-colliding paths are prohibited.")
            casefolded[folded] = logical
            value = path.read_bytes()
            if len(value) > self.limits.max_file_bytes:
                reject("package.limit_exceeded", logical, "File exceeds the accepted size limit.")
            files[logical] = value
        if len(files) > self.limits.max_files:
            reject("package.limit_exceeded", "package", "Package contains too many files.")
        if sum(len(value) for value in files.values()) > self.limits.max_total_bytes:
            reject("package.limit_exceeded", "package", "Package exceeds the accepted total size.")
        manifest_bytes = files.get("manifest.json")
        if manifest_bytes is None:
            reject("package.file_set_mismatch", "manifest.json", "Package manifest is missing.")
        if len(manifest_bytes) > self.limits.max_manifest_bytes:
            reject("package.limit_exceeded", "manifest.json", "Manifest exceeds the accepted size.")
        try:
            manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            reject("schema.invalid", "manifest.json", "Manifest is not valid UTF-8 JSON.")
        if not isinstance(manifest, dict) or _json_depth(manifest) > 32:
            reject("schema.invalid", "manifest.json", "Manifest structure is invalid.")
        errors = sorted(
            self.schema_validator.iter_errors(manifest),
            key=lambda error: tuple(str(item) for item in error.absolute_path),
        )
        if errors:
            path = ".".join(str(item) for item in errors[0].absolute_path) or "manifest.json"
            reject("schema.invalid", path, "Manifest does not satisfy lesson-package v1.")
        if manifest["schema_version"] != SUPPORTED_SCHEMA_VERSION:
            reject("package.unsupported_version", "schema_version", "Schema version is unsupported.")
        unknown = set(manifest["capabilities"]) - SUPPORTED_CAPABILITIES
        if unknown:
            reject("package.unsupported_capability", sorted(unknown)[0], "Capability is unsupported.")

        declarations = declaration_records(manifest)
        declared: dict[str, dict[str, object]] = {}
        declared_casefolded: set[str] = set()
        for declaration in declarations:
            logical = normalize_logical_path(declaration.get("path"))
            if logical == "manifest.json":
                reject("package.path_invalid", logical, "Manifest is implicit and cannot self-declare.")
            if logical in declared or logical.casefold() in declared_casefolded:
                reject("package.path_invalid", logical, "Declared paths must be unique.")
            declared[logical] = declaration
            declared_casefolded.add(logical.casefold())
        expected_files = {"manifest.json", *declared}
        if set(files) != expected_files:
            missing = sorted(expected_files - set(files))
            extra = sorted(set(files) - expected_files)
            reference = (missing or extra or ["package"])[0]
            reject(
                "package.file_set_mismatch",
                reference,
                "Declared and measured package files do not match.",
            )

        lesson_path = str(manifest["lesson"]["path"])
        if len(files[lesson_path]) > self.limits.max_lesson_bytes:
            reject("package.limit_exceeded", lesson_path, "Lesson exceeds the accepted size.")
        asset_paths = {str(item["path"]) for item in manifest["assets"]}
        for logical, declaration in declared.items():
            value = files[logical]
            declared_size = int(declaration["size_bytes"])
            declared_digest = str(declaration["sha256"])
            if declared_size != len(value) or not SHA256_RE.match(declared_digest):
                reject("package.integrity_mismatch", logical, "Declared size or digest is invalid.")
            if sha256_bytes(value) != declared_digest:
                reject("package.integrity_mismatch", logical, "File digest does not match.")
            measured_media = sniff_media_type(logical, value)
            declared_media = str(declaration["media_type"])
            if measured_media != declared_media:
                reject("package.media_mismatch", logical, "Declared and measured media types differ.")
            if measured_media.startswith("image/"):
                dimensions = image_dimensions(measured_media, value)
                if not dimensions:
                    reject("package.media_mismatch", logical, "Image header is invalid.")
                width, height = dimensions
                if width <= 0 or height <= 0 or width * height > self.limits.max_image_pixels:
                    reject("package.limit_exceeded", logical, "Image dimensions exceed the accepted limit.")

        try:
            lesson_text = files[lesson_path].decode("utf-8")
        except UnicodeDecodeError:
            reject("package.media_mismatch", lesson_path, "Lesson is not UTF-8 CommonMark.")
        source_urls = {str(item["locator"]) for item in manifest["sources"]}
        validate_markup(lesson_text, source_urls, asset_paths, self.limits)

        entries = tuple(
            {
                "path": logical,
                "media_type": sniff_media_type(logical, value),
                "size_bytes": len(value),
                "sha256": sha256_bytes(value),
            }
            for logical, value in sorted(files.items(), key=lambda item: item[0].encode("utf-8"))
        )
        index_bytes = canonical_index_bytes(entries)
        return ValidatedPackage(
            manifest=manifest,
            index=entries,
            index_bytes=index_bytes,
            package_digest=sha256_bytes(index_bytes),
        )


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_schema_dir() -> Path:
    return repository_root() / "contracts/learning/lesson-package/v1"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--schema-dir", type=Path, default=default_schema_dir())
    arguments = parser.parse_args(argv)
    try:
        result = LessonPackageValidator(arguments.schema_dir).validate(arguments.package)
    except (ConformanceError, OSError, RuntimeError) as error:
        diagnostic = (
            error.diagnostic
            if isinstance(error, ConformanceError)
            else Diagnostic("package.internal_error", "package", "Package validation could not complete.")
        )
        print(json.dumps({"valid": False, "diagnostic": diagnostic.as_dict()}, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "package_id": result.manifest["package_id"],
                "package_version": result.manifest["package_version"],
                "package_digest": result.package_digest,
                "file_count": len(result.index),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
