#!/usr/bin/env python3
"""Confinement, provenance, telemetry, harness, privacy, and friction tests."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from capabilities import CapabilityGrant  # noqa: E402
from contracts import ControlError  # noqa: E402
from harness import evaluate_corpus, evaluate_scenario  # noqa: E402
from provenance import attach, validates  # noqa: E402
from telemetry import FORBIDDEN_EVENT_FIELDS, TelemetrySink, emit_safely  # noqa: E402
from verification import CheckCatalog, CheckDefinition, execute_plan, select_checks  # noqa: E402


class CapabilityTests(unittest.TestCase):
    def test_exact_command_effect_and_paths_are_authorized_without_argv(self) -> None:
        grant = CapabilityGrant("fixture", ("check:docs",), ("docs/guide.md",), ("subprocess",))
        grant.authorize(command_id="check:docs", effect="subprocess", paths=["docs/guide.md"])
        contract = grant.contract()
        self.assertEqual("capability-grant-v1", contract["schema_version"])
        self.assertNotIn("argv", contract)
        self.assertRegex(grant.grant_digest, r"^sha256:[0-9a-f]{64}$")

    def test_command_effect_path_and_expiry_escapes_are_refused_before_execution(self) -> None:
        grant = CapabilityGrant("fixture", ("check:docs",), ("docs",), ("subprocess",), "2020-01-01T00:00:00Z")
        with self.assertRaises(ControlError) as expired:
            grant.authorize(command_id="check:docs", effect="subprocess", paths=["docs/a.md"], now=datetime.now(timezone.utc))
        self.assertEqual("capability.expired", expired.exception.code)
        live = CapabilityGrant("fixture", ("check:docs",), ("docs",), ("subprocess",))
        for kwargs, code in (
            ({"command_id": "check:shell", "effect": "subprocess", "paths": ["docs/a.md"]}, "capability.command-denied"),
            ({"command_id": "check:docs", "effect": "write-generated", "paths": ["docs/a.md"]}, "capability.effect-denied"),
            ({"command_id": "check:docs", "effect": "subprocess", "paths": ["src/a.py"]}, "capability.path-denied"),
        ):
            with self.assertRaises(ControlError) as denied:
                live.authorize(**kwargs)
            self.assertEqual(code, denied.exception.code)
            self.assertEqual(1, len(denied.exception.remediation))
        with self.assertRaises(ControlError) as traversal:
            live.authorize(command_id="check:docs", effect="subprocess", paths=["../docs/a.md"])
        self.assertEqual("capability.path-invalid", traversal.exception.code)

    def test_verification_executor_records_one_grant_and_denies_tampered_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capability-exec-") as directory:
            catalog = CheckCatalog("fixture", (CheckDefinition("docs:test", (sys.executable, "-c", "pass"), ("docs/**",), "low", 1),))
            plan = select_checks(catalog, "a" * 40, ["docs/a.md"])
            attempts = execute_plan(Path(directory), catalog, plan)
            self.assertRegex(attempts[0]["capability_digest"], r"^sha256:[0-9a-f]{64}$")
            tampered = copy.deepcopy(plan)
            tampered["selected"][0]["matched_paths"] = ["src/escape.py"]
            with self.assertRaises(ControlError) as denied:
                execute_plan(Path(directory), catalog, tampered)
            self.assertEqual("capability.path-denied", denied.exception.code)


class ProvenanceAndTelemetryTests(unittest.TestCase):
    def test_provenance_binds_output_without_copying_payload_into_envelope(self) -> None:
        with tempfile.TemporaryDirectory(prefix="provenance-") as directory:
            result = {"outcome": "succeeded", "code": "fixture.ok", "data": {"private": "payload"}}
            attached = attach(result, operation_id="fixture", root=Path(directory))
            self.assertTrue(validates(attached))
            envelope = attached["provenance"]
            self.assertNotIn("private", envelope)
            self.assertNotIn("payload", json.dumps(envelope))
            changed = copy.deepcopy(attached)
            changed["data"]["private"] = "changed"
            self.assertFalse(validates(changed))

    def test_telemetry_is_minimal_append_only_and_metrics_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="telemetry-") as directory:
            root = Path(directory)
            sink = TelemetrySink(root)
            first = sink.emit(command_id="verify", outcome="not-qualified", result_code="verification.failed", duration_ms=12.5, remediation_count=1)
            second = sink.emit(command_id="recover", outcome="succeeded", result_code="lifecycle.recovered", duration_ms=4, remediation_count=0)
            self.assertNotEqual(first, second)
            events, malformed = sink.events()
            self.assertEqual(0, malformed)
            self.assertEqual(2, len(events))
            self.assertFalse(FORBIDDEN_EVENT_FIELDS.intersection(events[0]))
            report = sink.report()
            self.assertEqual(0, report["ambiguous_refusal_count"])
            self.assertEqual({"attempts": 1, "succeeded": 1}, report["recovery"])
            self.assertEqual(1, report["verification"]["attempts"])

    def test_malformed_event_is_counted_and_sink_failure_never_blocks_operation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="telemetry-malformed-") as directory:
            root = Path(directory)
            sink = TelemetrySink(root)
            broken = root / ".local-codex/control-plane/telemetry/20261015/broken.json"
            broken.parent.mkdir(parents=True)
            broken.write_text("{broken", encoding="utf-8")
            self.assertEqual(1, sink.report()["malformed_event_count"])

            class BrokenSink:
                @staticmethod
                def emit(**event: object) -> Path:
                    raise OSError("disk unavailable")

            self.assertFalse(emit_safely(BrokenSink(), command_id="status", outcome="succeeded", result_code="ok", duration_ms=1, remediation_count=0))


class HarnessEvaluationTests(unittest.TestCase):
    def test_tracked_multi_turn_corpus_passes_all_safety_and_friction_budgets(self) -> None:
        corpus = json.loads((HERE / "evals/scenarios.json").read_text(encoding="utf-8"))
        report = evaluate_corpus(corpus)
        self.assertEqual("passed", report["status"])
        self.assertEqual(7, report["passed_count"])

    def test_safety_failure_cannot_be_offset_by_short_turn_count(self) -> None:
        scenario = {
            "id": "unsafe-shortcut",
            "turns": [{"command_id": "request-approval", "outcome": "refused", "code": "bad", "remediation_count": 0}],
            "assertions": {"max_turns": 1, "max_aggregate_readiness": 0, "expected_final_code": "bad"},
        }
        result = evaluate_scenario(scenario)
        self.assertEqual("failed", result["status"])
        self.assertGreaterEqual(len(result["violations"]), 2)

    def test_extra_full_readiness_and_privacy_fields_fail_deterministically(self) -> None:
        scenario = {
            "id": "rigid-and-sensitive",
            "turns": [{"command_id": "verify", "outcome": "succeeded", "code": "ok", "remediation_count": 0, "aggregate_readiness": True, "prompt": "secret"}],
            "assertions": {"max_turns": 1, "max_aggregate_readiness": 0, "expected_final_code": "ok"},
        }
        result = evaluate_scenario(scenario)
        self.assertEqual("failed", result["status"])
        self.assertTrue(any("aggregate-readiness" in value for value in result["violations"]))
        self.assertTrue(any("privacy-forbidden" in value for value in result["violations"]))


if __name__ == "__main__":
    unittest.main()
