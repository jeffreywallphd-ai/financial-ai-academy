# Provider and Durable-Job Operations

- Status: accepted design boundary; tooling and production qualification are gaps
- Canonical for: operator-visible provider activation and PostgreSQL job handling under ADR-0018
- Decision: [ADR-0018](../adr/ADR-0018-allowlisted-adapters-postgresql-at-least-once-jobs.md)

## Startup and Readiness

Startup validates exact allowlisted adapter identity/digest, manifest and
contract versions, configuration shape, secret references, outbound-host and
data-class declarations, and current admission state before activation. Missing,
disabled, incompatible, or unhealthy adapters report bounded capability state
without preventing unrelated core startup.

Worker readiness reports database connectivity, migration compatibility, claim
ability, backlog/oldest-work age, active leases, retry/dead-letter counts, and
provider health using bounded non-sensitive dimensions. Readiness does not
execute unadmitted adapter code or send test learner/provider payloads.

## Routine Handling

- Retry is automatic only for classified transient failure within the job's
  bounded attempt, time, quota, and cost policy.
- Cancellation is reported as requested, acknowledged, confirmed, or uncertain
  as applicable; timeout never implies an external provider stopped.
- Dead-letter release, manual retry, provider disablement, and reconciliation
  are explicit authorized actions with reason and durable audit references.
- Operators inspect canonical job IDs, operations, attempts, classifications,
  age, and bounded diagnostics, not secrets or raw learner/provider payloads.
- Unknown external outcomes are reconciled through the adapter before any retry
  that could repeat a harmful or costly effect.

## Shutdown, Maintenance, Backup, and Restore

Graceful shutdown stops new claims, allows bounded completion, records or
expires leases honestly, and never marks unfinished external work successful.
Maintenance and recovery coordinate API writes, workers, scheduled creation,
and providers as required by the accepted operation.

Backup/restore qualification must preserve canonical job and attempt history,
but ordinary workers and providers remain disabled during restore. Activation
reconciles expired/uncertain leases and authorization/provider state before
redelivery. A restore does not replay external effects merely because a job was
nonterminal at capture time.

## Incident Boundaries

Provider outage, quota exhaustion, retry storm, poison work, database pressure,
and stale workers must have bounded circuit, concurrency, and disablement
responses. One provider or job class cannot consume unbounded capacity or block
unrelated synchronous and asynchronous work.

No latency, throughput, availability, retention, RPO, RTO, or exactly-once
claim is supported until controlled qualification establishes it for a named
profile and limit set.
