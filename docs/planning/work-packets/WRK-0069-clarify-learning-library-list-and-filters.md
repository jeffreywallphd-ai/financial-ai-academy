---
id: WRK-0069
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: SLI-0122
capability: CAP-0030
depends_on: ["WRK-0068"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/features/learning-catalog/LearningCatalogPage.tsx", "apps/web/tests/component/learningCatalog.test.tsx", "apps/web/README.md", "docs/planning/work-packets/WRK-0069-clarify-learning-library-list-and-filters.md", "docs/planning/vertical-slices/SLI-0122-choose-learning-opportunities-in-plain-language.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 730ce3afb5dd9ee3d30796246027d7b46bea07d9
claim_id: WRK-0069:6b96043b-1095-418b-8d50-3fced0a92e7a
claimed_by: codex-plain-language-ui
claimed_at: 2026-10-16T09:07:39Z
---

# Agent Work Packet: Clarify Learning-Library List and Filters

## Objective and Deliverable

Apply the accepted learner-facing language standard to the `/learn` result
list, native filter form, opportunity cards, and current-page comparison
controls. A learner should be able to identify the library, choose filters,
understand each result, inspect supporting publication and technical facts,
and open an available lesson without seeing query, slug, package, provenance,
or exactness terminology in the primary flow.

This packet changes presentation only. It preserves the existing query
parameters, URL state, server order, availability rules, exact destination,
selection bounds, publication facts, technical values, and educational-use
notice.

## Required Context

Read and follow the repository startup and interface-design instructions. Use
the CAP-0030 package, SLI-0122, the completed WRK-0068 language standard and
content guide, CAP-0004 discovery authority, the web README, the catalog page,
its model, fixture, component tests, and the relevant browser tests. Inspect
the generated-client and backend contracts as read-only semantic authority;
do not rename their fields.

## Decisions and Assumptions

- `Learning library`, `Topic`, `Show results`, `Lesson version`, `Open lesson`,
  `Publication details`, and `Technical record` are the preferred learner
  labels from WRK-0068.
- The catalog remains deterministic and non-personalized. Plain language must
  retain that limitation without teaching the learner about server or
  projection implementation.
- Exact IDs, versions, digests, fingerprints, publisher, dates, educational-use
  notice, availability reason, and destination remain visible or accessible.
- Tests protect semantic roles, required facts, and actions. They may assert a
  short safety-critical phrase or control name but must not freeze whole
  explanatory paragraphs unnecessarily.

## In Scope

- Page eyebrow, introductory copy, result summary, filter labels/help/actions,
  empty state, list accessible name, card fact labels, publication heading,
  technical-record disclosure, availability explanation placement, and open
  action wording in `LearningCatalogPage`.
- Current-page comparison instructions/status wording where it appears inside
  the list experience; comparison mechanics and bounds remain unchanged.
- Focused component expectations for the revised accessible names, retained
  facts, disclosure reachability, unchanged destinations/order, flexible empty
  and variable record shapes, and bounded comparison behavior.
- Web documentation updates that describe the delivered presentation contract.

## Out of Scope

Route loading, denied, invalid, stale, unavailable, and unexpected messages;
detail-page and comparison-page presentation; browser qualification; query,
model, API, contract, generated-client, backend, storage, CSS, token, icon,
layout, route, or business-policy changes; localization; and automated content
checking.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Catalog presentation | list page, model, fixture, browser tests | `LearningCatalogPage.tsx` | Replace implementation-facing primary copy while preserving behavior and complete facts |
| Component evidence | existing catalog component suite | `learningCatalog.test.tsx` | Protect accessible names, actions, required facts, and anti-rigidity behavior |
| Web documentation | delivered route and verification boundary | `apps/web/README.md` | Describe the primary/supporting/technical-record presentation contract |
| Planning evidence | SLI-0122 and register | this packet, slice, register | Keep the just-in-time work seam and status coherent |

## Contracts and Interfaces

No external or internal data shape changes. HTML form `name` attributes,
allowed values, URL construction, cursor handling, opportunity identifiers,
exact destinations, and current comparison selection order remain unchanged.
Primary copy may describe these facts more clearly, while the technical record
must retain exact values in selectable text and remain keyboard and
screen-reader reachable.

## Dependencies and Parallel Safety

WRK-0068 is complete and supplies the accepted language contract. This packet
touches the shared catalog page and SLI/register coordination surfaces, so it
is not parallel-safe with the following detail/comparison packet. No durable
decision gate is open.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Find by topic | The learner opens the library | They inspect and submit the filters | The field is named `Topic`, the action is `Show results`, and the unchanged `topic` query value is submitted | component |
| Understand one result | An opportunity card is visible | The learner reads its facts | Classification, level, time, prerequisites, objectives, availability, publisher, review date, educational notice, and lesson version remain understandable | component |
| Inspect technical evidence | A card includes digest and source fingerprint | The learner opens `Technical record` | Both exact values remain visible and the disclosure has an accessible name | component/accessibility |
| Open an available lesson | An available lesson is present | The learner follows `Open lesson` | The existing exact same-origin destination is unchanged; planned and unavailable records remain non-actionable | component |
| Empty result | No opportunities match | The result area renders | It says no activities match the filters and gives a clear filter/search recovery without inventing a recommendation | component |
| Flexible result shapes | Empty, one-item, repeated-classification, variable-topic, and five-item pages render | The learner filters or compares | Copy and tests do not assume one fixture count or one unique classification, and the four-item comparison bound remains intact | anti-rigidity component |

## Verification Commands

Run the focused catalog component suite, web typecheck and lint, design-system,
documentation, planning, Git whitespace, selected affected verification, and
the fixed aggregate readiness check. Browser qualification is intentionally
deferred to JIT-D unless affected-check routing selects it for this packet.

## Documentation and Evidence Update

Record the changed learner labels, retained facts/actions, unchanged query and
selection behavior, focused and aggregate results, anti-rigidity evidence,
documentation impact, assumptions, and gaps. Do not record approval or
reviewer metadata in tracked files.

## Stop Conditions

Stop for a changed query or URL contract; changed server order, availability,
selection, exact destination, provenance, educational-use, or authorization
meaning; removal of technical evidence; CSS, token, icon, or layout changes;
route-state copy outside this packet; legal/risk wording changes; an unresolved
decision; a file-scope collision; or material CAP/SLI drift.

## Required Handoff

Report the revised list/filter/card terms, unchanged data and behavior
boundaries, technical-record reachability, tests and anti-rigidity evidence,
documentation impact, changed paths, assumptions, and known gaps. Leave the
detail/comparison/error packet dependency-ready or return a bounded blocker.

## Planning History

- 2026-10-16: Authored just in time after WRK-0068 completed. The packet is
  limited to the result-list experience and component evidence so destination
  pages, route failures, and browser qualification can be reviewed in their
  own dependency-ordered increments.
