# Context Pack: Testing and Quality

## Use When

Work affects tests, defects, diagnostics, architecture checks, docs checks, contract checks, or agent-support evaluation.

## Preserve

- Test invariants at their owning layer.
- Verify failure and denial behavior.
- Keep financial fixtures deterministic and independently expected.
- Keep model evaluation separate from deterministic correctness.
- Treat coverage claims as direct, representative, or gap.
- Run the fixed agent-readiness gate for repository support evidence, then add focused checks for the affected boundary.
- Select routine checks from the tracked affected-path catalog and record exact-candidate receipts; require a concrete shared-impact reason for full-suite escalation, and never treat a receipt as approval or criterion judgment.
- Test control-plane friction directly: narrow changes stay narrow, stale or partial evidence fails with a bounded rerun path, and failed attempts remain append-only.
- A clean candidate needs one independent technical disposition. Corrected descendants close named open findings with fresh evidence; they do not restart unrelated audits or create another planning gate.
- Keep local and CI policy rule inventories identical. Mark ignored local facts
  `not-evaluated` in public CI, retain privacy-minimized machine reports, and
  derive operator status without mutating lifecycle state.
- Exercise packet-start idempotence and semantic drift separately from prose
  churn. Prove completed correction routing is scope-bounded and maintenance is
  allowlisted, mutation-blocking, append-only, and health-gated.
- Test exact command/effect/path capability confinement, payload-free
  provenance, anonymous non-blocking telemetry, and hard safety assertions
  independently from friction budgets in the multi-turn corpus.

## Canonical Sources

- `docs/standards/testing-and-verification-standards.md`
- `docs/architecture/assurance/testing-architecture.md`
- `docs/architecture/assurance/architecture-verification.md`
- `docs/assurance/known-verification-gaps.md`
- `dev-tools/agent/README.md`

## Stop When

A failing check exposes a missing product or architecture decision rather than a local implementation defect.
