"""Project-neutral, repository-local exact-file edit coordination."""

from __future__ import annotations

import copy
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable

from contracts import ControlError, success
from state import parse_timestamp, timestamp, utc_now
from store import atomic_write, canonical_bytes, confined_path, exclusive_lock, normalize_resolved_path


SCHEMA_VERSION = "file-edit-state-v1"
DEFAULT_FILE_LEASE_MINUTES = 15
MAX_FILE_LEASE_MINUTES = 120
DEFAULT_INTENT_MINUTES = 5
Clock = Callable[[], datetime]


def canonical_file(root: Path, value: str) -> tuple[str, str]:
    """Return display path and host-normalized key for one repository file."""

    target = confined_path(root.resolve(), value)
    if target.exists() and target.is_dir():
        raise ControlError("edit.path-is-directory", "File-edit leases require an exact file, not a directory.", {"path": value}, ["Name the exact repository file immediately before editing it."])
    resolved_root = normalize_resolved_path(root)
    resolved = normalize_resolved_path(target)
    try:
        relative = resolved.relative_to(resolved_root).as_posix()
    except ValueError as error:
        raise ControlError("edit.path-outside-repository", "The canonical edit target escapes the repository.", {"path": value}, ["Choose an exact file within the repository checkout."]) from error
    if not relative or relative == ".":
        raise ControlError("edit.path-is-directory", "The repository root cannot be leased as a file.", {"path": value}, ["Name the exact file to edit."])
    return relative, relative.casefold()


def canonical_files(root: Path, values: Iterable[str]) -> list[tuple[str, str]]:
    paths = [canonical_file(root, value) for value in values]
    if not paths:
        raise ControlError("edit.paths-empty", "At least one exact file path is required.", {}, ["Name the bounded files about to be edited."])
    keys = [key for _display, key in paths]
    if len(keys) != len(set(keys)):
        raise ControlError("edit.paths-duplicate", "The request names the same canonical file more than once.", {"paths": [display for display, _key in paths]}, ["Remove case, separator, relative, or symlink aliases from the request."])
    return sorted(paths, key=lambda item: item[1])


def _stored_path_key_pair_is_canonical(path: str, key: str) -> bool:
    parts = path.split("/")
    return bool(path) and "\\" not in path and not path.startswith("/") and all(part not in {"", ".", ".."} for part in parts) and path.casefold() == key


def _duration(minutes: int, *, maximum: int = MAX_FILE_LEASE_MINUTES) -> None:
    if not 1 <= minutes <= maximum:
        raise ControlError("edit.duration-invalid", f"Duration must be between 1 and {maximum} minutes.", {"minutes": minutes}, [f"Choose a duration from 1 through {maximum} minutes."])


class FileLeaseStore:
    """Atomic local persistence for intents and exclusive exact-file leases."""

    def __init__(self, root: Path, *, clock: Clock = utc_now) -> None:
        self.root = root.resolve()
        self.clock = clock
        self.path = confined_path(self.root, ".local-codex/control-plane/file-leases.json")
        self.lock_path = confined_path(self.root, ".local-codex/control-plane/file-leases.lock")

    @staticmethod
    def empty() -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "revision": 0, "intents": {}, "leases": {}, "path_owners": {}, "history": []}

    def _load(self) -> dict[str, Any]:
        if not self.path.is_file():
            return self.empty()
        try:
            state = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ControlError("edit.state-malformed", "File-edit coordination state is unreadable and was preserved.", {}, ["Use bounded local maintenance; do not edit lease state by hand."]) from error
        required = {"revision", "intents", "leases", "path_owners", "history"}
        if not isinstance(state, dict) or state.get("schema_version") != SCHEMA_VERSION or not required <= set(state):
            raise ControlError("edit.state-incompatible", "File-edit coordination state uses an incompatible schema.", {"schema_version": state.get("schema_version") if isinstance(state, dict) else None}, ["Use a compatible controller or a documented local migration."])
        if not isinstance(state["revision"], int) or any(not isinstance(state[name], dict) for name in ("intents", "leases", "path_owners")) or not isinstance(state["history"], list):
            raise ControlError("edit.state-malformed", "File-edit coordination state has invalid field types.", {}, ["Use bounded local maintenance; preserve the malformed bytes."])
        return state

    @staticmethod
    def _event(state: dict[str, Any], event_type: str, now: datetime, details: dict[str, Any]) -> None:
        state["history"].append({"sequence": len(state["history"]) + 1, "type": event_type, "at": timestamp(now), "details": details})

    def _mutate(self, transition: Callable[[dict[str, Any], datetime], dict[str, Any]], *, expected_revision: int | None = None) -> dict[str, Any]:
        with exclusive_lock(self.lock_path):
            current = self._load()
            if expected_revision is not None and current["revision"] != expected_revision:
                raise ControlError("edit.revision-conflict", "File-edit state changed after the caller observed it.", {"expected_revision": expected_revision, "actual_revision": current["revision"]}, ["Read edit-status and retry with the current revision."])
            successor = transition(copy.deepcopy(current), self.clock())
            successor["revision"] = current["revision"] + 1
            atomic_write(self.path, canonical_bytes(successor))
            return successor

    def announce(self, *, unit_id: str, work_id: str, owner: str, claim_id: str, paths: list[str], minutes: int = DEFAULT_INTENT_MINUTES, expected_revision: int | None = None) -> dict[str, Any]:
        _duration(minutes, maximum=30)
        canonical = canonical_files(self.root, paths)
        created_intent_id = ""

        def transition(state: dict[str, Any], now: datetime) -> dict[str, Any]:
            nonlocal created_intent_id
            intent_id = f"intent:{uuid.uuid4()}"
            created_intent_id = intent_id
            record = {"schema_version": "file-edit-intent-v1", "intent_id": intent_id, "unit_id": unit_id, "work_id": work_id, "owner": owner, "claim_id": claim_id, "paths": [display for display, _key in canonical], "announced_at": timestamp(now), "expires_at": timestamp(now + timedelta(minutes=minutes))}
            state["intents"][intent_id] = record
            self._event(state, "intent-announced", now, {"intent_id": intent_id, "unit_id": unit_id, "work_id": work_id, "path_count": len(canonical)})
            return state

        state = self._mutate(transition, expected_revision=expected_revision)
        record = state["intents"][created_intent_id]
        return success("edit.intent-announced", "Published bounded edit intent; intent does not lock files.", revision=state["revision"], data={"intent": record})

    def acquire(self, *, unit_id: str, work_id: str, owner: str, claim_id: str, paths: list[str], lease_minutes: int = DEFAULT_FILE_LEASE_MINUTES, expected_revision: int | None = None, recovery: bool = False) -> dict[str, Any]:
        _duration(lease_minutes)
        canonical = canonical_files(self.root, paths)
        created_lease_id = ""

        def transition(state: dict[str, Any], now: datetime) -> dict[str, Any]:
            nonlocal created_lease_id
            conflicts: list[dict[str, Any]] = []
            expired_ids: set[str] = set()
            unowned_paths: list[str] = []
            for display, key in canonical:
                lease_id = state["path_owners"].get(key)
                if not lease_id:
                    unowned_paths.append(display)
                    continue
                lease = state["leases"].get(lease_id)
                if not isinstance(lease, dict):
                    raise ControlError("edit.state-malformed", "A path owner references a missing lease.", {"path": display}, ["Use bounded local maintenance."])
                expired = parse_timestamp(str(lease["leased_until"])) <= now
                if expired:
                    expired_ids.add(str(lease_id))
                else:
                    conflicts.append({"path": display, "unit_id": lease["unit_id"], "work_id": lease["work_id"], "leased_until": lease["leased_until"]})
            if conflicts:
                raise ControlError("edit.lease-contended", "At least one requested file has a live editing owner; nothing was acquired.", {"conflicts": conflicts}, ["Coordinate with the active lane or retry after explicit release or expiry."])
            if expired_ids and not recovery:
                raise ControlError("edit.recovery-required", "At least one requested file has an expired lease requiring explicit recovery; nothing was acquired.", {"expired_lease_ids": sorted(expired_ids)}, ["Use edit-recover to preserve recovery lineage."])
            if recovery and expired_ids and unowned_paths:
                raise ControlError("edit.recovery-path-unowned", "Recovery cannot acquire paths that have no expired owner; nothing was acquired.", {"paths": unowned_paths}, ["Recover only expired paths, then use edit-acquire separately for currently unowned files."])
            if recovery and not expired_ids:
                raise ControlError("edit.recovery-not-applicable", "Recovery requires at least one expired lease on the requested files.", {}, ["Use edit-acquire for currently unowned files."])
            recovered_from = sorted(expired_ids)
            requested_keys = {key for _display, key in canonical}
            validated_prior: dict[str, tuple[dict[str, Any], list[tuple[str, str]]]] = {}
            for prior_id in expired_ids:
                prior = state["leases"].get(prior_id)
                if not isinstance(prior, dict):
                    raise ControlError("edit.state-malformed", "An expired path owner references a missing lease.", {"lease_id": prior_id}, ["Use bounded local maintenance."])
                prior_paths = prior.get("paths")
                prior_keys = prior.get("keys")
                valid_pairs = (
                    isinstance(prior_paths, list)
                    and isinstance(prior_keys, list)
                    and len(prior_paths) == len(prior_keys)
                    and all(isinstance(path, str) for path in prior_paths)
                    and all(isinstance(key, str) for key in prior_keys)
                    and len(set(prior_paths)) == len(prior_paths)
                    and len(set(prior_keys)) == len(prior_keys)
                    and all(_stored_path_key_pair_is_canonical(path, key) for path, key in zip(prior_paths, prior_keys, strict=True))
                )
                if not valid_pairs:
                    raise ControlError("edit.state-malformed", "An expired lease has inconsistent path metadata.", {"lease_id": prior_id}, ["Use bounded local maintenance; preserve the malformed bytes."])
                prior_key_set = set(prior_keys)
                owned_keys = {key for key, owner_id in state["path_owners"].items() if owner_id == prior_id}
                if owned_keys != prior_key_set:
                    raise ControlError("edit.state-malformed", "An expired lease and its path-owner index disagree.", {"lease_id": prior_id}, ["Use bounded local maintenance; preserve the malformed bytes."])
                residual = [(path, key) for path, key in zip(prior_paths, prior_keys, strict=True) if key not in requested_keys]
                validated_prior[prior_id] = (prior, residual)
            for prior_id, (prior, residual) in validated_prior.items():
                for key in requested_keys.intersection(prior["keys"]):
                    if state["path_owners"].get(key) == prior_id:
                        state["path_owners"].pop(key, None)
                if residual:
                    prior["paths"] = [path for path, _key in residual]
                    prior["keys"] = [key for _path, key in residual]
                else:
                    state["leases"].pop(prior_id, None)
            lease_id = f"file-lease:{uuid.uuid4()}"
            created_lease_id = lease_id
            record = {"schema_version": "file-edit-lease-v1", "lease_id": lease_id, "unit_id": unit_id, "work_id": work_id, "owner": owner, "claim_id": claim_id, "paths": [display for display, _key in canonical], "keys": [key for _display, key in canonical], "acquired_at": timestamp(now), "leased_until": timestamp(now + timedelta(minutes=lease_minutes)), "recovered_from": recovered_from}
            state["leases"][lease_id] = record
            for _display, key in canonical:
                state["path_owners"][key] = lease_id
            state["intents"] = {intent_id: item for intent_id, item in state["intents"].items() if not (item.get("owner") == owner and item.get("claim_id") == claim_id and set(item.get("paths", [])) == set(record["paths"]))}
            event = "lease-recovered" if recovery else "lease-acquired"
            self._event(state, event, now, {"lease_id": lease_id, "unit_id": unit_id, "work_id": work_id, "path_count": len(canonical), "recovered_from": recovered_from})
            return state

        state = self._mutate(transition, expected_revision=expected_revision)
        lease = state["leases"][created_lease_id]
        code = "edit.lease-recovered" if recovery else "edit.lease-acquired"
        return success(code, f"Acquired an exclusive edit lease for {len(canonical)} file(s).", revision=state["revision"], data={"lease": {key: value for key, value in lease.items() if key != "keys"}})

    def _owned_lease(self, state: dict[str, Any], lease_id: str, owner: str, claim_id: str, now: datetime, *, require_live: bool = True) -> dict[str, Any]:
        lease = state["leases"].get(lease_id)
        if not isinstance(lease, dict):
            raise ControlError("edit.lease-missing", "The file-edit lease does not exist.", {"lease_id": lease_id}, ["Read edit-status and use an active lease ID."])
        if lease.get("owner") != owner or lease.get("claim_id") != claim_id:
            raise ControlError("edit.owner-mismatch", "The lease belongs to a different owner or claim.", {"lease_id": lease_id, "leased_until": lease.get("leased_until")}, ["Use the recorded owner/claim or wait for release/expiry."])
        if require_live and parse_timestamp(str(lease["leased_until"])) <= now:
            raise ControlError("edit.lease-expired", "The file-edit lease has expired.", {"lease_id": lease_id, "leased_until": lease["leased_until"]}, ["Use edit-recover with the exact paths and current work authority."])
        return lease

    def renew(self, *, lease_id: str, owner: str, claim_id: str, lease_minutes: int = DEFAULT_FILE_LEASE_MINUTES, expected_revision: int | None = None) -> dict[str, Any]:
        _duration(lease_minutes)

        def transition(state: dict[str, Any], now: datetime) -> dict[str, Any]:
            lease = self._owned_lease(state, lease_id, owner, claim_id, now)
            lease["leased_until"] = timestamp(now + timedelta(minutes=lease_minutes))
            self._event(state, "lease-renewed", now, {"lease_id": lease_id, "path_count": len(lease["paths"])})
            return state

        state = self._mutate(transition, expected_revision=expected_revision)
        lease = state["leases"][lease_id]
        return success("edit.lease-renewed", "Renewed the exclusive file-edit lease.", revision=state["revision"], data={"lease": {key: value for key, value in lease.items() if key != "keys"}})

    def release(self, *, lease_id: str, owner: str, claim_id: str, expected_revision: int | None = None) -> dict[str, Any]:
        released_paths: list[str] = []

        def transition(state: dict[str, Any], now: datetime) -> dict[str, Any]:
            nonlocal released_paths
            lease = self._owned_lease(state, lease_id, owner, claim_id, now, require_live=False)
            released_paths = list(lease["paths"])
            for key in lease["keys"]:
                if state["path_owners"].get(key) == lease_id:
                    state["path_owners"].pop(key, None)
            state["leases"].pop(lease_id, None)
            self._event(state, "lease-released", now, {"lease_id": lease_id, "path_count": len(released_paths)})
            return state

        state = self._mutate(transition, expected_revision=expected_revision)
        return success("edit.lease-released", "Released the exclusive file-edit lease.", revision=state["revision"], data={"lease_id": lease_id, "paths": released_paths})

    def status(self, *, path: str | None = None) -> dict[str, Any]:
        with exclusive_lock(self.lock_path):
            state = self._load()
        now = self.clock()
        path_key: str | None = None
        display: str | None = None
        if path:
            display, path_key = canonical_file(self.root, path)
        leases = []
        for lease in state["leases"].values():
            if path_key and path_key not in lease["keys"]:
                continue
            public = {key: value for key, value in lease.items() if key != "keys"}
            public["state"] = "live" if parse_timestamp(str(lease["leased_until"])) > now else "expired"
            leases.append(public)
        intents = []
        for intent in state["intents"].values():
            if parse_timestamp(str(intent["expires_at"])) <= now:
                continue
            if display and display not in intent["paths"]:
                continue
            intents.append(intent)
        leases.sort(key=lambda item: item["lease_id"])
        intents.sort(key=lambda item: item["intent_id"])
        return success("edit.status", f"Found {len(leases)} lease(s) and {len(intents)} live intent(s).", revision=state["revision"], data={"leases": leases, "intents": intents, "reads_require_lease": False})
