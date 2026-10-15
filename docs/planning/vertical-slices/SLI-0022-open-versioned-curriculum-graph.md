---
id: SLI-0022
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-15
parent: CAP-0005
depends_on: []
decision_gates: []
---

# Vertical Slice: Open a Versioned Curriculum Graph

## Outcome and User Scenario

An authenticated learner opens one approved curriculum and sees its exact
version, objectives, competencies, activities, required and optional branches,
and relationship structure in an accessible map/list. The view is produced
from a validated Curriculum-owned graph, preserves exact Content and Assessment
references, and makes no eligibility, mastery, or adaptive-ranking claim.

## Scope Boundaries

### In Scope

- A versioned Curriculum-owned graph with stable identities for curricula,
  objectives, competencies, activities, branches, and relationships.
- Exact lesson-placement and assessment-placement references for activities,
  including the referenced immutable package or assessment version and digest.
- Deterministic validation for duplicate or missing identities, dangling
  references, unsupported contract versions, disallowed cycles, invalid branch
  membership, and ambiguous graph structure before publication.
- An immutable approved graph version, Curriculum application read operation,
  Curriculum-owned PostgreSQL persistence, protected API operation, generated
  TypeScript client, and accessible learner-facing map/list route.
- Provenance and source-fingerprint fields sufficient to reproduce the graph
  shown to a learner and distinguish later curriculum versions.
- Focused anti-rigidity coverage proving that optional branches, unordered
  sibling presentation, and alternate valid graph shapes do not require a new
  contract or a particular visual layout.

### Out of Scope

- Completion, prerequisite satisfaction, eligible/locked/unavailable states,
  or explanation codes; those belong to SLI-0023.
- Activity launch, return context, current-position markers, or curriculum
  version-change behavior; those belong to SLI-0024.
- Mastery inference, recommendations, adaptive ranking, waivers, authoring,
  enrollment, catalog discovery, tenancy, or external-learning standards.
- Browser-authored graph mutation, collaborative drafts, model-generated
  relationships, or moving graph authority outside Curriculum.

## Canonical Context and Decisions

- [CAP-0005](../capabilities/CAP-0005-navigate-competency-based-curriculum.md)
  defines the approved outcome, scope, slice order, and material-change bounds.
- [Product Capability Catalog](../../product/capability-catalog.md), [Product
  Vision and Scope](../../product/product-vision-and-scope.md), and the [Initial
  Glossary](../../domain/glossary.md) govern learner value and terminology.
- [Module Map](../../architecture/modules/module-map.md) and [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
  assign graph and prerequisite meaning to Curriculum while Content and
  Assessment retain their exact-version resources.
- [Adaptive Pathway Architecture](../../architecture/learning/adaptive-pathway-architecture.md)
  requires deterministic eligibility before future adaptation; this slice
  intentionally stops before eligibility.
- [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md) and
  the [Contract Architecture](../../architecture/contracts/contract-architecture.md)
  govern immutable referenced content and generated public clients.
- [Interface Design System](../../design/README.md), [Style Guide](../../design/style-guide.md),
  and [Interface Design Standards](../../standards/interface-design-standards.md)
  govern equivalent accessible map/list behavior in both themes.
- CAP-0001 is complete and supplies exact lesson, assessment, and completion
  boundaries. No unresolved decision in the decision-readiness register applies
  to this read-only deterministic curriculum graph.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Versioned Curriculum graph through persistence, protected API, and accessible map/list | yes | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 13 |
| B. Define only graph schemas and domain records | no - no learner-observable increment | - | - | - | - | - | - | - | - |
| C. Build a browser-only curriculum-map prototype | no - makes layout data authoritative and bypasses Curriculum validation | - | - | - | - | - | - | - | - |
| D. Add graph fields to the discovery projection | no - discovery classification and curriculum structure have different ownership and lifecycle | - | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is the only eligible end-to-end increment. It scores full marks for
observable learner value, decision readiness, bounded independence, focused
verification, and additive rollback. Contracts score one because exact public
field names and compatibility cases must be frozen immediately before
WRK-0058; that bounded refinement does not alter the approved outcome or
boundary path. SLI-0023 is not eligible until this graph exists, SLI-0024 depends
on SLI-0023, and SLI-0025 is the final capability qualification. The approved
manifest order therefore resolves the selection without a tie.

## Boundary Path

1. Versioned JSON schemas and compatibility fixtures define one immutable
   learner-readable curriculum graph and bounded denials.
2. Curriculum domain records and application policy validate identities,
   references, branches, and relationships and expose approval/read operations.
3. A Curriculum repository port and PostgreSQL adapter persist immutable graph
   versions and their provenance without reaching into Content or Assessment
   tables.
4. The API host independently authorizes graph reads, maps public types to the
   OpenAPI contract, and regenerates the TypeScript client.
5. The web application renders the same semantics as a responsive map and list
   using shared tokens and reviewed icons, with the list remaining the robust
   accessible representation.
6. Contract, unit, integration, API, component, and live-browser checks qualify
   the exact path. Learner-model, adaptation, and job-provider layers are
   intentionally absent.

## Contracts, Data, and Provenance

The slice adds a `curriculum-graph-v1` contract beneath
`contracts/learning/curriculum/v1/` plus compatibility fixtures and bounded
denials. The graph carries a stable curriculum identity, semantic version,
graph digest, publication state, title and summary, ordered presentation hints,
objectives, competencies, activities, branches, typed relationships, and exact
public placement references. Relationship meaning is an allowlisted enum;
presentation order never changes graph semantics. Activities refer through
Curriculum's public lesson or assessment placements rather than provider or
storage payloads.

Curriculum owns immutable graph-version rows and constituent records. Each read
returns the approved version, graph digest, publication timestamp, and bounded
source references needed to explain what was shown. The API returns no draft,
provider-specific, author identity, approval-ledger, or browser-derived state.
Adding a valid optional branch or choosing list-first rendering must not require
a schema version change.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Approved graph | An authorized learner opens one curriculum and sees its exact version, objectives, competencies, activities, branches, and typed relationships in map and list views | API/component/browser |
| Exact references | Every lesson or assessment activity resolves to the exact public placement and immutable version/digest recorded by Curriculum | Domain/integration |
| Invalid identity or reference | Duplicate identities and dangling objective, competency, activity, branch, or relationship references fail before publication with stable bounded denials | Contract/domain |
| Invalid topology | A disallowed cycle, ambiguous root, invalid branch membership, or unsupported relationship/version fails before learner visibility | Contract/domain |
| Unauthorized read | Missing or insufficient server-issued permission returns the standard protected denial without revealing graph existence or content | API integration |
| Missing or corrupt version | An unknown, incomplete, digest-mismatched, or non-approved graph is unavailable and never silently falls forward to another version | Repository/application integration |
| Optional valid shape | Zero or multiple optional branches, additional objectives, and differently ordered siblings remain valid without code or schema changes | Contract/domain anti-rigidity test |
| Layout independence | The complete graph remains usable through the semantic list when the visual map is unavailable, narrow, zoomed, keyboard-only, or reduced-motion | Component/browser accessibility |
| Theme and viewport parity | Light, dark, system theme, narrow, and wide presentations retain equivalent content, actions, hierarchy, focus, and contrast | Browser/design-system check |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0058 | Establish versioned curriculum-graph contracts, compatibility corpus, Curriculum domain records, validation policy, and focused anti-rigidity tests | none | none | complete |
| WRK-0059 | Persist immutable approved graph versions and expose the protected Curriculum read operation through OpenAPI and the generated client | WRK-0058 | none | complete |
| WRK-0060 | Deliver the accessible responsive curriculum map/list route using the public generated client and shared design system | WRK-0059 | none | active |
| WRK-0061 | Qualify the live graph path, provenance, authorization, invalid-state behavior, accessibility, theme parity, and documentation | WRK-0060 | none | captured |

## Verification and Qualification

Run graph-schema and compatibility conformance tests; Curriculum domain and
application unit tests; migration and PostgreSQL repository integration tests;
protected API and OpenAPI regeneration checks; generated-client usage checks;
web model, component, accessibility, and browser tests; design-system and
architecture checks; documentation and planning validation; diff checks; and
`python dev-tools/agent/check_ready.py`. WRK-0061 must exercise the composed
application with real PostgreSQL and the web host, not only transport stubs.

Every packet must include an anti-rigidity assertion appropriate to its layer:
extensions through allowlisted relationship values and optional branches,
adapter independence, list-first fallback, or checks that distinguish governed
invariants from presentation preferences.

## Rollback and Migration

The graph contract, endpoint, route, and storage are additive. The migration has
an explicit down path that removes only Curriculum graph tables after consumers
are withdrawn. Immutable approved versions require no rewrite of CAP-0001
evidence. Rollback disables the route and read operation before reversing the
migration; it never mutates lesson, assessment, discovery, or learner evidence.

## Stop Conditions

Stop and return to shaping or decision review if implementation requires
mutable collaborative authoring, external-standard semantics, cross-tenant
catalogs, manual eligibility overrides, model-generated graph authority,
mastery or ranking claims, client-authoritative validation, cross-curriculum
credit, or ownership outside Curriculum. Also stop for conflicting canonical
sources, an unresolvable exact Content/Assessment reference, authorization
policy expansion, or a contract change that would alter a frozen packet set.

## Documentation Impact and Completion Evidence

Update the learning-contract index, Curriculum and host READMEs, API contract,
generated-client guidance, web feature documentation, and planning artifacts.
Completion evidence must record affected boundaries, focused and aggregate
checks, migration and rollback evidence, live browser qualification, design and
accessibility results, anti-rigidity coverage, assumptions, known gaps, and
confirmation that eligibility and adaptation remain outside this slice.

## Planning History

- 2026-10-15: Refined just in time as the first eligible CAP-0005 slice.
  Candidate A scored 13/14, remained inside the approved CAP package, and added
  no decision or approval gate.
- 2026-10-15: Activated through the bounded WRK-0058 claim after the current
  CAP package, manifest, decision readiness, dependencies, and write scope were
  revalidated.
- 2026-10-15: Completed WRK-0058 with the versioned graph schema, portable
  domain seam, bounded timestamp identity rules, compatibility corpus, and
  focused flexibility and denial evidence. WRK-0059 is dependency-ready.
- 2026-10-15: Refined WRK-0059 just in time around immutable JSONB aggregate
  storage behind the Curriculum repository port, exact placement admission,
  protected exact-version transport, and generated-client qualification.
- 2026-10-15: Activated WRK-0059 after revalidating the approved CAP package,
  completed dependency, decision posture, generated artifacts, and exact write
  scope.
- 2026-10-15: Completed WRK-0059 with immutable PostgreSQL graph versions,
  exact-reference admission, protected exact-version transport, generated
  client output, real-database evidence, and cross-layer flexible-graph
  qualification. WRK-0060 is dependency-ready for just-in-time refinement.
- 2026-10-15: Refined WRK-0060 just in time around an exact-version generated
  client loader, closed whole-response validation, and semantically equivalent
  accessible list/map views with direct excessive-rigidity checks.
- 2026-10-15: Activated WRK-0060 under the current CAP package after the
  implementation gate passed and the control plane issued its durable claim.
