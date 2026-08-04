#!/usr/bin/env python3
"""Run the fixed deterministic readiness gates for an automated agent change."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    arguments: tuple[str, ...]


def repository_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() and (candidate / "docs").is_dir():
            return candidate
    raise RuntimeError("Unable to locate repository root")


def checks(root: Path, profile: str, base_ref: str | None) -> list[Check]:
    python = sys.executable
    planning = [python, "dev-tools/planning/check_planning.py"]
    if base_ref:
        planning.extend(["--base-ref", base_ref])
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("local", "ci"), default="local")
    parser.add_argument("--base-ref", help="git revision used for lifecycle-transition checks")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    parser.add_argument("--verbose", action="store_true", help="show successful command output")
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
            "name": item.name,
            "status": "passed" if completed.returncode == 0 else "failed",
            "exitCode": completed.returncode,
            "durationSeconds": duration,
            "command": list(item.arguments),
        }
        if completed.stdout.strip():
            record["stdout"] = completed.stdout.strip()
        if completed.stderr.strip():
            record["stderr"] = completed.stderr.strip()
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
        "status": "ready" if passed else "not-ready",
        "profile": args.profile,
        "baseRef": args.base_ref,
        "checks": report,
    }
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        if args.profile == "local" and not (root / ".agents/skills").is_dir():
            print("NOTE local .agents/skills is not installed; run sync_skills.py when discovery is needed.")
        print(f"Agent readiness: {output['status']} ({len(report)} check(s))")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
