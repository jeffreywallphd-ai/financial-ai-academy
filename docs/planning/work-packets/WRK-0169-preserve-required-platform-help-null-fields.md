---
id: WRK-0169
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0020-correction
updated: 2026-10-18
parent: SLI-0082
capability: CAP-0020
depends_on: [WRK-0166]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/hosts/api/app.py", "backend/tests/integration/api/test_single_profile_guidance_api.py", "docs/architecture/contracts/platform-help-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0082-browse-search-approved-help.md", "docs/planning/work-packets/WRK-0168-qualify-platform-help-live-flow.md", "docs/planning/work-packets/WRK-0169-preserve-required-platform-help-null-fields.md"]
generated_artifacts: []
base_revision: 9fbe65f5ed0b47b0176c4850ec2d5cea75c58d3c
claim_id: WRK-0169:6b5c8496-590a-4b3c-9910-812fe90014e8
claimed_by: codex-cap-0020-correction
claimed_at: 2026-10-18T03:34:42Z
---

# Agent Work Packet: Preserve Required Platform Help Null Fields

## Objective and Deliverable

Correct the Platform Help search response so every successful page includes the
contract-required nullable `next_cursor` member, including terminal pages where
its value is `null`. Preserve the existing reviewed OpenAPI shape, deterministic
search/cursor meaning, generated client, browser validation, optional non-null
metadata, and protected read-only API.

## Required Context

Before any file change, read and follow applicable `AGENTS.md` and the
repository-root `docs/README.md`. Revalidate CAP-0020, SLI-0082, completed
WRK-0166 and WRK-0167, paused WRK-0168 live evidence, the platform-help
contract, Guidance/API response models and route, generated schema, browser
validator, nearest tests, change-impact matrix, and decision readiness.

The Required Startup was performed and reported before this planning change.
No durable decision is open. Stop for canonical conflict, stale CAP authority,
active collision, or scope beyond required-null serialization.

## Decisions and Assumptions

- The reviewed OpenAPI model is authoritative: `next_cursor` is required and
  nullable. Omitting it is not equivalent to returning it with `null`.
- FastAPI route-level `response_model_exclude_none=True` currently removes the
  terminal cursor along with absent optional metadata. The correction must
  retain the required nullable cursor while continuing to omit optional
  `topic_kind` or `glossary_term` when they have no value.
- The contract, Guidance core, ranking, cursor encoding, generated client, and
  browser remain unchanged. WRK-0168 resumes only after this packet completes.

## In Scope

- Preserve `next_cursor: null` on terminal search pages through the public API.
- Prove paged responses retain an opaque string cursor and terminal responses
  retain the required member with `null`.
- Prove optional non-null page/result metadata remains absent when unset and
  both terminal and continued HTTP documents satisfy the executable schema.
- Reconcile the platform-help contract note and WRK-0168 dependency state.

## Out of Scope

- Schema, OpenAPI, generated-client, Guidance domain/application/corpus,
  ranking, cursor, identity, authorization, browser, persistence, deployment,
  dependency, provider/model, learner-policy, or financial behavior changes.
- Making arbitrary response fields optional or changing nullability.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| API route | Search response model and route serialization | Platform Help search route only | Preserve required nullable output while omitting absent optional metadata |
| API evidence | Existing Guidance API integration tests | focused terminal/paged response assertions | Prevent omission regression |
| Contract documentation | Current API serialization note | one direct required-null clarification | Keep executable and written contract aligned |
| Planning | WRK-0168, this packet, slice, register | correction dependency and lifecycle | Resume qualification only after correction |

No unlisted file may change.

## Contracts and Interfaces

`PlatformHelpSearchPageResponseModel` and reviewed OpenAPI continue to require:

```json
{ "next_cursor": null }
```

for a terminal page, or a nonempty opaque string for a continued page. Optional
`topic_kind` and result `glossary_term` are non-null when present and remain
absent when unset. The API continues to reject unknown query members and bodies
and to authorize before Guidance access.

## Dependencies and Parallel Safety

WRK-0166 supplied the API and is complete. WRK-0168 found the mismatch during
live browser/headless qualification and is returned to ready with this packet
as a dependency. Shared planning files make the packets non-parallel-safe.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Terminal page | Search has no continuation | Protected API serializes the response | `next_cursor` exists and equals `null` | API integration |
| Continued page | Page size leaves more results | Protected API serializes the response | `next_cursor` exists as a nonempty opaque string | API integration |
| Optional metadata | A non-glossary result and no kind filter are returned | Response is serialized | Unset optional members remain absent and both pages validate against the executable schema | API/contract regression |
| Closed contract | Unknown request member or body is sent | API validates input | Existing bounded denial remains unchanged | existing API test |
| No new authority | Changed files and imports are inspected | Checks run | No corpus, ranking, identity, persistence, provider/model, or financial seam changes | diff/architecture |

## Verification Commands

Run the focused Guidance API integration suite; platform-help contract,
Guidance, OpenAPI check, and generated-client check; Web model/component and
focused Chromium checks; Python compilation; architecture, security,
documentation, planning, and whitespace checks; controller-selected exact-
candidate verification; proportionate independent review; and aggregate
readiness. WRK-0168 reruns the unchanged complete live topology afterward.

## Documentation and Evidence Update

Record the live failure cause, exact serialization correction, focused and
affected checks, changed files, unchanged schema/client meaning, and resumed
qualification dependency. Keep local reviewer evidence out of tracked files.

## Stop Conditions

Stop for a schema, OpenAPI, generated-client, Guidance core/corpus/ranking,
identity, persistence, browser, dependency, provider/model, financial, or
unrelated serialization change; canonical conflict; stale CAP authority; or
active collision. Harmless formatting does not reopen review.

## Required Handoff

Report `CAP-0020.SLI-0082.WRK-0169`; terminal and continued cursor evidence;
focused API/contract/client/Web checks; changed files; documentation impact;
and remaining live qualification. Confirm no schema, generated client, corpus,
ranking, identity, persistence, provider/model, learner-policy, or financial
behavior changed, then leave WRK-0168 ready to resume.

## Planning History

- 2026-10-18: Authored just in time after WRK-0168 live Chromium received a
  successful terminal search document that omitted the OpenAPI-required
  nullable `next_cursor`. The correction is isolated from qualification,
  remains inside approved SLI-0082, and requires no durable decision or lower-
  level approval.
- 2026-10-18: Activated from clean recorded base `9fbe65f` after validating
  current CAP authority, the completed API dependency, the bounded correction
  route, exact file ownership, and no active coordination collision.
- 2026-10-18: Independent review of candidate `eefe722` found that globally
  retaining nulls also emitted contract-invalid optional null members. The
  correction remains bounded to the existing route, API evidence, contract
  note, and packet; fresh schema-backed evidence and re-review are required.
