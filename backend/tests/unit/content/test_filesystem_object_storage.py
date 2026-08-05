from __future__ import annotations

from pathlib import Path

import pytest

from financial_ai_academy.platform.object_storage.filesystem import (
    FilesystemObjectStorage,
)


OBJECT_KEY = "ab/" + "a" * 64


def test_stage_finalize_and_bounded_read(tmp_path: Path) -> None:
    storage = FilesystemObjectStorage(tmp_path / "store")
    staged = storage.stage(
        OBJECT_KEY,
        {"manifest.json": b"{}", "lesson.md": b"# Lesson\\n"},
    )

    storage.finalize(staged)

    assert storage.read(OBJECT_KEY) == {
        "lesson.md": b"# Lesson\\n",
        "manifest.json": b"{}",
    }


@pytest.mark.parametrize(
    "logical_path",
    ["../escape", "/absolute", "folder\\\\entry", ".hidden"],
)
def test_storage_rejects_nonportable_logical_paths(
    tmp_path: Path, logical_path: str
) -> None:
    storage = FilesystemObjectStorage(tmp_path / "store")

    with pytest.raises(ValueError):
        storage.stage(OBJECT_KEY, {logical_path: b"x"})


def test_storage_rejects_nonopaque_object_key(tmp_path: Path) -> None:
    storage = FilesystemObjectStorage(tmp_path / "store")

    with pytest.raises(ValueError):
        storage.stage("../../outside", {"lesson.md": b"x"})
