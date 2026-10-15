"""Financial AI Academy adapter for the reusable operator projection."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PLANNING_TOOLS = HERE.parent / "planning"
if str(PLANNING_TOOLS) not in sys.path:
    sys.path.insert(0, str(PLANNING_TOOLS))

from approval_store import load_store, store_path  # noqa: E402
from planning_model import load_artifacts  # noqa: E402

from review import open_findings
from store import StateStore


class FinancialAcademyStatusAdapter:
    def __init__(self, root: Path, project: Any) -> None:
        self.root = root.resolve()
        self.project = project

    def _state(self) -> tuple[dict[str, Any], list[str]]:
        state = StateStore(self.root, self.project.projection)
        if not state.state_path.is_file():
            return state.empty(), []
        try:
            return state.load(), []
        except Exception:
            return state.empty(), ["optional local lifecycle state is unreadable"]

    def _reviews(self) -> list[dict[str, Any]]:
        if not store_path(self.root).is_file():
            return []
        try:
            ledger, _ = load_store(self.root, required=True)
            return [item for item in ledger.get("reviews", []) if isinstance(item, dict)]
        except Exception:
            return []

    def snapshots(self) -> list[dict[str, Any]]:
        envelope, state_diagnostics = self._state()
        reviews = self._reviews()
        receipt_root = self.root / ".local-codex/control-plane/receipts"
        snapshots: list[dict[str, Any]] = []
        for artifact in load_artifacts(self.root):
            if artifact.kind != "work-packet":
                continue
            work = envelope.get("work_items", {}).get(artifact.identifier, {})
            rounds = [item for item in reviews if item.get("subject") == artifact.identifier]
            opened = open_findings(rounds)
            claim = work.get("claim") if isinstance(work, dict) else None
            claim_summary = None
            if isinstance(claim, dict):
                claim_summary = {
                    "present": True,
                    "leased_until": claim.get("leased_until"),
                    "compatibility_projection": bool(claim.get("compatibility_projection")),
                }
            elif artifact.status == "active":
                claim_summary = {
                    "present": bool(artifact.metadata.get("claim_id")),
                    "leased_until": None,
                    "compatibility_projection": True,
                }
            receipts = list((receipt_root / artifact.identifier).glob("**/receipt-*.json")) if (receipt_root / artifact.identifier).is_dir() else []
            qualifying = 0
            for path in receipts:
                try:
                    import json

                    value = json.loads(path.read_text(encoding="utf-8"))
                    qualifying += bool(value.get("qualification", {}).get("qualifying"))
                except (OSError, ValueError, TypeError):
                    continue
            snapshots.append(
                {
                    "work_id": artifact.identifier,
                    "public_status": artifact.status,
                    "operational_state": work.get("state") if isinstance(work, dict) and work else None,
                    "claim_summary": claim_summary,
                    "submission_present": isinstance(work, dict) and isinstance(work.get("submission"), dict),
                    "qualifying_receipt_count": qualifying,
                    "review_round_count": len(rounds),
                    "latest_review_status": rounds[-1].get("status") if rounds else None,
                    "open_finding_ids": sorted(opened),
                    "open_blocking_finding_ids": sorted(identifier for identifier, item in opened.items() if item.get("blocking")),
                    "diagnostics": state_diagnostics,
                }
            )
        return snapshots
