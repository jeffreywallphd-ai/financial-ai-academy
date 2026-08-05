"""Run deterministic completed-slice architecture fitness functions."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]


def main() -> int:
    command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests/architecture",
        "-p",
        "test_*.py",
        "-v",
    ]
    completed = subprocess.run(command, cwd=REPOSITORY, check=False)
    if completed.returncode:
        print("Architecture fitness functions failed.", file=sys.stderr)
        return completed.returncode
    print("Architecture fitness functions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
