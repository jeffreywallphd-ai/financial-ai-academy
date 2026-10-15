---
id: WRK-0053
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: SLI-0020
capability: CAP-0004
depends_on: ["WRK-0051"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/features/learning-catalog/model.ts", "apps/web/src/features/learning-catalog/api.ts", "apps/web/tests/unit/learningCatalogModel.test.ts", "apps/web/README.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0020-inspect-and-compare-learning-opportunities.md", "docs/planning/work-packets/WRK-0053-define-opportunity-selection-model.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Define the Opportunity Selection Model

## Objective and Deliverable

Define and test the browser-side contract that turns one detail identity or an
ordered selection of two through four distinct comparison identities into
current, fully validated discovery records. Deliver a protected loader over the
existing generated queryless browse operation, a cursor-free bounded return
path, and fail-closed route states for malformed, changed, denied, unavailable,
or invalid data. Do not add routes or visible detail/comparison UI in this
packet.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`; route
through API/security, interface, testing-quality, and delivery-planning
context; read the change-impact matrix, decision readiness,
planning/concurrency guidance, CAP-0004, SLI-0020, completed SLI-0018 and
SLI-0019 packets, discovery-v1 and the discovery contract, the generated API
client, Identity session helper, learning-catalog model/API consumers and
tests, and the web README.

## Decisions and Assumptions

The accepted queryless browse operation remains the single authoritative
source for this browser projection. Its complete response is capped at 500
records and must pass the existing envelope, record, order, provenance,
fingerprint, and generation checks before any selected identity is resolved.
Selection order is user navigation state, not a ranking. A return reference is
optional browser navigation state, not a durable record, and may preserve only
a same-origin `/learn` path after removing a transient cursor.

## In Scope

- Define strict parsers for one bounded detail identity and two through four
  repeated, distinct, bounded comparison identities while rejecting unknown or
  client-supplied record fields.
- Define a bounded same-origin `/learn` return-path parser/builder that retains
  valid catalog query/filter/sort/page-size state but never retains `cursor`, a
  fragment, credentials, another origin, or an unrelated path.
- Resolve an accepted selection in input order only after the complete current
  discovery snapshot passes `learningCatalogIsSafe`; fail the entire selection
  when any identity is absent rather than rendering partial records.
- Add a protected current-snapshot loader through the generated
  `GET /api/v1/curriculum/opportunities` client operation, including the
  existing establish-session behavior and one bounded renewal after 401.
- Expose closed route states for ready detail/comparison, malformed selection,
  selection changed, unauthorized, forbidden, unavailable, invalid response,
  and unexpected response without disclosing records on failure.
- Add focused model/loader tests for bounds, ordering, complete validation,
  current-generation resolution, denial, renewal, changed selection, and
  anti-rigidity behavior that accepts ordinary `/learn` as the return path.
- Document the reusable client contract and its no-cache/no-browser-authority
  boundary in the web README.

## Out of Scope

React routes, components, styling, comparison controls, cards, tables, browser
or live qualification, backend/API/schema changes, generated-client changes,
new detail/comparison operations, saved comparisons, browser storage, caching,
enrollment, eligibility, prerequisite completion, ranking, recommendation,
learner progress, activity execution, provider integration, or background work.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Discovery validation model | discovery contract, generated schemas, current catalog model | `apps/web/src/features/learning-catalog/model.ts` | Add bounded selection, resolution, return-path, and closed route-state primitives |
| Protected client composition | generated client and single-profile session helper | `apps/web/src/features/learning-catalog/api.ts` | Read and validate the complete queryless snapshot with bounded 401 renewal |
| Focused evidence | existing catalog model/API tests and fixtures | `apps/web/tests/unit/learningCatalogModel.test.ts` | Prove parsing, integrity, exact resolution, denial, and anti-rigidity behavior |
| Consumer documentation | web README | `apps/web/README.md` | Record the client authority and navigation-state boundary |
| Lifecycle | parent slice, packet, planning register | listed planning files | Keep exact packet state and slice decomposition synchronized |

## Contracts and Interfaces

The packet consumes discovery-v1, the generated
`browseLearningOpportunities` operation, `SingleProfileSession`, and the
existing `learningCatalogIsSafe` validator unchanged. It produces typed detail
and comparison selection values, one cursor-free return-path value, a complete
snapshot resolver, and a loader state union for WRK-0054 and WRK-0055. No URL
value may supply an owner record fact, provenance field, availability result,
destination, generation, or cursor.

## Dependencies and Parallel Safety

WRK-0051 is complete and provides the qualified browse/query client boundary.
WRK-0054 consumes this packet's exact loader and state union, while WRK-0055
consumes its comparison selection and return-path contract. This packet is not
parallel-safe with either successor because they share the learning-catalog
client boundary and cannot safely invent the interface before it is verified.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Detail resolution | One valid current ID and a valid complete snapshot | The loader resolves the request | Exactly the current matching record and projection metadata are returned | unit |
| Comparison order | Two through four distinct valid IDs | The selection resolves | All records are returned in input order without scores or reordering | unit |
| Malformed selection | Invalid, duplicate, empty, excessive, or unknown URL state | Parsing runs | Work stops before session or API access and no record is exposed | unit |
| Changed selection | Any accepted ID is absent from the current generation | Resolution runs | The entire selection becomes `selection-changed`; no partial list is returned | unit |
| Invalid projection | A partial or integrity-invalid success response arrives | Validation runs | The result is `invalid-response` with no cached or URL-owned fallback | unit |
| Session renewal | The protected browse call returns 401 once | The session renews | The loader retries once only and otherwise fails closed | unit |
| Return continuity | A valid filtered `/learn` URL includes an opaque cursor | Return state is normalized | Valid query state remains but `cursor` and fragments do not | unit |
| Anti-rigidity | The origin is the ordinary unfiltered catalog | A return path is formed | `/learn` remains valid without synthetic filters, saved state, or extra services | unit |

## Verification Commands

Run the packet validator; focused Vitest model/API tests; web TypeScript
typecheck and lint; the complete web unit/component suite; generated-client
currency; web README/documentation validation; planning validation; Git diff
check; packet-start selected controls; independent technical review; and every
additional affected control-plane check. Aggregate readiness is not required
unless packet-start classifies the change as shared/control impact or the
implementation exposes broader drift.

## Documentation and Evidence Update

Keep this packet, SLI-0020, and `docs/planning/register.md` synchronized. Update
the web README for the accepted client boundary. Record exact focused evidence,
states, bounds, and residual UI/live work at completion; never copy local
approval or reviewer records into tracked artifacts.

## Stop Conditions

Stop for a new public backend operation or discovery meaning; URL-, cache-, or
browser-storage-owned record facts; partial comparison; durable saved state;
enrollment, eligibility, prerequisite completion, recommendation, ranking,
learner progress, or execution; an external provider, dependency, migration,
queue, background job, remote profile, or managed-cloud policy; overlapping
active scope; unresolved durable choice; or material CAP-0004/SLI-0020 outcome,
manifest, order, risk, or decision drift.

## Required Handoff

Report the exact identity/comparison/return bounds, complete-snapshot validation
and resolution behavior, denial/failure states, 401 renewal limit, tests and
other checks, documentation impact, residual UI/live work, and CAP/SLI
conformance.

## Planning History

- 2026-10-15: Authored just in time after SLI-0020 selection. The packet reuses
  the protected complete browse projection, introduces no backend contract or
  durable state, and provides the bounded client seam needed by the two UI
  packets without material CAP drift.
