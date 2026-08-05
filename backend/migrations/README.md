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
