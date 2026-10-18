---
id: WRK-0162
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0018-correction
updated: 2026-10-18
parent: SLI-0076
capability: CAP-0018
depends_on: [WRK-0160]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/features/assistance-preferences/model.ts", "apps/web/tests/unit/assistancePreferencesModel.test.ts", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0076-control-ai-help-and-local-reminders.md", "docs/planning/work-packets/WRK-0161-qualify-ai-help-and-local-reminders-live-flow.md", "docs/planning/work-packets/WRK-0162-accept-canonical-assistance-api-timestamps.md"]
generated_artifacts: []
base_revision: 8b147c1f7053961eeaa0af0df50d46b2d60fd5df
claim_id: WRK-0162:11ecff6f-4cb9-4443-809a-cd602b00153e
claimed_by: codex-cap-0018-correction
claimed_at: 2026-10-18T01:06:13Z
---

# Agent Work Packet: Accept Canonical Assistance API Timestamps

## Objective and Deliverable

Correct the assistance-preference browser validator so it accepts the
canonical UTC timestamp precision already emitted by the protected API and
bound into profile digests. Preserve fail-closed calendar, timezone, shape,
chronology, and digest checks without changing the contract, backend, public
API, generated client, route semantics, or local reminder adapter.

## Required Context

Revalidate `AGENTS.md`, `docs/README.md`, routed context, CAP-0018, SLI-0076,
WRK-0160, the assistance contract and API timestamp serializer, the browser
validator and nearest tests, and the WRK-0161 live failure evidence. Stop for
canonical conflict, stale CAP authority, active collision, or scope drift.

## In Scope

- Accept canonical `Z` timestamps with absent or one-through-six fractional
  second digits, matching the backend preference serializer and Python core.
- Retain real-calendar validation, UTC-only input, chronology, exact closed
  profile/history/export shapes, and digest validation.
- Add anti-rigidity tests for no fraction, milliseconds, microseconds, varied
  valid values, and malformed/non-UTC/impossible timestamps.
- Reconcile WRK-0161 dependency and planning lifecycle evidence.

## Out of Scope

- Contract, OpenAPI, generated-client, backend serializer, persistence,
  route, style, wording, local reminder, model/provider, notification, or
  unrelated date parser changes.
- Relaxing arbitrary timestamp text, ignoring digests, or converting the
  server timestamp before hashing.

## Expected File and Boundary Impact

| Boundary | Change | Invariant |
| --- | --- | --- |
| Assistance browser model | Correct canonical timestamp validation | Exact server text remains the digest material |
| Unit evidence | Cover valid precision and invalid calendar/offset cases | Tests assert meaning, not one frozen timestamp |
| Planning | Record corrective dependency and lifecycle | Qualification resumes only after correction completes |

No unlisted file may change.

## Contracts and Interfaces

The public shape remains `learner-assistance-preferences/v1`; no field, value,
endpoint, or generated type changes. Canonical UTC input must use a four-digit
year, two-digit month/day/time fields, and terminal `Z`, optionally with one
through six fractional-second digits.
Offsets, missing `Z`, extra precision, impossible calendar dates, leap-second
text, and other shapes remain invalid. The validator hashes the exact received
profile material after validation and compares the existing SHA-256 digest.

## Dependencies and Parallel Safety

WRK-0160 supplies the browser validator and is complete. WRK-0161 found the
defect during live qualification and is returned to ready with an explicit
dependency on this correction. Shared planning paths and assistance source
make this packet non-parallel-safe with that qualification packet.

## Decisions and Assumptions

- The backend `LearnerPreferenceTimestampModel` and canonical domain digest
  are accepted authority; the browser must consume their valid exact text.
- JavaScript `Date` has millisecond precision, so calendar fields can be
  validated without rewriting or truncating the exact microsecond text used
  for digest comparison.
- No durable decision gate is reached and no lower-level approval is needed.

## Acceptance Scenarios

| Scenario | Expected result |
| --- | --- |
| Whole-second API profile | Valid shape and digest are accepted |
| Millisecond API profile | Valid shape and digest are accepted |
| Microsecond API profile | Valid shape and digest are accepted without truncating digest material |
| Varied fractional precision | One through six digits remain valid |
| Impossible calendar date | Rejected before digest acceptance |
| Offset or non-UTC text | Rejected |
| Seven fractional digits | Rejected |
| Invalid chronology | Rejected |
| Digest mismatch | Rejected unchanged |
| Anti-rigidity | Validation does not freeze one date, revision, profile ID, or precision |

## Verification Commands

Run focused assistance model tests; full Web unit/component/contract tests;
typecheck, zero-warning lint, focused assistance Chromium, and production
build; planning validation; affected exact-candidate verification;
proportionate independent review; and aggregate readiness. WRK-0161 reruns the
complete live topology after this packet completes.

## Documentation and Evidence Update

Record the live failure cause, exact correction, focused and affected checks,
changed files, no contract/API impact, and the resumed qualification
dependency in this packet, WRK-0161, SLI-0076, and the register. Keep approval
and reviewer records in ignored local storage only.

## Stop Conditions

Stop for a contract, backend serializer, OpenAPI, generated-client, persistence,
route, local adapter, identity, provider/model, notification, or broader date-
handling change; a canonical-source conflict; stale CAP authority; or active
scope collision. Harmless formatting or optional wording does not reopen
review.

## Required Handoff

Report `CAP-0018.SLI-0076.WRK-0162`; the exact accepted timestamp language;
focused/full Web and affected checks; changed files; documentation impact; and
remaining gaps. Confirm no API, contract, backend, identity, AI, notification,
or financial behavior changed, then leave WRK-0161 ready to resume.

## Planning History

- 2026-10-18: Authored just in time after WRK-0161 live Chromium received a
  valid digest-bound microsecond API timestamp that the browser validator
  rejected. The correction is isolated from qualification and requires no new
  durable decision or lower-level approval.
- 2026-10-18: Activated from recorded base `8b147c1` after validating current
  CAP authority, the completed browser dependency, exact corrective scope, and
  no active coordination collision.

