---
id: WRK-0192
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0108
capability: CAP-0026
depends_on: [WRK-0191]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/app/main.tsx", "apps/web/src/app/router.tsx", "apps/web/src/features/accountable-history/AccountableHistoryPanel.tsx", "apps/web/src/features/accountable-history/api.ts", "apps/web/src/features/accountable-history/model.ts", "apps/web/src/features/lesson-reading/KnowledgeCheck.tsx", "apps/web/src/features/lesson-reading/LessonReadingPage.tsx", "apps/web/src/features/lesson-reading/LessonRoute.tsx", "apps/web/src/styles/accountable-history.css", "apps/web/tests/browser/lesson-reading/lesson-reading.spec.ts", "apps/web/tests/component/accountableHistory.test.tsx", "apps/web/tests/unit/accountableHistoryModel.test.ts", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0108-inspect-accountable-history.md", "docs/planning/work-packets/WRK-0192-present-accountable-history-to-learners.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Present Accountable History to Learners

## Objective and Deliverable

Deliver one reusable, accessible **Source and history** panel that consumes the
completed generated public client for both an exact lesson and each saved
knowledge-check result. The panel leads with plain explanations, missing-link
or validation guidance, and the learner's next safe action; keeps exact
versions, identifiers, times, kinds, relations, and integrity codes in a native
**Technical record** disclosure; and prepares a purpose-limited JSON download
only through the separate protected export operation.

The public API remains the sole authority. The browser validates and presents
the returned closed document but does not assemble history, infer a link,
recompute a digest, select a learner, or create another policy path.

## Required Context

Before any file change, read and follow repository-root `AGENTS.md` and
`docs/README.md`. Revalidate the current CAP-0026 package, active SLI-0108,
completed WRK-0189 through WRK-0191, the frozen accountable-history schemas,
provenance contract, generated client, protected session boundary, current
lesson and saved-completion consumers, interface design system, content style
guide, user-facing language standard, change-impact matrix, decision readiness,
nearest web README, and focused tests. Stop on conflicting canonical sources.

## Decisions and Assumptions

- The approved CAP-0026 package and active SLI-0108 authorize this dependent
  browser packet. No slice- or packet-level approval exists or is requested.
- WRK-0191 fixes the two protected generated-client operations and separate
  read/export permissions. This packet consumes and cannot widen them.
- The lesson panel uses the exact package ID, version, and digest already
  returned by the protected lesson read. A saved-result panel uses its exact
  evidence ID and its one-based position in the validated ordered completion
  history as the Audit occurrence. Neither path accepts typed or URL-selected
  learner, purpose, latest-version, provider, storage, or policy authority.
- Each panel loads only after a deliberate learner action. One failed history
  record does not disable lesson reading, the knowledge check, another saved
  result, or another panel.
- A portable download is a newly requested validated export. The browser may
  serialize that returned wrapper into an inert JSON `Blob`, start a local
  download, and immediately revoke its object URL. It never retains an export
  record or treats browser bytes as authority.
- Existing tokens, reviewed icons, button/status patterns, native `details`,
  session renewal, safe-download behavior, and lesson layout are sufficient.
  No shared design-system decision is introduced.

## In Scope

- Add a feature-owned runtime model that validates the generated closed lesson
  or completion request, root correlation, purpose, owner/resource-kind pairs,
  ordered bounded entries, references, relations, safe text, timestamps,
  diagnostics, redaction summaries, digests, and portable wrapper before use.
- Add read/export adapters using only the generated public client and current
  single-profile session, including one bounded unauthorized renewal and safe
  confidential failure mapping.
- Add a reusable panel with explicit idle, loading, ready, unavailable,
  forbidden, invalid-response, and download states. A retry repeats the same
  exact root; it does not silently substitute a newer record.
- Present title, summary, validation meaning, ordered steps, explicit gaps,
  safe diagnostics, and redaction meaning in plain learner language. Preserve
  exact returned technical facts in keyboard-operable disclosures.
- Embed a lesson-root panel beside publication details and one completion-root
  panel with each validated saved result. Varying zero/many sources, entries,
  transformations, gaps, diagnostics, redactions, and saved results must not
  depend on fixture counts or incidental order.
- Provide a deliberate **Download evidence record** action only after a
  validated review is visible. Validate the separate portable response, use
  the server filename and media type, announce success/failure, and create no
  file on denial, malformed data, changed root, or unavailable service.
- Add focused model, component, and Chromium evidence for lesson/completion
  behavior, isolation, keyboard/focus, axe, narrow reflow, text scaling,
  themes, forced colors, reduced motion, export cleanup, learner language,
  forbidden-field absence, and flexible valid shapes.
- Reconcile the web README, slice, packet, and planning register.

## Out of Scope

Backend, frozen schema, OpenAPI, generated-client regeneration, permission,
identity, persistence, migration, Audit composition, digest recomputation,
history mutation or repair, import, retained export, signing, encryption,
legal hold, recovery, background download, bulk export, search, pagination,
new lineage roots, URL-selected evidence, raw owner payload, lesson body,
answers, feedback, learner/profile identity, provider data, secrets, locators,
storage paths, raw exceptions, internal diagnostics, organization, tenant,
administrator, instructor, support, compliance, legal or public-audit access,
provider/model selection or execution, external action, financial action,
advice, suitability, mastery, certification, dependency change, shared token or
icon change, or unrelated visual polish.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generated public client | Exact history and export operations/types | No | Preserve browser/headless contract parity |
| Feature model/API | Existing session retry, runtime closure, safe-download patterns | New accountable-history files only | Keep browser validation and transport bounded |
| Lesson consumer | Protected lesson facts, saved completion ordering, existing actions | Listed lesson components only | Supply exact roots without new user-entered authority |
| Composition | Current dependency injection and global feature styles | `router.tsx`, `main.tsx` | Reuse one session-aware client seam and one feature stylesheet |
| Interface | Shared components, semantic tokens, reviewed icons, native disclosures | Feature panel and feature stylesheet | Deliver plain, accessible presentation without a parallel design system |
| Tests | Current model/component/browser, language, and boundary patterns | Three listed focused test files | Prove closure, isolation, accessibility, export cleanup, and anti-rigidity |
| Documentation/planning | Browser behavior, active slice, packet/register projection | Listed web and planning sources | Keep delivery meaning and status current |

No path outside `write_scope` may change. Stop if a backend, public contract,
generated client, dependency, shared token/icon, or unlisted shared component
must change.

## Contracts and Interfaces

`AccountableHistoryRequest` remains the generated discriminated lesson-or-
completion request. The lesson consumer constructs it only from the current
validated lesson. The completion consumer constructs it only from a validated
saved entry and its one-based ordered occurrence. The panel receives this
closed object as a prop; no form, query string, local storage, or free text can
alter it.

The reader returns either one runtime-validated `learner_review` document or a
closed failure state. The exporter returns either one validated
`portable_evidence` wrapper serialized as inert JSON with the server filename
and media type, or a closed failure state. Both validate exact root correlation
and reject unknown keys, invalid owner/kind combinations, noncanonical export
time, broken bounds, references, status, and digests. A browser check is
defensive consumption, not alternate authorization or business validation.

Primary content uses returned reviewed title/explanation text and stable plain
labels such as `Available history`, `Some history is unavailable`, and
`History could not be validated`. Raw enum values, resource kinds, owner module
names, relation codes, schema versions, IDs, digests, and exact timestamps stay
under `Technical record`. Required gaps and limitations remain in the primary
flow. The UI never calls a result tamper-proof, complete, compliant, mastered,
certified, suitable, or advised.

Download starts only from a validated export for the same exact root. It uses
`application/vnd.financial-ai-academy.accountable-history+json`, appends
`.json` to the bounded server stem, revokes the object URL, and announces the
result. Inspection remains usable when export is denied or unavailable.

## Dependencies and Parallel Safety

WRK-0191 is complete with a qualifying exact candidate and zero open findings.
WRK-0192 owns the shared lesson consumers, injected browser dependency, focused
feature source/tests, stylesheet, web documentation, and SLI/register
projection. It is not parallel-safe with another SLI-0108 writer and must
complete before WRK-0193 live cumulative qualification begins.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Lesson history | A validated lesson is open | Learner chooses **Show source and history** | One exact lesson request returns ordered plain history without disturbing lesson reading | component/Chromium |
| Saved-result history | A validated completion has zero or many saved results | Learner opens one result's history | Its exact evidence ID and ordered occurrence are used; other results and lesson content remain unchanged | component/Chromium |
| Deliberate loading | A panel has not been opened | Page renders | No history/export request occurs and ordinary learning remains available | component/network |
| Partial history | Valid response contains missing links, diagnostics, or incomplete entries | Panel opens | The gap and safe reason stay visible without invented replacement or raw internals | unit/component |
| Invalid history | Response has wrong root, purpose, owner/kind, order, reference, time, digest, unknown field, or forbidden key | Browser validates it | Panel fails closed, creates no download, and offers a bounded retry | parameterized unit/component |
| Technical evidence | Valid variable entries and relations exist | Learner opens **Technical record** | Every exact returned ID, version/occurrence, kind, owner, relation, time, status, and digest remains labeled and selectable | component/accessibility |
| Separate export authority | Inspection works but export is denied | Learner requests download | Inspection remains visible, no object URL/file is created, and a safe message explains that download is unavailable | component/Chromium |
| Portable export | Valid matching portable wrapper is returned | Learner downloads | One inert JSON file uses server media/name, URL is revoked, and no platform export state is retained | unit/component |
| Root change or malformed export | Export purpose/root/wrapper/entry differs or is invalid | Download validation runs | No file is created and the visible review remains unchanged | unit/component |
| Confidential failure | Session expires, permission is absent, root is unknown, or service fails | Read/export returns a bounded error | No existence, learner, permission, rejected value, stack, path, provider, or storage fact appears | component/Chromium |
| Accessible responsive use | Keyboard, axe, 320-pixel viewport, 200-percent text, both themes, forced colors, and reduced motion | Learner inspects and downloads | Equivalent content, action, focus, status, disclosure, and reflow remain usable | Chromium/design |
| Flexible valid shapes | Entry/gap/diagnostic/redaction counts and Unicode labels vary within bounds | Panel renders | Behavior follows invariants rather than fixed counts, IDs, or whole-document snapshots | unit/component |
| Headless parity retained | Browser files are absent | A protected headless caller uses WRK-0191 operations | The same authoritative inspection/export remains independently usable | generated-client/boundary |

## Verification Commands

- Run focused accountable-history model and component suites plus the lesson
  model/component regressions.
- Run the focused lesson Chromium journey with mocked valid, incomplete,
  denied, malformed, variable-shape, export, keyboard, axe, reflow, scaling,
  theme, forced-color, reduced-motion, network-containment, and cleanup cases.
- Run generated-client contract and browser-boundary tests, TypeScript
  typecheck, zero-warning lint, and production build.
- Run learner-language, design-system, architecture, security, documentation,
  planning, whitespace, controller-selected exact-candidate verification, one
  independent technical disposition, and
  `python dev-tools/agent/check_ready.py`.

Broader real PostgreSQL, restart, generated/direct-client parity, and
cumulative containment qualification remains WRK-0193 rather than becoming an
automatic full-suite gate for this browser packet.

## Documentation and Evidence Update

Document the reusable lesson/completion panel, generated-client-only read and
export, deliberate loading, plain-language hierarchy, progressive technical
record, export cleanup, isolated failures, and headless parity. Record focused
and affected checks, accessibility, language, anti-rigidity, assumptions, and
remaining live-qualification gaps. Keep approval, reviewer, and receipt data
only in ignored local control-plane storage.

## Stop Conditions

Stop for stale CAP authority; an unresolved identity, tenancy, retention,
deletion, signing, encryption, recovery, legal/commercial, public-hosting, or
external-execution choice; a new root; organization/admin/support access;
history mutation; copied owner data; caller-selected learner or purpose; raw
private payload or diagnostic disclosure; retained/browser-authoritative
export; backend or schema change; handwritten transport; generated-client
drift; dependency change; shared design-system change; file collision; or
material CAP-0026/SLI-0108 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
valid count/order/Unicode variation, nonfunctional styling, or another
inconsequential issue. Fix bounded defects locally or defer optional polish to
CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0108.WRK-0192`; exact candidate and qualifying receipt;
lesson and completion roots; read/export adapters; plain primary content and
technical evidence; isolated failures and export cleanup; generated-client and
headless parity; focused browser/accessibility/language, architecture,
security, documentation and readiness evidence; migration/rollback;
assumptions; residual live gaps; CAP conformance; and unresolved decisions.
Confirm no backend, public contract, persistence, provider/model, external
action, tenancy/admin, retained export, history mutation, financial authority,
advice, suitability, mastery, or certification changed.

## Planning History

- 2026-10-18: Authored just in time after WRK-0191 completed. The packet adds
  one generated-client-only panel for exact lesson and saved-completion roots,
  plain primary history, complete progressive technical evidence, isolated
  failure, and purpose-limited on-demand export. It preserves API/headless
  authority and requires no lower-level approval within the current CAP-0026
  package.
- 2026-10-18: Deterministic packet validation passed with the completed API
  dependency, exact browser-only write scope, current canonical interface and
  language standards, resolved local decision posture, and executable focused
  verification. The packet is ready to claim.
