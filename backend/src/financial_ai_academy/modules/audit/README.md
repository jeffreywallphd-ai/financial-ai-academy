# Audit Module

Audit owns append-oriented provenance and integrity references. For the first
learning loop it records the identity and canonical digest of each validated
Assessment completion event plus actor/action and exact source provenance. It
does not own attempts, scores, completion state, mastery, or learner progress.

## Public operation

- `reconcile_lesson_completion(ReconcileLessonCompletionAuditRequest) -> AuditReconciliationReceipt`
- `reconcile_project_completion(ReconcileProjectCompletionAuditRequest) -> ProjectAuditReconciliationReceipt`
- `read_published_lesson_lineage(ReadPublishedLessonLineageRequest) -> LineageView`
- `read_knowledge_check_completion_lineage(ReadKnowledgeCheckCompletionLineageRequest) -> LineageView`

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

The isolated browser/headless Project qualification correlates both accepted
Assessment occurrences with exactly two append-only Audit references, then
proves their identities and integrity digests remain unchanged across exact
replay and a normal application restart.

Synchronous reconciliation is not a queue, dispatcher, checkpoint, delivery
guarantee, export product, retention policy, recovery service, or managed-cloud
Audit posture.

## Pure provenance contract

`domain/provenance.py` and `adapters/provenance_contract.py` implement the
provider-neutral `provenance/v1` contract core. The core validates exact
Content, Assessment, and Audit references; canonicalizes owner envelopes; and
validates bounded acyclic learning-lineage views with explicit incomplete
links. Nodes are root-distance ordered and the complete public meaning is bound
by a deterministic SHA-256 view digest.

This pure seam does not read a repository, compose live owner records, resolve
identity or permission, expose HTTP, or change the existing reconciliation
operations. Content and Assessment remain authoritative for their records, and
a lineage reference grants no access or grading, mastery, causal, legal, or
financial meaning. The shared-core lineage service now reads exact published
lessons through Content's public operation, completion events through
Assessment's public replay seam, and retained integrity references only from
the Audit-owned table. The Content adapter omits lesson body, assets, source
locators, and authoring state.

Completion lineage reconciles idempotently, selects one exact evidence
occurrence, reads its retained Audit reference under the server-bound learner
and placement context, and composes a validated canonical view. It adds no
table or cross-module foreign key.

`POST /api/v1/audit/learning-lineage` exposes the two closed roots through the
same protected OpenAPI-generated contract for browser and headless callers. It
requires server-issued `audit.lineage.read` and `curriculum.lesson.read`, binds
the completion learner from the opaque session, and accepts no learner or
permission selector. Local composition injects the Content adapter into Audit;
the host maps the validated view without reading a repository or recomputing a
graph. The disposable local qualification proves generated-client and ordinary
HTTP parity for both roots, confidential denials, exact replay after a normal
host restart, and unchanged non-Identity database and bounded owner-file state
after the first deterministic reconciliation. It does not establish a hosted
retention, recovery, export, or managed-cloud posture.
