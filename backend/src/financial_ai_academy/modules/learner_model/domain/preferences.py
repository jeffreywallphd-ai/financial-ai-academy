"""Explicit learner-preference values and deterministic mutation rules."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Literal, Mapping
from uuid import UUID


VERSION = "1.0.0"
MAX_GOALS = 20
MAX_EXPERIENCE_ENTRIES = 20
MAX_INTERESTS = 50
MAX_HISTORY = 100

_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
_DIGEST = re.compile(r"^[a-f0-9]{64}$")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class InvalidLearnerPreference(ValueError):
    """A stable, learner-safe preference contract failure."""

    def __init__(self, code: str, reference: str) -> None:
        super().__init__("The learning preference record is inconsistent.")
        self.code = code
        self.reference = reference


@dataclass(frozen=True, slots=True)
class LearningGoal:
    goal_id: str
    title: str
    detail: str | None
    archived: bool
    created_at: datetime
    updated_at: datetime


ExperienceLevel = Literal["new", "some_experience", "experienced"]


@dataclass(frozen=True, slots=True)
class ExperienceEntry:
    experience_id: str
    subject: str
    level: ExperienceLevel
    detail: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class LearningInterest:
    interest_id: str
    label: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class LearnerPreferenceProfile:
    schema_version: str
    profile_id: str
    learner_id: str
    revision: int
    goals: tuple[LearningGoal, ...]
    experience: tuple[ExperienceEntry, ...]
    interests: tuple[LearningInterest, ...]
    created_at: datetime
    updated_at: datetime
    profile_digest: str


@dataclass(frozen=True, slots=True)
class PreferenceMutation:
    operation: str
    entry_id: str | None = None
    title: str | None = None
    detail: str | None = None
    subject: str | None = None
    level: ExperienceLevel | None = None
    label: str | None = None
    ordered_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PreferenceMutationIntent:
    schema_version: str
    idempotency_key: str
    expected_revision: int
    mutation: PreferenceMutation


@dataclass(frozen=True, slots=True)
class PreferenceChange:
    schema_version: str
    revision: int
    operation: str
    object_kind: str | None
    object_id: str | None
    occurred_at: datetime
    resulting_profile_digest: str


@dataclass(frozen=True, slots=True)
class PreferenceHistory:
    schema_version: str
    profile_id: str
    current_revision: int
    changes: tuple[PreferenceChange, ...]


@dataclass(frozen=True, slots=True)
class PreferenceExport:
    schema_version: str
    purpose: str
    limitations: tuple[str, ...]
    exported_at: datetime
    profile: LearnerPreferenceProfile
    history: PreferenceHistory


def canonical_digest(value: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def empty_preference_profile(
    *,
    profile_id: str,
    learner_id: str,
    created_at: datetime,
) -> LearnerPreferenceProfile:
    profile = LearnerPreferenceProfile(
        schema_version=VERSION,
        profile_id=profile_id,
        learner_id=learner_id,
        revision=1,
        goals=(),
        experience=(),
        interests=(),
        created_at=_aware(created_at, "created_at"),
        updated_at=_aware(created_at, "updated_at"),
        profile_digest="0" * 64,
    )
    profile = _seal(profile)
    validate_preference_profile(profile)
    return profile


def validate_preference_profile(profile: LearnerPreferenceProfile) -> None:
    if profile.schema_version != VERSION:
        _reject("learner_preferences.unsupported_version", "schema_version")
    _identifier(profile.profile_id, "profile_id")
    try:
        UUID(profile.learner_id)
    except (ValueError, AttributeError) as error:
        raise InvalidLearnerPreference(
            "learner_preferences.invalid_identity", "learner_id"
        ) from error
    if profile.revision < 1:
        _reject("learner_preferences.invalid_revision", "revision")
    created_at = _aware(profile.created_at, "created_at")
    updated_at = _aware(profile.updated_at, "updated_at")
    if updated_at < created_at:
        _reject("learner_preferences.invalid_time", "updated_at")
    if len(profile.goals) > MAX_GOALS:
        _reject("learner_preferences.goal_limit", "goals")
    if len(profile.experience) > MAX_EXPERIENCE_ENTRIES:
        _reject("learner_preferences.experience_limit", "experience")
    if len(profile.interests) > MAX_INTERESTS:
        _reject("learner_preferences.interest_limit", "interests")

    all_ids: list[str] = []
    for goal in profile.goals:
        _identifier(goal.goal_id, "goal_id")
        _text(goal.title, "title", 160)
        _optional_text(goal.detail, "detail", 2_000)
        _entry_time(goal.created_at, goal.updated_at, created_at, updated_at, goal.goal_id)
        all_ids.append(goal.goal_id)
    for entry in profile.experience:
        _identifier(entry.experience_id, "experience_id")
        _text(entry.subject, "subject", 120)
        if entry.level not in {"new", "some_experience", "experienced"}:
            _reject("learner_preferences.invalid_level", entry.experience_id)
        _optional_text(entry.detail, "detail", 1_000)
        _entry_time(
            entry.created_at,
            entry.updated_at,
            created_at,
            updated_at,
            entry.experience_id,
        )
        all_ids.append(entry.experience_id)
    for interest in profile.interests:
        _identifier(interest.interest_id, "interest_id")
        _text(interest.label, "label", 120)
        _entry_time(
            interest.created_at,
            interest.updated_at,
            created_at,
            updated_at,
            interest.interest_id,
        )
        all_ids.append(interest.interest_id)
    if len(all_ids) != len(set(all_ids)):
        _reject("learner_preferences.duplicate_id", "profile")
    if _DIGEST.fullmatch(profile.profile_digest) is None:
        _reject("learner_preferences.invalid_digest", "profile_digest")
    expected = canonical_digest(profile_document(profile, include_digest=False))
    if profile.profile_digest != expected:
        _reject("learner_preferences.digest_mismatch", "profile_digest")


def validate_preference_history(
    history: PreferenceHistory,
    profile: LearnerPreferenceProfile | None = None,
) -> None:
    if history.schema_version != VERSION:
        _reject("learner_preferences.unsupported_version", "history.schema_version")
    _identifier(history.profile_id, "history.profile_id")
    if history.current_revision < 1 or len(history.changes) > MAX_HISTORY:
        _reject("learner_preferences.invalid_history", "history")
    if profile is not None and (
        history.profile_id != profile.profile_id
        or history.current_revision != profile.revision
    ):
        _reject("learner_preferences.history_mismatch", "history")
    prior_revision = 0
    prior_time: datetime | None = None
    for change in history.changes:
        if change.schema_version != VERSION or change.revision <= prior_revision:
            _reject("learner_preferences.invalid_history", "changes.revision")
        if change.revision > history.current_revision:
            _reject("learner_preferences.invalid_history", "changes.revision")
        occurred_at = _aware(change.occurred_at, "changes.occurred_at")
        if prior_time is not None and occurred_at < prior_time:
            _reject("learner_preferences.invalid_history", "changes.occurred_at")
        if (change.object_kind is None) != (change.object_id is None):
            _reject("learner_preferences.invalid_history", "changes.object")
        if change.object_kind not in {None, "goal", "experience", "interest", "profile"}:
            _reject("learner_preferences.invalid_history", "changes.object_kind")
        if change.object_id is not None:
            _identifier(change.object_id, "changes.object_id")
        if _DIGEST.fullmatch(change.resulting_profile_digest) is None:
            _reject("learner_preferences.invalid_history", "changes.digest")
        prior_revision = change.revision
        prior_time = occurred_at
    if profile is not None and history.changes:
        latest = history.changes[-1]
        if (
            latest.revision != profile.revision
            or latest.resulting_profile_digest != profile.profile_digest
        ):
            _reject("learner_preferences.history_mismatch", "changes")


def validate_preference_export(value: PreferenceExport) -> None:
    if value.schema_version != VERSION:
        _reject("learner_preferences.unsupported_version", "export.schema_version")
    _text(value.purpose, "purpose", 240)
    if not 1 <= len(value.limitations) <= 8:
        _reject("learner_preferences.invalid_export", "limitations")
    for limitation in value.limitations:
        _text(limitation, "limitations", 320)
    exported_at = _aware(value.exported_at, "exported_at")
    validate_preference_profile(value.profile)
    validate_preference_history(value.history, value.profile)
    if exported_at < value.profile.updated_at:
        _reject("learner_preferences.invalid_export", "exported_at")


def apply_preference_mutation(
    profile: LearnerPreferenceProfile,
    intent: PreferenceMutationIntent,
    *,
    occurred_at: datetime,
    issued_id: str | None = None,
) -> tuple[LearnerPreferenceProfile, PreferenceChange]:
    validate_preference_profile(profile)
    if intent.schema_version != VERSION:
        _reject("learner_preferences.unsupported_version", "intent.schema_version")
    _identifier(intent.idempotency_key, "idempotency_key")
    if intent.expected_revision != profile.revision:
        _reject("learner_preferences.stale_revision", "expected_revision")
    now = _aware(occurred_at, "occurred_at")
    if now < profile.updated_at:
        _reject("learner_preferences.invalid_time", "occurred_at")

    goals = list(profile.goals)
    experience = list(profile.experience)
    interests = list(profile.interests)
    mutation = intent.mutation
    operation = mutation.operation
    object_kind: str | None = None
    object_id: str | None = None

    if operation == "create_goal":
        object_kind, object_id = "goal", _new_id(profile, issued_id)
        if len(goals) >= MAX_GOALS:
            _reject("learner_preferences.goal_limit", "goals")
        goals.append(
            LearningGoal(
                goal_id=object_id,
                title=_text(mutation.title, "title", 160),
                detail=_optional_text(mutation.detail, "detail", 2_000),
                archived=False,
                created_at=now,
                updated_at=now,
            )
        )
    elif operation == "update_goal":
        object_kind, object_id = "goal", _required_id(mutation.entry_id)
        index, current = _find(goals, "goal_id", object_id)
        title = _text(mutation.title, "title", 160)
        detail = _optional_text(mutation.detail, "detail", 2_000)
        if current.title == title and current.detail == detail:
            _reject("learner_preferences.no_change", "mutation")
        replacement = replace(
            current,
            title=title,
            detail=detail,
            updated_at=now,
        )
        goals[index] = replacement
    elif operation in {"archive_goal", "restore_goal"}:
        object_kind, object_id = "goal", _required_id(mutation.entry_id)
        index, current = _find(goals, "goal_id", object_id)
        archived = operation == "archive_goal"
        if current.archived == archived:
            _reject("learner_preferences.no_change", "mutation")
        replacement = replace(current, archived=archived, updated_at=now)
        goals[index] = replacement
    elif operation == "remove_goal":
        object_kind, object_id = "goal", _required_id(mutation.entry_id)
        index, _ = _find(goals, "goal_id", object_id)
        goals.pop(index)
    elif operation == "reorder_goals":
        goals = _reorder(goals, "goal_id", mutation.ordered_ids)
        object_kind = "profile"
    elif operation == "create_experience":
        object_kind, object_id = "experience", _new_id(profile, issued_id)
        if len(experience) >= MAX_EXPERIENCE_ENTRIES:
            _reject("learner_preferences.experience_limit", "experience")
        experience.append(
            ExperienceEntry(
                experience_id=object_id,
                subject=_text(mutation.subject, "subject", 120),
                level=_level(mutation.level),
                detail=_optional_text(mutation.detail, "detail", 1_000),
                created_at=now,
                updated_at=now,
            )
        )
    elif operation == "update_experience":
        object_kind, object_id = "experience", _required_id(mutation.entry_id)
        index, current = _find(experience, "experience_id", object_id)
        subject = _text(mutation.subject, "subject", 120)
        level = _level(mutation.level)
        detail = _optional_text(mutation.detail, "detail", 1_000)
        if (
            current.subject == subject
            and current.level == level
            and current.detail == detail
        ):
            _reject("learner_preferences.no_change", "mutation")
        replacement = replace(
            current,
            subject=subject,
            level=level,
            detail=detail,
            updated_at=now,
        )
        experience[index] = replacement
    elif operation == "remove_experience":
        object_kind, object_id = "experience", _required_id(mutation.entry_id)
        index, _ = _find(experience, "experience_id", object_id)
        experience.pop(index)
    elif operation == "reorder_experience":
        experience = _reorder(experience, "experience_id", mutation.ordered_ids)
        object_kind = "profile"
    elif operation == "create_interest":
        object_kind, object_id = "interest", _new_id(profile, issued_id)
        if len(interests) >= MAX_INTERESTS:
            _reject("learner_preferences.interest_limit", "interests")
        interests.append(
            LearningInterest(
                interest_id=object_id,
                label=_text(mutation.label, "label", 120),
                created_at=now,
                updated_at=now,
            )
        )
    elif operation == "rename_interest":
        object_kind, object_id = "interest", _required_id(mutation.entry_id)
        index, current = _find(interests, "interest_id", object_id)
        label = _text(mutation.label, "label", 120)
        if current.label == label:
            _reject("learner_preferences.no_change", "mutation")
        replacement = replace(
            current,
            label=label,
            updated_at=now,
        )
        interests[index] = replacement
    elif operation == "remove_interest":
        object_kind, object_id = "interest", _required_id(mutation.entry_id)
        index, _ = _find(interests, "interest_id", object_id)
        interests.pop(index)
    elif operation == "reorder_interests":
        interests = _reorder(interests, "interest_id", mutation.ordered_ids)
        object_kind = "profile"
    elif operation == "reset_profile":
        if not goals and not experience and not interests:
            _reject("learner_preferences.no_change", "profile")
        goals, experience, interests = [], [], []
        object_kind = "profile"
    else:
        _reject("learner_preferences.unsupported_operation", "operation")

    next_profile = LearnerPreferenceProfile(
        schema_version=VERSION,
        profile_id=profile.profile_id,
        learner_id=profile.learner_id,
        revision=profile.revision + 1,
        goals=tuple(goals),
        experience=tuple(experience),
        interests=tuple(interests),
        created_at=profile.created_at,
        updated_at=now,
        profile_digest="0" * 64,
    )
    next_profile = _seal(next_profile)
    validate_preference_profile(next_profile)
    return next_profile, PreferenceChange(
        schema_version=VERSION,
        revision=next_profile.revision,
        operation=operation,
        object_kind=object_kind,
        object_id=object_id,
        occurred_at=now,
        resulting_profile_digest=next_profile.profile_digest,
    )


def profile_document(
    profile: LearnerPreferenceProfile,
    *,
    include_digest: bool = True,
) -> dict[str, object]:
    document: dict[str, object] = {
        "schema_version": profile.schema_version,
        "profile_id": profile.profile_id,
        "learner_id": profile.learner_id,
        "revision": profile.revision,
        "goals": [_portable(item) for item in profile.goals],
        "experience": [_portable(item) for item in profile.experience],
        "interests": [_portable(item) for item in profile.interests],
        "created_at": _timestamp(profile.created_at),
        "updated_at": _timestamp(profile.updated_at),
    }
    if include_digest:
        document["profile_digest"] = profile.profile_digest
    return document


def _seal(profile: LearnerPreferenceProfile) -> LearnerPreferenceProfile:
    return replace(
        profile,
        profile_digest=canonical_digest(profile_document(profile, include_digest=False)),
    )


def _portable(value: object) -> dict[str, object]:
    result = asdict(value)
    for key, item in tuple(result.items()):
        if isinstance(item, datetime):
            result[key] = _timestamp(item)
    return result


def _timestamp(value: datetime) -> str:
    return _aware(value, "timestamp").isoformat().replace("+00:00", "Z")


def _aware(value: datetime, reference: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        _reject("learner_preferences.invalid_time", reference)
    return value.astimezone(timezone.utc)


def _entry_time(
    created: datetime,
    updated: datetime,
    profile_created: datetime,
    profile_updated: datetime,
    reference: str,
) -> None:
    created = _aware(created, reference)
    updated = _aware(updated, reference)
    if created < profile_created or updated < created or updated > profile_updated:
        _reject("learner_preferences.invalid_time", reference)


def _identifier(value: str, reference: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        _reject("learner_preferences.invalid_identity", reference)
    return value


def _required_id(value: str | None) -> str:
    if value is None:
        _reject("learner_preferences.invalid_identity", "entry_id")
    return _identifier(value, "entry_id")


def _text(value: str | None, reference: str, maximum: int) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > maximum
        or value != value.strip()
        or _CONTROL.search(value) is not None
    ):
        _reject("learner_preferences.invalid_text", reference)
    return value


def _optional_text(value: str | None, reference: str, maximum: int) -> str | None:
    if value is None:
        return None
    return _text(value, reference, maximum)


def _level(value: ExperienceLevel | None) -> ExperienceLevel:
    if value not in {"new", "some_experience", "experienced"}:
        _reject("learner_preferences.invalid_level", "level")
    return value


def _new_id(profile: LearnerPreferenceProfile, value: str | None) -> str:
    value = _required_id(value)
    known = {
        *(item.goal_id for item in profile.goals),
        *(item.experience_id for item in profile.experience),
        *(item.interest_id for item in profile.interests),
    }
    if value in known:
        _reject("learner_preferences.duplicate_id", value)
    return value


def _find(values: list[object], field: str, identifier: str) -> tuple[int, object]:
    for index, value in enumerate(values):
        if getattr(value, field) == identifier:
            return index, value
    _reject("learner_preferences.not_found", identifier)


def _reorder(values: list[object], field: str, ordered_ids: tuple[str, ...]) -> list[object]:
    known = {getattr(value, field): value for value in values}
    if len(ordered_ids) != len(set(ordered_ids)) or set(ordered_ids) != set(known):
        _reject("learner_preferences.invalid_order", field)
    reordered = [known[identifier] for identifier in ordered_ids]
    if reordered == values:
        _reject("learner_preferences.no_change", field)
    return reordered


def _reject(code: str, reference: str) -> None:
    raise InvalidLearnerPreference(code, reference)
