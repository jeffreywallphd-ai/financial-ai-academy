"""JSON Schema adapter for the learner-preferences v1 pure core."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Never

from jsonschema import Draft202012Validator, FormatChecker

from ..domain.preferences import (
    ExperienceEntry,
    InvalidLearnerPreference,
    LearnerPreferenceProfile,
    LearningGoal,
    LearningInterest,
    PreferenceChange,
    PreferenceExport,
    PreferenceHistory,
    PreferenceMutation,
    PreferenceMutationIntent,
    apply_preference_mutation,
    canonical_digest,
    empty_preference_profile,
    profile_document,
    validate_preference_export,
    validate_preference_history,
    validate_preference_profile,
)
from ..ports.preference_contract import LearnerPreferenceContractFailure


VERSION = "1.0.0"


class ContractLearnerPreferenceAdapter:
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

    def parse_profile(self, value: bytes) -> LearnerPreferenceProfile:
        document = self._document(value, "profile")
        profile = self._profile(document)
        self._domain(validate_preference_profile, profile)
        return profile

    def parse_mutation_intent(self, value: bytes) -> PreferenceMutationIntent:
        document = self._document(value, "mutation-intent")
        mutation = document["mutation"]
        intent = PreferenceMutationIntent(
            schema_version=document["schema_version"],
            idempotency_key=document["idempotency_key"],
            expected_revision=document["expected_revision"],
            mutation=PreferenceMutation(
                operation=mutation["operation"],
                entry_id=mutation.get("entry_id"),
                title=mutation.get("title"),
                detail=mutation.get("detail"),
                subject=mutation.get("subject"),
                level=mutation.get("level"),
                label=mutation.get("label"),
                ordered_ids=tuple(mutation.get("ordered_ids", [])),
            ),
        )
        if intent.schema_version != VERSION:
            self._reject(
                "learner_preferences.unsupported_version", "schema_version"
            )
        return intent

    def parse_history(self, value: bytes) -> PreferenceHistory:
        document = self._document(value, "history")
        history = self._history(document)
        self._domain(validate_preference_history, history)
        return history

    def parse_export(self, value: bytes) -> PreferenceExport:
        document = self._document(value, "export")
        profile_bytes = json.dumps(
            document["profile"], ensure_ascii=False
        ).encode("utf-8")
        history_bytes = json.dumps(
            document["history"], ensure_ascii=False
        ).encode("utf-8")
        exported = PreferenceExport(
            schema_version=document["schema_version"],
            purpose=document["purpose"],
            limitations=tuple(document["limitations"]),
            exported_at=self._timestamp(document["exported_at"]),
            profile=self.parse_profile(profile_bytes),
            history=self.parse_history(history_bytes),
        )
        self._domain(validate_preference_export, exported)
        return exported

    def profile_document(
        self, value: LearnerPreferenceProfile
    ) -> dict[str, object]:
        self._domain(validate_preference_profile, value)
        return profile_document(value)

    def mutation_intent_document(
        self, value: PreferenceMutationIntent
    ) -> dict[str, object]:
        operation = value.mutation.operation
        mutation: dict[str, object] = {"operation": operation}
        if operation in {
            "update_goal",
            "archive_goal",
            "restore_goal",
            "remove_goal",
            "update_experience",
            "remove_experience",
            "rename_interest",
            "remove_interest",
        }:
            mutation["entry_id"] = value.mutation.entry_id
        if operation in {"create_goal", "update_goal"}:
            mutation["title"] = value.mutation.title
            mutation["detail"] = value.mutation.detail
        if operation in {"create_experience", "update_experience"}:
            mutation["subject"] = value.mutation.subject
            mutation["level"] = value.mutation.level
            mutation["detail"] = value.mutation.detail
        if operation in {"create_interest", "rename_interest"}:
            mutation["label"] = value.mutation.label
        if operation in {
            "reorder_goals",
            "reorder_experience",
            "reorder_interests",
        }:
            mutation["ordered_ids"] = list(value.mutation.ordered_ids)
        document = {
            "schema_version": value.schema_version,
            "idempotency_key": value.idempotency_key,
            "expected_revision": value.expected_revision,
            "mutation": mutation,
        }
        self._shape("mutation-intent", document)
        return document

    def history_document(self, value: PreferenceHistory) -> dict[str, object]:
        self._domain(validate_preference_history, value)
        document = {
            "schema_version": value.schema_version,
            "profile_id": value.profile_id,
            "current_revision": value.current_revision,
            "changes": [self._portable(change) for change in value.changes],
        }
        self._shape("history", document)
        return document

    def export_document(self, value: PreferenceExport) -> dict[str, object]:
        self._domain(validate_preference_export, value)
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
        return canonical_digest(value)

    def empty_profile(
        self,
        *,
        profile_id: str,
        learner_id: str,
        created_at: datetime,
    ) -> LearnerPreferenceProfile:
        try:
            return empty_preference_profile(
                profile_id=profile_id,
                learner_id=learner_id,
                created_at=created_at,
            )
        except InvalidLearnerPreference as error:
            self._reject(error.code, error.reference)

    def apply_mutation(
        self,
        profile: LearnerPreferenceProfile,
        intent: PreferenceMutationIntent,
        *,
        occurred_at: datetime,
        issued_id: str | None = None,
    ) -> tuple[LearnerPreferenceProfile, PreferenceChange]:
        try:
            return apply_preference_mutation(
                profile,
                intent,
                occurred_at=occurred_at,
                issued_id=issued_id,
            )
        except InvalidLearnerPreference as error:
            self._reject(error.code, error.reference)

    def _document(self, value: bytes, schema: str) -> dict[str, Any]:
        try:
            document = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._reject("learner_preferences.invalid_json", schema)
        if not isinstance(document, dict):
            self._reject("learner_preferences.invalid_shape", schema)
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
            code = "learner_preferences.invalid_shape"
            if first.validator == "maxItems":
                if path == "goals":
                    code = "learner_preferences.goal_limit"
                elif path == "experience":
                    code = "learner_preferences.experience_limit"
                elif path == "interests":
                    code = "learner_preferences.interest_limit"
                elif path == "changes":
                    code = "learner_preferences.history_limit"
            self._reject(code, path or schema)

    def _profile(self, document: Mapping[str, Any]) -> LearnerPreferenceProfile:
        return LearnerPreferenceProfile(
            schema_version=document["schema_version"],
            profile_id=document["profile_id"],
            learner_id=document["learner_id"],
            revision=document["revision"],
            goals=tuple(
                LearningGoal(
                    goal_id=item["goal_id"],
                    title=item["title"],
                    detail=item["detail"],
                    archived=item["archived"],
                    created_at=self._timestamp(item["created_at"]),
                    updated_at=self._timestamp(item["updated_at"]),
                )
                for item in document["goals"]
            ),
            experience=tuple(
                ExperienceEntry(
                    experience_id=item["experience_id"],
                    subject=item["subject"],
                    level=item["level"],
                    detail=item["detail"],
                    created_at=self._timestamp(item["created_at"]),
                    updated_at=self._timestamp(item["updated_at"]),
                )
                for item in document["experience"]
            ),
            interests=tuple(
                LearningInterest(
                    interest_id=item["interest_id"],
                    label=item["label"],
                    created_at=self._timestamp(item["created_at"]),
                    updated_at=self._timestamp(item["updated_at"]),
                )
                for item in document["interests"]
            ),
            created_at=self._timestamp(document["created_at"]),
            updated_at=self._timestamp(document["updated_at"]),
            profile_digest=document["profile_digest"],
        )

    def _history(self, document: Mapping[str, Any]) -> PreferenceHistory:
        return PreferenceHistory(
            schema_version=document["schema_version"],
            profile_id=document["profile_id"],
            current_revision=document["current_revision"],
            changes=tuple(
                PreferenceChange(
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

    def _timestamp(self, value: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            self._reject("learner_preferences.invalid_time", "timestamp")
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            self._reject("learner_preferences.invalid_time", "timestamp")
        return parsed.astimezone(timezone.utc)

    def _format_timestamp(self, value: datetime) -> str:
        if value.tzinfo is None or value.utcoffset() is None:
            self._reject("learner_preferences.invalid_time", "timestamp")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def _portable(self, value: object) -> dict[str, object]:
        document = asdict(value)
        for key, item in tuple(document.items()):
            if isinstance(item, datetime):
                document[key] = self._format_timestamp(item)
        return document

    def _domain(self, function: Any, *args: object) -> None:
        try:
            function(*args)
        except InvalidLearnerPreference as error:
            self._reject(error.code, error.reference)

    def _reject(self, code: str, reference: str) -> Never:
        raise LearnerPreferenceContractFailure(code, reference)
