# Change Impact Matrix

- Status: accepted
- Canonical for: minimum impact analysis before implementation or review

Inspect does not mean change. It identifies evidence needed to preserve contracts, risk posture, and dependency direction.

| Change trigger | Inspect before editing | Likely coordinated updates | Minimum evidence |
| --- | --- | --- | --- |
| Domain term or invariant | Domain callers, application operations, contracts, glossary, tests | Domain docs/tests; contract or ADR only if meaning changes publicly | Focused domain tests and impacted contract checks |
| REST API operation/model | Application operation, auth policy, generated client, error model | API models, OpenAPI snapshot, client, route tests | Schema diff, success/failure/auth tests, client generation |
| Event contract | Producer, all consumers, idempotency, outbox, retention | Event schema/catalog, fixtures, consumers, compatibility docs | Old/new fixture validation and delivery/idempotency tests |
| Provider capability or manifest | Owning port, conformance suite, secrets, egress, data terms | Provider schemas, adapter, source register, risk/security docs | Capability, malformed, timeout, quota, provenance, safe-error tests |
| Market-data normalization | Instrument/time/currency/adjustment semantics, consumers, terms | Finance contracts, provider adapter, provenance docs | Deterministic mapping fixtures and data-use review |
| Portfolio calculation | Domain formulas, market inputs, rounding, calendars, fees, corporate actions | Domain docs, fixtures, independent expected results | Edge-case and independent deterministic calculation tests |
| Curriculum or competency | Prerequisites, activity versions, assessment mapping, adaptation | Domain docs/contracts, learner projections, migration plan | Eligibility and version-transition tests |
| Assessment or grading | Evidence lifecycle, missing states, review/override, learner state | Domain docs/contracts, UI, audit behavior | Scoring, null/missing, authorization, audit tests |
| Learner-state projection | Evidence inputs, versioning, rebuild, privacy | Projection code, adaptation inputs, retention docs | Rebuild/replay, stale version, deletion, isolation tests |
| Adaptive strategy/model | Eligibility, deterministic policy, baseline, experiment assignment | AI/ML docs, decision records, evaluation assets | Policy denial, fallback, outcome, bias/harm evaluation |
| Tutoring or generated content | Grounding sources, prompt/model version, claims, review path | AI/ML, risk, source, content docs/contracts | Citation/grounding, unsafe output, fallback, retention evidence |
| Dataset or feature pipeline | Source permission, lineage, split integrity, leakage, reproducibility | Data/AI docs, manifests, schemas, model evaluation | Lineage, split, leakage, version, reproducibility checks |
| AI/model provider | Data-use terms, egress, safety, cost, capability, fallback | Provider/source/risk/security docs and conformance suite | Redaction, timeout, validation, fallback, budget evidence |
| Persistence schema | Owning module, migrations, local/cloud parity, backup/export | Schema, migrations, data/operations docs | Upgrade/rollback, backup/restore, local/cloud integration |
| Object or analytical storage | Key ownership, lineage, cleanup, tenant scope | Storage adapters, retention, export, security docs | Traversal, isolation, lifecycle, corruption/failure tests |
| Identity, tenancy, entitlement | Decision readiness, request/job propagation, policies, database/storage scope | ADR, security architecture, hosts, contracts | Denial, cross-tenant isolation, missing-context failure |
| Local/cloud deployment | Shared artifacts, config, storage, secrets, health/recovery | Deployment and operations docs | Configuration, startup failure, parity and qualification checks |
| Dependency or build change | Provenance, license, advisories, compatibility, generated artifacts | Lock/build config, security/licensing docs | Clean install/build, relevant tests, reviewed advisories |
| Shared UI token, layout, component style, or icon | Style guide, executable tokens, icon manifest/sprite, both themes, responsive and accessibility consumers | Design docs/assets, consuming UI, visual/accessibility tests, context guidance | Design-system check plus focused light/dark, keyboard, contrast, zoom, and responsive evidence |
| Planning artifact, approval stage, ownership field, or planning skill | Planning guide/register/concurrent-work protocol/templates, ignored local-ledger contract, suite manifest/router/evaluations, decision readiness, owning canonical sources, current authority | Public artifact metadata/history, register, skills/assets/scripts, planning tools, roadmap/context guidance; local records remain ignored | Public planning integrity, local approval-gate and claim tests, planning-skill suite and prompt evaluations, aggregate readiness check |
| Canonical docs only | Implementation/tests, ADRs, context packs, links | Only sources made stale | Documentation structure/link checks |
| Agent/context/readiness guidance | Canonical sources, catalog, scenarios, pack budget, relevant planning skills, fixed readiness allowlist, CI workflow | Context packs/catalog/evaluations, suite manifest/router, agent tooling and CI | Aggregate agent-readiness check plus focused routing or runner refusal tests when affected |

## Ordering

For cross-boundary work:

1. Resolve the decision and risk posture.
2. Define domain meaning and stable contracts.
3. Implement application behavior.
4. Implement adapters and persistence.
5. Compose hosts and transports.
6. Update clients and UI.
7. Reconcile canonical docs and derived context.
8. Run focused and repository-wide applicable checks.

## Escalation

Stop before implementation when work would select an unresolved identity, tenancy, financial-claims, provider-license, model-authority, external-execution, encryption, recovery, public exposure, commercial-license, or breaking-compatibility policy.
