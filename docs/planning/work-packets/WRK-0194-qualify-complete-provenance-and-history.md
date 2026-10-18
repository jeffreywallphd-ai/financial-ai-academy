---
id: WRK-0194
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0109
capability: CAP-0026
depends_on: [WRK-0183, WRK-0188, WRK-0193]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/audit/README.md", "backend/tests/contract/provenance/test_capability_qualification.py", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/planning/capabilities/CAP-0026-preserve-provenance-and-accountable-history.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0109-qualify-complete-provenance-and-history.md", "docs/planning/work-packets/WRK-0194-qualify-complete-provenance-and-history.md", "tests/architecture/test_approved_lesson_boundaries.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: []
base_revision: 3abfab41aa499998ef635e8977fa2049f5b6b941
claim_id: WRK-0194:8e61115a-f474-4360-8676-5298b7b730aa
claimed_by: codex-cap-0026
claimed_at: 2026-10-18T11:50:56Z
---

# Agent Work Packet: Qualify Complete Provenance and History

## Objective and Deliverable

Add only the missing cumulative qualification evidence for the complete
CAP-0026 provenance and accountable-history boundary, prove the policy-neutral
retention and deployment seams without selecting a managed policy, rerun the
existing browser/headless/live evidence, and close SLI-0109 and CAP-0026 on one
exact reviewed candidate.

## Required Context

Before changing a repository file, read and follow every applicable
`AGENTS.md`, repository-root `docs/README.md`, routed context, change-impact
matrix, decision-readiness register, planning guide/register, CAP-0026,
SLI-0106 through SLI-0109, WRK-0183/WRK-0188/WRK-0193, the provenance and
accountable-history executable schemas and compatibility corpora, Audit public
surface and contributor README, architecture/deployment-parity contracts,
generated clients, cumulative browser/headless runner, and affected tests.

## Decisions and Assumptions

- The CAP package approval is current; SLI-0109 is in its manifest; all three
  dependency slices and packets are complete; and no local shared-core decision
  gate is unresolved.
- Existing v1/v2/history contracts and public operations are product authority.
  Qualification cannot weaken their exact identities, bounds, canonicalization,
  authorization, redaction, diagnostics, or owner boundaries.
- Retention is qualified as separation: owner records keep owner lifecycle,
  Audit stores bounded integrity/accountability references, and export is an
  unretained response. A retention duration, deletion/legal-hold rule, tenant
  policy, scheduler, or immutable store is neither needed nor authorized.
- Local qualification can prove adapter-neutral shared-core semantics but
  cannot claim managed-cloud infrastructure, tenant isolation, recovery, or
  provider operation.
- Existing focused and live evidence is reused. The packet adds one small
  cumulative contract test only where the full CAP seam is otherwise implicit.

## In Scope

1. Add a cumulative contract qualification that binds the accepted v1/v2 and
   accountable-history families, their public-safe bounds, and their retention
   separation without duplicating owner payloads or assigning policy meaning to
   provenance identity.
2. Prove that history/export public schemas reject retained-file, locator,
   lifecycle-policy, tenant, provider, and private owner fields and that the
   shared pure core remains free of host, database, cloud, provider, and
   filesystem dependencies.
3. Reuse existing property, integration, conformance, API/generated-client,
   browser, restart, containment, projection-rebuild, conflict, redaction,
   accessibility, and cleanup suites as cumulative acceptance evidence.
4. Correct only a bounded functional or evidence defect found inside the
   declared scope. Do not add a new product contract merely to satisfy a prose
   checklist.
5. Reconcile Audit, provenance, architecture-verification, packet, slice, CAP,
   and planning-register completion evidence with exact candidate and receipt.

## Out of Scope

- New product code, schema versions, migrations, tables, public routes,
  generated clients, owner adapters, profiles, browser features, provider/model
  operations, financial calculations, or external actions.
- Retention periods, deletion, legal holds, tenant/admin policy, public hosting,
  cloud providers, encryption/signing keys, recovery objectives, immutable
  infrastructure, compliance claims, or managed-cloud qualification.
- Treating synthetic v2 forecasts as production integrations, adding a dynamic
  registry, copying owner records into Audit, or manufacturing a universal
  provenance aggregate.
- Incidental formatting, fixture-count, test-order, snapshot, microbenchmark,
  or nonfunctional styling work.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Frozen contracts and compatibility | provenance v1/v2 and accountable-history schemas, runners, approved and denial corpora | no | remain exact qualification inputs |
| Audit shared core and public surface | domain, application, ports, adapters, API composition | no | verify rather than rewrite accepted behavior |
| Cumulative contract evidence | focused contract, integration, conformance, replay, API, browser, and architecture tests | one dedicated cumulative qualification file; bounded assertion corrections only in the two named shared test files | make CAP-wide separation and portability observable without product change |
| Contributor/architecture guidance | Audit README, provenance contract, architecture verification | yes | record the exact retention and deployment seam proved |
| Planning | CAP-0026, SLI-0109, WRK-0194, register | yes | record deterministic delivery and closure |

No production behavior, generated artifact, dependency, migration, contract
fixture, external resource, or unrelated documentation path is writable.

## Contracts and Interfaces

1. Provenance v1 remains the closed learning graph; v2 remains the additive
   closed owner-reference family; accountable-history remains a purpose-limited
   authorized read/export model over v1. None imports or rewrites another
   owner's business payload.
2. Exact replay converges. Reuse of an exact identity with changed meaning is a
   conflict, not an overwrite. Projection rebuild reproduces source-set and
   canonical view identity from owner facts.
3. Contract limits are semantic safety bounds. Qualification exercises valid
   varied and maximum-supported shapes plus over-limit denials without relying
   on fixed fixture counts or wall-clock thresholds.
4. Accountable-history export is a value returned by the public operation. It
   contains no retained-export identity, path, locator, tenant, provider,
   deletion time, legal policy, or storage instruction.
5. Future deployment and retention adapters may preserve these contracts but
   cannot insert their policy into provenance identity or claim cloud parity
   from the local evidence.
6. Browser and headless clients consume the same reviewed API. The browser may
   organize or progressively disclose content but adds no permission, policy,
   history, or provenance meaning.

## Dependencies and Parallel Safety

WRK-0183 supplies complete live learning-lineage qualification, WRK-0188
supplies mixed real/synthetic cross-domain conformance, and WRK-0193 supplies
complete protected accountable-history browser/headless qualification. All are
complete. This packet touches shared cumulative tests, architecture guidance,
and CAP planning files, so it is not parallel-safe with another writer on those
paths. Claim it once from a clean base and acquire one exclusive file lease over
the declared scope.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Frozen-family compatibility | All three accepted contract families and their compatibility corpora | Cumulative qualification runs | v1, v2, and history meanings and fingerprints remain exact | contract runners/cumulative test |
| Exact replay and rebuild | Accepted owner facts and one disposable Audit projection | Reconciliation repeats and the projection is rebuilt | Source-set, retained reference, public graph, history, and digest identities remain exact | unit/PostgreSQL/live replay |
| Tamper and conflict containment | One exact identity changes or one link is invalid | Composition or reconciliation runs | A closed conflict/diagnostic appears with no partial publication or unrelated-chain failure | contract/integration/security |
| Bounds and anti-rigidity | Valid values vary through documented zero-to-maximum shapes and one value exceeds a bound | Validators and cores run | Valid shapes remain deterministic; over-limit shapes fail closed without fixture or time assumptions | property/contract |
| Cross-owner isolation | Real Project and synthetic future forecasts run together | Order, partial sets, and one adapter failure vary | Coverage and results remain exact; one profile cannot disable another | v2 conformance |
| Retention separation | The accepted public schemas and operations are inspected and run repeatedly | History/export is requested before and after restart | No retained-export, storage-policy, tenant, provider, or owner-payload field/state is created | cumulative contract/live containment |
| Headless/browser parity | Generated browser and ordinary clients select both root kinds | Lineage/history/export calls run | Server-owned meaning and authorization remain equal and browser policy remains absent | API/Playwright/live |
| Adapter-neutral core | Shared domain/application sources are inspected and exercised | Qualification swaps test inputs/adapters | Canonical behavior has no cloud, host, database, filesystem, or provider dependency | architecture/cumulative test |
| Accessible use | The focused history interface runs under keyboard, reflow, themes, forced colors, and reduced motion | Browser qualification runs | Equivalent content/actions/status/disclosure remain usable | component/Chromium/design |
| Restart and cleanup | The disposable local topology completes or fails | Normal restart and final cleanup run | State rebuilds exactly and only named isolated resources are removed | live/control plane |

## Verification Commands

- `backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/provenance backend/tests/contract/provenance_v2 backend/tests/contract/accountable_history backend/tests/unit/audit backend/tests/integration/audit backend/tests/integration/api/test_single_profile_lineage_api.py backend/tests/integration/api/test_single_profile_accountable_history_api.py backend/tests/architecture/test_module_boundaries.py -q`
- `python tests/e2e/approved-lesson/test_replay_qualification.py`
- focused Web model/component and Playwright accountable-history checks, then
  the complete isolated approved-lesson runner using the repository-prepared
  Node/npm, pinned Chromium, and disposable PostgreSQL composition
- `python tests/architecture/test_approved_lesson_boundaries.py`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/content/check_learner_language.py --changed`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `git diff --check`
- exact-candidate controller affected verification and one independent
  technical review
- `python dev-tools/agent/check_ready.py`

No external or production resource is authorized or claimed. Verification and
review records remain only under ignored local control-plane storage.

## Documentation and Evidence Update

Update the Audit contributor README, provenance contract guide, architecture
verification matrix, WRK-0194, SLI-0109, CAP-0026, and planning register. Record
the exact candidate/receipt; focused and cumulative checks; replay/rebuild,
conflict, bounds, cross-owner isolation, retention separation, headless/browser,
accessibility, restart, containment, cleanup, and portability evidence; migration
status; residual future policy/cloud gaps; and CAP conformance.

## Stop Conditions

Stop for conflicting canonical authority; stale CAP approval; a breaking
contract; new owner/business aggregate, adapter, profile, route, persistence,
migration, browser behavior, or external action; selected retention duration,
deletion/legal-hold/tenant policy, cloud provider, encryption/signing, recovery,
immutable storage, or managed-cloud claim; provider/model execution; direct
cross-module storage; destructive repair; active file collision; or material
CAP-0026/SLI-0109 drift.

Do not stop or reopen broad review solely for harmless whitespace, optional
prose, generated formatting, valid count/order/Unicode variation,
nonfunctional styling, or another inconsequential issue. Fix bounded evidence
or documentation issues locally or defer polish to CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0109.WRK-0194`; exact candidate and qualifying receipt;
frozen compatibility; replay/rebuild/conflict/bounds; cross-owner failure
isolation; policy-neutral retention separation; browser/headless parity;
adapter-neutral shared-core evidence; accessibility, restart, containment, and
cleanup; focused and aggregate checks; documentation and migration impact;
assumptions and residual gaps; CAP conformance; and unresolved decisions.
Confirm no product contract, persistence, provider/model, external action,
tenancy/admin, financial, managed-retention, or managed-cloud behavior changed.

## Planning History

- 2026-10-18: Authored just in time after SLI-0109 refinement and completion of
  all three dependency packets. The packet reuses accepted focused/live evidence
  and adds only one missing cumulative contract qualification before deterministic
  slice and CAP closure. No lower-level approval exists or is required.
- 2026-10-18: Activated from clean base `3abfab4` with one bounded owner after
  revalidating the approved CAP manifest, all dependency packets, local
  decision posture, exact qualification scope, and absence of a write collision.
- 2026-10-18: Implemented the cumulative contract qualification for aligned
  lineage/history/source bounds, closed policy-neutral export and retention
  seams, and deployment-neutral shared-core imports. The 100-test replay suite,
  focused contract and Web suites, TypeScript, zero-warning lint, architecture,
  security, and the complete disposable PostgreSQL/Chromium topology pass. One
  first topology run reached and passed the provenance/history phases before an
  unrelated presentation-preference race failed; an exact clean rerun passed
  the entire topology and bounded cleanup.
- 2026-10-18: Submitted exact implementation candidate `366c7ee` and moved to
  deterministic affected verification. The lifecycle reconciliation below
  changes only tracked planning state and evidence, not product behavior.
- 2026-10-18: Corrected a bounded qualification defect found before packet
  closure. The cumulative portability test now discovers the complete Audit
  shared-core Python surface, resolves relative imports, applies structural
  inward-layer and effect-dependency rules, and no longer scans harmless prose.
- 2026-10-18: Completed the portability closure by adding the three designated
  strict contract-mapping adapters and replacing the incomplete effect denylist
  with an explicit reviewed pure-standard-library allowlist. Host, filesystem,
  network, database, cloud, and external-action imports now fail closed.
