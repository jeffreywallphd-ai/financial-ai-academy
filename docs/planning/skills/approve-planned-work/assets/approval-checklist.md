# Approval Checklist

Record the human decision and any reviewer statement only in the ignored local ledger. Do not add approval metadata, approval history, reviewer identity/status, or approval summaries to tracked files.

- Subject ID or closed bundle membership and one approval stage are unambiguous.
- Applicable `AGENTS.md` and repository-root `docs/README.md` were read and followed.
- Canonical sources and decision readiness are current and consistent.
- Scope, non-scope, dependencies, contracts, and ownership are explicit.
- Work-packet write scopes and generated artifacts are repository-relative, bounded, and non-overlapping with active work; parallel-safety declarations are reciprocal.
- Relevant success, denial, failure, degraded, provenance, parity, accessibility, or theme scenarios are present.
- Verification commands and documentation impact are executable and complete.
- No unresolved durable choice is hidden in implementation.
- The human decision, local actor label, date, scope when applicable, and authority reference are explicit in the ignored local ledger.
- `.local-codex/` is ignored and no local ledger content appears in Git status or tracked diffs.
- The state transition does not imply a later approval.
- A bundle contains only one stage; each member receives its own local record.
- Added or materially revised decisions, packets, and implementation scopes are explicitly outside prior bundle approval.
- External, destructive, credentialed, production, publication, and commercial actions retain separate authorization.
