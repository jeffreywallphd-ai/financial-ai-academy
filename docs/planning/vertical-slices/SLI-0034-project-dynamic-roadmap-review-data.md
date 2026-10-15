---
id: SLI-0034
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-roadmap-review
updated: 2026-10-15
parent: CAP-0008
depends_on: []
decision_gates: []
---

# Vertical Slice: Project Dynamic Roadmap Review Data

## Outcome and User Scenario

A repository operator or review client requests one current roadmap projection
and receives a versioned JSON document that accounts for all 26 product
capability candidates, maps explicitly associated formal CAPs, preserves
internal control-plane capabilities separately, and exposes CAP/SLI/WRK
hierarchy, public plan content, lifecycle state, dependency order, parallel
compatibility, diagnostics, and source freshness. The projection is rebuilt from
machine-readable catalog and planning sources; the Markdown register is checked
for parity but is not scraped as the runtime database.

## Scope Boundaries

### In Scope

- A versioned JSON companion to the product capability catalog with stable keys,
  order, descriptions, and explicit optional CAP mappings for exactly 26 items.
- Documentation validation that rejects catalog JSON/Markdown drift, duplicate or
  unknown keys and mappings, missing planned CAPs, and count/order violations.
- A project-neutral projection core for candidate inventory, governed hierarchy,
  order/compatibility facts, diagnostics, source fingerprints, and safe public
  plan sections.
- A Financial AI Academy adapter over the existing planning model and CAP-0003
  graph, ordering, and compatibility implementations.
- One read-only CLI/JSON command suitable for a later loopback review server.
- Focused tests for mapping, hierarchy, missing refinement, changed state,
  malformed sources, unknown/duplicate mappings, deterministic output, privacy,
  and adapter independence.

### Out of Scope

- Browser layout, local HTTP hosting, interactive navigation, visual graphs,
  roadmap acceptance, planning mutation, approval display, packet activation,
  file leases, static generated site data, hosted access, or remote execution.

## Canonical Context and Decisions

CAP-0008, CAP-0003, the product capability catalog, planning guide/register,
roadmap guidance, interface and testing standards, decision readiness, and the
reusable control-plane README govern. No unresolved durable decision applies to
this local read-only projection. Catalog identity/order is machine-readable;
governed planning state remains in planning artifacts and CAP-0003 projections.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Validated JSON catalog plus reusable live projection and repository adapter | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Parse `register.md` and the catalog Markdown table as the runtime database | no — brittle human formatting would become an accidental API | — | — | — | — | — | — | — | — |
| C. Commit prebuilt roadmap JSON after every planning change | no — creates a second manually synchronized source and violates refresh behavior | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A is the only eligible cut. It provides independently testable
operator value, reuses existing planning semantics, creates a stable contract
for later interface slices, and remains reversible and local. Candidates B and
C would create the maintenance burden the capability exists to remove.

## Boundary Path

The machine-readable product catalog and planning-artifact frontmatter/body feed
the Financial AI Academy adapter. The adapter consumes the existing portfolio
graph, order, and compatibility cores and supplies project-specific mapping and
source confinement. The generic projector emits `roadmap-review-v1` through the
existing control-plane success envelope. CLI output is the first host; the later
loopback server will consume the same projection without redefining it.

## Contracts, Data, and Provenance

`capability-catalog-v1` contains a version, exactly ordered candidate records,
stable keys, titles, descriptions, and optional formal CAP IDs. `roadmap-review-
v1` contains source fingerprints, candidate and internal capability groups,
hierarchical planning nodes, safe public document sections, order and
compatibility projections, and categorical diagnostics. It contains no ignored
approval/reviewer records, prompts, credentials, absolute paths, or raw active
HTML. Repository-relative source references and digests preserve provenance.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Current repository | Exactly 26 catalog candidates appear once; five explicitly mapped product CAPs resolve and CAP-0002, CAP-0003, and CAP-0008 remain separate internal capabilities | Adapter test |
| Unplanned candidate | Candidate remains present and clickable-by-key in the data contract with no invented CAP, dependency, order, or safety facts | Core/adapter test |
| Hierarchy | Every existing CAP exposes its manifest, refined slices, and work packets; missing just-in-time children are placeholders with diagnostics | Projection test |
| Order and parallel facts | Planned capability order and compatibility are the exact CAP-0003 results for the same inputs and retain unresolved or unknown evidence | Integration test |
| Source change | A changed lifecycle or plan body changes the fingerprint and next projection without a generation command or tracked output | Freshness test |
| Catalog drift | JSON/Markdown mismatch, count drift, duplicate key/order, unknown CAP mapping, or duplicate formal mapping fails with bounded diagnostics | Documentation/adapter test |
| Unsafe content | Markdown HTML/script/image content is represented only as escaped or inert structured text; traversal and non-allowlisted sources are refused | Parser/security test |
| Privacy | Projection contains no ignored ledger content, local actor/reviewer identity, prompts, credentials, or absolute paths | Privacy test |
| Reuse | Generic projector tests use `PROGRAM`/`INCREMENT`/`TASK` identifiers and import no Financial AI Academy adapter | Conformance test |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0024 | Deliver the versioned machine-readable catalog, reusable dynamic projection, Financial AI Academy adapter, read-only CLI, parity validation, focused tests, and operator documentation | none | none | complete |

## Verification and Qualification

Run the focused roadmap projection suite, existing portfolio graph/order/
compatibility suites, control-plane CLI tests, documentation validation,
planning validation, generic import/privacy checks, aggregate readiness, and
diff checks. This slice has no browser or hosted qualification.

## Rollback and Migration

The change adds a catalog companion, projector, adapter, command, tests, and
documentation. It does not migrate product or control-plane state. Rollback
removes the additive command and companion only after restoring catalog parsing
for existing CAP-0003 behavior; no generated runtime projection is retained.

## Stop Conditions

Stop for catalog/product-doc conflict, a mapping that requires title inference,
changed CAP-0003 semantics, arbitrary filesystem access, active content, ignored
authority disclosure, a second maintained planning source, generic-core imports
of project vocabulary, or any need for remote access or mutation.

## Documentation Impact and Completion Evidence

Delivered `capability-catalog-v1` with exactly 26 contiguous, unique candidates
and explicit mappings to CAP-0001 and CAP-0004 through CAP-0007. Delivered the
vocabulary-neutral `roadmap-review-v1` projector, inert Markdown subset, source
fingerprints, Financial AI Academy adapter, and read-only `roadmap-review` CLI.
The focused roadmap suite passed 8 tests; portfolio graph, ordering, and
compatibility suites passed 7 each; control-plane lifecycle passed 10; planning
validated 49 artifacts; documentation validated 172 Markdown files plus both
catalogs; Python compilation and diff checks passed; and aggregate readiness
passed 25 checks. The sandboxed lifecycle run first encountered the known
Windows temporary-directory permission limit, then passed through its established
unsandboxed route. Browser, hosted, and remote-access qualification are outside
this data-only slice and remain for later CAP-0008 slices. No migration or
generated tracked data was introduced, and the slice remains within CAP-0008.

## Planning History

- 2026-10-15: Refined just in time as the first CAP-0008 slice. Candidate A
  scored 14/14 and conforms to the approved package without adding a decision
  gate or a static regeneration workflow.
- 2026-10-15: Delivered and verified the machine catalog, reusable live
  projection, repository adapter, read-only CLI, parity validation, and focused
  safety, privacy, freshness, and reuse evidence.
