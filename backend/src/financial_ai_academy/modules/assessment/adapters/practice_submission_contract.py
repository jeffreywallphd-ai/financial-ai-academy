"""Closed practice-submission parser, scorer, and safe evidence mapper."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from ..domain.practice import (
    MultipleSelectPracticeResponse,
    NumericEntryPracticeResponse,
    PracticeDefinition,
    PracticeItemOutcome,
    PracticePresentationContext,
    PracticeResponse,
    PracticeResult,
    PracticeScoringError,
    PracticeSubmissionCandidate,
    SingleSelectPracticeResponse,
    score_practice,
)
from ..ports.practice_submission import PracticeSubmissionFailure


VERSION = "1.0.0"
POLICIES = {
    "single_select": "single-select-exact-match",
    "multiple_select": "multiple-select-exact-set",
    "numeric_entry": "numeric-exact-or-inclusive-range",
}


class ContractPracticeSubmissionAdapter:
    """Validates one exact response set and maps deterministic safe evidence."""

    def __init__(self, schema_dir: Path) -> None:
        checker = FormatChecker()
        schemas = {
            name: json.loads(
                (schema_dir / f"{name}.schema.json").read_text(encoding="utf-8")
            )
            for name in ("submission", "result", "completion-event")
        }
        registry = Registry().with_resources(
            (
                schema["$id"],
                Resource.from_contents(schema),
            )
            for schema in schemas.values()
        )
        self._validators: dict[str, Draft202012Validator] = {}
        for name, schema in schemas.items():
            Draft202012Validator.check_schema(schema)
            self._validators[name] = Draft202012Validator(
                schema, registry=registry, format_checker=checker
            )

    def parse_and_score(
        self,
        value: bytes,
        definition: PracticeDefinition,
        context: PracticePresentationContext,
        *,
        learner_id: str,
        attempt_id: str,
        evidence_id: str,
        event_id: str,
        submitted_at: datetime,
    ) -> PracticeSubmissionCandidate:
        document = self._document(value)
        self._versions(document)
        self._shape("submission", document)
        self._correlate(document, definition, context)
        responses = tuple(
            self._response(response) for response in document["responses"]
        )
        try:
            outcome = score_practice(definition, responses)
        except PracticeScoringError as error:
            self._reject("assessment.practice.invalid_response", error.reference)
        if submitted_at.tzinfo is None or submitted_at.utcoffset() != timezone.utc.utcoffset(submitted_at):
            self._reject(
                "assessment.practice.invalid_server_metadata", "submitted_at"
            )
        timestamp = submitted_at.isoformat().replace("+00:00", "Z")
        fingerprint = self.request_fingerprint(document)
        result = PracticeResult(
            schema_version=VERSION,
            attempt_id=attempt_id,
            evidence_id=evidence_id,
            learner_id=learner_id,
            submission_id=document["submission_id"],
            request_fingerprint=fingerprint,
            placement_id=context.placement_id,
            package_id=context.package_id,
            package_version=context.package_version,
            package_digest=context.package_digest,
            definition_digest=definition.definition_digest,
            practice_id=definition.practice_id,
            practice_version=definition.practice_version,
            attempt_policy_id=definition.attempt_policy.policy_id,
            attempt_policy_version=definition.attempt_policy.policy_version,
            score=outcome.score,
            max_score=outcome.max_score,
            outcome=outcome.outcome,
            review_reference_ids=outcome.review_reference_ids,
            item_results=outcome.item_results,
            submitted_at=submitted_at,
        )
        result_document = self.to_result_document(result)
        self._shape("result", result_document)
        event: dict[str, object] = {
            "schema_version": VERSION,
            "event_type": "assessment.practice.completed",
            "event_version": VERSION,
            "event_id": event_id,
            "owner": "assessment",
            "occurred_at": timestamp,
            "idempotency_key": evidence_id,
            "aggregate": {
                "aggregate_type": "practice_attempt",
                "aggregate_id": attempt_id,
            },
            "source": {"evidence_id": evidence_id},
            "payload": self._event_payload(result),
        }
        self._shape("completion-event", event)
        self._validate_event_correlation(event, result_document)
        return PracticeSubmissionCandidate(
            result=result,
            request_fingerprint=fingerprint,
            event_id=event_id,
            event=event,
            occurred_at=submitted_at,
        )

    @classmethod
    def request_fingerprint(cls, document: Mapping[str, Any]) -> str:
        canonical = copy.deepcopy(dict(document))
        responses = canonical.get("responses")
        if not isinstance(responses, list):
            cls._reject("assessment.practice.schema_invalid", "responses")
        for response in responses:
            if isinstance(response, dict) and isinstance(
                response.get("selected_option_ids"), list
            ):
                response["selected_option_ids"] = sorted(
                    response["selected_option_ids"]
                )
        canonical["responses"] = sorted(
            responses,
            key=lambda response: (
                str(response.get("item_id", ""))
                if isinstance(response, Mapping)
                else ""
            ),
        )
        payload = json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def to_result_document(result: PracticeResult) -> dict[str, Any]:
        return {
            "schema_version": result.schema_version,
            "attempt_id": result.attempt_id,
            "evidence_id": result.evidence_id,
            "learner_id": result.learner_id,
            "submission_id": result.submission_id,
            "request_fingerprint": result.request_fingerprint,
            "placement_id": result.placement_id,
            "package_id": result.package_id,
            "package_version": result.package_version,
            "package_digest": result.package_digest,
            "definition_digest": result.definition_digest,
            "practice_id": result.practice_id,
            "practice_version": result.practice_version,
            "attempt_policy_id": result.attempt_policy_id,
            "attempt_policy_version": result.attempt_policy_version,
            "score": result.score,
            "max_score": result.max_score,
            "outcome": result.outcome,
            "review_reference_ids": list(result.review_reference_ids),
            "item_results": [
                ContractPracticeSubmissionAdapter._item_result_document(item)
                for item in result.item_results
            ],
            "submitted_at": result.submitted_at.isoformat().replace(
                "+00:00", "Z"
            ),
        }

    @staticmethod
    def _item_result_document(item: PracticeItemOutcome) -> dict[str, Any]:
        response = item.response
        value: dict[str, Any] = {
            "item_id": response.item_id,
            "item_version": response.item_version,
            "item_type": response.item_type,
            "scoring_policy_id": response.scoring_policy_id,
            "scoring_policy_version": response.scoring_policy_version,
            "score": item.score,
            "max_score": item.max_score,
            "correct": item.correct,
            "feedback": {
                "feedback_id": item.feedback.feedback_id,
                "text": item.feedback.text,
                "review_reference_ids": list(
                    item.feedback.review_reference_ids
                ),
            },
        }
        if isinstance(response, SingleSelectPracticeResponse):
            value["selected_option_id"] = response.selected_option_id
        elif isinstance(response, MultipleSelectPracticeResponse):
            value["selected_option_ids"] = list(response.selected_option_ids)
        else:
            value["entered_value"] = response.entered_value
        return value

    @staticmethod
    def _event_payload(result: PracticeResult) -> dict[str, Any]:
        return {
            "learner_id": result.learner_id,
            "submission_id": result.submission_id,
            "placement_id": result.placement_id,
            "package_id": result.package_id,
            "package_version": result.package_version,
            "package_digest": result.package_digest,
            "definition_digest": result.definition_digest,
            "practice_id": result.practice_id,
            "practice_version": result.practice_version,
            "attempt_policy_id": result.attempt_policy_id,
            "attempt_policy_version": result.attempt_policy_version,
            "score": result.score,
            "max_score": result.max_score,
            "outcome": result.outcome,
            "item_scores": [
                {
                    "item_id": item.response.item_id,
                    "item_version": item.response.item_version,
                    "item_type": item.response.item_type,
                    "scoring_policy_id": item.response.scoring_policy_id,
                    "scoring_policy_version": (
                        item.response.scoring_policy_version
                    ),
                    "score": item.score,
                    "max_score": item.max_score,
                }
                for item in result.item_results
            ],
            "completed_at": result.submitted_at.isoformat().replace(
                "+00:00", "Z"
            ),
        }

    @staticmethod
    def _document(value: bytes) -> dict[str, Any]:
        try:
            document = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise PracticeSubmissionFailure(
                "assessment.practice.schema_invalid", "submission"
            ) from error
        if not isinstance(document, dict):
            raise PracticeSubmissionFailure(
                "assessment.practice.schema_invalid", "submission"
            )
        return document

    def _versions(self, document: Mapping[str, Any]) -> None:
        if document.get("schema_version") != VERSION:
            self._reject(
                "assessment.practice.unsupported_version", "schema_version"
            )
        if document.get("practice_version") not in (None, VERSION):
            self._reject(
                "assessment.practice.unsupported_version", "practice_version"
            )
        responses = document.get("responses")
        if not isinstance(responses, list):
            return
        for index, response in enumerate(responses):
            if not isinstance(response, Mapping):
                continue
            item_type = response.get("item_type")
            if isinstance(item_type, str) and item_type not in POLICIES:
                self._reject(
                    "assessment.practice.unsupported_item_type",
                    f"responses.{index}.item_type",
                )
            if response.get("item_version") not in (None, VERSION):
                self._reject(
                    "assessment.practice.unsupported_version",
                    f"responses.{index}.item_version",
                )
            if isinstance(item_type, str) and item_type in POLICIES:
                if response.get("scoring_policy_id") not in (
                    None,
                    POLICIES[item_type],
                ) or response.get("scoring_policy_version") not in (
                    None,
                    VERSION,
                ):
                    self._reject(
                        "assessment.practice.unsupported_policy",
                        f"responses.{index}.scoring_policy_id",
                    )

    def _shape(self, kind: str, document: Mapping[str, Any]) -> None:
        error = next(iter(self._validators[kind].iter_errors(document)), None)
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            self._reject(
                "assessment.practice.schema_invalid", reference or kind
            )

    def _correlate(
        self,
        document: Mapping[str, Any],
        definition: PracticeDefinition,
        context: PracticePresentationContext,
    ) -> None:
        expected = {
            "placement_id": context.placement_id,
            "package_id": context.package_id,
            "package_version": context.package_version,
            "package_digest": context.package_digest,
            "definition_digest": definition.definition_digest,
            "practice_id": definition.practice_id,
            "practice_version": definition.practice_version,
            "attempt_policy_id": definition.attempt_policy.policy_id,
            "attempt_policy_version": definition.attempt_policy.policy_version,
        }
        for name, value in expected.items():
            if document.get(name) != value:
                self._reject("assessment.practice.stale_reference", name)

    @staticmethod
    def _response(value: Mapping[str, Any]) -> PracticeResponse:
        common = {
            "item_id": value["item_id"],
            "item_version": value["item_version"],
            "item_type": value["item_type"],
            "scoring_policy_id": value["scoring_policy_id"],
            "scoring_policy_version": value["scoring_policy_version"],
        }
        if value["item_type"] == "single_select":
            return SingleSelectPracticeResponse(
                **common, selected_option_id=value["selected_option_id"]
            )
        if value["item_type"] == "multiple_select":
            return MultipleSelectPracticeResponse(
                **common,
                selected_option_ids=tuple(sorted(value["selected_option_ids"])),
            )
        return NumericEntryPracticeResponse(
            **common, entered_value=value["entered_value"]
        )

    def _validate_event_correlation(
        self, event: Mapping[str, object], result: Mapping[str, object]
    ) -> None:
        self._shape("result", result)
        expected = {
            "occurred_at": result["submitted_at"],
            "idempotency_key": result["evidence_id"],
            "aggregate": {
                "aggregate_type": "practice_attempt",
                "aggregate_id": result["attempt_id"],
            },
            "source": {"evidence_id": result["evidence_id"]},
        }
        for name, value in expected.items():
            if event.get(name) != value:
                self._reject("assessment.practice.stale_reference", name)
        payload = event.get("payload")
        if not isinstance(payload, Mapping):
            self._reject("assessment.practice.stale_reference", "payload")
        scalar_payload = {
            "learner_id": result["learner_id"],
            "submission_id": result["submission_id"],
            "placement_id": result["placement_id"],
            "package_id": result["package_id"],
            "package_version": result["package_version"],
            "package_digest": result["package_digest"],
            "definition_digest": result["definition_digest"],
            "practice_id": result["practice_id"],
            "practice_version": result["practice_version"],
            "attempt_policy_id": result["attempt_policy_id"],
            "attempt_policy_version": result["attempt_policy_version"],
            "score": result["score"],
            "max_score": result["max_score"],
            "outcome": result["outcome"],
            "completed_at": result["submitted_at"],
        }
        if any(payload.get(name) != value for name, value in scalar_payload.items()):
            self._reject("assessment.practice.stale_reference", "payload")
        expected_scores = [
            {
                key: item[key]
                for key in (
                    "item_id",
                    "item_version",
                    "item_type",
                    "scoring_policy_id",
                    "scoring_policy_version",
                    "score",
                    "max_score",
                )
            }
            for item in result["item_results"]  # type: ignore[union-attr]
        ]
        if payload.get("item_scores") != expected_scores:
            self._reject("assessment.practice.stale_reference", "payload")

    @staticmethod
    def _reject(code: str, reference: str) -> None:
        raise PracticeSubmissionFailure(code, reference)
