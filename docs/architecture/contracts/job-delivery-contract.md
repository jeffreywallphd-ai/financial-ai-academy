# Durable Job Delivery Contract

- Status: accepted
- Canonical for: provider-neutral durable job, attempt, lease, outcome, retry, cancellation, and dead-letter meaning
- Decision: [ADR-0018](../../adr/ADR-0018-allowlisted-adapters-postgresql-at-least-once-jobs.md)

## Purpose

This contract lets application modules request durable asynchronous work without
depending on PostgreSQL query shapes, a future broker payload, or a provider's
job model. Exact executable schemas and storage layout belong to CAP delivery.

## Job Envelope

A canonical job records:

- stable job ID, owning module, operation ID, and operation contract version;
- bounded input reference plus immutable digest, never an embedded secret;
- target provider/capability when applicable, without raw provider job payload;
- accepted request, actor, learner, and organization context references as
  applicable, with authorization rechecked at execution and commit boundaries;
- idempotency key and effect scope;
- creation time, priority class, not-before time, deadline/timeout policy,
  attempt limit, retention class, and trace/provenance references; and
- current state derived from append-preserving attempt and transition facts.

The envelope is versioned and bounded. Unknown security- or effect-relevant
fields fail closed. Sensitive values are referenced through owned stores and
redacted diagnostics, not copied into the queue.

## Delivery and Ownership

Delivery is at least once. A claim creates a unique attempt and bounded lease
with a fencing value. Only the current lease owner may renew, record progress,
or publish a terminal outcome. Lease expiry makes unfinished work eligible for
redelivery and prevents a stale worker from committing a later result.

Exactly-once execution and exactly-once external effects are not claimed.
Handlers must make effects idempotent or reconcile an uncertain outcome before
retry. The job record never treats a timeout as proof that a provider stopped.

## State and Failure Meaning

The contract distinguishes at least:

- pending or deferred work;
- actively leased work and its attempt;
- succeeded work with bounded outcome references;
- cancelled work, including requested versus confirmed cancellation;
- timed-out or deadline-exceeded work without implied external rollback;
- retryable failure waiting under bounded policy;
- permanent, policy-denied, invalid, or exhausted failure; and
- dead-lettered poison work awaiting an authorized disposition.

Exact labels may evolve, but these meanings cannot be collapsed. Prior attempts
and failures remain inspectable after retry or manual disposition.

## Retry, Cancellation, and Reconciliation

Automatic retry applies only to explicit transient classifications and remains
bounded by attempts, elapsed time, cost/quota policy, and shutdown controls.
Invalid, unauthorized, incompatible, policy-denied, and permanent failures do
not retry automatically.

Pending cancellation prevents a new claim. Active cancellation is cooperative:
the handler checks the request and lease/fence before authoritative commit.
External work that cannot be confirmed stopped is marked uncertain and routed
to reconciliation rather than reported as cancelled or retried unsafely.

Manual retry, release, cancellation, or reconciliation requires an allowlisted
authorized operation, creates an auditable transition, and does not mutate the
original request or erase attempts.

## Transaction and Publication Boundary

When a source state change and job share PostgreSQL, enqueue is atomic with the
state change or its outbox fact. A successful handler publishes its owned
application result and terminal outcome atomically where possible. Cross-system
effects use idempotency and reconciliation rather than a distributed-transaction
claim.

## Degradation

A stopped worker, unavailable provider, exhausted quota, or poison job degrades
only dependent capabilities. Backpressure is explicit and bounded. Core flows
that do not require the job system remain usable, and the system never silently
substitutes another provider or broadens permissions to clear work.

## Portability

PostgreSQL is the initial store and lease implementation. A future external
broker adapter must preserve this envelope, state, fencing, idempotency,
cancellation, uncertainty, retry, audit, and degradation meaning. Broker receipt
or provider job IDs stay adapter data rather than domain meaning.
