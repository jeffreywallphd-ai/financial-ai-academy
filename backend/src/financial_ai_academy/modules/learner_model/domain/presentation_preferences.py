"""Explicit presentation preferences and deterministic mutation rules."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Literal, Mapping
from uuid import UUID


VERSION = "1.0.0"
MAX_HISTORY = 100
DEFAULT_TEXT_SIZE = "default"
DEFAULT_TEXT_SPACING = "default"
DEFAULT_READING_WIDTH = "standard"
DEFAULT_MOTION = "system"

TextSize = Literal["default", "larger"]
TextSpacing = Literal["default", "increased"]
ReadingWidth = Literal["standard", "focused"]
MotionPreference = Literal["system", "reduce"]

_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
_DIGEST = re.compile(r"^[a-f0-9]{64}$")


class InvalidPresentationPreference(ValueError):
    """A stable, learner-safe presentation-preference contract failure."""

    def __init__(self, code: str, reference: str) -> None:
        super().__init__("The display preference record is inconsistent.")
        self.code = code
        self.reference = reference


@dataclass(frozen=True, slots=True)
class PresentationPreferenceProfile:
    schema_version: str
    profile_id: str
    learner_id: str
    revision: int
    text_size: TextSize
    text_spacing: TextSpacing
    reading_width: ReadingWidth
    motion: MotionPreference
    created_at: datetime
    updated_at: datetime
    profile_digest: str


@dataclass(frozen=True, slots=True)
class PresentationPreferenceMutation:
    operation: Literal["replace_preferences", "reset_profile"]
    text_size: TextSize | None = None
    text_spacing: TextSpacing | None = None
    reading_width: ReadingWidth | None = None
    motion: MotionPreference | None = None


@dataclass(frozen=True, slots=True)
class PresentationPreferenceMutationIntent:
    schema_version: str
    idempotency_key: str
    expected_revision: int
    mutation: PresentationPreferenceMutation


@dataclass(frozen=True, slots=True)
class PresentationPreferenceChange:
    schema_version: str
    revision: int
    operation: Literal["replace_preferences", "reset_profile"]
    object_kind: Literal["profile"]
    object_id: None
    occurred_at: datetime
    resulting_profile_digest: str


@dataclass(frozen=True, slots=True)
class PresentationPreferenceHistory:
    schema_version: str
    profile_id: str
    current_revision: int
    changes: tuple[PresentationPreferenceChange, ...]


@dataclass(frozen=True, slots=True)
class PresentationPreferenceExport:
    schema_version: str
    purpose: str
    limitations: tuple[str, ...]
    exported_at: datetime
    profile: PresentationPreferenceProfile
    history: PresentationPreferenceHistory


def canonical_digest(value: Mapping[str, object]) -> str:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as error:
        raise InvalidPresentationPreference(
            "learner_presentation_preferences.invalid_text", "canonical"
        ) from error
    return hashlib.sha256(encoded).hexdigest()


def default_presentation_preference_profile(
    *, profile_id: str, learner_id: str, created_at: datetime
) -> PresentationPreferenceProfile:
    profile = PresentationPreferenceProfile(
        schema_version=VERSION,
        profile_id=profile_id,
        learner_id=learner_id,
        revision=1,
        text_size=DEFAULT_TEXT_SIZE,
        text_spacing=DEFAULT_TEXT_SPACING,
        reading_width=DEFAULT_READING_WIDTH,
        motion=DEFAULT_MOTION,
        created_at=_aware(created_at, "created_at"),
        updated_at=_aware(created_at, "updated_at"),
        profile_digest="0" * 64,
    )
    profile = _seal(profile)
    validate_presentation_preference_profile(profile)
    return profile


def validate_presentation_preference_profile(
    profile: PresentationPreferenceProfile,
) -> None:
    if profile.schema_version != VERSION:
        _reject("unsupported_version", "schema_version")
    _identifier(profile.profile_id, "profile_id")
    try:
        UUID(profile.learner_id)
    except (ValueError, AttributeError) as error:
        raise InvalidPresentationPreference(
            "learner_presentation_preferences.invalid_identity", "learner_id"
        ) from error
    if profile.revision < 1:
        _reject("invalid_revision", "revision")
    created_at = _aware(profile.created_at, "created_at")
    updated_at = _aware(profile.updated_at, "updated_at")
    if updated_at < created_at:
        _reject("invalid_time", "updated_at")
    _choices(
        profile.text_size,
        profile.text_spacing,
        profile.reading_width,
        profile.motion,
    )
    if _DIGEST.fullmatch(profile.profile_digest) is None:
        _reject("invalid_digest", "profile_digest")
    expected = canonical_digest(profile_document(profile, include_digest=False))
    if profile.profile_digest != expected:
        _reject("digest_mismatch", "profile_digest")


def validate_presentation_preference_mutation_intent(
    intent: PresentationPreferenceMutationIntent,
) -> None:
    if intent.schema_version != VERSION:
        _reject("unsupported_version", "intent.schema_version")
    _identifier(intent.idempotency_key, "idempotency_key")
    if intent.expected_revision < 1:
        _reject("invalid_revision", "expected_revision")
    mutation = intent.mutation
    if mutation.operation == "replace_preferences":
        if None in {
            mutation.text_size,
            mutation.text_spacing,
            mutation.reading_width,
            mutation.motion,
        }:
            _reject("incomplete_replacement", "mutation")
        _choices(
            mutation.text_size,
            mutation.text_spacing,
            mutation.reading_width,
            mutation.motion,
        )
    elif mutation.operation == "reset_profile":
        if any(
            value is not None
            for value in (
                mutation.text_size,
                mutation.text_spacing,
                mutation.reading_width,
                mutation.motion,
            )
        ):
            _reject("invalid_mutation", "mutation")
    else:
        _reject("unsupported_operation", "mutation.operation")


def apply_presentation_preference_mutation(
    profile: PresentationPreferenceProfile,
    intent: PresentationPreferenceMutationIntent,
    *,
    occurred_at: datetime,
) -> tuple[PresentationPreferenceProfile, PresentationPreferenceChange]:
    validate_presentation_preference_profile(profile)
    validate_presentation_preference_mutation_intent(intent)
    if intent.expected_revision != profile.revision:
        _reject("stale_revision", "expected_revision")
    now = _aware(occurred_at, "occurred_at")
    if now < profile.updated_at:
        _reject("invalid_time", "occurred_at")
    mutation = intent.mutation
    if mutation.operation == "reset_profile":
        choices = (
            DEFAULT_TEXT_SIZE,
            DEFAULT_TEXT_SPACING,
            DEFAULT_READING_WIDTH,
            DEFAULT_MOTION,
        )
    else:
        choices = (
            mutation.text_size,
            mutation.text_spacing,
            mutation.reading_width,
            mutation.motion,
        )
    current = (
        profile.text_size,
        profile.text_spacing,
        profile.reading_width,
        profile.motion,
    )
    if choices == current:
        _reject("no_change", "mutation")
    text_size, text_spacing, reading_width, motion = choices
    _choices(text_size, text_spacing, reading_width, motion)
    next_profile = PresentationPreferenceProfile(
        schema_version=VERSION,
        profile_id=profile.profile_id,
        learner_id=profile.learner_id,
        revision=profile.revision + 1,
        text_size=text_size,
        text_spacing=text_spacing,
        reading_width=reading_width,
        motion=motion,
        created_at=profile.created_at,
        updated_at=now,
        profile_digest="0" * 64,
    )
    next_profile = _seal(next_profile)
    validate_presentation_preference_profile(next_profile)
    change = PresentationPreferenceChange(
        schema_version=VERSION,
        revision=next_profile.revision,
        operation=mutation.operation,
        object_kind="profile",
        object_id=None,
        occurred_at=now,
        resulting_profile_digest=next_profile.profile_digest,
    )
    return next_profile, change


def validate_presentation_preference_history(
    history: PresentationPreferenceHistory,
    profile: PresentationPreferenceProfile | None = None,
) -> None:
    if history.schema_version != VERSION:
        _reject("unsupported_version", "history.schema_version")
    _identifier(history.profile_id, "history.profile_id")
    if history.current_revision < 1 or len(history.changes) > MAX_HISTORY:
        _reject("invalid_history", "history")
    if profile is not None and (
        history.profile_id != profile.profile_id
        or history.current_revision != profile.revision
    ):
        _reject("history_mismatch", "history")
    prior_revision = 0
    prior_time: datetime | None = None
    for change in history.changes:
        if (
            change.schema_version != VERSION
            or change.revision <= prior_revision
            or change.revision > history.current_revision
            or change.operation not in {"replace_preferences", "reset_profile"}
            or change.object_kind != "profile"
            or change.object_id is not None
            or _DIGEST.fullmatch(change.resulting_profile_digest) is None
        ):
            _reject("invalid_history", "changes")
        occurred_at = _aware(change.occurred_at, "changes.occurred_at")
        if prior_time is not None and occurred_at < prior_time:
            _reject("invalid_history", "changes.occurred_at")
        prior_revision = change.revision
        prior_time = occurred_at
    if profile is not None and history.changes:
        latest = history.changes[-1]
        if (
            latest.revision != profile.revision
            or latest.resulting_profile_digest != profile.profile_digest
        ):
            _reject("history_mismatch", "changes")


def validate_presentation_preference_export(
    value: PresentationPreferenceExport,
) -> None:
    if value.schema_version != VERSION:
        _reject("unsupported_version", "export.schema_version")
    _text(value.purpose, "purpose", 240)
    if not 1 <= len(value.limitations) <= 8:
        _reject("invalid_export", "limitations")
    for limitation in value.limitations:
        _text(limitation, "limitations", 320)
    validate_presentation_preference_profile(value.profile)
    validate_presentation_preference_history(value.history, value.profile)
    if _aware(value.exported_at, "exported_at") < value.profile.updated_at:
        _reject("invalid_export", "exported_at")


def profile_document(
    profile: PresentationPreferenceProfile, *, include_digest: bool = True
) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": profile.schema_version,
        "profile_id": profile.profile_id,
        "learner_id": profile.learner_id,
        "revision": profile.revision,
        "text_size": profile.text_size,
        "text_spacing": profile.text_spacing,
        "reading_width": profile.reading_width,
        "motion": profile.motion,
        "created_at": _format_time(profile.created_at),
        "updated_at": _format_time(profile.updated_at),
    }
    if include_digest:
        value["profile_digest"] = profile.profile_digest
    return value


def _seal(profile: PresentationPreferenceProfile) -> PresentationPreferenceProfile:
    return replace(
        profile,
        profile_digest=canonical_digest(
            profile_document(profile, include_digest=False)
        ),
    )


def _choices(
    text_size: object,
    text_spacing: object,
    reading_width: object,
    motion: object,
) -> None:
    allowed = (
        (text_size, {"default", "larger"}, "text_size"),
        (text_spacing, {"default", "increased"}, "text_spacing"),
        (reading_width, {"standard", "focused"}, "reading_width"),
        (motion, {"system", "reduce"}, "motion"),
    )
    for value, values, reference in allowed:
        if value not in values:
            _reject("invalid_choice", reference)


def _identifier(value: object, reference: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        _reject("invalid_identity", reference)
    return value


def _text(value: object, reference: str, limit: int) -> str:
    if (
        not isinstance(value, str)
        or not 1 <= len(value) <= limit
        or value != value.strip()
        or any(0 <= ord(character) < 32 or 0xD800 <= ord(character) <= 0xDFFF for character in value)
    ):
        _reject("invalid_text", reference)
    return value


def _aware(value: datetime, reference: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _reject("invalid_time", reference)
    return value.astimezone(timezone.utc)


def _format_time(value: datetime) -> str:
    return _aware(value, "timestamp").isoformat().replace("+00:00", "Z")


def _reject(code: str, reference: str) -> None:
    raise InvalidPresentationPreference(
        f"learner_presentation_preferences.{code}", reference
    )
