# ADR-0018: Allowlisted Adapters with PostgreSQL At-Least-Once Jobs

- Status: accepted
- Date: 2026-10-15
- Decision request: [DEC-0017](../planning/decision-requests/DEC-0017-provider-admission-and-job-delivery-baseline.md)

## Context

Replaceable providers need executable adapters, secrets, outbound connections,
health, failure handling, and durable work. Treating adapter discovery as code
admission or claiming queue guarantees without a state machine could turn the
provider layer into an arbitrary plugin loader, duplicate external effects, or
lose work after crashes.

The initial product is a Python modular monolith with separate API and worker
hosts and PostgreSQL as its transactional system of record. A built-in durable
job store fits that shape and avoids committing every deployment to an external
broker or provider-host protocol before isolation and scale evidence exists.

## Decision

Use allowlisted packaged adapters and PostgreSQL-backed at-least-once job
delivery for the initial provider and background-work baseline.

### Provider Admission

- The initial executable provider set is closed and explicit. Each admitted
  adapter is identified by provider family, platform provider ID, adapter and
  contract versions, package origin and digest, reviewed trust class, declared
  dependencies, and an allowlist entry shipped or configured through an
  authorized deployment path.
- Admission requires a closed capability manifest, configuration schema,
  secret references, outbound hosts, data classes, resource bounds, health and
  disablement behavior, provider-specific current evidence, and reusable
  conformance results. Admission does not itself configure, select, enable, or
  license a provider.
- Only reviewed packaged adapters in the initial trusted class may execute in an
  application or worker process. Runtime download, arbitrary module paths,
  editable source discovery, dependency installation, entry-point scanning,
  and marketplace-style code activation are excluded.
- Inspection, manifest validation, configuration validation, and health
  reporting do not execute unadmitted code. Secrets are resolved by the host at
  the narrow invocation boundary and never stored in manifests or job payloads.
- An adapter that requires stronger isolation is not admitted to the in-process
  class. A future out-of-process host may implement the same provider port, but
  requires a separate durable decision and qualification for protocol,
  identity, tenancy, secrets, filesystem, network, resources, upgrades,
  observability, shutdown, and incident response.

### Durable Job Delivery

- PostgreSQL stores versioned canonical job, attempt, lease, outcome, and
  dead-letter metadata. A job is created transactionally with the application
  state or outbox fact that requires it when those records share the database.
- Delivery is **at least once**. A worker crash, lease expiry, uncertain provider
  response, or handoff failure may cause redelivery. The platform does not claim
  exactly-once execution or exactly-once external effects.
- Every job identifies its owner and operation/contract version, bounded input
  reference and digest, provider or capability target when applicable,
  request/actor/organization context allowed by accepted identity policy,
  idempotency key, priority class, attempt limit, time/deadline policy, and
  provenance references. Payloads contain no secrets or opaque provider job
  objects as platform meaning.
- Workers claim bounded leases with an attempt identity and fencing value,
  heartbeat or renew while active, and commit outcomes only while ownership is
  current. Expired work is eligible for redelivery; stale workers cannot publish
  a later authoritative outcome.
- Handlers are idempotent at the application-effect boundary. They use durable
  deduplication, compare-and-set/fencing, provider idempotency keys, or explicit
  reconciliation appropriate to the effect. Unknown external outcomes are
  reconciled before retry when repeating the effect could be harmful.
- Retry is bounded and policy-driven. Only classified transient failures retry
  automatically with bounded delay. Permanent, invalid, unauthorized, policy-
  denied, exhausted, or poison work becomes a visible terminal or dead-letter
  state without blocking unrelated jobs.
- Cancellation is explicit and best effort. Pending work can be prevented from
  starting; active work observes cancellation cooperatively and rechecks its
  lease/fence before committing. A timeout or cancellation does not claim that
  an external provider stopped or that an external side effect was reversed.
- Manual retry, dead-letter release, disablement, or reconciliation is an
  authorized, audited operation that preserves prior attempts and cannot edit a
  failed payload into a different hidden request.

### Future Broker and Host Seams

Application code targets provider and job-delivery ports, not PostgreSQL query
types or broker payloads. A future external broker may implement the same
canonical job and outcome semantics. A future provider host may implement the
same platform-owned provider ports for a separately admitted trust class.

Neither seam grants present authority. Selecting an external broker or
out-of-process runtime requires a new durable decision, migration and replay
design, failure-semantic comparison, local/cloud capability behavior, security
review, and conformance evidence. The PostgreSQL baseline remains usable when
those optional adapters are absent.

ADR-0016 remains controlling for financial experiment execution. Provider
admission and durable jobs do not authorize an experiment sandbox, arbitrary
code execution, package installation, or network/secret access for learner
artifacts.

## Consequences

- The first provider set and worker can share the modular-monolith release and
  PostgreSQL transaction boundary with fewer operational dependencies.
- At-least-once truthfully exposes duplicates and uncertain external outcomes,
  making idempotency and reconciliation mandatory rather than implicit.
- PostgreSQL throughput and isolation are bounded; evidence may later justify a
  broker or out-of-process host without changing application job meaning.
- A closed adapter allowlist reduces extension flexibility initially but avoids
  presenting arbitrary third-party code as safely supported.
- Adapter absence, provider outage, or poison work can degrade only dependent
  capabilities; unrelated core learning and native workflows remain usable.

## Alternatives Rejected

- **Isolated provider hosts plus an external broker from the first release.**
  Rejected because host protocol, sandbox/runtime, broker, deployment, secret,
  replay, and operations choices are not yet justified by evidence.
- **In-memory tasks or fire-and-forget background work.** Rejected because they
  cannot supply durable crash/restart, audit, cancellation, or recovery meaning.
- **Exactly-once delivery claims.** Rejected because worker and provider
  failures can leave uncertain effects; idempotency and reconciliation are the
  honest boundary.
- **Dynamic entry-point or directory discovery.** Rejected because discovering
  code is not reviewing or authorizing it.
- **Retry every failure.** Rejected because permanent and poison work can create
  retry storms, cost, duplicate effects, and broad service degradation.

## Boundaries

This decision does not admit a named provider, approve provider terms or data
licenses, choose an external broker, define organization tenancy, select a
cloud platform, approve arbitrary plugins, or provide a sandbox. It does not
guarantee job latency, throughput, availability, retention, RPO, RTO, or
exactly-once effects.

Exact schemas, SQL, lease durations, retry schedules, priority policy, worker
concurrency, retention, and operational limits remain CAP/slice work within
this semantic boundary.

## Verification Implications

- Prove only exact allowlisted package identities can activate and that
  inspection, invalid configuration, missing secrets, or unknown packages do
  not execute code.
- Run each provider-family conformance corpus across success, malformed output,
  timeout, cancellation, quota, health, disablement, redaction, and provenance.
- Exercise atomic enqueue, concurrent claims, lease expiry, stale-worker
  fencing, crash/restart, duplicate delivery, idempotent replay, retry
  exhaustion, poison work, cancellation races, timeout, and dead-letter release.
- Prove secrets and raw sensitive/provider payloads are absent from job metadata
  and bounded diagnostics.
- Prove unknown external outcomes reconcile before unsafe retry and operator
  actions preserve all attempts and audit references.
- Prove unavailable providers, a stopped worker, or one dead-letter class does
  not block unrelated synchronous or job capabilities.
- Qualify backup/restore, migrations, cleanup, retention, observability, and
  local/cloud parity before operational support claims.

## Supersession

An external broker, a new delivery guarantee, dynamic executable discovery, an
out-of-process provider runtime, a new trust class, unbounded retries, or an
experiment execution provider requires a superseding or extending ADR. Adding
an allowlisted adapter or conforming job operation does not necessarily require
supersession when it remains within this boundary and has current evidence.
