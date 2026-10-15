"""Pure, project-neutral work-item lifecycle transitions."""

from __future__ import annotations

import copy
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from contracts import ControlError


Clock = Callable[[], datetime]
MAX_LEASE_MINUTES = 24 * 60
DEFAULT_LEASE_MINUTES = 120


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise ControlError(
            "state.malformed-timestamp",
            "Lifecycle state contains an invalid UTC timestamp.",
            {"value": value},
            ["Use bounded control maintenance; do not edit state by hand."],
        ) from error
    if parsed.tzinfo is None:
        raise ControlError(
            "state.malformed-timestamp",
            "Lifecycle timestamps must include a timezone.",
            {"value": value},
            ["Use a UTC timestamp ending in Z."],
        )
    return parsed.astimezone(timezone.utc)


def validate_lease_minutes(minutes: int) -> None:
    if not 1 <= minutes <= MAX_LEASE_MINUTES:
        raise ControlError(
            "lease.invalid-duration",
            f"Lease duration must be between 1 and {MAX_LEASE_MINUTES} minutes.",
            {"lease_minutes": minutes},
            [f"Retry with --lease-minutes between 1 and {MAX_LEASE_MINUTES}."],
        )


def append_event(
    work: dict[str, Any],
    event_type: str,
    now: datetime,
    details: dict[str, Any] | None = None,
) -> None:
    history = work.setdefault("history", [])
    history.append(
        {
            "sequence": len(history) + 1,
            "type": event_type,
            "at": timestamp(now),
            "details": details or {},
        }
    )


def new_work(work_id: str) -> dict[str, Any]:
    return {
        "work_id": work_id,
        "revision": 0,
        "state": "ready",
        "claim": None,
        "submission": None,
        "history": [],
    }


def assert_expected_revision(work: dict[str, Any], expected: int | None) -> None:
    actual = int(work.get("revision", 0))
    if expected is not None and expected != actual:
        raise ControlError(
            "state.version-conflict",
            "The work item changed after the caller observed it.",
            {"expected_revision": expected, "actual_revision": actual},
            ["Run status, inspect the latest state, and retry with its revision."],
        )


def live_claim(work: dict[str, Any], now: datetime) -> dict[str, Any]:
    claim = work.get("claim")
    if not isinstance(claim, dict):
        raise ControlError(
            "lease.missing",
            "The work item has no active claim.",
            {"state": work.get("state")},
            ["Claim the ready work item before attempting this operation."],
        )
    if parse_timestamp(str(claim.get("leased_until", ""))) <= now:
        raise ControlError(
            "lease.expired",
            "The lease expired and cannot be used as a live claim.",
            {
                "owner": claim.get("owner"),
                "claim_id": claim.get("claim_id"),
                "leased_until": claim.get("leased_until"),
            },
            ["Use recover to acquire a new claim while preserving prior history."],
        )
    return claim


def require_owner(
    work: dict[str, Any], owner: str, claim_id: str, now: datetime
) -> dict[str, Any]:
    claim = live_claim(work, now)
    if claim.get("owner") != owner or claim.get("claim_id") != claim_id:
        raise ControlError(
            "lease.owner-mismatch",
            "The live claim belongs to a different owner or claim identifier.",
            {
                "requested_owner": owner,
                "recorded_owner": claim.get("owner"),
                "requested_claim_id": claim_id,
                "recorded_claim_id": claim.get("claim_id"),
                "leased_until": claim.get("leased_until"),
            },
            ["Ask the active owner to release the work or wait for lease expiry."],
        )
    return claim


def claim_work(
    work: dict[str, Any],
    *,
    owner: str,
    base_revision: str,
    branch: str,
    lease_minutes: int,
    expected_revision: int | None,
    clock: Clock = utc_now,
) -> dict[str, Any]:
    validate_lease_minutes(lease_minutes)
    assert_expected_revision(work, expected_revision)
    now = clock()
    if work.get("state") not in {"ready", "released"}:
        prior = work.get("claim") or {}
        raise ControlError(
            "lifecycle.not-ready",
            "Only ready or released work can be claimed.",
            {"state": work.get("state"), "owner": prior.get("owner"), "leased_until": prior.get("leased_until")},
            ["Run status and follow its next legal action."],
        )
    successor = copy.deepcopy(work)
    claim_id = f"{work['work_id']}:{uuid.uuid4()}"
    successor["state"] = "active"
    successor["revision"] = int(work.get("revision", 0)) + 1
    successor["claim"] = {
        "claim_id": claim_id,
        "owner": owner,
        "base_revision": base_revision,
        "branch": branch,
        "claimed_at": timestamp(now),
        "leased_until": timestamp(now + timedelta(minutes=lease_minutes)),
    }
    successor["submission"] = None
    append_event(successor, "claimed", now, {"claim_id": claim_id, "owner": owner, "lease_minutes": lease_minutes})
    return successor


def renew_work(
    work: dict[str, Any],
    *,
    owner: str,
    claim_id: str,
    lease_minutes: int,
    expected_revision: int | None,
    clock: Clock = utc_now,
) -> dict[str, Any]:
    validate_lease_minutes(lease_minutes)
    assert_expected_revision(work, expected_revision)
    now = clock()
    require_owner(work, owner, claim_id, now)
    if work.get("state") != "active":
        raise ControlError("lifecycle.not-active", "Only active work can renew a lease.", {"state": work.get("state")}, ["Run status and follow its next legal action."])
    successor = copy.deepcopy(work)
    successor["revision"] = int(work.get("revision", 0)) + 1
    successor["claim"]["leased_until"] = timestamp(now + timedelta(minutes=lease_minutes))
    append_event(successor, "lease-renewed", now, {"lease_minutes": lease_minutes})
    return successor


def resume_work(
    work: dict[str, Any], *, owner: str, claim_id: str, clock: Clock = utc_now
) -> dict[str, Any]:
    now = clock()
    claim = require_owner(work, owner, claim_id, now)
    if work.get("state") != "active":
        raise ControlError("lifecycle.not-active", "Only active work can be resumed.", {"state": work.get("state")}, ["Run status and follow its next legal action."])
    return {
        "work_id": work["work_id"],
        "state": work["state"],
        "revision": work["revision"],
        "claim": copy.deepcopy(claim),
        "next_action": "continue work, renew if needed, then submit the exact candidate",
    }


def recover_work(
    work: dict[str, Any],
    *,
    owner: str,
    base_revision: str,
    branch: str,
    lease_minutes: int,
    expected_revision: int | None,
    clock: Clock = utc_now,
) -> dict[str, Any]:
    validate_lease_minutes(lease_minutes)
    assert_expected_revision(work, expected_revision)
    now = clock()
    prior = work.get("claim")
    if work.get("state") != "active" or not isinstance(prior, dict):
        raise ControlError("recovery.not-applicable", "Recovery requires active work with an expired claim.", {"state": work.get("state")}, ["Run status and use its next legal action."])
    if parse_timestamp(str(prior.get("leased_until", ""))) > now:
        raise ControlError(
            "recovery.active-owner",
            "An unexpired owner cannot be displaced by recovery.",
            {"owner": prior.get("owner"), "leased_until": prior.get("leased_until")},
            ["Ask the owner to release the work or wait for lease expiry."],
        )
    successor = copy.deepcopy(work)
    successor["revision"] = int(work.get("revision", 0)) + 1
    claim_id = f"{work['work_id']}:{uuid.uuid4()}"
    successor["claim"] = {
        "claim_id": claim_id,
        "owner": owner,
        "base_revision": base_revision,
        "branch": branch,
        "claimed_at": timestamp(now),
        "leased_until": timestamp(now + timedelta(minutes=lease_minutes)),
        "recovered_from": prior.get("claim_id"),
    }
    append_event(successor, "claim-recovered", now, {"prior_claim_id": prior.get("claim_id"), "owner": owner})
    return successor


def submit_work(
    work: dict[str, Any],
    *,
    owner: str,
    claim_id: str,
    submission: dict[str, Any],
    expected_revision: int | None,
    clock: Clock = utc_now,
) -> dict[str, Any]:
    assert_expected_revision(work, expected_revision)
    now = clock()
    require_owner(work, owner, claim_id, now)
    if work.get("state") != "active":
        raise ControlError("lifecycle.not-active", "Only active work can be submitted.", {"state": work.get("state")}, ["Run status and follow its next legal action."])
    successor = copy.deepcopy(work)
    successor["revision"] = int(work.get("revision", 0)) + 1
    successor["state"] = "submitted"
    successor["submission"] = copy.deepcopy(submission)
    append_event(successor, "submitted", now, {"candidate": submission.get("candidate"), "changed_path_count": len(submission.get("changed_paths", []))})
    return successor


def release_work(
    work: dict[str, Any],
    *,
    owner: str,
    claim_id: str,
    expected_revision: int | None,
    clock: Clock = utc_now,
) -> dict[str, Any]:
    assert_expected_revision(work, expected_revision)
    now = clock()
    require_owner(work, owner, claim_id, now)
    if work.get("state") != "active":
        raise ControlError("lifecycle.not-active", "Only unsubmitted active work can be released.", {"state": work.get("state")}, ["Submitted work proceeds to verification; inspect status."])
    successor = copy.deepcopy(work)
    successor["revision"] = int(work.get("revision", 0)) + 1
    successor["state"] = "released"
    append_event(successor, "released", now, {"owner": owner, "claim_id": claim_id})
    successor["claim"] = None
    return successor


def resubmit_work(
    work: dict[str, Any],
    *,
    owner: str,
    claim_id: str,
    submission: dict[str, Any],
    expected_revision: int | None,
    root_cause: str | None = None,
    clock: Clock = utc_now,
) -> dict[str, Any]:
    """Replace only the current submission projection with a corrected descendant."""

    assert_expected_revision(work, expected_revision)
    now = clock()
    claim = work.get("claim")
    if not isinstance(claim, dict) or claim.get("owner") != owner or claim.get("claim_id") != claim_id:
        raise ControlError(
            "lease.owner-mismatch",
            "Corrected resubmission requires the exact prior claim owner and identifier.",
            {"requested_owner": owner, "recorded_owner": claim.get("owner") if isinstance(claim, dict) else None},
            ["Use the recorded owner or a separately governed ownership-transfer route."],
        )
    if work.get("state") != "submitted" or not isinstance(work.get("submission"), dict):
        raise ControlError(
            "review.resubmit-not-applicable",
            "Corrected resubmission requires a previously submitted candidate.",
            {"state": work.get("state")},
            ["Submit and verify the initial exact candidate first."],
        )
    successor = copy.deepcopy(work)
    parent = str(work["submission"].get("candidate"))
    corrected = copy.deepcopy(submission)
    corrected["parent_candidate"] = parent
    if root_cause:
        corrected["root_cause"] = root_cause
    successor["submission"] = corrected
    successor["revision"] = int(work.get("revision", 0)) + 1
    append_event(
        successor,
        "corrected-descendant-submitted",
        now,
        {"parent_candidate": parent, "candidate": corrected.get("candidate"), "root_cause_recorded": bool(root_cause)},
    )
    return successor
