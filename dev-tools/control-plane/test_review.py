#!/usr/bin/env python3
"""Independent-review, finding, closure, lineage, and anti-rigidity tests."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PLANNING = HERE.parent / "planning"
for path in (HERE, PLANNING):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from approval_store import empty_store, load_store, save_store, store_path  # noqa: E402
from contracts import ControlError  # noqa: E402
from control_plane import load_local_review_request  # noqa: E402
from financial_academy_review_ledger import FinancialAcademyReviewLedger  # noqa: E402
from review import REVIEW_TYPE, ReviewService, open_findings  # noqa: E402
from store import StateStore, atomic_write, canonical_bytes  # noqa: E402
from verification import CheckCatalog, CheckDefinition, ReceiptStore, select_checks  # noqa: E402


class JsonProjection:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = root / "work.json"
        if not self.path.exists():
            self.path.write_text('{"status":"verifying"}\n', encoding="utf-8")

    @property
    def relative_path(self) -> str:
        return "work.json"

    def content_sha256(self) -> str:
        import hashlib

        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def matches(self, updates: dict[str, Any]) -> bool:
        current = json.loads(self.path.read_text(encoding="utf-8"))
        return all(current.get(key) == value for key, value in updates.items())

    def apply(self, updates: dict[str, Any], expected_sha256: str) -> None:
        current = json.loads(self.path.read_text(encoding="utf-8"))
        current.update(updates)
        self.path.write_bytes(canonical_bytes(current))


class FixtureProject:
    def __init__(self, root: Path) -> None:
        self.public = JsonProjection(root)

    def projection(self, work_id: str) -> JsonProjection:
        return self.public

    @staticmethod
    def require_delivery_authority(work_id: str) -> dict[str, Any]:
        return {"allowed_paths": ["docs"], "canonical_inputs": [], "approval_stages_checked": ["fixture"]}

    @staticmethod
    def submit_projection_updates(work_id: str, work: dict[str, Any]) -> dict[str, Any]:
        return {"status": "verifying"}


class FixtureCandidate:
    def __init__(self) -> None:
        self.next_candidate = "b" * 40
        self.descendant = True

    @staticmethod
    def current_identity() -> dict[str, str]:
        return {"repository": "fixture", "branch": "codex/fixture", "head": "a" * 40}

    @staticmethod
    def stable_identity(candidate: str) -> dict[str, str]:
        return {"repository": "fixture", "branch": "codex/fixture", "head": candidate, "candidate": candidate}

    def is_strict_descendant(self, ancestor: str, descendant: str) -> bool:
        return self.descendant and ancestor != descendant

    def submission(self, **kwargs: Any) -> dict[str, Any]:
        return {"candidate": self.next_candidate, "changed_paths": ["docs/README.md"], "recorded_at": "2026-10-15T12:10:00Z", "base_revision": kwargs["base_revision"]}


class MemoryLedger:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def rounds(self, work_id: str) -> list[dict[str, Any]]:
        return [copy.deepcopy(item) for item in self.items if item["subject"] == work_id]

    def append(self, record: dict[str, Any]) -> None:
        self.items.append(copy.deepcopy(record))


def catalog() -> CheckCatalog:
    return CheckCatalog("review-fixture-v1", (CheckDefinition("docs:fixture", (sys.executable, "-c", "pass"), ("docs/**",), "low", 10),))


class ReviewServiceTests(unittest.TestCase):
    def prepare(self, root: Path) -> tuple[ReviewService, StateStore, MemoryLedger, FixtureCandidate, ReceiptStore]:
        project = FixtureProject(root)
        state = StateStore(root, project.projection)
        envelope = state.empty()
        envelope["revision"] = 1
        envelope["work_items"]["WORK-1"] = {
            "work_id": "WORK-1",
            "revision": 1,
            "state": "submitted",
            "claim": {"owner": "owner", "claim_id": "claim-1", "base_revision": "0" * 40},
            "submission": {"candidate": "a" * 40, "changed_paths": ["docs/README.md"], "recorded_at": "2026-10-15T12:00:00Z"},
            "history": [],
        }
        atomic_write(state.state_path, canonical_bytes(envelope))
        ledger = MemoryLedger()
        candidate = FixtureCandidate()
        receipts = ReceiptStore(root)
        service = ReviewService(root, project, state, candidate, catalog(), ledger, receipts)
        return service, state, ledger, candidate, receipts

    def receipt(self, receipts: ReceiptStore, candidate: str) -> Path:
        plan = select_checks(catalog(), candidate, ["docs/README.md"])
        return receipts.append(
            "WORK-1",
            {
                "schema_version": "verification-receipt-v1",
                "candidate": candidate,
                "plan": plan,
                "attempts": [{"check_id": "docs:fixture", "exit_code": 0, "timed_out": False}],
                "candidate_stability": {"post_run_stable": True, "errors": []},
                "recorded_at": "2026-10-15T12:05:00Z",
            },
        )

    @staticmethod
    def blocking_finding(title: str = "Invariant violation") -> list[dict[str, Any]]:
        return [{"severity": "high", "blocking": True, "title": title, "criterion": "candidate preserves invariant", "evidence": ["synthetic reproduction"]}]

    def test_clean_independent_candidate_needs_one_review_round_only(self) -> None:
        with tempfile.TemporaryDirectory(prefix="review-clean-") as directory:
            service, _state, ledger, _candidate, receipts = self.prepare(Path(directory))
            result = service.record("WORK-1", reviewer_label="independent", status="accepted", receipt_path=self.receipt(receipts, "a" * 40), findings=[], closures=[])
            self.assertEqual("review.recorded", result["code"])
            self.assertEqual("accepted", result["data"]["status"])
            self.assertEqual(1, len(ledger.items))
            self.assertEqual([], result["data"]["open_finding_ids"])

    def test_cleanup_finding_cannot_force_adverse_review(self) -> None:
        with tempfile.TemporaryDirectory(prefix="review-cleanup-disposition-") as directory:
            service, _state, ledger, _candidate, receipts = self.prepare(Path(directory))
            receipt = self.receipt(receipts, "a" * 40)
            cleanup = [{"severity": "low", "finding_class": "cleanup", "blocking": False, "title": "Trailing blank line", "criterion": "formatting is tidy", "evidence": ["one extra blank line"]}]
            with self.assertRaises(ControlError) as adverse:
                service.record("WORK-1", reviewer_label="independent", status="changes-requested", receipt_path=receipt, findings=cleanup, closures=[])
            self.assertEqual("review.adverse-without-blocking-finding", adverse.exception.code)
            accepted = service.record("WORK-1", reviewer_label="independent", status="accepted", receipt_path=receipt, findings=cleanup, closures=[])
            self.assertEqual("accepted", accepted["data"]["status"])
            self.assertEqual(1, len(ledger.items))

    def test_cleanup_descendant_inherits_review_after_fresh_verification(self) -> None:
        with tempfile.TemporaryDirectory(prefix="review-cleanup-inheritance-") as directory:
            root = Path(directory)
            service, state, ledger, _candidate, receipts = self.prepare(root)
            cleanup = [{"severity": "low", "finding_class": "cleanup", "blocking": False, "title": "Cosmetic spacing", "criterion": "presentation is tidy", "evidence": ["spacing does not affect use"]}]
            service.record("WORK-1", reviewer_label="independent", status="accepted", receipt_path=self.receipt(receipts, "a" * 40), findings=cleanup, closures=[])
            resubmitted = service.resubmit("WORK-1", owner="owner", claim_id="claim-1", cleanup_only=True)
            self.assertEqual("review.cleanup-descendant-submitted", resubmitted["code"])
            self.assertTrue(resubmitted["data"]["review_inherited_after_verification"])
            self.assertEqual("inherited-pending-verification", service.status("WORK-1")["data"]["review_binding"])
            self.receipt(receipts, "b" * 40)
            status = service.status("WORK-1")["data"]
            self.assertEqual("inherited", status["review_binding"])
            self.assertEqual("review complete", status["next_action"])
            self.assertEqual([], status["open_finding_ids"])
            self.assertEqual(1, len(ledger.items))
            self.assertEqual("a" * 40, state.load()["work_items"]["WORK-1"]["submission"]["review_inheritance"]["basis_candidate"])

    def test_cleanup_route_refuses_blocking_or_adverse_findings(self) -> None:
        with tempfile.TemporaryDirectory(prefix="review-cleanup-denial-") as directory:
            service, _state, _ledger, _candidate, receipts = self.prepare(Path(directory))
            with self.assertRaises(ControlError) as invalid_cleanup:
                service.record("WORK-1", reviewer_label="independent", status="accepted", receipt_path=self.receipt(receipts, "a" * 40), findings=[{"severity": "high", "finding_class": "cleanup", "blocking": True, "title": "Functional failure", "criterion": "feature works", "evidence": ["broken action"]}], closures=[])
            self.assertEqual("review.cleanup-cannot-block", invalid_cleanup.exception.code)

        with tempfile.TemporaryDirectory(prefix="review-cleanup-adverse-") as directory:
            service, _state, _ledger, _candidate, receipts = self.prepare(Path(directory))
            service.record("WORK-1", reviewer_label="independent", status="changes-requested", receipt_path=self.receipt(receipts, "a" * 40), findings=self.blocking_finding(), closures=[])
            with self.assertRaises(ControlError) as refused:
                service.resubmit("WORK-1", owner="owner", claim_id="claim-1", cleanup_only=True)
            self.assertEqual("review.cleanup-resubmit-not-authorized", refused.exception.code)

    def test_self_review_and_duplicate_candidate_are_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="review-independent-") as directory:
            service, _state, _ledger, _candidate, receipts = self.prepare(Path(directory))
            receipt = self.receipt(receipts, "a" * 40)
            with self.assertRaises(ControlError) as self_review:
                service.record("WORK-1", reviewer_label="owner", status="accepted", receipt_path=receipt, findings=[], closures=[])
            self.assertEqual("review.not-independent", self_review.exception.code)
            service.record("WORK-1", reviewer_label="independent", status="accepted", receipt_path=receipt, findings=[], closures=[])
            with self.assertRaises(ControlError) as duplicate:
                service.record("WORK-1", reviewer_label="another", status="accepted", receipt_path=receipt, findings=[], closures=[])
            self.assertEqual("review.candidate-already-reviewed", duplicate.exception.code)

    def test_blocking_finding_requires_strict_descendant_fresh_receipt_and_closure(self) -> None:
        with tempfile.TemporaryDirectory(prefix="review-correction-") as directory:
            root = Path(directory)
            service, state, ledger, candidate, receipts = self.prepare(root)
            first_receipt = self.receipt(receipts, "a" * 40)
            first = service.record("WORK-1", reviewer_label="reviewer-a", status="changes-requested", receipt_path=first_receipt, findings=self.blocking_finding(), closures=[])
            first_record = copy.deepcopy(ledger.items[0])
            with self.assertRaises(ControlError) as stale:
                service.record("WORK-1", reviewer_label="reviewer-b", status="accepted", receipt_path=first_receipt, findings=[], closures=[])
            self.assertEqual("review.candidate-already-reviewed", stale.exception.code)
            candidate.descendant = False
            with self.assertRaises(ControlError) as forked:
                service.resubmit("WORK-1", owner="owner", claim_id="claim-1")
            self.assertEqual("review.not-strict-descendant", forked.exception.code)
            candidate.descendant = True
            resubmitted = service.resubmit("WORK-1", owner="owner", claim_id="claim-1")
            self.assertTrue(resubmitted["data"]["fresh_verification_required"])
            with self.assertRaises(ControlError) as old_receipt:
                service.record("WORK-1", reviewer_label="reviewer-b", status="accepted", receipt_path=first_receipt, findings=[], closures=[{"finding_id": first["data"]["open_finding_ids"][0], "evidence": ["fixed"]}])
            self.assertEqual("review.receipt-invalid", old_receipt.exception.code)
            second_receipt = self.receipt(receipts, "b" * 40)
            with self.assertRaises(ControlError) as still_open:
                service.record("WORK-1", reviewer_label="reviewer-b", status="accepted", receipt_path=second_receipt, findings=[], closures=[])
            self.assertEqual("review.blocking-findings-open", still_open.exception.code)
            accepted = service.record("WORK-1", reviewer_label="reviewer-b", status="accepted", receipt_path=second_receipt, findings=[], closures=[{"finding_id": "R01-F001", "evidence": ["fresh regression proof"]}])
            self.assertEqual([], accepted["data"]["open_blocking_finding_ids"])
            self.assertEqual(first_record, ledger.items[0])
            self.assertEqual({}, open_findings(ledger.items))
            self.assertEqual("b" * 40, state.load()["work_items"]["WORK-1"]["submission"]["candidate"])

    def test_third_candidate_requires_root_cause_after_two_adverse_rounds(self) -> None:
        with tempfile.TemporaryDirectory(prefix="review-root-cause-") as directory:
            root = Path(directory)
            service, _state, _ledger, candidate, receipts = self.prepare(root)
            service.record("WORK-1", reviewer_label="reviewer-a", status="changes-requested", receipt_path=self.receipt(receipts, "a" * 40), findings=self.blocking_finding("first"), closures=[])
            service.resubmit("WORK-1", owner="owner", claim_id="claim-1")
            service.record("WORK-1", reviewer_label="reviewer-b", status="changes-requested", receipt_path=self.receipt(receipts, "b" * 40), findings=self.blocking_finding("second"), closures=[])
            candidate.next_candidate = "c" * 40
            with self.assertRaises(ControlError) as required:
                service.resubmit("WORK-1", owner="owner", claim_id="claim-1")
            self.assertEqual("review.root-cause-required", required.exception.code)
            result = service.resubmit("WORK-1", owner="owner", claim_id="claim-1", root_cause="shared state assumption")
            self.assertEqual("c" * 40, result["data"]["candidate"])


class LedgerAdapterTests(unittest.TestCase):
    def test_review_rounds_append_only_without_approval_records(self) -> None:
        with tempfile.TemporaryDirectory(prefix="review-ledger-") as directory:
            root = Path(directory)
            save_store(store_path(root), empty_store())
            ledger = FinancialAcademyReviewLedger(root)
            first = {"subject": "WRK-0001", "review_type": REVIEW_TYPE, "reviewer_label": "independent-a", "status": "changes-requested", "recorded_at": "2026-10-15T12:00:00Z", "round_id": "R01", "candidate": "a" * 40, "verification_receipt_digest": "sha256:" + "1" * 64, "findings": [], "closures": [], "notes": ""}
            ledger.append(first)
            frozen = copy.deepcopy(ledger.rounds("WRK-0001")[0])
            second = {**first, "reviewer_label": "independent-b", "status": "accepted", "recorded_at": "2026-10-15T12:01:00Z", "round_id": "R02", "candidate": "b" * 40}
            ledger.append(second)
            store, _ = load_store(root, required=True)
            self.assertEqual([], store["records"])
            self.assertEqual(frozen, ledger.rounds("WRK-0001")[0])
            self.assertEqual(2, len(store["reviews"]))
            with self.assertRaises(ControlError) as stale:
                ledger.append({**second, "round_id": "R02", "candidate": "c" * 40})
            self.assertEqual("review.concurrent-round", stale.exception.code)

    def test_review_request_is_confined_to_ignored_local_storage(self) -> None:
        with tempfile.TemporaryDirectory(prefix="review-request-") as directory:
            root = Path(directory)
            local = root / ".local-codex/request.json"
            local.parent.mkdir(parents=True)
            local.write_text('{"status":"accepted"}', encoding="utf-8")
            self.assertEqual("accepted", load_local_review_request(root, Path(".local-codex/request.json"))["status"])
            with self.assertRaises(ControlError) as tracked:
                load_local_review_request(root, Path("docs/review.json"))
            self.assertEqual("review.request-not-local", tracked.exception.code)


if __name__ == "__main__":
    unittest.main()
