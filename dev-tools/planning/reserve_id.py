#!/usr/bin/env python3
"""Reserve or consume planning IDs using ignored, atomic local state."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from planning_model import ARTIFACT_LOCATIONS, ID_RE, load_artifacts, repository_root


def state_directory(root: Path) -> Path:
    return root / ".local-codex/planning-reservations"


def reservation_files(root: Path) -> list[Path]:
    directory = state_directory(root)
    return sorted(directory.glob("*.json")) if directory.is_dir() else []


def read_reservations(root: Path) -> dict[str, dict[str, str]]:
    reservations: dict[str, dict[str, str]] = {}
    for path in reservation_files(root):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Invalid reservation file {path}: {error}") from error
        identifier = str(data.get("id", ""))
        if not ID_RE.match(identifier):
            raise ValueError(f"Invalid reservation id in {path}")
        reservations[identifier] = {str(key): str(value) for key, value in data.items()}
    return reservations


def acquire_lock(root: Path) -> Path:
    directory = state_directory(root)
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / ".reserve.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise RuntimeError("Another planning ID reservation is in progress") from error
    os.close(descriptor)
    return lock


def reserve(root: Path, kind: str, owner: str) -> dict[str, str]:
    if kind not in ARTIFACT_LOCATIONS:
        raise ValueError("kind must be CAP, DEC, SLI, or WRK")
    if not owner.strip():
        raise ValueError("owner is required")
    lock = acquire_lock(root)
    try:
        used = {artifact.identifier for artifact in load_artifacts(root)}
        used.update(read_reservations(root))
        numbers = [
            int(identifier.split("-", 1)[1])
            for identifier in used if identifier.startswith(kind + "-")
        ]
        number = max(numbers, default=0) + 1
        identifier = f"{kind}-{number:04d}"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        record = {"id": identifier, "owner": owner.strip(), "reserved_at": now}
        target = state_directory(root) / f"{identifier}.json"
        descriptor = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(record, handle, indent=2, sort_keys=True)
            handle.write("\n")
        return record
    finally:
        lock.unlink(missing_ok=True)


def consume(root: Path, identifier: str, owner: str, artifact: Path) -> dict[str, str]:
    if not ID_RE.match(identifier):
        raise ValueError("identifier must match CAP|DEC|SLI|WRK-####")
    target = state_directory(root) / f"{identifier}.json"
    if not target.is_file():
        raise ValueError(f"No local reservation exists for {identifier}")
    record = json.loads(target.read_text(encoding="utf-8"))
    if record.get("owner") != owner:
        raise ValueError("Only the reservation owner may consume it")
    resolved = (artifact if artifact.is_absolute() else root / artifact).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError("artifact must be inside the repository") from error
    if not resolved.is_file():
        raise ValueError("artifact must exist before its reservation is consumed")
    matching = [item for item in load_artifacts(root) if item.identifier == identifier]
    if len(matching) != 1 or matching[0].path.resolve() != resolved:
        raise ValueError("artifact id/path does not match the reservation")
    target.unlink()
    return {
        "id": identifier,
        "owner": owner,
        "artifact": resolved.relative_to(root).as_posix(),
        "status": "consumed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)
    reserve_parser = subparsers.add_parser("reserve")
    reserve_parser.add_argument("--kind", choices=sorted(ARTIFACT_LOCATIONS), required=True)
    reserve_parser.add_argument("--owner", required=True)
    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(command="list")
    consume_parser = subparsers.add_parser("consume")
    consume_parser.add_argument("identifier")
    consume_parser.add_argument("--owner", required=True)
    consume_parser.add_argument("--artifact", type=Path, required=True)
    args = parser.parse_args()
    try:
        root = (args.root or repository_root()).resolve()
        if args.command == "reserve":
            result = reserve(root, args.kind, args.owner)
        elif args.command == "consume":
            result = consume(root, args.identifier, args.owner, args.artifact)
        else:
            result = list(read_reservations(root).values())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exception:
        print(f"Planning ID operation failed: {exception}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
