---
id: WRK-0112
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-control-plane-correction
updated: 2026-10-16
parent: SLI-0005
capability: CAP-0002
depends_on: ["WRK-0013", "WRK-0070"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/README.md", "dev-tools/control-plane/review.py", "dev-tools/control-plane/test_review.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0005-record-review-findings-and-corrected-descendants.md", "docs/planning/work-packets/WRK-0112-allow-resubmission-after-failed-verification.md"]
generated_artifacts: []
base_revision: da4eee2b2037c127266111cdc605a08de20757fc
claim_id: WRK-0112:c5c7d610-4a1d-456d-8f0f-fc05636e8777
claimed_by: codex-control-plane-correction
claimed_at: 2026-10-16T20:50:53Z
---

# Agent Work Packet: Allow Resubmission After Failed Verification

## Objective and Deliverable

Correct the reusable review/resubmission service so an owner can submit a clean
strict descendant after the latest exact-candidate verification attempt fails
one or more selected checks or times out. Preserve append-only receipts,
exact-candidate binding, reviewer independence, strict-descendant lineage, and
fresh verification. Do not require or synthesize a technical review for a
candidate that never qualified for review.

This packet implements the bounded correction route recorded for WRK-0013 with
route digest
`sha256:fd734819d0fb2fb9039fd7c221ff804e083198bf809a2a162b055dd913060dec`.

## Required Context

Read the repository startup sources, CAP-0002, SLI-0004, SLI-0005, WRK-0012,
WRK-0013, WRK-0070, the recorded correction route, concurrent-work and testing
guidance, the receipt/review/state implementations and tests, and the nearest
control-plane README before editing.

## Decisions and Assumptions

- A failed or timed-out selected check is evidence that the submitted candidate
  may need a correction; it is not an independent technical disposition.
- Authorization is limited to the latest stored receipt for the exact current
  candidate, and that receipt must fail validation only because a selected
  check failed or timed out.
- Stale catalog/input/candidate evidence, incomplete coverage, candidate drift,
  malformed receipts, digest mismatch, and a prior review of the exact
  candidate do not authorize this route.
- The corrected candidate must remain a strict descendant inside the current
  packet scope and must receive fresh exact-candidate verification and the
  ordinary independent review.

## In Scope

- Add a narrow failed-verification authorization predicate to ordinary
  corrected resubmission.
- Retain adverse-review and cleanup-only resubmission behavior unchanged.
- Add anti-rigidity and anti-bypass tests for failed, timed-out, passing, stale,
  malformed, drifted, already-reviewed, same-candidate, and forked cases.
- Document the lifecycle route and its retained safety boundaries.

## Out of Scope

Weakening receipt validation, treating a failed check as a review, bypassing
fresh verification or independent review, rewriting candidate/receipt history,
arbitrary state edits, remote execution, or another approval stage.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable review core | review, receipt and resubmission services | `dev-tools/control-plane/review.py` | recognize one structurally valid failed-execution receipt as correction authority |
| Focused evidence | review and anti-rigidity tests | `dev-tools/control-plane/test_review.py` | prove the route is usable and cannot accept stale or malformed evidence |
| Reusable guidance | control-plane command lifecycle | `dev-tools/control-plane/README.md` | explain failed-verification correction without adding approval |
| Planning lineage | this packet, parent slice and register | named planning files | preserve the bounded descendant correction |

## Acceptance Scenarios

| Scenario | Expected result |
| --- | --- |
| Selected check fails or times out | the exact owner may submit one strict descendant and fresh verification is required |
| Candidate has no receipt | resubmission is refused with bounded remediation |
| Latest exact receipt qualifies | the candidate proceeds to review; correction is not authorized by verification |
| Receipt is stale, malformed, incomplete, drifted, or digest-invalid | resubmission is refused without state mutation |
| Exact candidate was already reviewed | the existing adverse-review or cleanup-only rules remain authoritative |
| Descendant is the same commit or a fork | resubmission is refused |

## Verification Commands

- `python dev-tools/control-plane/test_review.py`
- `python dev-tools/control-plane/test_verification.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- affected exact-candidate verification and independent technical review
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

## Stop Conditions

Stop for receipt-validation weakening beyond failed/timed-out selected checks,
review bypass after an exact candidate has been reviewed, non-descendant
replacement, history rewrite, a path outside the correction route, or material
CAP-0002 drift.

## Required Handoff

Report the authorization predicate, retained refusal cases, exact focused and
aggregate results, candidate and receipt, independent technical disposition,
documentation impact, and confirmation that no approval or review record was
synthesized.

## Planning History

- 2026-10-16: Authored from the bounded WRK-0013 correction route after a real
  product packet produced a non-qualifying first receipt and exposed that no
  legal strict-descendant resubmission existed before independent review. The
  correction removes that dead end without weakening evidence or review.
