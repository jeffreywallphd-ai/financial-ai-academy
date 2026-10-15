# Learning Discovery Contract

- Status: implemented for the initial approved-lesson application core
- Canonical for: discovery v1 record, owner-fact provenance, projection rebuild, and fixed browse meaning
- Parent capability: [CAP-0004](../../planning/capabilities/CAP-0004-discover-learning-opportunities.md)
- Executable schemas: [Learning Discovery v1](../../../contracts/learning/discovery/v1/README.md)
- Compatibility evidence: [Discovery v1 corpus](../../../contracts/compatibility/discovery/v1/README.md)

## Ownership and Authority

Learning discovery is a Curriculum-owned read projection, not a new semantic
module. Content remains authoritative for exact package identity, immutable
version/digest, title, objectives, publication state, and provenance.
Curriculum remains authoritative for exact placement/destination, catalog
summary and classification, prerequisite summary, availability, and rebuild
policy. The projection may copy those public facts for query use but cannot
publish content, authorize access, grant eligibility or enrollment, or promise
that an activity can execute.

The current profile accepts only `lesson` records backed by an exact existing
Curriculum placement and a successful exact Content public read. The closed
`course`, `lab`, and `project` vocabulary supports later portable records but
does not authorize fabricated destinations or undelivered execution.

## Record and Projection Identity

Discovery v1 records carry stable opportunity and placement IDs, an exact
same-origin lesson destination, kind, title, catalog summary, objectives,
sorted topic slugs, level, estimated minutes, prerequisite summary,
availability and reason, exact package version/digest, publication provenance,
a source fingerprint, and projection time. They contain no learner or provider
identity, package body, answer, object key, database row, ranking score,
eligibility result, recommendation, or financial-performance meaning.

The source fingerprint is SHA-256 over compact sorted-key UTF-8 JSON for every
visible owner fact except `source_fingerprint` and `projected_at`. A projection
generation is SHA-256 over the stably ordered records after projection time is
removed and each source fingerprint is retained. Records order by normalized
title and then opportunity ID; this is deterministic presentation order, not
relevance or personalized ranking. Curriculum owns that ordering rule and
validates it before publication, including Unicode `casefold()` behavior. A
consumer must preserve the published order and may validate the ordered
generation digest, but should not recreate a language-specific normalization
algorithm that could disagree with the authoritative projection.

## Registration, Rebuild, and Failure

Registration validates bounded identifiers/text, closed enums, sorted unique
topics, duration, exact placement, and exact Content version. Repeating
identical facts is idempotent; reusing an opportunity ID with different facts
is an immutable conflict.

Rebuild collects and validates every record before requesting one atomic
projection replacement. Missing placements, missing or mismatched exact
Content, unsupported records, and source corruption publish no partial
generation. Adapter failure retains the last complete generation. Browse
rejects an absent, unsorted, or digest-mismatched projection rather than
returning stale or partial data.

## Persistence and Protected Browse

Curriculum migration `curriculum_0002_discovery_projection` stores immutable
lesson classification separately from one replaceable ordered generation.
Generation state and records are committed atomically behind a transaction
lock; a failed replacement rolls back to the prior complete generation. Stored
rows are reconstructed through the same public value types and are rejected if
their count, order, fingerprint, generation, or bounded fields no longer
validate.

The queryless `GET /api/v1/curriculum/opportunities` operation exposes the
closed browse envelope through the reviewed OpenAPI snapshot and generated
TypeScript client. Identity issues `curriculum.discovery.read` in the current
single-profile context, and the host checks it independently before invoking
Curriculum. The client cannot select a learner, permission, projection, sort,
or filter.

The static web application consumes that generated operation at `/learn` and
validates the entire closed envelope before presenting any records. It retains
the server-validated projection order without locally reimplementing
Curriculum's Unicode ordering policy or adding ranking. It accepts an empty or
variable valid catalog including distinct opportunities that share one
placement, recomputes every owner-fact source fingerprint after applying the
contract's UTC publication-time normalization, and recomputes the ordered
generation digest. It fails the whole response closed on unknown fields,
malformed identity/destination/digest/calendar values, duplicate opportunity
identities, incoherent projection timestamps, or integrity mismatch. Only a
contract-valid available lesson links to its exact placement destination;
other kinds and availability states remain explanatory and non-executable.

## Compatibility and Remaining Work

The compatibility corpus fixes one synthetic exact approved lesson and bounded
codes for unsupported versions/kinds, unsafe destinations, malformed records,
source tamper, and generation tamper. Focused unit evidence covers replay,
conflict, exact-source denial, all-or-nothing replacement, stable ordering, and
output confidentiality.

Real PostgreSQL evidence covers replay, immutable conflict, empty generations,
transaction interruption, stored corruption, and the protected HTTP read of
the exact persisted generation. Focused API evidence covers denial before
disclosure, insufficient or client-selected permission, bounded failure, and
stable OpenAPI/client generation. The isolated local qualification additionally
admits one exact package and placement, registers its catalog classification,
atomically rebuilds the projection, and browses from `/learn` into that exact
lesson through one same-origin Python/static host over PostgreSQL 18.4.

Production/background rebuild scheduling, search/filter/pagination semantics,
non-lesson destinations, background indexing, external providers, tenancy, and
managed-cloud operation remain later boundaries.
