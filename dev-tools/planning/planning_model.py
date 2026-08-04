#!/usr/bin/env python3
"""Shared, dependency-free model helpers for planning automation."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ARTIFACT_LOCATIONS = {
    "CAP": ("docs/planning/capabilities", "capability"),
    "DEC": ("docs/planning/decision-requests", "decision-request"),
    "SLI": ("docs/planning/vertical-slices", "vertical-slice"),
    "WRK": ("docs/planning/work-packets", "work-packet"),
}
ID_RE = re.compile(r"^(CAP|DEC|SLI|WRK)-(\d{4,})$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)
NULL_VALUES = {"", "null", "none", "unassigned"}


@dataclass(frozen=True)
class Artifact:
    """A planning artifact and its parsed frontmatter."""

    path: Path
    relative_path: str
    metadata: dict[str, object]

    @property
    def identifier(self) -> str:
        return str(self.metadata.get("id", ""))

    @property
    def kind(self) -> str:
        return str(self.metadata.get("kind", ""))

    @property
    def status(self) -> str:
        return str(self.metadata.get("planning_status", ""))


def repository_root(start: Path | None = None) -> Path:
    """Find the nearest repository root without invoking a shell."""

    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() and (candidate / "docs").is_dir():
            return candidate
    raise RuntimeError("Unable to locate repository root")


def parse_value(raw: str) -> object:
    """Parse the small YAML-compatible subset used by planning metadata."""

    value = raw.strip()
    if value in {"null", "~"}:
        return None
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            body = value[1:-1].strip()
            if not body:
                return []
            return [item.strip().strip("\"'") for item in body.split(",")]
        return parsed
    return value.strip("\"'")


def parse_frontmatter(text: str) -> tuple[dict[str, object], int]:
    """Return frontmatter and the closing delimiter line index."""

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, -1
    try:
        end = next(
            index for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        )
    except StopIteration:
        return {}, -1

    data: dict[str, object] = {}
    for line in lines[1:end]:
        if not line or line.startswith((" ", "-", "#")) or ":" not in line:
            continue
        key, raw = line.split(":", 1)
        data[key.strip()] = parse_value(raw)
    return data, end


def frontmatter_from_path(path: Path) -> dict[str, object]:
    return parse_frontmatter(path.read_text(encoding="utf-8"))[0]


def as_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [as_text(item) for item in value if as_text(item)]
    text = as_text(value)
    if not text or text == "[]":
        return []
    return [text]


def is_present(value: object) -> bool:
    return as_text(value).lower() not in NULL_VALUES


def normalize_repo_path(value: str) -> str:
    """Normalize a declared repository-relative write scope."""

    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.endswith("/**"):
        normalized = normalized[:-3]
    return normalized.rstrip("/")


def scopes_overlap(left: Iterable[str], right: Iterable[str]) -> bool:
    """Conservatively detect exact or parent/child write-scope overlap."""

    left_paths = [normalize_repo_path(item) for item in left]
    right_paths = [normalize_repo_path(item) for item in right]
    for first in left_paths:
        for second in right_paths:
            if not first or not second:
                continue
            if first == second:
                return True
            if first.startswith(second + "/") or second.startswith(first + "/"):
                return True
    return False


def load_artifacts(root: Path) -> list[Artifact]:
    artifacts: list[Artifact] = []
    for prefix, (directory, _kind) in ARTIFACT_LOCATIONS.items():
        location = root / directory
        if not location.is_dir():
            continue
        for path in sorted(location.glob(f"{prefix}-*.md")):
            metadata = frontmatter_from_path(path)
            artifacts.append(
                Artifact(
                    path=path,
                    relative_path=path.relative_to(root).as_posix(),
                    metadata=metadata,
                )
            )
    return artifacts


def git_output(root: Path, arguments: list[str]) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=root, check=False, capture_output=True,
        text=True, encoding="utf-8", errors="replace",
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or "git command failed")
    return completed.stdout


def git_revision(root: Path, revision: str = "HEAD") -> str:
    return git_output(root, ["rev-parse", "--verify", revision]).strip()


def frontmatter_at_revision(
    root: Path, revision: str, relative_path: str
) -> dict[str, object] | None:
    completed = subprocess.run(
        ["git", "show", f"{revision}:{relative_path}"], cwd=root, check=False,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if completed.returncode:
        return None
    return parse_frontmatter(completed.stdout)[0]


def format_value(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def update_frontmatter(path: Path, updates: dict[str, object]) -> None:
    """Atomically update existing frontmatter fields while preserving the body."""

    text = path.read_text(encoding="utf-8")
    data, end = parse_frontmatter(text)
    if end < 0:
        raise ValueError(f"Missing frontmatter: {path}")
    missing = set(updates) - set(data)
    if missing:
        raise ValueError(
            "Cannot add undeclared metadata fields: " + ", ".join(sorted(missing))
        )
    lines = text.splitlines()
    pending = dict(updates)
    for index in range(1, end):
        line = lines[index]
        if line.startswith((" ", "-", "#")) or ":" not in line:
            continue
        key = line.split(":", 1)[0].strip()
        if key in pending:
            lines[index] = f"{key}: {format_value(pending.pop(key))}"
    if pending:
        raise ValueError("Unable to update metadata fields")
    newline = "\r\n" if "\r\n" in text else "\n"
    rendered = newline.join(lines) + (newline if text.endswith(("\n", "\r")) else "")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8", newline="")
    temporary.replace(path)
