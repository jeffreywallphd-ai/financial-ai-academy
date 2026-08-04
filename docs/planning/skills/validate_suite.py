#!/usr/bin/env python3
"""Validate the governed planning skill suite and compatibility contract."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "suite-manifest.json"
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FIELD_RE = re.compile(r"^([a-z][a-z0-9-]*):\s*(.+)$")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def skill_metadata(text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, ["missing YAML frontmatter"]
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        field = FIELD_RE.match(line)
        if not field:
            errors.append(f"invalid frontmatter line: {line}")
            continue
        values[field.group(1)] = field.group(2).strip().strip('"')
    extra = set(values) - {"name", "description"}
    if extra:
        errors.append("unsupported frontmatter fields: " + ", ".join(sorted(extra)))
    return values, errors


def main() -> int:
    errors: list[str] = []
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: unable to load manifest: {error}")
        return 2
    names = [entry["name"] for entry in manifest.get("skills", [])]
    if manifest.get("contractVersion") != 2:
        errors.append("manifest contractVersion must be 2")
    if manifest.get("discoveryTarget") != ".agents/skills":
        errors.append("manifest discoveryTarget must be .agents/skills")
    expected_ownership = {
        "write_scope", "generated_artifacts", "base_revision", "claim_id",
        "claimed_by", "claimed_at",
    }
    if set(manifest.get("workPacketOwnershipFields", [])) != expected_ownership:
        errors.append("manifest workPacketOwnershipFields are incomplete")
    if len(names) != len(set(names)):
        errors.append("manifest skill names must be unique")
    for entry in manifest.get("skills", []):
        name = entry["name"]
        folder = ROOT / name
        if not NAME_RE.match(name) or folder.name != name:
            errors.append(f"{name}: invalid skill name")
            continue
        for relative in entry.get("requiredFiles", []):
            if not (folder / relative).is_file():
                errors.append(f"{name}: missing {relative}")
        skill_path = folder / "SKILL.md"
        if not skill_path.is_file():
            continue
        text = skill_path.read_text(encoding="utf-8")
        metadata, metadata_errors = skill_metadata(text)
        errors.extend(f"{name}: {error}" for error in metadata_errors)
        if metadata.get("name") != name:
            errors.append(f"{name}: frontmatter name must match folder")
        description = metadata.get("description", "")
        if not description or len(description) > 1024:
            errors.append(f"{name}: description must contain 1-1024 characters")
        if len(text.splitlines()) > 500:
            errors.append(f"{name}: SKILL.md exceeds 500 lines")
        if "AGENTS.md" not in text or "docs/README.md" not in text:
            errors.append(f"{name}: repository-entry gate is incomplete")
        if name != "guide-next-planning-action" and not (
            "## Mandatory Repository Entry Gate" in text
            or "## MANDATORY FILE-CHANGE GATE" in text
        ):
            errors.append(f"{name}: mandatory file-change gate is not prominent")
        if name == "guide-next-planning-action" and "mandatory file-change gate" not in text:
            errors.append(f"{name}: routed file-change gate is missing")
        if "TODO" in text or "[TODO" in text:
            errors.append(f"{name}: unresolved TODO placeholder")
        yaml_path = folder / "agents" / "openai.yaml"
        if yaml_path.is_file():
            yaml_text = yaml_path.read_text(encoding="utf-8")
            for field in ("display_name:", "short_description:", "default_prompt:"):
                if field not in yaml_text:
                    errors.append(f"{name}: openai.yaml missing {field[:-1]}")
            if ("$" + name) not in yaml_text:
                errors.append(f"{name}: default_prompt must mention $" + name)
        for script in (folder / "scripts").glob("*.py"):
            try:
                compile(script.read_text(encoding="utf-8"), str(script), "exec")
            except SyntaxError as error:
                errors.append(f"{name}: invalid Python in {script.name}: {error}")
    router = (ROOT / "guide-next-planning-action" / "SKILL.md").read_text(encoding="utf-8")
    for name in names:
        if name != "guide-next-planning-action" and name not in router:
            errors.append(f"router does not reference {name}")
    implement = (ROOT / "implement-vertical-slice" / "SKILL.md").read_text(encoding="utf-8")
    for token in ("selection_approval", "planning_approval", "implementation_approval", "current explicit"):
        if token not in implement:
            errors.append(f"implementation skill missing gate token: {token}")
    approval = (ROOT / "approve-planned-work" / "SKILL.md").read_text(encoding="utf-8")
    for prefix in manifest.get("approvalPrefixes", []):
        if ("`" + prefix + "`") not in approval:
            errors.append(f"approval skill missing prefix: {prefix}")
    for support in (
        ROOT / "sync_skills.py",
        ROOT / "evaluate_scenarios.py",
        ROOT / "evals" / "scenarios.json",
        ROOT / "evals" / "reference-responses.json",
    ):
        if not support.is_file():
            errors.append(f"missing suite support file: {support.relative_to(ROOT)}")
    packet_template = (
        ROOT / "author-agent-work-packet" / "assets" / "work-packet-template.md"
    ).read_text(encoding="utf-8")
    for field in expected_ownership:
        if f"{field}:" not in packet_template:
            errors.append(f"work-packet template missing ownership field: {field}")
    if errors:
        print("Planning skill suite validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Planning skill suite validation passed: {len(names)} compatible skills verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
