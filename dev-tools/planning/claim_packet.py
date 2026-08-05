#!/usr/bin/env python3
"""Preview, claim, or release a locally approved agent work packet."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from approval_store import ApprovalStoreError, load_store, require_decision

from planning_model import (
    as_list,
    as_text,
    frontmatter_from_path,
    git_revision,
    load_artifacts,
    normalize_repo_path,
    repository_root,
    scopes_overlap,
    update_frontmatter,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def resolve_packet(root: Path, requested: Path) -> Path:
    path = requested if requested.is_absolute() else root / requested
    path = path.resolve()
    expected = (root / "docs/planning/work-packets").resolve()
    try:
        path.relative_to(expected)
    except ValueError as error:
        raise ValueError("packet must be under docs/planning/work-packets") from error
    if not path.is_file():
        raise ValueError(f"packet not found: {path}")
    return path


def packet_lock(root: Path, identifier: str) -> Path:
    directory = root / ".local-codex/planning-locks"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{identifier}.lock"
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise RuntimeError(f"Another claim operation is in progress for {identifier}") from error
    os.close(descriptor)
    return path


def normalized_scope(value: object) -> list[str]:
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("["):
            try:
                value = json.loads(text)
            except json.JSONDecodeError as error:
                raise ValueError("implementation approval scope must be a JSON array") from error
        else:
            value = [text]
    return sorted({
        normalize_repo_path(item)
        for item in as_list(value)
        if normalize_repo_path(item)
    })


def claim_updates(
    root: Path, path: Path, owner: str, authority: str, base_revision: str
) -> dict[str, object]:
    data = frontmatter_from_path(path)
    if data.get("kind") != "work-packet" or not as_text(data.get("id")).startswith("WRK-"):
        raise ValueError("target is not a work packet")
    if data.get("planning_status") != "ready":
        raise ValueError("only a ready packet may be claimed")
    store, _store_path = load_store(root, required=True)
    identifier = as_text(data.get("id"))
    require_decision(store, identifier, "planning")
    implementation = require_decision(store, identifier, "implementation")
    if as_text(implementation.get("authority")) != authority:
        raise ValueError("--authority must exactly match the local implementation authority")
    scopes = as_list(data.get("write_scope"))
    generated = as_list(data.get("generated_artifacts"))
    if not scopes:
        raise ValueError("packet must declare a non-empty write_scope")
    if normalized_scope(implementation.get("scope")) != normalized_scope(scopes):
        raise ValueError(
            "local implementation approval scope must exactly match the packet write_scope"
        )
    artifacts = load_artifacts(root)
    by_id = {artifact.identifier: artifact for artifact in artifacts}
    for dependency in as_list(data.get("depends_on")):
        if dependency not in by_id:
            raise ValueError(f"dependency {dependency} does not exist")
        if by_id[dependency].status != "complete":
            raise ValueError(f"dependency {dependency} must be complete before claim")
    for artifact in artifacts:
        if artifact.kind != "work-packet" or artifact.status != "active":
            continue
        other_scopes = as_list(artifact.metadata.get("write_scope"))
        other_generated = as_list(artifact.metadata.get("generated_artifacts"))
        if any((
            scopes_overlap(scopes, other_scopes),
            scopes_overlap(scopes, other_generated),
            scopes_overlap(generated, other_scopes),
            scopes_overlap(generated, other_generated),
        )):
            raise ValueError(f"write scope overlaps active packet {artifact.identifier}")
        if (
            artifact.identifier not in as_list(data.get("parallel_safe_with"))
            or as_text(data.get("id")) not in as_list(
                artifact.metadata.get("parallel_safe_with")
            )
        ):
            raise ValueError(
                f"packet does not declare reciprocal parallel safety with {artifact.identifier}"
            )
    if not owner.strip():
        raise ValueError("owner is required")
    return {
        "planning_status": "active",
        "owner": owner.strip(),
        "updated": utc_now().split("T", 1)[0],
        "base_revision": base_revision,
        "claim_id": f"{data['id']}:{uuid.uuid4()}",
        "claimed_by": owner.strip(),
        "claimed_at": utc_now(),
    }


def release_updates(path: Path, owner: str, target_status: str) -> dict[str, object]:
    data = frontmatter_from_path(path)
    if data.get("planning_status") not in {"active", "verifying"}:
        raise ValueError("only an active or verifying packet may be released")
    if as_text(data.get("claimed_by")) != owner:
        raise ValueError("only the recorded claim owner may release the packet")
    if target_status not in {"ready", "verifying"}:
        raise ValueError("release target must be ready or verifying")
    if target_status == "verifying" and data.get("planning_status") != "active":
        raise ValueError("only an active packet may move to verifying")
    return {
        "planning_status": target_status,
        "updated": utc_now().split("T", 1)[0],
    }


def finalize_updates(path: Path, owner: str) -> dict[str, object]:
    data = frontmatter_from_path(path)
    if data.get("planning_status") != "verifying":
        raise ValueError("only a verifying packet may be finalized")
    if as_text(data.get("claimed_by")) != owner:
        raise ValueError("only the recorded claim owner may finalize the packet")
    return {
        "planning_status": "complete",
        "updated": utc_now().split("T", 1)[0],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("packet", type=Path)
    claim_parser = subparsers.add_parser("claim")
    claim_parser.add_argument("packet", type=Path)
    claim_parser.add_argument("--owner", required=True)
    claim_parser.add_argument("--authority", required=True)
    claim_parser.add_argument("--base-revision")
    claim_parser.add_argument(
        "--confirm-current-instruction", action="store_true",
        help="confirm a current explicit instruction authorizes this named packet",
    )
    claim_parser.add_argument("--apply", action="store_true")
    release_parser = subparsers.add_parser("release")
    release_parser.add_argument("packet", type=Path)
    release_parser.add_argument("--owner", required=True)
    release_parser.add_argument("--to", choices=("ready", "verifying"), required=True)
    release_parser.add_argument("--apply", action="store_true")
    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("packet", type=Path)
    finalize_parser.add_argument("--owner", required=True)
    finalize_parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        root = (args.root or repository_root()).resolve()
        path = resolve_packet(root, args.packet)
        data = frontmatter_from_path(path)
        if args.command == "status":
            output = data
        else:
            identifier = as_text(data.get("id"))
            if args.command == "claim":
                if not args.confirm_current_instruction:
                    raise ValueError("claim requires --confirm-current-instruction")
                base = git_revision(root, args.base_revision or "HEAD")
                updates = claim_updates(root, path, args.owner, args.authority, base)
            elif args.command == "release":
                updates = release_updates(path, args.owner, args.to)
            else:
                updates = finalize_updates(path, args.owner)
            output = {
                "packet": path.relative_to(root).as_posix(),
                "operation": args.command,
                "apply": args.apply,
                "updates": updates,
                "register_update_required": True,
            }
            if args.apply:
                lock = packet_lock(root, identifier)
                try:
                    update_frontmatter(path, updates)
                finally:
                    lock.unlink(missing_ok=True)
    except (OSError, RuntimeError, ApprovalStoreError, ValueError) as exception:
        print(f"Work-packet claim operation failed: {exception}", file=sys.stderr)
        return 1
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
