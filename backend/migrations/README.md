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

The Curriculum Assessment-reference stream under `curriculum/` is applied
after the root stream. The Assessment evidence/outbox stream under
`assessment/` is applied after Curriculum. Migration IDs are globally unique
in `platform.schema_migrations`; controlled teardown removes module streams in
reverse dependency order before rolling back the root stream.

The same Curriculum stream owns
`curriculum_0002_discovery_projection`. It stores immutable catalog
classifications separately from the replaceable singleton discovery generation
and its ordered records. Replacement is one database transaction, so an
interrupted rebuild retains the prior complete generation. These derived rows
have no cross-module foreign key and may be dropped and rebuilt without
removing Content versions or lesson placements.

The Learner-model stream under `learner_model/` owns only rebuildable completion
projection/history tables. It retains Assessment identifiers as source
references without a cross-schema foreign key or direct Assessment-table read.
Dropping that stream removes derived state only; rebuilding still requires the
authoritative Assessment evidence set to remain available.

The Audit stream under `audit/` owns append-only Assessment-event integrity and
provenance references. It has no cross-schema foreign keys. Unlike the
Learner-model projection, accepted Audit records reject ordinary update/delete;
teardown is limited to controlled development/test rollback and must not be
described as harmless evidence rebuilding.
