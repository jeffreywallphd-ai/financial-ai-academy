#!/usr/bin/env python3
"""Validate public planning artifacts, references, lifecycle, and ownership."""

from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from pathlib import Path

from approval_store import ApprovalStoreError, load_store, require_decision

from planning_model import (
    ARTIFACT_LOCATIONS,
    DATE_RE,
    ID_RE,
    TIMESTAMP_RE,
    Artifact,
    as_list,
    as_text,
    frontmatter_at_revision,
    git_output,
    is_present,
    load_artifacts,
    normalize_repo_path,
    repository_root,
    scopes_overlap,
)


STATUSES = {
    "captured", "shaping", "decision-blocked", "ready", "active",
    "verifying", "complete", "superseded",
}
REQUIRED_FIELDS = {
    "capability": {
        "id", "kind", "planning_status", "authority", "owner", "updated",
        "parent", "depends_on", "decision_gates",
    },
    "decision-request": {
        "id", "kind", "planning_status", "authority", "owner", "updated",
        "parent", "depends_on", "decision_gates", "decision_record",
    },
    "vertical-slice": {
        "id", "kind", "planning_status", "authority", "owner", "updated",
        "parent", "depends_on", "decision_gates",
    },
    "work-packet": {
        "id", "kind", "planning_status", "authority", "owner", "updated",
        "parent", "capability", "depends_on", "decision_gates",
        "parallel_safe_with", "write_scope", "generated_artifacts",
        "base_revision", "claim_id", "claimed_by", "claimed_at",
    },
}
LOCAL_GATES = {
    "capability": (({"ready", "active", "verifying", "complete"}, "capability"),),
    "decision-request": (({"ready", "verifying", "complete"}, "decision"),),
    "vertical-slice": (
        ({"ready", "active", "verifying", "complete"}, "selection"),
        ({"complete"}, "completion"),
    ),
    "work-packet": (
        ({"ready", "active", "verifying", "complete"}, "planning"),
        ({"active", "verifying", "complete"}, "implementation"),
    ),
}
ALLOWED_TRANSITIONS = {
    "captured": {"captured", "shaping", "superseded"},
    "shaping": {"shaping", "decision-blocked", "ready", "superseded"},
    "decision-blocked": {"decision-blocked", "shaping", "ready", "superseded"},
    "ready": {"ready", "shaping", "decision-blocked", "active", "superseded"},
    "active": {"active", "ready", "decision-blocked", "verifying", "superseded"},
    "verifying": {"verifying", "active", "complete", "superseded"},
    "complete": {"complete", "superseded"},
    "superseded": {"superseded"},
}


def error(errors: list[str], artifact: Artifact, message: str) -> None:
    errors.append(f"{artifact.relative_path}: {message}")


def validate_identity(artifact: Artifact, errors: list[str]) -> None:
    data = artifact.metadata
    missing = REQUIRED_FIELDS.get(artifact.kind, set()) - set(data)
    for field in sorted(missing):
        error(errors, artifact, f"missing metadata field {field}")
    forbidden = [
        field for field in data
        if field.endswith(("_approval", "_approved_by", "_approved_at"))
        or field == "implementation_authority"
    ]
    for field in sorted(forbidden):
        error(errors, artifact, f"local-only approval metadata must not be tracked: {field}")
    if re.search(
        r"^## Approval History\s*$",
        artifact.path.read_text(encoding="utf-8"),
        re.MULTILINE,
    ):
        error(errors, artifact, "approval history must remain in the ignored local ledger")

    match = ID_RE.match(artifact.identifier)
    if not match:
        error(errors, artifact, "id must match CAP|DEC|SLI|WRK-####")
        return
    expected_prefix = next(
        prefix for prefix, (_directory, kind) in ARTIFACT_LOCATIONS.items()
        if kind == artifact.kind
    ) if artifact.kind in REQUIRED_FIELDS else ""
    if match.group(1) != expected_prefix:
        error(errors, artifact, f"id prefix does not match kind {artifact.kind}")
    if not artifact.path.name.startswith(artifact.identifier + "-"):
        error(errors, artifact, "filename must begin with the artifact id and a dash")
    if artifact.status not in STATUSES:
        error(errors, artifact, f"invalid planning_status {artifact.status!r}")
    if not DATE_RE.match(as_text(data.get("updated"))):
        error(errors, artifact, "updated must be YYYY-MM-DD")


def validate_lifecycle(artifact: Artifact, errors: list[str]) -> None:
    data = artifact.metadata
    status = artifact.status
    if status == "decision-blocked" and not as_list(data.get("decision_gates")):
        error(errors, artifact, "decision-blocked requires at least one decision gate")

    if artifact.kind == "decision-request" and status == "complete":
        if not is_present(data.get("decision_record")):
            error(errors, artifact, "complete decision request requires decision_record")
    elif artifact.kind == "work-packet":
        if status in {"active", "verifying", "complete"}:
            for field in ("base_revision", "claim_id", "claimed_by", "claimed_at"):
                if not is_present(data.get(field)):
                    error(errors, artifact, f"{status} requires {field}")
            if not TIMESTAMP_RE.match(as_text(data.get("claimed_at"))):
                error(errors, artifact, "claimed_at must be an ISO UTC timestamp ending in Z")
            if not as_list(data.get("write_scope")):
                error(errors, artifact, f"{status} requires a non-empty write_scope")
            if as_text(data.get("claimed_by")) != as_text(data.get("owner")):
                error(errors, artifact, "claimed_by must match owner")


def validate_scope(artifact: Artifact, errors: list[str]) -> None:
    if artifact.kind != "work-packet":
        return
    for field in ("write_scope", "generated_artifacts"):
        for declared in as_list(artifact.metadata.get(field)):
            normalized = normalize_repo_path(declared)
            if (
                not normalized
                or normalized.startswith("/")
                or re.match(r"^[A-Za-z]:", normalized)
                or ".." in Path(normalized).parts
                or normalized in {".", "*", "**"}
            ):
                error(errors, artifact, f"unsafe {field} entry {declared!r}")


def decision_readiness(root: Path) -> dict[str, str]:
    path = root / "docs/adr/decision-readiness.md"
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 2 and cells[0] not in {"Area", "---"}:
            result[cells[0]] = cells[1]
    return result


def validate_references(
    root: Path, artifacts: list[Artifact], by_id: dict[str, Artifact], errors: list[str]
) -> None:
    readiness = decision_readiness(root)
    for artifact in artifacts:
        data = artifact.metadata
        parent = as_text(data.get("parent"))
        if artifact.kind in {"capability", "decision-request"}:
            if parent:
                error(errors, artifact, "top-level artifact parent must be null")
        elif artifact.kind == "vertical-slice":
            if parent not in by_id or by_id[parent].kind != "capability":
                error(errors, artifact, "parent must reference an existing capability")
        elif artifact.kind == "work-packet":
            if parent not in by_id or by_id[parent].kind != "vertical-slice":
                error(errors, artifact, "parent must reference an existing vertical slice")
            capability = as_text(data.get("capability"))
            if capability not in by_id or by_id[capability].kind != "capability":
                error(errors, artifact, "capability must reference an existing capability")
            elif parent in by_id and as_text(by_id[parent].metadata.get("parent")) != capability:
                error(errors, artifact, "capability must match the parent slice capability")

        for dependency in as_list(data.get("depends_on")):
            if dependency not in by_id:
                error(errors, artifact, f"unknown dependency {dependency}")
            elif dependency == artifact.identifier:
                error(errors, artifact, "artifact cannot depend on itself")
        for gate in as_list(data.get("decision_gates")):
            if gate.startswith("DEC-"):
                if gate not in by_id or by_id[gate].kind != "decision-request":
                    error(errors, artifact, f"unknown decision request {gate}")
                elif artifact.status in {"ready", "active", "verifying", "complete"} and (
                    by_id[gate].status != "complete"
                    or not is_present(by_id[gate].metadata.get("decision_record"))
                ):
                    error(errors, artifact, f"decision gate {gate} is unresolved")
            elif gate not in readiness:
                error(errors, artifact, f"unknown decision-readiness area {gate!r}")
            elif artifact.status in {"ready", "active", "verifying", "complete"} and readiness[gate] in {
                "proposed", "decision-required"
            }:
                error(errors, artifact, f"decision-readiness gate {gate!r} is {readiness[gate]}")
        for peer in as_list(data.get("parallel_safe_with")):
            if peer not in by_id or by_id[peer].kind != "work-packet":
                error(errors, artifact, f"unknown parallel-safe packet {peer}")
            elif artifact.identifier not in as_list(
                by_id[peer].metadata.get("parallel_safe_with")
            ):
                error(errors, artifact, f"parallel safety with {peer} must be reciprocal")


def validate_dependency_cycles(
    artifacts: list[Artifact], by_id: dict[str, Artifact], errors: list[str]
) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str, trail: list[str]) -> None:
        if identifier in visiting:
            cycle = trail[trail.index(identifier):] + [identifier]
            errors.append("dependency cycle: " + " -> ".join(cycle))
            return
        if identifier in visited:
            return
        visiting.add(identifier)
        artifact = by_id[identifier]
        for dependency in as_list(artifact.metadata.get("depends_on")):
            if dependency in by_id:
                visit(dependency, trail + [dependency])
        visiting.remove(identifier)
        visited.add(identifier)

    for artifact in artifacts:
        if artifact.identifier in by_id:
            visit(artifact.identifier, [artifact.identifier])


def validate_concurrency(artifacts: list[Artifact], errors: list[str]) -> None:
    active = [item for item in artifacts if item.kind == "work-packet" and item.status == "active"]
    for left, right in itertools.combinations(active, 2):
        left_write = as_list(left.metadata.get("write_scope"))
        right_write = as_list(right.metadata.get("write_scope"))
        left_generated = as_list(left.metadata.get("generated_artifacts"))
        right_generated = as_list(right.metadata.get("generated_artifacts"))
        if any((
            scopes_overlap(left_write, right_write),
            scopes_overlap(left_write, right_generated),
            scopes_overlap(left_generated, right_write),
            scopes_overlap(left_generated, right_generated),
        )):
            errors.append(
                f"active write-scope collision: {left.identifier} and {right.identifier}"
            )
        elif right.identifier not in as_list(left.metadata.get("parallel_safe_with")):
            errors.append(
                f"active packets lack reciprocal parallel safety: {left.identifier} and {right.identifier}"
            )


def register_rows(root: Path) -> tuple[dict[str, list[str]], list[str]]:
    path = root / "docs/planning/register.md"
    rows: dict[str, list[str]] = {}
    duplicates: list[str] = []
    if not path.is_file():
        return rows, duplicates
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 4 and ID_RE.match(cells[0]):
            if cells[0] in rows:
                duplicates.append(cells[0])
            rows[cells[0]] = cells
    return rows, duplicates


def validate_register(root: Path, artifacts: list[Artifact], errors: list[str]) -> None:
    rows, duplicates = register_rows(root)
    registered = set(rows)
    expected = {artifact.identifier for artifact in artifacts}
    for identifier in sorted(expected - registered):
        errors.append(f"docs/planning/register.md: missing {identifier}")
    for identifier in sorted(registered - expected):
        errors.append(f"docs/planning/register.md: unknown {identifier}")
    for identifier in sorted(set(duplicates)):
        errors.append(f"docs/planning/register.md: duplicate row for {identifier}")
    by_id = {artifact.identifier: artifact for artifact in artifacts}
    for identifier in sorted(expected & registered):
        cells = rows[identifier]
        if cells[3] != by_id[identifier].status:
            errors.append(
                f"docs/planning/register.md: {identifier} status {cells[3]!r} "
                f"does not match {by_id[identifier].status!r}"
            )
        if len(cells) >= 9:
            if cells[7] != as_text(by_id[identifier].metadata.get("owner")):
                errors.append(f"docs/planning/register.md: {identifier} owner is stale")
            if cells[8] != as_text(by_id[identifier].metadata.get("updated")):
                errors.append(f"docs/planning/register.md: {identifier} updated date is stale")


def validate_transitions(
    root: Path, artifacts: list[Artifact], base_ref: str, errors: list[str]
) -> None:
    for artifact in artifacts:
        previous = frontmatter_at_revision(root, base_ref, artifact.relative_path)
        if previous is None:
            continue
        old = as_text(previous.get("planning_status"))
        if old in ALLOWED_TRANSITIONS and artifact.status not in ALLOWED_TRANSITIONS[old]:
            error(errors, artifact, f"illegal lifecycle transition {old} -> {artifact.status}")
    previous_paths = git_output(
        root,
        ["ls-tree", "-r", "--name-only", base_ref, "--", "docs/planning"],
    ).splitlines()
    current_paths = {artifact.relative_path for artifact in artifacts}
    for relative in previous_paths:
        name = Path(relative).name
        if any(name.startswith(prefix + "-") for prefix in ARTIFACT_LOCATIONS) and name.endswith(".md"):
            if relative not in current_paths:
                errors.append(
                    f"{relative}: planning artifacts must be retained and superseded, not deleted"
                )


def validate_local_gates(root: Path, artifacts: list[Artifact], errors: list[str]) -> None:
    try:
        store, _path = load_store(root, required=True)
    except ApprovalStoreError as exception:
        errors.append(str(exception))
        return
    for artifact in artifacts:
        for statuses, stage in LOCAL_GATES.get(artifact.kind, ()):
            if artifact.status not in statuses:
                continue
            try:
                record = require_decision(store, artifact.identifier, stage)
                if stage == "implementation":
                    raw_scope = record.get("scope")
                    if isinstance(raw_scope, str) and raw_scope.strip().startswith("["):
                        try:
                            raw_scope = json.loads(raw_scope)
                        except json.JSONDecodeError as exception:
                            raise ApprovalStoreError(
                                f"invalid implementation scope for {artifact.identifier}"
                            ) from exception
                    approved_scope = sorted({
                        normalize_repo_path(item)
                        for item in as_list(raw_scope)
                        if normalize_repo_path(item)
                    })
                    packet_scope = sorted({
                        normalize_repo_path(item)
                        for item in as_list(artifact.metadata.get("write_scope"))
                        if normalize_repo_path(item)
                    })
                    if approved_scope != packet_scope:
                        raise ApprovalStoreError(
                            f"approved implementation scope for {artifact.identifier} "
                            "does not match write_scope"
                        )
            except ApprovalStoreError as exception:
                error(errors, artifact, str(exception))


def run(
    root: Path, base_ref: str | None = None, *, require_local_approvals: bool = False
) -> list[str]:
    errors: list[str] = []
    artifacts = load_artifacts(root)
    by_id: dict[str, Artifact] = {}
    for artifact in artifacts:
        validate_identity(artifact, errors)
        if artifact.identifier in by_id:
            errors.append(
                f"duplicate id {artifact.identifier}: {by_id[artifact.identifier].relative_path}, "
                f"{artifact.relative_path}"
            )
        elif artifact.identifier:
            by_id[artifact.identifier] = artifact
        if artifact.kind in REQUIRED_FIELDS:
            validate_lifecycle(artifact, errors)
            validate_scope(artifact, errors)
        else:
            error(errors, artifact, f"invalid kind {artifact.kind!r}")
    validate_references(root, artifacts, by_id, errors)
    validate_dependency_cycles(artifacts, by_id, errors)
    validate_concurrency(artifacts, errors)
    validate_register(root, artifacts, errors)
    if require_local_approvals:
        validate_local_gates(root, artifacts, errors)
    if base_ref:
        validate_transitions(root, artifacts, base_ref, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="repository root")
    parser.add_argument("--base-ref", help="git revision used to validate state transitions")
    parser.add_argument(
        "--require-local-approvals", action="store_true",
        help="require approval evidence from the ignored local ledger",
    )
    args = parser.parse_args()
    try:
        root = (args.root or repository_root()).resolve()
        errors = run(
            root, args.base_ref, require_local_approvals=args.require_local_approvals
        )
    except (OSError, RuntimeError, ValueError) as exception:
        print(f"Planning integrity check could not run: {exception}", file=sys.stderr)
        return 2
    if errors:
        print("Planning integrity check failed:")
        for item in errors:
            print(f"- {item}")
        return 1
    count = len(load_artifacts(root))
    print(f"Planning integrity check passed: {count} artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
