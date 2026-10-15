"""Deterministic real-core portfolio safety and anti-rigidity evaluator."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from contracts import ControlError
from portfolio import analyze
from portfolio_allocation import allocate
from store import canonical_bytes


CORPUS_SCHEMA = "portfolio-harness-corpus-v1"
REPORT_SCHEMA = "portfolio-harness-report-v1"


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _normalized_groups(value: object) -> list[list[str]]:
    if not isinstance(value, list):
        return []
    return [[str(item) for item in group] for group in value if isinstance(group, list)]


def evaluate_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    scenario_id = str(scenario.get("id", ""))
    violations: list[str] = []
    nodes = scenario.get("nodes")
    expected = scenario.get("expected")
    budgets = scenario.get("budgets")
    if not scenario_id or not isinstance(nodes, list) or not isinstance(expected, dict) or not isinstance(budgets, dict):
        return {"scenario_id": scenario_id or "invalid", "status": "failed", "violations": ["scenario.shape-invalid"], "scenario_digest": _digest(scenario)}
    graph = analyze(item for item in nodes if isinstance(item, dict))
    allocation: dict[str, Any] | None = None
    observed_error: str | None = None
    try:
        allocation = allocate(
            graph,
            level=str(scenario.get("level", "")),
            authority_current=[str(item) for item in scenario.get("authority_current", [])],
            explicit_priority=[str(item) for item in scenario.get("explicit_priority", [])],
            accepted_sequence=[str(item) for item in scenario.get("accepted_sequence", [])],
            coordination=scenario.get("coordination") if isinstance(scenario.get("coordination"), dict) else None,
        )
    except ControlError as error:
        observed_error = error.code

    expected_error = expected.get("error_code")
    if expected_error:
        if observed_error != expected_error:
            violations.append("safety.expected-error-mismatch")
        metrics = {"blocked_count": 0, "isolated_lane_count": 0, "parallel_lane_count": 0, "unresolved_pair_count": 0}
    elif observed_error or allocation is None:
        violations.append("safety.unexpected-refusal")
        metrics = {"blocked_count": 0, "isolated_lane_count": 0, "parallel_lane_count": 0, "unresolved_pair_count": 0}
    else:
        lane_ids = [str(item.get("unit_id")) for item in allocation["lanes"]]
        groups = _normalized_groups(allocation["parallel_groups"])
        blocked_ids = [str(item.get("id")) for item in allocation["blocked"]]
        if "lane_ids" in expected and lane_ids != [str(item) for item in expected["lane_ids"]]:
            violations.append("safety.lane-set-or-order-mismatch")
        if "parallel_groups" in expected and groups != _normalized_groups(expected["parallel_groups"]):
            violations.append("safety.parallel-groups-mismatch")
        if "blocked_ids" in expected and blocked_ids != [str(item) for item in expected["blocked_ids"]]:
            violations.append("safety.blocked-set-mismatch")
        if not allocation.get("constraints", {}).get("single_hierarchy_level"):
            violations.append("safety.mixed-hierarchy-level")
        if allocation.get("constraints", {}).get("creates_agents") or allocation.get("constraints", {}).get("grants_authority"):
            violations.append("safety.authority-or-execution-granted")
        unresolved_pairs = {tuple(sorted((str(item.get("left")), str(item.get("right"))))) for item in allocation["unresolved_pairs"]}
        for group in groups:
            for index, left in enumerate(group):
                for right in group[index + 1:]:
                    if tuple(sorted((left, right))) in unresolved_pairs:
                        violations.append("safety.unresolved-pair-grouped")
        metrics = {
            "blocked_count": len(blocked_ids),
            "isolated_lane_count": sum(len(group) == 1 for group in groups),
            "parallel_lane_count": sum(len(group) for group in groups if len(group) > 1),
            "unresolved_pair_count": len(allocation["unresolved_pairs"]),
        }

    budget_rules = {
        "max_blocked_count": (metrics["blocked_count"], lambda actual, limit: actual <= limit),
        "max_isolated_lane_count": (metrics["isolated_lane_count"], lambda actual, limit: actual <= limit),
        "min_parallel_lane_count": (metrics["parallel_lane_count"], lambda actual, limit: actual >= limit),
        "max_unresolved_pair_count": (metrics["unresolved_pair_count"], lambda actual, limit: actual <= limit),
    }
    for name, (actual, predicate) in budget_rules.items():
        if name in budgets and not predicate(actual, int(budgets[name])):
            violations.append(f"friction.{name}-violated")
    return {
        "scenario_id": scenario_id,
        "status": "failed" if violations else "passed",
        "metrics": metrics,
        "violations": violations,
        "scenario_digest": _digest(scenario),
    }


def evaluate_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    scenarios = corpus.get("scenarios")
    if corpus.get("schema_version") != CORPUS_SCHEMA or not isinstance(scenarios, list) or not scenarios:
        results = [{"scenario_id": "corpus", "status": "failed", "metrics": {}, "violations": ["corpus.schema-invalid"], "scenario_digest": _digest(corpus)}]
    else:
        identifiers = [str(item.get("id", "")) for item in scenarios if isinstance(item, dict)]
        results = [evaluate_scenario(item) for item in scenarios if isinstance(item, dict)]
        if len(identifiers) != len(scenarios) or identifiers != sorted(set(identifiers)):
            results.append({"scenario_id": "corpus-order", "status": "failed", "metrics": {}, "violations": ["corpus.ids-not-unique-sorted"], "scenario_digest": _digest(identifiers)})
    passed = all(item["status"] == "passed" for item in results)
    return {
        "schema_version": REPORT_SCHEMA,
        "status": "passed" if passed else "failed",
        "corpus_digest": _digest(corpus),
        "scenario_count": len(results),
        "passed_count": sum(item["status"] == "passed" for item in results),
        "failed_count": sum(item["status"] == "failed" for item in results),
        "aggregate_metrics": {
            key: sum(int(item.get("metrics", {}).get(key, 0)) for item in results)
            for key in ("blocked_count", "isolated_lane_count", "parallel_lane_count", "unresolved_pair_count")
        },
        "results": results,
    }
