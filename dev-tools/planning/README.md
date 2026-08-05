# Planning Automation

These dependency-free tools enforce the planning contracts in `docs/planning/`.
They are narrow validators and state helpers, not a general command runner.

Before changing these tools or planning artifacts, read and follow the applicable
`AGENTS.md`, repository-root `docs/README.md`, and `docs/planning/README.md`.

The supported entry points are:

- `check_planning.py` — validate public artifact identity, references,
  lifecycle transitions, register synchronization, and concurrent write scopes;
  add `--require-local-approvals` for guarded local readiness.
- `manage_approval.py` — record and inspect human decisions and reviewer
  statements in the ignored local ledger; `record-bundle` atomically records one
  response for a closed related DEC set or one slice's planning/implementation packet set.
- `reserve_id.py` — reserve collision-resistant planning IDs in ignored local
  state before an artifact is authored.
- `claim_packet.py` — preview or atomically claim, release, or finalize one locally
  approved work packet; exact approved scope and completed dependencies are enforced.

Local reservations, locks, and approval/reviewer records live under
`.local-codex/`, which is ignored. Public planning artifacts remain the
reviewable source of planning state but are deliberately not approval evidence.
