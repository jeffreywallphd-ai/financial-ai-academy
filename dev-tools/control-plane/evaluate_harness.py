#!/usr/bin/env python3
"""Evaluate the tracked deterministic multi-turn control-plane corpus."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from harness import evaluate_corpus  # noqa: E402
from policy import write_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=HERE / "evals/scenarios.json")
    parser.add_argument("--report-path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = HERE.parents[1]
    try:
        corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
        report = evaluate_corpus(corpus)
        if args.report_path:
            write_report(root, args.report_path, report)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Harness evaluation failed: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Harness evaluation {report['status']}: {report['passed_count']}/{report['scenario_count']} scenario(s) passed")
        for result in report["results"]:
            for violation in result.get("violations", []):
                print(f"- {result['scenario_id']}: {violation}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
