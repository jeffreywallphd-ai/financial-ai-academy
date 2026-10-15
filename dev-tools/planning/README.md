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
  response for a closed related DEC set, while CAP approvals automatically bind
  the governed package digest and exact slice manifest.
- `reserve_id.py` — reserve collision-resistant planning IDs in ignored local
  state before an artifact is authored.
- `claim_packet.py` — preview or atomically claim, release, or finalize one
  CAP-authorized work packet; current CAP binding, manifest membership, scope
  collision rules, and completed dependencies are enforced. This remains the
  compatibility helper for packets created before the lease-aware controller.

The reusable lease-aware controller lives in `dev-tools/control-plane/`. Its
project-neutral kernel and store are composed with this repository's planning
and Git adapters. Use `control_plane.py` for interruption-safe claim, resume,
renew, recover, exact-candidate submit, release, and status operations. It
updates the same tracked packet projection through a recoverable journal and
stores operational state only under ignored `.local-codex/control-plane/`.

Local reservations, locks, and approval/reviewer records live under
`.local-codex/`, which is ignored. Public planning artifacts remain the
reviewable source of planning state but are deliberately not approval evidence.
Legacy lower-level approval records remain readable, but new records can only
use the `capability` and `decision` stages.

The ordinary path deliberately remains short: claim, implement, commit through
separately authorized Git practice, and submit. Renewal is optional, recovery
is used only after expiry, and submission does not impose a repository-wide
test suite or another planning approval.

After submission, `plan-checks` deterministically selects commands from the
tracked Financial AI Academy catalog. `verify` runs only those allowlisted
commands by default and appends a candidate/input/environment-bound receipt
under ignored local state. Full readiness is selected only by a tracked
shared-impact rule. Receipt reuse remains disabled until installed executable
closure and trusted producer provenance are demonstrably complete.

Independent technical review uses the same ignored approval ledger's `reviews`
array through the control-plane review adapter. Review rounds bind one exact
candidate and qualifying receipt, remain append-only, and cannot accept while a
blocking finding is open. Corrections are strict descendants and require fresh
verification. These technical dispositions are not planning approvals and no
reviewer data belongs in tracked files.

`policy-check` evaluates the same stable rules locally and in CI; differences
only reflect evidence availability. `operator-status` is the read-only,
single-command projection for public state, optional lease/submission state,
receipt counts, anonymous finding IDs, diagnostics, and the next legal action.
Neither command grants authority or introduces another approval gate.

Immediately after a packet is claimed, `packet-start` freezes its semantic
acceptance/scope manifest and risk-selected evidence route. It ignores prose
history and other non-semantic churn. A completed-work defect uses
`correction-route` to prove path confinement before a bounded descendant WRK is
authored under the same slice; conforming correction work needs no additional
approval. Controller defects use the allowlisted maintenance commands, never
manual lifecycle metadata editing or arbitrary shell repair.

Execution capabilities name stable catalog/action IDs, path scopes, and effects;
they never embed argv or broaden CAP authority. CLI provenance and anonymous
local telemetry are evidence only. The committed multi-turn corpus guards both
safety and avoidable friction; optimization results cannot waive a safety rule
or create another planning gate.
