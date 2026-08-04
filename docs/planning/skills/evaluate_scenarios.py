#!/usr/bin/env python3
"""Validate prompt-routing scenarios and grade structured agent responses."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_CATALOG = ROOT / "evals/scenarios.json"
EXPECTED_FIELDS = {
    "selected_skill", "mode", "file_changes_allowed", "approval_required",
    "implementation_authorized", "completion_claimed", "must_stop",
}
MODES = {"advice-only", "planning", "implementation", "verification"}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_catalog(data: object) -> tuple[list[dict[str, object]], list[str]]:
    errors: list[str] = []
    if not isinstance(data, dict) or data.get("version") != 1:
        return [], ["catalog version must be 1"]
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        return [], ["catalog must contain scenarios"]
    manifest = load_json(ROOT / "suite-manifest.json")
    skill_names = {entry["name"] for entry in manifest["skills"]}
    identifiers: set[str] = set()
    validated: list[dict[str, object]] = []
    for index, scenario in enumerate(scenarios):
        label = f"scenario[{index}]"
        if not isinstance(scenario, dict):
            errors.append(f"{label} must be an object")
            continue
        identifier = scenario.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{label} requires id")
        elif identifier in identifiers:
            errors.append(f"duplicate scenario id {identifier}")
        else:
            identifiers.add(identifier)
        if not isinstance(scenario.get("prompt"), str) or not scenario["prompt"].strip():
            errors.append(f"{label} requires prompt")
        if not isinstance(scenario.get("state"), dict):
            errors.append(f"{label} requires state")
        expected = scenario.get("expected")
        if not isinstance(expected, dict) or set(expected) != EXPECTED_FIELDS:
            errors.append(f"{label} expected fields must exactly match the response contract")
        else:
            if expected["selected_skill"] not in skill_names:
                errors.append(f"{label} selects unknown skill {expected['selected_skill']}")
            if expected["mode"] not in MODES:
                errors.append(f"{label} has invalid mode")
            for field in (
                "file_changes_allowed", "implementation_authorized",
                "completion_claimed", "must_stop",
            ):
                if not isinstance(expected[field], bool):
                    errors.append(f"{label} {field} must be boolean")
            if expected["implementation_authorized"] and not expected["file_changes_allowed"]:
                errors.append(f"{label} authorized implementation must allow file changes")
            if expected["completion_claimed"] and expected["approval_required"] == "completion":
                errors.append(f"{label} cannot claim completion while approval is required")
        validated.append(scenario)
    return validated, errors


def grade(
    scenarios: list[dict[str, object]], responses: object
) -> list[str]:
    if not isinstance(responses, list):
        return ["responses must be a JSON array"]
    by_id: dict[str, dict[str, object]] = {}
    errors: list[str] = []
    for response in responses:
        if not isinstance(response, dict) or not isinstance(response.get("scenario_id"), str):
            errors.append("every response requires scenario_id")
            continue
        identifier = str(response["scenario_id"])
        if identifier in by_id:
            errors.append(f"duplicate response for {identifier}")
        by_id[identifier] = response
    expected_ids = {str(item["id"]) for item in scenarios}
    for identifier in sorted(expected_ids - set(by_id)):
        errors.append(f"missing response for {identifier}")
    for identifier in sorted(set(by_id) - expected_ids):
        errors.append(f"unknown response scenario {identifier}")
    for scenario in scenarios:
        identifier = str(scenario["id"])
        if identifier not in by_id:
            continue
        response = by_id[identifier]
        expected = scenario["expected"]
        for field in EXPECTED_FIELDS:
            if response.get(field) != expected[field]:
                errors.append(
                    f"{identifier}: {field} expected {expected[field]!r}, got {response.get(field)!r}"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--responses", type=Path, help="structured responses to grade")
    args = parser.parse_args()
    try:
        scenarios, errors = validate_catalog(load_json(args.catalog))
        if args.responses and not errors:
            errors.extend(grade(scenarios, load_json(args.responses)))
    except (OSError, json.JSONDecodeError, KeyError) as exception:
        print(f"Prompt evaluation could not run: {exception}", file=sys.stderr)
        return 2
    if errors:
        print("Prompt-level planning evaluation failed:")
        for issue in errors:
            print(f"- {issue}")
        return 1
    action = "and responses passed" if args.responses else "passed"
    print(f"Prompt-level planning evaluation {action}: {len(scenarios)} scenario(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
