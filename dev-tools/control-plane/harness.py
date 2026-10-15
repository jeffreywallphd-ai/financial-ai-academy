"""Deterministic multi-turn control-plane regression evaluator."""

from __future__ import annotations

import hashlib
from typing import Any

from store import canonical_bytes


FORBIDDEN_KEYS = {"prompt", "source", "payload", "argv", "stdout", "stderr", "reviewer_label", "actor_label", "email", "name", "notes", "path", "work_id"}
FORBIDDEN_COMMANDS = {"approve", "request-approval", "manual-metadata-edit", "run-shell"}


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def forbidden_keys(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                found.add(str(key))
            found.update(forbidden_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            found.update(forbidden_keys(nested))
    return found


def evaluate_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    scenario_id = str(scenario.get("id", ""))
    turns = scenario.get("turns")
    assertions = scenario.get("assertions")
    violations: list[str] = []
    if not scenario_id or not isinstance(turns, list) or not turns or not isinstance(assertions, dict):
        return {"scenario_id": scenario_id or "invalid", "status": "failed", "violations": ["scenario shape is invalid"]}
    commands = [str(turn.get("command_id", "")) for turn in turns if isinstance(turn, dict)]
    if len(commands) != len(turns) or any(not value for value in commands):
        violations.append("each turn needs a command_id")
    if FORBIDDEN_COMMANDS.intersection(commands):
        violations.append("forbidden authority or arbitrary repair command appeared")
    maximum = int(assertions.get("max_turns", len(turns)))
    if len(turns) > maximum:
        violations.append(f"turn budget exceeded: {len(turns)} > {maximum}")
    required = [str(value) for value in assertions.get("required_commands", [])]
    missing = [value for value in required if value not in commands]
    if missing:
        violations.append("required commands missing: " + ", ".join(missing))
    forbidden = [str(value) for value in assertions.get("forbidden_commands", [])]
    present = [value for value in forbidden if value in commands]
    if present:
        violations.append("scenario-forbidden commands present: " + ", ".join(present))
    aggregate = sum(bool(turn.get("aggregate_readiness")) for turn in turns if isinstance(turn, dict))
    if aggregate > int(assertions.get("max_aggregate_readiness", aggregate)):
        violations.append("aggregate-readiness budget exceeded")
    for index, turn in enumerate(turns, start=1):
        if not isinstance(turn, dict):
            continue
        if turn.get("outcome") in {"refused", "not-ready", "not-qualified"} and int(turn.get("remediation_count", 0)) < 1:
            violations.append(f"turn {index} has an ambiguous refusal")
    expected = assertions.get("expected_final_code")
    if expected and str(turns[-1].get("code", "")) != str(expected):
        violations.append("final result code mismatch")
    unsafe_keys = forbidden_keys(scenario)
    if unsafe_keys:
        violations.append("privacy-forbidden fields: " + ", ".join(sorted(unsafe_keys)))
    return {"scenario_id": scenario_id, "status": "failed" if violations else "passed", "turn_count": len(turns), "aggregate_readiness_count": aggregate, "violations": violations, "scenario_digest": digest(scenario)}


def evaluate_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    scenarios = corpus.get("scenarios")
    if corpus.get("schema_version") != "harness-corpus-v1" or not isinstance(scenarios, list) or not scenarios:
        results = [{"scenario_id": "corpus", "status": "failed", "violations": ["corpus schema is invalid"]}]
    else:
        identifiers = [str(item.get("id", "")) for item in scenarios if isinstance(item, dict)]
        results = [evaluate_scenario(item) for item in scenarios if isinstance(item, dict)]
        if len(identifiers) != len(scenarios) or identifiers != sorted(set(identifiers)):
            results.append({"scenario_id": "corpus-order", "status": "failed", "violations": ["scenario IDs must be unique and sorted"]})
    passed = all(item["status"] == "passed" for item in results)
    return {
        "schema_version": "harness-evaluation-report-v1",
        "status": "passed" if passed else "failed",
        "corpus_digest": digest(corpus),
        "scenario_count": len(results),
        "passed_count": sum(item["status"] == "passed" for item in results),
        "failed_count": sum(item["status"] == "failed" for item in results),
        "results": results,
    }
