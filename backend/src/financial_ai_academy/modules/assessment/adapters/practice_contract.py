"""Closed parser and answer-safe projector for Assessment practice v1."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from ..domain.practice import (
    MultipleSelectPracticeItem,
    NumericPracticeAnswer,
    NumericPracticeItem,
    NumericPracticePresentationItem,
    NumericPracticeResponse,
    PracticeAttemptPolicy,
    PracticeDefinition,
    PracticeFeedback,
    PracticeFeedbackPair,
    PracticeItem,
    PracticeOption,
    PracticePresentation,
    PracticePresentationContext,
    PracticePresentationItem,
    PracticeResourceReference,
    PracticeScoringPolicy,
    SelectPracticePresentationItem,
    SingleSelectPracticeItem,
)
from ..ports.practice_definition import PracticeDefinitionFailure


VERSION = "1.0.0"
POLICIES = {
    "single_select": "single-select-exact-match",
    "multiple_select": "multiple-select-exact-set",
    "numeric_entry": "numeric-exact-or-inclusive-range",
}
DECIMAL_RE = re.compile(r"^-?(0|[1-9][0-9]*)(?:\.([0-9]{1,6}))?$")


class ContractPracticeDefinitionAdapter:
    """Parses private definitions and projects safe, serializable views."""

    def __init__(self, schema_dir: Path) -> None:
        self._validators: dict[str, Draft202012Validator] = {}
        for name in ("definition", "presentation"):
            schema = json.loads(
                (schema_dir / f"{name}.schema.json").read_text(encoding="utf-8")
            )
            Draft202012Validator.check_schema(schema)
            self._validators[name] = Draft202012Validator(schema)

    def parse(self, value: bytes) -> PracticeDefinition:
        document = self._document(value)
        self._versions(document)
        self._shape("definition", document)
        practice = document["practice"]
        measured = hashlib.sha256(
            json.dumps(
                practice,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        if measured != document["definition_digest"]:
            self._reject(
                "assessment.practice.definition_digest_mismatch",
                "definition_digest",
            )
        self._semantics(practice)
        return PracticeDefinition(
            practice_id=practice["practice_id"],
            practice_version=practice["practice_version"],
            definition_digest=document["definition_digest"],
            title=practice["title"],
            purpose=practice["purpose"],
            instructions=practice["instructions"],
            attempt_policy=self._attempt_policy(practice["attempt_policy"]),
            source_references=self._references(practice["source_references"]),
            review_references=self._references(practice["review_references"]),
            items=tuple(self._item(item) for item in practice["items"]),
        )

    def project(
        self,
        definition: PracticeDefinition,
        context: PracticePresentationContext,
    ) -> PracticePresentation:
        presentation = PracticePresentation(
            schema_version=VERSION,
            placement_id=context.placement_id,
            package_id=context.package_id,
            package_version=context.package_version,
            package_digest=context.package_digest,
            definition_digest=definition.definition_digest,
            practice_id=definition.practice_id,
            practice_version=definition.practice_version,
            title=definition.title,
            purpose=definition.purpose,
            instructions=definition.instructions,
            attempt_policy=definition.attempt_policy,
            source_references=definition.source_references,
            review_references=definition.review_references,
            items=tuple(self._presentation_item(item) for item in definition.items),
        )
        self._shape("presentation", self.to_document(presentation))
        return presentation

    @staticmethod
    def to_document(presentation: PracticePresentation) -> dict[str, Any]:
        """Return the JSON-compatible shape used by every transport adapter."""

        return json.loads(json.dumps(asdict(presentation)))

    @staticmethod
    def _document(value: bytes) -> dict[str, Any]:
        try:
            document = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise PracticeDefinitionFailure(
                "assessment.practice.schema_invalid", "definition"
            ) from error
        if not isinstance(document, dict):
            raise PracticeDefinitionFailure(
                "assessment.practice.schema_invalid", "definition"
            )
        return document

    def _shape(self, kind: str, document: Mapping[str, Any]) -> None:
        error = next(iter(self._validators[kind].iter_errors(document)), None)
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            self._reject(
                "assessment.practice.schema_invalid", reference or kind
            )

    def _versions(self, document: Mapping[str, Any]) -> None:
        if document.get("schema_version") != VERSION:
            self._reject(
                "assessment.practice.unsupported_version", "schema_version"
            )
        practice = document.get("practice")
        if not isinstance(practice, Mapping):
            return
        if practice.get("practice_version") != VERSION:
            self._reject(
                "assessment.practice.unsupported_version", "practice_version"
            )
        items = practice.get("items")
        if not isinstance(items, list):
            return
        for index, item in enumerate(items):
            if not isinstance(item, Mapping):
                continue
            item_type = item.get("item_type")
            if not isinstance(item_type, str):
                continue
            if item_type not in POLICIES:
                self._reject(
                    "assessment.practice.unsupported_item_type",
                    f"items.{index}.item_type",
                )
            if item.get("item_version") != VERSION:
                self._reject(
                    "assessment.practice.unsupported_version",
                    f"items.{index}.item_version",
                )
            policy = item.get("scoring_policy")
            if isinstance(policy, Mapping) and (
                policy.get("policy_id") != POLICIES[item_type]
                or policy.get("policy_version") != VERSION
            ):
                self._reject(
                    "assessment.practice.unsupported_policy",
                    f"items.{index}.scoring_policy",
                )

    def _semantics(self, practice: Mapping[str, Any]) -> None:
        self._unique(
            [item["item_id"] for item in practice["items"]], "items"
        )
        self._unique(
            [item["resource_id"] for item in practice["source_references"]],
            "source_references",
        )
        review_ids = [
            item["resource_id"] for item in practice["review_references"]
        ]
        self._unique(review_ids, "review_references")
        declared_review_ids = set(review_ids)
        for index, item in enumerate(practice["items"]):
            for feedback in item["feedback"].values():
                if not set(feedback["review_reference_ids"]).issubset(
                    declared_review_ids
                ):
                    self._reject(
                        "assessment.practice.invalid_definition",
                        f"items.{index}.feedback",
                    )
            if item["item_type"] in {"single_select", "multiple_select"}:
                option_ids = [option["option_id"] for option in item["options"]]
                self._unique(option_ids, f"items.{index}.options")
                correct_ids = (
                    {item["correct_option_id"]}
                    if item["item_type"] == "single_select"
                    else set(item["correct_option_ids"])
                )
                if not correct_ids.issubset(set(option_ids)):
                    self._reject(
                        "assessment.practice.invalid_definition",
                        f"items.{index}.options",
                    )
                continue
            self._numeric_semantics(item, index)

    def _numeric_semantics(self, item: Mapping[str, Any], index: int) -> None:
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
            self._reject(
                "assessment.practice.invalid_decimal", f"items.{index}.answer"
            )
        if answer["mode"] == "inclusive_range" and decimals[0] > decimals[1]:
            self._reject(
                "assessment.practice.invalid_decimal", f"items.{index}.answer"
            )

    @staticmethod
    def _decimal(value: str, scale: int, index: int) -> Decimal:
        match = DECIMAL_RE.fullmatch(value)
        if match is None or len(match.group(2) or "") != scale:
            raise PracticeDefinitionFailure(
                "assessment.practice.invalid_decimal", f"items.{index}.answer"
            )
        try:
            parsed = Decimal(value)
        except InvalidOperation as error:
            raise PracticeDefinitionFailure(
                "assessment.practice.invalid_decimal", f"items.{index}.answer"
            ) from error
        if value.startswith("-0") and parsed == 0:
            raise PracticeDefinitionFailure(
                "assessment.practice.invalid_decimal", f"items.{index}.answer"
            )
        return parsed

    def _unique(self, values: list[str], reference: str) -> None:
        if len(values) != len(set(values)):
            self._reject("assessment.practice.invalid_definition", reference)

    @staticmethod
    def _attempt_policy(value: Mapping[str, Any]) -> PracticeAttemptPolicy:
        return PracticeAttemptPolicy(
            policy_id=value["policy_id"],
            policy_version=value["policy_version"],
            max_attempts=value["max_attempts"],
            resume_allowed=value["resume_allowed"],
            history_visible=value["history_visible"],
        )

    @staticmethod
    def _references(
        values: list[Mapping[str, str]],
    ) -> tuple[PracticeResourceReference, ...]:
        return tuple(
            PracticeResourceReference(
                resource_id=value["resource_id"],
                resource_version=value["resource_version"],
                resource_digest=value["resource_digest"],
                title=value["title"],
            )
            for value in values
        )

    @staticmethod
    def _options(values: list[Mapping[str, str]]) -> tuple[PracticeOption, ...]:
        return tuple(
            PracticeOption(option_id=value["option_id"], label=value["label"])
            for value in values
        )

    @staticmethod
    def _feedback(value: Mapping[str, Any]) -> PracticeFeedback:
        return PracticeFeedback(
            feedback_id=value["feedback_id"],
            text=value["text"],
            review_reference_ids=tuple(value["review_reference_ids"]),
        )

    @classmethod
    def _feedback_pair(cls, value: Mapping[str, Any]) -> PracticeFeedbackPair:
        return PracticeFeedbackPair(
            correct=cls._feedback(value["correct"]),
            incorrect=cls._feedback(value["incorrect"]),
        )

    @staticmethod
    def _policy(value: Mapping[str, Any]) -> PracticeScoringPolicy:
        return PracticeScoringPolicy(
            policy_id=value["policy_id"],
            policy_version=value["policy_version"],
            max_score=value["max_score"],
        )

    @classmethod
    def _item(cls, value: Mapping[str, Any]) -> PracticeItem:
        common = {
            "item_id": value["item_id"],
            "item_version": value["item_version"],
            "item_type": value["item_type"],
            "prompt": value["prompt"],
            "scoring_policy": cls._policy(value["scoring_policy"]),
            "feedback": cls._feedback_pair(value["feedback"]),
        }
        if value["item_type"] == "single_select":
            return SingleSelectPracticeItem(
                **common,
                options=cls._options(value["options"]),
                correct_option_id=value["correct_option_id"],
            )
        if value["item_type"] == "multiple_select":
            return MultipleSelectPracticeItem(
                **common,
                options=cls._options(value["options"]),
                correct_option_ids=tuple(value["correct_option_ids"]),
            )
        response = value["response"]
        answer = value["answer"]
        return NumericPracticeItem(
            **common,
            response=NumericPracticeResponse(
                scale=response["scale"],
                unit_label=response["unit_label"],
                allow_negative=response["allow_negative"],
            ),
            answer=NumericPracticeAnswer(
                mode=answer["mode"],
                value=(Decimal(answer["value"]) if "value" in answer else None),
                lower=(Decimal(answer["lower"]) if "lower" in answer else None),
                upper=(Decimal(answer["upper"]) if "upper" in answer else None),
            ),
        )

    @staticmethod
    def _presentation_item(item: PracticeItem) -> PracticePresentationItem:
        common = {
            "item_id": item.item_id,
            "item_version": item.item_version,
            "item_type": item.item_type,
            "prompt": item.prompt,
            "scoring_policy_id": item.scoring_policy.policy_id,
            "scoring_policy_version": item.scoring_policy.policy_version,
            "max_score": item.scoring_policy.max_score,
        }
        if isinstance(item, (SingleSelectPracticeItem, MultipleSelectPracticeItem)):
            return SelectPracticePresentationItem(
                **common,
                options=item.options,
            )
        return NumericPracticePresentationItem(
            **common,
            scale=item.response.scale,
            unit_label=item.response.unit_label,
            allow_negative=item.response.allow_negative,
        )

    @staticmethod
    def _reject(code: str, reference: str) -> None:
        raise PracticeDefinitionFailure(code, reference)
