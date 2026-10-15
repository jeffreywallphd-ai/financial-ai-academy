---
id: WRK-0012
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-control-plane
updated: 2026-10-15
parent: SLI-0004
capability: CAP-0002
depends_on: ["WRK-0011"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane", "dev-tools/planning/README.md", "docs/context/packs/testing-quality.pack.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0004-select-affected-checks-and-record-receipts.md", "docs/planning/work-packets/WRK-0012-deliver-affected-verification-receipts.md", "docs/standards/testing-and-verification-standards.md"]
generated_artifacts: []
base_revision: 204c9f14a18bcfd6d48d41bdb5dfe43be32c4b8a
claim_id: WRK-0012:3a416dfa-cd92-406f-9c70-935b9385c226
claimed_by: codex-control-plane
claimed_at: 2026-10-15T12:44:07Z
---

# Agent Work Packet: Deliver Affected Verification Receipts

## Objective and Deliverable

Extend the reusable control plane with deterministic risk-selected checks, an
allowlisted local executor, input/environment fingerprints, append-only
exact-candidate receipts, freshness validation, commands, documentation, and
direct safety and anti-rigidity evidence.

## Required Context

Read applicable `AGENTS.md`, `docs/README.md`, CAP-0002, SLI-0004, SLI-0003 and
WRK-0011 contracts, planning/concurrent-work guides, testing standards,
agent-readiness allowlist and CI workflow, affected control-plane code/tests,
and nearest READMEs before editing.

## Decisions and Assumptions

- The reusable selector and receipt model are project-neutral; a repository
  adapter supplies catalog entries and path/risk rules.
- Only tracked allowlisted command definitions execute. A receipt reports facts
  and never grants approval or acceptance by itself.
- Fresh execution is the default. Reuse is rejected unless complete input and
  producer closure can be proven; this packet does not enable reuse.
- Narrow checks are the default. Full readiness requires a deterministic
  shared-impact rule and recorded reason.

## In Scope

Check catalog/schema, selector, fingerprints, subprocess result capture,
append-only receipt chain, validation, CLI operations, docs, focused tests, and
per-slice anti-rigidity assertions.

## Out of Scope

Independent review, CI artifact retention, remote execution/cache/signing,
arbitrary command discovery, criterion judgment, or a new approval stage.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable core | Current ports, engine, store, CLI, tests | `dev-tools/control-plane/` | Add project-neutral verification primitives and repository adapter |
| Guidance | Planning/testing references | Named docs in `write_scope` | Document selection, receipts, failure semantics, and friction limits |
| Planning | SLI/WRK/register | Named planning files | Keep lifecycle and evidence synchronized |

## Contracts and Interfaces

Stable `check-plan-v1` and `verification-receipt-v1` JSON objects; canonical
SHA-256 digests; command IDs rather than free-form shell input; exact candidate,
catalog, input, environment, producer and prior-receipt bindings; stable refusal
codes and remediation.

## Dependencies and Parallel Safety

WRK-0011 is complete. This packet is serial because it extends its submission
and state contracts and is not parallel-safe with another control-plane change.

## Acceptance Scenarios

The SLI-0004 scenario table is normative. Tests must additionally show identical
selection order across repeated calls, no full-suite selection for a docs-only
fixture, a concrete reason for every escalation, output digests without embedded
raw secrets, and preserved failed attempts.

## Verification Commands

- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/control-plane/test_verification.py`
- `python dev-tools/planning/test_planning_tools.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`

## Documentation and Evidence Update

Update reusable extension guidance, command reference, testing/context rules,
packet and slice evidence, and the register. Keep runtime receipts and all local
authority/reviewer records ignored and untracked.

## Stop Conditions

Stop for material CAP drift, arbitrary/untracked commands, unknown input closure
being treated as reusable proof, external services/credentials, or a selector
that cannot explain why a broader profile is necessary.

## Required Handoff

Report selector and receipt contracts, exact checks/results, failed/stale/replay
and anti-rigidity evidence, environment limits, documentation impact, and the
next deterministic slice action.

## Completion Evidence

- Added reusable check-catalog, affected-selection, fingerprint, executor,
  receipt-store, validation, and verification-service primitives plus the
  Financial AI Academy tracked catalog and CLI commands.
- `python dev-tools/control-plane/test_verification.py` passed 10 tests covering
  deterministic order/digests, docs-only and control-only narrow selection,
  reason-bound full-readiness escalation, unclassified-path refusal, subprocess
  output minimization, failed and timed-out attempts, receipt-chain integrity,
  disabled optimistic reuse, qualifying/non-qualifying receipts, and candidate
  drift retained as non-qualifying evidence.
- `python dev-tools/control-plane/test_control_plane.py` passed 10 lifecycle,
  recovery, concurrency, exact-Git, adapter-reuse, and anti-rigidity tests.
- Planning-tool behavior, public planning integrity for 18 artifacts, SLI/WRK
  validation, documentation validation for 138 Markdown files and the context
  catalog, and all 10 aggregate agent-readiness checks passed.
- Receipt output records command IDs/arguments, exit state, byte counts, and
  hashes without raw stdout/stderr. Receipts remain ignored local evidence,
  cannot authorize transitions, and reject stale catalog, plan, candidate,
  coverage, failure, timeout, and digest mismatches.
- Windows executed the real allowlisted subprocess fixtures. Other hosts and
  reusable result-cache provenance remain explicit gaps; reuse is disabled.
- The ordinary low-risk path selects only matched narrow checks. No lower-level
  approval prompt, arbitrary command, speculative full-suite fallback, remote
  service, credential, commit, push, or product-state mutation was added.

## Planning History

- 2026-10-15: Authored just in time as the single bounded SLI-0004 packet after
  WRK-0011 and SLI-0003 completed.
