---
id: SLI-0108
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: CAP-0026
depends_on: ["SLI-0107"]
decision_gates: []
---

# Vertical Slice: Inspect Accountable History

## Outcome and User Scenario

An authorized learner can inspect where a lesson or completion record came
from, which transformations produced it, whether links are missing or invalid,
and whether integrity checks detected a conflict. The same authoritative result
is available through the protected API for headless clients. A learner may also
download a deterministic, purpose-limited evidence record without exposing
private payloads, provider secrets, persistence details, or another learner's
history.

## Scope Boundaries

### In Scope

- A versioned `accountable-history/v1` contract for inspection, safe
  diagnostics, redaction facts, and portable evidence export over the existing
  learning-lineage root delivered by SLI-0106.
- Closed local purposes for learner review and portable evidence. Purpose is
  selected by the operation, not accepted as an open-ended policy string.
- Pure Audit composition that converts an already validated lineage view into
  ordered plain-language history, bounded technical facts, explicit missing
  links, validation state, and safe tamper diagnostics.
- A separate protected export permission and endpoint so inspection access does
  not automatically grant download authority.
- A generated public TypeScript client and an accessible browser view titled
  **Source and history**. Ordinary explanations use plain language; exact IDs,
  versions, integrity values, and technical labels appear under a secondary
  **Technical record** section.
- Deterministic on-demand JSON export with an exact contract version and digest.
  No export is retained by the platform.
- Compatibility, authorization, redaction, isolation, accessibility,
  restartability, headless/browser parity, and anti-rigidity evidence.

### Out of Scope

- Organization, tenant, administrator, support, instructor, compliance, legal,
  or public-audit access; those require their owning identity and policy work.
- Selecting retention periods, legal hold, regulatory rules, deletion policy,
  managed-cloud storage, signing keys, immutable infrastructure, or recovery.
- Mutating, correcting, appending, deleting, or rebuilding authoritative
  history. This slice exposes a read-only derived view and on-demand export.
- Copying owner records, lesson content, submissions, profile data, provider
  payloads, internal errors, paths, stack traces, tokens, or storage details
  into Audit, the API, the browser, or an export.
- Live presentation of SLI-0107's synthetic future-owner profiles. The current
  product operation remains the real learning lineage; later owner CAPs adopt
  the additive cross-domain contract through their public seams.
- Claims of correctness, mastery, advice, suitability, regulatory compliance,
  complete history, or tamper-proof storage.
- Broad visual redesign or nonfunctional styling work, which remains CAP-0031.

## Canonical Context and Decisions

- [CAP-0026](../capabilities/CAP-0026-preserve-provenance-and-accountable-history.md)
  authorizes an authorized, purpose-limited history and export after the
  learning and cross-domain provenance foundations.
- [Provenance and Lineage Contract](../../architecture/contracts/provenance-and-lineage-contract.md),
  [Data Architecture](../../architecture/data/data-architecture.md),
  [Module Map](../../architecture/modules/module-map.md), and
  [Contract Architecture](../../architecture/contracts/contract-architecture.md)
  keep owner data with its module and make Audit a bounded composer rather than
  a second domain database.
- [Interface Design Standards](../../standards/interface-design-standards.md),
  [User-Facing Language Standards](../../standards/user-facing-language-standards.md),
  and the [Design Style Guide](../../design/style-guide.md) require plain task
  language, accessible disclosure, shared tokens and icons, equivalent themes,
  keyboard access, and responsive behavior.
- Accepted ADR-0005 and the completed SLI-0106 and SLI-0107 artifacts preserve
  exact Learning ownership, a protected public operation, additive contract
  versioning, and bounded reference-only cross-domain extension.
- The decision-readiness register exposes no unresolved choice for a local
  learner's read-only inspection and ephemeral export. Tenant, administrator,
  managed retention, legal/commercial, encryption-key, and immutable-storage
  choices remain outside this slice and are stop conditions if introduced.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Build a headless-first deterministic inspection and export projection, then consume its generated client in an accessible browser view | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Assemble history and redaction rules in the browser from existing responses | no; it makes the client authoritative, weakens redaction, and omits headless parity | - | - | - | - | - | - | - |
| C. Copy all owner history into a mutable Audit store before inspection | no; it violates owner authority and turns Audit into a second domain database | - | - | - | - | - | - | - |
| D. Expose only the protected API and defer all human inspection | yes, but it leaves the approved user-observable increment incomplete | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 12 |

## Selection Rationale

Candidate A scores 14 of 14 because one deterministic server result governs
headless, browser, and export behavior. It gives the learner a usable account of
source and history without placing authorization, redaction, diagnostics, or
digest decisions in TypeScript. Candidate B is ineligible because private-data
protection cannot depend on UI assembly. Candidate C violates the approved
ownership boundary. Candidate D is architecturally sound but does not complete
the human inspection outcome authorized by CAP-0026.

The selection preserves the approved capability outcome, four-slice manifest,
order, decision posture, risks, and non-goals. It requires no slice-level or
work-level approval.

## Boundary Path

1. Additive schemas freeze a closed request, inspection document, safe
   diagnostic family, redaction summary, and portable export document without
   changing `provenance-envelope/v1` or `provenance-envelope/v2`.
2. The pure Audit core accepts only a validated SLI-0106 `LineageView`, a closed
   purpose, and bounded display context. It canonicalizes ordering, maps errors
   to safe codes, and removes fields not permitted for that purpose.
3. Audit application/public operations authorize the current learner, open the
   real Learning lineage through existing public seams, and compose inspection
   or export without cross-module persistence access.
4. The host exposes separate protected inspection and export operations. Export
   requires explicit export permission and returns a bounded JSON document; no
   file path or retained download record is created.
5. The OpenAPI snapshot and generated TypeScript client remain the sole browser
   transport contract.
6. The browser renders plain source/history explanations, expandable technical
   facts, safe status text, missing-link guidance, and a deliberate download
   action with keyboard, focus, reflow, theme, and screen-reader equivalence.
7. Live qualification proves authorization, redaction, deterministic output,
   restart behavior, headless/browser parity, database containment, and
   isolation from malformed or unavailable records.

## Contracts, Data, Redaction, and Export

`accountable-history/v1` is an additive view contract, not a new authoritative
record. The request identifies one existing lesson or completion root and one
closed purpose. The response contains a summary, ordered history steps,
transformation relations, incomplete-link facts, validation state, safe
diagnostics, redaction facts, exact technical identifiers, contract version,
and a deterministic digest over the disclosed content.

The learner-review purpose returns only facts needed to understand the source
and processing of the current record. The portable-evidence purpose may include
the same bounded technical facts in a stable JSON export but never lesson body,
answers, profile attributes, provider payloads, internal error text, storage
coordinates, or another learner's identifiers. Redaction reports categories and
counts, not rejected values. Missing and invalid links remain explicit rather
than being silently dropped or described as proof of tampering.

Diagnostics are closed safe codes such as incomplete link, unsupported version,
integrity mismatch, invalid relation, or temporarily unavailable owner. They
describe validation results and do not claim malicious activity, regulatory
noncompliance, or tamper-proof storage. Observed, calculated, simulated,
predicted, generated, and administrative labels retain their existing origin
meaning and do not grant authority.

Exports are produced on demand from the same authorized view, use canonical JSON
ordering, include their disclosed-content digest, and are not persisted by the
platform. A later contract version is required for any meaning change.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Authorized lesson review | The current learner requests one available lesson's source and history | The protected API and browser show the same bounded ordered explanation and exact technical facts | application/browser |
| Authorized completion review | The current learner requests one of their completion records | Evidence source, grading transformation, integrity and validation states are visible without answer or profile payloads | application/security |
| Separate export authority | A learner can inspect but lacks the export permission | Inspection succeeds and export is denied with the standard confidential response | authorization/contract |
| Portable evidence export | An authorized learner downloads the same root twice | Canonical JSON bytes and disclosed-content digest are identical and no retained export record is created | contract/integration |
| Purpose-limited redaction | A lineage contains fields or diagnostic values outside the selected purpose | Those values are absent; bounded categories and counts explain the redaction without echoing secrets | domain/security |
| Missing or unavailable link | An owner reference is absent or temporarily unavailable | The view remains usable, marks the exact gap, and does not invent a replacement or disable unrelated records | domain/isolation |
| Integrity or validation failure | A digest, relation, or contract version fails validation | A closed safe diagnostic is returned without raw payload, rejected value, path, or stack trace | contract/security |
| Unauthorized learner | A caller requests another learner's root, an unknown root, or malformed identity | The response remains confidential and does not disclose existence or validation detail | authorization/security |
| Headless/browser parity | The browser renders a generated-client response from the live operation | Human content, statuses, technical facts, and export availability match the server contract; no client policy is authoritative | contract/browser |
| Variable valid history | Step counts, relation order, optional facts, Unicode text, and valid missing-link combinations vary | Canonical results are deterministic without fixed fixture counts or whole-page snapshots | property/anti-rigidity |
| Accessible responsive use | The view is used by keyboard and screen reader at narrow and wide layouts in both themes | Content, actions, focus, disclosure, contrast, and status meaning remain equivalent | browser/accessibility |
| Restart and containment | The host restarts between equivalent requests | The result rebuilds from owner operations, no Audit business copy or export state appears, and local database ownership remains intact | integration/architecture |

## Agent Work Packets

Detailed packet files are authored one at a time immediately before work starts.
The dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| [WRK-0189](../work-packets/WRK-0189-freeze-accountable-history-contracts.md) | Freeze accountable-history inspection, diagnostic, redaction, export, compatibility, and safe-language contracts | none | none | complete |
| [WRK-0190](../work-packets/WRK-0190-implement-accountable-history-core.md) | Implement the pure Audit inspection, purpose-limited redaction, safe diagnostic, canonical export, and anti-rigidity core | WRK-0189 | none | complete |
| [WRK-0191](../work-packets/WRK-0191-expose-protected-accountable-history-api.md) | Expose protected Audit inspection/export operations through FastAPI, OpenAPI, and the generated TypeScript client | WRK-0190 | none | active |
| WRK-0192 | Add the accessible plain-language Source and history browser view using only the generated client | WRK-0191 | none | captured |
| WRK-0193 | Qualify headless/browser parity, authorization, redaction, export, restart, containment, accessibility, and slice completion | WRK-0192 | none | captured |

Sequential delivery is required because each packet freezes the meaning consumed
by the next. No safe parallel packet exists inside this small shared contract and
presentation boundary. A bounded correction may add a dependent packet without
changing the approved CAP or slice outcome.

## Verification and Qualification

Run schema and compatibility conformance; safe diagnostic, redaction, canonical
ordering/digest, and property tests; application authorization and public-only
dependency checks; FastAPI and OpenAPI contract tests; generated-client parity;
browser component and Chromium tests; keyboard, focus, reflow, light/dark, and
automated accessibility checks; confidential-denial and secret-leak tests;
restart and database-containment integration; documentation and planning checks;
whitespace integrity; design-system integrity; and aggregate agent readiness.
Tests vary valid counts, order, optional facts, Unicode values, and partial
history and avoid brittle whole-document or pixel snapshots.

## Rollback and Migration

The contract, pure view, public operations, endpoints, generated client, and UI
are additive. No database migration, retained export, owner-state rewrite, or
provider change applies. Before product adoption they can be removed without
changing existing lineage. After adoption, meaning changes through a later
contract version; rollback disables the new routes and browser entry while
leaving SLI-0106 and SLI-0107 intact.

## Stop Conditions

Stop for stale capability authority; conflicting owner semantics; organization,
tenant, administrator, support, instructor, legal, or compliance access; managed
retention or deletion policy; encryption-key, signing, recovery, immutable-
storage, or public-disclosure choices; history mutation; copied owner records;
provider-specific payloads; a new cross-module database join; external action;
or a breaking existing provenance contract.

Do not stop or reopen review solely for harmless whitespace, optional wording,
valid fixture count/order, nonfunctional styling, or another inconsequential
issue. Fix bounded documentation locally or route optional polish to CAP-0031.

## Documentation Impact and Completion Evidence

Update the provenance contract guide, contract catalog, Audit contributor
instructions, host/API documentation, generated-client notes, interface content
examples, packet artifacts, this slice, and the planning register. Completion
evidence must record exact candidates and qualifying receipts, contract and
compatibility results, authorization/redaction/secret-leak results, headless and
browser parity, accessibility, restart/database containment, architecture and
security gates, aggregate readiness, migration status, residual gaps, and CAP
conformance.

## Planning History

- 2026-10-18: Refined immediately after SLI-0107 completion. Candidate A scores
  14 of 14 and selects one headless-first authoritative inspection/export view,
  a generated-client browser consumer, purpose-limited redaction, and cumulative
  live qualification. The refinement preserves CAP-0026's approved outcome,
  manifest, sequence, decision posture, risks, and non-goals; no lower-level
  approval exists or is required.
- 2026-10-18: Activated dependency-first WRK-0189 after confirming current CAP
  authority, completed SLI-0107, resolved local decision posture, exact
  contract-only write scope, and no active ownership collision.
- 2026-10-18: WRK-0189 completed with the additive accountable-history contract,
  compatibility corpus, deterministic export rules, bounded diagnostic and
  redaction meaning, unchanged provenance v1/v2 fingerprints, and current
  qualifying evidence. WRK-0190 is now dependency-ready.
- 2026-10-18: Authored WRK-0190 just in time with a pure-core and strict-adapter
  boundary, truthful zero/many-source pressure tests, deterministic portable
  export, exact write scope, and no application, authorization, API/client,
  browser, persistence, or lower-level approval expansion.
- 2026-10-18: WRK-0190 completed at exact candidate `e7c916e` with the
  framework-free composer and strict adapter, a contract-parity bound of 128
  transformations, truthful zero/one/many-source behavior, deterministic
  portable export, and current qualifying evidence. The dependent public API
  packet is now eligible.
- 2026-10-18: Authored WRK-0191 just in time with separate inspection and
  export permissions, server-selected purpose, session-bound completion
  identity, exact frozen responses, generated headless client parity, bounded
  write scope, and no persistence, browser, tenant/admin, or lower-level
  approval expansion.
- 2026-10-18: Activated WRK-0191 after revalidating the current CAP package,
  completed WRK-0190 dependency, local decision posture, exact public API and
  generated-artifact scope, and absence of a file-ownership collision.
