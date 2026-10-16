"""Exact Git candidate adapter with repository-path confinement."""

from __future__ import annotations

import hashlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from contracts import ControlError


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class GitCandidateAdapter:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def _run(self, *arguments: str, text: bool = True) -> subprocess.CompletedProcess:
        environment = dict(os.environ)
        environment["GIT_CONFIG_NOSYSTEM"] = "1"
        environment["GIT_NO_REPLACE_OBJECTS"] = "1"
        return subprocess.run(
            ["git", "-c", "core.hooksPath=NUL" if os.name == "nt" else "core.hooksPath=/dev/null", *arguments],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=text,
            encoding="utf-8" if text else None,
            errors="replace" if text else None,
            env=environment,
        )

    def _required(self, *arguments: str) -> str:
        completed = self._run(*arguments)
        if completed.returncode:
            raise ControlError(
                "git.command-failed",
                "Git could not establish the required candidate fact.",
                {"arguments": list(arguments), "stderr": completed.stderr.strip()},
                ["Correct the repository state and retry status or submission."],
            )
        return completed.stdout.strip()

    def current_identity(self) -> dict[str, str]:
        root = Path(self._required("rev-parse", "--show-toplevel")).resolve()
        if root != self.root:
            raise ControlError(
                "git.repository-mismatch",
                "Git resolved a different repository root.",
                {"expected": str(self.root), "actual": str(root)},
                ["Run the command from the packet's canonical worktree."],
            )
        branch = self._required("branch", "--show-current")
        if not branch:
            raise ControlError(
                "git.detached-head",
                "A live work claim requires a named branch.",
                {},
                ["Switch to the intended existing work branch and retry."],
            )
        return {"repository": self.root.as_posix(), "branch": branch, "head": self._required("rev-parse", "HEAD")}

    def stable_identity(self, candidate: str) -> dict[str, str]:
        identity = self.current_identity()
        exact_candidate = self._required("rev-parse", f"{candidate}^{{commit}}")
        if exact_candidate != identity["head"]:
            raise ControlError(
                "git.stale-candidate",
                "Verification must run against the submitted exact HEAD.",
                {"candidate": exact_candidate, "head": identity["head"]},
                ["Restore the submitted candidate in a clean worktree and run fresh verification."],
            )
        status = self._required("status", "--porcelain=v1", "--untracked-files=all")
        if status:
            raise ControlError(
                "git.dirty-worktree",
                "Verification requires a clean worktree so inputs remain fixed.",
                {"status_lines": status.splitlines()},
                ["Commit or safely relocate the changes, then run fresh verification."],
            )
        return {**identity, "candidate": exact_candidate}

    def is_strict_descendant(self, ancestor: str, descendant: str) -> bool:
        exact_ancestor = self._required("rev-parse", f"{ancestor}^{{commit}}")
        exact_descendant = self._required("rev-parse", f"{descendant}^{{commit}}")
        if exact_ancestor == exact_descendant:
            return False
        return self._run("merge-base", "--is-ancestor", exact_ancestor, exact_descendant).returncode == 0

    @staticmethod
    def _normalized(relative: str) -> str:
        path = PurePosixPath(relative.replace("\\", "/"))
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise ControlError(
                "scope.invalid-path",
                "Candidate paths must be normalized repository-relative paths.",
                {"path": relative},
                ["Remove absolute or parent-traversal paths."],
            )
        return path.as_posix()

    @classmethod
    def _allowed(cls, path: str, scopes: list[str]) -> bool:
        candidate = cls._normalized(path)
        return any(candidate == cls._normalized(scope) or candidate.startswith(cls._normalized(scope).rstrip("/") + "/") for scope in scopes)

    def _blob_hash(self, candidate: str, relative: str) -> str:
        normalized = self._normalized(relative)
        completed = self._run("show", f"{candidate}:{normalized}", text=False)
        if completed.returncode:
            raise ControlError(
                "git.input-missing",
                "A declared submission input is absent from the candidate.",
                {"candidate": candidate, "input": normalized},
                ["Commit the complete declared input set, then submit again."],
            )
        return hashlib.sha256(completed.stdout).hexdigest()

    def submission(
        self,
        *,
        base_revision: str,
        candidate: str,
        allowed_paths: list[str],
        declared_inputs: list[str],
    ) -> dict[str, Any]:
        identity = self.stable_identity(candidate)
        exact_candidate = identity["candidate"]
        ancestry = self._run("merge-base", "--is-ancestor", base_revision, exact_candidate)
        if ancestry.returncode:
            raise ControlError(
                "git.forked-candidate",
                "The candidate is not a descendant of the claimed base revision.",
                {"base_revision": base_revision, "candidate": exact_candidate},
                ["Reconcile ancestry on the intended branch and create a descendant candidate."],
            )
        changed_output = self._required("diff", "--name-only", "--diff-filter=ACMDRTUXB", base_revision, exact_candidate)
        changed = sorted({self._normalized(line) for line in changed_output.splitlines() if line.strip()})
        outside = [path for path in changed if not self._allowed(path, allowed_paths)]
        if outside:
            raise ControlError(
                "git.scope-escape",
                "The candidate changes paths outside the packet's declared scope.",
                {"outside_paths": outside, "allowed_paths": allowed_paths},
                ["Move unrelated changes to another packet or refine this packet within the CAP boundary."],
            )
        inputs = sorted({self._normalized(path) for path in declared_inputs if path})
        return {
            "schema_version": "1.0",
            "repository": identity["repository"],
            "branch": identity["branch"],
            "base_revision": base_revision,
            "candidate": exact_candidate,
            "changed_paths": changed,
            "declared_inputs": [{"path": path, "sha256": self._blob_hash(exact_candidate, path)} for path in inputs],
            "recorded_at": utc_timestamp(),
        }
