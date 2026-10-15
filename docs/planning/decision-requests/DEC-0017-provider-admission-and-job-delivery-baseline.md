---
id: DEC-0017
kind: decision-request
planning_status: captured
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
decision_record: null
---

# Decision Request: Choose the Provider Admission and Job Delivery Baseline

## Decision Needed

Choose the initial trust/admission and isolation classes for replaceable
providers and the asynchronous job-delivery semantics required to invoke them,
including retries, idempotency, cancellation, timeout, and dead-letter handling.

## Why Now

Provider governance, local operation, managed cloud, and operator health need a
coherent execution boundary. Loading adapters and dispatching durable work are
one trust path; choosing them implicitly risks arbitrary code execution or
unprovable delivery guarantees.

## Current Authority and Constraints

Providers implement versioned platform-owned ports and cannot define domain or
licensing authority. Provider admission/sandbox technology and queue/delivery
guarantees are decision-required. The modular monolith and shared local/cloud
core remain fixed; arbitrary plugin marketplaces are excluded.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Allowlisted packaged adapters plus PostgreSQL-backed at-least-once jobs | Fits the modular monolith, limits dependencies, and can provide transactional job metadata with idempotent handlers. | Adapters share process trust unless separately hosted; throughput and isolation are bounded. | Provider manifest/admission, process boundary, job schema, leasing, retry/idempotency, health and operations. | Medium-high; an external broker/host can implement the same port later. |
| B. Isolated provider hosts plus external broker from the first release | Stronger isolation and scalable delivery primitives. | Requires host protocol, sandbox/runtime, broker selection, deployment, secrets, networking, replay, and larger operations surface. | Provider RPC, sandbox, broker/job contracts, deployment, telemetry, recovery and conformance. | Medium-low; infrastructure becomes a supported baseline. |

## Recommendation

Option A for the first bounded provider set, with strict allowlisting,
capability manifests, startup/conformance checks, idempotent handlers, and an
explicit path to out-of-process adapters for elevated trust classes.

## Evidence Required

- Provider threat classes and adapter supply-chain review.
- Job state machine, transactional boundary, idempotency, retry, cancellation,
  timeout, crash/restart, and poison-message corpus.
- Local and cloud load/failure prototype and operational cost comparison.
- Criteria that force an adapter out of process or require a broker decision.

## Required Authority

Architecture/platform authority with security, operations, provider-domain,
data, recovery, and cost review.

## Decision Record and Promotion

Promote the selected baseline to an ADR, provider/job contracts, security and
deployment architecture, operations, and decision readiness.

## Dependent Planning Updates

Reconcile CAP-0024, CAP-0027, CAP-0028, CAP-0029, and any execution-dependent CAP.

## Planning History

- 2026-10-15: Captured as the shared provider execution and job-delivery gate.

