# Context Pack: Delivery Planning

## Use When

Work creates, reviews, sequences, or executes capabilities, vertical slices, agent work packets, decision requests, or roadmaps.

## Preserve

- Canonical sources and accepted ADRs outrank planning artifacts.
- Decompose substantial outcomes from capability to vertical slice to one-agent work packets.
- Resolve named decision gates before dependent work becomes ready.
- Use one human delivery approval for the complete CAP planning package. It must enumerate and sequence every intended slice before delivery; an agent may record but never originate approval.
- Refine each slice and packet immediately before it starts. Do not request SLI, WRK, implementation, or completion approval when the refinement stays within the approved CAP package.
- Keep every approval and reviewer record only in the ignored local ledger; never copy its identity, decision, date, authority, scope, history, or summary into tracked files.
- Define contracts, dependencies, failure scenarios, verification, documentation impact, and stop conditions before execution.
- Parallelize only packets with accepted inputs and non-overlapping ownership.
- Reserve planning IDs, declare write scopes and generated artifacts, and create durable packet claims through the repository planning tools.
- Planning readiness, an accepted roadmap, and advice-only prompts do not grant implementation or external-action authority.
- Require a current CAP package binding, manifest membership, deterministic readiness, bounded write scope, completed dependencies, and a collision-free claim before work becomes active. Material CAP changes require renewed CAP approval; bounded SLI/WRK refinements do not.
- Prefer the reusable lease-aware controller for new packets: exact candidate and scope evidence, CAS revisions, recoverable transactions, and expired-lease recovery are controls; renewal, full-suite checks, and lower-level approvals are not routine prerequisites.
- Keep independent technical dispositions append-only in the ignored reviewer ledger, bind them to exact candidates and qualifying receipts, and replay only open findings plus incremental risk on a corrected strict descendant.
- Close semantic acceptance once at packet start, exclude non-semantic prose
  churn from drift detection, and keep low/medium-risk work on the affected-check
  plus one-review path.
- Route in-scope defects in completed work to one bounded descendant WRK without
  reopening history or asking for approval; reserve CAP reshaping for material
  package drift.
- Use allowlisted, health-gated maintenance only for controller defects; never
  turn maintenance into an arbitrary shell or ordinary implementation step.
- Treat capability grants, provenance, telemetry, and harness metrics as
  deterministic evidence, not planning/external authority or a new approval.
- Use hierarchy-specific portfolio readiness, compatibility, and allocation as
  advisory evidence. Never treat an ancestor and descendant as separate edit
  owners, and isolate unknown evidence to the affected lane rather than locking
  the repository.
- Publish optional edit intent and acquire renewable exact-file leases only for
  bounded writes under an active packet claim; reads and unrelated files remain
  concurrent, and a file lease never broadens authority.
- Execute CAP-authorized slice delivery one dependency-ready packet at a time, completing the current packet before claiming its successor unless its scopes are explicitly parallel-safe.

## Canonical Sources

- `docs/planning/README.md`
- `docs/planning/skills/README.md`
- `docs/planning/concurrent-work.md`
- `docs/standards/ai-agent-development-standards.md`
- `docs/standards/change-impact-matrix.md`
- `docs/adr/decision-readiness.md`
- `docs/roadmaps/README.md`

## Stop When

A plan would invent product or architecture meaning, bypass an unresolved decision or approval, claim authority it does not have, self-approve, activate work without claim evidence, or assign overlapping active ownership without coordination.
