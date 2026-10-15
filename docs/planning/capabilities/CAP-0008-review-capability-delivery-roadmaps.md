---
id: CAP-0008
kind: capability
planning_status: complete
authority: noncanonical
owner: codex-roadmap-review
updated: 2026-10-15
parent: null
depends_on: ["CAP-0003"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0034", "SLI-0035", "SLI-0036", "SLI-0037"]
---

# Capability: Review Capability Delivery Roadmaps

## Outcome

A repository operator can open a local review site that presents all 26 product
capability candidates, including candidates that have not yet been shaped into
formal `CAP-*` packages, and can distinguish catalog intent from governed
planning state. The site shows the dependency-respecting proposed CAP order,
accepted-roadmap order when one exists, and evidence-backed parallel-executable
groups without representing missing planning evidence as approval or safety.

From that overview, the operator can navigate from a planned capability to its
current CAP package, from the CAP to every declared slice, from each refined
slice to its work packets, and from each work packet to the current plan and
completion evidence. The presentation is generated from a versioned
machine-readable capability-catalog manifest, CAP/SLI/WRK frontmatter and plan
sections, accepted roadmap state, and the CAP-0003 portfolio projections. The
Markdown planning register remains a synchronized human index and validation
target, not the site's runtime database. A normal source change becomes visible
on refresh without manually rebuilding roadmap cards or copying plan prose into
a second maintained dataset.

## Users and Value

Repository operators and reviewers need one legible place to understand what is
planned, what is only a catalog candidate, what is ready or blocked, why work is
ordered, and where parallel delivery is supported. Markdown artifacts and JSON
projections remain authoritative, but they are slow to review as a portfolio and
make hierarchy traversal unnecessarily laborious.

Value is observable when an operator can account for all 26 catalog capabilities
exactly once, inspect every available CAP/SLI/WRK plan without searching the
repository, see missing refinement as an explicit state, and identify concurrent
lanes with the same rationale as the reusable portfolio control plane. Future
planning and completion changes appear without a hand-edited visual roadmap.

## In Scope

- A project-neutral, read-only roadmap-review projection that composes a
  machine-readable candidate manifest, structured artifact metadata and plan
  sections, roadmap state, and reusable portfolio order and compatibility
  results behind a project-specific adapter.
- A versioned JSON capability-catalog manifest with stable candidate keys,
  catalog order, titles, descriptions, and optional formal CAP mappings for all
  26 product capabilities. Documentation validation keeps it synchronized with
  the human product catalog; the site does not scrape a Markdown table for its
  candidate inventory.
- A stable mapping contract from catalog keys to formal CAP packages. Mappings
  are explicit rather than inferred from similar titles. Internal control-plane
  capabilities remain visible but are presented separately from the 26 product
  catalog candidates.
- Exact accounting for all 26 current product catalog candidates, including an
  explicit unplanned state and the absence of a formal CAP identifier, slice
  manifest, dependency order, or parallel-safety evidence when those facts do
  not yet exist.
- Dependency-respecting proposed order, accepted-roadmap order when available,
  ready/blocked rationale, parallel-safe sets, incompatible pairs, and narrowly
  isolated unknown compatibility derived from CAP-0003 rather than reimplemented
  in the interface.
- A local, loopback-default review server with a versioned read-only JSON
  boundary and a TypeScript interface that uses the repository design system.
- An overview for lifecycle, decision posture, dependency order, parallel lanes,
  progress, missing refinement, and source freshness, with filters and accessible
  non-graph alternatives for every visual relationship.
- Clickable CAP and catalog-candidate views. Planned CAP views expose bounded
  package sections and the complete declared slice manifest; unplanned candidate
  views expose catalog intent and clearly state which planning details do not
  yet exist.
- Clickable slice views that expose the current slice plan and associated work
  packets, including declared-but-not-refined work where the parent plan records
  it, plus clickable work-packet views for exact work plans and public completion
  evidence.
- Safe structured rendering of repository Markdown without executing embedded
  HTML, scripts, links, images, or other active content. File access is confined
  to allowlisted planning, roadmap, and catalog sources.
- Refresh-on-navigation or explicit refresh behavior that reprojects current
  repository state without committing generated roadmap data or requiring a
  manual site-content regeneration step.
- Light, dark, and system themes; keyboard and assistive-technology navigation;
  visible focus; responsive reflow; 200 percent zoom; reduced-motion and
  forced-color behavior; and status communication that does not depend on color.
- Focused projection, API, component, browser, security, freshness, and
  anti-rigidity tests, including malformed or missing artifacts and changing
  completion states.

## Out of Scope

- Treating the site, catalog inclusion, a visual position, or a parallel-safe
  recommendation as CAP approval, roadmap acceptance, product priority, packet
  authority, or permission to start implementation.
- Inventing dependencies, ordering, formal CAP identities, slice manifests,
  work packets, completion facts, or parallel safety for the unplanned catalog
  candidates.
- Editing planning artifacts, recording approvals or reviewer data, accepting a
  roadmap, claiming work, acquiring file leases, starting agents, committing,
  merging, pushing, publishing, or deploying from the site.
- Copying ignored local approval/reviewer identity or authority records into the
  browser payload, telemetry, screenshots, tracked fixtures, or generated files.
- A hosted or remotely accessible planning service, multi-user collaboration,
  organization tenancy, authentication, distributed scheduling, notifications,
  or production operations dashboard.
- Replacing planning artifacts, the human planning register, accepted roadmaps,
  or control-plane JSON contracts as their respective sources of truth. The
  machine-readable catalog manifest owns stable candidate identity and order;
  it does not acquire planning authority.
- Embedding the operator site in the learner-facing product application or
  exposing repository planning files through the product API.
- Creating 26 formal CAP packages merely to populate the visualization. Formal
  shaping remains a separate governed activity.

## Canonical Context

- [Product Capability Catalog](../../product/capability-catalog.md)
- [Automated Development Planning](../README.md)
- [Planning Register](../register.md)
- [Concurrent Automated Work](../concurrent-work.md)
- [Implementation Roadmaps](../../roadmaps/README.md)
- [Interface Design System](../../design/README.md)
- [Interface Design Standards](../../standards/interface-design-standards.md)
- [Testing and Verification Standards](../../standards/testing-and-verification-standards.md)
- [Decision Readiness](../../adr/decision-readiness.md)
- [CAP-0003: Plan and Orchestrate Capability Portfolios](CAP-0003-plan-and-orchestrate-capability-portfolios.md)
- [Reusable Local Control Plane](../../../dev-tools/control-plane/README.md)

## Decision Gates and Constraints

- CAP-0003 remains the source of dependency order, readiness, compatibility,
  parallel grouping, and allocation semantics. The review site may adapt and
  present those results but may not fork their rules or turn a proposal into
  authority.
- The versioned capability-catalog JSON manifest supplies the complete candidate
  inventory, stable identity, and catalog order. CAP/SLI/WRK frontmatter and
  artifact bodies supply governed planning state and readable plan sections.
  The Markdown register is checked for synchronization but is not parsed as the
  primary runtime data source. When a candidate has no mapped CAP, the site must
  say so rather than synthesizing one.
- No accepted active roadmap currently exists. Until one is accepted, displayed
  sequencing is labeled as a dependency-respecting proposal with unresolved ties
  preserved. Accepted roadmap order takes precedence when canonical state later
  provides it.
- Unknown compatibility is not parallel-safe. It isolates only the affected
  item or pair and includes bounded remediation; it does not serialize all
  unrelated work.
- The site is read-only and loopback-default. It has no arbitrary path parameter,
  raw filesystem browser, shell surface, active Markdown, approval mutation, or
  ignored-ledger payload.
- A browser request reprojects or reads a safely cached projection whose source
  fingerprint is checked. Generated data remains ephemeral and is never a
  separately edited planning source.
- The generic projection and view contracts do not assume CAP/SLI/WRK names.
  Financial AI Academy vocabulary, catalog-manifest shape, planning frontmatter,
  register synchronization, source roots, and design-system integration belong
  in adapters.
- The operator interface uses TypeScript and the existing semantic tokens and
  reviewed icon pack. It does not create a feature-local palette, spacing scale,
  theme map, icon set, or inaccessible graph-only representation.
- Any future remote access, write capability, automatic agent activation,
  identity-bearing collaboration, or approval interaction requires a separate
  durable security/identity review and material CAP reshaping.

No unresolved identity, tenancy, provider, licensing, model-authority, queue,
encryption, recovery, commercial, or external-execution decision is required
for this local read-only capability.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0034 | An operator or interface client receives one versioned roadmap-review projection that accounts for all 26 catalog candidates from a validated JSON manifest, maps available formal CAPs by stable key, preserves internal capabilities separately, and joins CAP/SLI/WRK frontmatter and public plan sections with lifecycle/completion state, proposed or accepted order, compatibility, and source freshness without exposing ignored approval data. | First; reuses CAP-0003 graph, order, and compatibility cores and establishes the generic projection contract plus Financial AI Academy catalog-manifest/planning-artifact adapter. The Markdown register is a parity check, not runtime storage. | Inventing formal plans or dependencies, scraping the human register as a database, copying plan prose into maintained generated data, exposing arbitrary files or ignored authority, changing CAP-0003 planning semantics, or coupling the generic core to CAP/SLI/WRK vocabulary changes the CAP package. | captured |
| SLI-0035 | The operator opens a responsive local roadmap overview that visibly accounts for all 26 product capabilities, distinguishes planned, unplanned, blocked, ready, active, verifying, and complete states, and presents dependency order, unresolved ties, and evidence-backed parallel lanes with accessible list/table alternatives. | After SLI-0034; consumes only the versioned projection. May be refined in parallel with SLI-0036 once the projection and route contracts are stable and their detailed write scopes are disjoint. | Editing or accepting plans, implying authority from placement, hiding unknown evidence, embedding the tool in the learner application, or creating a second ordering/compatibility engine changes the CAP package. | captured |
| SLI-0036 | From any overview item, the operator navigates through dynamically projected capability or candidate details, a CAP's complete declared slice list, a slice's plan and associated work list, and each work packet's plan and public completion evidence, with truthful empty and missing-artifact states and stable deep links. | After SLI-0034; shares the projection and route contracts with SLI-0035. The CAP-to-slice-to-work hierarchy must be preserved, and missing just-in-time artifacts remain navigable placeholders rather than broken links. | Rendering active Markdown or arbitrary paths, adding planning mutations, treating a missing child as an error that blocks unrelated review, or maintaining copied detail pages changes the CAP package. | captured |
| SLI-0037 | The dynamic review site is qualified for source-change freshness, exact 26-candidate accounting, hierarchy integrity, order/parallel consistency with CAP-0003, malformed and missing inputs, path and content confinement, privacy, light/dark/system parity, keyboard and assistive-technology use, responsive/zoom/forced-color/reduced-motion behavior, and anti-rigidity budgets. | Last; depends on SLI-0034 through SLI-0036 and reconciles commands, documentation, reusable-core guidance, and known gaps. | A mandatory static regeneration step, unrelated full-suite requirement for ordinary refresh, safety weakened for convenience, hosted exposure, or approval/agent activation behavior changes the CAP package. | captured |

SLI-0035 and SLI-0036 may be refined concurrently after SLI-0034 only when
their WRK scopes and generated outputs are reciprocal and conflict-free. Their
implementation remains subject to exact-file coordination. SLI-0037 is the
cumulative integration and qualification slice.

## Capability Acceptance

The capability is acceptable when evidence demonstrates that:

- the current catalog yields exactly 26 product capability entries, each shown
  exactly once with its catalog title and description, whether or not a formal
  CAP package exists;
- catalog candidates map deterministically to formal CAP packages only through
  stable explicit keys, duplicate or unknown mappings fail with bounded
  diagnostics, and internal control-plane CAPs do not displace or masquerade as
  product catalog candidates;
- an unplanned candidate remains useful and clickable while clearly showing that
  no governed CAP ID, manifest, dependencies, approval state, order, or parallel
  safety has been established;
- planned CAP status, dependency and decision posture, declared slice manifest,
  refined children, work packets, and public completion evidence agree with
  structured planning frontmatter and source artifacts, while the Markdown
  register remains synchronized as a human index;
- dependency-respecting order, accepted sequence when present, ready/blocked
  reasons, unresolved ties, compatible groups, incompatible pairs, and unknown
  evidence agree with CAP-0003 outputs for the same repository revision;
- visual parallel lanes never convert unknown or merely unplanned candidates
  into safe concurrent work and do not serialize unrelated evidence-backed work;
- every planned CAP is clickable, every declared slice is represented and
  clickable even before detailed refinement, every refined slice lists its
  associated work, and every existing work packet opens its current plan and
  public completion evidence through a stable deep link;
- source changes to the catalog manifest, CAP/SLI/WRK frontmatter or plan text,
  roadmap, or completion state appear after refresh without a committed
  static-data rebuild, while manifest/register drift and malformed or
  temporarily inconsistent sources produce a bounded diagnostic and preserve
  unaffected review paths;
- Markdown-derived content is rendered from an allowlisted structured subset,
  active content is inert, external navigation is explicit, arbitrary paths and
  traversal are refused, and ignored approval/reviewer content never enters a
  browser response;
- the server binds to loopback by default, has no write endpoint, and an
  ordinary review requires one start command plus browser navigation without a
  CAP approval, file lease, packet claim, full-suite run, or generated roadmap
  commit;
- light, dark, and system themes contain equivalent information and controls;
  keyboard order, visible focus, landmarks, headings, status announcements,
  200 percent zoom, narrow-screen reflow, reduced motion, forced colors, and
  relevant assistive-technology behavior meet the interface standards;
- focused tests exercise direct success, missing/unrefined children, newly
  shaped CAP mapping, lifecycle and completion changes, catalog-count drift,
  cycles or blocked order, incompatible and unknown pairs, malformed Markdown,
  traversal attempts, stale-cache detection, empty roadmaps, and server failure;
- the projection and route core is reusable with a non-Financial-AI-Academy
  adapter and does not require CAP/SLI/WRK identifiers, while this repository's
  adapter retains its own vocabulary and design integration; and
- documentation names the start, refresh, build, test, troubleshooting, and
  extension paths and distinguishes direct automated evidence from manual or
  external accessibility qualification.

## Risks and Non-Goals

- A polished visualization can imply priority or authority that the underlying
  sources do not possess. Every proposed, tied, unknown, unplanned, or blocked
  state must remain explicit in text, not only color or geometry.
- Catalog-to-CAP title inference can silently misassociate work, so it is not an
  authority mechanism. Stable explicit catalog keys are required; missing,
  unknown, or duplicate mappings fail closed without hiding the candidate.
- Rendering repository text creates an injection and path-disclosure risk. The
  server returns structured escaped content from fixed roots and never sends
  arbitrary files, raw ignored state, or active HTML.
- Dynamic projection can become sluggish or brittle if every request launches
  redundant subprocesses. Caching may use source fingerprints but must never
  require a manual regeneration step or conceal staleness.
- Graph layouts can create accessibility and small-screen barriers. The ordered
  list/table representation is complete and authoritative; any visual graph is
  supplementary.
- This CAP does not plan the remaining product candidates, decide their
  dependencies, or accept a roadmap. It makes absence and uncertainty visible.

## Documentation Impact

Delivery is expected to add the versioned machine-readable capability-catalog
manifest and its Markdown parity check; update the reusable control-plane or
review-site README, planning-tool or operator commands, relevant architecture
and assurance pages, the interface style guide only if a genuinely shared
pattern changes, the design-system consumer documentation, context routing when
new paths require it, and known verification gaps. The planning register changes
with each refined SLI/WRK artifact but remains a human index; generated review
projections remain untracked runtime data.

## Completion Evidence

All four approved manifest slices and their dependency-ordered packets are
complete. SLI-0034 delivered the validated 26-item JSON product catalog,
vocabulary-neutral inert roadmap projector, Financial AI Academy adapter,
source fingerprints, and read-only control-plane command. SLI-0035 delivered the
one-command loopback host and accessible TypeScript overview for planning state,
dependency order, ties, blockers, and conservative parallel evidence. SLI-0036
delivered stable candidate/CAP/slice/work routes, complete internal and mapped
hierarchies, useful unplanned/unrefined states, and inert plan details. SLI-0037
integrated proportionate fixed qualification, live browser evidence, known-gap
reconciliation, and anti-rigidity protection.

The reusable boundary remains `capability-catalog-v1` plus
`roadmap-review-v1`: the generic core imports no CAP/SLI/WRK or Financial AI
Academy vocabulary, while this repository's adapter owns mapping, source roots,
planning terms, and design integration. The Markdown register is a synchronized
human index, not runtime storage. Browser refresh dynamically reprojects current
catalog, plan, lifecycle, order, and compatibility sources; no static roadmap or
detail-page generation exists.

Final cumulative evidence passed 10 projection/adapter tests, 8 live server and
security/freshness tests, 11 TypeScript model/DOM/route tests, 6 dependency-free
site qualification tests, strict TypeScript checking, and 3 live Chromium
Playwright scenarios with zero axe violations. Chromium evidence covers exact
26 accounting, product and internal capabilities, refined and missing slices,
work details, inert plan content, unknown routes, keyboard skip focus,
light/dark/system themes, 360-pixel reflow, reduced motion, forced colors, and
bounded API failure. The first narrow-screen browser run exposed horizontal
overflow; the responsive grid/table constraints were corrected and the complete
browser suite passed afterward. Design validation passed for 125 tokens and 56
icons, planning integrity passed for 55 artifacts, documentation integrity
passed for 178 Markdown files plus context and product catalogs, Python
compilation and diff checks passed, local readiness passed 27 checks, and the
CI profile passed 26 checks.

The fixed roadmap safety net remains dependency-free and does not require Node,
a socket, Chromium, an approval, a claim, a lease, a full UI suite, or generated
data for unrelated work. Focused Node/socket/browser evidence remains available
for affected interface changes. Manual screen-reader operation, actual browser
200-percent zoom controls, non-Chromium browsers, non-Windows visual baselines,
hosted access, and remote/multi-user operation were not performed and remain
either documented verification gaps or explicit CAP non-goals. No migration,
backup, commit, merge, push, publication, deployment, credential use, or
production mutation was required. CAP-0008 conforms to its approved package and
is complete without a lower-level or final approval stage.

## Planning History

- 2026-10-15: Shaped from the requested dynamic all-capability review site as a
  separate operator-facing capability dependent on completed CAP-0003. The
  complete provisional manifest is SLI-0034 through SLI-0037; the plan preserves
  all 26 product catalog candidates without inventing formal planning state for
  candidates that have not yet been shaped.
- 2026-10-15: All four approved manifest slices passed deterministic completion
  and cumulative fixed, focused, browser, accessibility, security, freshness,
  privacy, and anti-rigidity qualification; CAP-0008 moved to `complete` without
  a slice, packet, implementation, completion, or final approval stage.
