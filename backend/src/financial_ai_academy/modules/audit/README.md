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
- `read_published_lesson_accountable_history(ReadPublishedLessonLineageRequest) -> AccountableHistoryDocument`
- `read_knowledge_check_completion_accountable_history(ReadKnowledgeCheckCompletionLineageRequest) -> AccountableHistoryDocument`
- `export_published_lesson_accountable_history(ReadPublishedLessonLineageRequest) -> PortableEvidenceExport`
- `export_knowledge_check_completion_accountable_history(ReadKnowledgeCheckCompletionLineageRequest) -> PortableEvidenceExport`

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

`domain/cross_domain_provenance.py` and
`adapters/cross_domain_provenance_contract.py` implement the separate additive
`provenance/v2` owner-reference value and mapping core. Immutable profile-
specific identities cover the nine closed profiles and both explicit financial
account/analysis variants. The core enforces owner, label, relation, identity,
resource-ID, digest, time, and source bounds; normalizes times and source order;
and produces the same canonical envelope digest as the frozen language-neutral
contract runner. One malformed document fails locally without a mutable
registry or impact on v1.

This v2 core does not make future owners real. It has no graph, retained record,
repository, migration, provider/model call, new public operation, authorization
decision, or browser surface. A v2 reference carries evidence meaning only and
grants no access, quality, mastery, financial, administrative, or execution
authority.

`ports/cross_domain_provenance.py` and
`application/cross_domain_conformance.py` add a reusable, stateless owner-
adapter qualification seam. A future owner declares one closed profile and
issues one typed envelope. The kit returns only a profile-bound canonical
digest or a bounded failure code/reference, isolates one failing adapter, and
supports partial adoption without a fixed adapter count. Duplicate declarations
fail without choosing an adapter, and complete qualification requires every
closed profile exactly once.

The synthetic adapters beside the v2 contract tests are test-only proofs. They
do not make a provider, dataset, model, execution, calculation, recommendation,
administrator, or Project integration real. Product code does not import them,
and the conformance kit performs no I/O or registration.

`adapters/project_snapshot_reference.py` is the first real v2 owner adapter. It
calls only Project's public exact-snapshot operation, using learner identity
solely to authorize that read, and issues the minimal observed Project snapshot
identity, revision, digest, and close-time reference. Learning-started and
independent Projects share this origin-neutral seam. Learner identity, origin,
workspace content, resource details, paths, URLs, bytes, storage coordinates,
and Project persistence never enter the envelope. Other owner adapters remain
future work.

The cumulative v2 qualification replaces only the synthetic Project profile
with that real adapter, then runs the same profile-ordered conformance suite.
Complete nine-profile and varied partial subsets remain deterministic under
input reordering, and a Project failure cannot disable unrelated profiles.
This evidence does not turn the other eight synthetic profiles into product
owners or create an all-or-nothing runtime registry.

The additive `accountable-history/v1` executable contract now freezes a
purpose-limited read model over an already authorized learning-lineage root.
It defines reviewed plain display text, bounded exact technical facts, safe
diagnostics, explicit gaps, redaction category counts, deterministic disclosed-
content digests, and an ephemeral portable evidence wrapper. Its executable
contract runner imports no Audit product code. The shared core described below
now supplies the composer and strict mapping adapter, but adds no permission,
public operation, endpoint, generated client, browser, persistence, migration,
retained export, tenant/admin policy, provider/model action, or history change.

`domain/accountable_history.py` and
`adapters/accountable_history_contract.py` implement the framework-free shared
core for that contract. The composer accepts only a validated learning-lineage
view and one closed purpose, then derives ordered history entries, explicit
gaps, safe diagnostics, bounded redaction counts, reviewed purpose/root/state
copy, canonical disclosed-content digests, and an on-demand portable wrapper.
Valid lessons with zero, one, or many reviewed sources use truthful generic
summary copy rather than assuming one fixture shape. Equivalent source order
and time offsets normalize to the same result; changed disclosed meaning changes
the digest.

The strict adapter admits and emits only the exact v1 mapping. It has no
application, Identity, host, framework, database, filesystem, network, clock,
provider, or model dependency. It does not authorize a root, load lineage,
retain an export, create a file, authorize a request, or grant grading, mastery,
legal, compliance, financial, administrative, or execution authority. The
application operations and protected transport below provide the bounded read
seam without changing those core limits.

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

`POST /api/v1/audit/accountable-history` exposes learner review and
`POST /api/v1/audit/accountable-history/export` exposes the separate on-demand
portable wrapper. The host selects purpose, derives completion learner identity
from the opaque session, requires separate `audit.history.read` or
`audit.history.export` authority plus `curriculum.lesson.read`, and returns the
same strict core mapping to browser or headless callers. No export record, file,
path, owner payload, or alternate policy route is created.

The disposable local qualification derives both exact roots through public
operations, compares generated-client and ordinary authenticated HTTP
inspection/export documents, repeats them before and after a normal host
restart, and checks confidential missing-session, query, and guessed-completion
denials. Once the completion selector has refreshed its existing rebuildable
Learner-model projection, accountable-history-only operations leave every non-
Identity schema and the bounded application-data tree unchanged. The test
accepts variable bounded entries, transformations, gaps, diagnostics,
redactions, Unicode, and timestamps rather than freezing one fixture count or
prose shape. It does not establish retained export, public hosting, tenant,
legal, recovery, or managed-cloud behavior.
