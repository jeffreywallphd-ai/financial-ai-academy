"""Closed draft, retry-state, and completion-replay contract adapter."""

from __future__ import annotations

import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from ..domain.practice import (
    MultipleSelectPracticeResponse,
    NumericEntryPracticeResponse,
    PracticeCompletionEvent,
    PracticeCompletionItemScore,
    PracticeDefinition,
    PracticeDraft,
    PracticeDraftSave,
    PracticePresentationContext,
    PracticeResponse,
    PracticeRetryState,
    PracticeScope,
    PracticeScoringError,
    SingleSelectPracticeResponse,
    validate_practice_response_subset,
)
from ..ports.practice_progress import PracticeProgressFailure


VERSION = "1.0.0"
POLICIES = {
    "single_select": "single-select-exact-match",
    "multiple_select": "multiple-select-exact-set",
    "numeric_entry": "numeric-exact-or-inclusive-range",
}


class ContractPracticeProgressAdapter:
    """Validates mutable draft input and immutable completion replay."""

    def __init__(self, schema_dir: Path) -> None:
        checker = FormatChecker()
        schemas = {
            name: json.loads(
                (schema_dir / f"{name}.schema.json").read_text(encoding="utf-8")
            )
            for name in ("draft-save", "draft", "retry-state", "completion-event")
        }
        registry = Registry().with_resources(
            (schema["$id"], Resource.from_contents(schema))
            for schema in schemas.values()
        )
        self._validators: dict[str, Draft202012Validator] = {}
        for name, schema in schemas.items():
            Draft202012Validator.check_schema(schema)
            self._validators[name] = Draft202012Validator(
                schema, registry=registry, format_checker=checker
            )

    def parse_draft_save(
        self,
        value: bytes,
        definition: PracticeDefinition,
        context: PracticePresentationContext,
    ) -> PracticeDraftSave:
        document = self._document(value)
        self._version(document)
        self._shape("draft-save", document)
        scope = self._scope(document)
        if scope != self.scope(definition, context):
            self._reject("assessment.practice.stale_reference", "draft")
        responses = tuple(self._response(item) for item in document["responses"])
        try:
            validate_practice_response_subset(definition, responses)
        except PracticeScoringError as error:
            self._reject("assessment.practice.invalid_draft", error.reference)
        return PracticeDraftSave(
            scope=scope,
            expected_revision=int(document["expected_revision"]),
            responses=responses,
            response_fingerprint=self.response_fingerprint(document["responses"]),
        )

    def parse_completion_event(
        self, value: Mapping[str, Any]
    ) -> PracticeCompletionEvent:
        document = copy.deepcopy(dict(value))
        self._version(document)
        self._shape("completion-event", document)
        aggregate = document["aggregate"]
        source = document["source"]
        payload = document["payload"]
        if (
            aggregate["aggregate_type"] != "practice_attempt"
            or document["idempotency_key"] != source["evidence_id"]
            or document["occurred_at"] != payload["completed_at"]
        ):
            self._reject("assessment.practice.inconsistent_event", "event")
        item_scores = payload["item_scores"]
        item_ids = [item["item_id"] for item in item_scores]
        total_score = sum(int(item["score"]) for item in item_scores)
        total_maximum = sum(int(item["max_score"]) for item in item_scores)
        if (
            len(item_ids) != len(set(item_ids))
            or any(
                item["scoring_policy_id"] != POLICIES[item["item_type"]]
                for item in item_scores
            )
            or total_score != payload["score"]
            or total_maximum != payload["max_score"]
            or (payload["outcome"] == "all_correct")
            != (total_score == total_maximum)
        ):
            self._reject("assessment.practice.inconsistent_event", "payload")
        return PracticeCompletionEvent(
            schema_version=document["schema_version"],
            event_id=document["event_id"],
            event_type=document["event_type"],
            event_version=document["event_version"],
            owner=document["owner"],
            occurred_at=self._timestamp(document["occurred_at"]),
            idempotency_key=document["idempotency_key"],
            attempt_id=aggregate["aggregate_id"],
            evidence_id=source["evidence_id"],
            learner_id=payload["learner_id"],
            submission_id=payload["submission_id"],
            scope=self._scope(payload),
            score=int(payload["score"]),
            max_score=int(payload["max_score"]),
            outcome=payload["outcome"],
            item_scores=tuple(
                PracticeCompletionItemScore(
                    item_id=item["item_id"],
                    item_version=item["item_version"],
                    item_type=item["item_type"],
                    scoring_policy_id=item["scoring_policy_id"],
                    scoring_policy_version=item["scoring_policy_version"],
                    score=int(item["score"]),
                    max_score=int(item["max_score"]),
                )
                for item in item_scores
            ),
            completed_at=self._timestamp(payload["completed_at"]),
        )

    def draft_document(self, draft: PracticeDraft) -> dict[str, Any]:
        value = {
            "schema_version": VERSION,
            **self._scope_document(draft.scope),
            "responses": [self.response_document(item) for item in draft.responses],
            "revision": draft.revision,
            "saved_at": self._timestamp_text(draft.saved_at),
            "response_fingerprint": draft.response_fingerprint,
        }
        self._shape("draft", value)
        return value

    def retry_state_document(
        self, state: PracticeRetryState
    ) -> dict[str, Any]:
        value = {
            "schema_version": VERSION,
            **self._scope_document(state.scope),
            "attempts_used": state.attempts_used,
            "max_attempts": state.max_attempts,
            "attempts_remaining": state.attempts_remaining,
            "can_retry": state.can_retry,
            "state": state.state,
        }
        self._shape("retry-state", value)
        return value

    @staticmethod
    def scope(
        definition: PracticeDefinition,
        context: PracticePresentationContext,
    ) -> PracticeScope:
        return PracticeScope(
            placement_id=context.placement_id,
            package_id=context.package_id,
            package_version=context.package_version,
            package_digest=context.package_digest,
            definition_digest=definition.definition_digest,
            practice_id=definition.practice_id,
            practice_version=definition.practice_version,
            attempt_policy_id=definition.attempt_policy.policy_id,
            attempt_policy_version=definition.attempt_policy.policy_version,
        )

    @staticmethod
    def response_fingerprint(
        responses: Sequence[Mapping[str, Any]],
    ) -> str:
        canonical = copy.deepcopy(list(responses))
        for response in canonical:
            selected = response.get("selected_option_ids")
            if isinstance(selected, list):
                response["selected_option_ids"] = sorted(selected)
        canonical.sort(key=lambda item: str(item.get("item_id", "")))
        value = json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(value).hexdigest()

    @staticmethod
    def response_document(response: PracticeResponse) -> dict[str, Any]:
        value: dict[str, Any] = {
            "item_id": response.item_id,
            "item_version": response.item_version,
            "item_type": response.item_type,
            "scoring_policy_id": response.scoring_policy_id,
            "scoring_policy_version": response.scoring_policy_version,
        }
        if isinstance(response, SingleSelectPracticeResponse):
            value["selected_option_id"] = response.selected_option_id
        elif isinstance(response, MultipleSelectPracticeResponse):
            value["selected_option_ids"] = list(response.selected_option_ids)
        else:
            value["entered_value"] = response.entered_value
        return value

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

    @staticmethod
    def _scope(value: Mapping[str, Any]) -> PracticeScope:
        return PracticeScope(
            placement_id=value["placement_id"],
            package_id=value["package_id"],
            package_version=value["package_version"],
            package_digest=value["package_digest"],
            definition_digest=value["definition_digest"],
            practice_id=value["practice_id"],
            practice_version=value["practice_version"],
            attempt_policy_id=value["attempt_policy_id"],
            attempt_policy_version=value["attempt_policy_version"],
        )

    @staticmethod
    def _scope_document(scope: PracticeScope) -> dict[str, Any]:
        return {
            "placement_id": scope.placement_id,
            "package_id": scope.package_id,
            "package_version": scope.package_version,
            "package_digest": scope.package_digest,
            "definition_digest": scope.definition_digest,
            "practice_id": scope.practice_id,
            "practice_version": scope.practice_version,
            "attempt_policy_id": scope.attempt_policy_id,
            "attempt_policy_version": scope.attempt_policy_version,
        }

    @staticmethod
    def _document(value: bytes) -> dict[str, Any]:
        try:
            document = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise PracticeProgressFailure(
                "assessment.practice.schema_invalid", "draft"
            ) from error
        if not isinstance(document, dict):
            raise PracticeProgressFailure(
                "assessment.practice.schema_invalid", "draft"
            )
        return document

    def _shape(self, kind: str, document: Mapping[str, Any]) -> None:
        error = next(iter(self._validators[kind].iter_errors(document)), None)
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            self._reject(
                "assessment.practice.schema_invalid", reference or kind
            )

    def _version(self, document: Mapping[str, Any]) -> None:
        if document.get("schema_version") != VERSION:
            self._reject(
                "assessment.practice.unsupported_version", "schema_version"
            )

    @staticmethod
    def _timestamp(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    def _timestamp_text(value: datetime) -> str:
        return value.isoformat().replace("+00:00", "Z")

    @staticmethod
    def _reject(code: str, reference: str) -> None:
        raise PracticeProgressFailure(code, reference)
