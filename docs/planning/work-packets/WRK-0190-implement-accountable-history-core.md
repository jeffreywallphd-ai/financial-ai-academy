---
id: WRK-0190
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0108
capability: CAP-0026
depends_on: ["WRK-0189"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/audit/README.md", "backend/src/financial_ai_academy/modules/audit/adapters/__init__.py", "backend/src/financial_ai_academy/modules/audit/adapters/accountable_history_contract.py", "backend/src/financial_ai_academy/modules/audit/domain/__init__.py", "backend/src/financial_ai_academy/modules/audit/domain/accountable_history.py", "backend/tests/contract/accountable_history/runner.py", "backend/tests/contract/accountable_history/test_conformance.py", "backend/tests/unit/audit/test_accountable_history.py", "contracts/compatibility/accountable-history/v1/approved/incomplete-review.json", "contracts/compatibility/accountable-history/v1/approved/lesson-review.json", "contracts/compatibility/accountable-history/v1/vectors/canonicalization.json", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0108-inspect-accountable-history.md", "docs/planning/work-packets/WRK-0190-implement-accountable-history-core.md"]
generated_artifacts: []
base_revision: 52fbbc5c62fa4921a901f4a8156462edfc1fcd8b
claim_id: WRK-0190:940c1a68-2278-4282-942b-147ac1f53df5
claimed_by: codex-cap-0026
claimed_at: 2026-10-18T10:16:06Z
---

# Agent Work Packet: Implement Accountable History Core

## Objective and Deliverable

Implement the pure Audit core that turns one already validated learning-lineage
view into the frozen `accountable-history/v1` learner-review document or
portable-evidence wrapper. Deliver immutable domain values, deterministic
composition, a strict mapping adapter, purpose-bound reviewed copy, explicit
gaps and safe diagnostics, bounded redaction facts, canonical digests and
exports, and anti-rigidity unit/contract evidence.

The packet leaves one framework-free shared-core result for WRK-0191 to expose.
It does not authorize a caller, load lineage, call another module, persist or
retain an export, expose HTTP, generate a client, or add browser behavior.

## Required Context

The Required Startup in `AGENTS.md` and `docs/README.md` was completed and
reported before this planning edit. Review covered context routing, change
impact, decision readiness, CAP-0026, SLI-0108, completed WRK-0189, provenance
and accountable-history contracts, Audit domain/adapters/public seams,
learning-lineage tests, interface language standards, and the nearest READMEs.

Before implementation, revalidate the current CAP and slice, exact WRK-0189
contract candidate, dependency completion, decision readiness, and file
ownership. Inspect the complete lineage value/adapter, compatibility runner and
fixtures, all Audit exports, consumers, unit tests, and architecture fitness
rules before editing.

## Decisions and Assumptions

- CAP-0026 authority and SLI-0108 selection remain current; WRK-0189 is complete
  at its recorded exact candidate and the local learner read/export boundary
  introduces no unresolved durable decision.
- The composer accepts only a validated `LineageView`; it does not reinterpret
  owner records, repair an invalid graph, or turn a lineage reference into
  access, grading, mastery, compliance, legal, financial, or execution meaning.
- `learner_review` and `portable_evidence` are closed domain values selected by
  separate future operations. No arbitrary purpose, wording, redaction rule,
  identity, policy, field list, or runtime registry enters the core.
- Reviewed display text is selected from a versioned internal catalog correlated
  to purpose, root, and state. Exact technical facts remain available beside
  ordinary language; raw payload, authoring content, answer, score, feedback,
  learner identity, provider material, internal errors, and storage details do
  not enter the values.
- A valid lesson may have zero, one, or many reviewed sources. Its generic
  reviewed summary must remain accurate at every valid count; this packet may
  reconcile the one affected approved compatibility fixture/vector and runner
  catalog without changing schema shape, existing technical facts, or any
  provenance v1/v2 meaning.

## In Scope

- Add immutable accountable-history purpose, state, role, diagnostic, redaction,
  entry, transformation, missing-link, document, and export values under Audit.
- Compose deterministic ordered entries and transformations from validated
  lineage nodes and edges, preserving exact resource identities, digests,
  source times, validation status, Unicode, and existing relation meaning.
- Map incomplete lineage links to explicit missing-link facts and one closed
  safe diagnostic per distinct gap. Map not-found, unavailable, and redacted
  reasons without raw exceptions or rejected values.
- Derive state from validated source facts: complete inputs are `valid` and
  explicit gaps or truncation are `incomplete`. Invalid untrusted inputs fail
  closed rather than producing a plausible document.
- Derive redaction counts from disclosed topology and root kind without
  inspecting or copying owned payloads. Preserve purpose isolation and never
  let a caller choose which fields are omitted.
- Canonicalize UTC times, semantic sequence/link/gap/diagnostic/redaction order,
  and compact sorted-key UTF-8 JSON. Bind the full disclosed document with
  lowercase SHA-256 excluding its own digest.
- Build portable evidence from the same composed meaning with a deterministic
  ASCII filename stem based on the exact root, latest source instant, fixed
  media type, and document digest. Perform no file or storage I/O.
- Add a strict mapping adapter whose output matches the frozen contract and
  whose input accepts no unknown field, framework object, persistence handle,
  or provider-specific value.
- Add contract pressure and unit/property tests for zero/one/many sources,
  varied valid node counts and order, Unicode identities, time offsets and
  fractional precision, partial gaps, changed meaning, malformed values,
  purpose separation, deterministic replay, redaction, confidentiality, and
  fixture-independent composition.
- Reconcile only the approved lesson-review summary, canonical digest vector,
  and reviewed-copy catalog if required to keep zero-source lessons truthful.

## Out of Scope

- Audit application/public operations, permissions, opaque sessions, Identity,
  FastAPI, OpenAPI, generated TypeScript, browser code, downloadable response
  headers, or live host composition.
- Database tables, migrations, repositories, object/file storage, retained
  downloads, signing, encryption, keys, queue, job, notification, recovery,
  deletion, retention, or legal hold.
- Organization, tenant, instructor, administrator, support, compliance, public-
  audit, managed-cloud, or commercial policy.
- New lineage roots, owner profiles, cross-domain live graphs, provider/model
  calls, datasets, recommendations, financial calculations, external actions,
  history mutation, or copied owner records.
- Arbitrary localization, Markdown/HTML, caller-supplied copy, visual styling,
  or unrelated cleanup.

## Expected File and Boundary Impact

| Area | Allowed change | Boundary |
| --- | --- | --- |
| Audit domain | new pure accountable-history values/composer and domain exports | imports only Audit domain provenance values and standard library |
| Audit adapter | new strict mapping/canonical JSON adapter and adapter exports | no framework, repository, network, clock, owner, or provider dependency |
| Unit/contract evidence | isolated core tests plus bounded runner pressure tests | vary valid shapes; no fixture-count coupling or product import in contract runner |
| Frozen compatibility | at most one generic valid-lesson summary and its exact digest vector/catalog | no schema shape, technical fact, denial, or provenance v1/v2 reinterpretation |
| Audit documentation | exact pure-core ownership and non-authority statement | do not describe API/application/UI work as delivered |
| Planning | this packet, SLI-0108, register lifecycle/evidence only | no CAP/slice outcome or manifest change |

## Contracts and Interfaces

1. `compose_accountable_history(lineage, purpose)` validates the exact lineage,
   canonicalizes it, and returns one immutable history document. The purpose is
   a closed enum, not a stringly policy selector.
2. Resource kind determines owner, role, reviewed entry label, and exact
   identity form. Sequence follows canonical lineage order; transformations and
   gaps correlate only disclosed entry IDs.
3. Missing-link reason determines one reviewed explanation and diagnostic code.
   Truncation is explicit and incomplete. Invalid lineage raises one bounded
   domain error without raw input or a partial document.
4. `accountable_history_payload(document)` returns the exact contract mapping;
   `accountable_history_document_from_mapping` admits only that exact shape and
   recomputes semantic consistency and digest.
5. `build_portable_evidence(lineage)` uses the same composer with the portable
   purpose. `portable_evidence_payload` produces exact canonical contract data,
   derives time and filename from source facts, and performs no I/O.
6. Canonicalization and digest semantics match WRK-0189 byte-for-byte. Equivalent
   source order or timezone offsets produce equal output; changed disclosed
   meaning changes the digest.

## Dependencies and Parallel Safety

WRK-0189 is complete and owns the contract consumed here. WRK-0191 depends on
this packet. No SLI-0108 packet is parallel-safe because the next public/API
layer imports this exact core and the planning/Audit files overlap.

## Acceptance Scenarios

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Valid lesson with zero, one, or many sources | truthful generic summary, exact available entries, stable order, no invented gap | property/unit/contract |
| Valid completion | lesson, definition, event/evidence and Audit facts compose without answer, score, feedback, or learner identity | unit/security |
| Explicit unavailable source | usable incomplete document with exact gap and reviewed safe diagnostic | unit/contract |
| Purpose separation | learner and portable documents use their correlated copy and purpose; cross-purpose mappings fail | unit/denial |
| Portable evidence | repeated composition yields equal mapping, digest, ASCII filename and source-derived export time | unit/vector |
| Equivalent input | reordered nodes/links and equivalent offsets yield identical canonical output | property/unit |
| Variable valid history | bounded counts and Unicode identifiers work without hard-coded fixture length | property/anti-rigidity |
| Invalid input | changed digest, relation, identity, unsafe mapping key, or wrong type fails closed without raw detail | unit/security |
| Layer isolation | core and adapter import no application, public, framework, repository, provider, network, or clock seam | architecture |

## Verification Commands

- `backend\.venv\Scripts\python.exe -m pytest backend/tests/unit/audit/test_accountable_history.py backend/tests/unit/audit/test_provenance_contract.py backend/tests/contract/accountable_history -q`
- `backend\.venv\Scripts\python.exe -m pytest backend/tests/unit/audit backend/tests/contract/accountable_history backend/tests/contract/provenance backend/tests/contract/provenance_v2 -q`
- `python backend/tests/architecture/test_module_boundaries.py`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Run the controller-selected affected plan and exact-candidate verification after
freezing the candidate, then obtain an independent technical disposition.
PostgreSQL, Docker, FastAPI, OpenAPI, generated-client, and browser checks are
not routine for this framework-free packet.

## Documentation and Evidence Update

Record domain value/composer/adapter semantics, purpose and redaction behavior,
zero/many-source anti-rigidity, canonical/export parity, focused and affected
checks, exact candidate and receipt, migration/rollback posture, residual gaps,
and CAP/slice conformance. Approval and reviewer records remain only in ignored
local state.

## Stop Conditions

Stop for a changed owner fact; contract shape/version break; a new root or
purpose; caller-defined wording/redaction; copied owner payload; application or
authorization policy; persistence/retention/signing/encryption/recovery; tenant,
admin, instructor, support, legal/commercial, public disclosure, provider/model,
external action, financial authority, scope collision, or material CAP drift.

Do not stop or reopen approval for truthful generic copy, valid count/order/
Unicode variation, harmless whitespace, optional prose, or other inconsequential
cleanup. Fix bounded defects locally or defer visual polish to CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0108.WRK-0190`; exact candidate and receipt; pure values,
composer and strict mapping adapter; purpose/copy/redaction/gap behavior;
canonical/export parity; anti-rigidity and confidentiality results; architecture,
security, documentation and readiness evidence; migration/rollback status;
assumptions, residual gaps, CAP conformance, and unresolved decisions. Confirm no
application/public API, persistence, client/UI, identity, provider/model, tenant/
admin, external action, or financial authority changed.

## Planning History

- 2026-10-18: Authored just in time after WRK-0189 completion. The packet
  implements the frozen framework-free Audit core and strict adapter, includes
  consumer-pressure evidence for zero/many-source accuracy, and leaves all
  authorization, API/client, browser, persistence, and live qualification to
  dependent packets without adding a lower-level approval.
- 2026-10-18: Activated from clean base `e373ef4` after confirming current CAP
  authority, completed WRK-0189, resolved local decision posture, deterministic
  packet validation, exact write scope, and no active ownership collision.
- 2026-10-18: Incrementally added the approved incomplete-review fixture to the
  bounded compatibility scope so zero/many-gap copy can remain truthful without
  changing schema shape, technical facts, or provenance meaning.
- 2026-10-18: Reclaimed the refined packet from clean base `52fbbc5` after
  revalidating the expanded bounded scope, dependency completion, decision
  posture, and absence of a file-ownership collision.
- 2026-10-18: Submitted exact candidate `5811505` after 173 Audit/provenance
  unit and contract tests passed with direct product/contract canonicalization
  parity, together with architecture, security, documentation, planning,
  whitespace, and all 30 aggregate-readiness checks.
- 2026-10-18: Completed at corrected exact candidate `e7c916e` with qualifying
  receipt digest `sha256:0f04a3fc291f771b1b9452e6b4975b565ffcbd17ad49b294bb05a0f9b60017b0`.
  The final boundary enforces the frozen 128-transformation maximum and keeps
  canonical documentation aligned with the delivered shared core. Focused 49
  and affected 174-test suites passed together with module, architecture,
  security, documentation, planning, whitespace, and all 30 aggregate-readiness
  checks. No migration, persistence, permission, public API, client, UI,
  identity, provider/model, tenant/admin, external-action, or financial-
  authority change applies.
