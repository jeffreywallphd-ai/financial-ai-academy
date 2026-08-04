#!/usr/bin/env python3
"""Exercise skill synchronization and prompt-evaluation support."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from sync_skills import check_one, install_one, skill_names  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="planning-skill-sync-") as directory:
        target_root = Path(directory) / "skills"
        for name in skill_names():
            source = ROOT / name
            target = target_root / name
            assert install_one(source, target, "copy") == "copy"
            assert check_one(source, target) is None
        drift = target_root / skill_names()[0] / "SKILL.md"
        drift.write_text(drift.read_text(encoding="utf-8") + "\nDrift\n", encoding="utf-8")
        assert check_one(ROOT / skill_names()[0], target_root / skill_names()[0]) is not None

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "evaluate_scenarios.py"),
            "--responses",
            str(ROOT / "evals/reference-responses.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode:
        raise AssertionError(completed.stdout + completed.stderr)
    catalog = json.loads((ROOT / "evals/scenarios.json").read_text(encoding="utf-8"))
    assert len(catalog["scenarios"]) >= 10
    print("Planning skill support tests passed: managed sync, drift detection, and prompt grading verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
