#!/usr/bin/env python3
"""Install canonical planning skills into a supported Codex discovery directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "suite-manifest.json"
MARKER = ".planning-skill-install.json"
IGNORED_PARTS = {"__pycache__", ".pytest_cache"}
IGNORED_SUFFIXES = {".pyc", ".pyo", ".zip"}


def repository_root() -> Path:
    for candidate in (ROOT, *ROOT.parents):
        if (candidate / ".git").exists() and (candidate / "docs").is_dir():
            return candidate
    raise RuntimeError("Unable to locate repository root")


def skill_names() -> list[str]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return [str(entry["name"]) for entry in data.get("skills", [])]


def included_files(source: Path) -> list[Path]:
    return sorted(
        path for path in source.rglob("*")
        if path.is_file()
        and not any(part in IGNORED_PARTS for part in path.relative_to(source).parts)
        and path.suffix not in IGNORED_SUFFIXES
        and path.name != MARKER
    )


def digest(source: Path) -> str:
    value = hashlib.sha256()
    for path in included_files(source):
        relative = path.relative_to(source).as_posix().encode("utf-8")
        value.update(len(relative).to_bytes(4, "big"))
        value.update(relative)
        content = path.read_bytes()
        value.update(len(content).to_bytes(8, "big"))
        value.update(content)
    return value.hexdigest()


def marker_data(source: Path) -> dict[str, object]:
    root = repository_root()
    return {
        "managedBy": "docs/planning/skills/sync_skills.py",
        "canonicalSource": source.relative_to(root).as_posix(),
        "sha256": digest(source),
        "contractVersion": json.loads(MANIFEST.read_text(encoding="utf-8"))["contractVersion"],
    }


def managed_copy(path: Path) -> bool:
    marker = path / MARKER
    if not marker.is_file():
        return False
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return data.get("managedBy") == "docs/planning/skills/sync_skills.py"


def remove_managed(path: Path) -> None:
    if path.is_symlink():
        path.unlink()
    elif path.is_dir() and managed_copy(path):
        shutil.rmtree(path)
    elif path.exists():
        raise ValueError(f"Refusing to replace unmanaged target: {path}")


def install_copy(source: Path, target: Path) -> None:
    target.mkdir(parents=True)
    for path in included_files(source):
        destination = target / path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    (target / MARKER).write_text(
        json.dumps(marker_data(source), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def install_one(source: Path, target: Path, mode: str) -> str:
    if target.exists() or target.is_symlink():
        remove_managed(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    if mode in {"auto", "symlink"}:
        try:
            target.symlink_to(source, target_is_directory=True)
            return "symlink"
        except OSError:
            if mode == "symlink":
                raise
    install_copy(source, target)
    return "copy"


def check_one(source: Path, target: Path) -> str | None:
    if target.is_symlink():
        try:
            if target.resolve(strict=True) == source.resolve(strict=True):
                return None
        except OSError:
            pass
        return "symlink does not resolve to the canonical source"
    if not target.is_dir():
        return "target is missing"
    marker = target / MARKER
    if not marker.is_file():
        return "target is an unmanaged copy"
    try:
        actual_marker = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "installation marker is invalid"
    expected = marker_data(source)
    if actual_marker != expected:
        return "installation marker is stale or does not match canonical source"
    if digest(target) != digest(source):
        return "installed copy has drifted from canonical source"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, help="skills discovery directory")
    parser.add_argument("--mode", choices=("auto", "copy", "symlink"), default="auto")
    parser.add_argument("--check", action="store_true", help="verify without changing files")
    args = parser.parse_args()
    try:
        root = repository_root()
        target_root = (args.target or root / ".agents/skills").expanduser().resolve()
        if args.target is None:
            try:
                target_root.relative_to(root)
            except ValueError as error:
                raise ValueError(
                    "default .agents/skills target resolves outside the repository"
                ) from error
        names = skill_names()
        results: dict[str, str] = {}
        errors: list[str] = []
        for name in names:
            source = ROOT / name
            target = target_root / name
            if args.check:
                issue = check_one(source, target)
                if issue:
                    errors.append(f"{name}: {issue}")
                else:
                    results[name] = "current"
            else:
                results[name] = install_one(source, target, args.mode)
        if errors:
            print("Planning skill discovery check failed:")
            for issue in errors:
                print(f"- {issue}")
            return 1
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exception:
        print(f"Planning skill synchronization failed: {exception}", file=sys.stderr)
        return 2
    operation = "verified" if args.check else "installed"
    print(json.dumps({"operation": operation, "target": str(target_root), "skills": results}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
