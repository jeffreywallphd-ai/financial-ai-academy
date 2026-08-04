# Prompt Routing

- Status: accepted
- Canonical for: minimum-sufficient task context

## Baseline

1. Read `docs/README.md`.
2. Include `docs/context/packs/index.pack.md`.
3. Classify the task with the change-impact matrix.
4. Add one primary and at most one adjacent pack by default.
5. Read canonical sources named by those packs.
6. Consult decision readiness for architecture-sensitive work.
7. Inspect affected implementation, contracts, consumers, tests, and nearest README.

## Routing

| Task materially involves | Primary pack | Common adjacent pack |
| --- | --- | --- |
| Product scope, editions, users, non-goals, domain vocabulary | `product-domain` | `security-risk` |
| Repository structure, modules, dependency direction, APIs, events, providers | `architecture-contracts` | owning feature pack |
| Curriculum, assessment, learner state, recommendations | `learning-adaptation` | `ai-ml` |
| Instruments, market data, portfolios, backtests, data provenance | `financial-data` | `security-risk` |
| Models, prompts, tutoring, datasets, features, evaluations | `ai-ml` | owning learning/finance pack |
| Privacy, financial claims, licenses, external sources, executable plugins | `security-risk` | owning feature pack |
| Local/cloud configuration, storage, jobs, backup, migrations, recovery | `deployment-operations` | `security-risk` |
| Capability shaping, vertical slices, work packets, approvals, planning skills, ID reservation, packet claims, concurrent ownership, “what next?” routing, delivery sequencing | `delivery-planning` | `testing-quality` when changing planning automation |
| User interface, themes, design tokens, layouts, charts, accessibility presentation, iconography | `interface-design` | `testing-quality` |
| Tests, defects, diagnostics, architecture checks, documentation checks, agent readiness, prompt evaluations, CI gates | `testing-quality` | pack owning the failing seam |

## Stop Conditions

Stop when:

- canonical sources conflict,
- decision readiness is `proposed` or `decision-required`,
- provider/data permission is unclear,
- work would cross the education/advice boundary,
- model output would become authoritative for protected state,
- identity, tenancy, encryption, external execution, recovery, or commercial licensing policy is unresolved,
- required authority, credentials, destructive action, production mutation, or external publication is absent.
