# Approval Checklist

Record the human decision and any reviewer statement only in the ignored local ledger. Do not add approval metadata, approval history, reviewer identity/status, or approval summaries to tracked files.

- The subject is one complete CAP package or one closed related DEC set.
- Applicable `AGENTS.md` and repository-root `docs/README.md` were read and followed.
- Canonical sources and decision readiness are current and consistent.
- Scope, non-scope, dependencies, contracts, and ownership are explicit.
- The CAP has an exact `slice_ids` manifest; every row has a coarse outcome, dependency/order constraint, and material-change boundary.
- Relevant success, denial, failure, degraded, provenance, parity, accessibility, or theme scenarios are present.
- Verification commands and documentation impact are executable and complete.
- No unresolved durable choice is hidden in implementation.
- The human decision, local actor label, date, scope when applicable, and authority reference are explicit in the ignored local ledger.
- `.local-codex/` is ignored and no local ledger content appears in Git status or tracked diffs.
- The CAP approval is the only delivery approval; no later SLI, WRK, implementation, or completion approval is implied.
- A DEC bundle contains only the decision stage; each member receives its own local record.
- Material CAP change requires renewed CAP approval; conforming just-in-time SLI and WRK detail does not.
- External, destructive, credentialed, production, publication, and commercial actions retain separate authorization.
