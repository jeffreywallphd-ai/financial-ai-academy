---
id: WRK-0004
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-agent
updated: 2026-08-05
parent: SLI-0001
capability: CAP-0001
depends_on: ["WRK-0003"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/package.json", "apps/web/package-lock.json", "apps/web/index.html", "apps/web/tsconfig.json", "apps/web/vite.config.ts", "apps/web/src/app", "apps/web/src/components", "apps/web/src/features/lesson-reading", "apps/web/src/platform/auth", "apps/web/src/platform/theme", "apps/web/src/styles", "apps/web/tests/unit", "apps/web/tests/component", "apps/web/tests/browser", "apps/web/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md"]
generated_artifacts: ["apps/web/package-lock.json"]
base_revision: a9503220007fedb9b67113a1b3f1e6e498fc6205
claim_id: WRK-0004:26d7eed0-4ef4-4b8c-824c-227fef6373ff
claimed_by: codex-agent
claimed_at: 2026-08-05T01:19:22Z
---

# Agent Work Packet: Deliver the Accessible Lesson-Reading Page

## Objective and Deliverable

Build the React learner-facing route that uses the WRK-0003 generated client to establish the configured single-profile session and open one approved lesson. The observable deliverable is a responsive reading page that presents title, objectives, safe lesson body, educational sources, package version/digest, and provenance with equivalent light, dark, and system-theme behavior plus explicit loading, denial, unavailable, and safe failure states.

## Required Context

Before changing files, prominently read and follow every applicable `AGENTS.md` and repository-root `docs/README.md`. Route through the baseline pack with `interface-design` as primary and `testing-quality` as adjacent. Read SLI-0001, WRK-0003 and the generated client, ADR-0007, ADR-0009, the education-versus-advice boundary, interface design README, style guide, interface standards, executable token and icon documentation, web README, affected application/client code, consumers, tests, and nearest READMEs. Mockups are directional only.

## Decisions and Assumptions

- React 19, TypeScript 7, React Router 8 Data Mode, Vite 8, Node 24, and a client-rendered static application are fixed by ADR-0009.
- The generated TypeScript client is the only lesson-data seam. UI code does not duplicate API models, parse raw CommonMark, access backend internals, or select the learner.
- The primary route is `/learn/placements/:placementId`. It performs the explicit same-origin single-profile bootstrap when no current application session is available, then loads the exact placement through generated operations.
- The API's closed body-node union maps to ordinary React elements through an exhaustive renderer. `dangerouslySetInnerHTML`, runtime HTML sanitization as authority, implicit fetches, arbitrary URLs, and unreviewed component injection are prohibited.
- Existing `--faa-*` tokens and reviewed SVG icons satisfy this slice. If implementation discovers a genuinely missing shared visual role or icon, stop for synchronized design-system review rather than adding feature-local values.
- Theme selection supports light, dark, and system preference, persists only the non-sensitive display preference locally, and never changes content or action availability.
- UI/query/testing libraries are replaceable implementation dependencies pinned in `package-lock.json`. They may be selected for the bounded deliverable but cannot introduce server rendering, a second data protocol, or a component-level design system.

## In Scope

- Minimal application shell, React Router Data Mode configuration, route loading/error composition, and the one lesson-reading route.
- Explicit single-profile session bootstrap behavior using only generated client operations and bounded retry rules.
- Accessible title, objectives, constrained body nodes, application-controlled passive images, sources, version/digest, and provenance presentation.
- Reading-layout primary column with secondary provenance/context rail that stacks after content at narrow widths.
- Light, dark, and system theme handling using existing tokens; reviewed icon usage; keyboard/focus, landmarks, headings, link semantics, status announcements, 200 percent zoom, responsive reflow, reduced-motion, and forced-color behavior.
- Loading skeleton/text, unauthorized/forbidden, unavailable/not-found, invalid-content, integrity, and generic safe-error states without leaking internals.
- Focused unit, component, route, accessibility, and browser tests for the delivered interface.

## Out of Scope

- Editing generated API code, backend operations, contract schemas, identity modes beyond single profile, login/recovery screens, setup wizard, or administration.
- Knowledge checks, progress, completion, notes, bookmarks, recommendations, AI tutoring, market data, portfolio behavior, or learner evidence.
- New global colors, spacing, radii, shadows, icon sets, production logo, downloaded fonts, charting, component-library standardization, or mockup replication.
- SSR, RSC, server actions, React Router Framework Mode, Next.js, Node production server, BFF, service worker/offline product, analytics provider, or production deployment.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| App composition | ADR-0009 and generated client | `apps/web/src/app/` | Static router, route lifecycle, and shell |
| Lesson feature | SLI-0001 result semantics | `apps/web/src/features/lesson-reading/` | One bounded learner-visible outcome |
| Shared presentation | Existing tokens/icons/components | `apps/web/src/components/`, `apps/web/src/styles/` | Reusable accessible primitives only where needed |
| Platform UI | Session and theme contracts | Named `platform/auth` and `platform/theme` roots | Generated-client bootstrap and theme preference |
| Build metadata | Web README and accepted runtime lines | Named manifests/configuration | Reproducible static build |
| Verification/docs | Current web tests and assurance maps | Named tests and documents | Focused accessibility/theme/browser evidence |

The implementing agent may inspect `apps/web/src/design-system/` but may not change it in this packet.

## Contracts and Interfaces

WRK-0004 consumes the committed WRK-0003 generated client and its exact safe body-node union, error codes, asset locators, and session-cookie behavior.

It produces:

- a route-level view state union for loading, ready, unauthorized, forbidden, not-found, unavailable, invalid-content, and unexpected safe failure;
- an exhaustive body-node renderer for the accepted heading, paragraph, list, emphasis, code, approved HTTPS link, and passive image nodes actually present in the API contract;
- accessible source and provenance components that visibly identify publisher/title/locator, package version, digest, and publication context; and
- static Vite artifacts whose runtime needs only the browser and Python-served same-origin API/static assets.

No UI type becomes a second public contract. Unrecognized body-node discriminators fail to the invalid-content state rather than rendering partially or falling through.

## Dependencies and Parallel Safety

WRK-0003 must complete first because this packet consumes its generated client and exact response/error types. The packet owns the web manifests and the delivered route, so it cannot run in parallel with client generation or the final browser/deployment qualification packet. WRK-0005 starts after the production build and focused browser tests are stable.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Read approved lesson | The configured local learner opens a valid placement | Bootstrap and route loading finish | Title, objectives, body, sources, version, digest, and provenance appear in correct hierarchy | Component plus browser test |
| Theme parity | The same ready/error states are rendered in light, dark, and system modes | Theme changes or system preference changes | Content, actions, focus, hierarchy, and contrast remain equivalent | Theme matrix and screenshot assertions |
| Keyboard and assistive access | The learner uses no pointer and a semantic accessibility tree | The page is traversed and links/actions are used | Landmarks, headings, focus order/visibility, names, status announcements, and external-link meaning are usable | Automated accessibility plus manual checklist |
| Responsive reading | The route is viewed at supported widths and 200 percent zoom | Rails and controls reflow | Primary reading order is preserved with no hidden content or horizontal page overflow | Browser viewport/zoom checks |
| Loading and unavailable | The API is pending or returns not-found/unavailable | The route resolves | Stable non-jumping status UI explains the state and a safe next action | Route/component tests |
| Unauthorized or forbidden | Bootstrap/session resolution fails | The page loads | No lesson internals appear; a concise bounded access state is announced | Browser denial test |
| Invalid or unknown content | A safe result contains an unsupported node discriminator or integrity error | Rendering begins | The route fails closed to invalid-content UI; no partial unsafe DOM is inserted | Renderer unit/security test |
| Safe external source | An approved HTTPS source is displayed | The learner activates it | The destination and external context are clear and opener access is prevented where a new context is used | DOM and browser assertion |
| Reduced/forced settings | Reduced motion or forced colors are active | The route renders and focus moves | Motion is nonessential and states/focus remain distinguishable without color alone | Browser emulation checks |
| Static runtime | The production application is built | Static assets are inspected/served | No Node server bundle, SSR entry, backend import, or handwritten API model is present | Build and architecture test |

## Verification Commands

```powershell
npm --prefix apps/web ci
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web test -- --run apps/web/tests/unit apps/web/tests/component
npm --prefix apps/web run test:browser -- apps/web/tests/browser/lesson-reading
npm --prefix apps/web run build
python dev-tools/design/check_design_system.py
python dev-tools/documentation/check_docs.py
python dev-tools/agent/check_ready.py
git diff --check
```

Report manual assistive-technology, 200 percent zoom, forced-color, and browser-matrix qualification separately when the local environment cannot automate it.

## Documentation and Evidence Update

Update the web README only for actual app commands and boundaries. Promote architecture verification or close known gaps only for direct static-build, generated-client-use, route, accessibility, and theme evidence. Do not change the style guide, tokens, icons, or mockups unless a separate synchronized design decision is approved.

## Stop Conditions

- The generated client lacks an exact safe result/error needed by the route, requiring a WRK-0003 contract revision.
- Rendering would require raw HTML, `dangerouslySetInnerHTML`, implicit fetch, arbitrary schemes, unreviewed SVG/assets, or non-exhaustive node handling.
- Existing design tokens/icons cannot express a required accessible state without a shared design change.
- A dependency requires SSR, Node production runtime, framework-owned data APIs, duplicated public models, or incompatible licensing.
- Work expands into assessment, learner evidence, multiple identity modes, setup administration, AI, financial tools, analytics, deployment, or another named non-scope.
- Accessibility, theme parity, or safe failure cannot be verified; canonical sources conflict; or active scope overlaps.

## Required Handoff

Report routes and state model, generated-client operations consumed, renderer node coverage, theme/accessibility/browser results, static build contents, dependency and license evidence, documentation changes, manual qualification gaps, and exact end-to-end inputs handed to WRK-0005.

## Completion Evidence

- The React Router 8 Data Mode application delivers `/learn/placements/:placementId` with explicit `loading`, `ready`, `unauthorized`, `forbidden`, `not-found`, `unavailable`, `invalid-content`, and `unexpected` states. A bounded in-memory session controller calls only generated `bootstrapSingleProfileSession` and `getPlacedLesson` operations, coalesces bootstrap, and permits one server-authorized renewal after an unauthorized read.
- The generated OpenAPI types remain the only public lesson model. Runtime validation closes unsafe or missing discriminators, unapproved schemes/source IDs, undeclared assets, non-application asset locators, excessive nesting/node counts, malformed digests, and invalid content before presentation.
- The ordinary React renderer exhaustively handles heading, paragraph, code block, thematic break, bullet/ordered list, text, inline code, soft/hard break, emphasis, strong, reviewed HTTPS source link, and declared passive image nodes. It uses no `dangerouslySetInnerHTML`, runtime HTML sanitizer, remote embed, backend import, database/provider access, or hand-maintained API field model.
- The page visibly presents title, objectives, reviewed source title/publisher/review date, package ID/version/digest, publisher/publication/review provenance, and the educational-use/advice boundary. Its reading column and context rail preserve reading order when stacked.
- Light, dark, and system preferences use only existing `--faa-*` tokens and reviewed sprite icons. The non-sensitive theme preference is the only browser-local value persisted; content and actions are identical across themes. Baseline SHA-256 values are `24BECD386E9599065201E008A81F8796F45DA5480D68966B99517114F24272BC` (light) and `F4D23288110B3B943471AE74B9665C6A1AAEC86BC5F78DA5DF678A877BC0C4A2` (dark).
- A clean npm install reproduced under Node 24.14/npm 10.8.2. TypeScript 7 and oxlint pass; five Vitest files provide 18 passing unit/component/static-boundary tests, and six Playwright Chromium tests pass with zero axe violations. Browser evidence covers theme visuals, keyboard/skip-link/focus, safe external links, narrow and 200-percent-equivalent reflow, reduced motion, forced colors, loading/denial, redaction, and unknown-node failure.
- Vite 8 transformed 97 modules into static-only `index.html`, CSS, JavaScript, source map, and the reviewed SVG sprite. The inspected build contained no server entry, backend/database dependency, `react-router-dom` compatibility package, or Framework Mode package. The package-lock SHA-256 is `FBC50B9DA87CA62BE69E092284C26E04A8BDDA59A75A99A8AF6B1EEFDB138374`.
- npm audit reported zero known vulnerabilities. All 190 resolved package relationships declared licenses; the inventory contains MIT, MIT-0, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, BlueOak-1.0.0, CC0-1.0, and MPL-2.0. MPL-2.0 packages are development tooling/transitives and no modified third-party source is distributed by this work.
- `apps/web/README.md` now documents the delivered route, static/runtime boundary, exact commands, coherent loopback proxy configuration, and verification ownership. WRK-0005 receives the exact route, generated operations, visual baselines, focused tests, build command, and static artifact expectations for aggregate qualification.
- Controlled manual screen-reader operation, actual browser zoom controls, non-Chromium browsers, non-Windows visual baselines, real backend/static co-serving, and passive-asset retrieval are not claimed by this packet and remain qualification gaps.

## Planning History

- 2026-08-04: Shaped from SLI-0001 boundary seam 6; planning approval and implementation activation remain separate local-only stages.
- 2026-08-05: Implemented and verified the accessible generated-client lesson route, closed renderer, three-mode theme behavior, focused browser evidence, and static Vite artifact; WRK-0004 completed and handed off to WRK-0005.
- 2026-08-05: Reopened after live approved-fixture qualification exposed insufficient light-theme contrast for muted text on the subtle surface.
- 2026-08-05: Reused the accepted secondary-text token for the two affected surfaces, added explicit light/dark axe assertions, regenerated both visual baselines, and reran the focused WRK-0004 suite successfully.
