"""Ignored approval-ledger adapter for append-only technical review rounds."""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PLANNING_TOOLS = HERE.parent / "planning"
if str(PLANNING_TOOLS) not in sys.path:
    sys.path.insert(0, str(PLANNING_TOOLS))

from approval_store import load_store, save_store  # noqa: E402

from contracts import ControlError
from review import REVIEW_TYPE
from store import exclusive_lock


class FinancialAcademyReviewLedger:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.lock_path = self.root / ".local-codex/approvals/review.lock"

    def rounds(self, work_id: str) -> list[dict[str, Any]]:
        store, _ = load_store(self.root, required=True)
        return [copy.deepcopy(item) for item in store.get("reviews", []) if isinstance(item, dict) and item.get("subject") == work_id and item.get("review_type") == REVIEW_TYPE]

    def append(self, record: dict[str, Any]) -> None:
        with exclusive_lock(self.lock_path):
            store, path = load_store(self.root, required=True)
            rounds = [item for item in store.get("reviews", []) if isinstance(item, dict) and item.get("subject") == record["subject"] and item.get("review_type") == REVIEW_TYPE]
            expected_round = f"R{len(rounds) + 1:02d}"
            if record.get("round_id") != expected_round:
                raise ControlError("review.concurrent-round", "Review history advanced before this round could be appended.", {"expected_round": expected_round, "requested_round": record.get("round_id")}, ["Reload review status and retry against the latest candidate."])
            if any(item.get("candidate") == record.get("candidate") for item in rounds):
                raise ControlError("review.candidate-already-reviewed", "The exact candidate already has an immutable review round.", {"candidate": record.get("candidate")}, ["Submit a corrected strict descendant before another review."])
            store["reviews"].append(copy.deepcopy(record))
            save_store(path, store)
