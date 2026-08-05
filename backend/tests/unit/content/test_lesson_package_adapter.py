from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from financial_ai_academy.modules.content.adapters.lesson_package import (
    ContractLessonPackageValidator,
    PackageLimits,
)
from financial_ai_academy.modules.content.ports.package_validator import (
    PackageValidationFailure,
)


REPOSITORY = Path(__file__).resolve().parents[4]
CORPUS = REPOSITORY / "contracts/compatibility/lesson-package/v1"
APPROVED = CORPUS / "approved/intro-risk-return"
SCHEMAS = REPOSITORY / "contracts/learning/lesson-package/v1"
DENIALS = json.loads(
    (CORPUS / "cases/denials.json").read_text(encoding="utf-8")
)


def set_manifest_value(manifest: dict[str, object], path: str, value: object) -> None:
    parts = path.split(".")
    current: dict[str, object] = manifest
    for part in parts[:-1]:
        nested = current[part]
        assert isinstance(nested, dict)
        current = nested
    current[parts[-1]] = value


def write_manifest(root: Path, manifest: dict[str, object]) -> None:
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + chr(10),
        encoding="utf-8",
    )


def refresh_declaration(
    root: Path, manifest: dict[str, object], logical_path: str
) -> None:
    value = (root / logical_path).read_bytes()
    lesson = manifest["lesson"]
    assert isinstance(lesson, dict)
    assert lesson["path"] == logical_path
    lesson["size_bytes"] = len(value)
    lesson["sha256"] = hashlib.sha256(value).hexdigest()


def apply_mutation(
    root: Path, mutation: dict[str, object]
) -> PackageLimits:
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    operation = mutation["op"]
    limits = PackageLimits()
    if operation == "manifest-set":
        set_manifest_value(
            manifest, str(mutation["path"]), mutation["value"]
        )
        write_manifest(root, manifest)
    elif operation == "delete":
        (root / str(mutation["path"])).unlink()
    elif operation == "write":
        target = root / str(mutation["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(mutation["value"]), encoding="utf-8")
    elif operation == "append":
        logical = str(mutation["path"])
        target = root / logical
        target.write_text(
            target.read_text(encoding="utf-8") + str(mutation["value"]),
            encoding="utf-8",
        )
        if mutation.get("refresh_declaration"):
            refresh_declaration(root, manifest, logical)
            write_manifest(root, manifest)
    elif operation == "limit":
        limits = replace(
            limits,
            **{str(mutation["name"]): int(mutation["value"])},
        )
    else:
        raise AssertionError(f"Unknown mutation: {operation}")
    return limits


@pytest.mark.parametrize(
    ("case_id", "mutation", "expected_code"),
    [
        (
            str(case["id"]),
            case["mutation"],
            str(case["expected_code"]),
        )
        for case in DENIALS
    ],
)
def test_runtime_adapter_matches_committed_denial_corpus(
    tmp_path: Path,
    case_id: str,
    mutation: dict[str, object],
    expected_code: str,
) -> None:
    root = tmp_path / case_id
    shutil.copytree(APPROVED, root)
    limits = apply_mutation(root, mutation)

    with pytest.raises(PackageValidationFailure) as captured:
        ContractLessonPackageValidator(SCHEMAS, limits).validate_directory(root)

    assert captured.value.code == expected_code
    assert len(captured.value.reference) <= 120
    assert chr(10) not in captured.value.reference


@pytest.mark.parametrize(
    "logical_path",
    [
        "../lesson.md",
        "/absolute.md",
        "C:/drive.md",
        "folder\\lesson.md",
        ".hidden.md",
        "folder/../lesson.md",
        "CON.txt",
        "lesson.md ",
    ],
)
def test_runtime_adapter_rejects_hostile_portable_paths(
    tmp_path: Path, logical_path: str
) -> None:
    root = tmp_path / "hostile"
    shutil.copytree(APPROVED, root)
    manifest = json.loads(
        (root / "manifest.json").read_text(encoding="utf-8")
    )
    manifest["lesson"]["path"] = logical_path
    write_manifest(root, manifest)

    with pytest.raises(PackageValidationFailure) as captured:
        ContractLessonPackageValidator(SCHEMAS).validate_directory(root)

    assert captured.value.code == "package.path_invalid"
