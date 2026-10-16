#!/usr/bin/env python3
"""Focused tests for reusable exact-file edit coordination."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from contracts import ControlError  # noqa: E402
from file_leases import FileLeaseStore, canonical_file  # noqa: E402
from financial_academy_editing import FinancialAcademyEditingService  # noqa: E402
from planning_model import load_artifacts  # noqa: E402
from store import normalize_resolved_path  # noqa: E402


class Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.value

    def advance(self, minutes: int) -> None:
        self.value += timedelta(minutes=minutes)


def acquire(store: FileLeaseStore, *, owner: str, path: str, work: str = "TASK-1", unit: str = "GROUP-1", claim: str | None = None, minutes: int = 15) -> dict:
    return store.acquire(unit_id=unit, work_id=work, owner=owner, claim_id=claim or f"claim-{owner}", paths=[path], lease_minutes=minutes)


class FileLeaseCoreTests(unittest.TestCase):
    def fixture(self, directory: str, clock: Clock | None = None) -> tuple[Path, FileLeaseStore]:
        root = Path(directory)
        (root / "src").mkdir(parents=True)
        (root / "src/a.py").write_text("a", encoding="utf-8")
        (root / "src/b.py").write_text("b", encoding="utf-8")
        return root, FileLeaseStore(root, clock=clock or Clock())

    def test_different_files_are_concurrent_and_reads_need_no_lease(self) -> None:
        with tempfile.TemporaryDirectory(prefix="file-leases-") as directory:
            _root, store = self.fixture(directory)
            acquire(store, owner="one", path="src/a.py")
            acquire(store, owner="two", path="src/b.py", work="TASK-2", unit="GROUP-2")
            status = store.status()["data"]
            self.assertEqual(2, len(status["leases"]))
            self.assertFalse(status["reads_require_lease"])

    def test_case_separator_and_relative_aliases_share_one_key(self) -> None:
        with tempfile.TemporaryDirectory(prefix="file-alias-") as directory:
            root, store = self.fixture(directory)
            acquire(store, owner="one", path="./src/A.py")
            with self.assertRaises(ControlError) as conflict:
                acquire(store, owner="two", path="src\\a.py", work="TASK-2")
            self.assertEqual("edit.lease-contended", conflict.exception.code)
            self.assertEqual(canonical_file(root, "src/a.py")[1], canonical_file(root, "SRC/A.PY")[1])

    def test_multi_file_acquisition_is_all_or_nothing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="file-atomic-") as directory:
            _root, store = self.fixture(directory)
            acquire(store, owner="one", path="src/b.py")
            with self.assertRaises(ControlError):
                store.acquire(unit_id="GROUP-2", work_id="TASK-2", owner="two", claim_id="claim-two", paths=["src/a.py", "src/b.py"])
            self.assertEqual([], store.status(path="src/a.py")["data"]["leases"])
            self.assertEqual(1, len(store.status(path="src/b.py")["data"]["leases"]))

    def test_live_owner_cannot_be_recovered_and_expiry_preserves_lineage(self) -> None:
        clock = Clock()
        with tempfile.TemporaryDirectory(prefix="file-recovery-") as directory:
            _root, store = self.fixture(directory, clock)
            first = acquire(store, owner="one", path="src/a.py", minutes=1)["data"]["lease"]
            with self.assertRaises(ControlError) as live:
                store.acquire(unit_id="GROUP-2", work_id="TASK-2", owner="two", claim_id="claim-two", paths=["src/a.py"], recovery=True)
            self.assertEqual("edit.lease-contended", live.exception.code)
            clock.advance(2)
            recovered = store.acquire(unit_id="GROUP-2", work_id="TASK-2", owner="two", claim_id="claim-two", paths=["src/a.py"], recovery=True)
            self.assertEqual([first["lease_id"]], recovered["data"]["lease"]["recovered_from"])
            state = json.loads(store.path.read_text(encoding="utf-8"))
            self.assertEqual(["lease-acquired", "lease-recovered"], [item["type"] for item in state["history"]])

    def test_recovery_requires_the_expired_lease_complete_path_set(self) -> None:
        clock = Clock()
        with tempfile.TemporaryDirectory(prefix="file-recovery-set-") as directory:
            _root, store = self.fixture(directory, clock)
            original = store.acquire(unit_id="GROUP-1", work_id="TASK-1", owner="one", claim_id="claim-one", paths=["src/a.py", "src/b.py"], lease_minutes=1)["data"]["lease"]
            clock.advance(2)
            with self.assertRaises(ControlError) as partial:
                store.acquire(unit_id="GROUP-2", work_id="TASK-2", owner="two", claim_id="claim-two", paths=["src/a.py"], recovery=True)
            self.assertEqual("edit.recovery-path-set-mismatch", partial.exception.code)
            self.assertEqual(original["lease_id"], store.status(path="src/b.py")["data"]["leases"][0]["lease_id"])
            recovered = store.acquire(unit_id="GROUP-2", work_id="TASK-2", owner="two", claim_id="claim-two", paths=["src/a.py", "src/b.py"], recovery=True)
            self.assertEqual([original["lease_id"]], recovered["data"]["lease"]["recovered_from"])

    def test_intent_is_visible_but_nonblocking_and_release_is_prompt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="file-intent-") as directory:
            _root, store = self.fixture(directory)
            store.announce(unit_id="GROUP-1", work_id="TASK-1", owner="one", claim_id="claim-one", paths=["src/a.py"])
            lease = acquire(store, owner="two", path="src/a.py", work="TASK-2")["data"]["lease"]
            self.assertEqual(1, len(store.status()["data"]["leases"]))
            store.release(lease_id=lease["lease_id"], owner="two", claim_id="claim-two")
            self.assertEqual([], store.status()["data"]["leases"])

    def test_invalid_broad_paths_durations_and_owner_are_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="file-denial-") as directory:
            _root, store = self.fixture(directory)
            for path in ("src", "../escape.py"):
                with self.assertRaises(ControlError):
                    acquire(store, owner="one", path=path)
            with self.assertRaises(ControlError) as duration:
                store.acquire(unit_id="G", work_id="T", owner="one", claim_id="c", paths=["src/a.py"], lease_minutes=121)
            self.assertEqual("edit.duration-invalid", duration.exception.code)
            lease = acquire(store, owner="one", path="src/a.py")["data"]["lease"]
            with self.assertRaises(ControlError) as owner:
                store.renew(lease_id=lease["lease_id"], owner="two", claim_id="claim-two")
            self.assertEqual("edit.owner-mismatch", owner.exception.code)

    def test_duplicate_paths_stale_revision_and_malformed_state_are_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="file-state-denial-") as directory:
            _root, store = self.fixture(directory)
            with self.assertRaises(ControlError) as duplicate:
                store.acquire(unit_id="G", work_id="T", owner="one", claim_id="c", paths=["src/a.py", "./SRC/A.py"])
            self.assertEqual("edit.paths-duplicate", duplicate.exception.code)
            first = acquire(store, owner="one", path="src/a.py")
            with self.assertRaises(ControlError) as stale:
                store.announce(unit_id="G", work_id="T", owner="one", claim_id="c", paths=["src/b.py"], expected_revision=first["state_revision"] - 1)
            self.assertEqual("edit.revision-conflict", stale.exception.code)
            store.path.write_text("{not-json", encoding="utf-8")
            with self.assertRaises(ControlError) as malformed:
                store.status()
            self.assertEqual("edit.state-malformed", malformed.exception.code)

    def test_intent_expiry_and_state_payload_minimization(self) -> None:
        clock = Clock()
        with tempfile.TemporaryDirectory(prefix="file-intent-expiry-") as directory:
            _root, store = self.fixture(directory, clock)
            result = store.announce(unit_id="GROUP-1", work_id="TASK-1", owner="robot-label", claim_id="claim-one", paths=["src/a.py"], minutes=1)
            self.assertEqual(result["data"]["intent"]["intent_id"], next(iter(json.loads(store.path.read_text(encoding="utf-8"))["intents"])))
            raw = store.path.read_text(encoding="utf-8")
            for forbidden in ("file contents", "prompt text", "reviewer@example.com", "credential"):
                self.assertNotIn(forbidden, raw)
            clock.advance(2)
            self.assertEqual([], store.status()["data"]["intents"])

    def test_two_processes_cannot_acquire_the_same_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="file-race-") as directory:
            root, _store = self.fixture(directory)
            commands = [[sys.executable, str(Path(__file__)), "--worker", str(root), owner] for owner in ("one", "two")]
            processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8") for command in commands]
            outputs = [process.communicate(timeout=10) for process in processes]
            diagnostics = [
                {"returncode": process.returncode, "stdout": stdout, "stderr": stderr}
                for process, (stdout, stderr) in zip(processes, outputs, strict=True)
            ]
            self.assertTrue(all(item["returncode"] == 0 and item["stdout"] for item in diagnostics), diagnostics)
            results = [json.loads(item["stdout"]) for item in diagnostics]
            self.assertEqual(1, sum(item["outcome"] == "succeeded" for item in results), results)
            self.assertEqual(1, sum(item["code"] == "edit.lease-contended" for item in results), results)

    @unittest.skipUnless(sys.platform == "win32", "Windows device-prefix normalization")
    def test_equivalent_windows_device_prefixes_share_one_resolved_path(self) -> None:
        ordinary = Path(r"C:\repository\work")
        extended = Path(r"\\?\C:\repository\work")
        self.assertEqual(ordinary, normalize_resolved_path(extended))


class FinancialAcademyEditingTests(unittest.TestCase):
    @patch("financial_academy.require_current_package", return_value={})
    @patch("financial_academy.load_store", return_value=(object(), Path("unused")))
    def test_active_packet_authorizes_cap_slice_or_work_lane_but_not_scope_escape(
        self, _load_store: object, _require_current_package: object
    ) -> None:
        relatives = [
            "docs/planning/capabilities/CAP-0003-plan-and-orchestrate-capability-portfolios.md",
            "docs/planning/vertical-slices/SLI-0014-qualify-portfolio-control-plane.md",
            *[f"docs/planning/work-packets/WRK-{number:04d}-" for number in range(17, 23)],
        ]
        with tempfile.TemporaryDirectory(prefix="editing-adapter-") as directory:
            root = Path(directory)
            concrete: list[str] = []
            for relative in relatives:
                if relative.endswith("-"):
                    matches = list((ROOT / Path(relative).parent).glob(Path(relative).name + "*.md"))
                    self.assertEqual(1, len(matches))
                    relative = matches[0].relative_to(ROOT).as_posix()
                concrete.append(relative)
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)
            packet_path = next(root / item for item in concrete if "/WRK-0022-" in item)
            lines = packet_path.read_text(encoding="utf-8").splitlines()
            packet_path.write_text("\n".join("planning_status: active" if line.startswith("planning_status:") else line for line in lines) + "\n", encoding="utf-8")
            service = FinancialAcademyEditingService(root)
            artifacts = {item.identifier: item for item in load_artifacts(root)}
            packet = artifacts["WRK-0022"]
            owner = str(packet.metadata["claimed_by"])
            claim_id = str(packet.metadata["claim_id"])
            for unit in ("CAP-0003", "SLI-0014", "WRK-0022"):
                paths = service._authorize(unit_id=unit, work_id="WRK-0022", owner=owner, claim_id=claim_id, paths=["dev-tools/control-plane/portfolio_harness.py"])
                self.assertEqual(["dev-tools/control-plane/portfolio_harness.py"], paths)
            with self.assertRaises(ControlError) as outside:
                service._authorize(unit_id="CAP-0003", work_id="WRK-0022", owner=owner, claim_id=claim_id, paths=["docs/product/capability-catalog.md"])
            self.assertEqual("edit.path-outside-work-scope", outside.exception.code)
            lease = service.acquire(unit_id="WRK-0022", work_id="WRK-0022", owner=owner, claim_id=claim_id, paths=["dev-tools/control-plane/portfolio_harness.py"])["data"]["lease"]
            renewed = service.renew(lease_id=lease["lease_id"], owner=owner, claim_id=claim_id)
            self.assertEqual("edit.lease-renewed", renewed["code"])
            packet_lines = packet_path.read_text(encoding="utf-8").splitlines()
            packet_path.write_text("\n".join("planning_status: complete" if line.startswith("planning_status:") else line for line in packet_lines) + "\n", encoding="utf-8")
            with self.assertRaises(ControlError) as closed:
                service.renew(lease_id=lease["lease_id"], owner=owner, claim_id=claim_id)
            self.assertEqual("edit.work-claim-mismatch", closed.exception.code)
            released = service.release(lease_id=lease["lease_id"], owner=owner, claim_id=claim_id)
            self.assertEqual("edit.lease-released", released["code"])


def worker(root: Path, owner: str) -> int:
    try:
        result = acquire(FileLeaseStore(root), owner=owner, path="src/a.py", work=f"TASK-{owner}", unit=f"GROUP-{owner}")
    except ControlError as error:
        result = error.as_result()
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        raise SystemExit(worker(Path(sys.argv[2]), sys.argv[3]))
    unittest.main()
