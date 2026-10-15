# Concurrent Automated Work

- Status: accepted
- Canonical for: planning ID reservation, agent packet ownership, and concurrent write-scope coordination

## Principle

Concurrency is permitted only across approved work packets whose dependencies,
contracts, write scopes, and generated artifacts are independent. Conversation,
branch names, or agent intent alone do not establish ownership.

Before changing planning or implementation files, prominently read and follow
every applicable `AGENTS.md`, the repository-root `docs/README.md`, and the
planning guide. These controls add evidence; they never broaden authority.

## Reserve Artifact IDs

Reserve an ID before creating a planning artifact:

```text
python dev-tools/planning/reserve_id.py reserve --kind WRK --owner <owner>
```

Reservations are atomic inside one workspace and live under ignored
`.local-codex/planning-reservations/`. After the matching artifact exists and is
listed in the planning register, consume the reservation:

```text
python dev-tools/planning/reserve_id.py consume WRK-0001 --owner <owner> --artifact docs/planning/work-packets/WRK-0001-name.md
```

CI remains the final collision check across branches and workspaces.

## Declare Ownership Boundaries

Every work packet declares:

- `write_scope`: repository-relative files or directory roots the packet may edit;
- `generated_artifacts`: derived files the packet may regenerate;
- `parallel_safe_with`: reciprocal packet IDs with accepted, independent inputs;
- null claim fields while the packet is not active.

Do not declare the repository root, absolute paths, parent traversal, or broad
wildcards as a write scope. A file and its parent directory overlap. Generated
artifacts count as owned write scope even when their source inputs differ.

## Claim Approved Work

A claim requires a ready packet whose parent slice is included in the current
approved CAP package, a package digest and slice manifest that still match that
approval, completed dependencies, and a non-empty collision-free public
`write_scope`. The current user instruction to deliver the approved capability
activates its conforming slices; no packet-specific authority flag or repeated
approval record is required. Preview first by omitting `--apply`; then use:

```text
python dev-tools/planning/claim_packet.py claim <packet> --owner <owner> --apply
```

The helper validates the CAP binding and manifest membership, records
`base_revision`, `claim_id`, `claimed_by`, and `claimed_at`, and moves the packet
to `active`. Update `register.md` in the same repository change. The helper
refuses overlap with another active packet.

For lease-aware work, prefer the reusable controller:

```text
python dev-tools/control-plane/control_plane.py claim <WRK-ID> --owner <owner>
python dev-tools/control-plane/control_plane.py resume <WRK-ID> --owner <owner> --claim-id <claim-id>
python dev-tools/control-plane/control_plane.py renew <WRK-ID> --owner <owner> --claim-id <claim-id>
python dev-tools/control-plane/control_plane.py recover <WRK-ID> --owner <owner>
python dev-tools/control-plane/control_plane.py submit <WRK-ID> --owner <owner> --claim-id <claim-id>
python dev-tools/control-plane/control_plane.py packet-start <WRK-ID>
```

The controller stores the renewable lease and append-only transition history
under ignored `.local-codex/control-plane/`, retains tracked packet frontmatter
as the public projection, and uses a journal to finish interrupted two-file
publication. `recover` is legal only after lease expiry and never displaces an
active owner. Every refusal reports the failed invariant, observed facts, and a
bounded command-level remediation; routine recovery never asks the operator to
hand-edit metadata.

Run `packet-start` immediately after claim. It closes the semantic acceptance
set and selects the minimum evidence route for that claim without adding an
approval. Its digest excludes prose history, timestamps, completion evidence,
and other non-semantic churn. Low/medium work uses affected verification and one
independent review; only explicit shared/control impact adds aggregate
readiness.

For a slice-wide implementation bundle, claim only the next dependency-ready
packet. Finish its focused verification, move it to `verifying`, and finalize it:

Move a finished implementation into evidence gathering with:

```text
python dev-tools/planning/claim_packet.py release <packet> --owner <owner> --to verifying --apply
python dev-tools/planning/claim_packet.py finalize <packet> --owner <owner> --apply
```

Only after finalization may a dependent packet be claimed. Use `--to ready` when safely abandoning an activation. Preserve claim fields as
audit evidence. Never transfer ownership silently: return to `ready`, update
public ownership, record any new authority only in the local ledger, and create
a new claim. New packets or changed scopes need no approval when they remain
within the current approved CAP and slice contracts; material CAP drift requires
renewed CAP-level approval.

The compatibility claim helper and lease-aware controller share the same public
projection. A pre-controller active packet is readable through controller
`status` as a compatibility projection. New lease-aware mutations create the
versioned ignored state; they do not synthesize or rewrite earlier history.

## Failure and Recovery

Stop when an active scope overlaps, the base revision is stale in a way that
changes packet assumptions, claim metadata conflicts, or generated output has
another owner. Reconcile the planning artifact and register through review; do
not delete durable evidence to make a check pass. Stale local lock files may be
removed only after verifying that no claim command is running and the packet
metadata is authoritative.
An interrupted controller transaction is recovered automatically by the next
status or mutation command. Preserve malformed state or journal bytes for the
bounded maintenance route instead of deleting them.

Do not reopen completed packet history. First run `correction-route` with the
exact proposed paths. An in-scope result routes to one bounded descendant WRK
under the same slice with no new approval; a scope escape returns to CAP shaping
only when it materially changes the approved package. Controller repair uses an
allowlisted maintenance session. While active it blocks normal mutations,
records append-only events, and exits only after a registered action succeeds
and health passes. It never accepts arbitrary shell text.
