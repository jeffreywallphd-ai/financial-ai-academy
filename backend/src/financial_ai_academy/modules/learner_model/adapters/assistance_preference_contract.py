"""JSON Schema adapter for learner-assistance-preferences v1."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Never

from jsonschema import Draft202012Validator, FormatChecker

from ..domain.assistance_preferences import (
    AssistancePreferenceChange,
    AssistancePreferenceExport,
    AssistancePreferenceHistory,
    AssistancePreferenceMutation,
    AssistancePreferenceMutationIntent,
    AssistancePreferenceProfile,
    InvalidAssistancePreference,
    apply_assistance_preference_mutation,
    canonical_digest,
    default_assistance_preference_profile,
    profile_document,
    validate_assistance_preference_export,
    validate_assistance_preference_history,
    validate_assistance_preference_mutation_intent,
    validate_assistance_preference_profile,
)
from ..ports.assistance_preference_contract import (
    AssistancePreferenceContractFailure,
)


class ContractAssistancePreferenceAdapter:
    def __init__(self, schema_directory: Path) -> None:
        self._validators = {
            name: Draft202012Validator(
                json.loads((schema_directory / filename).read_text(encoding="utf-8")),
                format_checker=FormatChecker(),
            )
            for name, filename in {
                "profile": "profile.schema.json",
                "mutation-intent": "mutation-intent.schema.json",
                "history": "history.schema.json",
                "export": "export.schema.json",
            }.items()
        }

    def parse_profile(self, value: bytes) -> AssistancePreferenceProfile:
        document = self._document(value, "profile")
        profile = self._profile(document)
        self._domain(validate_assistance_preference_profile, profile)
        return profile

    def parse_mutation_intent(
        self, value: bytes
    ) -> AssistancePreferenceMutationIntent:
        document = self._document(value, "mutation-intent")
        mutation = document["mutation"]
        intent = AssistancePreferenceMutationIntent(
            schema_version=document["schema_version"],
            idempotency_key=document["idempotency_key"],
            expected_revision=document["expected_revision"],
            mutation=AssistancePreferenceMutation(
                operation=mutation["operation"],
                assistance_mode=mutation.get("assistance_mode"),
            ),
        )
        self._domain(validate_assistance_preference_mutation_intent, intent)
        return intent

    def parse_history(self, value: bytes) -> AssistancePreferenceHistory:
        document = self._document(value, "history")
        history = AssistancePreferenceHistory(
            schema_version=document["schema_version"],
            profile_id=document["profile_id"],
            current_revision=document["current_revision"],
            changes=tuple(
                AssistancePreferenceChange(
                    schema_version=item["schema_version"],
                    revision=item["revision"],
                    operation=item["operation"],
                    object_kind=item["object_kind"],
                    object_id=item["object_id"],
                    occurred_at=self._timestamp(item["occurred_at"]),
                    resulting_profile_digest=item["resulting_profile_digest"],
                )
                for item in document["changes"]
            ),
        )
        self._domain(validate_assistance_preference_history, history)
        return history

    def parse_export(self, value: bytes) -> AssistancePreferenceExport:
        document = self._document(value, "export")
        exported = AssistancePreferenceExport(
            schema_version=document["schema_version"],
            purpose=document["purpose"],
            limitations=tuple(document["limitations"]),
            exported_at=self._timestamp(document["exported_at"]),
            profile=self.parse_profile(self._bytes(document["profile"])),
            history=self.parse_history(self._bytes(document["history"])),
        )
        self._domain(validate_assistance_preference_export, exported)
        return exported

    def profile_document(
        self, value: AssistancePreferenceProfile
    ) -> dict[str, object]:
        self._domain(validate_assistance_preference_profile, value)
        document = profile_document(value)
        self._shape("profile", document)
        return document

    def mutation_intent_document(
        self, value: AssistancePreferenceMutationIntent
    ) -> dict[str, object]:
        self._domain(validate_assistance_preference_mutation_intent, value)
        mutation: dict[str, object] = {"operation": value.mutation.operation}
        if value.mutation.operation == "replace_preferences":
            mutation["assistance_mode"] = value.mutation.assistance_mode
        document = {
            "schema_version": value.schema_version,
            "idempotency_key": value.idempotency_key,
            "expected_revision": value.expected_revision,
            "mutation": mutation,
        }
        self._shape("mutation-intent", document)
        return document

    def history_document(
        self, value: AssistancePreferenceHistory
    ) -> dict[str, object]:
        self._domain(validate_assistance_preference_history, value)
        document = {
            "schema_version": value.schema_version,
            "profile_id": value.profile_id,
            "current_revision": value.current_revision,
            "changes": [
                {
                    "schema_version": change.schema_version,
                    "revision": change.revision,
                    "operation": change.operation,
                    "object_kind": change.object_kind,
                    "object_id": change.object_id,
                    "occurred_at": self._format_timestamp(change.occurred_at),
                    "resulting_profile_digest": change.resulting_profile_digest,
                }
                for change in value.changes
            ],
        }
        self._shape("history", document)
        return document

    def export_document(
        self, value: AssistancePreferenceExport
    ) -> dict[str, object]:
        self._domain(validate_assistance_preference_export, value)
        document = {
            "schema_version": value.schema_version,
            "purpose": value.purpose,
            "limitations": list(value.limitations),
            "exported_at": self._format_timestamp(value.exported_at),
            "profile": self.profile_document(value.profile),
            "history": self.history_document(value.history),
        }
        self._shape("export", document)
        return document

    def canonical_digest(self, value: Mapping[str, object]) -> str:
        try:
            return canonical_digest(value)
        except InvalidAssistancePreference as error:
            self._reject(error.code, error.reference)

    def default_profile(
        self, *, profile_id: str, learner_id: str, created_at: datetime
    ) -> AssistancePreferenceProfile:
        try:
            return default_assistance_preference_profile(
                profile_id=profile_id,
                learner_id=learner_id,
                created_at=created_at,
            )
        except InvalidAssistancePreference as error:
            self._reject(error.code, error.reference)

    def apply_mutation(
        self,
        profile: AssistancePreferenceProfile,
        intent: AssistancePreferenceMutationIntent,
        *,
        occurred_at: datetime,
    ) -> tuple[AssistancePreferenceProfile, AssistancePreferenceChange]:
        try:
            return apply_assistance_preference_mutation(
                profile, intent, occurred_at=occurred_at
            )
        except InvalidAssistancePreference as error:
            self._reject(error.code, error.reference)

    def _document(self, value: bytes, schema: str) -> dict[str, Any]:
        try:
            document = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._reject("learner_assistance_preferences.invalid_json", schema)
        if not isinstance(document, dict):
            self._reject("learner_assistance_preferences.invalid_shape", schema)
        self._shape(schema, document)
        return document

    def _shape(self, schema: str, document: Mapping[str, object]) -> None:
        errors = sorted(
            self._validators[schema].iter_errors(document),
            key=lambda error: (
                tuple(str(part) for part in error.absolute_path),
                error.message,
            ),
        )
        if errors:
            first = errors[0]
            path = ".".join(str(part) for part in first.absolute_path)
            code = "learner_assistance_preferences.invalid_shape"
            if first.validator == "maxItems" and path == "changes":
                code = "learner_assistance_preferences.history_limit"
            self._reject(code, path or schema)

    def _profile(self, document: Mapping[str, Any]) -> AssistancePreferenceProfile:
        return AssistancePreferenceProfile(
            schema_version=document["schema_version"],
            profile_id=document["profile_id"],
            learner_id=document["learner_id"],
            revision=document["revision"],
            assistance_mode=document["assistance_mode"],
            created_at=self._timestamp(document["created_at"]),
            updated_at=self._timestamp(document["updated_at"]),
            profile_digest=document["profile_digest"],
        )

    def _timestamp(self, value: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            self._reject("learner_assistance_preferences.invalid_time", "timestamp")
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            self._reject("learner_assistance_preferences.invalid_time", "timestamp")
        return parsed.astimezone(timezone.utc)

    def _format_timestamp(self, value: datetime) -> str:
        if value.tzinfo is None or value.utcoffset() is None:
            self._reject("learner_assistance_preferences.invalid_time", "timestamp")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def _bytes(self, value: object) -> bytes:
        try:
            return json.dumps(value, ensure_ascii=False).encode("utf-8")
        except (TypeError, ValueError, UnicodeError):
            self._reject("learner_assistance_preferences.invalid_text", "document")

    def _domain(self, function: Any, *args: object) -> None:
        try:
            function(*args)
        except InvalidAssistancePreference as error:
            self._reject(error.code, error.reference)

    def _reject(self, code: str, reference: str) -> Never:
        raise AssistancePreferenceContractFailure(code, reference)
