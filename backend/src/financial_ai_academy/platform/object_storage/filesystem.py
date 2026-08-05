"""Restrictive local filesystem implementation of the Content object-store port."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path, PurePosixPath
from typing import Mapping
from uuid import UUID, uuid4

from financial_ai_academy.modules.content.ports.object_storage import StagedObject


_OBJECT_KEY = re.compile(r"^[a-f0-9]{2}/[a-f0-9]{64}$")


class FilesystemObjectStorage:
    def __init__(
        self,
        root: Path,
        *,
        max_files: int = 128,
        max_total_bytes: int = 32 * 1024 * 1024,
    ) -> None:
        if root.exists() and root.is_symlink():
            raise ValueError("Object-storage root cannot be a symbolic link.")
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._root = root.resolve()
        self._staging = self._root / "staging"
        self._objects = self._root / "objects"
        self._staging.mkdir(exist_ok=True, mode=0o700)
        self._objects.mkdir(exist_ok=True, mode=0o700)
        self._max_files = max_files
        self._max_total_bytes = max_total_bytes

    def stage(
        self, object_key: str, files: Mapping[str, bytes]
    ) -> StagedObject:
        self._validate_object_key(object_key)
        if len(files) > self._max_files:
            raise ValueError("Object contains too many files.")
        if sum(len(value) for value in files.values()) > self._max_total_bytes:
            raise ValueError("Object exceeds the total size limit.")
        stage_id = uuid4().hex
        stage_root = self._staging / stage_id
        stage_root.mkdir(mode=0o700)
        staged = StagedObject(stage_id=stage_id, object_key=object_key)
        try:
            for logical_path, value in sorted(files.items()):
                target = self._logical_target(stage_root, logical_path)
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                with target.open("xb") as stream:
                    stream.write(value)
                    stream.flush()
                    os.fsync(stream.fileno())
                target.chmod(0o600)
                if hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(
                    value
                ).digest():
                    raise OSError("Staged object verification failed.")
            return staged
        except BaseException:
            self.discard_stage(staged)
            raise

    def finalize(self, staged: StagedObject) -> None:
        stage_root = self._stage_root(staged.stage_id)
        if not stage_root.is_dir() or stage_root.is_symlink():
            raise OSError("Staged object is unavailable.")
        destination = self._object_root(staged.object_key)
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if destination.exists():
            if not destination.is_dir() or destination.is_symlink():
                raise OSError("Final object location is invalid.")
            self.discard_stage(staged)
            return
        os.replace(stage_root, destination)

    def discard_stage(self, staged: StagedObject) -> None:
        stage_root = self._stage_root(staged.stage_id)
        if stage_root.exists():
            if stage_root.is_symlink() or not stage_root.is_dir():
                raise OSError("Staging entry is invalid.")
            shutil.rmtree(stage_root)

    def read(self, object_key: str) -> Mapping[str, bytes]:
        object_root = self._object_root(object_key)
        if not object_root.is_dir() or object_root.is_symlink():
            raise FileNotFoundError("Stored object is unavailable.")
        result: dict[str, bytes] = {}
        total_bytes = 0
        for path in object_root.rglob("*"):
            if path.is_symlink():
                raise OSError("Linked object entries are prohibited.")
            if not path.is_file():
                continue
            logical = path.relative_to(object_root).as_posix()
            self._logical_target(object_root, logical)
            value = path.read_bytes()
            result[logical] = value
            total_bytes += len(value)
            if len(result) > self._max_files or total_bytes > self._max_total_bytes:
                raise OSError("Stored object exceeds read limits.")
        return result

    @staticmethod
    def _validate_object_key(object_key: str) -> None:
        if not _OBJECT_KEY.fullmatch(object_key):
            raise ValueError("Object key is not in the opaque key profile.")

    def _object_root(self, object_key: str) -> Path:
        self._validate_object_key(object_key)
        candidate = (self._objects / PurePosixPath(object_key)).resolve(
            strict=False
        )
        if not candidate.is_relative_to(self._objects):
            raise ValueError("Object key escapes the storage root.")
        return candidate

    def _stage_root(self, stage_id: str) -> Path:
        try:
            normalized = UUID(hex=stage_id).hex
        except ValueError as error:
            raise ValueError("Stage identifier is invalid.") from error
        candidate = (self._staging / normalized).resolve(strict=False)
        if not candidate.is_relative_to(self._staging):
            raise ValueError("Stage identifier escapes the staging root.")
        return candidate

    @staticmethod
    def _logical_target(root: Path, logical_path: str) -> Path:
        if (
            not logical_path
            or chr(92) in logical_path
            or logical_path.startswith("/")
        ):
            raise ValueError("Logical path is invalid.")
        logical = PurePosixPath(logical_path)
        if logical.is_absolute() or str(logical) != logical_path:
            raise ValueError("Logical path is not normalized.")
        if any(part in {"", ".", ".."} or part.startswith(".") for part in logical.parts):
            raise ValueError("Logical path contains a prohibited segment.")
        candidate = (root / logical).resolve(strict=False)
        if not candidate.is_relative_to(root.resolve()):
            raise ValueError("Logical path escapes the object root.")
        return candidate
