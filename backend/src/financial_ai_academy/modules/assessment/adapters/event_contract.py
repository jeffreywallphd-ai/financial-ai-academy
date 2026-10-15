"""Executable Assessment completion-event contract adapter."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from ..ports.event_parser import EventParsingFailure
from ..public import KnowledgeCheckCompletionEvent


class ContractAssessmentEventParser:
    def __init__(self, schema_dir: Path) -> None:
        schema = json.loads(
            (schema_dir / "knowledge-check-completed.schema.json").read_text(
                encoding="utf-8"
            )
        )
        Draft202012Validator.check_schema(schema)
        self._validator = Draft202012Validator(
            schema, format_checker=FormatChecker()
        )

    def parse(
        self, value: Mapping[str, object]
    ) -> KnowledgeCheckCompletionEvent:
        document = dict(value)
        self._versions(document)
        validation_error = next(
            iter(self._validator.iter_errors(document)), None
        )
        if validation_error is not None:
            reference = ".".join(
                str(part) for part in validation_error.absolute_path
            )
            raise EventParsingFailure(
                "assessment.schema_invalid", reference or "event"
            )
        aggregate = self._mapping(document["aggregate"], "aggregate")
        source = self._mapping(document["source"], "source")
        payload = self._mapping(document["payload"], "payload")
        if document["idempotency_key"] != source["evidence_id"]:
            raise EventParsingFailure(
                "assessment.inconsistent_event", "idempotency_key"
            )
        occurred_at = self._timestamp(document["occurred_at"], "occurred_at")
        completed_at = self._timestamp(
            payload["completed_at"], "payload.completed_at"
        )
        if occurred_at != completed_at:
            raise EventParsingFailure(
                "assessment.inconsistent_event", "payload.completed_at"
            )
        return KnowledgeCheckCompletionEvent(
            schema_version=str(document["schema_version"]),
            event_id=str(document["event_id"]),
            event_type=str(document["event_type"]),
            event_version=str(document["event_version"]),
            owner=str(document["owner"]),
            occurred_at=occurred_at,
            idempotency_key=str(document["idempotency_key"]),
            attempt_id=str(aggregate["aggregate_id"]),
            evidence_id=str(source["evidence_id"]),
            learner_id=str(payload["learner_id"]),
            placement_id=str(payload["placement_id"]),
            package_id=str(payload["package_id"]),
            package_version=str(payload["package_version"]),
            package_digest=str(payload["package_digest"]),
            assessment_id=str(payload["assessment_id"]),
            assessment_version=str(payload["assessment_version"]),
            definition_digest=str(payload["definition_digest"]),
            item_id=str(payload["item_id"]),
            item_version=str(payload["item_version"]),
            scoring_policy_id=str(payload["scoring_policy_id"]),
            scoring_policy_version=str(payload["scoring_policy_version"]),
            score=int(payload["score"]),
            max_score=int(payload["max_score"]),
            completed_at=completed_at,
        )

    @staticmethod
    def _versions(document: Mapping[str, Any]) -> None:
        if (
            document.get("schema_version") != "1.0.0"
            or document.get("event_version") != "1.0.0"
        ):
            raise EventParsingFailure(
                "assessment.unsupported_event_version", "event_version"
            )
        if document.get("event_type") != "assessment.knowledge-check.completed":
            raise EventParsingFailure(
                "assessment.unsupported_event_version", "event_type"
            )

    @staticmethod
    def _mapping(value: object, reference: str) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise EventParsingFailure("assessment.schema_invalid", reference)
        return value

    @staticmethod
    def _timestamp(value: object, reference: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as error:
            raise EventParsingFailure(
                "assessment.schema_invalid", reference
            ) from error
        if parsed.tzinfo is None:
            raise EventParsingFailure("assessment.schema_invalid", reference)
        return parsed.astimezone(timezone.utc)
