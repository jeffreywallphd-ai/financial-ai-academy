"""Project-neutral deterministic policy evaluation and report publication."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping

from contracts import ControlError, success
from store import atomic_write, canonical_bytes, confined_path


Predicate = Callable[[object], bool]


@dataclass(frozen=True, slots=True)
class Fact:
    available: bool
    value: object = None
    evidence_count: int = 0
    reason: str = ""


@dataclass(frozen=True, slots=True)
class Rule:
    rule_id: str
    severity: str
    fact_id: str
    remediation: str
    predicate: Predicate = bool


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def evaluate_policy(
    rules: tuple[Rule, ...],
    facts: Mapping[str, Fact],
    *,
    profile: str,
    revision: str | None = None,
) -> dict[str, Any]:
    """Evaluate one stable inventory without exposing fact payloads."""

    if profile not in {"local", "ci"}:
        raise ControlError(
            "policy.profile-invalid",
            "Policy profile must be local or ci.",
            {"profile": profile},
            ["Use --profile local or --profile ci."],
        )
    identifiers = [rule.rule_id for rule in rules]
    if identifiers != sorted(set(identifiers)):
        raise ControlError(
            "policy.inventory-invalid",
            "Policy rule identifiers must be unique and sorted.",
            {},
            ["Sort the adapter rule inventory and remove duplicate IDs."],
        )
    started = utc_timestamp()
    results: list[dict[str, Any]] = []
    for rule in rules:
        fact = facts.get(rule.fact_id, Fact(False, reason="fact unavailable"))
        if not fact.available:
            disposition = "not-evaluated"
        else:
            try:
                disposition = "passed" if rule.predicate(fact.value) else "failed"
            except (TypeError, ValueError):
                disposition = "failed"
        result = {
            "rule_id": rule.rule_id,
            "severity": rule.severity,
            "disposition": disposition,
            "evidence_digest": digest(fact.value) if fact.available else None,
            "evidence_count": fact.evidence_count if fact.available else 0,
            "reason": "" if fact.available else (fact.reason or "fact unavailable"),
            "remediation": rule.remediation if disposition == "failed" else "",
        }
        results.append(result)
    failed = [item for item in results if item["disposition"] == "failed"]
    report = {
        "schema_version": "control-policy-report-v1",
        "tool_version": "1.0",
        "profile": profile,
        "revision": revision,
        "started_at": started,
        "completed_at": utc_timestamp(),
        "status": "failed" if failed else "ready",
        "rule_inventory_digest": digest(identifiers),
        "rules": results,
        "summary": {
            "passed": sum(item["disposition"] == "passed" for item in results),
            "failed": len(failed),
            "not_evaluated": sum(item["disposition"] == "not-evaluated" for item in results),
        },
    }
    return report


def write_report(root: Path, relative_path: str, report: dict[str, Any]) -> Path:
    normalized = PurePosixPath(relative_path.replace("\\", "/"))
    allowed = (
        PurePosixPath("artifacts/control-plane"),
        PurePosixPath(".local-codex/control-plane/reports"),
    )
    if not any(normalized == prefix or prefix in normalized.parents for prefix in allowed):
        raise ControlError(
            "policy.report-path-not-confined",
            "Policy reports must remain in a designated generated-output directory.",
            {"path": relative_path},
            ["Use artifacts/control-plane/ or .local-codex/control-plane/reports/."],
        )
    path = confined_path(root.resolve(), normalized.as_posix())
    atomic_write(path, canonical_bytes(report))
    return path


class PolicyService:
    def __init__(self, rules: tuple[Rule, ...], fact_provider: Callable[[str], Mapping[str, Fact]], revision_provider: Callable[[], str | None]) -> None:
        self.rules = rules
        self.fact_provider = fact_provider
        self.revision_provider = revision_provider

    def check(self, *, profile: str, report_path: str | None = None, root: Path | None = None) -> dict[str, Any]:
        report = evaluate_policy(self.rules, self.fact_provider(profile), profile=profile, revision=self.revision_provider())
        written = None
        if report_path is not None:
            if root is None:
                raise ValueError("root is required when report_path is set")
            written = write_report(root, report_path, report).relative_to(root.resolve()).as_posix()
        result = success(
            "policy.checked",
            f"Policy is {report['status']} across {len(report['rules'])} rule(s).",
            data={"report": report, "report_path": written},
        )
        if report["status"] == "failed":
            result["outcome"] = "not-ready"
            result["remediation"] = [str(item["remediation"]) for item in report["rules"] if item["disposition"] == "failed"]
        return result
