---
id: CAP-0024
kind: capability
planning_status: shaping
authority: noncanonical
owner: unassigned
updated: 2026-10-16
parent: null
depends_on: ["CAP-0026"]
decision_gates: ["DEC-0011", "DEC-0012", "DEC-0017"]
approval_model: cap-package-v1
slice_ids: ["SLI-0098", "SLI-0099", "SLI-0100", "SLI-0101"]
---

# Capability: Connect and Govern Replaceable Providers

## Outcome

An authorized operator can admit, configure, inspect, disable, and replace
market-data, model, content, storage, identity, and job providers through
platform-owned contracts with capability, health, quota, attribution, licensing,
cost, trust, provenance, and failure visibility.

## Users and Value

Operators and contributors need integrations that do not leak provider-specific
meaning into product domains. Value is observable when a provider is replaceable
within a declared capability and failure degrades explicitly without broadening
authority or corrupting durable state.

## Scope

### In Scope

- Versioned provider capability/manifest, configuration reference, health,
  quota, cost, attribution, licensing, data-use, provenance, and disablement.
- ADR-0018 allowlisted-adapter trust and PostgreSQL at-least-once job posture;
  market and model specifics selected in ADR-0020 and ADR-0013.
- Secret indirection, startup validation, health-gated use, bounded retries,
  circuit/degraded behavior, audit, and local/cloud capability discovery.
- Conformance kits for platform-owned ports and truthful operator interfaces.

### Out of Scope

- A general plugin marketplace, arbitrary extension execution, provider terms as
  code, storing secrets in domain state, or promising equivalent capabilities.
- Selecting cloud infrastructure, commercial licensing, or product-domain rules.

## Canonical Context

- [Contract Architecture](../../architecture/contracts/contract-architecture.md)
- [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md)
- [Data Architecture](../../architecture/data/data-architecture.md)
- [Security Architecture](../../security/README.md)
- [Decision Readiness](../../adr/decision-readiness.md)
- [ADR-0018](../../adr/ADR-0018-allowlisted-adapters-postgresql-at-least-once-jobs.md)
- [ADR-0020](../../adr/ADR-0020-staged-market-data-sourcing-with-alpha-vantage-first.md)
- [Provider Admission and Job Delivery](../../architecture/deployment/provider-admission-and-job-delivery.md)
- [Durable Job Delivery Contract](../../architecture/contracts/job-delivery-contract.md)
- [CAP-0026](CAP-0026-preserve-provenance-and-accountable-history.md)

## Decision Gates and Constraints

- ADR-0018 fixes exact allowlisted reviewed packaged adapters and PostgreSQL-
  backed at-least-once delivery. Out-of-process hosts, elevated trust classes,
  external brokers, different guarantees, and sandboxes require another decision.
  ADR-0013 and ADR-0020 select constrained model and market-data use postures.
- Alpha Vantage is the first market-data adapter target, but the platform port,
  manifest, rights profile, normalized records, errors, and conformance corpus
  remain provider-neutral and also run against an independent fake/reference
  adapter. No provider SDK or payload becomes a public contract.
- Platform contracts own canonical meaning. Adapters translate provider payloads
  and never supply domain authority or license interpretation.
- Secrets remain behind platform resolution; provider capability and health are
  explicit and can differ honestly by deployment profile.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0098 | An operator admits a provider against a versioned manifest, trust class, capability contract, configuration schema, and conformance evidence. | First after decisions and CAP-0026. | Arbitrary plugins, provider-owned domain semantics, or embedded secrets changes the CAP package. | captured |
| SLI-0099 | The operator configures and health-checks an admitted provider through secret indirection with quota, attribution, licensing/data-use, and cost visibility. | After SLI-0098. | Treating configuration as license approval or exposing secrets changes the CAP package. | captured |
| SLI-0100 | Product operations select, disable, replace, and degrade providers under deterministic capability policy and ADR-0018 at-least-once job semantics, including idempotency/reconciliation, cancellation, retry, and dead-letter handling. | After SLI-0099. | Silent fallback, cross-provider semantic drift, external broker/host, or different delivery guarantees changes the CAP package. | captured |
| SLI-0101 | Provider governance is qualified for conformance, isolation, secret handling, quota/outage, replacement, audit, local/cloud discovery, accessibility, and anti-rigidity. | Last; depends on SLI-0098 through SLI-0100. | Marketplace, remote code execution, or cloud platform selection changes the CAP package. | captured |

## Capability Acceptance

- Every admitted provider declares exact contract/capability versions, trust,
  configuration, health, quotas, attribution, data use, costs, and provenance.
- Invalid, unhealthy, unauthorized, over-quota, incompatible, or disabled
  providers fail boundedly; fallback never changes domain semantics silently.
- Secrets and raw payloads remain confined and redacted; provider replacement is
  tested against shared contract and failure corpora.
- Operator behavior is accessible and capability differences are reported
  honestly across deployment profiles.
- Alpha Vantage configuration, capability, quota, rights, health, disablement,
  and replacement are exercised through the same controls as another adapter;
  no live secret or provider response is required by deterministic tests.

- Every slice includes focused failure and anti-rigidity tests so an unhealthy
  or unsupported provider isolates only dependent capabilities and never forces
  repository-wide or product-wide lockstep.

## Risks and Non-Goals

Provider frameworks can become arbitrary code loaders or accidental licensing
authorities. This CAP excludes a marketplace, unsandboxed extensions, secret
leakage, provider-specific domain models, and cloud-platform selection.

## Documentation Impact

Delivery will add manifest/provider contracts, conformance, trust and sandbox,
secret/configuration, health/quota/cost, attribution/licensing, jobs/failure,
operator UI, operations, and verification documentation.

## Planning History

- 2026-10-15: Shaped from catalog candidate 21 with manifest SLI-0098 through
  SLI-0101. DEC-0011, DEC-0012, and DEC-0017 block CAP approval and delivery.
- 2026-10-15: DEC-0017 was promoted to ADR-0018, selecting allowlisted packaged
  adapters and PostgreSQL-backed at-least-once jobs. DEC-0012 remains unresolved.
- 2026-10-16: DEC-0012 was promoted through ADR-0020. All listed decision gates
  are resolved, so this CAP returns to shaping for dependency and CAP-package
  readiness validation.
- 2026-10-16: Revalidated the complete four-slice package against ADR-0020.
  Alpha Vantage supplies the first market-data conformance case without changing
  the provider-neutral manifest, admission, operation, or qualification sequence.

