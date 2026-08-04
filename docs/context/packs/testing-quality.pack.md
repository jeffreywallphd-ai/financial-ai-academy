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

## Canonical Sources

- `docs/standards/testing-and-verification-standards.md`
- `docs/architecture/assurance/testing-architecture.md`
- `docs/assurance/architecture-verification.md`
- `docs/assurance/known-verification-gaps.md`
- `dev-tools/agent/README.md`

## Stop When

A failing check exposes a missing product or architecture decision rather than a local implementation defect.
