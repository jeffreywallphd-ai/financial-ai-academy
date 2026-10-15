#!/usr/bin/env python3
"""Operate the repository-local AI-development control plane."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from contracts import ControlError, success
from engine import ControlPlane
from financial_academy import FinancialAcademyAdapter
from financial_academy_checks import catalog as financial_academy_catalog
from financial_academy_review_ledger import FinancialAcademyReviewLedger
from financial_academy_policy import service as financial_academy_policy_service
from financial_academy_status import FinancialAcademyStatusAdapter
from financial_academy_operations import services as financial_academy_operation_services
from financial_academy_editing import FinancialAcademyEditingService
from financial_academy_portfolio import compatibility_result as financial_academy_compatibility_result
from financial_academy_portfolio import allocation_result as financial_academy_allocation_result
from financial_academy_portfolio import plan_result as financial_academy_plan_result
from financial_academy_portfolio import result as financial_academy_portfolio_result
from git_candidate import GitCandidateAdapter
from operator_status import OperatorStatusService
from state import DEFAULT_LEASE_MINUTES
from store import StateStore, confined_path
from verification import VerificationService
from review import ReviewService
from harness import evaluate_corpus
from policy import write_report as write_generated_report
from provenance import attach as attach_provenance
from telemetry import TelemetrySink, emit_safely


def repository_root(requested: Path | None) -> Path:
    if requested is not None:
        return requested.resolve()
    import subprocess

    completed = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if completed.returncode:
        raise ControlError("repository.not-found", "No Git repository root could be resolved.", {}, ["Pass --root with the intended repository checkout."])
    return Path(completed.stdout.strip()).resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--json", action="store_true", help="emit the stable JSON result contract")
    commands = parser.add_subparsers(dest="command", required=True)

    status = commands.add_parser("status")
    status.add_argument("work_id")

    claim = commands.add_parser("claim")
    claim.add_argument("work_id")
    claim.add_argument("--owner", required=True)
    claim.add_argument("--lease-minutes", type=int, default=DEFAULT_LEASE_MINUTES)
    claim.add_argument("--expected-revision", type=int)

    for name in ("renew", "resume", "submit", "release"):
        command = commands.add_parser(name)
        command.add_argument("work_id")
        command.add_argument("--owner", required=True)
        command.add_argument("--claim-id", required=True)
        if name in {"renew"}:
            command.add_argument("--lease-minutes", type=int, default=DEFAULT_LEASE_MINUTES)
        if name in {"renew", "submit", "release"}:
            command.add_argument("--expected-revision", type=int)
        if name == "submit":
            command.add_argument("--candidate", default="HEAD")
            command.add_argument("--input", action="append", default=[])

    recover = commands.add_parser("recover")
    recover.add_argument("work_id")
    recover.add_argument("--owner", required=True)
    recover.add_argument("--lease-minutes", type=int, default=DEFAULT_LEASE_MINUTES)
    recover.add_argument("--expected-revision", type=int)

    plan_checks = commands.add_parser("plan-checks")
    plan_checks.add_argument("work_id")

    verify = commands.add_parser("verify")
    verify.add_argument("work_id")

    validate_receipt = commands.add_parser("validate-receipt")
    validate_receipt.add_argument("receipt_path", type=Path)
    validate_receipt.add_argument("--current-candidate")

    review_status = commands.add_parser("review-status")
    review_status.add_argument("work_id")

    record_review = commands.add_parser("record-review")
    record_review.add_argument("work_id")
    record_review.add_argument("--reviewer-label", required=True)
    record_review.add_argument("--from", dest="from_file", type=Path, required=True)

    resubmit = commands.add_parser("resubmit")
    resubmit.add_argument("work_id")
    resubmit.add_argument("--owner", required=True)
    resubmit.add_argument("--claim-id", required=True)
    resubmit.add_argument("--candidate", default="HEAD")
    resubmit.add_argument("--input", action="append", dest="declared_inputs", default=[])
    resubmit.add_argument("--expected-revision", type=int)
    resubmit.add_argument("--root-cause")

    policy = commands.add_parser("policy-check")
    policy.add_argument("--profile", choices=("local", "ci"), default="local")
    policy.add_argument("--report-path")

    operator_status = commands.add_parser("operator-status")
    operator_status.add_argument("work_id", nargs="?")

    packet_start = commands.add_parser("packet-start")
    packet_start.add_argument("work_id")

    correction = commands.add_parser("correction-route")
    correction.add_argument("work_id")
    correction.add_argument("--path", action="append", dest="paths", required=True)
    correction.add_argument("--reason-code", required=True)

    maintenance_start = commands.add_parser("maintenance-start")
    maintenance_start.add_argument("--defect-code", required=True)
    maintenance_start.add_argument("--allow", action="append", dest="allowed_action_ids", required=True)
    maintenance_action = commands.add_parser("maintenance-action")
    maintenance_action.add_argument("action_id")
    commands.add_parser("maintenance-finish")
    commands.add_parser("maintenance-status")
    telemetry_report = commands.add_parser("telemetry-report")
    telemetry_report.add_argument("--report-path")
    harness_evaluate = commands.add_parser("harness-evaluate")
    harness_evaluate.add_argument("--report-path")
    commands.add_parser("portfolio-graph")
    portfolio_plan = commands.add_parser("portfolio-plan")
    portfolio_plan.add_argument("--level", choices=("capability", "slice", "work"), required=True)
    portfolio_plan.add_argument("--priority", action="append", default=[])
    portfolio_compatibility = commands.add_parser("portfolio-compatibility")
    portfolio_compatibility.add_argument("--level", choices=("capability", "slice", "work"), required=True)
    portfolio_compatibility.add_argument("--id", action="append", dest="ids")
    portfolio_allocation = commands.add_parser("portfolio-allocate")
    portfolio_allocation.add_argument("--level", choices=("capability", "slice", "work"), required=True)
    portfolio_allocation.add_argument("--priority", action="append", default=[])
    portfolio_allocation.add_argument("--previous-plan", type=Path)
    edit_intent = commands.add_parser("edit-intent")
    edit_acquire = commands.add_parser("edit-acquire")
    edit_recover = commands.add_parser("edit-recover")
    for edit_command in (edit_intent, edit_acquire, edit_recover):
        edit_command.add_argument("--unit-id", required=True)
        edit_command.add_argument("--work-id", required=True)
        edit_command.add_argument("--owner", required=True)
        edit_command.add_argument("--claim-id", required=True)
        edit_command.add_argument("--path", action="append", dest="paths", required=True)
        edit_command.add_argument("--expected-revision", type=int)
    edit_intent.add_argument("--minutes", type=int, default=5)
    edit_acquire.add_argument("--lease-minutes", type=int, default=15)
    edit_recover.add_argument("--lease-minutes", type=int, default=15)
    edit_renew = commands.add_parser("edit-renew")
    edit_release = commands.add_parser("edit-release")
    for edit_command in (edit_renew, edit_release):
        edit_command.add_argument("lease_id")
        edit_command.add_argument("--owner", required=True)
        edit_command.add_argument("--claim-id", required=True)
        edit_command.add_argument("--expected-revision", type=int)
    edit_renew.add_argument("--lease-minutes", type=int, default=15)
    edit_status = commands.add_parser("edit-status")
    edit_status.add_argument("--path")
    return parser


def load_local_review_request(root: Path, requested: Path) -> dict:
    if requested.is_absolute():
        raise ControlError("review.request-not-local", "Review request files must use an ignored repository-relative path.", {"path": str(requested)}, ["Place the request under .local-codex/ and retry."])
    relative = requested.as_posix()
    if not relative.startswith(".local-codex/"):
        raise ControlError("review.request-not-local", "Review request files must remain under ignored .local-codex/.", {"path": relative}, ["Move the request under .local-codex/ and retry."])
    path = confined_path(root, relative)
    try:
        value = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as error:
        raise ControlError("review.request-invalid", "The local review request is unreadable or invalid JSON.", {"path": relative}, ["Correct the local request without moving it into tracked files."]) from error
    if not isinstance(value, dict):
        raise ControlError("review.request-invalid", "The local review request must be a JSON object.", {"path": relative}, ["Use the documented review request fields."])
    return value


def render(result: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    print(f"{result['outcome']}: {result['message']}")
    if result.get("state_revision") is not None:
        print(f"state revision: {result['state_revision']}")
    for remediation in result.get("remediation", []):
        print(f"next: {remediation}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    started = time.perf_counter()
    root: Path | None = None
    command = str(args.command)
    try:
        root = repository_root(args.root)
        project = FinancialAcademyAdapter(root)
        state = StateStore(root, project.projection)
        candidate = GitCandidateAdapter(root)
        engine = ControlPlane(project, candidate, state)
        catalog = financial_academy_catalog()
        verifier = VerificationService(root, project, state, catalog, candidate)
        reviewer = ReviewService(root, project, state, candidate, catalog, FinancialAcademyReviewLedger(root))
        policy = financial_academy_policy_service(root, project)
        operator = OperatorStatusService(FinancialAcademyStatusAdapter(root, project))
        starter, corrections, maintenance = financial_academy_operation_services(root, project)
        editing = FinancialAcademyEditingService(root)
        values = vars(args)
        command = values.pop("command")
        as_json = values.pop("json")
        values.pop("root")
        if command in {"claim", "renew", "recover", "submit", "release", "verify", "record-review", "resubmit", "packet-start", "correction-route", "edit-intent", "edit-acquire", "edit-recover", "edit-renew", "edit-release"}:
            maintenance.guard_mutation(command)
        if command == "plan-checks":
            result = verifier.plan(**values)
        elif command == "verify":
            result = verifier.verify(**values)
        elif command == "validate-receipt":
            if not values["receipt_path"].is_absolute():
                values["receipt_path"] = root / values["receipt_path"]
            result = verifier.validate(**values)
        elif command == "review-status":
            result = reviewer.status(**values)
        elif command == "record-review":
            request = load_local_review_request(root, values.pop("from_file"))
            receipt_path = Path(str(request.get("receipt_path", "")))
            if not receipt_path.is_absolute():
                receipt_path = root / receipt_path
            result = reviewer.record(
                values["work_id"],
                reviewer_label=values["reviewer_label"],
                status=str(request.get("status", "")),
                receipt_path=receipt_path,
                findings=request.get("findings", []),
                closures=request.get("closures", []),
                notes=str(request.get("notes", "")),
            )
        elif command == "resubmit":
            result = reviewer.resubmit(**values)
        elif command == "policy-check":
            result = policy.check(root=root, **values)
        elif command == "operator-status":
            result = operator.status(**values)
        elif command == "packet-start":
            result = starter.start(**values)
        elif command == "correction-route":
            result = corrections.plan(**values)
        elif command == "maintenance-start":
            result = maintenance.start(**values)
        elif command == "maintenance-action":
            result = maintenance.execute(**values)
        elif command == "maintenance-finish":
            result = maintenance.finish()
        elif command == "maintenance-status":
            result = maintenance.status()
        elif command == "telemetry-report":
            result = TelemetrySink(root).report_result(**values)
        elif command == "harness-evaluate":
            corpus = json.loads((Path(__file__).resolve().parent / "evals/scenarios.json").read_text(encoding="utf-8"))
            report = evaluate_corpus(corpus)
            written = write_generated_report(root, values["report_path"], report).relative_to(root).as_posix() if values.get("report_path") else None
            result = success("harness.evaluated", f"Harness evaluation {report['status']} across {report['scenario_count']} scenario(s).", data={"report": report, "report_path": written})
            if report["status"] != "passed":
                result["outcome"] = "not-ready"
                result["remediation"] = ["Correct the named deterministic scenario violation without weakening its safety assertion."]
        elif command == "portfolio-graph":
            result = financial_academy_portfolio_result(root)
        elif command == "portfolio-plan":
            result = financial_academy_plan_result(root, **values)
        elif command == "portfolio-compatibility":
            result = financial_academy_compatibility_result(root, **values)
        elif command == "portfolio-allocate":
            result = financial_academy_allocation_result(root, **values)
        elif command == "edit-intent":
            result = editing.announce(**values)
        elif command == "edit-acquire":
            result = editing.acquire(**values)
        elif command == "edit-recover":
            result = editing.recover(**values)
        elif command == "edit-renew":
            result = editing.renew(**values)
        elif command == "edit-release":
            result = editing.release(**values)
        elif command == "edit-status":
            result = editing.status(**values)
        else:
            result = getattr(engine, command)(**values)
        exit_code = 1 if result.get("outcome") == "not-ready" else 0
    except ControlError as error:
        result = error.as_result()
        as_json = getattr(args, "json", False)
        exit_code = 2
    if root is not None:
        duration_ms = (time.perf_counter() - started) * 1000
        emit_safely(
            TelemetrySink(root),
            command_id=command,
            outcome=str(result.get("outcome", "unknown")),
            result_code=str(result.get("code", "unknown")),
            duration_ms=duration_ms,
            remediation_count=len(result.get("remediation", [])),
        )
        result = attach_provenance(result, operation_id=command, root=root)
    render(result, as_json)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
