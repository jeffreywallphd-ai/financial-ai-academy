---
id: WRK-0024
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-roadmap-review
updated: 2026-10-15
parent: SLI-0034
capability: CAP-0008
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["docs/product/capability-catalog.json", "docs/product/capability-catalog.md", "dev-tools/control-plane/roadmap_review.py", "dev-tools/control-plane/financial_academy_roadmap_review.py", "dev-tools/control-plane/control_plane.py", "dev-tools/control-plane/test_roadmap_review.py", "dev-tools/control-plane/README.md", "dev-tools/documentation/check_docs.py", "docs/planning/register.md", "docs/planning/capabilities/CAP-0008-review-capability-delivery-roadmaps.md", "docs/planning/vertical-slices/SLI-0034-project-dynamic-roadmap-review-data.md", "docs/planning/work-packets/WRK-0024-deliver-dynamic-roadmap-review-data.md"]
generated_artifacts: []
base_revision: eac534abe9154710db2599a429a1f05d9cf47867
claim_id: WRK-0024:a80429b3-f337-4b55-904c-de3988cbae64
claimed_by: codex-roadmap-review
claimed_at: 2026-10-15T15:25:31Z
---

# Agent Work Packet: Deliver Dynamic Roadmap Review Data

## Objective and Deliverable

Deliver `capability-catalog-v1` and `roadmap-review-v1`, a project-neutral
projection core, a Financial AI Academy planning adapter, a read-only
control-plane command, synchronized product/operator documentation, and focused
tests that satisfy SLI-0034 without producing committed generated roadmap data.

## Required Context

Read and follow `AGENTS.md`, `docs/README.md`, the baseline, delivery-planning,
interface-design, and testing context, CAP-0008, SLI-0034, CAP-0003 and its
portfolio implementation/tests, the product catalog, planning model/register,
roadmap guide, decision readiness, design standards, documentation validator,
control-plane CLI/contracts, and the nearest READMEs before changing files.

## Decisions and Assumptions

- JSON is used for the machine catalog because it is versionable, natively
  supported by the dependency-free Python control plane, and directly consumable
  by the later TypeScript client.
- The Markdown catalog remains the human product-intent document; validation
  keeps candidate rows synchronized with the JSON manifest.
- Planning frontmatter and artifact bodies remain canonical for planning facts;
  the Markdown register is parity evidence, not runtime storage.
- CAP-0003 owns graph, order, readiness, and compatibility semantics.
- Explicit stable catalog keys own CAP mapping; title similarity has no authority.

## In Scope

Catalog manifest and parity validation; generic safe document/projection model;
repository adapter; existing-core composition; deterministic source digests;
read-only CLI integration; success, drift, malformed, missing, path, privacy,
reuse, and anti-rigidity tests; operator and planning documentation.

## Out of Scope

HTTP server, TypeScript UI, browser routing, visual graph, planning mutation,
roadmap acceptance, approvals, claims or leases from the site, fixed readiness
integration beyond affected validation, hosted exposure, or generated site data.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Candidate data | Product catalog and current parser | Catalog JSON and catalog guidance | Provide stable machine identity/order/mapping |
| Generic projection | CAP-0003 cores/contracts/tests | `roadmap_review.py` | Add vocabulary-neutral projection and safe plan sections |
| Repository adapter | Planning model, artifacts, roadmaps, CAP-0003 adapter | `financial_academy_roadmap_review.py` | Map canonical sources without parsing the register as storage |
| CLI | Existing parser/dispatch/envelopes | `control_plane.py` | Add one read-only JSON/text command |
| Validation/tests | Docs checker and control-plane suites | Named validator/test files | Prove parity, safety, freshness, reuse, and low friction |
| Docs/planning | README, CAP, SLI, WRK, register | Exact named files | Keep operation and lifecycle state synchronized |

## Contracts and Interfaces

`capability-catalog-v1`, `roadmap-review-v1`, existing `portfolio-graph-v1`,
portfolio order and compatibility contracts, existing control-plane success/
refusal envelopes, repository-relative source references, SHA-256 source
fingerprints, and a safe structured Markdown subset containing headings,
paragraphs, lists, tables, and fenced-code text only.

## Dependencies and Parallel Safety

CAP-0003 is complete and CAP-0008 is current. This first packet establishes the
contract consumed by every later CAP-0008 packet and therefore runs serially.
It has no active peer or reciprocal parallel declaration.

## Acceptance Scenarios

The SLI-0034 scenario table is normative. Focused tests additionally cover
non-contiguous catalog order, blank descriptions, exact count changes, unknown
and duplicate formal mappings, internal capabilities, missing future slices,
duplicate hierarchy nodes, invalid artifact source roots, inert HTML/script
text, deterministic ordering/digests, changed status/body fingerprints, generic
vocabulary, no local-ledger reads, and one-command read-only behavior.

## Verification Commands

- `python dev-tools/control-plane/test_roadmap_review.py`
- `python dev-tools/control-plane/test_portfolio.py`
- `python dev-tools/control-plane/test_portfolio_ordering.py`
- `python dev-tools/control-plane/test_portfolio_conflicts.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

## Documentation and Evidence Update

Update catalog machine-source guidance, the control-plane architecture/command
guide, planning register states, and SLI/WRK completion evidence. Do not record
approval/reviewer metadata or generated projection output.

## Stop Conditions

Stop for canonical-source conflict, title-inferred identity, changed portfolio
semantics, a second manually maintained plan database, active rendering,
arbitrary path reads, ignored-ledger data, project vocabulary in the generic
core, remote access, mutation, or a required new durable decision.

## Required Handoff

Delivered `capability-catalog-v1`, `roadmap-review-v1`, explicit five-CAP
mapping, the generic inert projector, Financial AI Academy adapter, read-only
CLI, product-catalog parity check, README guidance, and focused tests. The
roadmap suite passed 8 tests; existing portfolio graph, order, and compatibility
suites passed 7 each; control-plane lifecycle passed 10 outside the Windows
sandbox after its expected temp-directory denial; planning checked 49 artifacts;
documentation checked 172 Markdown files plus both catalogs; Python compilation,
diff checks, and all 25 aggregate readiness checks passed. No browser, HTTP,
hosted, or remote qualification was performed because those belong to later
slices. No migration or generated tracked artifact exists. The packet conforms
to SLI-0034 and CAP-0008.

## Planning History

- 2026-10-15: Authored just in time as the sole serial SLI-0034 packet with an
  exact write scope and no generated tracked artifact.
- 2026-10-15: Delivered the machine catalog, reusable projection, repository
  adapter, read-only CLI, parity validation, tests, and operator documentation;
  moved to verification after focused and aggregate checks passed.
