---
id: WRK-0072
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: SLI-0122
capability: CAP-0030
depends_on: ["WRK-0071"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/tests/browser/learning-catalog/learning-catalog.spec.ts", "docs/planning/work-packets/WRK-0072-qualify-plain-language-learning-library.md", "docs/planning/vertical-slices/SLI-0122-choose-learning-opportunities-in-plain-language.md", "docs/planning/register.md"]
generated_artifacts: ["artifacts/playwright/wrk0004/**"]
base_revision: b81f3078e20486071e9da2985150ff62fc915749
claim_id: WRK-0072:7bdaea75-3533-4cc3-a965-d7996182651d
claimed_by: codex-plain-language-ui
claimed_at: 2026-10-16T09:47:28Z
---

# Agent Work Packet: Qualify the Plain-Language Learning Library

## Objective and Deliverable

Qualify the complete SLI-0122 learning-library flow in pinned Chromium after
the catalog, detail, comparison, loading, and recovery language changes. Update
only stale browser expectations and add bounded assertions that prove the
learner-facing actions and complete technical records remain usable across the
supported themes and access modes. Reconcile the slice evidence and close
SLI-0122 when every scenario passes.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Use the baseline, `interface-design`, and
`testing-quality` packs. Read CAP-0030, SLI-0122, WRK-0068, WRK-0069,
WRK-0071, the language and interface standards, design content guide, existing
learning-catalog component and browser tests, browser configuration/support,
the generated-client boundary, catalog fixtures, and `apps/web/README.md`.

## Decisions and Assumptions

- The completed packets own the delivered copy and behavior. This packet
  qualifies those outcomes and does not introduce new product behavior.
- Browser assertions protect task meaning, actions, required evidence,
  accessibility, fail-closed behavior, and layout modes rather than exact full
  paragraphs or one fixture count.
- Technical facts remain complete and reachable through native `Technical
  record` disclosures; tests may open those disclosures without moving their
  contents into the primary flow.
- Nonfunctional styling preferences are nonblocking and belong in CAP-0031
  unless they impair function, comprehension, accessibility, contrast,
  hierarchy, responsive use, safety, or an SLI-0122 acceptance scenario.
- The pinned Chromium route is the currently accepted local browser
  qualification boundary. Cross-browser expansion is not implied.

## In Scope

- Replace stale browser expectations such as `Apply query`, `Open exact
  lesson`, `Return to catalog`, and `Compare educational facts` with the
  delivered task-focused accessible names.
- Verify the topic-format instruction, plain filter action, available and
  unavailable card behavior, learner-order comparison, and safe return links.
- Open detail and comparison `Technical record` disclosures and verify exact
  identities, digests, generation, schema, and source fingerprints remain
  present and selectable.
- Preserve existing theme, axe, keyboard, forced-color, reduced-motion, narrow
  viewport, 200-percent text, denied-state, invalid-response, and fail-closed
  coverage using the revised words.
- Add narrowly scoped anti-jargon/anti-rigidity assertions only where they map
  directly to primary learner regions.
- Run the focused Chromium suite, production build/type/lint/unit checks as
  selected, design/documentation/planning/readiness gates, affected
  verification, and the deterministic slice completion gate.
- Reconcile WRK-0072 and SLI-0122 completion evidence with the planning
  register.

## Out of Scope

- Product component, route, model, API, generated-client, query, selection,
  authorization, availability, exact-placement, provenance, persistence, or
  session changes.
- New browser engines, visual snapshots, token/icon changes, visual redesign,
  broad prose freezing, external accessibility or content services, or formal
  standards claims.
- Curriculum, lesson/completion, or changed-copy checker work reserved for
  SLI-0123 through SLI-0125.
- Treating cosmetic styling or terminal-blank-line differences as reasons for
  a new review round.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Learner behavior | catalog/detail/comparison components, routes, fixtures, generated client | none | Confirm behavior and evidence without changing it |
| Browser evidence | learning-catalog Chromium suite and support/config | one named specification | Align accessible names and add bounded end-to-end evidence |
| Planning | CAP, slice, completed packets, register | packet, parent slice, register | Record qualification and close the slice |
| Generated evidence | Playwright output directory | generated only | Retain failure diagnostics when a browser scenario fails |

## Contracts and Interfaces

No public, domain, API, generated-client, persistence, or event contract
changes. The browser suite consumes the existing loopback Vite host, mocked
single-profile session, validated catalog fixtures, URLs, and accessible names.
Exact values are asserted only for facts whose preservation is part of the
technical-record contract.

## Dependencies and Parallel Safety

WRK-0068 through WRK-0071 are complete and supply the language contract and
the full revised discovery flow. WRK-0072 is serial because it qualifies their
combined observable outcome and closes SLI-0122. It is not declared parallel-
safe; an exact-file lease still allows unrelated CAP work outside this scope.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Find and open | A current available lesson | The learner searches or filters and opens it | `Topic`, format help, `Show results`, and `Open lesson` work with unchanged URLs | Chromium |
| Inspect facts | A current lesson and project | The learner opens details and technical records | Plain facts remain primary and every required exact technical value remains reachable | Chromium/accessibility |
| Compare in order | Two selected opportunities | The learner compares them | Learner order, kind-sensitive labels, no-winner explanation, actions, and technical records remain intact | Chromium |
| Non-openable item | A planned project | Its card/detail/comparison renders | Facts and availability reason remain visible without inventing an open action | Chromium |
| Safe failure | Denied, changed, malformed, or invalid data occurs | The route resolves | No private or partial facts render and the existing safe next action uses plain words | Chromium |
| Access parity | Themes, keyboard, forced colors, reduced motion, narrow viewport, or 200-percent text are used | The full flow is exercised | Equivalent content/actions remain accessible without horizontal overflow or motion reliance | Chromium/axe |
| Anti-rigidity | Harmless prose or catalog cardinality changes | Tests evaluate the page | Assertions depend on roles, actions, required phrases/facts, and flexible records rather than exact paragraphs | Test review |

## Verification Commands

- `npm --prefix apps/web run test:browser -- apps/web/tests/browser/learning-catalog`
- `npm --prefix apps/web test -- --run apps/web/tests/component/learningCatalog.test.tsx apps/web/tests/component/learningOpportunityDetail.test.tsx apps/web/tests/component/learningOpportunityComparison.test.tsx`
- `npm --prefix apps/web run typecheck`
- `npm --prefix apps/web run lint`
- `npm --prefix apps/web run build`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- affected verification through `python dev-tools/control-plane/control_plane.py verify WRK-0072`
- `python scripts/check_completion_gate.py SLI-0122 WRK-0068 WRK-0069 WRK-0071 WRK-0072`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

No Docker, database, backend, live API, generated-client regeneration, or full
approved-lesson suite is required unless an actual changed path or discovered
behavior crosses that boundary.

## Documentation and Evidence Update

No product, architecture, contract, or web README change is expected because
WRK-0068 through WRK-0071 already reconciled the delivered terms. Update this
packet, SLI-0122, and the register together with browser outcomes, completion-
gate results, affected checks, supported-environment limits, residual risks,
and the next slice route.

## Stop Conditions

Stop for a product behavior defect; missing or inaccessible technical facts;
changed query, ordering, selection, authorization, availability, session,
destination, provenance, or disclosure meaning; a new browser-support promise;
a required implementation path outside the declared scope; unresolved
canonical conflict; overlapping active file lease; or material CAP-0030 drift.

## Required Handoff

Report each revised browser scenario, exact checks and results, accessibility/
theme/responsive evidence, preserved contracts and facts, environment limits,
assumptions, residual risks, completion-gate result, slice closure decision,
and the next CAP-manifest action. Do not request a slice-level approval.

## Planning History

- 2026-10-16: Refined JIT-D after WRK-0071 completed. The packet is limited to
  the existing learning-catalog Chromium specification plus planning closure,
  and treats cosmetic styling as deferred cleanup rather than a review gate.
- 2026-10-16: Activated after validating its dependency, current CAP authority,
  exact write and generated-artifact scope, completion scenarios, and absence
  of an unresolved decision gate.
