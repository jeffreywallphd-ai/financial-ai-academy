"""Privacy-minimized provenance envelopes for control-plane outputs."""

from __future__ import annotations

import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from store import canonical_bytes


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def repository_revision(root: Path) -> str | None:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return completed.stdout.strip() if completed.returncode == 0 else None


def envelope(
    *,
    operation_id: str,
    output: object,
    revision: str | None = None,
    input_digest: str | None = None,
    capability_digest: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "control-provenance-v1",
        "producer": {"id": "local-control-plane", "version": "1.0"},
        "operation_id": operation_id,
        "revision": revision,
        "input_digest": input_digest,
        "capability_digest": capability_digest,
        "output_digest": digest(output),
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }


def attach(result: dict[str, Any], *, operation_id: str, root: Path) -> dict[str, Any]:
    core = {key: value for key, value in result.items() if key != "provenance"}
    return {**core, "provenance": envelope(operation_id=operation_id, output=core, revision=repository_revision(root))}


def validates(result: dict[str, Any]) -> bool:
    provenance = result.get("provenance")
    if not isinstance(provenance, dict):
        return False
    core = {key: value for key, value in result.items() if key != "provenance"}
    return provenance.get("output_digest") == digest(core)
