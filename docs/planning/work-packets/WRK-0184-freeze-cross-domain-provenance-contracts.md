---
id: WRK-0184
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0107
capability: CAP-0026
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/guidance/adapters/immutable_corpus.py", "backend/src/financial_ai_academy/modules/guidance/resources/contextual-help/v1/practice-result.json", "backend/src/financial_ai_academy/modules/guidance/resources/contextual-help/v1/project-result.json", "backend/src/financial_ai_academy/modules/guidance/resources/feature-guidance/v1/mappings/lesson-reading-exact-version-unavailable.json", "backend/src/financial_ai_academy/modules/guidance/resources/feature-guidance/v1/records/lesson-version-unavailable.json", "backend/src/financial_ai_academy/modules/guidance/resources/platform-help/v1/data-meaning.json", "backend/tests/contract/contextual_help/test_conformance.py", "backend/tests/contract/provenance_v2", "contracts/README.md", "contracts/compatibility/README.md", "contracts/compatibility/contextual-help/v1/approved/context.json", "contracts/compatibility/contextual-help/v1/vectors/canonicalization.json", "contracts/compatibility/provenance/v2", "contracts/provenance/v2", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0107-extend-provenance-across-domain-owners.md", "docs/planning/work-packets/WRK-0184-freeze-cross-domain-provenance-contracts.md"]
generated_artifacts: []
base_revision: e7e5dce89f991bb83b503654f417082adc937a1f
claim_id: WRK-0184:c7303571-d38e-4a94-af5b-83b26059ef1d
claimed_by: codex-cap-0026
claimed_at: 2026-10-18T09:00:39Z
---

# Agent Work Packet: Freeze Cross-Domain Provenance Contracts

## Objective and Deliverable

Freeze an additive, language-neutral `provenance/v2` owner-reference contract
family that later domain adapters can implement without changing the closed
learning-lineage v1 meaning. Deliver executable Draft 2020-12 schemas, a closed
profile catalog, approved and denial compatibility fixtures, deterministic
canonicalization vectors, a dependency-light schema conformance runner, and
canonical ownership documentation.

The packet must leave one coherent contract-only result. It does not change the
Audit shared core, add an owner adapter, compose a lineage graph, persist data,
or expose a public operation. Those seams remain WRK-0185 through WRK-0188.

## Required Context

Before this planning edit, the repository `AGENTS.md` and `docs/README.md`
Required Startup was completed and reported. The review covered context routing,
change impact, decision readiness, delivery planning, CAP-0026, SLI-0107,
provenance v1 schemas/core/consumers/tests, Audit and Project boundaries,
Project public snapshot meaning, future Market-data/Portfolio/Adaptation/AI
ownership, finance and AI constraints, contracts, tests, and nearest READMEs.

Before any implementation file changes, repeat and report the applicable
`AGENTS.md` and repository-root `docs/README.md` startup gate. Revalidate the
current CAP package and parent slice, then inspect the v1 schemas and
compatibility corpus, contract catalogs, the provenance contract guide, module
map, Project snapshot contract, existing conformance runner/tests, and every
consumer or check affected by a new provenance contract directory.

## Decisions and Assumptions

- CAP-0026 authority is current, SLI-0107 is in its exact manifest, SLI-0106 is
  complete, and no unresolved decision applies to a pure additive local contract
  or synthetic compatibility corpus.
- `provenance-envelope/v1` remains closed to learning roots. The cross-domain
  family uses schema version `2.0.0`; no v1 schema, fixture, canonical bytes,
  request, response, adapter, or meaning changes.
- The v2 catalog is closed to nine profiles: `project_snapshot`,
  `market_observation`, `financial_result`, `dataset_snapshot`, `model_version`,
  `model_execution`, `simulation_result`, `recommendation_record`, and
  `administrative_action`.
- Closed owner/profile pairs are Project/project snapshot; Market data/market
  observation; Portfolio/financial result and simulation result; AI
  orchestration/dataset snapshot, model version, and model execution;
  Adaptation/recommendation record; and Audit/administrative action.
- Fixtures for all profiles except Project are synthetic contract evidence.
  They do not claim an implemented owner, approved provider, model, dataset,
  calculation, recommendation policy, tenant policy, or administrative action.
- Identity is a closed profile-discriminated union rather than a generic bag of
  optional fields. Common meaning includes exact resource ID and integrity,
  aware recorded time, origin label, validation status, producer, and bounded
  typed source references. Profile-specific identity is fixed below.
- Canonicalization is compact sorted-key UTF-8 JSON with unescaped Unicode and
  UTC `Z` time projection. Canonical vectors bind meaning, not incidental file
  formatting or array input order where the contract declares order irrelevant.

## In Scope

- Add `contracts/provenance/v2` documentation and schemas for one owner-reference
  envelope, its closed profile catalog, exact profile identity variants,
  producer, validation, origin label, typed source relation, size bounds, and
  safe common scalar formats.
- Define the exact profile identities:
  - Project snapshot: project ID, snapshot ID, positive project revision, and
    positive workspace revision.
  - Market observation: instrument ID, observation time, method ID/version,
    and source-set digest; its common resource ID is the canonical digest of
    that exact tuple rather than an independent identity field.
  - Financial result: an explicit `subject_kind` discriminator plus either an
    account ID or analysis ID, as-of time, method ID/version, and source-set
    digest.
  - Dataset snapshot: dataset ID and immutable dataset version.
  - Model version: model ID and immutable model version.
  - Model execution: execution ID, model ID/version, and positive occurrence.
  - Simulation result: simulation ID, method ID/version, as-of time, and
    positive occurrence.
  - Recommendation record: recommendation ID, policy ID/version, decision time,
    and positive occurrence.
  - Administrative action: action ID, policy ID/version, recorded time, and
    positive occurrence; it carries no actor identity or authorization claim.
- Close origin labels to `observed`, `calculated`, `simulated`, `predicted`,
  `generated`, and `administrative`, then constrain allowed labels per profile.
- Close source relations to descriptive evidence links suitable for the
  profiles, including `derived_from`, `calculated_from`, `used_dataset`,
  `used_model`, `executed_as`, `simulated_from`, `recommended_from`,
  `governed_by`, and `recorded_as`. Relations grant no causal, permission,
  suitability, compliance, or quality conclusion.
- Add approved fixtures for every profile, including valid Unicode and varied
  source counts/order, plus denial cases for unknown profiles/owners/labels,
  mismatched owner-profile and label-profile pairs, ambiguous identity, bad
  digests/times/versions, private/provider/path/URL/payload fields, duplicate
  conflicts, and exceeded bounds.
- Add a dependency-light test runner that validates Draft 2020-12 shape,
  profile semantics, canonical ordering/digest vectors, bounded diagnostics,
  v1 immutability fingerprints, and corpus completeness without importing
  product adapters or implementation modules.
- Update contract catalogs and canonical architecture/ownership/verification
  documentation for the exact additive boundary.
- Reconcile only the exact immutable Guidance source fingerprints that bind the
  changed canonical contract-architecture file. This mechanical derived update
  includes the directly bound digest vector/assertion and changes no Help text,
  topic identity, mapping, feature state, or authority.

## Out of Scope

- Audit domain/application/adapter changes, a Project provenance adapter, or
  any production Python behavior beyond the exact Guidance source-fingerprint
  reconciliation required by the canonical documentation change.
- Lineage request/view v2, graph composition, persistence, migrations, API,
  OpenAPI, generated client, browser interface, export, or retention control.
- Live owner records for Market data, Portfolio, Adaptation, AI orchestration,
  model, dataset, recommendation, simulation, or administrative profiles.
- Provider calls or payloads, licensed data, instrument normalization,
  financial calculations, advice, model training/inference, sandbox/job
  execution, tenant/organization/actor identity, administrator authorization,
  notification, or external action.
- Dynamic profile registration, arbitrary owners/kinds/relations, copied domain
  payloads, cross-module table access, active content, storage locators,
  credentials, or secret-bearing fields.
- Unrelated refactoring, dependency changes, UI styling, or cleanup.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | provenance v1 schemas, other versioned contract conventions | new `contracts/provenance/v2` schemas and README; top-level catalog sentence | freeze portable additive shape |
| Compatibility | provenance v1 corpus and compatibility conventions | new v2 approved/denial/vector corpus and compatibility README/catalog | bind exact accepted and rejected meaning |
| Contract qualification | existing provenance runner/tests | new isolated `backend/tests/contract/provenance_v2` runner/tests only | execute schema/profile/canonicalization/v1-stability evidence without product imports |
| Derived Guidance binding | immutable corpus adapter, bound topic/context/feature records, focused quality gate | only the exact contract-architecture digest constants in the listed files | keep canonical-source integrity synchronized without changing Help meaning |
| Derived compatibility evidence | contextual-help canonical vector and its exact focused assertion | only the expected digest derived from the changed source binding | keep the existing contract test synchronized with the same record bytes |
| Architecture | provenance contract, contract architecture, module map, verification map | exact v2 ownership/non-authority/verification sections | state boundary and maturity honestly |
| Planning | SLI-0107, this packet, register | lifecycle and evidence sections only | maintain governed state |

No production backend module, public API/client, persistence/migration, Web,
deployment, dependency, provider, or unrelated documentation path is writable.

## Contracts and Interfaces

1. `OwnerReferenceEnvelopeV2` has schema version `2.0.0`, one closed `profile`,
   one exactly matching discriminated `resource`, one producer reference, and
   zero to twenty typed source references. Unknown keys fail closed.
2. Every resource retains its exact closed owner/profile identity, lowercase
   SHA-256 integrity digest, aware recorded time, allowed origin label, and
   `validated` or `incomplete` status. A profile identity admits all and only
   the fields listed under In Scope.
   A financial result selects exactly one account or analysis variant. A market
   observation derives `resource_id` from its canonical exact identity tuple.
3. Identifiers and versions reuse v1 safety intent: bounded Unicode identifiers
   begin alphanumerically and exclude control/format/path/query syntax; versions
   are bounded ASCII tokens; times accept RFC 3339 offsets with at most six
   fractional digits; digests are lowercase SHA-256.
4. Each source names one closed relation and embeds one exact v2 resource
   reference. A source cannot carry owner payload, permission, provider name or
   payload, storage location, actor identity, prompt, dataset rows, model input
   or output, financial values, recommendation prose, or active instructions.
5. Canonical resource identity includes the profile and every profile-specific
   field but excludes input ordering. Equivalent source order projects one
   canonical document and digest; changed same-identity meaning fails.
6. The conformance runner loads only schemas and corpus documents, emits stable
   bounded diagnostics, and exposes no rejected values. It imports no product
   module, framework, database, filesystem outside named contract files,
   network, provider, model, identity, clock, or execution dependency.
7. WRK-0185 may consume the frozen schemas/catalog/corpus to implement pure v2
   values and adapters. It may not reinterpret an accepted fixture in place.

## Dependencies and Parallel Safety

The packet depends on completed SLI-0106 and the accepted v1 contract meaning,
but has no prior SLI-0107 packet dependency. It owns the exact schemas and
compatibility evidence required by WRK-0185. It is not parallel-safe with
another SLI-0107 packet because downstream values, adapters, and conformance
tools must consume this frozen identity/profile contract, and planning and
architecture files overlap.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete closed catalog | One approved document exists for each of the nine profiles | The dependency-light runner validates the corpus | Every document matches its exact owner/profile/label/identity and the catalog has neither gaps nor extras | schema/corpus |
| Project snapshot profile | Exact safe Project snapshot identity facts | The v2 envelope is validated and canonicalized | Project, snapshot, revisions, integrity, producer, and sources are retained without Project content or learner identity | schema/vector |
| Future-owner fixtures | Synthetic financial, dataset, model, execution, simulation, recommendation, and administrative documents | Conformance runs | Contract meaning passes without a product adapter, provider call, model execution, or authority claim | corpus/architecture |
| Equivalent source order | One valid envelope's sources arrive in another order | Canonicalization runs | Canonical bytes and digest are identical | vector/property |
| Valid flexible values | Unicode identifiers, optional source counts, exact times, versions, and occurrences vary within bounds | Validation runs | Values pass without fixed production IDs or fixture-count assumptions | property/anti-rigidity |
| Profile mismatch | Owner, profile, identity fields, or origin label do not form an allowed combination | Validation runs | The document fails with one bounded stable diagnostic | schema/semantic |
| Unsafe/private input | A URL/path, provider payload, actor/learner/tenant ID, prompt, financial values, secret-like field, executable instruction, or unknown key appears | Validation runs | The document fails before raw input or a partial value is exposed | schema/security |
| Changed duplicate | One exact profile identity is repeated with a changed digest or provenance meaning | Corpus validation runs | The conflict is rejected rather than selected or merged | semantic/compatibility |
| v1 stability | Current v1 schemas and approved corpus remain present | v2 conformance runs | Recorded v1 fingerprints are unchanged and the existing v1 suite still passes | compatibility/regression |
| Layer isolation | The new runner imports are inspected | Architecture checks run | No product backend, framework, persistence, provider, model, host, or foreign owner implementation is imported | architecture |

## Verification Commands

- `backend\.venv\Scripts\python.exe -m pytest backend/tests/contract/provenance backend/tests/contract/provenance_v2 -q`
- `python backend/tests/architecture/test_module_boundaries.py`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Run the tracked affected-check plan and exact-candidate verification after the
implementation candidate is frozen, followed by one independent technical
disposition. API, generated-client, PostgreSQL, browser, Docker, and live-host
checks are not routine for this pure contract-only packet.

## Documentation and Evidence Update

Record the exact family/profile/identity/label/relation catalogs, bounds,
canonicalization, v1 compatibility fingerprints, focused and affected checks,
candidate and receipt, technical disposition, rollback/migration impact,
residual gaps, and CAP/slice conformance in this packet and its direct
canonical/catalog sources. Keep all approval and reviewer records only in
ignored local state.

## Stop Conditions

Stop for conflicting owner authority; stale CAP authority; an identity/profile
meaning that cannot be resolved from current canonical sources; a v1 change;
dynamic profiles or relations; copied business payload; a production owner
implementation requirement; cross-module persistence; unresolved provider,
data-license, tenancy/administrator, model, execution, financial-authority,
retention/export, legal/commercial, encryption, queue, or external-action
choice; a write-scope collision; or material CAP/SLI drift.

Do not stop or reopen review solely for harmless whitespace, optional prose,
valid fixture count/order, nonfunctional styling, or another inconsequential
issue. Fix bounded documentation locally or defer polish to CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0107.WRK-0184`; exact candidate and qualifying receipt;
v2 family/profile/identity/label/relation catalogs; approved/denial corpus and
canonical vectors; v1 stability evidence; deterministic and anti-rigidity
results; architecture/security isolation; documentation impact; migration and
rollback status; assumptions; residual gaps; CAP conformance; and any unresolved
decision. Confirm no production module, persistence, public API/client, UI,
provider/model, tenant/admin, external-action, or financial authority changed.

## Completion Evidence

- Exact implementation candidate:
  `77af7bbf1c1b9c1903810008fec5dc1029766a00`.
- Qualifying affected-check receipt:
  `sha256:037b55eb0f43a29ad13223212282430fd0f77240424be5f75404aab02bffd16c`.
- The closed v2 catalog covers all nine profiles. Financial results select one
  explicit account or analysis identity variant, and Market-observation
  resource IDs derive from the canonical exact identity tuple. The reusable
  CLI rejects both missing and extra approved profiles.
- Provenance v1/v2 qualification passed 44 tests. Combined provenance and
  Guidance contract qualification passed 64 tests; architecture passed 18
  tests, security passed ten control groups, and documentation, planning,
  whitespace, and all 30 aggregate-readiness checks passed.
- The v1 schemas and approved-corpus fingerprints remain exact. The v2 runner
  imports no product module, provider, model, persistence, host, or network
  dependency, and diagnostics remain bounded.
- No migration, rollback action, dependency, production owner adapter,
  persistence, public API/client, UI, provider/model, tenant/administrator,
  external-action, or financial-authority behavior changed. Later packets may
  consume this frozen contract but may not reinterpret its accepted fixtures.

## Planning History

- 2026-10-18: Authored just in time after SLI-0107 refinement. The packet
  freezes one additive pure cross-domain reference contract and compatibility
  seam, preserves learning-lineage v1 exactly, and leaves product values,
  conformance adapters, real Project integration, and cumulative qualification
  to dependent packets without adding a lower-level approval.
- 2026-10-18: Activated from clean base `cfc0db4` after the implementation gate
  confirmed current CAP authority, parent/dependency readiness, resolved
  decisions, exact write scope, and no active ownership collision.
- 2026-10-18: Incrementally included the exact immutable Guidance records and
  corpus constant whose contract-architecture fingerprint became stale. This
  is a bounded derived-digest reconciliation only; it changes no Help prose,
  product behavior, packet outcome, or approval posture.
- 2026-10-18: Released and reclaimed the packet from base `e7e5dce` so a new
  packet-start manifest and file leases bind the complete revised scope before
  the derived Guidance fingerprints change.
- 2026-10-18: Added the one contextual-help canonical vector and exact assertion
  exposed by focused verification after the source fingerprint changed. This is
  the same bounded derived reconciliation and does not alter acceptance meaning.
- 2026-10-18: Reclaimed from base `e7e5dce` after that final derived vector/test
  scope was explicit so the replacement packet-start manifest and leases bind
  the complete implementation surface.
- 2026-10-18: Submitted exact candidate `9f54667` after 65 focused contract and
  Guidance tests plus eight subtests, architecture/security/documentation/
  planning gates, whitespace integrity, and all 30 readiness checks passed.
- 2026-10-18: Closed three bounded contract gaps. Financial results now use
  explicit account-or-analysis identity variants, Market resource IDs derive
  from the exact tuple digest, and the CLI rejects missing or extra approved
  profiles. The correction did not expand the packet, product behavior, or
  decision surface.
- 2026-10-18: Completed at exact candidate `77af7bb` after exact-candidate
  qualification, focused contract checks, architecture/security isolation,
  documentation/planning integrity, and aggregate readiness all passed with no
  remaining technical gap in the packet scope.
