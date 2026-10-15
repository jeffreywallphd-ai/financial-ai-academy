"""Reusable packet-start, completed-correction, and maintenance controls."""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Protocol

from contracts import ControlError, success
from store import atomic_write, canonical_bytes, confined_path, exclusive_lock


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def append_once(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise ControlError(
            "evidence.append-conflict",
            "An append-only evidence record already occupies the generated identity.",
            {"record": path.name},
            ["Reload the existing record and retry only if the source facts changed."],
        ) from error
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(canonical_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())


class OperationsProjectPort(Protocol):
    def start_context(self, work_id: str) -> dict[str, Any]: ...

    def correction_context(self, work_id: str) -> dict[str, Any]: ...


def route_for_risk(risk: str, reason: str) -> dict[str, Any]:
    if risk not in {"low", "medium", "high"}:
        raise ControlError("start.risk-invalid", "The project adapter returned an unsupported risk tier.", {"risk": risk}, ["Map the packet to low, medium, or high risk."])
    steps = ["affected-verification"]
    if risk == "high":
        steps.append("aggregate-readiness")
    steps.append("independent-technical-review")
    return {"risk": risk, "reason": reason, "required_evidence": steps}


class PacketStartService:
    def __init__(self, root: Path, project: OperationsProjectPort) -> None:
        self.root = root.resolve()
        self.project = project
        self.base = confined_path(self.root, ".local-codex/control-plane/starts")

    def start(self, work_id: str) -> dict[str, Any]:
        context = self.project.start_context(work_id)
        route = route_for_risk(str(context["risk"]), str(context["risk_reason"]))
        core = {
            "schema_version": "packet-start-manifest-v1",
            "work_id": work_id,
            "claim_digest": digest(str(context["claim_id"])),
            "canonical_input_digest": str(context["canonical_input_digest"]),
            "acceptance_ids": sorted(str(value) for value in context["acceptance_ids"]),
            "acceptance_digest": str(context["acceptance_digest"]),
            "scope_digest": str(context["scope_digest"]),
            "route": route,
        }
        core["manifest_digest"] = digest(core)
        claim_key = hashlib.sha256(str(context["claim_id"]).encode("utf-8")).hexdigest()[:20]
        path = confined_path(self.root, f".local-codex/control-plane/starts/{work_id}/{claim_key}.json")
        if path.is_file():
            try:
                existing = json.loads(path.read_bytes())
            except (OSError, json.JSONDecodeError) as error:
                raise ControlError("start.manifest-malformed", "The existing packet-start manifest is unreadable and was preserved.", {"work_id": work_id}, ["Use bounded maintenance on that one manifest."]) from error
            if existing.get("manifest_digest") != core["manifest_digest"]:
                raise ControlError("start.planning-drift", "Packet scope or acceptance changed after this claim was started.", {"work_id": work_id}, ["Release and re-claim the packet so one new start manifest binds the revised plan."])
            return success("start.manifest-replayed", f"Replayed the unchanged start manifest for {work_id}.", data={"manifest": existing, "manifest_path": path.relative_to(self.root).as_posix(), "created": False})
        manifest = {**core, "recorded_at": utc_timestamp()}
        append_once(path, manifest)
        return success("start.manifest-recorded", f"Recorded the packet-start manifest for {work_id}.", data={"manifest": manifest, "manifest_path": path.relative_to(self.root).as_posix(), "created": True})


def normalized_path(value: str) -> str:
    posix = PurePosixPath(value.replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts or not posix.parts or re.match(r"^[A-Za-z]:", value):
        raise ControlError("correction.path-invalid", "Correction paths must be normalized repository-relative paths.", {"path": value}, ["Pass the exact repository-relative changed path."])
    return posix.as_posix()


def within_scope(path: str, scopes: list[str]) -> bool:
    for raw in scopes:
        scope = raw.replace("\\", "/").removesuffix("/**").rstrip("/")
        if path == scope or path.startswith(scope + "/"):
            return True
    return False


class CorrectionRouteService:
    def __init__(self, root: Path, project: OperationsProjectPort) -> None:
        self.root = root.resolve()
        self.project = project

    def plan(self, work_id: str, *, paths: list[str], reason_code: str) -> dict[str, Any]:
        if not paths:
            raise ControlError("correction.paths-required", "A correction route requires at least one affected path.", {}, ["Pass only the paths needed for the observed defect."])
        if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,63}", reason_code):
            raise ControlError("correction.reason-invalid", "Correction reason codes use lowercase letters, digits, dots, and hyphens.", {}, ["Use a stable non-sensitive defect code."])
        context = self.project.correction_context(work_id)
        normalized = sorted(set(normalized_path(value) for value in paths))
        escaped = [value for value in normalized if not within_scope(value, list(context["allowed_paths"]))]
        if escaped:
            raise ControlError("correction.scope-escape", "The proposed correction escapes the completed packet's bounded scope.", {"path_count": len(escaped)}, ["Shape the scope change at CAP level if it changes the approved package; otherwise choose an in-scope path."])
        core = {
            "schema_version": "correction-route-v1",
            "target_work_id": work_id,
            "parent_slice": str(context["parent_slice"]),
            "reason_code": reason_code,
            "paths": normalized,
            "scope_digest": digest(sorted(context["allowed_paths"])),
            "route": ["author-bounded-descendant-wrk", "affected-verification", "independent-technical-review", "deterministic-completion"],
        }
        core["route_digest"] = digest(core)
        key = core["route_digest"].split(":", 1)[1]
        path = confined_path(self.root, f".local-codex/control-plane/corrections/{work_id}/{key}.json")
        if path.is_file():
            record = json.loads(path.read_bytes())
            created = False
        else:
            record = {**core, "recorded_at": utc_timestamp()}
            append_once(path, record)
            created = True
        return success("correction.route-planned", f"Planned a bounded corrective route for {work_id}.", data={"route": record, "route_path": path.relative_to(self.root).as_posix(), "created": created})


MaintenanceAction = Callable[[], dict[str, Any]]


class MaintenanceService:
    def __init__(self, root: Path, actions: dict[str, MaintenanceAction], health_check: Callable[[], bool]) -> None:
        self.root = root.resolve()
        self.actions = dict(actions)
        self.health_check = health_check
        self.base = confined_path(self.root, ".local-codex/control-plane/maintenance")
        self.current_path = confined_path(self.root, ".local-codex/control-plane/maintenance/current.json")
        self.lock_path = confined_path(self.root, ".local-codex/control-plane/maintenance.lock")

    def _current(self) -> dict[str, Any] | None:
        if not self.current_path.is_file():
            return None
        try:
            value = json.loads(self.current_path.read_bytes())
        except (OSError, json.JSONDecodeError) as error:
            raise ControlError("maintenance.session-malformed", "The maintenance session pointer is unreadable and was preserved.", {}, ["Use repository backup evidence to restore this one ignored pointer."]) from error
        return value if isinstance(value, dict) else None

    def _event(self, session: dict[str, Any], event: str, outcome: str, details: dict[str, Any] | None = None) -> None:
        directory = confined_path(self.root, f".local-codex/control-plane/maintenance/{session['session_id']}")
        existing = [int(path.stem.split("-", 1)[1]) for path in directory.glob("event-*.json") if path.stem.split("-", 1)[1].isdigit()] if directory.is_dir() else []
        sequence = max([int(session.get("event_count", 0)), *existing], default=0) + 1
        record = {"schema_version": "maintenance-event-v1", "session_id": session["session_id"], "sequence": sequence, "event": event, "outcome": outcome, "recorded_at": utc_timestamp(), "details": details or {}}
        path = confined_path(self.root, f".local-codex/control-plane/maintenance/{session['session_id']}/event-{sequence:04d}.json")
        append_once(path, record)
        session["event_count"] = sequence

    def start(self, *, defect_code: str, allowed_action_ids: list[str]) -> dict[str, Any]:
        if not re.fullmatch(r"[a-z][a-z0-9.-]{2,79}", defect_code):
            raise ControlError("maintenance.defect-invalid", "Maintenance requires a stable non-sensitive defect code.", {}, ["Use the controller refusal code or a bounded diagnostic code."])
        requested = sorted(set(allowed_action_ids))
        unknown = [value for value in requested if value not in self.actions]
        if not requested or unknown:
            raise ControlError("maintenance.action-not-allowed", "Maintenance actions must be a non-empty subset of the registered action IDs.", {"unknown_action_ids": unknown}, ["Choose only an action ID shown by maintenance-status."])
        with exclusive_lock(self.lock_path):
            current = self._current()
            if current and current.get("status") == "active":
                raise ControlError("maintenance.already-active", "A maintenance session is already active.", {"session_id": current.get("session_id")}, ["Finish the active session before starting another."])
            session = {"schema_version": "maintenance-session-v1", "session_id": str(uuid.uuid4()), "status": "active", "defect_code": defect_code, "allowed_action_ids": requested, "successful_action_ids": [], "event_count": 0, "started_at": utc_timestamp()}
            self._event(session, "started", "succeeded", {"allowed_action_ids": requested})
            atomic_write(self.current_path, canonical_bytes(session))
        return success("maintenance.started", "Entered bounded control-plane maintenance.", data={"session": session})

    def execute(self, action_id: str) -> dict[str, Any]:
        with exclusive_lock(self.lock_path):
            session = self._current()
            if not session or session.get("status") != "active":
                raise ControlError("maintenance.not-active", "No maintenance session is active.", {}, ["Start a bounded session with the required action ID."])
            if action_id not in session.get("allowed_action_ids", []) or action_id not in self.actions:
                raise ControlError("maintenance.action-not-allowed", "The action is outside this session's frozen allowlist.", {"action_id": action_id}, ["Finish and start a new bounded session if a different registered action is required."])
            try:
                details = self.actions[action_id]()
            except ControlError as error:
                self._event(session, action_id, "failed", {"error_code": error.code})
                atomic_write(self.current_path, canonical_bytes(session))
                raise
            successful = sorted(set(session.get("successful_action_ids", [])) | {action_id})
            session["successful_action_ids"] = successful
            self._event(session, action_id, "succeeded", details)
            atomic_write(self.current_path, canonical_bytes(session))
        return success("maintenance.action-succeeded", f"Completed registered maintenance action {action_id}.", data={"action_id": action_id, "details": details})

    def finish(self) -> dict[str, Any]:
        with exclusive_lock(self.lock_path):
            session = self._current()
            if not session or session.get("status") != "active":
                raise ControlError("maintenance.not-active", "No maintenance session is active.", {}, ["No exit action is needed."])
            if not session.get("successful_action_ids"):
                raise ControlError("maintenance.no-success", "Maintenance cannot exit before one allowed action succeeds.", {}, ["Run the narrow registered action that addresses the defect."])
            if not self.health_check():
                raise ControlError("maintenance.health-failed", "Maintenance health validation still fails.", {}, ["Run another allowed repair action or preserve the session for diagnosis."])
            session["status"] = "closed"
            session["closed_at"] = utc_timestamp()
            self._event(session, "finished", "succeeded", {"health": "passed"})
            atomic_write(self.current_path, canonical_bytes(session))
        return success("maintenance.finished", "Exited bounded control-plane maintenance after health validation.", data={"session": session})

    def status(self) -> dict[str, Any]:
        session = self._current()
        return success("maintenance.status", "Reported bounded maintenance state.", data={"active": bool(session and session.get("status") == "active"), "session": session, "registered_action_ids": sorted(self.actions)})

    def guard_mutation(self, command: str) -> None:
        session = self._current()
        if session and session.get("status") == "active":
            raise ControlError("maintenance.blocks-mutation", "Normal control-plane mutations are paused during bounded maintenance.", {"command": command, "session_id": session.get("session_id")}, ["Finish the active maintenance session after health validation."])
