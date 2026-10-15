#!/usr/bin/env python3
"""Focused lifecycle, recovery, Git, portability, and anti-rigidity tests."""

from __future__ import annotations

import copy
import hashlib
import json
import multiprocessing
import os
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PLANNING = HERE.parent / "planning"
for path in (HERE, PLANNING):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from approval_store import empty_store, save_store, store_path  # noqa: E402
from cap_package import approval_fields  # noqa: E402
from contracts import ControlError  # noqa: E402
from engine import ControlPlane  # noqa: E402
from financial_academy import FinancialAcademyAdapter  # noqa: E402
from git_candidate import GitCandidateAdapter  # noqa: E402
from state import (  # noqa: E402
    claim_work,
    recover_work,
    release_work,
    renew_work,
    resume_work,
    submit_work,
)
from store import StateStore, canonical_bytes, confined_path  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class JsonProjection:
    def __init__(self, root: Path, relative_path: str) -> None:
        self.root = root
        self.path = root / relative_path

    @property
    def relative_path(self) -> str:
        return self.path.relative_to(self.root).as_posix()

    def content_sha256(self) -> str:
        return sha(self.path)

    def matches(self, updates: dict[str, Any]) -> bool:
        current = json.loads(self.path.read_text(encoding="utf-8"))
        return all(current.get(key) == value for key, value in updates.items())

    def apply(self, updates: dict[str, Any], expected_sha256: str) -> None:
        if self.content_sha256() != expected_sha256 and not self.matches(updates):
            raise ControlError("fixture.conflict", "projection changed", {}, [])
        current = json.loads(self.path.read_text(encoding="utf-8"))
        current.update(updates)
        self.path.write_bytes(canonical_bytes(current))


class MinimalProjectAdapter:
    """A non-Financial-Academy adapter proving kernel reuse."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.file = root / "work.json"
        self.file.write_bytes(canonical_bytes({"status": "ready", "owner": None}))

    def projection(self, work_id_or_path: str) -> JsonProjection:
        return JsonProjection(self.root, "work.json")

    def require_delivery_authority(self, work_id: str) -> dict[str, Any]:
        return {"approval_stages_checked": ["project"], "allowed_paths": ["src"], "canonical_inputs": []}

    @staticmethod
    def initial_work_state(work_id: str) -> dict[str, Any]:
        from state import new_work

        return new_work(work_id)

    @staticmethod
    def claim_projection_updates(work_id: str, work: dict[str, Any]) -> dict[str, Any]:
        return {"status": "active", "owner": work["claim"]["owner"]}

    @staticmethod
    def submit_projection_updates(work_id: str, work: dict[str, Any]) -> dict[str, Any]:
        return {"status": "verifying"}

    @staticmethod
    def release_projection_updates(work_id: str, work: dict[str, Any]) -> dict[str, Any]:
        return {"status": "ready", "owner": None}


class MinimalCandidateAdapter:
    @staticmethod
    def current_identity() -> dict[str, str]:
        return {"repository": "fixture", "branch": "codex/fixture", "head": "a" * 40}

    @staticmethod
    def stable_identity(candidate: str) -> dict[str, str]:
        return {"repository": "fixture", "branch": "codex/fixture", "head": candidate, "candidate": candidate}

    @staticmethod
    def is_strict_descendant(ancestor: str, descendant: str) -> bool:
        return ancestor != descendant

    @staticmethod
    def submission(**kwargs: Any) -> dict[str, Any]:
        return {"candidate": "b" * 40, "changed_paths": ["src/value.txt"], "recorded_at": "2026-10-15T12:00:00Z"}


def concurrent_worker(root_text: str, queue: Any) -> None:
    root = Path(root_text)
    projection = JsonProjection(root, "work.json")
    store = StateStore(root, lambda _path: projection)
    try:
        def transition(envelope: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
            if envelope["revision"] != 0:
                raise ControlError("state.version-conflict", "stale", {}, ["retry"])
            successor = copy.deepcopy(envelope)
            successor["revision"] = 1
            successor["work_items"]["WORK-1"] = {"state": "active"}
            time.sleep(0.1)
            return successor, {"status": "active"}

        store.mutate(projection, transition)
        queue.put("succeeded")
    except ControlError as error:
        queue.put(error.code)


class KernelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)
        self.clock = lambda: self.now
        from state import new_work

        self.ready = new_work("WORK-1")

    def test_claim_resume_renew_release_short_path(self) -> None:
        active = claim_work(self.ready, owner="agent", base_revision="a" * 40, branch="codex/test", lease_minutes=30, expected_revision=0, clock=self.clock)
        self.assertEqual("active", active["state"])
        self.assertEqual("continue work, renew if needed, then submit the exact candidate", resume_work(active, owner="agent", claim_id=active["claim"]["claim_id"], clock=self.clock)["next_action"])
        renewed = renew_work(active, owner="agent", claim_id=active["claim"]["claim_id"], lease_minutes=60, expected_revision=1, clock=self.clock)
        released = release_work(renewed, owner="agent", claim_id=renewed["claim"]["claim_id"], expected_revision=2, clock=self.clock)
        self.assertEqual("released", released["state"])
        self.assertEqual(["claimed", "lease-renewed", "released"], [event["type"] for event in released["history"]])

    def test_version_conflict_and_active_owner_refuse_with_remediation(self) -> None:
        active = claim_work(self.ready, owner="agent", base_revision="a" * 40, branch="codex/test", lease_minutes=30, expected_revision=0, clock=self.clock)
        with self.assertRaises(ControlError) as conflict:
            renew_work(active, owner="agent", claim_id=active["claim"]["claim_id"], lease_minutes=30, expected_revision=0, clock=self.clock)
        self.assertEqual("state.version-conflict", conflict.exception.code)
        self.assertTrue(conflict.exception.remediation)
        with self.assertRaises(ControlError) as displaced:
            recover_work(active, owner="other", base_revision="a" * 40, branch="codex/test", lease_minutes=30, expected_revision=1, clock=self.clock)
        self.assertEqual("recovery.active-owner", displaced.exception.code)

    def test_expired_claim_recovers_without_rewriting_history(self) -> None:
        active = claim_work(self.ready, owner="agent", base_revision="a" * 40, branch="codex/test", lease_minutes=1, expected_revision=0, clock=self.clock)
        self.now += timedelta(minutes=2)
        with self.assertRaises(ControlError) as expired:
            resume_work(active, owner="agent", claim_id=active["claim"]["claim_id"], clock=self.clock)
        self.assertEqual("lease.expired", expired.exception.code)
        recovered = recover_work(active, owner="other", base_revision="a" * 40, branch="codex/test", lease_minutes=30, expected_revision=1, clock=self.clock)
        self.assertEqual(active["claim"]["claim_id"], recovered["claim"]["recovered_from"])
        self.assertEqual(["claimed", "claim-recovered"], [event["type"] for event in recovered["history"]])

    def test_submit_is_exact_fact_input_not_test_or_approval_authority(self) -> None:
        active = claim_work(self.ready, owner="agent", base_revision="a" * 40, branch="codex/test", lease_minutes=30, expected_revision=0, clock=self.clock)
        submitted = submit_work(active, owner="agent", claim_id=active["claim"]["claim_id"], submission={"candidate": "b" * 40, "changed_paths": []}, expected_revision=1, clock=self.clock)
        self.assertEqual("submitted", submitted["state"])
        self.assertNotIn("approval", submitted["submission"])
        self.assertNotIn("checks", submitted["submission"])


class StoreAndReuseTests(unittest.TestCase):
    def test_generic_adapter_uses_core_without_repository_vocabulary(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generic-control-plane-") as directory:
            root = Path(directory)
            project = MinimalProjectAdapter(root)
            plane = ControlPlane(project, MinimalCandidateAdapter(), StateStore(root, project.projection))
            result = plane.claim("WORK-1", owner="agent", lease_minutes=10)
            self.assertEqual("claim.created", result["code"])
            self.assertEqual(["project"], result["data"]["approval_stages_checked"])
            self.assertFalse(result["data"]["lower_level_approval_required"])
            self.assertFalse(result["data"]["mandatory_full_suite"])

    def test_interrupted_publication_recovers_idempotently(self) -> None:
        with tempfile.TemporaryDirectory(prefix="control-plane-journal-") as directory:
            root = Path(directory)
            project = MinimalProjectAdapter(root)
            projection = project.projection("WORK-1")
            store = StateStore(root, project.projection)

            def transition(envelope: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
                successor = copy.deepcopy(envelope)
                successor["revision"] = 1
                successor["work_items"]["WORK-1"] = {"state": "active"}
                return successor, {"status": "active", "owner": "agent"}

            with self.assertRaisesRegex(OSError, "injected"):
                store.mutate(projection, transition, fault_after="state")
            envelope, recovered = store.read()
            self.assertTrue(recovered)
            self.assertEqual(1, envelope["revision"])
            self.assertEqual("active", json.loads(project.file.read_text(encoding="utf-8"))["status"])
            self.assertFalse(store.journal_path.exists())

    def test_two_processes_cannot_both_apply_same_revision(self) -> None:
        with tempfile.TemporaryDirectory(prefix="control-plane-race-") as directory:
            root = Path(directory)
            (root / "work.json").write_bytes(canonical_bytes({"status": "ready"}))
            context = multiprocessing.get_context("spawn")
            queue = context.Queue()
            processes = [context.Process(target=concurrent_worker, args=(str(root), queue)) for _ in range(2)]
            for process in processes:
                process.start()
            for process in processes:
                process.join(15)
                self.assertEqual(0, process.exitcode)
            outcomes = sorted(queue.get(timeout=2) for _ in range(2))
            self.assertEqual(["state.version-conflict", "succeeded"], outcomes)

    def test_path_confinement_rejects_absolute_and_parent_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="control-plane-path-") as directory:
            root = Path(directory)
            for unsafe in ("../escape.json", str((root.parent / "escape.json").resolve())):
                with self.subTest(path=unsafe):
                    with self.assertRaises(ControlError) as refused:
                        confined_path(root, unsafe)
                    self.assertEqual("path.outside-repository", refused.exception.code)


class FinancialAcademyIntegrationTests(unittest.TestCase):
    def git(self, root: Path, *arguments: str) -> str:
        completed = subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True, text=True, encoding="utf-8")
        return completed.stdout.strip()

    def write(self, root: Path, relative: str, text: str) -> Path:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")
        return path

    def fixture(self, directory: str) -> tuple[Path, ControlPlane]:
        root = Path(directory)
        self.git(root, "init", "--initial-branch=codex/fixture")
        self.git(root, "config", "user.name", "Fixture")
        self.git(root, "config", "user.email", "fixture@example.invalid")
        self.write(root, ".gitignore", "/.local-codex/\n")
        self.write(root, "AGENTS.md", "# Fixture")
        self.write(root, "docs/README.md", "# Fixture docs")
        self.write(root, "src/value.txt", "base")
        self.write(root, "docs/planning/register.md", "# Register")
        cap = self.write(root, "docs/planning/capabilities/CAP-0001-fixture.md", """
---
id: CAP-0001
kind: capability
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0001"]
---
# Capability: Fixture
## Outcome
A reusable controller can deliver one work item.
## Scope
Local fixture only.
## Decision Gates and Constraints
No external actions.
## Proposed Vertical Slices
| Slice ID | Observable increment | Dependencies | Material boundary | Status |
| --- | --- | --- | --- | --- |
| SLI-0001 | Deliver fixture | none | remote work | ready |
## Capability Acceptance
One bounded item completes.
## Risks and Non-Goals
No hosted service.
""")
        self.write(root, "docs/planning/vertical-slices/SLI-0001-fixture.md", """
---
id: SLI-0001
kind: vertical-slice
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: CAP-0001
depends_on: []
decision_gates: []
---
# Vertical Slice: Fixture
""")
        self.write(root, "docs/planning/work-packets/WRK-0001-fixture.md", """
---
id: WRK-0001
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: SLI-0001
capability: CAP-0001
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["src", "docs/planning/work-packets/WRK-0001-fixture.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---
# Work Packet: Fixture
""")
        self.git(root, "add", ".")
        self.git(root, "commit", "-m", "fixture base")
        local = empty_store()
        local["records"].append(
            {
                "subject": "CAP-0001",
                "stage": "capability",
                "decision": "approved",
                "actor_label": "fixture-authority",
                "decided_at": "2026-10-15",
                "authority": "fixture",
                "recorded_at": "2026-10-15T12:00:00Z",
                **approval_fields(root, "CAP-0001"),
            }
        )
        save_store(store_path(root), local)
        project = FinancialAcademyAdapter(root)
        return root, ControlPlane(project, GitCandidateAdapter(root), StateStore(root, project.projection))

    def test_minimal_claim_submit_path_has_one_approval_and_no_full_suite_gate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="faa-control-plane-") as directory:
            root, plane = self.fixture(directory)
            claimed = plane.claim("WRK-0001", owner="agent", lease_minutes=30)
            self.assertEqual(["capability"], claimed["data"]["approval_stages_checked"])
            self.assertFalse(claimed["data"]["lower_level_approval_required"])
            self.assertFalse(claimed["data"]["mandatory_full_suite"])
            claim_id = claimed["data"]["claim"]["claim_id"]
            self.write(root, "src/value.txt", "candidate")
            self.git(root, "add", ".")
            self.git(root, "commit", "-m", "fixture candidate")
            submitted = plane.submit("WRK-0001", owner="agent", claim_id=claim_id)
            self.assertEqual("submission.recorded", submitted["code"])
            self.assertEqual(self.git(root, "rev-parse", "HEAD"), submitted["data"]["submission"]["candidate"])

    def test_dirty_and_out_of_scope_candidates_are_actionable_denials(self) -> None:
        with tempfile.TemporaryDirectory(prefix="faa-control-plane-denial-") as directory:
            root, plane = self.fixture(directory)
            claimed = plane.claim("WRK-0001", owner="agent", lease_minutes=30)
            claim_id = claimed["data"]["claim"]["claim_id"]
            self.write(root, "src/value.txt", "dirty")
            with self.assertRaises(ControlError) as dirty:
                plane.submit("WRK-0001", owner="agent", claim_id=claim_id)
            self.assertEqual("git.dirty-worktree", dirty.exception.code)
            self.assertTrue(dirty.exception.remediation)
            self.git(root, "add", ".")
            self.git(root, "commit", "-m", "in-scope candidate")
            self.write(root, "outside.txt", "outside")
            self.git(root, "add", ".")
            self.git(root, "commit", "-m", "outside candidate")
            with self.assertRaises(ControlError) as outside:
                plane.submit("WRK-0001", owner="agent", claim_id=claim_id)
            self.assertEqual("git.scope-escape", outside.exception.code)
            self.assertIn("outside.txt", outside.exception.observed["outside_paths"])


if __name__ == "__main__":
    multiprocessing.freeze_support()
    unittest.main()
