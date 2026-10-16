---
id: SLI-0035
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-roadmap-order-correction
updated: 2026-10-16
parent: CAP-0008
depends_on: ["SLI-0034"]
decision_gates: []
---

# Vertical Slice: Review Capability Order and Parallelism

## Outcome and User Scenario

A repository operator runs one local command and opens a responsive review
overview that accounts for all 26 product capability candidates. The page makes
planned versus unplanned state, current lifecycle, dependency-respecting
proposed order, accepted order when available, unresolved ties, blockers, and
evidence-backed parallel lanes understandable without treating a visual position
as authority. Refresh reprojects current sources through `roadmap-review-v1`.

## Scope Boundaries

### In Scope

- A loopback-default, GET/HEAD-only Python host for the dynamic projection and a
  fixed allowlist of review-site and shared design-system assets.
- A TypeScript overview client compiled automatically into ignored local output
  by the one start command; no committed roadmap data or manual build step.
- Exact 26-candidate accounting, planned/unplanned filters, text search, lifecycle
  summaries, proposed order, unresolved ties, blockers, internal capabilities,
  and parallel/unknown/incompatible evidence.
- Complete list/table alternatives, status text independent of color, explicit
  authority disclaimers, refresh status, stable capability links prepared for
  SLI-0036, and light/dark/system theme behavior.
- Focused server, view-model, DOM, TypeScript, accessibility-structure,
  responsive-style, confinement, read-only, and anti-rigidity tests.

### Out of Scope

- CAP/slice/work detail rendering, deep-link routing beyond preserving the
  capability key, visual graph manipulation, planning writes, approval display,
  agent activation, hosted access, remote clients, or product-app integration.

## Canonical Context and Decisions

CAP-0008, SLI-0034 and `roadmap-review-v1`, interface design standards and
tokens/icons, testing standards, security locality, and the control-plane README
govern. No new shared visual token or icon is required. No durable decision is
needed for a read-only loopback developer tool.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Dependency-light TypeScript client plus Python loopback host over `roadmap-review-v1` | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add the roadmap to the learner-facing React application | no — exposes repository planning through the product boundary | — | — | — | — | — | — | — | — |
| C. Commit a regenerated static HTML roadmap after every change | no — defeats live refresh and duplicates planning state | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A delivers the full operator overview with one local command, reuses
the existing projection and design assets, and remains isolated from the learner
application. Candidates B and C violate explicit CAP boundaries.

## Boundary Path

The loopback host invokes the Financial AI Academy roadmap adapter per API
request, returns the existing success envelope with `no-store`, and serves only
allowlisted static and shared design assets. The TypeScript client normalizes the
projection into overview summaries, filters and renders semantic HTML, applies
the shared theme contract, and preserves capability keys for the next slice.

## Contracts, Data, and Provenance

The host exposes `GET /api/roadmap` and fixed static routes only. It binds to
`127.0.0.1` by default, returns JSON UTF-8, disables API caching, and refuses
mutation methods and traversal. Client state contains only filter/theme choices;
planning data is not persisted. Every displayed source fingerprint comes from
`roadmap-review-v1`.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Start and refresh | One documented command compiles the client into ignored output, starts loopback, and each refresh obtains a current projection | Server/integration test |
| All candidates | Overview and count expose exactly 26 product candidates, including truthful unplanned states | Model/DOM test |
| Order | Planned items show CAP-0003 proposed order and unresolved ties; absence of accepted roadmap is explicit | Model/DOM test |
| Parallel evidence | Compatible sets are shown as parallel lanes; unknown and incompatible pairs remain clearly separate and never become safe | Model/DOM test |
| Filtering | Search and planned/status filters preserve truthful counts and provide an empty result state without mutating sources | DOM test |
| Read-only confinement | POST/PUT/DELETE, traversal, arbitrary files, non-loopback defaults, and unknown assets are refused | Server/security test |
| Theme/accessibility | Light/dark/system content parity, landmarks, headings, labels, keyboard controls, live refresh status, visible focus, narrow reflow, zoom, forced-color and reduced-motion styles are present | Component/style/browser qualification |
| Anti-rigidity | Ordinary review is one start command and browser refresh; it requires no planning approval, packet claim, lease, data generation command, or repository-wide suite | Command/test evidence |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0025 | Deliver the loopback read-only host and accessible TypeScript all-capability overview with focused server/client tests and operator guidance | WRK-0024 | none | complete |
| WRK-0081 | Render the allocator-derived current capability order and explicit sequential/parallel lanes while retaining future order as advisory context | WRK-0025, WRK-0080 | none | complete |

## Verification and Qualification

Run Python server tests, TypeScript typecheck, client model/DOM tests, focused
roadmap projection tests, design-system validation, documentation/planning
checks, aggregate readiness, and diff checks. Browser-engine screenshots and
assistive-technology qualification remain cumulative SLI-0037 evidence.

## Rollback and Migration

The site is additive developer tooling. It creates only ignored compiled client
output and no durable state. Rollback removes the host/client/tests/docs and the
ignored output can be regenerated or discarded safely.

## Stop Conditions

Stop for non-loopback exposure, any write endpoint, product-app integration,
duplicated ordering logic, persisted roadmap data, active plan rendering,
arbitrary paths, a new visual token/icon system, missing accessible alternative,
or material CAP drift.

## Documentation Impact and Completion Evidence

Delivered a separate local review site and documented its one-command start,
dynamic sources, ignored build output, security boundary, refresh behavior,
focused checks, and reusable `roadmap-review-v1` seam. The overview accounts for
all 26 candidates (five currently mapped to product CAPs and 21 explicitly
unplanned), keeps three internal enabling CAPs separate, and presents CAP-0003
order, ties, blockers, compatible/incompatible/unknown counts, and safe sets
without inventing authority or safety.

`python dev-tools/roadmap-review-site/test_server.py` passed 7 server, API,
loopback, read-only, traversal, asset, failure, and exact-count scenarios;
`node apps/web/node_modules/vitest/vitest.mjs run --globals --environment jsdom
dev-tools/roadmap-review-site/tests` passed 8 model and DOM scenarios; TypeScript
typecheck and the 8-test roadmap projection suite passed. Design-system
validation reported 125 tokens and 56 reviewed icons; planning validated 51
artifacts; documentation validated 174 Markdown files plus catalogs; diff checks
passed; and aggregate readiness passed all 25 checks. The focused server suite
required execution outside the managed socket sandbox and Vitest required its
established external temp-cache path; both passed there. Browser-engine visual,
zoom, and assistive-technology qualification is not claimed and remains in
SLI-0037. No migration, hosted exposure, product-app integration, or tracked
generated data exists. The implementation conforms to CAP-0008 and retains the
existing CAP/SLI/WRK vocabulary.

## Planning History

- 2026-10-15: Refined after SLI-0034 as the first usable browser overview.
  Candidate A scored 14/14 and retains detail navigation for SLI-0036.
- 2026-10-15: Activated after WRK-0025 passed the implementation gate and was
  claimed with bounded write scope.
- 2026-10-15: Moved to verification after delivering the complete dynamic
  overview and passing focused and aggregate automated evidence.
- 2026-10-15: Closed deterministically after WRK-0025 completed and the slice
  completion structure, evidence, documentation, and CAP conformance passed.
- 2026-10-16: Reopened through a bounded descendant correction after the order
  card was found to render broader future ordering rather than current
  executable allocation lanes.
- 2026-10-16: The review now renders the allocator's exact current order and
  explicit sequential/parallel groups while keeping future dependency order,
  blockers, and compatibility detail advisory and non-authorizing.
