# Context Pack: Delivery Planning

## Use When

Work creates, reviews, sequences, or executes capabilities, vertical slices, agent work packets, decision requests, or roadmaps.

## Preserve

- Canonical sources and accepted ADRs outrank planning artifacts.
- Decompose substantial outcomes from capability to vertical slice to one-agent work packets.
- Resolve named decision gates before dependent work becomes ready.
- Keep all six human approval stages separate; an agent may record but never originate approval. One response may cover a closed related DEC set or one slice's closed packet set at one stage, with one local record per artifact.
- Keep every approval and reviewer record only in the ignored local ledger; never copy its identity, decision, date, authority, scope, history, or summary into tracked files.
- Define contracts, dependencies, failure scenarios, verification, documentation impact, and stop conditions before execution.
- Parallelize only packets with accepted inputs and non-overlapping ownership.
- Reserve planning IDs, declare write scopes and generated artifacts, and create durable packet claims through the repository planning tools.
- Planning readiness, an accepted roadmap, and advice-only prompts do not grant implementation or external-action authority.
- Require locally recorded slice selection, packet planning, separate implementation approval exactly matching each packet's current write scope, and a current explicit implementation request before work becomes active. New or materially revised bundle members require renewed approval.
- Execute an approved slice bundle one dependency-ready packet at a time, completing the current packet before claiming its successor unless separately authorized otherwise.

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
