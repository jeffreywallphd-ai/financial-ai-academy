"""Financial AI Academy adapters for start, correction, and maintenance."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PLANNING_TOOLS = HERE.parent / "planning"
if str(PLANNING_TOOLS) not in sys.path:
    sys.path.insert(0, str(PLANNING_TOOLS))

from planning_model import as_list, as_text, load_artifacts  # noqa: E402

from contracts import ControlError
from operations import CorrectionRouteService, MaintenanceService, PacketStartService, digest
from store import StateStore


def acceptance_section(path: Path) -> tuple[list[str], str]:
    text = path.read_text(encoding="utf-8")
    marker = "## Acceptance Scenarios\n"
    if marker not in text:
        return [], ""
    section = text.split(marker, 1)[1].split("\n## ", 1)[0].strip()
    rows = [line for line in section.splitlines() if line.startswith("|")]
    data_rows = rows[2:] if len(rows) >= 2 else []
    identifier = path.stem.split("-", 2)[:2]
    prefix = "-".join(identifier)
    return [f"{prefix}:A{index:03d}" for index, _ in enumerate(data_rows, start=1)], section


class FinancialAcademyOperationsAdapter:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def _by_id(self) -> dict[str, Any]:
        return {artifact.identifier: artifact for artifact in load_artifacts(self.root)}

    def start_context(self, work_id: str) -> dict[str, Any]:
        artifacts = self._by_id()
        packet = artifacts.get(work_id)
        if packet is None or packet.kind != "work-packet":
            raise ControlError("start.packet-missing", "Packet start requires an existing WRK artifact.", {"work_id": work_id}, ["Use an exact WRK ID from the planning register."])
        if packet.status != "active":
            raise ControlError("start.packet-not-active", "Packet start requires an already claimed active packet.", {"planning_status": packet.status}, ["Claim the ready packet, then record its start manifest."])
        claim_id = as_text(packet.metadata.get("claim_id"))
        if not claim_id:
            raise ControlError("start.claim-missing", "The active packet lacks a durable claim identifier.", {}, ["Use the governed claim command before packet start."])
        slice_id = as_text(packet.metadata.get("parent"))
        slice_artifact = artifacts.get(slice_id)
        if slice_artifact is None:
            raise ControlError("start.slice-missing", "The packet's parent slice is missing.", {"slice": slice_id}, ["Restore the parent slice before starting work."])
        packet_ids, packet_section = acceptance_section(packet.path)
        slice_ids, slice_section = acceptance_section(slice_artifact.path)
        acceptance_ids = slice_ids + packet_ids
        if not acceptance_ids:
            raise ControlError("start.acceptance-missing", "Packet start requires explicit slice or packet acceptance scenarios.", {}, ["Refine the bounded acceptance scenarios without adding an approval gate."])
        scopes = as_list(packet.metadata.get("write_scope")) + as_list(packet.metadata.get("generated_artifacts"))
        high_markers = (".github", "dev-tools/control-plane", "dev-tools/planning", "docs/planning/skills", "contracts")
        high_matches = sorted(scope for scope in scopes if scope.startswith(high_markers))
        risk = "high" if high_matches else ("medium" if any(not scope.startswith("docs/") for scope in scopes) else "low")
        reason = "shared control or contract boundary" if risk == "high" else ("bounded implementation boundary" if risk == "medium" else "documentation-only boundary")
        semantic_inputs = {
            "packet": work_id,
            "slice": slice_id,
            "depends_on": as_list(packet.metadata.get("depends_on")),
            "decision_gates": as_list(packet.metadata.get("decision_gates")),
            "acceptance_digest": digest([slice_section, packet_section]),
            "scope_digest": digest(sorted(scopes)),
        }
        return {
            "claim_id": claim_id,
            "canonical_input_digest": digest(semantic_inputs),
            "acceptance_ids": acceptance_ids,
            "acceptance_digest": digest([slice_section, packet_section]),
            "scope_digest": digest(sorted(scopes)),
            "risk": risk,
            "risk_reason": reason,
        }

    def correction_context(self, work_id: str) -> dict[str, Any]:
        packet = self._by_id().get(work_id)
        if packet is None or packet.kind != "work-packet":
            raise ControlError("correction.packet-missing", "Correction routing requires an existing completed WRK artifact.", {"work_id": work_id}, ["Use an exact completed WRK ID from the planning register."])
        if packet.status != "complete":
            raise ControlError("correction.not-complete", "The bounded correction route applies only to completed work.", {"planning_status": packet.status}, ["Use the current packet lifecycle for unfinished work."])
        return {"parent_slice": as_text(packet.metadata.get("parent")), "allowed_paths": as_list(packet.metadata.get("write_scope")) + as_list(packet.metadata.get("generated_artifacts"))}


def services(root: Path, project: Any) -> tuple[PacketStartService, CorrectionRouteService, MaintenanceService]:
    operations = FinancialAcademyOperationsAdapter(root)
    state = StateStore(root, project.projection)

    def validate_state() -> dict[str, Any]:
        envelope = state.load()
        return {"state_revision": int(envelope["revision"]), "work_item_count": len(envelope["work_items"])}

    def recover_transaction() -> dict[str, Any]:
        envelope, recovered = state.read()
        return {"transaction_recovered": recovered, "state_revision": int(envelope["revision"]), "work_item_count": len(envelope["work_items"])}

    def health() -> bool:
        try:
            state.load()
            return True
        except ControlError:
            return False

    maintenance = MaintenanceService(root, {"recover-interrupted-transaction": recover_transaction, "validate-local-state": validate_state}, health)
    return PacketStartService(root, operations), CorrectionRouteService(root, operations), maintenance
