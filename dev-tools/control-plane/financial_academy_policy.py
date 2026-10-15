"""Financial AI Academy facts and rules for the reusable policy core."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PLANNING_TOOLS = HERE.parent / "planning"
if str(PLANNING_TOOLS) not in sys.path:
    sys.path.insert(0, str(PLANNING_TOOLS))

from approval_store import load_store, store_path  # noqa: E402
from planning_model import as_list, as_text, load_artifacts, scopes_overlap  # noqa: E402

from policy import Fact, PolicyService, Rule
from store import StateStore


RULES = (
    Rule("control.active-claims-complete", "error", "active_claims_complete", "Repair the one active packet's incomplete public claim fields."),
    Rule("control.active-scopes-do-not-overlap", "error", "active_scopes_disjoint", "Finish or release the specifically overlapping active packet."),
    Rule("control.local-authority-readable", "error", "local_authority_readable", "Repair or re-establish the ignored local authority ledger."),
    Rule("control.local-state-readable", "error", "local_state_readable", "Run bounded maintenance on the preserved local state file."),
    Rule("control.register-covers-artifacts", "error", "register_covers_artifacts", "Add only the missing planning artifact row to the register."),
)


class FinancialAcademyPolicyFacts:
    def __init__(self, root: Path, project: Any) -> None:
        self.root = root.resolve()
        self.project = project

    def __call__(self, profile: str) -> dict[str, Fact]:
        artifacts = load_artifacts(self.root)
        active = [item for item in artifacts if item.kind == "work-packet" and item.status == "active"]
        claims_complete = all(
            all(as_text(item.metadata.get(key)) for key in ("claim_id", "claimed_by", "claimed_at", "base_revision"))
            for item in active
        )
        overlap = False
        for index, left in enumerate(active):
            left_scope = as_list(left.metadata.get("write_scope")) + as_list(left.metadata.get("generated_artifacts"))
            for right in active[index + 1 :]:
                right_scope = as_list(right.metadata.get("write_scope")) + as_list(right.metadata.get("generated_artifacts"))
                overlap = overlap or scopes_overlap(left_scope, right_scope)
        register = (self.root / "docs/planning/register.md").read_text(encoding="utf-8")
        covered = all(f"| {item.identifier} |" in register for item in artifacts)
        facts = {
            "active_claims_complete": Fact(True, claims_complete, len(active)),
            "active_scopes_disjoint": Fact(True, not overlap, len(active)),
            "register_covers_artifacts": Fact(True, covered, len(artifacts)),
        }
        if profile == "ci":
            facts["local_authority_readable"] = Fact(False, reason="ignored local authority is intentionally unavailable in CI")
            facts["local_state_readable"] = Fact(False, reason="ignored local state is intentionally unavailable in CI")
            return facts
        ledger = store_path(self.root)
        if ledger.is_file():
            try:
                load_store(self.root, required=True)
                facts["local_authority_readable"] = Fact(True, True, 1)
            except Exception:
                facts["local_authority_readable"] = Fact(True, False, 1)
        else:
            facts["local_authority_readable"] = Fact(False, reason="local authority ledger is not installed")
        state = StateStore(self.root, self.project.projection)
        if state.state_path.is_file():
            try:
                state.load()
                facts["local_state_readable"] = Fact(True, True, 1)
            except Exception:
                facts["local_state_readable"] = Fact(True, False, 1)
        else:
            facts["local_state_readable"] = Fact(False, reason="local lifecycle state has not been created")
        return facts


def git_revision(root: Path) -> str | None:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return completed.stdout.strip() if completed.returncode == 0 else None


def service(root: Path, project: Any) -> PolicyService:
    return PolicyService(RULES, FinancialAcademyPolicyFacts(root, project), lambda: git_revision(root))
