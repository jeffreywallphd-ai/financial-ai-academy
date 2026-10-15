"""Closed parser for the executable private Assessment v1 definition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from ..domain.models import AssessmentDefinition, AssessmentOption
from ..ports.definition_parser import DefinitionParsingFailure
from ..public import KnowledgeCheckFeedback


class ContractAssessmentDefinitionParser:
    def __init__(self, schema_dir: Path) -> None:
        schema = json.loads(
            (schema_dir / "definition.schema.json").read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)
        self._validator = Draft202012Validator(schema)

    def parse(self, value: bytes) -> AssessmentDefinition:
        try:
            document = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise DefinitionParsingFailure(
                "assessment.schema_invalid", "definition"
            ) from error
        if not isinstance(document, dict):
            raise DefinitionParsingFailure(
                "assessment.schema_invalid", "definition"
            )
        self._versions(document)
        validation_error = next(iter(self._validator.iter_errors(document)), None)
        if validation_error is not None:
            reference = ".".join(
                str(part) for part in validation_error.absolute_path
            )
            raise DefinitionParsingFailure(
                "assessment.schema_invalid", reference or "definition"
            )
        assessment = document["assessment"]
        measured = hashlib.sha256(
            json.dumps(
                assessment,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        if measured != document["definition_digest"]:
            raise DefinitionParsingFailure(
                "assessment.definition_digest_mismatch", "definition_digest"
            )
        item = assessment["item"]
        option_ids = [option["option_id"] for option in item["options"]]
        if (
            len(option_ids) != len(set(option_ids))
            or item["correct_option_id"] not in option_ids
        ):
            raise DefinitionParsingFailure(
                "assessment.invalid_definition", "options"
            )
        return AssessmentDefinition(
            assessment_id=assessment["assessment_id"],
            assessment_version=assessment["assessment_version"],
            definition_digest=document["definition_digest"],
            item_type=assessment["item_type"],
            item_id=item["item_id"],
            item_version=item["item_version"],
            scoring_policy_id=assessment["scoring_policy"]["policy_id"],
            scoring_policy_version=assessment["scoring_policy"]["policy_version"],
            prompt=item["prompt"],
            options=tuple(
                AssessmentOption(option["option_id"], option["label"])
                for option in item["options"]
            ),
            correct_option_id=item["correct_option_id"],
            correct_feedback=self._feedback(item["feedback"]["correct"]),
            incorrect_feedback=self._feedback(item["feedback"]["incorrect"]),
        )

    @staticmethod
    def _versions(document: Mapping[str, Any]) -> None:
        if document.get("schema_version") != "1.0.0":
            raise DefinitionParsingFailure(
                "assessment.unsupported_version", "schema_version"
            )
        assessment = document.get("assessment")
        if not isinstance(assessment, Mapping):
            return
        if assessment.get("assessment_version") != "1.0.0":
            raise DefinitionParsingFailure(
                "assessment.unsupported_version", "assessment_version"
            )
        if assessment.get("item_type") != "single_select":
            raise DefinitionParsingFailure(
                "assessment.unsupported_item_type", "item_type"
            )
        policy = assessment.get("scoring_policy")
        if isinstance(policy, Mapping) and (
            policy.get("policy_id") != "single-select-exact-match"
            or policy.get("policy_version") != "1.0.0"
        ):
            raise DefinitionParsingFailure(
                "assessment.unsupported_policy", "scoring_policy"
            )

    @staticmethod
    def _feedback(value: Mapping[str, str]) -> KnowledgeCheckFeedback:
        return KnowledgeCheckFeedback(
            feedback_id=value["feedback_id"], text=value["text"]
        )

