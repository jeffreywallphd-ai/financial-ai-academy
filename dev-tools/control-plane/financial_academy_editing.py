"""Financial AI Academy authorization adapter for generic file-edit leases."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PLANNING_TOOLS = HERE.parent / "planning"
if str(PLANNING_TOOLS) not in sys.path:
    sys.path.insert(0, str(PLANNING_TOOLS))

from planning_model import as_list, as_text, load_artifacts, normalize_repo_path  # noqa: E402

from contracts import ControlError
from file_leases import FileLeaseStore, canonical_files
from financial_academy import FinancialAcademyAdapter


def _allowed(path: str, scopes: list[str]) -> bool:
    candidate = normalize_repo_path(path).casefold()
    for value in scopes:
        scope = normalize_repo_path(value).casefold()
        if scope and (candidate == scope or candidate.startswith(scope + "/")):
            return True
    return False


class FinancialAcademyEditingService:
    """Bind logical CAP/SLI/WRK lanes to one active WRK scope."""

    def __init__(self, root: Path, store: FileLeaseStore | None = None) -> None:
        self.root = root.resolve()
        self.project = FinancialAcademyAdapter(self.root)
        self.store = store or FileLeaseStore(self.root)

    def _authorize(self, *, unit_id: str, work_id: str, owner: str, claim_id: str, paths: list[str]) -> list[str]:
        artifacts = {item.identifier: item for item in load_artifacts(self.root)}
        packet = artifacts.get(work_id)
        if packet is None or packet.kind != "work-packet":
            raise ControlError("edit.work-missing", "File edits require an exact WRK packet.", {"work_id": work_id}, ["Use an active WRK ID from the planning register."])
        self.project.require_delivery_authority(work_id)
        if packet.status != "active" or as_text(packet.metadata.get("claimed_by")) != owner or as_text(packet.metadata.get("claim_id")) != claim_id:
            raise ControlError("edit.work-claim-mismatch", "The WRK packet is not actively claimed by this owner and claim.", {"work_id": work_id, "planning_status": packet.status}, ["Claim the packet or use its exact active owner and claim ID."])
        slice_id = as_text(packet.metadata.get("parent"))
        slice_artifact = artifacts.get(slice_id)
        cap_id = as_text(packet.metadata.get("capability"))
        if unit_id not in {work_id, slice_id, cap_id}:
            raise ControlError("edit.unit-not-ancestor", "The logical coordination lane is not this packet or one of its ancestors.", {"unit_id": unit_id, "work_id": work_id}, ["Use the packet, its parent SLI, or its parent CAP as the lane ID."])
        unit = artifacts.get(unit_id)
        if unit is None or (unit_id == slice_id and (slice_artifact is None or slice_artifact.kind != "vertical-slice")):
            raise ControlError("edit.unit-missing", "The logical coordination lane artifact is missing.", {"unit_id": unit_id}, ["Restore the governed CAP, SLI, or WRK artifact."])
        displays = [display for display, _key in canonical_files(self.root, paths)]
        scopes = as_list(packet.metadata.get("write_scope")) + as_list(packet.metadata.get("generated_artifacts"))
        outside = [path for path in displays if not _allowed(path, scopes)]
        if outside:
            raise ControlError("edit.path-outside-work-scope", "A requested file is outside the active WRK scope; no lease was changed.", {"paths": outside, "work_id": work_id}, ["Refine the packet scope if conforming, or choose only declared files."])
        return displays

    def announce(self, **values: Any) -> dict[str, Any]:
        paths = self._authorize(**{key: values[key] for key in ("unit_id", "work_id", "owner", "claim_id", "paths")})
        values["paths"] = paths
        return self.store.announce(**values)

    def acquire(self, **values: Any) -> dict[str, Any]:
        paths = self._authorize(**{key: values[key] for key in ("unit_id", "work_id", "owner", "claim_id", "paths")})
        values["paths"] = paths
        return self.store.acquire(**values)

    def recover(self, **values: Any) -> dict[str, Any]:
        paths = self._authorize(**{key: values[key] for key in ("unit_id", "work_id", "owner", "claim_id", "paths")})
        values["paths"] = paths
        values["recovery"] = True
        return self.store.acquire(**values)

    def renew(self, **values: Any) -> dict[str, Any]:
        lease_id = str(values["lease_id"])
        status = self.store.status()
        lease = next((item for item in status["data"]["leases"] if item.get("lease_id") == lease_id), None)
        if lease is None:
            raise ControlError("edit.lease-missing", "The file-edit lease does not exist.", {"lease_id": lease_id}, ["Read edit-status and use an active lease ID."])
        if lease.get("owner") != values["owner"] or lease.get("claim_id") != values["claim_id"]:
            raise ControlError("edit.owner-mismatch", "The lease belongs to a different owner or claim.", {"lease_id": lease_id, "leased_until": lease.get("leased_until")}, ["Use the recorded owner/claim or wait for release/expiry."])
        self._authorize(
            unit_id=str(lease["unit_id"]),
            work_id=str(lease["work_id"]),
            owner=str(values["owner"]),
            claim_id=str(values["claim_id"]),
            paths=[str(path) for path in lease.get("paths", [])],
        )
        return self.store.renew(**values)

    def release(self, **values: Any) -> dict[str, Any]:
        return self.store.release(**values)

    def status(self, **values: Any) -> dict[str, Any]:
        return self.store.status(**values)
