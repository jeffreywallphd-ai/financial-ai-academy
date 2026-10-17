# Audit Module

Audit owns append-oriented provenance and integrity references. For the first
learning loop it records the identity and canonical digest of each validated
Assessment completion event plus actor/action and exact source provenance. It
does not own attempts, scores, completion state, mastery, or learner progress.

## Public operation

- `reconcile_lesson_completion(ReconcileLessonCompletionAuditRequest) -> AuditReconciliationReceipt`
- `reconcile_project_completion(ReconcileProjectCompletionAuditRequest) -> ProjectAuditReconciliationReceipt`

The operation obtains events only through Assessment's public replay query,
derives deterministic Audit IDs and canonical event digests, and appends one
record per source event. Exact replay is idempotent. Reuse of an event ID for
different content is a conflict and never overwrites the retained record.

## Persistence and limits

`audit_0001_assessment_completion_records` owns the append-only
`audit.assessment_completion_records` table. Update/delete triggers protect
accepted records, and the schema has no cross-module foreign keys. The receipt
exposes only count and source-set digest.

`audit_0002_project_completion_records` adds append-only integrity references
for validated `assessment.project.completed@1.0.0` events. Each record binds
event/evidence/submission identity, actor/action, exact Project, snapshot,
brief, placement, policy, occurrence, supersession, source time, and canonical
event digest without copying workspace state or becoming completion authority.
Exact replay is idempotent; changed reuse conflicts and ordinary update/delete
remain denied.

Synchronous reconciliation is not a queue, dispatcher, checkpoint, delivery
guarantee, export product, retention policy, recovery service, or managed-cloud
Audit posture.
