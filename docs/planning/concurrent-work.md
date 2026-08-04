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

A claim requires a ready packet, approved planning and implementation gates,
recorded `implementation_authority`, a current explicit instruction for the
named work, and a non-empty scope. Preview first by omitting `--apply`; then use:

```text
python dev-tools/planning/claim_packet.py claim <packet> --owner <owner> --authority <authority> --confirm-current-instruction --apply
```

The helper records `base_revision`, `claim_id`, `claimed_by`, and `claimed_at`,
and moves the packet to `active`. Update `register.md` in the same repository
change. The helper refuses overlap with another active packet.

Move a finished implementation into evidence gathering with:

```text
python dev-tools/planning/claim_packet.py release <packet> --owner <owner> --to verifying --apply
```

Use `--to ready` when safely abandoning an activation. Preserve claim fields as
audit evidence. Never transfer ownership silently: return to `ready`, update the
owner/authority as approved, and create a new claim.

## Failure and Recovery

Stop when an active scope overlaps, the base revision is stale in a way that
changes packet assumptions, claim metadata conflicts, or generated output has
another owner. Reconcile the planning artifact and register through review; do
not delete durable evidence to make a check pass. Stale local lock files may be
removed only after verifying that no claim command is running and the packet
metadata is authoritative.
