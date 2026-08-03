#!/usr/bin/env python3
"""Validate documentation links and AI context routing integrity."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / "docs"
CATALOG_PATH = DOCS / "context" / "pack-catalog.json"
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
IGNORED_SCHEMES = ("http://", "https://", "mailto:")
MAX_PACK_LINES = 200


def relative(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def markdown_sources() -> list[Path]:
    sources = list(DOCS.rglob("*.md"))
    for name in ("README.md", "AGENTS.md"):
        path = REPO / name
        if path.exists():
            sources.append(path)
    return sorted(set(sources))


def validate_links(errors: list[str]) -> None:
    for source in markdown_sources():
        text = source.read_text(encoding="utf-8")
        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip().strip("<>")
            if not target or target.startswith("#") or target.startswith(IGNORED_SCHEMES):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            candidate = (source.parent / target).resolve()
            try:
                candidate.relative_to(REPO)
            except ValueError:
                errors.append(
                    f"{relative(source)}: link escapes repository: {raw_target}"
                )
                continue
            if not candidate.exists():
                errors.append(
                    f"{relative(source)}: missing link target: {raw_target}"
                )


def validate_catalog(errors: list[str]) -> None:
    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"{relative(CATALOG_PATH)}: unable to load: {error}")
        return

    packs = catalog.get("packs")
    if not isinstance(packs, list):
        errors.append(f"{relative(CATALOG_PATH)}: packs must be an array")
        return

    ids: list[str] = []
    paths: list[str] = []
    for index, pack in enumerate(packs):
        if not isinstance(pack, dict):
            errors.append(f"{relative(CATALOG_PATH)}: pack {index} must be an object")
            continue
        pack_id = pack.get("id")
        pack_path = pack.get("path")
        if not isinstance(pack_id, str) or not pack_id:
            errors.append(f"{relative(CATALOG_PATH)}: pack {index} has invalid id")
            continue
        if not isinstance(pack_path, str) or not pack_path:
            errors.append(f"{relative(CATALOG_PATH)}: pack {pack_id} has invalid path")
            continue
        ids.append(pack_id)
        paths.append(pack_path)

    if len(ids) != len(set(ids)):
        errors.append(f"{relative(CATALOG_PATH)}: pack ids must be unique")
    if len(paths) != len(set(paths)):
        errors.append(f"{relative(CATALOG_PATH)}: pack paths must be unique")

    known_ids = set(ids)
    if catalog.get("baselinePack") not in known_ids:
        errors.append(f"{relative(CATALOG_PATH)}: baselinePack is not a known id")

    for pack in packs:
        if not isinstance(pack, dict):
            continue
        pack_id = pack.get("id")
        pack_path = pack.get("path")
        if not isinstance(pack_id, str) or not isinstance(pack_path, str):
            continue
        path = REPO / pack_path
        if not path.is_file():
            errors.append(f"{relative(CATALOG_PATH)}: missing pack path {pack_path}")
        else:
            line_count = len(path.read_text(encoding="utf-8").splitlines())
            if line_count > MAX_PACK_LINES:
                errors.append(
                    f"{pack_path}: {line_count} lines exceeds {MAX_PACK_LINES}"
                )

        canonical_sources = pack.get("canonicalSources", [])
        if not isinstance(canonical_sources, list):
            errors.append(
                f"{relative(CATALOG_PATH)}: {pack_id} canonicalSources must be an array"
            )
        else:
            for value in canonical_sources:
                if not isinstance(value, str) or not (REPO / value).is_file():
                    errors.append(
                        f"{relative(CATALOG_PATH)}: {pack_id} missing canonical source {value!r}"
                    )

        adjacent = pack.get("adjacentPacks", [])
        if not isinstance(adjacent, list):
            errors.append(
                f"{relative(CATALOG_PATH)}: {pack_id} adjacentPacks must be an array"
            )
        else:
            for value in adjacent:
                if value not in known_ids:
                    errors.append(
                        f"{relative(CATALOG_PATH)}: {pack_id} unknown adjacent pack {value!r}"
                    )

    discovered = {
        relative(path)
        for path in (DOCS / "context" / "packs").glob("*.pack.md")
    }
    cataloged = set(paths)
    for missing in sorted(discovered - cataloged):
        errors.append(f"{relative(CATALOG_PATH)}: uncataloged pack {missing}")
    for missing in sorted(cataloged - discovered):
        errors.append(f"{relative(CATALOG_PATH)}: catalog path is not a pack {missing}")


def main() -> int:
    errors: list[str] = []
    validate_links(errors)
    validate_catalog(errors)
    if errors:
        print("Documentation validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"Documentation validation passed: {len(markdown_sources())} Markdown "
        f"files and context catalog verified."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

