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
PRODUCT_CAPABILITY_CATALOG = DOCS / "product" / "capability-catalog.md"
PRODUCT_CAPABILITY_MANIFEST = DOCS / "product" / "capability-catalog.json"
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


def validate_product_capability_catalog(errors: list[str]) -> None:
    try:
        manifest = json.loads(PRODUCT_CAPABILITY_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: unable to load: {error}")
        return
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "capability-catalog-v1":
        errors.append(f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: incompatible schema_version")
        return
    items = manifest.get("capabilities")
    if not isinstance(items, list) or len(items) != 26:
        errors.append(f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: capabilities must contain exactly 26 entries")
        return

    keys: list[str] = []
    orders: list[int] = []
    planning_ids: list[str] = []
    manifest_rows: list[tuple[str, str]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: entry {index} must be an object")
            continue
        key = item.get("key")
        order = item.get("order")
        title = item.get("title")
        description = item.get("description")
        planning_id = item.get("planning_id")
        if not isinstance(key, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key):
            errors.append(f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: entry {index} has invalid key")
        else:
            keys.append(key)
        if not isinstance(order, int):
            errors.append(f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: entry {index} has invalid order")
        else:
            orders.append(order)
        if not isinstance(title, str) or not title or not isinstance(description, str) or not description:
            errors.append(f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: entry {index} needs title and description")
        else:
            manifest_rows.append((title, description))
        if planning_id is not None:
            if not isinstance(planning_id, str) or not re.fullmatch(r"CAP-\d{4,}", planning_id):
                errors.append(f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: entry {index} has invalid planning_id")
            else:
                planning_ids.append(planning_id)
                if not list((DOCS / "planning" / "capabilities").glob(f"{planning_id}-*.md")):
                    errors.append(f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: missing mapped artifact {planning_id}")

    if len(keys) != len(set(keys)):
        errors.append(f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: candidate keys must be unique")
    if sorted(orders) != list(range(1, 27)):
        errors.append(f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: order must be contiguous from 1 through 26")
    if len(planning_ids) != len(set(planning_ids)):
        errors.append(f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: planning_id mappings must be unique")

    markdown_rows: list[tuple[str, str]] = []
    for line in PRODUCT_CAPABILITY_CATALOG.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 2 or cells[0] == "Capability" or set(cells[0]) <= {"-", ":"}:
            continue
        markdown_rows.append((cells[0], cells[1]))
    if markdown_rows != manifest_rows:
        errors.append(
            f"{relative(PRODUCT_CAPABILITY_MANIFEST)}: title/description rows do not match "
            f"{relative(PRODUCT_CAPABILITY_CATALOG)} in order"
        )


def main() -> int:
    errors: list[str] = []
    validate_links(errors)
    validate_catalog(errors)
    validate_product_capability_catalog(errors)
    if errors:
        print("Documentation validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"Documentation validation passed: {len(markdown_sources())} Markdown "
        f"files plus context and product capability catalogs verified."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

