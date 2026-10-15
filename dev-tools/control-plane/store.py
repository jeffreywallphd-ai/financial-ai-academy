"""Project-neutral journaled CAS persistence with a pluggable projection."""

from __future__ import annotations

import json
import os
import re
import time
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterator

from contracts import ControlError
from ports import ProjectionPort


SCHEMA_VERSION = "1.0"


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def confined_path(root: Path, relative: str) -> Path:
    posix = PurePosixPath(relative.replace("\\", "/"))
    if (
        posix.is_absolute()
        or re.match(r"^[A-Za-z]:", relative)
        or ".." in posix.parts
        or not posix.parts
    ):
        raise ControlError(
            "path.outside-repository",
            "Control-plane paths must be non-empty repository-relative paths.",
            {"path": relative},
            ["Use a normalized repository-relative path without parent traversal."],
        )
    target = root.joinpath(*posix.parts)
    resolved_root = root.resolve()
    resolved_parent = target.parent.resolve()
    try:
        resolved_parent.relative_to(resolved_root)
    except ValueError as error:
        raise ControlError(
            "path.outside-repository",
            "The resolved path escapes the repository boundary.",
            {"path": relative, "resolved_parent": str(resolved_parent)},
            ["Remove the symlink or junction escape and retry."],
        ) from error
    if target.exists():
        try:
            target.resolve().relative_to(resolved_root)
        except ValueError as error:
            raise ControlError(
                "path.outside-repository",
                "The resolved target escapes the repository boundary.",
                {"path": relative, "resolved_target": str(target.resolve())},
                ["Use a path contained by the repository."],
            ) from error
    return target


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def exclusive_lock(path: Path, timeout_seconds: float = 5.0) -> Iterator[None]:
    deadline = time.monotonic() + timeout_seconds
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor: int | None = None
    while descriptor is None:
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise ControlError(
                    "state.lock-contended",
                    "Another control-plane mutation still owns the repository lock.",
                    {"lock": path.name},
                    ["Wait for the current mutation to finish, then retry."],
                )
            time.sleep(0.025)
    try:
        os.write(descriptor, canonical_bytes({"pid": os.getpid(), "created": time.time()}))
        os.close(descriptor)
        descriptor = None
        yield
    finally:
        if descriptor is not None:
            os.close(descriptor)
        path.unlink(missing_ok=True)


class StateStore:
    """A reusable state envelope with recoverable state/projection publication."""

    def __init__(
        self,
        root: Path,
        projection_resolver: Callable[[str], ProjectionPort],
    ) -> None:
        self.root = root.resolve()
        self.projection_resolver = projection_resolver
        self.state_path = confined_path(self.root, ".local-codex/control-plane/state.json")
        self.journal_path = confined_path(self.root, ".local-codex/control-plane/transaction.json")
        self.lock_path = confined_path(self.root, ".local-codex/control-plane/mutation.lock")

    @staticmethod
    def empty() -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "revision": 0, "work_items": {}}

    def load(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return self.empty()
        try:
            value = json.loads(self.state_path.read_bytes())
        except (OSError, json.JSONDecodeError) as error:
            raise ControlError(
                "state.malformed",
                "Local control-plane state is unreadable; its bytes were preserved.",
                {"path": self.state_path.relative_to(self.root).as_posix()},
                ["Run bounded control maintenance; do not edit state by hand."],
            ) from error
        if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
            raise ControlError(
                "state.incompatible-version",
                "Local state uses an unsupported schema version.",
                {"schema_version": value.get("schema_version") if isinstance(value, dict) else None},
                ["Use a documented forward migration or compatible controller."],
            )
        if not isinstance(value.get("revision"), int) or not isinstance(value.get("work_items"), dict):
            raise ControlError(
                "state.malformed",
                "The state envelope is missing its revision or work-item map.",
                {},
                ["Run bounded control maintenance; do not edit state by hand."],
            )
        return value

    def _read_journal(self) -> dict[str, Any] | None:
        if not self.journal_path.exists():
            return None
        try:
            value = json.loads(self.journal_path.read_bytes())
        except (OSError, json.JSONDecodeError) as error:
            raise ControlError(
                "transaction.malformed",
                "An interrupted transaction journal is unreadable and was preserved.",
                {"path": self.journal_path.relative_to(self.root).as_posix()},
                ["Run bounded control maintenance."],
            ) from error
        if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
            raise ControlError(
                "transaction.incompatible-version",
                "The transaction journal has an unsupported version.",
                {},
                ["Use a compatible controller or bounded maintenance."],
            )
        return value

    def _apply_projection(self, journal: dict[str, Any]) -> None:
        projection = self.projection_resolver(str(journal["projection_path"]))
        updates = journal["projection_updates"]
        if projection.matches(updates):
            return
        projection.apply(updates, str(journal["projection_before_sha256"]))

    def recover(self) -> bool:
        journal = self._read_journal()
        if journal is None:
            return False
        current = self.load()
        before = int(journal["before_revision"])
        successor = journal["successor"]
        after = int(successor["revision"])
        if int(current["revision"]) == before:
            atomic_write(self.state_path, canonical_bytes(successor))
        elif int(current["revision"]) != after:
            raise ControlError(
                "transaction.state-conflict",
                "State advanced beyond an interrupted transaction.",
                {"before_revision": before, "successor_revision": after, "actual_revision": current["revision"]},
                ["Use bounded control maintenance; preserve the journal."],
            )
        self._apply_projection(journal)
        self.journal_path.unlink(missing_ok=True)
        return True

    def read(self) -> tuple[dict[str, Any], bool]:
        with exclusive_lock(self.lock_path):
            recovered = self.recover()
            return self.load(), recovered

    def mutate(
        self,
        projection: ProjectionPort,
        transition: Callable[
            [dict[str, Any]], tuple[dict[str, Any], dict[str, Any]]
        ],
        *,
        fault_after: str | None = None,
    ) -> tuple[dict[str, Any], bool]:
        with exclusive_lock(self.lock_path):
            recovered = self.recover()
            current = self.load()
            successor, projection_updates = transition(current)
            if int(successor.get("revision", -1)) != int(current["revision"]) + 1:
                raise ControlError(
                    "state.invalid-successor",
                    "A mutation must advance state by exactly one revision.",
                    {"before": current["revision"], "after": successor.get("revision")},
                    ["Repair the transition implementation before retrying."],
                )
            journal = {
                "schema_version": SCHEMA_VERSION,
                "before_revision": current["revision"],
                "projection_path": projection.relative_path,
                "projection_before_sha256": projection.content_sha256(),
                "projection_updates": projection_updates,
                "successor": successor,
            }
            atomic_write(self.journal_path, canonical_bytes(journal))
            if fault_after == "journal":
                raise OSError("injected failure after journal publication")
            atomic_write(self.state_path, canonical_bytes(successor))
            if fault_after == "state":
                raise OSError("injected failure after state publication")
            self._apply_projection(journal)
            self.journal_path.unlink(missing_ok=True)
            return successor, recovered
