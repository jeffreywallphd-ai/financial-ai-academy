#!/usr/bin/env python3
"""Create one portable zip archive per planning skill."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "suite-manifest.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skill", action="append", default=[], help="Package only this skill; repeat as needed")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    known = [entry["name"] for entry in manifest["skills"]]
    selected = args.skill or known
    unknown = sorted(set(selected) - set(known))
    if unknown:
        parser.error("unknown skill(s): " + ", ".join(unknown))
    args.output.mkdir(parents=True, exist_ok=True)
    for name in selected:
        folder = ROOT / name
        if not (folder / "SKILL.md").is_file():
            parser.error(f"invalid skill folder: {folder}")
        archive = args.output / f"{name}.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for path in sorted(folder.rglob("*")):
                if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue
                target.write(path, path.relative_to(folder).as_posix())
        print(f"Packaged {name}: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
