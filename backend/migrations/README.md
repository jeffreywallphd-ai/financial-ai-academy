# PostgreSQL Migrations

Migrations are forward-applied in filename order and checksum-locked after
application. Every `*.up.sql` file has a matching `*.down.sql` file for
controlled development/test rollback. Production rollback policy may select a
forward fix instead, but it must never edit an already-applied migration.

Content and Curriculum own separate schemas and tables. Curriculum stores exact
Content identifiers without a cross-module foreign key or direct Content-table
read.

Module-specific migration streams live in named subdirectories. The Identity
stream is applied after the root Content and Curriculum stream so later slices
do not invalidate the earlier stream's deterministic migration inventory.

The Project stream is applied after Content and Curriculum. Project owns
`project.project_shells`; its rows retain learner ownership, idempotency
fingerprint, immutable accepted origin, lifecycle, revision, and UTC times
without a cross-schema foreign key. The empty development down migration is
reversible, but it fails closed when retained Project rows exist.

`project_0002_workspace_snapshots` adds the mutable revision-guarded Project
workspace aggregate, accepted mutation replays, opaque content-addressed
artifact references, and immutable snapshot rows with the exact closed
workspace record. Artifact bytes remain outside PostgreSQL behind the Project
object port. Snapshot rows reject ordinary update/delete. Controlled
development rollback applies the workspace down migration before the shell
down migration and refuses to discard any retained workspace, artifact,
mutation, or snapshot record.

The Curriculum Assessment-reference stream under `curriculum/` is applied
after the root stream. The Assessment evidence/outbox stream under
`assessment/` is applied after Curriculum. Migration IDs are globally unique
in `platform.schema_migrations`; controlled teardown removes module streams in
reverse dependency order before rolling back the root stream.

`assessment_0002_practice_evidence` adds Assessment-owned practice attempts,
definition-ordered response and score rows, completion results, and a bounded
practice outbox. It depends on the `assessment_0001` schema and append-only
trigger function but uses separate additive tables so existing knowledge-check
evidence is not reinterpreted. Development/test teardown removes practice
tables before the knowledge-check stream; retained evidence is never described
as safely down-migratable.

`assessment_0003_practice_progress` adds server-revisioned mutable drafts,
exact-scope transaction-lock rows, and stable attempt order. Existing attempts
become order 1 while retained result and completion-event JSON stay unchanged.
The former one-completion uniqueness constraint becomes an exact-scope/order
constraint so the application can enforce the immutable definition's bounded
retry policy under a row lock. Drafts are mutable work, not evidence. The down
migration is for controlled development only and fails rather than deleting or
collapsing retained evidence when a scope contains more than one attempt.

The same Curriculum stream owns
`curriculum_0002_discovery_projection`. It stores immutable catalog
classifications separately from the replaceable singleton discovery generation
and its ordered records. Replacement is one database transaction, so an
interrupted rebuild retains the prior complete generation. These derived rows
have no cross-module foreign key and may be dropped and rebuilt without
removing Content versions or lesson placements.

`curriculum_0003_curriculum_graphs` adds one append-only approved graph
aggregate per Curriculum ID and semantic version. Root columns are constrained
to the validated JSONB meaning, and a trigger rejects ordinary update/delete.
The table has no Content or Assessment foreign key; graph admission proves the
exact Curriculum-owned placement references before insert, and the adapter
revalidates the whole portable graph on read.

`curriculum_0005_practice_review_targets` adds append-only exact mappings from
one Curriculum-owned practice placement and complete review-resource identity
to an available exact lesson destination or explicit unavailable reason. The
mapping has no Assessment or Content persistence dependency and never stores
feedback, learner evidence, or content bytes.

`curriculum_0006_project_brief_placements` adds append-only exact placements
for approved Project briefs. Each placement binds an existing exact Curriculum
graph and lesson activity to the matching Content package and brief. The table
stores only public identities, versions, digests, and creation time; it has no
Content or Project persistence dependency. Development rollback refuses to
drop retained placements.

The Learner-model stream under `learner_model/` owns only rebuildable completion
projection/history tables. It retains Assessment identifiers as source
references without a cross-schema foreign key or direct Assessment-table read.
Dropping that stream removes derived state only; rebuilding still requires the
authoritative Assessment evidence set to remain available.

`learner_model_0002_practice_history` adds rebuildable exact-scope roots and
ordered safe item-summary rows for zero through ten practice attempts. One
transaction replaces a complete history and its source digest; interrupted
replacement rolls back to the prior complete projection. The tables contain no
Assessment foreign key and are not mastery or eligibility evidence.

The Audit stream under `audit/` owns append-only Assessment-event integrity and
provenance references. It has no cross-schema foreign keys. Unlike the
Learner-model projection, accepted Audit records reject ordinary update/delete;
teardown is limited to controlled development/test rollback and must not be
described as harmless evidence rebuilding.
