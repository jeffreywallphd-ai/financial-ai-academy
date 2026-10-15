"""Financial AI Academy adapter for the reusable control-plane core."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PLANNING_TOOLS = HERE.parent / "planning"
if str(PLANNING_TOOLS) not in sys.path:
    sys.path.insert(0, str(PLANNING_TOOLS))

from approval_store import load_store  # noqa: E402
from cap_package import require_current_package  # noqa: E402
from planning_model import (  # noqa: E402
    as_list,
    as_text,
    frontmatter_from_path,
    load_artifacts,
    scopes_overlap,
    update_frontmatter,
)

from contracts import ControlError
from state import DEFAULT_LEASE_MINUTES, new_work, parse_timestamp, timestamp
from store import confined_path


class FrontmatterProjection:
    def __init__(self, root: Path, relative_path: str) -> None:
        self.root = root.resolve()
        self.path = confined_path(self.root, relative_path)
        if not self.path.is_file():
            raise ControlError(
                "projection.missing",
                "The tracked work-packet projection does not exist.",
                {"path": relative_path},
                ["Restore the packet artifact and planning register entry."],
            )

    @property
    def relative_path(self) -> str:
        return self.path.relative_to(self.root).as_posix()

    def content_sha256(self) -> str:
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def matches(self, updates: dict[str, Any]) -> bool:
        metadata = frontmatter_from_path(self.path)
        return all(metadata.get(key) == value for key, value in updates.items())

    def apply(self, updates: dict[str, Any], expected_sha256: str) -> None:
        actual = self.content_sha256()
        if actual != expected_sha256 and not self.matches(updates):
            raise ControlError(
                "transaction.projection-conflict",
                "The tracked packet changed during an interrupted transaction.",
                {"path": self.relative_path, "expected_sha256": expected_sha256, "actual_sha256": actual},
                ["Preserve both changes and use bounded control maintenance to reconcile them."],
            )
        if not self.matches(updates):
            update_frontmatter(self.path, updates)


class FinancialAcademyAdapter:
    """Maps CAP/SLI/WRK artifacts onto reusable work-item primitives."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def _artifacts(self) -> dict[str, Any]:
        return {artifact.identifier: artifact for artifact in load_artifacts(self.root)}

    def _packet(self, work_id: str) -> Any:
        packet = self._artifacts().get(work_id)
        if packet is None or packet.kind != "work-packet":
            raise ControlError(
                "planning.packet-missing",
                "The requested WRK work packet does not exist.",
                {"work_id": work_id},
                ["Use an exact WRK-* identifier listed in docs/planning/register.md."],
            )
        return packet

    def projection(self, work_id_or_path: str) -> FrontmatterProjection:
        if work_id_or_path.startswith("WRK-"):
            packet = self._packet(work_id_or_path)
            relative = packet.path.relative_to(self.root).as_posix()
        else:
            relative = work_id_or_path
        return FrontmatterProjection(self.root, relative)

    def require_delivery_authority(self, work_id: str) -> dict[str, Any]:
        artifacts = self._artifacts()
        packet = artifacts.get(work_id)
        if packet is None or packet.kind != "work-packet":
            return self._packet(work_id)  # raises stable refusal
        capability_id = as_text(packet.metadata.get("capability"))
        capability = artifacts.get(capability_id)
        if capability is None or capability.kind != "capability":
            raise ControlError(
                "authority.capability-missing",
                "The packet does not reference an existing capability.",
                {"capability": capability_id},
                ["Repair the packet capability reference before claiming work."],
            )
        try:
            store, _ = load_store(self.root, required=True)
            require_current_package(store, capability)
        except Exception as error:
            raise ControlError(
                "authority.cap-package-missing-or-stale",
                "The parent CAP package lacks a current local approval binding.",
                {"capability": capability_id},
                ["Review the current complete CAP package and record one CAP-level decision."],
            ) from error
        slice_id = as_text(packet.metadata.get("parent"))
        if slice_id not in as_list(capability.metadata.get("slice_ids")):
            raise ControlError(
                "authority.slice-outside-package",
                "The packet's parent slice is outside the approved CAP manifest.",
                {"capability": capability_id, "slice": slice_id},
                ["Return the CAP package to shaping if the slice manifest must change."],
            )
        if as_list(packet.metadata.get("decision_gates")):
            raise ControlError(
                "authority.decision-blocked",
                "The packet still names unresolved durable decision gates.",
                {"decision_gates": as_list(packet.metadata.get("decision_gates"))},
                ["Resolve and promote the named durable decisions first."],
            )
        for dependency in as_list(packet.metadata.get("depends_on")):
            required = artifacts.get(dependency)
            if required is None or required.status != "complete":
                raise ControlError(
                    "planning.dependency-incomplete",
                    "A work-packet dependency is not complete.",
                    {"dependency": dependency, "status": required.status if required else "missing"},
                    ["Complete and verify the dependency before claiming this packet."],
                )
        scopes = as_list(packet.metadata.get("write_scope"))
        generated = as_list(packet.metadata.get("generated_artifacts"))
        for other in artifacts.values():
            if other.identifier == work_id or other.kind != "work-packet" or other.status != "active":
                continue
            other_scopes = as_list(other.metadata.get("write_scope"))
            other_generated = as_list(other.metadata.get("generated_artifacts"))
            if any(
                (
                    scopes_overlap(scopes, other_scopes),
                    scopes_overlap(scopes, other_generated),
                    scopes_overlap(generated, other_scopes),
                    scopes_overlap(generated, other_generated),
                )
            ):
                raise ControlError(
                    "planning.scope-overlap",
                    "The packet scope overlaps another active work packet.",
                    {"active_packet": other.identifier},
                    ["Finish or safely release the overlapping packet before claiming this one."],
                )
        slice_artifact = artifacts.get(slice_id)
        return {
            "packet": packet,
            "capability": capability,
            "slice": slice_artifact,
            "allowed_paths": as_list(packet.metadata.get("write_scope"))
            + as_list(packet.metadata.get("generated_artifacts")),
            "canonical_inputs": [
                packet.path.relative_to(self.root).as_posix(),
                capability.path.relative_to(self.root).as_posix(),
                slice_artifact.path.relative_to(self.root).as_posix() if slice_artifact else "",
                "AGENTS.md",
                "docs/README.md",
            ],
            "approval_stages_checked": ["capability"],
        }

    def initial_work_state(self, work_id: str) -> dict[str, Any]:
        packet = self._packet(work_id)
        status = packet.status
        if status == "ready":
            return new_work(work_id)
        if status not in {"active", "verifying", "complete"}:
            raise ControlError(
                "planning.packet-not-runnable",
                "The packet is not in a runnable lifecycle state.",
                {"planning_status": status},
                ["Refine the packet to ready or inspect its completion evidence."],
            )
        claim_id = as_text(packet.metadata.get("claim_id"))
        owner = as_text(packet.metadata.get("claimed_by"))
        claimed_at = as_text(packet.metadata.get("claimed_at"))
        if not all((claim_id, owner, claimed_at)):
            raise ControlError(
                "planning.claim-incomplete",
                "The public packet projection has incomplete historical claim metadata.",
                {"planning_status": status},
                ["Use bounded control maintenance to reconcile the public projection."],
            )
        at = parse_timestamp(claimed_at)
        state = "submitted" if status in {"verifying", "complete"} else "active"
        work = new_work(work_id)
        work.update(
            {
                "state": state,
                "claim": {
                    "claim_id": claim_id,
                    "owner": owner,
                    "base_revision": as_text(packet.metadata.get("base_revision")),
                    "branch": "legacy-unrecorded",
                    "claimed_at": claimed_at,
                    "leased_until": timestamp(at + timedelta(minutes=DEFAULT_LEASE_MINUTES)),
                    "compatibility_projection": True,
                },
            }
        )
        return work

    @staticmethod
    def claim_projection_updates(work_id: str, work: dict[str, Any]) -> dict[str, Any]:
        claim = work["claim"]
        return {
            "planning_status": "active",
            "owner": claim["owner"],
            "updated": claim["claimed_at"].split("T", 1)[0],
            "base_revision": claim["base_revision"],
            "claim_id": claim["claim_id"],
            "claimed_by": claim["owner"],
            "claimed_at": claim["claimed_at"],
        }

    @staticmethod
    def submit_projection_updates(work_id: str, work: dict[str, Any]) -> dict[str, Any]:
        return {
            "planning_status": "verifying",
            "updated": str(work["submission"]["recorded_at"]).split("T", 1)[0],
        }

    @staticmethod
    def release_projection_updates(work_id: str, work: dict[str, Any]) -> dict[str, Any]:
        return {"planning_status": "ready", "owner": "unassigned"}


def metadata_json(value: object) -> str:
    """Stable debug helper retained for adapter contract tests."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))
