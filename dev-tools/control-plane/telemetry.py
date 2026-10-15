"""Append-only anonymous local telemetry and deterministic friction metrics."""

from __future__ import annotations

import json
import math
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from policy import write_report
from store import canonical_bytes, confined_path


FORBIDDEN_EVENT_FIELDS = {"args", "argv", "path", "paths", "prompt", "source", "stdout", "stderr", "work_id", "owner", "reviewer", "approval", "finding", "notes"}
SAFE_CATEGORY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
OUTCOMES = {"succeeded", "refused", "not-ready", "not-qualified", "unknown"}


class TelemetrySink:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.base = confined_path(self.root, ".local-codex/control-plane/telemetry")

    def emit(self, *, command_id: str, outcome: str, result_code: str, duration_ms: float, remediation_count: int) -> Path:
        if not SAFE_CATEGORY.fullmatch(command_id) or not SAFE_CATEGORY.fullmatch(result_code) or outcome not in OUTCOMES:
            raise ValueError("telemetry categories must use stable non-sensitive IDs")
        if not math.isfinite(duration_ms):
            raise ValueError("telemetry duration must be finite")
        now = datetime.now(timezone.utc)
        event = {
            "schema_version": "control-event-v1",
            "event_id": str(uuid.uuid4()),
            "recorded_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "command_id": command_id,
            "outcome": outcome,
            "result_code": result_code,
            "duration_ms": round(max(0.0, duration_ms), 3),
            "remediation_count": max(0, int(remediation_count)),
        }
        if FORBIDDEN_EVENT_FIELDS.intersection(event):
            raise ValueError("telemetry event contains forbidden fields")
        directory = confined_path(self.root, f".local-codex/control-plane/telemetry/{now:%Y%m%d}")
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{now:%H%M%S}-{event['event_id']}.json"
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(canonical_bytes(event))
            stream.flush()
            os.fsync(stream.fileno())
        return path

    def events(self) -> tuple[list[dict[str, Any]], int]:
        events: list[dict[str, Any]] = []
        malformed = 0
        if not self.base.is_dir():
            return events, malformed
        for path in sorted(self.base.glob("*/*.json")):
            try:
                value = json.loads(path.read_bytes())
                if not isinstance(value, dict) or value.get("schema_version") != "control-event-v1" or FORBIDDEN_EVENT_FIELDS.intersection(value):
                    raise ValueError("invalid event")
                events.append(value)
            except (OSError, ValueError, json.JSONDecodeError):
                malformed += 1
        return events, malformed

    def report(self) -> dict[str, Any]:
        events, malformed = self.events()
        durations = sorted(float(item.get("duration_ms", 0)) for item in events)
        refused = [item for item in events if item.get("outcome") in {"refused", "not-ready", "not-qualified"}]
        recovery = [item for item in events if item.get("command_id") in {"recover", "maintenance-action"}]
        verification = [item for item in events if item.get("command_id") == "verify"]
        p95_index = max(0, min(len(durations) - 1, int((len(durations) - 1) * 0.95))) if durations else 0
        return {
            "schema_version": "control-telemetry-report-v1",
            "event_count": len(events),
            "malformed_event_count": malformed,
            "outcomes": {key: sum(item.get("outcome") == key for item in events) for key in sorted({str(item.get("outcome")) for item in events})},
            "refusal_count": len(refused),
            "ambiguous_refusal_count": sum(int(item.get("remediation_count", 0)) == 0 for item in refused),
            "replay_count": sum("replayed" in str(item.get("result_code", "")) for item in events),
            "recovery": {"attempts": len(recovery), "succeeded": sum(item.get("outcome") == "succeeded" for item in recovery)},
            "verification": {"attempts": len(verification), "duration_ms_total": round(sum(float(item.get("duration_ms", 0)) for item in verification), 3)},
            "duration_ms": {"total": round(sum(durations), 3), "p95": durations[p95_index] if durations else 0.0},
        }

    def report_result(self, report_path: str | None = None) -> dict[str, Any]:
        from contracts import success

        report = self.report()
        written = write_report(self.root, report_path, report).relative_to(self.root).as_posix() if report_path else None
        return success("telemetry.reported", f"Aggregated {report['event_count']} anonymous event(s).", data={"report": report, "report_path": written})


def emit_safely(sink: TelemetrySink, **event: Any) -> bool:
    """Telemetry is deliberately unable to invalidate the governed operation."""

    try:
        sink.emit(**event)
    except (OSError, ValueError):
        return False
    return True
