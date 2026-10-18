---
id: WRK-0163
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0018-correction
updated: 2026-10-18
parent: SLI-0076
capability: CAP-0018
depends_on: [WRK-0129]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/features/project-workspace/api.ts", "apps/web/src/features/project-workspace/model.ts", "apps/web/tests/unit/projectWorkspaceModel.test.ts", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0076-control-ai-help-and-local-reminders.md", "docs/planning/work-packets/WRK-0161-qualify-ai-help-and-local-reminders-live-flow.md", "docs/planning/work-packets/WRK-0163-correlate-equivalent-project-timestamps.md"]
generated_artifacts: []
base_revision: 80b8eef4e5819a5cb03ae29d43911d45f4f565bb
claim_id: WRK-0163:560119ab-6682-452e-b029-db6d87c794ae
claimed_by: codex-cap-0018-correction
claimed_at: 2026-10-18T01:26:40Z
---

# Agent Work Packet: Correlate Equivalent Project Timestamps

## Objective and Deliverable

Allow the Project learning loader to correlate two already validated UTC
timestamps that represent the same instant with different fractional-second
widths. Preserve exact microsecond meaning so `.8629Z` and `.862900Z` match,
while `.862900Z` and `.862901Z` remain different. Keep the source API strings
unchanged and retain conservative rejection for invalid or genuinely
uncorrelated responses.

## Required Context

Before implementation, revalidate `AGENTS.md`, `docs/README.md`, routed startup
context, CAP-0018, SLI-0076, completed WRK-0129 and WRK-0162, current decision
readiness, the Project workspace public contracts, model validators, loader,
unit tests, live failure trace, nearest README, and active coordination state.
Stop for a canonical conflict, stale CAP package, missing dependency, unresolved
durable decision, active write collision, or material scope drift.

## Decisions and Assumptions

- The live API returned the same semantic instant as `...20.862900Z` in the
  completion projection and `...20.8629Z` in submission history. Both values
  individually satisfy the accepted one-through-six-digit UTC contract.
- Correlation must preserve microseconds and therefore must not use the
  millisecond-limited JavaScript `Date` value as its comparison authority.
- This is a bounded compatibility correction inside the approved CAP-0018
  qualification flow. It changes no contract, persistence, identity, grading,
  evidence, or user-visible product meaning and reaches no durable decision.

## In Scope

- One reusable Project timestamp-equivalence helper over validated UTC strings.
- Use that helper only when correlating Project completion and submission
  history entries in the browser loader.
- Unit evidence for equivalent fractional widths, genuine microsecond
  differences, invalid inputs, and loader fail-closed behavior.
- Planning dependency updates so WRK-0161 resumes after this correction.

## Out of Scope

Backend serialization, OpenAPI or schema changes, generated clients, timestamp
ordering, timezone-offset equivalence, persistence, contracts, migrations,
Project submission behavior, UI wording or styling, and any other loader
correlation rule.

## Expected File and Boundary Impact

| Boundary | Owned change | Evidence target |
| --- | --- | --- |
| Project browser model | Add fixed-width UTC comparison without losing microseconds | pure unit vectors |
| Project learning loader | Compare submission timestamps by semantic instant | loader accepts width-only variation and rejects true mismatch |
| Planning | Route WRK-0161 through this dependency | packet, slice, and register agree |

No backend, contract, generated-client, database, design-system, or unrelated
planning source is in scope.

## Contracts and Interfaces

The helper accepts only the canonical Project timestamp domain already
validated by the model: a UTC `Z` suffix, valid calendar/time fields, and zero
through six fractional digits. It compares an exact normalized representation
with six fractional digits. It returns false for invalid text, non-UTC offsets,
or different instants. It does not mutate, reserialize, or expose normalized
values.

## Dependencies and Parallel Safety

WRK-0129 supplies the qualified Project submission flow that revealed this
compatibility seam. WRK-0161 depends on this packet before resuming complete
live qualification. This packet is not parallel-safe with another writer on
the Project workspace model, loader, tests, or SLI-0076 planning surfaces.

Claim the packet from a recorded base revision, acquire one-owner leases for
the declared write scope, and complete it before reactivating WRK-0161.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Equivalent precision | `.8629Z` and `.862900Z` | helper compares them | result is true without truncation | unit |
| Exact second | no fraction and `.000000Z` | helper compares them | result is true | unit |
| Microsecond difference | `.862900Z` and `.862901Z` | helper compares them | result is false | unit |
| Invalid or offset input | malformed text or non-UTC offset | helper compares it | result is false | unit |
| Correlated loader | completion and history differ only in fractional width | Project learning loader composes them | route is ready | unit |
| True mismatch | completion and history differ by one microsecond | loader correlates them | route is `invalid-response` | unit |

## Verification Commands

Run the focused Project workspace unit suite; full Web tests, typecheck,
zero-warning lint, and build as selected by the affected-check catalog;
planning, documentation, Python compilation, and whitespace checks;
controller-selected exact-candidate verification; proportionate independent
technical review; and `python dev-tools/agent/check_ready.py`. WRK-0161 will
then rerun the complete isolated live workflow rather than duplicating it here.

## Documentation and Evidence Update

Record the exact candidate, qualifying receipt, focused equivalence and
fail-closed tests, selected Web checks, scope, and remaining live dependency.
Keep approval and reviewer records only in ignored local control-plane storage.

## Stop Conditions

Stop for a contract, backend serializer, OpenAPI, generated-client, persistence,
migration, UI, dependency, timezone-equivalence, ordering, or Project behavior
change; any loss of microsecond discrimination; a need to accept invalid
timestamps; an unresolved durable decision; active scope collision; or material
CAP-0018/SLI-0076 drift.

Do not reopen planning for harmless formatting or another inconsequential
correction that does not change functionality or the approved outcome.

## Required Handoff

Report `CAP-0018.SLI-0076.WRK-0163`; exact candidate and receipt; accepted and
rejected timestamp vectors; loader correlation behavior; focused, affected,
and aggregate checks; changed files; unchanged contracts/backend/API strings;
and WRK-0161 readiness.

## Planning History

- 2026-10-18: Authored just in time after WRK-0161 proved the assistance path
  and then reproduced a Project completion/history correlation failure caused
  only by equivalent fractional-second widths. The correction is bounded to
  exact browser-side correlation and requires no lower-level approval.
- 2026-10-18: Activated from recorded base `80b8eef` after validating the
  completed dependency, current CAP authority, exact write scope, and no active
  coordination collision.
