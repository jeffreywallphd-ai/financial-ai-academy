from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from .runner import (
    ConformanceError,
    LessonPackageValidator,
    PackageLimits,
    canonical_index_bytes,
    default_schema_dir,
    immutable_conflict,
    normalize_logical_path,
)


REPOSITORY = Path(__file__).resolve().parents[4]
CORPUS = REPOSITORY / "contracts/compatibility/lesson-package/v1"
APPROVED = CORPUS / "approved/intro-risk-return"
SCHEMA_DIR = REPOSITORY / "contracts/learning/lesson-package/v1"


def copy_approved(tmp_path: Path) -> Path:
    target = tmp_path / "package"
    shutil.copytree(APPROVED, target)
    return target


def load_manifest(root: Path) -> dict[str, object]:
    return json.loads((root / "manifest.json").read_text(encoding="utf-8"))


def write_manifest(root: Path, manifest: dict[str, object]) -> None:
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def nested_set(document: dict[str, object], dotted: str, value: object) -> None:
    parts = dotted.split(".")
    current: dict[str, object] = document
    for part in parts[:-1]:
        child = current[part]
        assert isinstance(child, dict)
        current = child
    current[parts[-1]] = value


def refresh_declaration(root: Path, logical: str) -> None:
    manifest = load_manifest(root)
    declarations = [
        manifest["lesson"],
        *manifest["assessments"],
        *manifest["assets"],
    ]
    value = (root / logical).read_bytes()
    for declaration in declarations:
        if declaration["path"] == logical:
            declaration["size_bytes"] = len(value)
            declaration["sha256"] = hashlib.sha256(value).hexdigest()
            write_manifest(root, manifest)
            return
    raise AssertionError(f"declaration not found: {logical}")


def apply_mutation(root: Path, mutation: dict[str, object]) -> PackageLimits:
    operation = mutation["op"]
    limits = PackageLimits()
    if operation == "manifest-set":
        manifest = load_manifest(root)
        nested_set(manifest, str(mutation["path"]), mutation["value"])
        write_manifest(root, manifest)
    elif operation == "delete":
        (root / str(mutation["path"])).unlink()
    elif operation == "write":
        path = root / str(mutation["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(mutation["value"]), encoding="utf-8")
    elif operation == "append":
        path = root / str(mutation["path"])
        path.write_text(
            path.read_text(encoding="utf-8") + str(mutation["value"]),
            encoding="utf-8",
            newline="\n",
        )
        if mutation.get("refresh_declaration"):
            refresh_declaration(root, str(mutation["path"]))
    elif operation == "limit":
        limits = PackageLimits(**{str(mutation["name"]): int(mutation["value"])})
    else:
        raise AssertionError(f"unknown mutation operation: {operation}")
    return limits


def assert_rejected(
    root: Path,
    expected_code: str,
    *,
    limits: PackageLimits | None = None,
) -> None:
    validator = LessonPackageValidator(SCHEMA_DIR, limits)
    with pytest.raises(ConformanceError) as captured:
        validator.validate(root)
    diagnostic = captured.value.diagnostic
    assert diagnostic.code == expected_code
    assert len(diagnostic.reference) <= 120
    assert "\n" not in diagnostic.reference


def test_all_json_schemas_are_valid_draft_2020_12() -> None:
    schemas = list(SCHEMA_DIR.glob("*.schema.json"))
    assert {path.name for path in schemas} == {
        "assessment-file.schema.json",
        "file.schema.json",
        "image-asset.schema.json",
        "manifest.schema.json",
        "package-index.schema.json",
        "source.schema.json",
    }
    for path in schemas:
        Draft202012Validator.check_schema(
            json.loads(path.read_text(encoding="utf-8"))
        )


def test_approved_package_matches_committed_digest_vector() -> None:
    result = LessonPackageValidator(SCHEMA_DIR).validate(APPROVED)
    vector = json.loads(
        (CORPUS / "vectors/package-index.json").read_text(encoding="utf-8")
    )
    assert result.manifest["package_id"] == "intro-risk-return"
    assert result.manifest["package_version"] == "1.0.0"
    assert result.package_digest == vector["package_digest"]
    assert result.index_bytes.hex() == vector["canonical_index_utf8_hex"]
    assert list(result.index) == vector["entries"]


def test_index_is_independent_of_input_enumeration_order() -> None:
    result = LessonPackageValidator(SCHEMA_DIR).validate(APPROVED)
    assert canonical_index_bytes(result.index) == canonical_index_bytes(
        reversed(result.index)
    )


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["id"],
)
def test_hostile_compatibility_cases_fail_closed(
    tmp_path: Path, case: dict[str, object]
) -> None:
    root = copy_approved(tmp_path)
    limits = apply_mutation(root, case["mutation"])
    assert_rejected(root, str(case["expected_code"]), limits=limits)


@pytest.mark.parametrize(
    "path",
    [
        "",
        "/absolute",
        "C:/drive",
        "../escape",
        "folder/../escape",
        "folder\\file.md",
        ".hidden/file.md",
        "folder/CON.txt",
        "folder/trailing.",
        "folder//double.md",
    ],
)
def test_portable_path_profile_rejects_unsafe_paths(path: str) -> None:
    with pytest.raises(ConformanceError) as captured:
        normalize_logical_path(path)
    assert captured.value.diagnostic.code == "package.path_invalid"


def test_case_collisions_are_rejected(tmp_path: Path) -> None:
    root = copy_approved(tmp_path)
    manifest = load_manifest(root)
    duplicate = dict(manifest["lesson"])
    duplicate["assessment_id"] = "duplicate"
    duplicate["schema_version"] = "1.0.0"
    duplicate["path"] = "LESSON.md"
    duplicate["media_type"] = "application/json"
    manifest["assessments"].append(duplicate)
    write_manifest(root, manifest)
    (root / "LESSON.md").write_text("{}", encoding="utf-8")
    assert_rejected(root, "package.path_invalid")


def test_oversized_image_dimensions_are_rejected(tmp_path: Path) -> None:
    root = copy_approved(tmp_path)
    image = (
        b"\x89PNG\r\n\x1a\n"
        + b"\x00\x00\x00\rIHDR"
        + (5000).to_bytes(4, "big")
        + (5000).to_bytes(4, "big")
    )
    image_path = root / "assets/oversized.png"
    image_path.parent.mkdir()
    image_path.write_bytes(image)
    manifest = load_manifest(root)
    manifest["assets"].append(
        {
            "asset_id": "oversized-image",
            "path": "assets/oversized.png",
            "media_type": "image/png",
            "size_bytes": len(image),
            "sha256": hashlib.sha256(image).hexdigest(),
            "alt_text": "Synthetic oversized test image",
        }
    )
    manifest["capabilities"].append("asset.raster.v1")
    lesson_path = root / "lesson.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8")
        + "\n![Synthetic oversized test image](assets/oversized.png)\n",
        encoding="utf-8",
        newline="\n",
    )
    value = lesson_path.read_bytes()
    manifest["lesson"]["size_bytes"] = len(value)
    manifest["lesson"]["sha256"] = hashlib.sha256(value).hexdigest()
    write_manifest(root, manifest)
    assert_rejected(root, "package.limit_exceeded")


def test_manifest_self_declaration_is_rejected(tmp_path: Path) -> None:
    root = copy_approved(tmp_path)
    manifest = load_manifest(root)
    manifest["lesson"]["path"] = "manifest.json"
    write_manifest(root, manifest)
    assert_rejected(root, "package.path_invalid")


def test_immutable_conflict_vector_has_stable_safe_outcome() -> None:
    vector = json.loads(
        (CORPUS / "vectors/immutable-conflict.json").read_text(encoding="utf-8")
    )
    diagnostic = immutable_conflict(
        vector["package_id"],
        vector["package_version"],
        vector["accepted_digest"],
        vector["package_id"],
        vector["package_version"],
        vector["conflicting_digest"],
    )
    assert diagnostic is not None
    assert diagnostic.code == vector["expected_code"]
    assert vector["accepted_digest"] not in diagnostic.message
    assert vector["conflicting_digest"] not in diagnostic.message


def test_identical_immutable_tuple_is_idempotent() -> None:
    assert (
        immutable_conflict(
            "package",
            "1.0.0",
            "a" * 64,
            "package",
            "1.0.0",
            "a" * 64,
        )
        is None
    )


def test_cli_emits_bounded_json_without_stack_trace() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "tests.contract.lesson_package.runner",
            str(APPROVED),
            "--schema-dir",
            str(default_schema_dir()),
        ],
        cwd=REPOSITORY / "backend",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["valid"] is True
    assert output["file_count"] == 3
    assert "Traceback" not in completed.stdout + completed.stderr
