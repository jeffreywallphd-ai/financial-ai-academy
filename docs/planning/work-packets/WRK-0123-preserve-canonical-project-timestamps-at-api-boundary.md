---
id: WRK-0123
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-17
parent: SLI-0031
capability: CAP-0007
depends_on: [WRK-0122]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/hosts/api/models.py", "backend/tests/integration/api/test_single_profile_project_api.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0031-save-project-work-and-close-a-snapshot.md", "docs/planning/work-packets/WRK-0121-qualify-project-workspace-snapshot-flow.md", "docs/planning/work-packets/WRK-0123-preserve-canonical-project-timestamps-at-api-boundary.md"]
generated_artifacts: []
base_revision: ff2423ea38ca4d871d716bb73d72a84f2d6d34ac
claim_id: WRK-0123:86c273ff-4ba6-4f79-8e59-f20c091fb7f3
claimed_by: codex-cap-0007
claimed_at: 2026-10-17T02:24:40Z
---

# Agent Work Packet: Preserve Canonical Project Timestamps at the API Boundary

## Objective and Deliverable

Remove the Project export-integrity failure exposed by the resumed live
qualifier. Preserve the Project contract's canonical UTC timestamp spelling
when FastAPI serializes Project response models, cover fractional seconds that
end in zero, and return WRK-0121 to qualification without changing the public
schema, digest algorithm, stored time, or authority.

## Required Context

Before editing, follow `AGENTS.md` and `docs/README.md`; route through the
Project, API/security, architecture, and testing-quality context packs; apply
the change-impact matrix and decision-readiness register; inspect CAP-0007,
SLI-0031, WRK-0118 through WRK-0122, the Project contracts and service,
`ContractProjectAdapter`, all Project API response models and converters, the
Project integration tests, OpenAPI snapshot, generated client, browser export
verification, and nearest READMEs.

## Decisions and Assumptions

- Accepted Project timestamp, snapshot, export, API-first, and generated-client
  decisions remain sufficient. No durable decision or new human approval is
  required.
- The Project contract adapter is the canonical timestamp authority. HTTP
  serialization must not expand a contract string such as `.84748Z` into
  `.847480Z` after the server has computed a digest over the canonical form.
- The observed failure is deterministic: the API response preserves the same
  instant but changes its JSON spelling, so a headless or browser client
  correctly recomputes a different export digest.
- This is a functional evidence-integrity correction, not optional copy,
  whitespace, or styling.

## In Scope

- Apply one Project-specific response-serialization policy to every Project
  response timestamp that can participate in public records, nested snapshot
  material, or export digest material.
- Preserve UTC `Z`, omit fractional seconds when zero, and trim only trailing
  fractional zeroes while retaining the exact instant and accepted precision.
- Add deterministic API-model and public-response regressions for zero,
  trimmed, and full fractional precision, including nested export material and
  client-side digest recomputation.
- Prove that naive or otherwise invalid timestamp input remains rejected and
  that no global or non-Project API serialization behavior changes.
- Verify that the reviewed OpenAPI snapshot and generated TypeScript client are
  unchanged. WRK-0121 owns the resumed live qualifier.

## Out of Scope

Any schema or generated-client change; digest relaxation or new algorithm;
database, migration, contract, domain, application-service, browser, or
non-Project timestamp behavior; stored precision loss; compatibility bypass;
identity, tenancy, provider, Portfolio, Assessment, learner-model, financial
action, AI authority, external execution, managed-cloud, recovery, styling, or
remote-push change.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Project API models | all Project response models and converters | `models.py` only | Preserve the already accepted canonical timestamp spelling at JSON serialization |
| Regression | current Project API integration coverage | named Project API test | Reproduce trailing-zero expansion and prove export-digest parity |
| Planning | SLI-0031, WRK-0121, this packet, register | named planning files | Record the bounded correction and return to qualification |
| Contracts/client/storage/UI | affected sources and consumers | none | Exact public shapes, storage, and authority remain frozen |

## Contracts and Interfaces

No external field, type, endpoint, validation, or digest meaning changes.
Project response timestamps remain RFC 3339 UTC `date-time` strings. The fix
ensures JSON uses the same canonical spelling already emitted and validated by
the Project contract. OpenAPI remains unchanged, and the generated client
continues to expose strings.

## Dependencies and Parallel Safety

WRK-0122 corrected application-side snapshot material and supplies the
canonical source. WRK-0123 is the bounded transport correction prerequisite
for WRK-0121. It is not parallel-safe with WRK-0121 because both reconcile
SLI-0031 planning state, so WRK-0121 remains released until this packet is
complete.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Trailing-zero transport | an accepted Project timestamp has nonzero microseconds ending in zero | FastAPI serializes a Project response | JSON retains the contract's trimmed canonical spelling | deterministic API-model/public-response regression |
| Export integrity | a checkpoint/export contains nested timestamps and a server digest | a browser or headless client hashes the public JSON material | the recomputed SHA-256 digest equals `export_digest` exactly | Project API integration regression |
| Precision flexibility | valid UTC times have zero, trimmed, or full fractional precision | response models serialize them | each uses one canonical form without rejecting a valid instant | parameterized anti-rigidity regression |
| Invalid time safety | a naive or noncanonical input reaches contract validation | the normal Project boundary evaluates it | existing validation still fails closed | focused negative test |
| Schema preservation | the Project-only serialization policy is applied | OpenAPI and client checks run | no reviewed schema or generated-client diff appears | OpenAPI/client verification |
| Boundary containment | the correction is inspected | non-Project models and application/storage code are compared | only Project response JSON spelling is affected | architecture and diff review |

## Verification Commands

Run packet validation and planning integrity; focused Project API integration
tests including nested export digest parity; affected Project contract and
application tests; reviewed OpenAPI snapshot and generated-client reproduction;
Python compile/lint/format checks available in the repository; Git whitespace,
documentation, architecture, security, exact-candidate, aggregate readiness,
and independent technical review. After completion, resume WRK-0121 and run its
isolated PostgreSQL/API/Chromium/restart qualifier.

## Documentation and Evidence Update

Record the exact expanded timestamp, the server and client digest values, the
Project-only serialization seam, regression results, candidate receipt, and
review outcome in this packet, the SLI history, and the register. Do not claim
a schema, stored-time, algorithm, or authority change. Assurance documents
remain owned by WRK-0121 unless the correction changes an existing claim.

## Stop Conditions

Stop for a required contract/schema/client/migration change; evidence that the
contract canonicalizer is inconsistent; stored precision loss; digest bypass;
global datetime serialization changes; unrelated Project behavior; active
write collision; unresolved identity, tenancy, provider, recovery, legal,
commercial, model-authority, or external-execution choice; or material
CAP-0007 drift.

Do not reopen review for formatting-only corrections inside the named files.

## Required Handoff

Report `CAP-0007.SLI-0031.WRK-0123`; exact root cause and timestamp; changed
serialization boundary; digest-parity regression; OpenAPI/client result;
focused and cumulative checks; candidate receipt and independent review;
documentation impact; and confirmation that no contract, storage, browser,
provider, Assessment, learner-model, financial, or AI authority changed. Then
return to WRK-0121.

## Planning History

- 2026-10-17: Authored after WRK-0121's live export check showed that FastAPI
  serialized the canonical contract value `2026-10-17T02:18:48.84748Z` as
  `2026-10-17T02:18:48.847480Z`. The two strings denote the same instant, but
  the response no longer matched the exact JSON used for the server export
  digest. The packet is limited to Project response serialization and a
  deterministic transport regression.
- 2026-10-17: Activated from clean base `ff2423e` after the implementation gate
  confirmed current CAP authority, completed dependencies, bounded Project-only
  response scope, and no lower-level approval requirement.
- 2026-10-17: Submitted exact candidate `b985db7`. A Project-specific Pydantic
  response base now applies the contract's UTC timestamp spelling at JSON
  serialization only. Deterministic nested-export and live HTTP regressions
  cover zero, trimmed, and full fractional precision, exact digest parity,
  naive-time denial, and the unchanged reviewed OpenAPI snapshot. The affected
  Project suite passed 141 tests with 10 environment-specific skips; focused
  HTTP verification passed 8 tests with one PostgreSQL skip; architecture and
  all 10 security control groups passed.
