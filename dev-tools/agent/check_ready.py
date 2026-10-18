#!/usr/bin/env python3
"""Run the fixed deterministic readiness gates for an automated agent change."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    arguments: tuple[str, ...]


REPORT_SCHEMA = "agent-readiness-report-v1"


def repository_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() and (candidate / "docs").is_dir():
            return candidate
    raise RuntimeError("Unable to locate repository root")


def checks(root: Path, profile: str, base_ref: str | None) -> list[Check]:
    python = sys.executable
    planning = [python, "dev-tools/planning/check_planning.py"]
    learner_language = [python, "dev-tools/learner-language/check_learner_language.py"]
    if base_ref:
        planning.extend(["--base-ref", base_ref])
        learner_language.extend(["--base-ref", base_ref])
    selected = [
        Check("planning integrity", tuple(planning)),
        Check("planning tool behavior", (python, "dev-tools/planning/test_planning_tools.py")),
        Check("planning skill compatibility", (python, "docs/planning/skills/validate_suite.py")),
        Check("planning skill behavior", (python, "docs/planning/skills/test_suite.py")),
        Check("planning skill support", (python, "docs/planning/skills/test_support.py")),
        Check(
            "prompt-level planning evaluations",
            (
                python,
                "docs/planning/skills/evaluate_scenarios.py",
                "--responses",
                "docs/planning/skills/evals/reference-responses.json",
            ),
        ),
        Check("agent-readiness CI workflow", (python, "dev-tools/agent/check_ci_workflow.py")),
        Check("agent-readiness behavior", (python, "dev-tools/agent/test_check_ready.py")),
        Check("guidance quality", (python, "dev-tools/guidance/check_guidance_quality.py")),
        Check("learner-language quality", tuple(learner_language)),
        Check("control-plane policy", (python, "dev-tools/control-plane/control_plane.py", "--json", "policy-check", "--profile", profile)),
        Check("control-plane lifecycle", (python, "dev-tools/control-plane/test_control_plane.py")),
        Check("control-plane verification", (python, "dev-tools/control-plane/test_verification.py")),
        Check("control-plane review", (python, "dev-tools/control-plane/test_review.py")),
        Check("control-plane policy and status", (python, "dev-tools/control-plane/test_policy.py")),
        Check("control-plane start and maintenance", (python, "dev-tools/control-plane/test_operations.py")),
        Check("control-plane qualification", (python, "dev-tools/control-plane/test_qualification.py")),
        Check("control-plane multi-turn evaluations", (python, "dev-tools/control-plane/evaluate_harness.py")),
        Check("portfolio graph", (python, "dev-tools/control-plane/test_portfolio.py")),
        Check("portfolio ordering", (python, "dev-tools/control-plane/test_portfolio_ordering.py")),
        Check("portfolio compatibility", (python, "dev-tools/control-plane/test_portfolio_conflicts.py")),
        Check("file-edit coordination", (python, "dev-tools/control-plane/test_file_leases.py")),
        Check("portfolio allocation", (python, "dev-tools/control-plane/test_portfolio_allocation.py")),
        Check("portfolio qualification", (python, "dev-tools/control-plane/test_portfolio_qualification.py")),
        Check("portfolio real-core evaluations", (python, "dev-tools/control-plane/evaluate_portfolio.py")),
        Check("roadmap review projection", (python, "dev-tools/control-plane/test_roadmap_review.py")),
        Check("roadmap review site contract", (python, "dev-tools/roadmap-review-site/test_qualification.py")),
        Check("documentation integrity", (python, "dev-tools/documentation/check_docs.py")),
        Check("design-system integrity", (python, "dev-tools/design/check_design_system.py")),
    ]
    discovery = root / ".agents/skills"
    if profile == "local" and discovery.is_dir():
        selected.insert(
            6,
            Check(
                "local planning skill discovery",
                (python, "docs/planning/skills/sync_skills.py", "--check"),
            ),
        )
    return selected


def output_summary(value: str) -> dict[str, object]:
    payload = value.encode("utf-8")
    return {"sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}


def write_report(root: Path, requested: str, value: dict[str, object]) -> Path:
    normalized = Path(requested.replace("\\", "/"))
    if normalized.is_absolute() or ".." in normalized.parts or normalized.parts[:2] != ("artifacts", "control-plane"):
        raise ValueError("--report-path must be repository-relative under artifacts/control-plane/")
    path = root / normalized
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("local", "ci"), default="local")
    parser.add_argument("--base-ref", help="git revision used for lifecycle-transition checks")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    parser.add_argument("--verbose", action="store_true", help="show successful command output")
    parser.add_argument("--report-path", help="write a privacy-minimized JSON report under artifacts/control-plane/")
    args = parser.parse_args()
    try:
        root = repository_root()
    except RuntimeError as exception:
        print(str(exception), file=sys.stderr)
        return 2

    report: list[dict[str, object]] = []
    for item in checks(root, args.profile, args.base_ref):
        started = time.monotonic()
        completed = subprocess.run(
            list(item.arguments),
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        duration = round(time.monotonic() - started, 3)
        record: dict[str, object] = {
            "check_id": item.name,
            "name": item.name,
            "status": "passed" if completed.returncode == 0 else "failed",
            "exitCode": completed.returncode,
            "durationSeconds": duration,
            "stdout": output_summary(completed.stdout),
            "stderr": output_summary(completed.stderr),
        }
        report.append(record)
        if not args.json:
            print(f"{'PASS' if completed.returncode == 0 else 'FAIL'} {item.name} ({duration:.3f}s)")
            if completed.returncode or args.verbose:
                if completed.stdout.strip():
                    print(completed.stdout.rstrip())
                if completed.stderr.strip():
                    print(completed.stderr.rstrip(), file=sys.stderr)

    passed = all(item["status"] == "passed" for item in report)
    output = {
        "schema_version": REPORT_SCHEMA,
        "status": "ready" if passed else "not-ready",
        "profile": args.profile,
        "baseRef": args.base_ref,
        "checks": report,
    }
    if args.report_path:
        try:
            written = write_report(root, args.report_path, output)
        except (OSError, ValueError) as exception:
            print(f"Readiness report write failed: {exception}", file=sys.stderr)
            return 2
        if not args.json:
            print(f"Readiness report: {written.relative_to(root).as_posix()}")
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        if args.profile == "local" and not (root / ".agents/skills").is_dir():
            print("NOTE local .agents/skills is not installed; run sync_skills.py when discovery is needed.")
        print(f"Agent readiness: {output['status']} ({len(report)} check(s))")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
