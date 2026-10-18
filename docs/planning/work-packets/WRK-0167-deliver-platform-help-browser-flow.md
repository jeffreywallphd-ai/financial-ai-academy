---
id: WRK-0167
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0082
capability: CAP-0020
depends_on: [WRK-0166]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/app/AppShell.tsx", "apps/web/src/app/main.tsx", "apps/web/src/app/router.tsx", "apps/web/src/features/platform-help", "apps/web/src/styles/platform-help.css", "apps/web/tests/browser/platform-help", "apps/web/tests/component/platformHelp.test.tsx", "apps/web/tests/component/platformHelpFixture.ts", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/unit/platformHelpModel.test.ts", "backend/src/financial_ai_academy/modules/guidance/README.md", "docs/architecture/contracts/platform-help-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0082-browse-search-approved-help.md", "docs/planning/work-packets/WRK-0167-deliver-platform-help-browser-flow.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Deliver the Platform Help Browser Flow

## Objective and Deliverable

Deliver URL-backed `Help` browse/search and exact-topic pages that consume only
WRK-0166's generated public client. An authorized learner can open Help from the
application navigation, search or filter the reviewed corpus, clear filters,
page through results, open one exact topic version, follow related exact topics,
return to Help, inspect publication details, and reach complete technical facts
through progressive disclosure.

The deliverable is a safe browser presentation over the existing API. It adds
no browser-owned ranking, corpus, authorization, provider, persistence, model,
or policy authority.

## Required Context

Before implementation, read and follow `AGENTS.md`, `docs/README.md`, routed
context, the change-impact matrix, decision readiness, CAP-0020, SLI-0082,
WRK-0166, the platform-help contract, Guidance README, generated-client
contract, interface design system, content and user-facing-language standards,
Web design-system and icon rules, and the nearest router, loader, model,
component, CSS, and browser-test examples. Inspect the generated search and
exact-topic types before writing browser validation or presentation code.

The Required Startup was performed and reported before this planning change.
No unresolved durable decision applies. Stop for stale CAP authority, a
canonical conflict, an active file collision, or material CAP/slice drift.

## Decisions and Assumptions

- The current approved CAP-0020 package and active SLI-0082 remain binding;
  WRK-0166 is complete and supplies the only search, exact-read, authorization,
  integrity, ordering, and cursor authority.
- Browser routes are `/help` and
  `/help/topics/:topicId/versions/:topicVersion`. The exact route never asks for
  or substitutes a latest version.
- URL query state admits only `query`, optional `topic_kind`, `page_size`, and
  opaque `cursor`, using the server contract's bounds. Unknown, duplicate, or
  malformed inputs fail to a bounded recovery state before any request.
- The browser validates closed generated response shapes before rendering and
  renders the body node union as inert React elements. It never uses raw HTML,
  Markdown, arbitrary links, or active content.
- Primary copy uses `Help`, `Search help`, `Show results`, `Clear search`,
  `Publication details`, and `Technical record`. Exact IDs, versions, digests,
  source keys, and fingerprints remain available in the technical layer.
- Related topics are same-origin exact-version links derived only from the
  validated document. Search and topic access remain read-only and do not
  record learner behavior.
- Existing semantic tokens, components, icons, and theme rules are sufficient;
  this packet creates no shared visual-system decision.

## In Scope

- Add generated-client-derived model types and strict browser response
  validators for search pages, exact topics, safe body nodes, source facts,
  publication chronology, related exact identities, digests, cursor/query
  echo, and closed object keys.
- Add search and exact-topic loaders using `SingleProfileSession`, one bounded
  unauthorized renewal, authorization-before-content behavior, and explicit
  mapping for invalid query/cursor, missing exact version, unavailable service,
  invalid response, and unexpected failure.
- Add Help browse/search UI with native form controls, stable result order,
  result-count-independent empty/populated behavior, kind labels, publication
  facts, exact links, and cursor-preserving next-page links.
- Add exact-topic UI with safe body-node rendering, applicability, publication
  and source summaries, related topic links, return-to-Help behavior, and a
  keyboard-operable `Technical record` retaining every exact technical fact.
- Add Help to the application navigation, route table, skip-link wording, and
  root stylesheet imports.
- Add focused model, loader, component, generated-client usage, and mocked
  Chromium checks for safe rendering, authorization containment, exact-version
  navigation, themes, keyboard use, narrow/zoom/reduced-motion/forced-color
  behavior, and anti-rigidity across varied valid record counts and node shapes.
- Reconcile direct Guidance/platform-help browser status and planning evidence.

## Out of Scope

- Backend, OpenAPI, generated-client, corpus, identity permission, search
  ranking, cursor, source-manifest, or public API changes.
- Contextual help links from other product features; SLI-0083 owns them.
- Expanded methodology/provenance or feature-specific unavailable and
  troubleshooting topics; SLI-0084 owns them.
- Disposable PostgreSQL/API/browser restart, offline/no-outbound, headless
  parity, source-integrity, containment, and cleanup qualification; WRK-0168
  owns that dependent slice-closing evidence.
- Mutable authoring, remote content, arbitrary URLs, analytics, search history,
  recommendations, personalization, semantic/vector search, generated answers,
  model/provider execution, grading, eligibility, financial conclusions, or
  external action.
- New tokens, icons, layouts, screenshots, visual snapshots, or optional style
  polish that does not affect function, comprehension, or accessibility.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Web application | Router, shell, root imports, session adapter | Add Help navigation, loaders, routes, and feature stylesheet import | Reach the protected feature through ordinary application paths |
| Help feature | Generated types, analogous model/API/route/page features | Add platform-help model, API, browse/topic routes and pages | Render one safe browser view over the public API |
| Design system | Tokens, icons, shared StatusPanel, style rules | Consume only; add feature CSS using semantic variables | Preserve theme and accessibility contracts without a new shared pattern |
| Tests | Generated-client usage and analogous unit/component/browser suites | Add Help fixtures and focused model/component/Chromium evidence | Prove containment, exactness, accessibility, and anti-rigidity |
| Documentation | Guidance README and platform-help contract | Update browser implementation status and retained headless authority | Reconcile the delivered boundary |
| Planning | SLI-0082, WRK-0167, register | Activation, verification, neutral evidence, and status only | Keep governed state synchronized |

No backend, API schema, generated artifact, persistence, deployment, provider,
model, design-token, icon, or unrelated feature file may change.

## Contracts and Interfaces

`components["schemas"]["PlatformHelpSearchResponseModel"]` and
`components["schemas"]["PlatformHelpTopicResponseModel"]`, together with the
generated search and exact operations, are the only remote inputs. Browser
validation must reject missing, extra, malformed, unsafe, chronologically
invalid, or internally inconsistent fields before rendering any partial page.

Search links retain only the validated public query. Topic links carry exact
`topic_id` and `topic_version`; an optional same-origin `/help` return target may
preserve the current search without accepting credentials, fragments, other
paths, or origins. Loader states are transport-neutral presentation outcomes,
not new API meanings.

Body rendering is exhaustive over heading levels 2-4, paragraphs, ordered or
unordered lists, educational/limitation/warning notes, and exact topic
references. Unknown node kinds fail the complete document closed.

## Dependencies and Parallel Safety

WRK-0166 is complete. This packet changes the shared router, navigation, root
style imports, Help feature, Web contract-usage proof, and slice/register, so it
is not parallel-safe with another writer on those files. WRK-0168 waits for this
packet's exact browser routes and focused checks.

Claim from a clean recorded base revision, run `packet-start`, acquire exact
file leases immediately before edits, retain one owner through verification,
and keep approval/reviewer records only in ignored local storage.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Browse and search | A valid protected search page with varied records | The learner opens Help or shows bounded query/kind inputs | Results preserve server order and exact facts; no client ranking or analytics runs | unit/component/Chromium |
| Empty and paging | Zero results or an opaque next cursor | The page renders | Empty guidance offers a clear recovery, or one exact next-page link preserves validated query state | unit/component |
| Exact topic | A complete valid topic with varied safe nodes | The learner opens its exact link | Every node renders inertly, applicability and publication facts remain readable, and no raw markup executes | model/component/Chromium |
| Related topic | A valid exact relation exists | The learner follows it | The exact ID/version route opens without latest-version substitution | component/Chromium |
| Technical record | Exact IDs, versions, digests, source keys, versions, and fingerprints exist | The disclosure opens | Every value remains labeled, selectable, and reachable by keyboard | component/Chromium |
| Authorization confidentiality | Session creation or exact permission fails | Either route loads | Bounded 401/403 learner guidance appears before Help content or corpus facts are requested/shown | loader/Chromium |
| Invalid or stale input | Query, cursor, exact path, response shape, or source chronology is invalid | Loader/model validates it | The complete result fails closed with a safe next action and no rejected/private detail | unit/component |
| Theme and reflow | Content varies in count, Unicode, node length, and relations | Light/dark/system, keyboard, narrow, zoomed, reduced-motion, and forced-color checks run | Equivalent content/actions remain usable without horizontal page overflow or hidden meaning | component/Chromium |
| Headless authority retained | Imports and requests are inspected | Browser flow runs | Only the generated client reaches the same protected API; no browser corpus, ranking, or policy authority exists | contract/architecture |

## Verification Commands

Run focused Vitest model/component tests and generated-client contract usage;
TypeScript typecheck, zero-warning lint, and build; focused Playwright Help
checks; design-system, learner-language, architecture, security,
documentation, planning, and whitespace checks; exact-candidate affected
verification; one independent technical review; and
`python dev-tools/agent/check_ready.py`.

Record only passing commands. A harmless whitespace, optional copy, or
nonfunctional style concern may be corrected in scope without renewed approval
or a full review loop; optional polish may be deferred to CAP-0031.

## Documentation and Evidence Update

Document URL-backed Help routes, generated-client-only access, strict response
validation, safe body rendering, exact relation/return links, task-first copy,
publication/technical layers, accessibility behavior, assumptions, checks, and
remaining live/contextual/methodology work. Update packet, slice, and register
together; never copy local approval or reviewer records into tracked files.

## Stop Conditions

Stop for a required backend/API/generated-client change; ambiguous content or
source authority; raw HTML/Markdown or arbitrary URL need; browser-owned
ranking, corpus, identity, policy, persistence, analytics, model/provider,
personalization, grading, eligibility, financial action, or external effect;
new shared token/icon/design decision; inaccessible required meaning; stale CAP
authority; active collision; or material CAP-0020/SLI-0082 drift.

Do not stop for harmless whitespace, optional wording, fixture count/order,
nonfunctional styling, or another inconsequential issue. Fix it in bounded
scope or defer optional polish.

## Required Handoff

Report `CAP-0020.SLI-0082.WRK-0167`; exact candidate and receipt; Help and exact
topic routes; generated-client operations; validation, safe rendering, search,
filter, paging, related-topic, publication, technical-record, authorization,
theme, accessibility, anti-rigidity, and headless-authority evidence; checks;
docs; assumptions; and remaining live/contextual/methodology gaps. Confirm no
backend/API/schema, persistence, provider/model, learner authority, external
content/action, or financial behavior changed.

## Planning History

- 2026-10-18: Authored just in time after WRK-0166 completed. The packet
  delivers the approved slice's browser seam over the existing protected API
  and generated client, while leaving live restart/offline/headless
  qualification to its dependency-ordered successor. It preserves CAP-0020 and
  requires no lower-level approval.
