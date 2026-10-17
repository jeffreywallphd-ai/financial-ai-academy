---
id: WRK-0151
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: SLI-0074
capability: CAP-0018
depends_on: [WRK-0148]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/hosts/api/models.py", "backend/tests/integration/api/test_single_profile_learner_preferences_api.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0074-record-learning-goals-experience-interests.md", "docs/planning/work-packets/WRK-0150-qualify-learning-preferences-live-flow.md", "docs/planning/work-packets/WRK-0151-preserve-learner-preference-canonical-timestamps.md"]
generated_artifacts: []
base_revision: 95b0afa6804669a63a7c74dfc78fb11555a64449
claim_id: WRK-0151:7df35f8d-b516-40e6-b1ea-13811a6a9087
claimed_by: codex-cap-0018
claimed_at: 2026-10-17T19:59:49Z
---

# Agent Work Packet: Preserve Learner Preference Canonical Timestamps

## Objective and Deliverable

Correct the learner-preference API response projection so every timestamp keeps
the exact canonical text used by the already accepted profile digest. Add a
regression that proves a nonzero microsecond ending in zero is not shortened in
profile, nested item, history, or export JSON. Resume WRK-0150 only after the
public response validates against its existing digest.

## Required Context

Follow `AGENTS.md`, `docs/README.md`, and the repository startup, planning,
concurrency, API, contract, testing,
and decision-readiness guidance. Inspect CAP-0018, SLI-0074, WRK-0147 through
WRK-0150, the routed WRK-0148 correction record, learner-preference canonical
digest rules, API response models, route projections, integration tests,
OpenAPI generation, generated-client reproduction, and nearest READMEs.

## Decisions and Assumptions

- The domain profile and stored digest are authoritative and already use the
  accepted fixed UTC timestamp representation.
- The defect is confined to learner-preference response serialization: a
  generic API serializer removes a trailing fractional zero after the digest
  has been calculated.
- A learner-preference-specific response base is safer than changing timestamp
  text for unrelated Project or Personal-workspace contracts.
- The JSON Schema/OpenAPI type remains `string` with `date-time` format, so no
  public shape, generated client, or migration change is intended.
- This bounded correction is part of the approved SLI-0074 outcome and needs no
  additional lower-level approval.

## In Scope

- Preserve six fractional digits for nonzero learner-preference response
  datetimes and preserve the existing whole-second UTC representation.
- Apply that response behavior to profile, goal, experience, interest, change,
  history, and export response models only.
- Add an API regression that receives an actual FastAPI JSON response, verifies
  the exact canonical timestamp, and recomputes the profile digest from the
  returned document.
- Prove OpenAPI and generated TypeScript client reproduction remain unchanged.
- Record correction and qualification-resumption evidence in this packet,
  SLI-0074, and the planning register.

## Out of Scope

Domain digest rules; stored data; schemas or migrations; request models;
unrelated API timestamp conventions; OpenAPI shape; generated-client behavior;
browser behavior; new dependencies; identity, tenancy, provider, model,
recovery, licensing, legal, commercial, or external-execution decisions.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| API projection | shared and learner-preference response models | `models.py` | Preserve digest-covered timestamp text without affecting unrelated contracts |
| API evidence | existing protected learner-preference routes | focused integration test | Reproduce the exact trailing-zero case through FastAPI JSON |
| Planning | SLI-0074, packet, register | named planning files | Keep the bounded correction and resume path explicit |

## Dependencies and Parallel Safety

WRK-0148 supplied the affected API projection. WRK-0150 discovered the defect
and pauses product qualification until this correction passes. WRK-0151 owns
its two product/test files and shared SLI planning files, so no parallel writer
may edit them.

## Contracts and Interfaces

The existing learner-preference profile, history, and export contracts remain
unchanged. Their canonical digest covers compact sorted-key UTF-8 JSON with the
document digest omitted, including the exact UTC timestamp strings. The API
must serialize those response timestamps without changing their canonical
text. OpenAPI continues to expose the same date-time strings, and browser and
headless clients continue to use the same protected operations.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Trailing-zero profile time | canonical `...007590Z` profile data and digest | the protected API serializes it | JSON retains `...007590Z` and its recomputed digest matches | API integration |
| Nested/history/export time | canonical item and change timestamps | response models serialize them | all nonzero fractions retain six digits | focused model/API assertions |
| Whole-second stability | a UTC timestamp with zero microseconds | response serialization runs | existing `...:00Z` representation remains | regression |
| Contract stability | the correction candidate | OpenAPI and generated client are reproduced | no reviewed API shape or client diff appears | reproduction checks |
| Scope containment | affected verification runs | changed paths and tests are inspected | no domain, persistence, browser, dependency, or unrelated timestamp behavior changes | diff/check evidence |

## Verification Commands

Run the focused learner-preference API integration test, relevant API model and
learner-preference contract tests, OpenAPI and generated-client reproduction,
Python compilation, architecture/security/documentation/planning/whitespace
checks, affected verification, proportionate independent technical review, and
`python dev-tools/agent/check_ready.py`. Resume the full WRK-0150 live
qualification after this packet completes.

## Documentation and Evidence Update

Record the exact failing and corrected timestamp text, successful digest
recalculation, focused test result, unchanged OpenAPI/client reproduction,
affected checks, and WRK-0150 resumption. Do not add approval or reviewer
identity to tracked files; those records remain in the ignored local ledger.

## Stop Conditions

Stop for a required digest/schema/migration/generated-client change; evidence
that stored canonical data is corrupt; an incompatible change to unrelated API
contracts; private-data leakage; unresolved decision; active file collision;
or material CAP-0018/SLI-0074 drift. Do not create a review loop for harmless
formatting or another inconsequential in-scope correction.

## Required Handoff

Report `CAP-0018.SLI-0074.WRK-0151`, the reproduced defect, exact correction,
focused and reproduction checks, changed files, unchanged boundaries, and the
WRK-0150 resume result.

## Completion Evidence

- Live WRK-0150 qualification reproduced an accepted stored profile whose
  canonical `2026-10-17T19:57:15.007590Z` timestamp had been shortened by the
  API to `2026-10-17T19:57:15.00759Z` after its digest was calculated. The
  browser correctly rejected that internally inconsistent response.
- Learner-preference response models now preserve all six fractional digits
  whenever microseconds are nonzero, while retaining the existing whole-second
  UTC form. The shared Project timestamp serializer is unchanged.
- The focused FastAPI suite passes 20 tests. Its new regression exercises
  profile, nested goal, history, and export JSON, then removes the returned
  digest and independently recalculates the canonical profile digest.
- The learner-preference contract, parser, domain, and application matrix
  passes 67 tests. Reviewed OpenAPI is current, generated TypeScript client
  reproduction passes, and web typecheck plus zero-warning lint pass.
- Architecture passes 17 checks after directing temporary files to the bounded
  workspace path; security passes 10 control groups. Documentation, packet,
  planning, whitespace, Python compilation, and all 29 aggregate readiness
  checks pass.
- The restricted Windows sandbox could not create TestClient loopback event-
  loop sockets, so the focused API suite was rerun outside that restriction.
  This was an environment constraint, not a product failure.
- No schema, migration, stored value, domain digest, OpenAPI shape, generated
  client, browser behavior, dependency, identity, provider, model, or unrelated
  API timestamp contract changed. WRK-0150 remains paused at `ready` until this
  bounded correction is accepted and then resumes from its preserved work.

## Planning History

- 2026-10-17: Authored just in time after WRK-0150 reproduced a valid stored
  profile whose API timestamp was shortened after digest calculation. The
  WRK-0148 bounded correction route was recorded; no CAP scope or decision
  changed.
