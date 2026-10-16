"""Reusable affected-check planning and exact-candidate verification receipts."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any, Iterable

from contracts import ControlError, success
from capabilities import CapabilityGrant
from ports import CandidateAdapter, ProjectAdapter
from provenance import digest as provenance_digest, envelope as provenance_envelope
from store import StateStore, atomic_write, canonical_bytes, confined_path


RISK_ORDER = {"low": 0, "medium": 1, "high": 2}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
BASE_REVISION_ARGUMENT = "{base_revision}"
EXACT_REVISION = re.compile(r"^[0-9a-f]{40,64}$")


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class CheckDefinition:
    check_id: str
    argv: tuple[str, ...]
    path_patterns: tuple[str, ...]
    risk: str
    order: int
    timeout_seconds: int = 300
    description: str = ""

    def __post_init__(self) -> None:
        if not SAFE_ID.match(self.check_id):
            raise ValueError(f"unsafe check id: {self.check_id}")
        if not self.argv or any(not item for item in self.argv):
            raise ValueError(f"check {self.check_id} needs a non-empty argv")
        if self.risk not in RISK_ORDER:
            raise ValueError(f"check {self.check_id} has unsupported risk {self.risk}")
        if not self.path_patterns:
            raise ValueError(f"check {self.check_id} needs path patterns")

    def contract(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "argv": list(self.argv),
            "path_patterns": list(self.path_patterns),
            "risk": self.risk,
            "order": self.order,
            "timeout_seconds": self.timeout_seconds,
            "description": self.description,
        }


class CheckCatalog:
    def __init__(self, catalog_id: str, checks: Iterable[CheckDefinition]) -> None:
        if not SAFE_ID.match(catalog_id):
            raise ValueError("unsafe catalog id")
        ordered = sorted(checks, key=lambda item: (item.order, item.check_id))
        if not ordered or len({item.check_id for item in ordered}) != len(ordered):
            raise ValueError("catalog must contain unique checks")
        self.catalog_id = catalog_id
        self.checks = tuple(ordered)

    def contract(self) -> dict[str, Any]:
        return {"schema_version": "check-catalog-v1", "catalog_id": self.catalog_id, "checks": [check.contract() for check in self.checks]}

    @property
    def catalog_digest(self) -> str:
        return digest(self.contract())

    def by_id(self, check_id: str) -> CheckDefinition:
        for check in self.checks:
            if check.check_id == check_id:
                return check
        raise ControlError("verification.unknown-check", "A check plan references an unknown catalog command.", {"check_id": check_id}, ["Regenerate the plan from the current tracked catalog."])


def normalize_path(path: str) -> str:
    value = path.replace("\\", "/").strip("/")
    if not value or ".." in value.split("/") or re.match(r"^[A-Za-z]:", value):
        raise ControlError("verification.invalid-path", "Changed paths must be normalized repository-relative paths.", {"path": path}, ["Regenerate candidate evidence from Git."])
    return value


def select_checks(
    catalog: CheckCatalog,
    candidate: str,
    changed_paths: list[str],
    *,
    base_revision: str | None = None,
) -> dict[str, Any]:
    paths = sorted({normalize_path(path) for path in changed_paths})
    selected: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    for check in catalog.checks:
        matches = sorted(path for path in paths if any(fnmatchcase(path, pattern) for pattern in check.path_patterns))
        if matches:
            selected.append({"check_id": check.check_id, "risk": check.risk, "reason": "affected path matched tracked rule", "matched_paths": matches})
        else:
            deferred.append({"check_id": check.check_id, "reason": "no affected path matched tracked rule"})
    if not selected:
        raise ControlError(
            "verification.unclassified-impact",
            "No tracked affected-check rule covers the candidate paths.",
            {"changed_paths": paths, "catalog_digest": catalog.catalog_digest},
            ["Add a bounded tracked rule and focused test; do not execute an arbitrary command."],
        )
    risk = max((item["risk"] for item in selected), key=RISK_ORDER.__getitem__)
    plan_core = {
        "schema_version": "check-plan-v1",
        "candidate": candidate,
        "base_revision": base_revision,
        "changed_paths": paths,
        "catalog_id": catalog.catalog_id,
        "catalog_digest": catalog.catalog_digest,
        "risk": risk,
        "selected": selected,
        "deferred": deferred,
    }
    return {**plan_core, "plan_digest": digest(plan_core)}


def materialize_arguments(check: CheckDefinition, plan: dict[str, Any]) -> tuple[str, ...]:
    if BASE_REVISION_ARGUMENT not in check.argv:
        return check.argv
    base_revision = plan.get("base_revision")
    if not isinstance(base_revision, str) or not EXACT_REVISION.fullmatch(base_revision):
        raise ControlError(
            "verification.base-revision-required",
            "This affected check requires an exact submitted base revision.",
            {"check_id": check.check_id},
            ["Regenerate the plan from the exact packet submission."],
        )
    return tuple(base_revision if value == BASE_REVISION_ARGUMENT else value for value in check.argv)


def environment_fingerprint() -> dict[str, Any]:
    facts = {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
    }
    return {"facts": facts, "digest": digest(facts), "reuse_eligible": False, "reuse_reason": "installed executable closure is not authenticated"}


class ReceiptStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.base = confined_path(self.root, ".local-codex/control-plane/receipts")

    def _directory(self, work_id: str, candidate: str) -> Path:
        if not SAFE_ID.match(work_id) or not re.fullmatch(r"[0-9a-f]{40,64}", candidate):
            raise ControlError("verification.unsafe-identity", "Receipt identities are unsafe for local storage.", {"work_id": work_id, "candidate": candidate}, ["Use controller-produced work and Git identities."])
        return confined_path(self.root, f".local-codex/control-plane/receipts/{work_id}/{candidate}")

    def append(self, work_id: str, receipt: dict[str, Any]) -> Path:
        directory = self._directory(work_id, str(receipt["candidate"]))
        directory.mkdir(parents=True, exist_ok=True)
        prior_digest = None
        prior_path = self.latest_path(work_id, str(receipt["candidate"]))
        if prior_path is not None:
            prior_document = self.load(prior_path)
            prior_digest = prior_document.get("receipt_digest")
        payload = {**receipt, "prior_receipt_digest": prior_digest}
        payload["receipt_digest"] = digest(payload)
        name = f"{payload['recorded_at'].replace(':', '').replace('-', '')}-{uuid.uuid4()}.json"
        path = directory / name
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as error:
            raise ControlError("verification.receipt-collision", "The append-only receipt path already exists.", {"path": path.name}, ["Retry; never overwrite an existing receipt."]) from error
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(canonical_bytes(payload))
                stream.flush()
                os.fsync(stream.fileno())
        except Exception:
            path.unlink(missing_ok=True)
            raise
        return path

    def paths(self, work_id: str, candidate: str) -> list[Path]:
        directory = self._directory(work_id, candidate)
        return sorted(directory.glob("*.json")) if directory.is_dir() else []

    def latest_path(self, work_id: str, candidate: str) -> Path | None:
        """Return the unique append-chain head, independent of filename order."""

        paths = self.paths(work_id, candidate)
        if not paths:
            return None
        by_digest: dict[str, Path] = {}
        prior_by_digest: dict[str, str | None] = {}
        for path in paths:
            document = self.load(path)
            receipt_digest = document.get("receipt_digest")
            prior_digest = document.get("prior_receipt_digest")
            if (
                not isinstance(receipt_digest, str)
                or not receipt_digest.startswith("sha256:")
                or receipt_digest in by_digest
                or (prior_digest is not None and not isinstance(prior_digest, str))
                or receipt_digest
                != digest(
                    {
                        key: value
                        for key, value in document.items()
                        if key != "receipt_digest"
                    }
                )
            ):
                raise ControlError(
                    "verification.receipt-chain-invalid",
                    "The receipt chain is incomplete or ambiguous.",
                    {"work_id": work_id, "candidate": candidate},
                    ["Preserve the receipt files and use bounded control maintenance."],
                )
            by_digest[receipt_digest] = path
            prior_by_digest[receipt_digest] = prior_digest
        referenced = {
            value for value in prior_by_digest.values() if value is not None
        }
        if not referenced.issubset(by_digest):
            raise ControlError(
                "verification.receipt-chain-invalid",
                "The receipt chain is incomplete or ambiguous.",
                {"work_id": work_id, "candidate": candidate},
                ["Preserve the receipt files and use bounded control maintenance."],
            )
        heads = set(by_digest) - referenced
        if len(heads) != 1:
            raise ControlError(
                "verification.receipt-chain-invalid",
                "The receipt chain is incomplete or ambiguous.",
                {"work_id": work_id, "candidate": candidate},
                ["Preserve the receipt files and use bounded control maintenance."],
            )
        head = next(iter(heads))
        seen: set[str] = set()
        current: str | None = head
        while current is not None:
            if current in seen or current not in by_digest:
                raise ControlError(
                    "verification.receipt-chain-invalid",
                    "The receipt chain is incomplete or ambiguous.",
                    {"work_id": work_id, "candidate": candidate},
                    ["Preserve the receipt files and use bounded control maintenance."],
                )
            seen.add(current)
            current = prior_by_digest[current]
        if seen != set(by_digest):
            raise ControlError(
                "verification.receipt-chain-invalid",
                "The receipt chain is incomplete or ambiguous.",
                {"work_id": work_id, "candidate": candidate},
                ["Preserve the receipt files and use bounded control maintenance."],
            )
        return by_digest[head]

    def load(self, path: Path) -> dict[str, Any]:
        resolved = path.resolve()
        try:
            resolved.relative_to(self.base.resolve())
        except ValueError as error:
            raise ControlError("verification.receipt-outside-store", "Receipt paths must remain inside ignored receipt storage.", {"path": str(path)}, ["Use a receipt path returned by the controller."]) from error
        try:
            return json.loads(resolved.read_bytes())
        except (OSError, json.JSONDecodeError) as error:
            raise ControlError("verification.receipt-malformed", "The receipt is unreadable and was preserved.", {"path": str(path)}, ["Run bounded control maintenance; do not edit the receipt."]) from error


def grant_for_plan(plan: dict[str, Any]) -> CapabilityGrant:
    return CapabilityGrant(
        subject="verification-plan",
        command_ids=tuple(str(item["check_id"]) for item in plan["selected"]),
        path_scopes=tuple(str(value) for value in plan["changed_paths"]),
        effects=("subprocess",),
    )


def execute_plan(root: Path, catalog: CheckCatalog, plan: dict[str, Any], grant: CapabilityGrant | None = None) -> list[dict[str, Any]]:
    capability = grant or grant_for_plan(plan)
    attempts: list[dict[str, Any]] = []
    for selected in plan["selected"]:
        capability.authorize(command_id=str(selected["check_id"]), effect="subprocess", paths=[str(value) for value in selected["matched_paths"]])
        check = catalog.by_id(selected["check_id"])
        arguments = materialize_arguments(check, plan)
        started = time.perf_counter()
        try:
            completed = subprocess.run(list(arguments), cwd=root, check=False, capture_output=True, timeout=check.timeout_seconds)
            exit_code = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
            timed_out = False
        except subprocess.TimeoutExpired as error:
            exit_code = None
            stdout = error.stdout or b""
            stderr = error.stderr or b""
            timed_out = True
        duration_ms = round((time.perf_counter() - started) * 1000, 3)
        attempts.append(
            {
                "check_id": check.check_id,
                "argv": list(arguments),
                "exit_code": exit_code,
                "duration_ms": duration_ms,
                "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
                "stdout_bytes": len(stdout),
                "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
                "stderr_bytes": len(stderr),
                "timed_out": timed_out,
                "capability_digest": capability.grant_digest,
            }
        )
    return attempts


def validate_receipt(receipt: dict[str, Any], catalog: CheckCatalog, current_candidate: str | None = None) -> list[str]:
    errors: list[str] = []
    plan = receipt.get("plan")
    if not isinstance(plan, dict) or plan.get("plan_digest") != digest({key: value for key, value in plan.items() if key != "plan_digest"}):
        errors.append("plan digest mismatch")
    elif plan.get("catalog_digest") != catalog.catalog_digest:
        errors.append("catalog digest is stale")
    selected = [item.get("check_id") for item in (plan or {}).get("selected", [])]
    attempts = receipt.get("attempts")
    if not isinstance(attempts, list) or [item.get("check_id") for item in attempts] != selected:
        errors.append("attempts do not exactly cover selected checks")
    elif any(item.get("exit_code") != 0 or item.get("timed_out") for item in attempts):
        errors.append("one or more selected checks failed or timed out")
    if receipt.get("candidate") != (plan or {}).get("candidate"):
        errors.append("receipt candidate does not match plan")
    if current_candidate is not None and receipt.get("candidate") != current_candidate:
        errors.append("receipt candidate is stale")
    stability = receipt.get("candidate_stability")
    if stability is not None and not stability.get("post_run_stable"):
        errors.append("candidate changed or became dirty during verification")
    stored_digest = receipt.get("receipt_digest")
    if stored_digest:
        core = {key: value for key, value in receipt.items() if key != "receipt_digest"}
        if stored_digest != digest(core):
            errors.append("receipt digest mismatch")
    provenance = receipt.get("provenance")
    if isinstance(provenance, dict):
        provenance_output = {"candidate": receipt.get("candidate"), "plan_digest": (plan or {}).get("plan_digest"), "attempts": attempts}
        if provenance.get("output_digest") != provenance_digest(provenance_output):
            errors.append("receipt provenance digest mismatch")
    return errors


class VerificationService:
    def __init__(self, root: Path, project: ProjectAdapter, state: StateStore, catalog: CheckCatalog, candidate: CandidateAdapter, receipts: ReceiptStore | None = None) -> None:
        self.root = root.resolve()
        self.project = project
        self.state = state
        self.catalog = catalog
        self.candidate = candidate
        self.receipts = receipts or ReceiptStore(root)

    def _submission(self, work_id: str) -> tuple[dict[str, Any], dict[str, Any], bool]:
        self.project.require_delivery_authority(work_id)
        envelope, recovered = self.state.read()
        work = envelope["work_items"].get(work_id)
        if not isinstance(work, dict) or work.get("state") != "submitted" or not isinstance(work.get("submission"), dict):
            raise ControlError("verification.not-submitted", "Affected-check planning requires an exact submitted candidate.", {"work_id": work_id, "state": work.get("state") if isinstance(work, dict) else None}, ["Submit the clean exact candidate first."])
        self.candidate.stable_identity(str(work["submission"]["candidate"]))
        return envelope, work["submission"], recovered

    def plan(self, work_id: str) -> dict[str, Any]:
        envelope, submission, recovered = self._submission(work_id)
        plan = select_checks(
            self.catalog,
            str(submission["candidate"]),
            list(submission["changed_paths"]),
            base_revision=str(submission["base_revision"]),
        )
        return success("verification.plan-created", f"Selected {len(plan['selected'])} affected check(s) for {work_id}.", revision=envelope["revision"], data={"work_id": work_id, "plan": plan, "transaction_recovered": recovered})

    def verify(self, work_id: str) -> dict[str, Any]:
        envelope, submission, recovered = self._submission(work_id)
        plan = select_checks(
            self.catalog,
            str(submission["candidate"]),
            list(submission["changed_paths"]),
            base_revision=str(submission["base_revision"]),
        )
        capability = grant_for_plan(plan)
        attempts = execute_plan(self.root, self.catalog, plan, capability)
        stability_errors: list[str] = []
        try:
            self.candidate.stable_identity(str(submission["candidate"]))
        except ControlError as error:
            stability_errors.append(error.code)
        receipt = {
            "schema_version": "verification-receipt-v1",
            "work_id": work_id,
            "candidate": submission["candidate"],
            "submission_input_digest": digest(submission),
            "plan": plan,
            "environment": environment_fingerprint(),
            "attempts": attempts,
            "candidate_stability": {"post_run_stable": not stability_errors, "errors": stability_errors},
            "producer": {"tool": "local-control-plane", "schema_version": "1.0"},
            "fresh": True,
            "recorded_at": utc_timestamp(),
        }
        receipt["provenance"] = provenance_envelope(
            operation_id="verification.receipt",
            output={"candidate": receipt["candidate"], "plan_digest": plan["plan_digest"], "attempts": attempts},
            revision=str(receipt["candidate"]),
            input_digest=str(receipt["submission_input_digest"]),
            capability_digest=capability.grant_digest,
        )
        errors = validate_receipt(receipt, self.catalog, current_candidate=str(submission["candidate"])) + stability_errors
        receipt["qualification"] = {"qualifying": not errors, "errors": errors}
        path = self.receipts.append(work_id, receipt)
        result = success("verification.receipt-recorded", f"Recorded {'qualifying' if not errors else 'non-qualifying'} receipt for {work_id}.", revision=envelope["revision"], data={"work_id": work_id, "receipt_path": path.relative_to(self.root).as_posix(), "qualifying": not errors, "errors": errors, "selected_check_ids": [item["check_id"] for item in plan["selected"]], "deferred_check_ids": [item["check_id"] for item in plan["deferred"]], "transaction_recovered": recovered})
        if errors:
            result["outcome"] = "not-qualified"
            result["code"] = "verification.failed"
            result["remediation"] = ["Correct the failed or stale boundary and run fresh affected verification."]
        return result

    def validate(self, receipt_path: Path, current_candidate: str | None = None) -> dict[str, Any]:
        receipt = self.receipts.load(receipt_path)
        errors = validate_receipt(receipt, self.catalog, current_candidate=current_candidate)
        if errors:
            raise ControlError("verification.receipt-invalid", "The verification receipt is not current and qualifying.", {"errors": errors}, ["Run fresh affected verification for the exact candidate."])
        return success("verification.receipt-valid", "The receipt is internally valid and qualifying.", data={"receipt_path": receipt_path.as_posix(), "candidate": receipt["candidate"], "receipt_digest": receipt["receipt_digest"]})
