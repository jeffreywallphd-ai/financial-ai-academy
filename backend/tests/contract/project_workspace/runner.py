"""Dependency-light conformance runner for Project workspace v1."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker


VERSION = "1.0.0"
FORBIDDEN_KEYS = {
    "answer",
    "completion",
    "credential",
    "execution",
    "host_path",
    "mastery",
    "portfolio",
    "provider_payload",
    "score",
    "storage_key",
}


class ProjectConformanceFailure(ValueError):
    def __init__(self, code: str, reference: str) -> None:
        super().__init__("Project contract input was rejected.")
        self.code = code
        self.reference = (
            str(reference)
            .replace(chr(0), "")
            .replace("\r", " ")
            .replace("\n", " ")[:120]
        )


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def schema_dir() -> Path:
    return repository_root() / "contracts/learning/project/v1"


def corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/project-workspace/v1"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_brief_bytes(brief: Mapping[str, Any]) -> bytes:
    return json.dumps(
        brief,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def brief_digest(document: Mapping[str, Any]) -> str:
    brief = document.get("brief")
    if not isinstance(brief, Mapping):
        raise ProjectConformanceFailure(
            "project.contract.schema_invalid",
            "brief",
        )
    return hashlib.sha256(canonical_brief_bytes(brief)).hexdigest()


class ProjectContractValidator:
    def __init__(self, schemas: Path | None = None) -> None:
        root = schemas or schema_dir()
        self._validators: dict[str, Draft202012Validator] = {}
        for name in ("brief", "create-intent", "shell"):
            schema = load_json(root / f"{name}.schema.json")
            Draft202012Validator.check_schema(schema)
            self._validators[name] = Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            )

    def validate_brief(self, document: Mapping[str, Any]) -> None:
        self._version(document)
        self._shape("brief", document)
        if brief_digest(document) != document["brief_digest"]:
            self._reject(
                "project.contract.brief_digest_mismatch",
                "brief_digest",
            )
        brief = document["brief"]
        self._unique(
            [item["milestone_id"] for item in brief["milestones"]],
            "brief.milestones",
        )
        self._unique(
            [item["resource_id"] for item in brief["source_references"]],
            "brief.source_references",
        )
        self._confidential(document)

    def validate_intent(
        self,
        document: Mapping[str, Any],
        approved_brief: Mapping[str, Any] | None = None,
    ) -> None:
        self._version(document)
        self._shape("create-intent", document)
        origin = document["origin"]
        if origin["origin_type"] == "learning":
            if approved_brief is None:
                self._reject(
                    "project.contract.learning_brief_required",
                    "origin.brief_id",
                )
            self.validate_brief(approved_brief)
            brief = approved_brief["brief"]
            expected = (
                approved_brief["schema_version"],
                brief["brief_id"],
                brief["brief_version"],
                approved_brief["brief_digest"],
                brief["title"],
                brief["purpose"],
            )
            actual = (
                origin["project_brief_schema_version"],
                origin["brief_id"],
                origin["brief_version"],
                origin["brief_digest"],
                origin["brief_title"],
                origin["brief_purpose"],
            )
            if actual != expected:
                self._reject(
                    "project.contract.stale_learning_reference",
                    "origin.brief_id",
                )
        self._confidential(document)

    def validate_shell(self, document: Mapping[str, Any]) -> None:
        self._version(document)
        self._shape("shell", document)
        created = self._timestamp(document["created_at"])
        updated = self._timestamp(document["updated_at"])
        if updated < created:
            self._reject("project.contract.invalid_shell", "updated_at")
        self._confidential(document)

    def validate_approved(self, corpus: Path | None = None) -> None:
        approved = (corpus or corpus_dir()) / "approved"
        brief = load_json(approved / "brief.json")
        self.validate_brief(brief)
        self.validate_intent(load_json(approved / "independent-intent.json"))
        self.validate_intent(
            load_json(approved / "learning-intent.json"),
            brief,
        )
        self.validate_shell(load_json(approved / "independent-shell.json"))
        self.validate_shell(load_json(approved / "learning-shell.json"))

    def _shape(self, kind: str, document: Mapping[str, Any]) -> None:
        error = next(iter(self._validators[kind].iter_errors(document)), None)
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            self._reject(
                "project.contract.schema_invalid",
                reference or kind,
            )

    def _version(self, document: Mapping[str, Any]) -> None:
        if document.get("schema_version") != VERSION:
            self._reject(
                "project.contract.unsupported_version",
                "schema_version",
            )

    def _unique(self, values: list[str], reference: str) -> None:
        if len(values) != len(set(values)):
            self._reject("project.contract.invalid_brief", reference)

    def _confidential(self, value: object, reference: str = "record") -> None:
        if isinstance(value, Mapping):
            for key, nested in value.items():
                if key in FORBIDDEN_KEYS:
                    self._reject(
                        "project.contract.private_field",
                        f"{reference}.{key}",
                    )
                self._confidential(nested, f"{reference}.{key}")
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                self._confidential(nested, f"{reference}.{index}")

    @staticmethod
    def _timestamp(value: str) -> datetime:
        return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")

    @staticmethod
    def _reject(code: str, reference: str) -> None:
        raise ProjectConformanceFailure(code, reference)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schemas", type=Path, default=schema_dir())
    parser.add_argument("--corpus", type=Path, default=corpus_dir())
    arguments = parser.parse_args()
    ProjectContractValidator(arguments.schemas).validate_approved(arguments.corpus)
    print("PASS project workspace v1 compatibility")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
