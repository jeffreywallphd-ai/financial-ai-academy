"""Project-neutral, read-only operator projection over adapter snapshots."""

from __future__ import annotations

from typing import Any, Protocol

from contracts import ControlError, success


class OperatorSnapshotPort(Protocol):
    def snapshots(self) -> list[dict[str, Any]]: ...


def next_action(item: dict[str, Any]) -> str:
    public = str(item.get("public_status", ""))
    operational = item.get("operational_state")
    latest_review = item.get("latest_review_status")
    blockers = item.get("open_blocking_finding_ids", [])
    if public == "complete":
        return "none"
    if blockers or latest_review in {"changes-requested", "rejected"}:
        return "correct named findings and submit a strict descendant"
    if public == "verifying" or operational == "submitted":
        if latest_review == "accepted":
            return "run deterministic completion verification"
        return "record one independent technical review"
    if public == "active" or operational == "active":
        return "continue claimed work or recover only after lease expiry"
    if public == "ready":
        return "claim the packet"
    return "inspect the public planning status"


def project_status(snapshots: list[dict[str, Any]], work_id: str | None = None) -> dict[str, Any]:
    selected = [item for item in snapshots if work_id is None or item.get("work_id") == work_id]
    if work_id is not None and not selected:
        raise ControlError(
            "operator.work-not-found",
            "The requested work item is not present in the project adapter.",
            {"work_id": work_id},
            ["Use a work ID reported by operator-status."],
        )
    projected: list[dict[str, Any]] = []
    for item in sorted(selected, key=lambda value: str(value.get("work_id", ""))):
        public = str(item.get("public_status", ""))
        operational = item.get("operational_state")
        diagnostics = list(item.get("diagnostics", []))
        if public == "complete" and operational not in {None, "complete"}:
            diagnostics.append("tracked terminal status supersedes stale optional local state")
        projected.append(
            {
                "work_id": str(item["work_id"]),
                "public_status": public,
                "operational_state": operational,
                "claim": item.get("claim_summary"),
                "submission_present": bool(item.get("submission_present")),
                "qualifying_receipt_count": int(item.get("qualifying_receipt_count", 0)),
                "review_round_count": int(item.get("review_round_count", 0)),
                "latest_review_status": item.get("latest_review_status"),
                "open_finding_ids": sorted(str(value) for value in item.get("open_finding_ids", [])),
                "open_blocking_finding_ids": sorted(str(value) for value in item.get("open_blocking_finding_ids", [])),
                "diagnostics": sorted(set(str(value) for value in diagnostics)),
                "next_action": next_action(item),
            }
        )
    return {
        "schema_version": "operator-status-v1",
        "work_items": projected,
        "summary": {
            "count": len(projected),
            "actionable": sum(item["next_action"] != "none" for item in projected),
            "diagnostic_count": sum(len(item["diagnostics"]) for item in projected),
        },
    }


class OperatorStatusService:
    def __init__(self, source: OperatorSnapshotPort) -> None:
        self.source = source

    def status(self, work_id: str | None = None) -> dict[str, Any]:
        projection = project_status(self.source.snapshots(), work_id)
        return success(
            "operator.status",
            f"Projected {projection['summary']['count']} work item(s) without mutation.",
            data={"projection": projection},
        )
