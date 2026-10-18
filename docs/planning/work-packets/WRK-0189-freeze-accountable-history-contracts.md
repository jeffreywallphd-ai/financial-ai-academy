---
id: WRK-0189
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0108
capability: CAP-0026
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/audit/README.md", "backend/src/financial_ai_academy/modules/guidance/adapters/immutable_corpus.py", "backend/src/financial_ai_academy/modules/guidance/resources/contextual-help/v1/practice-result.json", "backend/src/financial_ai_academy/modules/guidance/resources/contextual-help/v1/project-result.json", "backend/src/financial_ai_academy/modules/guidance/resources/feature-guidance/v1/mappings/lesson-reading-exact-version-unavailable.json", "backend/src/financial_ai_academy/modules/guidance/resources/feature-guidance/v1/records/lesson-version-unavailable.json", "backend/src/financial_ai_academy/modules/guidance/resources/platform-help/v1/data-meaning.json", "backend/tests/contract/accountable_history", "backend/tests/contract/contextual_help/test_conformance.py", "contracts/README.md", "contracts/accountable-history/v1", "contracts/compatibility/README.md", "contracts/compatibility/accountable-history/v1", "contracts/compatibility/contextual-help/v1/approved/context.json", "contracts/compatibility/contextual-help/v1/vectors/canonicalization.json", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0108-inspect-accountable-history.md", "docs/planning/work-packets/WRK-0189-freeze-accountable-history-contracts.md"]
generated_artifacts: []
base_revision: dd3cb7172224e3b1e4d88d1a500fdc979755f6f2
claim_id: WRK-0189:fbda5e77-8ee4-4ce0-85ea-ab543796112a
claimed_by: codex-cap-0026
claimed_at: 2026-10-18T09:55:04Z
---

# Agent Work Packet: Freeze Accountable History Contracts

## Objective and Deliverable

Freeze the additive, language-neutral `accountable-history/v1` family that
turns one already authorized learning-lineage root into a purpose-limited
inspection or portable evidence document. Deliver executable Draft 2020-12
schemas, approved and denial compatibility fixtures, canonicalization vectors,
a dependency-light conformance runner, safe diagnostic and redaction meaning,
and canonical ownership documentation.

The packet leaves one coherent contract-only result. It does not implement the
Audit composition core, authorize a caller, call owner modules, expose HTTP,
generate a client, add a browser view, persist an export, or change provenance
v1/v2 meaning. Those seams remain WRK-0190 through WRK-0193.

## Required Context

Before this planning edit, the repository `AGENTS.md` and `docs/README.md`
Required Startup was completed and reported. Review covered context routing,
change impact, decision readiness, CAP-0026, completed SLI-0106/SLI-0107,
SLI-0108, provenance contracts/core/API, Audit ownership, current Identity
permissions, interface and user-language standards, tests, consumers, and
nearest READMEs.

Before implementation changes, report the applicable startup gate, revalidate
the current CAP and slice, and inspect the provenance v1 schemas/corpus, pure
values and adapter, live lineage operation, contract catalogs, architecture and
provenance guides, Guidance source bindings, contract-test conventions, and all
direct consumers affected by the new contract directory.

## Decisions and Assumptions

- CAP-0026 authority is current, SLI-0108 is in its exact manifest, SLI-0107 is
  complete, and no unresolved decision applies to a local learner's read-only
  inspection or ephemeral export contract.
- `accountable-history/v1` consumes one validated `LineageViewV1` later; it
  neither changes nor re-embeds an owner payload. Provenance v1/v2 fingerprints
  remain exact.
- Two separate operations select two closed purposes: `learner_review` and
  `portable_evidence`. The caller never supplies an arbitrary purpose or
  learner, tenant, role, policy, redaction rule, or output field list.
- Inspection and export share one disclosed-content shape. The export wrapper
  changes the purpose and binds exact canonical bytes and digest; it contains
  no retained download or storage reference.
- Diagnostics describe validation state, not malicious intent, regulatory
  compliance, or tamper-proof storage. They expose only a closed code and safe
  reference, never rejected values, payloads, or internal exceptions.
- Plain display text is versioned contract data for the current English product
  and is accompanied by exact technical facts. Later localization or meaning
  changes require additive contract evolution rather than silent replacement.

## In Scope

- Add `contracts/accountable-history/v1` documentation and schemas for:
  closed lesson/completion root requests; one disclosed history document;
  purpose, overall validation state, ordered history entries, transformation
  links, missing links, safe diagnostics, redaction summary, exact technical
  facts, display text, and disclosed-content digest; and one portable export
  wrapper.
- Freeze the request rule that learner identity and purpose are server-bound.
  Requests contain only the existing closed learning root selector.
- Close purposes to `learner_review` and `portable_evidence`; overall states to
  `valid`, `incomplete`, and `invalid`; entry roles to `source`, `published`,
  `defined`, `completed`, and `recorded`; and transformation relations to the
  existing provenance v1 relations.
- Close safe diagnostics to `missing_reference`, `owner_unavailable`,
  `unsupported_contract_version`, `integrity_mismatch`, `invalid_relation`,
  `identity_conflict`, and `redacted_detail`. A diagnostic includes only its
  code, a bounded safe reference, and reviewed plain-language explanation.
- Define bounded redaction categories for protected content, learner/private
  identity, owner payload, provider/secret material, internal diagnostics, and
  storage details. Summaries expose only category and nonnegative count.
- Define exact portable export canonicalization: compact sorted-key UTF-8 JSON,
  unescaped Unicode, UTC `Z` times, semantic order for entries/links/
  diagnostics/redactions, and lowercase SHA-256 over the disclosed document.
- Add approved learner-review and portable-evidence fixtures for lesson and
  completion roots, including incomplete history, safe diagnostics, redaction,
  Unicode, varied valid counts, and input reordering.
- Add denial fixtures for open purposes, learner/role/tenant selectors, answer
  or lesson body, provider payloads, secrets, storage/path/URL fields, raw
  errors, unknown keys/codes, invalid or duplicate order, changed identity,
  mismatched digest, unsafe text, and exceeded bounds.
- Add a dependency-light runner that loads only contracts/corpus, validates
  shape and semantics, verifies canonical vectors and provenance v1/v2
  fingerprints, and emits bounded diagnostics without product imports.
- Update contract catalogs and exact architecture/provenance/verification
  documentation. Reconcile only the immutable Guidance fingerprints and direct
  compatibility vectors mechanically affected by the canonical contract-
  architecture edit; do not change Help meaning or prose.

## Out of Scope

- Production Audit domain/application/adapter/public code, authorization,
  permissions, FastAPI, OpenAPI, generated clients, Web code, browser copy, or
  deployment behavior.
- Persistence, migration, export retention, file creation, signing, encryption,
  key management, queue, notification, background job, recovery, or deletion.
- Tenant, organization, instructor, administrator, support, compliance, legal,
  public-audit, or managed-cloud policy.
- A new lineage root, cross-domain v2 graph, live future-owner profile,
  provider/model call, dataset, financial calculation, recommendation, external
  action, or copied business record.
- Arbitrary display HTML/Markdown, active content, arbitrary diagnostic prose,
  caller-chosen redaction, dynamic contract registration, or unrelated cleanup.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | provenance v1/v2 and adjacent contract conventions | new `accountable-history/v1` schemas/README and catalog entry | freeze portable inspection/export shape |
| Compatibility | provenance and other compatibility conventions | new history v1 corpus/vectors plus catalog | bind exact accepted/rejected meaning and fingerprints |
| Contract qualification | existing dependency-light runners | new isolated accountable-history runner/tests | execute shape, semantics, canonicalization, privacy, and compatibility evidence |
| Canonical architecture | contract architecture, provenance guide, verification map, Audit README | exact new family/ownership/non-authority sections | state boundaries and maturity honestly |
| Derived Guidance binding | immutable corpus and records bound to contract architecture | only changed source fingerprint constants and their exact vectors/assertions | keep immutable source evidence current without changing Help meaning |
| Planning | SLI-0108, this packet, register | lifecycle/evidence sections only | maintain governed state |

No production behavior, public API/client, persistence, migration, Web,
deployment, dependency, provider, model, Identity, or unrelated documentation
path is writable.

## Contracts and Interfaces

1. `AccountableHistoryRequestV1` reuses the exact provenance v1 tagged root and
   admits no learner, purpose, role, tenant, permission, policy, requested field,
   output format, or arbitrary owner selector.
2. `AccountableHistoryDocumentV1` identifies schema version `1.0.0`, the exact
   root, one server-selected closed purpose, an overall state, reviewed summary,
   bounded ordered entries and links, incomplete facts, safe diagnostics,
   redaction summaries, the source lineage digest, and its own digest.
3. Each history entry carries sequence, stable safe reference, closed role,
   reviewed display label/explanation, and the bounded exact technical owner,
   kind, stable ID, applicable version or occurrence, integrity digest, recorded
   time, and validation state. It never carries the owned payload.
4. Transformation links use existing closed provenance relations and correlate
   exact disclosed entry references. Missing links similarly correlate a
   declared source and safe target reference; no fabricated entry is allowed.
5. Overall `invalid` documents disclose only safe diagnostics and already safe
   identities. Raw rejected values, payload fragments, exception text, paths,
   queries, credentials, active content, or secret-like unknown fields fail.
6. `PortableEvidenceExportV1` wraps one `portable_evidence` document, a stable
   media type and filename stem, an export time derived from the document's
   source facts rather than the runtime clock, and the exact canonical document
   digest. No storage locator or download identity appears.
7. Canonicalization normalizes aware times to UTC `Z`, orders semantic arrays
   deterministically, and hashes the full disclosed document without its own
   digest. Equivalent input order yields identical bytes; changed meaning does
   not. The runner imports no product module, framework, database, filesystem
   outside the named contracts, network, provider, model, Identity, or clock.

## Dependencies and Parallel Safety

The packet depends on completed SLI-0106 and SLI-0107 semantics but has no prior
SLI-0108 packet dependency. It owns the external meaning consumed by WRK-0190.
It is not parallel-safe with another SLI-0108 packet because the pure core,
operations, client, and browser must consume the frozen contract and the
planning/architecture files overlap.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Lesson review | A complete approved lesson lineage | The inspection document validates | Reviewed plain language and exact technical source/publish facts round-trip without lesson content | schema/corpus |
| Completion review | A completion lineage with Assessment and Audit entries | The document validates | Completion, evidence, transformation, and integrity facts remain exact without answer, score detail, feedback, or learner identity | schema/corpus |
| Portable export | One disclosed document is wrapped twice | Canonicalization runs | Canonical document bytes, filename stem, media type, and digest are deterministic with no storage reference | vector/property |
| Purpose isolation | A request or document supplies an arbitrary purpose or mixes learner-review and portable-evidence rules | Validation runs | The document fails with one bounded diagnostic | schema/semantic |
| Explicit gap | One declared source is incomplete or unavailable | The inspection validates | The exact gap and safe status remain visible; no owner payload or invented replacement appears | schema/corpus |
| Safe integrity diagnostic | A fixture represents an integrity mismatch or identity conflict | Validation runs | Only the closed code/reference/reviewed explanation is exposed, with no rejected digest or raw input | security/semantic |
| Purpose redaction | Protected/private/provider/internal/storage categories are withheld | The document validates | Only closed category counts remain, and count/order variation within bounds is accepted | corpus/property |
| Equivalent input order | Valid entries, links, diagnostics, or redactions arrive in another order | Canonicalization runs | Canonical public order and digest are identical | vector/property |
| Unsafe/private input | Learner/tenant/actor data, payload, answer, body, score detail, feedback, provider material, secret, path, URL, stack trace, or unknown key appears | Validation runs | The whole document fails before raw content or a partial value is returned | schema/security |
| Provenance stability | Existing v1/v2 schemas and approved corpus remain present | Accountable-history conformance runs | Recorded fingerprints remain unchanged and existing suites still pass | compatibility/regression |
| Layer isolation | The runner imports are inspected | Architecture checks run | No product, framework, persistence, provider/model, Identity, host, Web, or foreign owner implementation is imported | architecture |

## Verification Commands

- `backend\.venv\Scripts\python.exe -m pytest backend/tests/contract/accountable_history backend/tests/contract/provenance backend/tests/contract/provenance_v2 -q`
- `python backend/tests/architecture/test_module_boundaries.py`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Run the tracked affected-check plan and exact-candidate verification after the
candidate is frozen, followed by an independent technical disposition. API,
generated-client, PostgreSQL, browser, Docker, and live-host checks are not
routine for this pure contract packet.

## Documentation and Evidence Update

Record exact purpose/state/role/relation/diagnostic/redaction catalogs, bounds,
display and technical facts, canonicalization/export rules, compatibility
fixtures and fingerprints, focused and affected checks, candidate/receipt,
technical disposition, migration/rollback impact, residual gaps, and CAP/slice
conformance. Approval and reviewer records remain only in ignored local state.

## Stop Conditions

Stop for conflicting owner or disclosure authority; stale CAP authority; a
provenance v1/v2 reinterpretation; a new root or live cross-domain graph;
caller-defined purpose/redaction; copied owner payload; new persistence;
organization/tenant/admin/instructor/support access; managed retention, legal/
commercial, encryption/signing, recovery, immutable-storage, provider/model,
financial/external-action, or public-disclosure choice; a scope collision; or
material CAP/SLI drift.

Do not stop or reopen review solely for harmless whitespace, optional prose,
valid fixture count/order, nonfunctional styling, or another inconsequential
issue. Fix bounded documentation locally or defer polish to CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0108.WRK-0189`; exact candidate and qualifying receipt;
contract catalogs, approved/denial corpus and vectors; safe diagnostic and
redaction semantics; deterministic/anti-rigidity and provenance-stability
results; architecture/security isolation; documentation impact; migration and
rollback status; assumptions; residual gaps; CAP conformance; and unresolved
decisions. Confirm no production core, persistence, API/client, UI, identity,
provider/model, tenant/admin, external action, or financial authority changed.

## Completion Evidence

- Exact candidate: `b91e40a48afc68452fc6be31b8aa51926d0d58bb`.
- Qualifying receipt:
  `sha256:45641be538488db2c46f5e8e7c2a0b59f123984c8e428e5589b1823e94c2eb83`.
- The accountable-history, provenance v1/v2, Guidance contract/unit, and module-
  boundary affected suite passed 190 tests. Architecture passed 18 checks,
  security passed 10 control groups, and documentation, planning, whitespace,
  and all 30 aggregate-readiness checks passed.
- Contract evidence covers closed purpose/root/state-correlated display text,
  owner-to-resource correlation, incomplete versus invalid diagnostics,
  Unicode-total deterministic export names, instant-based timestamp ordering,
  safe redaction and diagnostic behavior, and unchanged provenance v1/v2
  fingerprints. The final focused contract review passed 83 tests.
- No production core, persistence, migration, API/client, UI, identity,
  provider/model, tenant/administrator, external-action, or financial-authority
  behavior changed. Rollback removes only the additive contract and corpus
  before adoption; later packets consume but do not reinterpret this meaning.

## Planning History

- 2026-10-18: Authored just in time after SLI-0108 refinement. The packet
  freezes one additive inspection/export contract and compatibility seam and
  leaves pure composition, authorization/API, generated-client UI, and live
  qualification to dependent packets without adding a lower-level approval.
- 2026-10-18: Activated from clean base `dd3cb71` after the implementation gate
  confirmed current CAP authority, parent/dependency readiness, resolved
  decisions, exact write scope, and no active ownership collision.
- 2026-10-18: Submitted exact candidate `b7eae65` after 182 focused
  accountable-history, unchanged-provenance, Guidance contract/unit, and
  module-boundary tests passed together with architecture, security,
  documentation, planning, whitespace, and all 30 readiness checks.
- 2026-10-18: Completed at exact candidate `b91e40a` after bounded corrections
  correlated owner and resource meaning, validation state and diagnostics,
  deterministic Unicode-safe export identity, exact timestamp order, and
  reviewed display text with purpose/root/state. All qualifying gates are
  current and the dependent pure-core packet may start.
