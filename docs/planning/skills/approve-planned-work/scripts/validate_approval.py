#!/usr/bin/env python3
"""Validate one human decision from the ignored local approval ledger."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from approval_store import ApprovalStoreError, STAGES, load_store, require_decision


def repository_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() and (candidate / "docs").is_dir():
            return candidate
    raise ApprovalStoreError("unable to locate repository root")


def metadata(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0] != "---":
        return {}
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}
    result: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line and not line.startswith((" ", "-")):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip(chr(34))
    return result


def scope_items(value: object) -> list[str]:
    text = "" if value is None else str(value).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return []
        values = parsed if isinstance(parsed, list) else []
    else:
        values = [text]
    return sorted({
        str(item)
        .strip()
        .replace(chr(92), "/")
        .removeprefix("./")
        .removesuffix("/**")
        .rstrip("/")
        for item in values
        if str(item).strip()
    })


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--stage", choices=sorted(STAGES), required=True)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--store", type=Path)
    args = parser.parse_args()
    if not args.artifact.is_file():
        parser.error(f"file not found: {args.artifact}")
    try:
        root = (args.root or repository_root(args.artifact)).resolve()
        text = args.artifact.read_text(encoding="utf-8")
        data = metadata(text)
        identifier = data.get("id", "")
        errors: list[str] = []
        if not re.match(r"^(CAP|DEC|SLI|WRK)-\d{4,}$", identifier):
            errors.append("artifact must contain a planning ID")
        forbidden = [
            key for key in data
            if key.endswith(("_approval", "_approved_by", "_approved_at"))
            or key == "implementation_authority"
        ]
        if forbidden:
            errors.append(
                "tracked artifact contains local-only approval metadata: "
                + ", ".join(forbidden)
            )
        if "## Approval History" in text:
            errors.append("tracked artifact must not contain Approval History")
        if errors:
            raise ApprovalStoreError("; ".join(errors))
        store, _path = load_store(root, args.store, required=True)
        record = require_decision(store, identifier, args.stage)
        if args.stage == "implementation":
            if scope_items(record.get("scope")) != scope_items(data.get("write_scope")):
                raise ApprovalStoreError(
                    "approved implementation scope must exactly match artifact write_scope"
                )
            bundle_subject = str(record.get("bundle_subject", "")).strip()
            if bundle_subject and bundle_subject != data.get("parent"):
                raise ApprovalStoreError(
                    "implementation bundle subject must match the packet parent"
                )
        if args.stage == "decision" and data.get("planning_status") == "complete":
            if data.get("decision_record") in {"", "null", None}:
                raise ApprovalStoreError(
                    "complete decision request requires canonical decision_record"
                )
        print(f"Local approval validation passed: {args.stage} on {identifier}")
        return 0
    except (OSError, RuntimeError, ApprovalStoreError, ValueError) as error:
        print(f"Approval validation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
