"""JSON Schema adapter for learner-presentation-preferences v1."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Never

from jsonschema import Draft202012Validator, FormatChecker

from ..domain.presentation_preferences import (
    InvalidPresentationPreference,
    PresentationPreferenceChange,
    PresentationPreferenceExport,
    PresentationPreferenceHistory,
    PresentationPreferenceMutation,
    PresentationPreferenceMutationIntent,
    PresentationPreferenceProfile,
    apply_presentation_preference_mutation,
    canonical_digest,
    default_presentation_preference_profile,
    profile_document,
    validate_presentation_preference_export,
    validate_presentation_preference_history,
    validate_presentation_preference_mutation_intent,
    validate_presentation_preference_profile,
)
from ..ports.presentation_preference_contract import (
    PresentationPreferenceContractFailure,
)


class ContractPresentationPreferenceAdapter:
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

    def parse_profile(self, value: bytes) -> PresentationPreferenceProfile:
        document = self._document(value, "profile")
        profile = self._profile(document)
        self._domain(validate_presentation_preference_profile, profile)
        return profile

    def parse_mutation_intent(
        self, value: bytes
    ) -> PresentationPreferenceMutationIntent:
        document = self._document(value, "mutation-intent")
        mutation = document["mutation"]
        intent = PresentationPreferenceMutationIntent(
            schema_version=document["schema_version"],
            idempotency_key=document["idempotency_key"],
            expected_revision=document["expected_revision"],
            mutation=PresentationPreferenceMutation(
                operation=mutation["operation"],
                text_size=mutation.get("text_size"),
                text_spacing=mutation.get("text_spacing"),
                reading_width=mutation.get("reading_width"),
                motion=mutation.get("motion"),
            ),
        )
        self._domain(validate_presentation_preference_mutation_intent, intent)
        return intent

    def parse_history(self, value: bytes) -> PresentationPreferenceHistory:
        document = self._document(value, "history")
        history = PresentationPreferenceHistory(
            schema_version=document["schema_version"],
            profile_id=document["profile_id"],
            current_revision=document["current_revision"],
            changes=tuple(
                PresentationPreferenceChange(
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
        self._domain(validate_presentation_preference_history, history)
        return history

    def parse_export(self, value: bytes) -> PresentationPreferenceExport:
        document = self._document(value, "export")
        exported = PresentationPreferenceExport(
            schema_version=document["schema_version"],
            purpose=document["purpose"],
            limitations=tuple(document["limitations"]),
            exported_at=self._timestamp(document["exported_at"]),
            profile=self.parse_profile(self._bytes(document["profile"])),
            history=self.parse_history(self._bytes(document["history"])),
        )
        self._domain(validate_presentation_preference_export, exported)
        return exported

    def profile_document(
        self, value: PresentationPreferenceProfile
    ) -> dict[str, object]:
        self._domain(validate_presentation_preference_profile, value)
        document = profile_document(value)
        self._shape("profile", document)
        return document

    def mutation_intent_document(
        self, value: PresentationPreferenceMutationIntent
    ) -> dict[str, object]:
        self._domain(validate_presentation_preference_mutation_intent, value)
        mutation: dict[str, object] = {"operation": value.mutation.operation}
        if value.mutation.operation == "replace_preferences":
            mutation.update(
                text_size=value.mutation.text_size,
                text_spacing=value.mutation.text_spacing,
                reading_width=value.mutation.reading_width,
                motion=value.mutation.motion,
            )
        document = {
            "schema_version": value.schema_version,
            "idempotency_key": value.idempotency_key,
            "expected_revision": value.expected_revision,
            "mutation": mutation,
        }
        self._shape("mutation-intent", document)
        return document

    def history_document(
        self, value: PresentationPreferenceHistory
    ) -> dict[str, object]:
        self._domain(validate_presentation_preference_history, value)
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
        self, value: PresentationPreferenceExport
    ) -> dict[str, object]:
        self._domain(validate_presentation_preference_export, value)
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
        except InvalidPresentationPreference as error:
            self._reject(error.code, error.reference)

    def default_profile(
        self, *, profile_id: str, learner_id: str, created_at: datetime
    ) -> PresentationPreferenceProfile:
        try:
            return default_presentation_preference_profile(
                profile_id=profile_id,
                learner_id=learner_id,
                created_at=created_at,
            )
        except InvalidPresentationPreference as error:
            self._reject(error.code, error.reference)

    def apply_mutation(
        self,
        profile: PresentationPreferenceProfile,
        intent: PresentationPreferenceMutationIntent,
        *,
        occurred_at: datetime,
    ) -> tuple[PresentationPreferenceProfile, PresentationPreferenceChange]:
        try:
            return apply_presentation_preference_mutation(
                profile, intent, occurred_at=occurred_at
            )
        except InvalidPresentationPreference as error:
            self._reject(error.code, error.reference)

    def _document(self, value: bytes, schema: str) -> dict[str, Any]:
        try:
            document = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._reject("learner_presentation_preferences.invalid_json", schema)
        if not isinstance(document, dict):
            self._reject("learner_presentation_preferences.invalid_shape", schema)
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
            code = "learner_presentation_preferences.invalid_shape"
            if first.validator == "maxItems" and path == "changes":
                code = "learner_presentation_preferences.history_limit"
            self._reject(code, path or schema)

    def _profile(self, document: Mapping[str, Any]) -> PresentationPreferenceProfile:
        return PresentationPreferenceProfile(
            schema_version=document["schema_version"],
            profile_id=document["profile_id"],
            learner_id=document["learner_id"],
            revision=document["revision"],
            text_size=document["text_size"],
            text_spacing=document["text_spacing"],
            reading_width=document["reading_width"],
            motion=document["motion"],
            created_at=self._timestamp(document["created_at"]),
            updated_at=self._timestamp(document["updated_at"]),
            profile_digest=document["profile_digest"],
        )

    def _timestamp(self, value: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            self._reject("learner_presentation_preferences.invalid_time", "timestamp")
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            self._reject("learner_presentation_preferences.invalid_time", "timestamp")
        return parsed.astimezone(timezone.utc)

    def _format_timestamp(self, value: datetime) -> str:
        if value.tzinfo is None or value.utcoffset() is None:
            self._reject("learner_presentation_preferences.invalid_time", "timestamp")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def _bytes(self, value: object) -> bytes:
        try:
            return json.dumps(value, ensure_ascii=False).encode("utf-8")
        except (TypeError, ValueError, UnicodeError):
            self._reject("learner_presentation_preferences.invalid_text", "document")

    def _domain(self, function: Any, *args: object) -> None:
        try:
            function(*args)
        except InvalidPresentationPreference as error:
            self._reject(error.code, error.reference)

    def _reject(self, code: str, reference: str) -> Never:
        raise PresentationPreferenceContractFailure(code, reference)
