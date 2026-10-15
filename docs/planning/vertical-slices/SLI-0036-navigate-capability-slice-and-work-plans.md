---
id: SLI-0036
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-roadmap-review
updated: 2026-10-15
parent: CAP-0008
depends_on: ["SLI-0034", "SLI-0035"]
decision_gates: []
---

# Vertical Slice: Navigate Capability, Slice, and Work Plans

## Outcome and User Scenario

From any roadmap entry, a repository operator follows stable browser links to a
product candidate or internal CAP, reviews its current public plan and complete
declared slice manifest, opens a refined or not-yet-refined slice, sees its
associated work packets, and opens each current work plan and public completion
evidence. All detail data is projected on refresh; no page is maintained by hand.

## Scope Boundaries

### In Scope

- Additive `roadmap-review-v1` hierarchy for internal capabilities using the
  same declared-slice, placeholder, refined-slice, and work representation as
  mapped product CAPs.
- Stable same-origin routes for candidates, internal CAPs, slices, and work;
  route resolution is against projected IDs/keys rather than filesystem paths.
- Candidate/CAP context, dependency and decision posture, complete slice lists,
  associated work lists, lifecycle state, source references, and safe public plan
  blocks rendered as semantic headings, paragraphs, lists, tables, and code text.
- Truthful unplanned, missing-refinement, empty-work, unknown-route, reload,
  breadcrumb, keyboard, focus, narrow-layout, theme, and bounded failure states.
- Focused projection, route, inert-rendering, DOM, security, and anti-rigidity
  tests plus updated operator guidance.

### Out of Scope

- Planning mutation, active Markdown/HTML, arbitrary source browsing, approval
  display, source editing, roadmap acceptance, agent or lease actions, external
  links inferred from Markdown text, hosted access, or learner-app integration.

## Canonical Context and Decisions

CAP-0008, completed SLI-0034 and SLI-0035 contracts, CAP-0003 hierarchy and
compatibility semantics, planning artifacts, interface/testing/security
standards, and the review-site/control-plane READMEs govern. This local read-only
extension needs no durable decision.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Client-side stable route resolver over an additively enriched live projection | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Generate one committed HTML file per planning artifact | no — creates copied pages and a regeneration burden | — | — | — | — | — | — | — | — |
| C. Pass source paths to a generic file endpoint and render Markdown directly | no — exposes arbitrary paths and active-content risk | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A preserves a single dynamic contract, stable deep links, and the
existing confinement boundary. It delivers useful missing-artifact views and
keeps ordinary navigation free of planning controls. Candidates B and C violate
the CAP's maintenance and security constraints.

## Boundary Path

The generic projector enriches every capability with its declared children and
existing work nodes. The repository adapter continues to provide allowlisted
planning artifacts. The loopback host serves only fixed route shapes, and the
TypeScript router resolves requested keys or IDs from the fetched projection.
The inert block renderer creates DOM nodes with `textContent`; it never parses
HTML, follows source paths, or executes plan content.

## Contracts, Data, and Provenance

`roadmap-review-v1` remains compatible and gains the existing `slices` hierarchy
on internal capability records. Candidate, CAP, slice, and work URLs contain
validated key/ID segments only. Documents remain the structured inert subset
with repository-relative source and the projection source fingerprint.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Candidate detail | Every candidate link opens its title, description, planning coverage, and mapped CAP detail when present | Route/DOM test |
| Internal CAP detail | An internal capability opens independently and lists every declared slice in manifest order | Projection/DOM test |
| Missing refinement | A declared but unrefined slice is clickable and explains that no detailed SLI artifact or work plan exists yet | Route/DOM test |
| Refined hierarchy | A refined slice opens its public plan and associated work; each work packet opens its current plan and completion evidence | Projection/DOM test |
| Safe plan rendering | Headings, text, lists, tables, and code remain inert text; HTML/script-like input cannot become active DOM | Parser/DOM/security test |
| Stable deep link | Reloading a valid detail URL serves the same shell and resolves from the newest projection | Server/integration test |
| Unknown route | Unknown keys and IDs yield a bounded not-found view with a roadmap return link, not a filesystem lookup | Route/server test |
| Anti-rigidity | Adding/refining an artifact requires no detail-page generation, route registration, approval, lease, or broad test run before it appears on refresh | Projection/command evidence |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0026 | Enrich the generic hierarchy and deliver safe dynamic candidate/CAP/slice/work detail routes, renderers, tests, and guidance | WRK-0025 | none | complete |

## Verification and Qualification

Run focused roadmap projection, server, client route/model/DOM/inert-rendering,
type, design, planning, documentation, aggregate readiness, and diff checks.
Cumulative browser-engine and assistive-technology qualification remains in
SLI-0037.

## Rollback and Migration

The projection change is additive and the site retains overview compatibility.
Rollback removes enriched internal hierarchy and detail rendering/routes. No
persisted application data or tracked generated page requires migration.

## Stop Conditions

Stop for arbitrary paths, active content, hand-maintained detail data, planning
mutation, inferred CAP mapping, changed CAP-0003 semantics, remote access, a new
theme system, missing keyboard/list alternatives, unresolved decision, or
material CAP drift.

## Documentation Impact and Completion Evidence

The generic projection now gives internal capabilities the same declared-slice,
refined-slice, placeholder, and associated-work hierarchy already used by mapped
product CAPs. The client resolves stable candidate, CAP, slice, and work routes
only from that projection and safely constructs plan headings, paragraphs,
lists, tables, and code with inert DOM text. Candidate and internal CAP context,
manifest order, work lists, source references, breadcrumbs, refresh, unknown
routes, unplanned candidates, and unrefined slices are all explicit.

`python dev-tools/control-plane/test_roadmap_review.py` passed 8 contract and
adapter tests; the focused server suite passed 7 API, deep-link, loopback,
read-only, traversal, asset, and bounded-failure scenarios; the client suite
passed 11 model, DOM, route, filter, theme, inert-content, and missing-state
scenarios; and TypeScript typecheck passed. Design-system validation reported
125 tokens and 56 icons; planning validated 53 artifacts; documentation
validated 176 Markdown files plus catalogs; diff checks passed; and aggregate
readiness passed all 25 checks. Socket and Vitest temp-cache restrictions
required their established runs outside the managed sandbox. Browser-engine
visual, zoom/reflow, and assistive-technology qualification is not claimed and
remains in SLI-0037. No migration, static detail generation, hosted exposure,
or product integration exists. The additive projection remains compatible and
the slice conforms to CAP-0008.

## Planning History

- 2026-10-15: Refined just in time after SLI-0035. Candidate A scored 14/14 and
  keeps all detail pages dynamic, inert, route-confined, and read-only.
- 2026-10-15: Activated after the implementation gate passed and WRK-0026 was
  claimed with exact scope and generated-output declarations.
- 2026-10-15: Moved to verification after the dynamic detail hierarchy passed
  focused and aggregate checks with browser qualification reserved for SLI-0037.
- 2026-10-15: Closed deterministically after WRK-0026 completed and the slice
  completion structure, documentation, evidence, and CAP conformance passed.
