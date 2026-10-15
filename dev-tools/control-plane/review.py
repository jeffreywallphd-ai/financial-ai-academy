"""Reusable append-only technical review and corrected-descendant service."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from contracts import ControlError, success
from ports import CandidateAdapter, ProjectAdapter
from state import resubmit_work
from store import StateStore
from verification import CheckCatalog, ReceiptStore, validate_receipt


REVIEW_TYPE = "technical-control-plane-v1"
STATUSES = {"accepted", "changes-requested", "rejected"}
SEVERITIES = {"critical", "high", "medium", "low"}
ADVERSE = {"changes-requested", "rejected"}


class ReviewLedgerPort(Protocol):
    def rounds(self, work_id: str) -> list[dict[str, Any]]: ...

    def append(self, record: dict[str, Any]) -> None: ...


def open_findings(rounds: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    opened: dict[str, dict[str, Any]] = {}
    for round_record in rounds:
        for closure in round_record.get("closures", []):
            opened.pop(str(closure.get("finding_id")), None)
        for finding in round_record.get("findings", []):
            opened[str(finding["finding_id"])] = copy.deepcopy(finding)
    return opened


def consecutive_adverse(rounds: list[dict[str, Any]]) -> int:
    count = 0
    for item in reversed(rounds):
        if item.get("status") not in ADVERSE:
            break
        count += 1
    return count


def validate_findings(round_id: str, findings: object) -> list[dict[str, Any]]:
    if not isinstance(findings, list):
        raise ControlError("review.findings-invalid", "Review findings must be an array.", {}, ["Use the local review-request schema."])
    result: list[dict[str, Any]] = []
    for index, item in enumerate(findings, start=1):
        if not isinstance(item, dict):
            raise ControlError("review.findings-invalid", "Every finding must be an object.", {"index": index}, ["Use the local review-request schema."])
        severity = str(item.get("severity", ""))
        title = str(item.get("title", "")).strip()
        criterion = str(item.get("criterion", "")).strip()
        evidence = item.get("evidence")
        if severity not in SEVERITIES or not title or not criterion or not isinstance(evidence, list) or not evidence:
            raise ControlError("review.findings-invalid", "Each finding needs severity, title, criterion, and non-empty evidence.", {"index": index}, ["Complete the finding before recording the round."])
        result.append(
            {
                "finding_id": f"{round_id}-F{index:03d}",
                "severity": severity,
                "blocking": bool(item.get("blocking", severity in {"critical", "high"})),
                "title": title,
                "criterion": criterion,
                "evidence": [str(value) for value in evidence],
            }
        )
    return result


def validate_closures(closures: object, currently_open: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(closures, list):
        raise ControlError("review.closures-invalid", "Review closures must be an array.", {}, ["Use the local review-request schema."])
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(closures, start=1):
        if not isinstance(item, dict):
            raise ControlError("review.closures-invalid", "Every closure must be an object.", {"index": index}, ["Use the local review-request schema."])
        finding_id = str(item.get("finding_id", ""))
        evidence = item.get("evidence")
        if finding_id not in currently_open or finding_id in seen or not isinstance(evidence, list) or not evidence:
            raise ControlError("review.closures-invalid", "A closure must reference one open finding and non-empty evidence exactly once.", {"index": index, "finding_id": finding_id}, ["Replay the current open-finding IDs and add direct closure evidence."])
        seen.add(finding_id)
        result.append({"finding_id": finding_id, "evidence": [str(value) for value in evidence], "notes": str(item.get("notes", "")).strip()})
    return result


class ReviewService:
    def __init__(
        self,
        root: Path,
        project: ProjectAdapter,
        state: StateStore,
        candidate: CandidateAdapter,
        catalog: CheckCatalog,
        ledger: ReviewLedgerPort,
        receipts: ReceiptStore | None = None,
    ) -> None:
        self.root = root.resolve()
        self.project = project
        self.state = state
        self.candidate = candidate
        self.catalog = catalog
        self.ledger = ledger
        self.receipts = receipts or ReceiptStore(root)

    def _submitted(self, work_id: str) -> tuple[dict[str, Any], dict[str, Any], bool]:
        self.project.require_delivery_authority(work_id)
        envelope, recovered = self.state.read()
        work = envelope["work_items"].get(work_id)
        if not isinstance(work, dict) or work.get("state") != "submitted" or not isinstance(work.get("submission"), dict):
            raise ControlError("review.not-submitted", "Technical review requires a submitted exact candidate.", {"work_id": work_id, "state": work.get("state") if isinstance(work, dict) else None}, ["Submit and verify the candidate before review."])
        self.candidate.stable_identity(str(work["submission"]["candidate"]))
        return envelope, work, recovered

    def status(self, work_id: str) -> dict[str, Any]:
        rounds = self.ledger.rounds(work_id)
        opened = open_findings(rounds)
        blocking = sorted(identifier for identifier, item in opened.items() if item.get("blocking"))
        return success(
            "review.status",
            f"{work_id} has {len(rounds)} review round(s) and {len(opened)} open finding(s).",
            data={
                "work_id": work_id,
                "round_count": len(rounds),
                "latest_status": rounds[-1]["status"] if rounds else None,
                "open_finding_ids": sorted(opened),
                "open_blocking_finding_ids": blocking,
                "next_action": "record an independent review" if not rounds else ("correct and resubmit" if rounds[-1]["status"] in ADVERSE else "review complete"),
            },
        )

    def record(
        self,
        work_id: str,
        *,
        reviewer_label: str,
        status: str,
        receipt_path: Path,
        findings: object,
        closures: object,
        notes: str = "",
    ) -> dict[str, Any]:
        envelope, work, recovered = self._submitted(work_id)
        if status not in STATUSES:
            raise ControlError("review.status-invalid", "Technical review status is unsupported.", {"status": status}, ["Use accepted, changes-requested, or rejected."])
        owner = str((work.get("claim") or {}).get("owner", ""))
        if not reviewer_label.strip() or reviewer_label.strip() == owner:
            raise ControlError("review.not-independent", "The technical reviewer must differ from the current work owner.", {"owner": owner}, ["Use an independent reviewer label and statement."])
        receipt = self.receipts.load(receipt_path)
        receipt_errors = validate_receipt(receipt, self.catalog, current_candidate=str(work["submission"]["candidate"]))
        if receipt_errors:
            raise ControlError("review.receipt-invalid", "Review requires a current qualifying verification receipt.", {"errors": receipt_errors}, ["Run fresh affected verification for the exact candidate."])
        rounds = self.ledger.rounds(work_id)
        candidate = str(work["submission"]["candidate"])
        if any(item.get("candidate") == candidate for item in rounds):
            raise ControlError("review.candidate-already-reviewed", "This exact candidate already has an immutable review round.", {"candidate": candidate}, ["Correct and submit a strict descendant before another review."])
        round_id = f"R{len(rounds) + 1:02d}"
        opened = open_findings(rounds)
        validated_closures = validate_closures(closures, opened)
        for closure in validated_closures:
            opened.pop(closure["finding_id"], None)
        validated_findings = validate_findings(round_id, findings)
        for finding in validated_findings:
            opened[finding["finding_id"]] = finding
        blocking = sorted(identifier for identifier, item in opened.items() if item.get("blocking"))
        if status == "accepted" and blocking:
            raise ControlError("review.blocking-findings-open", "An accepted disposition cannot leave blocking findings open.", {"open_blocking_finding_ids": blocking}, ["Record explicit closure evidence on a corrected descendant."])
        if status in ADVERSE and not validated_findings:
            raise ControlError("review.adverse-without-finding", "An adverse disposition requires at least one reproducible finding.", {}, ["Record the violated criterion and evidence."])
        if consecutive_adverse(rounds) >= 2 and not str(work["submission"].get("root_cause", "")).strip():
            raise ControlError("review.root-cause-required", "A third review round after repeated adverse results requires root-cause evidence on the corrected submission.", {}, ["Add root-cause evidence during corrected resubmission."])
        record = {
            "subject": work_id,
            "review_type": REVIEW_TYPE,
            "reviewer_label": reviewer_label.strip(),
            "status": status,
            "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "round_id": round_id,
            "candidate": candidate,
            "verification_receipt_digest": receipt["receipt_digest"],
            "findings": validated_findings,
            "closures": validated_closures,
            "notes": notes.strip(),
        }
        self.ledger.append(record)
        return success("review.recorded", f"Recorded immutable {round_id} technical disposition for {work_id}.", revision=envelope["revision"], data={"work_id": work_id, "round_id": round_id, "status": status, "candidate": candidate, "open_finding_ids": sorted(opened), "open_blocking_finding_ids": blocking, "transaction_recovered": recovered})

    def resubmit(
        self,
        work_id: str,
        *,
        owner: str,
        claim_id: str,
        candidate: str = "HEAD",
        declared_inputs: list[str] | None = None,
        expected_revision: int | None = None,
        root_cause: str | None = None,
    ) -> dict[str, Any]:
        authority = self.project.require_delivery_authority(work_id)
        rounds = self.ledger.rounds(work_id)
        if not rounds or rounds[-1].get("status") not in ADVERSE:
            raise ControlError("review.resubmit-not-authorized", "Corrected resubmission requires the latest immutable review to be adverse.", {"latest_status": rounds[-1].get("status") if rounds else None}, ["Record the independent technical disposition first."])
        if consecutive_adverse(rounds) >= 2 and not (root_cause or "").strip():
            raise ControlError("review.root-cause-required", "A third candidate after two adverse rounds requires root-cause evidence.", {}, ["Pass concise root-cause evidence with the corrected resubmission."])
        projection = self.project.projection(work_id)

        def transition(envelope: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
            work = envelope["work_items"].get(work_id)
            if not isinstance(work, dict) or not isinstance(work.get("submission"), dict):
                raise ControlError("review.resubmit-not-applicable", "No prior submitted candidate is available.", {}, ["Submit and review the initial candidate first."])
            prior_candidate = str(work["submission"]["candidate"])
            claim = work.get("claim") or {}
            submission = self.candidate.submission(base_revision=str(claim.get("base_revision", "")), candidate=candidate, allowed_paths=list(authority["allowed_paths"]), declared_inputs=list(authority["canonical_inputs"]) + (declared_inputs or []))
            if not self.candidate.is_strict_descendant(prior_candidate, str(submission["candidate"])):
                raise ControlError("review.not-strict-descendant", "A corrected candidate must be a strict descendant of the reviewed candidate.", {"reviewed_candidate": prior_candidate, "candidate": submission["candidate"]}, ["Create and submit a clean descendant preserving prior history."])
            successor_work = resubmit_work(work, owner=owner, claim_id=claim_id, submission=submission, expected_revision=expected_revision, root_cause=(root_cause or "").strip() or None)
            successor = copy.deepcopy(envelope)
            successor["revision"] = int(envelope["revision"]) + 1
            successor["work_items"][work_id] = successor_work
            return successor, self.project.submit_projection_updates(work_id, successor_work)

        envelope, recovered = self.state.mutate(projection, transition)
        work = envelope["work_items"][work_id]
        return success("review.corrected-descendant-submitted", f"Recorded corrected descendant for {work_id}; fresh verification is required.", revision=envelope["revision"], data={"work_id": work_id, "candidate": work["submission"]["candidate"], "parent_candidate": work["submission"]["parent_candidate"], "fresh_verification_required": True, "transaction_recovered": recovered})
