from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOKENS_PATH = ROOT / "apps/web/src/design-system/tokens.css"
SPRITE_PATH = ROOT / "apps/web/src/design-system/icons/faa-icons.svg"
MANIFEST_PATH = ROOT / "apps/web/src/design-system/icons/manifest.json"
ICON_CSS_PATH = ROOT / "apps/web/src/design-system/icons/icons.css"
STYLE_GUIDE_PATH = ROOT / "docs/design/style-guide.md"

VAR_RE = re.compile(r"(--faa-[a-z0-9-]+)\s*:\s*([^;]+);")
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
XML_NAMESPACE = "{http://www.w3.org/2000/svg}"

THEME_TOKENS = [
    "--faa-color-canvas",
    "--faa-color-surface",
    "--faa-color-surface-raised",
    "--faa-color-surface-subtle",
    "--faa-color-surface-selected",
    "--faa-color-text-primary",
    "--faa-color-text-secondary",
    "--faa-color-text-muted",
    "--faa-color-text-disabled",
    "--faa-color-text-inverse",
    "--faa-color-border",
    "--faa-color-border-strong",
    "--faa-color-overlay",
    "--faa-color-brand",
    "--faa-color-brand-hover",
    "--faa-color-brand-active",
    "--faa-color-on-brand",
    "--faa-color-accent",
    "--faa-color-accent-hover",
    "--faa-color-accent-strong",
    "--faa-color-on-accent",
    "--faa-color-action-primary",
    "--faa-color-action-primary-hover",
    "--faa-color-on-action-primary",
    "--faa-color-link",
    "--faa-color-focus-ring",
    "--faa-color-control",
    "--faa-color-control-hover",
    "--faa-color-control-disabled",
    "--faa-color-nav-bg",
    "--faa-color-nav-text",
    "--faa-color-nav-muted",
    "--faa-color-nav-active-bg",
    "--faa-color-nav-active-text",
    "--faa-color-icon-default",
    "--faa-color-icon-muted",
    "--faa-color-icon-active",
    "--faa-color-icon-accent",
    "--faa-color-success",
    "--faa-color-success-surface",
    "--faa-color-warning",
    "--faa-color-warning-surface",
    "--faa-color-danger",
    "--faa-color-danger-surface",
    "--faa-color-info",
    "--faa-color-info-surface",
    "--faa-color-chart-1",
    "--faa-color-chart-2",
    "--faa-color-chart-3",
    "--faa-color-chart-4",
    "--faa-color-chart-5",
    "--faa-color-chart-grid",
    "--faa-color-chart-axis",
    "--faa-color-chart-reference",
    "--faa-shadow-sm",
    "--faa-shadow-md",
    "--faa-shadow-lg",
]

CONTRAST_CHECKS = [
    ("--faa-color-text-primary", "--faa-color-canvas", 4.5),
    ("--faa-color-text-secondary", "--faa-color-canvas", 4.5),
    ("--faa-color-text-muted", "--faa-color-canvas", 4.5),
    ("--faa-color-text-primary", "--faa-color-surface", 4.5),
    ("--faa-color-on-brand", "--faa-color-brand", 4.5),
    ("--faa-color-on-accent", "--faa-color-accent", 4.5),
    ("--faa-color-on-action-primary", "--faa-color-action-primary", 4.5),
    ("--faa-color-link", "--faa-color-canvas", 4.5),
    ("--faa-color-focus-ring", "--faa-color-canvas", 3.0),
    ("--faa-color-nav-text", "--faa-color-nav-bg", 4.5),
    ("--faa-color-nav-active-text", "--faa-color-nav-active-bg", 4.5),
    ("--faa-color-icon-default", "--faa-color-canvas", 3.0),
    ("--faa-color-success", "--faa-color-canvas", 4.5),
    ("--faa-color-warning", "--faa-color-canvas", 4.5),
    ("--faa-color-danger", "--faa-color-canvas", 4.5),
    ("--faa-color-info", "--faa-color-canvas", 4.5),
    ("--faa-color-chart-1", "--faa-color-canvas", 3.0),
    ("--faa-color-chart-2", "--faa-color-canvas", 3.0),
    ("--faa-color-chart-3", "--faa-color-canvas", 3.0),
    ("--faa-color-chart-4", "--faa-color-canvas", 3.0),
    ("--faa-color-chart-5", "--faa-color-canvas", 3.0),
]

ALLOWED_ICON_TAGS = {
    "circle",
    "ellipse",
    "line",
    "path",
    "polyline",
    "rect",
    "symbol",
}
ALLOWED_CATEGORIES = {"action", "concept", "navigation", "status", "system"}


def extract_block(source: str, marker: str) -> str:
    marker_index = source.find(marker)
    if marker_index < 0:
        raise ValueError(f"missing CSS block marker: {marker}")
    start = source.find("{", marker_index)
    if start < 0:
        raise ValueError(f"missing opening brace after: {marker}")
    depth = 0
    for index in range(start, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start + 1 : index]
    raise ValueError(f"unclosed CSS block after: {marker}")


def parse_variables(block: str) -> dict[str, str]:
    return {name: value.strip() for name, value in VAR_RE.findall(block)}


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]

    def linearize(value: float) -> float:
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (linearize(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first: str, second: str) -> float:
    first_luminance = relative_luminance(first)
    second_luminance = relative_luminance(second)
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def local_name(tag: str) -> str:
    return tag.removeprefix(XML_NAMESPACE)


def validate_tokens(errors: list[str]) -> int:
    source = TOKENS_PATH.read_text(encoding="utf-8")
    try:
        light = parse_variables(extract_block(source, ':root,\n[data-theme="light"]'))
        dark = parse_variables(extract_block(source, '[data-theme="dark"]'))
        system_dark = parse_variables(extract_block(source, '[data-theme="system"]'))
    except ValueError as error:
        errors.append(str(error))
        return 0

    for theme_name, variables in (
        ("light", light),
        ("dark", dark),
        ("system dark", system_dark),
    ):
        missing = sorted(set(THEME_TOKENS) - variables.keys())
        if missing:
            errors.append(f"{theme_name} theme is missing: {', '.join(missing)}")

    for token in THEME_TOKENS:
        if token in dark and token in system_dark and dark[token] != system_dark[token]:
            errors.append(
                f"system dark mismatch for {token}: {system_dark[token]} != {dark[token]}"
            )

    for theme_name, variables in (("light", light), ("dark", dark)):
        for foreground_name, background_name, minimum in CONTRAST_CHECKS:
            foreground = variables.get(foreground_name)
            background = variables.get(background_name)
            if foreground is None or background is None:
                continue
            if not HEX_RE.fullmatch(foreground) or not HEX_RE.fullmatch(background):
                errors.append(
                    f"{theme_name} contrast pair must use direct six-digit hex values: "
                    f"{foreground_name}={foreground}, {background_name}={background}"
                )
                continue
            ratio = contrast_ratio(foreground, background)
            if ratio + 1e-9 < minimum:
                errors.append(
                    f"{theme_name} contrast {foreground_name} on {background_name} "
                    f"is {ratio:.2f}:1; expected at least {minimum:.1f}:1"
                )

    required_global_tokens = {
        "--faa-font-display",
        "--faa-font-sans",
        "--faa-font-mono",
        "--faa-space-1",
        "--faa-space-16",
        "--faa-radius-card",
        "--faa-target-min",
        "--faa-layout-content-max",
        "--faa-duration-standard",
    }
    missing_global = sorted(required_global_tokens - light.keys())
    if missing_global:
        errors.append(f"global tokens are missing: {', '.join(missing_global)}")

    return len(light)


def validate_icons(errors: list[str]) -> int:
    tree = ET.parse(SPRITE_PATH)
    root = tree.getroot()
    if local_name(root.tag) != "svg":
        errors.append("icon sprite root must be an SVG element")
        return 0
    if root.attrib.get("aria-hidden") != "true":
        errors.append("icon sprite root must be aria-hidden=true")

    symbols = [element for element in root if local_name(element.tag) == "symbol"]
    symbol_ids = [symbol.attrib.get("id", "") for symbol in symbols]
    if len(symbol_ids) != len(set(symbol_ids)):
        errors.append("icon sprite contains duplicate symbol IDs")

    expected_symbol_attributes = {
        "viewBox": "0 0 24 24",
        "fill": "none",
        "stroke": "currentColor",
        "stroke-width": "1.75",
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
    }
    for symbol in symbols:
        symbol_id = symbol.attrib.get("id", "")
        if not symbol_id.startswith("faa-icon-"):
            errors.append(f"invalid icon symbol ID: {symbol_id}")
        for attribute, expected in expected_symbol_attributes.items():
            actual = symbol.attrib.get(attribute)
            if actual != expected:
                errors.append(
                    f"{symbol_id} has {attribute}={actual!r}; expected {expected!r}"
                )
        if len(list(symbol)) == 0:
            errors.append(f"{symbol_id} contains no geometry")
        for element in symbol.iter():
            name = local_name(element.tag)
            if name not in ALLOWED_ICON_TAGS:
                errors.append(f"{symbol_id} contains unsupported element: {name}")
            if name == "title":
                errors.append(f"{symbol_id} must not contain a reusable title")
            for color_attribute in ("fill", "stroke", "style", "class"):
                if element is symbol:
                    continue
                if color_attribute in element.attrib:
                    errors.append(
                        f"{symbol_id} child embeds {color_attribute}; "
                        "theme styling must remain on the symbol or host"
                    )

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = manifest.get("icons", [])
    names = [entry.get("name", "") for entry in entries]
    manifest_ids = [entry.get("id", "") for entry in entries]

    if names != sorted(names):
        errors.append("icon manifest names must be sorted")
    if len(names) != len(set(names)):
        errors.append("icon manifest contains duplicate names")
    if len(manifest_ids) != len(set(manifest_ids)):
        errors.append("icon manifest contains duplicate IDs")
    if set(manifest_ids) != set(symbol_ids):
        missing_from_manifest = sorted(set(symbol_ids) - set(manifest_ids))
        missing_from_sprite = sorted(set(manifest_ids) - set(symbol_ids))
        if missing_from_manifest:
            errors.append(
                "sprite symbols missing from manifest: " + ", ".join(missing_from_manifest)
            )
        if missing_from_sprite:
            errors.append(
                "manifest IDs missing from sprite: " + ", ".join(missing_from_sprite)
            )

    for entry in entries:
        name = entry.get("name", "")
        if entry.get("id") != f"faa-icon-{name}":
            errors.append(f"manifest ID does not match name for: {name}")
        if entry.get("category") not in ALLOWED_CATEGORIES:
            errors.append(f"invalid icon category for {name}: {entry.get('category')}")
        if not str(entry.get("label", "")).strip():
            errors.append(f"icon manifest label is missing for: {name}")

    if len(entries) < 50:
        errors.append("production icon baseline must contain at least 50 icons")

    icon_css = ICON_CSS_PATH.read_text(encoding="utf-8")
    if re.search(r"#[0-9a-fA-F]{3,8}\b", icon_css):
        errors.append("icon CSS must not embed theme color literals")
    for required_class in (".faa-icon", ".faa-icon-button", ".faa-icon--active"):
        if required_class not in icon_css:
            errors.append(f"icon CSS is missing required class: {required_class}")

    return len(entries)


def validate_documentation(errors: list[str]) -> None:
    style_guide = STYLE_GUIDE_PATH.read_text(encoding="utf-8")
    for required_reference in (
        "../../apps/web/src/design-system/tokens.css",
        "../../apps/web/src/design-system/icons/README.md",
        "dev-tools/design/check_design_system.py",
    ):
        if required_reference not in style_guide:
            errors.append(f"style guide is missing required reference: {required_reference}")


def main() -> int:
    errors: list[str] = []
    required_paths = [
        TOKENS_PATH,
        SPRITE_PATH,
        MANIFEST_PATH,
        ICON_CSS_PATH,
        STYLE_GUIDE_PATH,
    ]
    missing_paths = [str(path.relative_to(ROOT)) for path in required_paths if not path.is_file()]
    if missing_paths:
        print("Design-system validation failed:")
        for path in missing_paths:
            print(f"- missing required file: {path}")
        return 1

    token_count = validate_tokens(errors)
    try:
        icon_count = validate_icons(errors)
    except (ET.ParseError, json.JSONDecodeError) as error:
        errors.append(f"icon asset parse failure: {error}")
        icon_count = 0
    validate_documentation(errors)

    if errors:
        print("Design-system validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Design-system validation passed: "
        f"{token_count} light/global tokens and {icon_count} icons verified."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
