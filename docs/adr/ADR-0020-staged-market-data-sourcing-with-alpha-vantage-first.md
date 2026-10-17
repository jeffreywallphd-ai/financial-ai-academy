# ADR-0020: Staged Market-Data Sourcing with Alpha Vantage First

- Status: accepted
- Date: 2026-10-16
- Decision request: [DEC-0012](../planning/decision-requests/DEC-0012-market-data-provider-and-licensed-use-baseline.md)
- Extends: [ADR-0002](ADR-0002-contract-driven-provider-architecture.md), [ADR-0015](ADR-0015-market-data-portfolio-method-registry.md), and [ADR-0018](ADR-0018-allowlisted-adapters-postgresql-at-least-once-jobs.md)

## Context

The first useful market-data experience needs a practical source while keeping
canonical financial meaning, data-use policy, and product availability
independent of any one vendor. Alpha Vantage has broad historical and
fundamental coverage, documents support for verified open-source and educational
projects, and has previously been accessible to the project's educational
context. Its public terms nevertheless distinguish private individual use from
organizational, shared, and commercial use, and its education-support statement
does not by itself define storage, backup, export, redistribution, managed-cloud,
real-time, or AI/ML rights.

Technical access or a provider relationship therefore cannot become general
license authority. The platform needs an early adapter that can deliver value
within a narrow reviewed profile and fail closed everywhere else, while making
later provider additions ordinary adapter work instead of a domain rewrite.

## Decision

Use a staged, rights-profiled hybrid sourcing architecture. Alpha Vantage is
the first external market-data integration target, but it is not the canonical
data model, the exclusive provider, a bundled credential, or the source of
product authority.

Market data owns provider-neutral, versioned contracts for:

- instrument and coverage identity;
- bounded queries and declared capabilities;
- observations, calendars, corporate actions, adjustment and quality;
- source, effective-market, retrieval, and as-of times;
- attribution, provenance, transformation, and applicable-use references; and
- typed unavailable, unsupported, invalid, quota, timeout, entitlement, and
  rights-policy outcomes.

Adapters translate untrusted provider responses into those contracts. Provider
SDK types, endpoint names, quota messages, identifiers, and payloads remain
inside the adapter. Browser and headless clients consume the same public
application/API operations and never call Alpha Vantage directly as product
behavior.

### Staged Source Order

1. Preserve validated user-supplied imports as the provider-independent local
   fallback.
2. Implement an Alpha Vantage adapter first for a bounded historical or
   end-of-day educational path selected during CAP delivery.
3. Add authoritative public sources such as SEC, BLS, and BEA, plus only
   individually reviewed FRED series, through the same contracts.
4. Add other community or managed providers only through independently
   reviewed adapters and use profiles. Provider order may change when coverage,
   quality, cost, reliability, or rights evidence changes; canonical meaning
   does not.

### Alpha Vantage Initial Boundary

The initial adapter is configured explicitly and uses a user-, project-, or
institution-supplied credential held behind host secret resolution. No key is
committed, embedded in portable state, or enabled merely because it exists.
The initial plan posture is Alpha Vantage free API access: the runtime enforces
the standard published quota unless the exact credential has current verified
open-source or educational-project quota evidence. No platform-funded shared
key is assumed.

The first rights profile is deliberately narrow:

- educational or research use only;
- local single-profile or another exact deployment explicitly covered by the
  recorded provider evidence;
- historical/end-of-day retrieval and bounded display only for allowlisted
  datasets and endpoints;
- transient processing unless a current written profile expressly permits
  canonical retention, cache, backup, or derived-data persistence; and
- no real-time or delayed exchange-data entitlement, managed-cloud display,
  multi-user service, machine-readable export, redistribution, publication,
  model training/fine-tuning, reusable benchmark dataset, or retained provider
  fixture unless separately documented and admitted.

Alpha Vantage's published support statement for unlimited requests by verified
open-source or educational projects is quota evidence, not a blanket expansion
of license rights. Its standard terms permit private individual investment
analysis, research, testing, and monitoring as non-commercial activity, while
organizational or shared access can require a written arrangement. The admitted
profile records the exact credential owner, dataset, plan or written
confirmation, deployment, audience, allowed uses, attribution, quota, retention,
and exit behavior. Missing, ambiguous, expired, or conflicting evidence denies
only the affected provider/use path.

Tests, examples, screenshots, and repository fixtures use synthetic or
expressly permitted data. They never depend on a live provider, secret, quota,
or mutable response.

### Provider Evolution

Every provider implements the same platform port and conformance corpus. A
provider-specific capability may be absent without weakening the common
contract or blocking unrelated product behavior. Selection is policy based on
declared capability, current use profile, health, quality, quota, cost, and
deployment—not scattered conditional logic in domains or clients.

An additional provider can be admitted without superseding this ADR when it:

- stays inside ADR-0018's exact allowlisted packaged-adapter trust class;
- preserves the provider-neutral Market data contracts and ADR-0015 semantics;
- has a current versioned use profile and external-source evidence; and
- passes shared success, denial, malformed, quota, timeout, provenance,
  replacement, and degraded-operation conformance.

A new trust class, provider-owned domain meaning, silent semantic fallback,
managed execution boundary, general redistribution right, AI/ML training use,
or materially broader license posture requires another durable decision.

## Consequences

- The project can integrate Alpha Vantage early without making it an
  architectural dependency.
- A local learner can benefit from a narrow educational path while unavailable
  or unlicensed uses degrade explicitly instead of blocking the whole product.
- Provider manifests and rights profiles add policy and conformance work, but
  make later providers additive and replaceable.
- The first adapter may initially support transient queries only. Persistent
  canonical history, export, shared classrooms, and managed cloud can remain
  unavailable until their exact rights are documented.
- Public provider statements and terms remain time-sensitive external authority;
  repository summaries must be refreshed and cannot substitute for them.

## Alternatives Rejected

- **Make Alpha Vantage the platform data model or exclusive provider.** Rejected
  because vendor payloads, capabilities, availability, and terms would leak
  into domain meaning and make replacement expensive.
- **Wait for one provider that covers every deployment and use.** Rejected
  because community education, managed display, retention, export, real-time,
  and AI/ML uses have different rights and cost profiles.
- **Use imports only.** Rejected as the sole path because it weakens onboarding
  and consistent provider qualification, while imports remain a useful fallback.
- **Treat educational support as unrestricted license authority.** Rejected
  because quota support and technical access do not establish every storage,
  audience, export, redistribution, exchange, or model-use right.

## Boundaries

This decision does not purchase or accept provider terms, create a provider
account, grant commercial or legal authority, select real-time entitlements,
promise an SLA, authorize cloud/multi-user display, permit redistribution or
bulk export, or authorize provider data for AI/ML training. It does not select
every initial dataset, endpoint, retention interval, or credential workflow;
those details must conform to the exact admitted profile during CAP delivery.

Provider-written clarification and qualified licensing review remain required
where public evidence does not expressly cover an intended use. Provider
profile activation, expansion, suspension, and exit are governed actions, not
configuration side effects.

## Verification Implications

- Prove the Market data core and public API contain no Alpha Vantage payload,
  SDK, identifier, error, endpoint, or quota type.
- Run one conformance corpus against the Alpha Vantage adapter and a second
  fake/reference adapter to prove the abstraction is not vendor-shaped.
- Cover successful normalization, missing capabilities, malformed data,
  timestamps, calendars, adjustments, corporate actions, corrections, quality,
  quota, rate limiting, timeout, outage, cancellation, and redacted diagnostics.
- Prove rights policy fails closed for persistence, backup, export,
  redistribution, managed cloud, real-time data, and AI/ML use unless the exact
  active profile permits them.
- Prove provider absence, disabled credentials, exhausted quota, or expired
  rights degrades only dependent features and leaves imports and unrelated
  product behavior available.
- Use synthetic deterministic fixtures for tests and examples; live
  qualification is separate, secret-aware, non-recording, and bounded.
- Preserve complete source, retrieval, effective-time, transformation,
  quality, use-profile, attribution, and adapter-version provenance.

## Supersession

Supersede or extend this ADR before changing provider-neutral market semantics,
making one provider mandatory, adding an elevated adapter trust class, or
granting a materially broader data-use posture. Adding a conforming provider or
narrower reviewed rights profile does not by itself require supersession.
