"""Reusable control-plane application service composed from project ports."""

from __future__ import annotations

import copy
from typing import Any

from contracts import ControlError, success
from ports import CandidateAdapter, ProjectAdapter
from state import (
    DEFAULT_LEASE_MINUTES,
    claim_work,
    recover_work,
    release_work,
    renew_work,
    resume_work,
    submit_work,
)
from store import StateStore


class ControlPlane:
    def __init__(self, project: ProjectAdapter, candidate: CandidateAdapter, store: StateStore) -> None:
        self.project = project
        self.candidate = candidate
        self.store = store

    def _current_work(self, envelope: dict[str, Any], work_id: str) -> dict[str, Any]:
        current = envelope["work_items"].get(work_id)
        return copy.deepcopy(current) if current is not None else self.project.initial_work_state(work_id)

    @staticmethod
    def _successor_envelope(
        envelope: dict[str, Any], work_id: str, work: dict[str, Any]
    ) -> dict[str, Any]:
        successor = copy.deepcopy(envelope)
        successor["revision"] = int(envelope["revision"]) + 1
        successor["work_items"][work_id] = work
        return successor

    @staticmethod
    def _public_data(work: dict[str, Any], *, recovered: bool = False) -> dict[str, Any]:
        return {
            "work_id": work["work_id"],
            "state": work["state"],
            "work_revision": work["revision"],
            "claim": work.get("claim"),
            "submission": work.get("submission"),
            "transaction_recovered": recovered,
        }

    def status(self, work_id: str) -> dict[str, Any]:
        self.project.projection(work_id)
        envelope, recovered = self.store.read()
        work = self._current_work(envelope, work_id)
        next_action = {
            "ready": "claim",
            "released": "claim",
            "active": "resume, renew, submit, or release",
            "submitted": "verify the exact candidate",
        }.get(str(work.get("state")), "inspect the lifecycle state")
        data = self._public_data(work, recovered=recovered)
        data["next_action"] = next_action
        return success("status.ok", f"{work_id} is {work['state']}.", revision=envelope["revision"], data=data)

    def claim(
        self,
        work_id: str,
        *,
        owner: str,
        lease_minutes: int = DEFAULT_LEASE_MINUTES,
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        authority = self.project.require_delivery_authority(work_id)
        identity = self.candidate.current_identity()
        projection = self.project.projection(work_id)

        def transition(envelope: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
            work = self._current_work(envelope, work_id)
            successor_work = claim_work(
                work,
                owner=owner,
                base_revision=identity["head"],
                branch=identity["branch"],
                lease_minutes=lease_minutes,
                expected_revision=expected_revision,
            )
            return (
                self._successor_envelope(envelope, work_id, successor_work),
                self.project.claim_projection_updates(work_id, successor_work),
            )

        envelope, recovered = self.store.mutate(projection, transition)
        work = envelope["work_items"][work_id]
        data = self._public_data(work, recovered=recovered)
        data.update(
            {
                "approval_stages_checked": authority["approval_stages_checked"],
                "lower_level_approval_required": False,
                "mandatory_full_suite": False,
            }
        )
        return success("claim.created", f"Claimed {work_id}.", revision=envelope["revision"], data=data)

    def renew(
        self,
        work_id: str,
        *,
        owner: str,
        claim_id: str,
        lease_minutes: int = DEFAULT_LEASE_MINUTES,
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        self.project.require_delivery_authority(work_id)
        projection = self.project.projection(work_id)

        def transition(envelope: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
            work = self._current_work(envelope, work_id)
            successor_work = renew_work(work, owner=owner, claim_id=claim_id, lease_minutes=lease_minutes, expected_revision=expected_revision)
            return self._successor_envelope(envelope, work_id, successor_work), {}

        envelope, recovered = self.store.mutate(projection, transition)
        work = envelope["work_items"][work_id]
        return success("lease.renewed", f"Renewed {work_id}.", revision=envelope["revision"], data=self._public_data(work, recovered=recovered))

    def resume(self, work_id: str, *, owner: str, claim_id: str) -> dict[str, Any]:
        self.project.require_delivery_authority(work_id)
        envelope, recovered = self.store.read()
        work = self._current_work(envelope, work_id)
        resumed = resume_work(work, owner=owner, claim_id=claim_id)
        resumed["transaction_recovered"] = recovered
        resumed["manual_metadata_edit_required"] = False
        return success("work.resumed", f"Resumed {work_id}.", revision=envelope["revision"], data=resumed)

    def recover(
        self,
        work_id: str,
        *,
        owner: str,
        lease_minutes: int = DEFAULT_LEASE_MINUTES,
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        self.project.require_delivery_authority(work_id)
        identity = self.candidate.current_identity()
        projection = self.project.projection(work_id)

        def transition(envelope: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
            work = self._current_work(envelope, work_id)
            prior = work.get("claim") or {}
            successor_work = recover_work(
                work,
                owner=owner,
                base_revision=str(prior.get("base_revision") or identity["head"]),
                branch=identity["branch"],
                lease_minutes=lease_minutes,
                expected_revision=expected_revision,
            )
            return self._successor_envelope(envelope, work_id, successor_work), self.project.claim_projection_updates(work_id, successor_work)

        envelope, recovered = self.store.mutate(projection, transition)
        work = envelope["work_items"][work_id]
        return success("claim.recovered", f"Recovered {work_id} without manual metadata edits.", revision=envelope["revision"], data=self._public_data(work, recovered=recovered))

    def submit(
        self,
        work_id: str,
        *,
        owner: str,
        claim_id: str,
        candidate: str = "HEAD",
        declared_inputs: list[str] | None = None,
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        authority = self.project.require_delivery_authority(work_id)
        projection = self.project.projection(work_id)
        extra_inputs = declared_inputs or []

        def transition(envelope: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
            work = self._current_work(envelope, work_id)
            claim = work.get("claim") or {}
            submission = self.candidate.submission(
                base_revision=str(claim.get("base_revision", "")),
                candidate=candidate,
                allowed_paths=list(authority["allowed_paths"]),
                declared_inputs=list(authority["canonical_inputs"]) + extra_inputs,
            )
            successor_work = submit_work(work, owner=owner, claim_id=claim_id, submission=submission, expected_revision=expected_revision)
            return self._successor_envelope(envelope, work_id, successor_work), self.project.submit_projection_updates(work_id, successor_work)

        envelope, recovered = self.store.mutate(projection, transition)
        work = envelope["work_items"][work_id]
        return success("submission.recorded", f"Submitted exact candidate for {work_id}.", revision=envelope["revision"], data=self._public_data(work, recovered=recovered))

    def release(
        self,
        work_id: str,
        *,
        owner: str,
        claim_id: str,
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        self.project.require_delivery_authority(work_id)
        projection = self.project.projection(work_id)

        def transition(envelope: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
            work = self._current_work(envelope, work_id)
            successor_work = release_work(work, owner=owner, claim_id=claim_id, expected_revision=expected_revision)
            return self._successor_envelope(envelope, work_id, successor_work), self.project.release_projection_updates(work_id, successor_work)

        envelope, recovered = self.store.mutate(projection, transition)
        work = envelope["work_items"][work_id]
        return success("claim.released", f"Released {work_id} to ready.", revision=envelope["revision"], data=self._public_data(work, recovered=recovered))


def refusal(error: Exception) -> dict[str, Any]:
    if isinstance(error, ControlError):
        return error.as_result()
    raise error
