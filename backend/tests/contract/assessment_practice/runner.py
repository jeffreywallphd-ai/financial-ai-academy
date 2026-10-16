"""Dependency-light conformance runner for Assessment practice v1."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator


VERSION = "1.0.0"
POLICIES = {
    "single_select": "single-select-exact-match",
    "multiple_select": "multiple-select-exact-set",
    "numeric_entry": "numeric-exact-or-inclusive-range",
}
DECIMAL_RE = re.compile(r"^-?(0|[1-9][0-9]*)(?:\.([0-9]{1,6}))?$")
PRIVATE_NAMES = {
    "answer",
    "correct_option_id",
    "correct_option_ids",
    "feedback",
}


class PracticeConformanceFailure(ValueError):
    def __init__(self, code: str, reference: str, message: str) -> None:
        self.code = code
        self.reference = safe_reference(reference)
        self.message = message
        super().__init__(message)

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "reference": self.reference,
            "message": self.message,
        }


def safe_reference(value: object) -> str:
    return (
        str(value)
        .replace(chr(0), "")
        .replace("\r", " ")
        .replace("\n", " ")[:120]
    )


def reject(code: str, reference: str, message: str) -> None:
    raise PracticeConformanceFailure(code, reference, message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def schema_dir() -> Path:
    return repository_root() / "contracts/learning/assessment/practice/v1"


def corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/assessment-practice/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject(
            "assessment.practice.schema_invalid",
            path.name,
            "Practice record must be an object.",
        )
    return value


def canonical_practice_bytes(practice: Mapping[str, Any]) -> bytes:
    return json.dumps(
        practice,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def definition_digest(definition: Mapping[str, Any]) -> str:
    practice = definition.get("practice")
    if not isinstance(practice, Mapping):
        reject(
            "assessment.practice.schema_invalid",
            "practice",
            "Practice definition is malformed.",
        )
    return hashlib.sha256(canonical_practice_bytes(practice)).hexdigest()


def approved_pair(
    corpus: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    approved = (corpus or corpus_dir()) / "approved"
    return load_json(approved / "definition.json"), load_json(
        approved / "presentation.json"
    )


def _private_name(value: object) -> str | None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key in PRIVATE_NAMES:
                return str(key)
            found = _private_name(nested)
            if found:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = _private_name(nested)
            if found:
                return found
    return None


class PracticeContractValidator:
    def __init__(self, schemas: Path | None = None) -> None:
        root = schemas or schema_dir()
        self._schemas = {
            name: load_json(root / f"{name}.schema.json")
            for name in ("definition", "presentation")
        }
        for schema in self._schemas.values():
            Draft202012Validator.check_schema(schema)

    def _versions(self, definition: Mapping[str, Any]) -> None:
        if definition.get("schema_version") != VERSION:
            reject(
                "assessment.practice.unsupported_version",
                "schema_version",
                "Practice contract version is unsupported.",
            )
        practice = definition.get("practice")
        if not isinstance(practice, Mapping):
            return
        if practice.get("practice_version") != VERSION:
            reject(
                "assessment.practice.unsupported_version",
                "practice_version",
                "Practice version is unsupported.",
            )
        for index, item in enumerate(practice.get("items", ())):
            if not isinstance(item, Mapping):
                continue
            item_type = item.get("item_type")
            if item_type not in POLICIES:
                reject(
                    "assessment.practice.unsupported_item_type",
                    f"items.{index}.item_type",
                    "Practice item type is unsupported.",
                )
            if item.get("item_version") != VERSION:
                reject(
                    "assessment.practice.unsupported_version",
                    f"items.{index}.item_version",
                    "Practice item version is unsupported.",
                )
            policy = item.get("scoring_policy")
            if isinstance(policy, Mapping) and (
                policy.get("policy_id") != POLICIES[item_type]
                or policy.get("policy_version") != VERSION
            ):
                reject(
                    "assessment.practice.unsupported_policy",
                    f"items.{index}.scoring_policy",
                    "Practice scoring policy is unsupported.",
                )

    def _shape(self, kind: str, value: Mapping[str, Any]) -> None:
        error = next(
            iter(Draft202012Validator(self._schemas[kind]).iter_errors(value)),
            None,
        )
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            reject(
                "assessment.practice.schema_invalid",
                reference or kind,
                f"Practice {kind} is malformed.",
            )

    def validate_definition(self, definition: Mapping[str, Any]) -> None:
        self._versions(definition)
        self._shape("definition", definition)
        if definition_digest(definition) != definition["definition_digest"]:
            reject(
                "assessment.practice.definition_digest_mismatch",
                "definition_digest",
                "Practice definition digest does not match its meaning.",
            )
        practice = definition["practice"]
        self._unique(
            [item["item_id"] for item in practice["items"]],
            "items",
        )
        self._unique(
            [item["resource_id"] for item in practice["source_references"]],
            "source_references",
        )
        review_ids = [
            item["resource_id"] for item in practice["review_references"]
        ]
        self._unique(review_ids, "review_references")
        declared_review = set(review_ids)
        for index, item in enumerate(practice["items"]):
            self._validate_item(item, index, declared_review)

    def _validate_item(
        self, item: Mapping[str, Any], index: int, review_ids: set[str]
    ) -> None:
        item_type = item["item_type"]
        for feedback in item["feedback"].values():
            if not set(feedback["review_reference_ids"]).issubset(review_ids):
                reject(
                    "assessment.practice.invalid_definition",
                    f"items.{index}.feedback",
                    "Feedback must reference declared review resources.",
                )
        if item_type in {"single_select", "multiple_select"}:
            option_ids = [option["option_id"] for option in item["options"]]
            self._unique(option_ids, f"items.{index}.options")
            declared = set(option_ids)
            correct = (
                {item["correct_option_id"]}
                if item_type == "single_select"
                else set(item["correct_option_ids"])
            )
            if not correct.issubset(declared):
                reject(
                    "assessment.practice.invalid_definition",
                    f"items.{index}.options",
                    "Correct options must be declared by the item.",
                )
            return
        response = item["response"]
        answer = item["answer"]
        values = (
            [answer["value"]]
            if answer["mode"] == "exact"
            else [answer["lower"], answer["upper"]]
        )
        decimals = [
            self._decimal(value, response["scale"], index) for value in values
        ]
        if not response["allow_negative"] and any(value < 0 for value in decimals):
            reject(
                "assessment.practice.invalid_decimal",
                f"items.{index}.answer",
                "Negative answers are not allowed by this item.",
            )
        if answer["mode"] == "inclusive_range" and decimals[0] > decimals[1]:
            reject(
                "assessment.practice.invalid_decimal",
                f"items.{index}.answer",
                "Numeric range bounds are inverted.",
            )

    @staticmethod
    def _unique(values: list[str], reference: str) -> None:
        if len(values) != len(set(values)):
            reject(
                "assessment.practice.invalid_definition",
                reference,
                "Practice identities must be unique.",
            )

    @staticmethod
    def _decimal(value: str, scale: int, item_index: int) -> Decimal:
        match = DECIMAL_RE.fullmatch(value)
        fraction = match.group(2) if match else None
        if match is None or len(fraction or "") != scale:
            reject(
                "assessment.practice.invalid_decimal",
                f"items.{item_index}.answer",
                "Numeric answer does not match the declared fixed scale.",
            )
        if value.startswith("-0") and Decimal(value) == 0:
            reject(
                "assessment.practice.invalid_decimal",
                f"items.{item_index}.answer",
                "Negative zero is not a canonical numeric answer.",
            )
        try:
            return Decimal(value)
        except InvalidOperation as error:
            raise PracticeConformanceFailure(
                "assessment.practice.invalid_decimal",
                f"items.{item_index}.answer",
                "Numeric answer is invalid.",
            ) from error

    def project(
        self,
        definition: Mapping[str, Any],
        *,
        placement_id: str,
        package_id: str,
        package_version: str,
        package_digest: str,
    ) -> dict[str, Any]:
        self.validate_definition(definition)
        practice = definition["practice"]
        items: list[dict[str, Any]] = []
        for item in practice["items"]:
            projected = {
                "item_id": item["item_id"],
                "item_version": item["item_version"],
                "item_type": item["item_type"],
                "prompt": item["prompt"],
                "scoring_policy_id": item["scoring_policy"]["policy_id"],
                "scoring_policy_version": item["scoring_policy"]["policy_version"],
                "max_score": item["scoring_policy"]["max_score"],
            }
            if item["item_type"] in {"single_select", "multiple_select"}:
                projected["options"] = copy.deepcopy(item["options"])
            else:
                projected.update(copy.deepcopy(item["response"]))
            items.append(projected)
        return {
            "schema_version": VERSION,
            "placement_id": placement_id,
            "package_id": package_id,
            "package_version": package_version,
            "package_digest": package_digest,
            "definition_digest": definition["definition_digest"],
            "practice_id": practice["practice_id"],
            "practice_version": practice["practice_version"],
            "title": practice["title"],
            "purpose": practice["purpose"],
            "instructions": practice["instructions"],
            "attempt_policy": copy.deepcopy(practice["attempt_policy"]),
            "source_references": copy.deepcopy(practice["source_references"]),
            "review_references": copy.deepcopy(practice["review_references"]),
            "items": items,
        }

    def validate_presentation(
        self,
        definition: Mapping[str, Any],
        presentation: Mapping[str, Any],
    ) -> None:
        leaked = _private_name(presentation)
        if leaked:
            reject(
                "assessment.practice.presentation_leak",
                leaked,
                "Practice presentation contains private Assessment fields.",
            )
        self._shape("presentation", presentation)
        expected = self.project(
            definition,
            placement_id=str(presentation["placement_id"]),
            package_id=str(presentation["package_id"]),
            package_version=str(presentation["package_version"]),
            package_digest=str(presentation["package_digest"]),
        )
        if presentation != expected:
            reject(
                "assessment.practice.stale_reference",
                "presentation",
                "Practice presentation does not match the exact definition.",
            )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        definition, presentation = approved_pair(arguments.corpus)
        PracticeContractValidator().validate_presentation(definition, presentation)
    except (PracticeConformanceFailure, OSError, ValueError) as error:
        diagnostic = (
            error.as_dict()
            if isinstance(error, PracticeConformanceFailure)
            else PracticeConformanceFailure(
                "assessment.practice.internal_error",
                "practice",
                "Practice conformance could not complete.",
            ).as_dict()
        )
        print(json.dumps({"valid": False, "diagnostic": diagnostic}, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "practice_id": definition["practice"]["practice_id"],
                "definition_digest": definition["definition_digest"],
                "item_types": [
                    item["item_type"] for item in definition["practice"]["items"]
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
