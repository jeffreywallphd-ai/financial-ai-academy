# Planning Automation

These dependency-free tools enforce the planning contracts in `docs/planning/`.
They are narrow validators and state helpers, not a general command runner.

Before changing these tools or planning artifacts, read and follow the applicable
`AGENTS.md`, repository-root `docs/README.md`, and `docs/planning/README.md`.

The supported entry points are:

- `check_planning.py` — validate artifact identity, references, approvals,
  lifecycle transitions, register synchronization, and concurrent write scopes.
- `reserve_id.py` — reserve collision-resistant planning IDs in ignored local
  state before an artifact is authored.
- `claim_packet.py` — preview or atomically claim/release an approved work packet.

Local reservations and locks live under `.local-codex/`, which is ignored. The
planning artifacts themselves remain the durable, reviewable source of truth.
