#!/usr/bin/env python3
"""Record and inspect ignored local planning approvals and reviews."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from approval_store import (
    DECISIONS,
    REVIEW_STATES,
    STAGES,
    ApprovalStoreError,
    latest_record,
    load_store,
    save_store,
)
from planning_model import as_list, load_artifacts, repository_root


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


BUNDLE_PREFIX_BY_STAGE = {
    "decision": "DEC",
    "planning": "WRK",
    "implementation": "WRK",
}


def bundle_records(root: Path, args: argparse.Namespace) -> list[dict[str, object]]:
    subjects = list(dict.fromkeys(args.subjects))
    if len(subjects) != len(args.subjects):
        raise ApprovalStoreError("record-bundle subjects must be unique")
    if len(subjects) < 2:
        raise ApprovalStoreError("record-bundle requires at least two subjects")
    prefix = BUNDLE_PREFIX_BY_STAGE[args.stage]
    invalid = [subject for subject in subjects if not subject.startswith(prefix + "-")]
    if invalid:
        raise ApprovalStoreError(
            f"{args.stage} bundles require {prefix}-* subjects: " + ", ".join(invalid)
        )
    if args.scope_from_artifacts != (args.stage == "implementation"):
        raise ApprovalStoreError(
            "implementation bundles require --scope-from-artifacts; other bundles must omit it"
        )

    artifacts = {item.identifier: item for item in load_artifacts(root)}
    if args.stage in {"planning", "implementation"}:
        if not args.bundle_subject or not args.bundle_subject.startswith("SLI-"):
            raise ApprovalStoreError("packet bundles require --bundle-subject SLI-*")
        missing = [subject for subject in subjects if subject not in artifacts]
        if missing:
            raise ApprovalStoreError("work packet artifact not found: " + ", ".join(missing))
        wrong_parent = [
            subject for subject in subjects
            if str(artifacts[subject].metadata.get("parent", "")) != args.bundle_subject
        ]
        if wrong_parent:
            raise ApprovalStoreError(
                f"packet bundle members must belong to {args.bundle_subject}: "
                + ", ".join(wrong_parent)
            )

    bundle_id = str(uuid.uuid4())
    recorded_at = utc_now()
    records: list[dict[str, object]] = []
    for subject in subjects:
        item: dict[str, object] = {
            "subject": subject,
            "stage": args.stage,
            "decision": args.decision,
            "actor_label": args.actor_label.strip(),
            "decided_at": args.decided_at,
            "authority": args.authority.strip(),
            "recorded_at": recorded_at,
            "bundle_id": bundle_id,
            "bundle_size": len(subjects),
        }
        if args.bundle_subject:
            item["bundle_subject"] = args.bundle_subject
        if args.scope_from_artifacts:
            scope = as_list(artifacts[subject].metadata.get("write_scope"))
            if not scope:
                raise ApprovalStoreError(f"{subject} must declare a non-empty write_scope")
            item["scope"] = json.dumps(scope, separators=(",", ":"))
        if args.note:
            item["note"] = args.note.strip()
        records.append(item)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="repository root")
    parser.add_argument("--store", type=Path, help="override local ledger path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    record = subparsers.add_parser("record")
    record.add_argument("--subject", required=True)
    record.add_argument("--stage", choices=sorted(STAGES), required=True)
    record.add_argument("--decision", choices=sorted(DECISIONS), required=True)
    record.add_argument("--actor-label", required=True)
    record.add_argument("--decided-at", required=True)
    record.add_argument("--authority", required=True)
    record.add_argument("--scope")
    record.add_argument("--note")
    record.add_argument("--confirm-human-decision", action="store_true")

    bundle = subparsers.add_parser("record-bundle")
    bundle.add_argument("--subjects", nargs="+", required=True)
    bundle.add_argument("--stage", choices=sorted(BUNDLE_PREFIX_BY_STAGE), required=True)
    bundle.add_argument("--decision", choices=sorted(DECISIONS), required=True)
    bundle.add_argument("--actor-label", required=True)
    bundle.add_argument("--decided-at", required=True)
    bundle.add_argument("--authority", required=True)
    bundle.add_argument("--bundle-subject")
    bundle.add_argument("--scope-from-artifacts", action="store_true")
    bundle.add_argument("--note")
    bundle.add_argument("--confirm-human-decision", action="store_true")

    review = subparsers.add_parser("review")
    review.add_argument("--subject", required=True)
    review.add_argument("--review-type", required=True)
    review.add_argument("--reviewer-label", required=True)
    review.add_argument("--status", choices=sorted(REVIEW_STATES), required=True)
    review.add_argument("--note")
    review.add_argument("--confirm-reviewer-statement", action="store_true")

    show = subparsers.add_parser("show")
    show.add_argument("--subject")
    show.add_argument("--stage", choices=sorted(STAGES))

    args = parser.parse_args()
    try:
        root = (args.root or repository_root()).resolve()
        store, path = load_store(root, args.store)
        if args.command in {"record", "record-bundle"}:
            if not args.confirm_human_decision:
                raise ApprovalStoreError(
                    f"{args.command} requires --confirm-human-decision"
                )
            if args.command == "record-bundle":
                items = bundle_records(root, args)
                store["records"].extend(items)
                output: object = {"bundle": items}
            else:
                item: dict[str, object] = {
                    "subject": args.subject,
                    "stage": args.stage,
                    "decision": args.decision,
                    "actor_label": args.actor_label.strip(),
                    "decided_at": args.decided_at,
                    "authority": args.authority.strip(),
                    "recorded_at": utc_now(),
                }
                if args.scope:
                    item["scope"] = args.scope.strip()
                if args.note:
                    item["note"] = args.note.strip()
                store["records"].append(item)
                output = item
            save_store(path, store)
        elif args.command == "review":
            if not args.confirm_reviewer_statement:
                raise ApprovalStoreError("review requires --confirm-reviewer-statement")
            item = {
                "subject": args.subject,
                "review_type": args.review_type.strip(),
                "reviewer_label": args.reviewer_label.strip(),
                "status": args.status,
                "recorded_at": utc_now(),
            }
            if args.note:
                item["note"] = args.note.strip()
            store["reviews"].append(item)
            save_store(path, store)
            output = item
        else:
            if args.subject and args.stage:
                output = latest_record(store, args.subject, args.stage)
            else:
                records = store["records"]
                if args.subject:
                    records = [item for item in records if item.get("subject") == args.subject]
                output = {"records": records, "reviews": store["reviews"]}
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, RuntimeError, ApprovalStoreError, ValueError) as error:
        print(f"Local approval operation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
