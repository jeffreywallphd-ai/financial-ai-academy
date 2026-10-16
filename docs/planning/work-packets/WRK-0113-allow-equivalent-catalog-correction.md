---
id: WRK-0113
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-control-plane-correction
updated: 2026-10-16
parent: SLI-0005
capability: CAP-0002
depends_on: ["WRK-0112"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/README.md", "dev-tools/control-plane/review.py", "dev-tools/control-plane/test_review.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0005-record-review-findings-and-corrected-descendants.md", "docs/planning/work-packets/WRK-0113-allow-equivalent-catalog-correction.md"]
generated_artifacts: []
base_revision: 80c15703a6d2b6fba50edc757c7ba204b082ec43
claim_id: WRK-0113:c7fe7885-9605-4aa3-ac7c-a0bd62e18e61
claimed_by: codex-control-plane-correction
claimed_at: 2026-10-16T21:11:48Z
---

# Agent Work Packet: Allow Equivalent-Catalog Correction

## Objective and Deliverable

Keep failed-verification correction usable when an unrelated catalog revision
occurs after the failed receipt. Accept the historical failure only when the
current catalog selects the exact same check IDs, matched paths, and materialized
commands for the exact historical candidate. Continue to fail closed whenever
the affected evidence route changes.

This packet implements the bounded WRK-0112 correction route with digest
`sha256:8b893dcf685acc3b95decb375e1147f43c17bb5a2aa1f5788cf4b87f5331ed47`.

## Required Context

Read the repository startup sources, CAP-0002, SLI-0004, SLI-0005, WRK-0012,
WRK-0013, WRK-0070, WRK-0112, the recorded correction route, concurrent-work
and testing guidance, the receipt/review implementation and tests, the tracked
check catalog, and the nearest control-plane README before editing.

## Decisions and Assumptions

- A catalog digest change alone does not invalidate a failed execution when the
  current catalog yields the same affected check IDs, matched paths, and exact
  materialized command arguments for the receipt's candidate and base revision.
- The receipt plan, receipt digest, provenance, exact candidate, current
  submission digest, attempt coverage, candidate stability, and failed/timed-out
  result must remain valid.
- Any added, removed, renamed, rematched, or command-changed affected check
  denies correction and requires current exact-candidate evidence.

## In Scope

- Add a reusable semantic-equivalence predicate for the one stale-catalog error
  allowed by failed-verification correction.
- Add positive coverage for unrelated catalog expansion.
- Add refusal coverage for newly affected checks, changed commands, changed
  matched paths, incomplete attempt commands, and all existing tamper/drift
  cases.
- Document why catalog evolution does not create an unrelated correction dead
  end while preserving fresh verification of the descendant.

## Out of Scope

Accepting stale catalogs for technical review, reusing a passing receipt,
running historical commands, weakening receipt integrity, ignoring changed
affected checks, rewriting evidence, adding an approval stage, or changing
product behavior.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable review core | receipt validation, affected selection, materialized commands | `dev-tools/control-plane/review.py` | admit only a semantically identical current affected route |
| Focused evidence | failed-verification and anti-bypass tests | `dev-tools/control-plane/test_review.py` | prove safe catalog evolution and changed-route refusals |
| Operator guidance | failed-verification correction lifecycle | `dev-tools/control-plane/README.md` | explain retained safety boundary |
| Planning lineage | this packet, parent slice, register | named planning files | retain bounded correction provenance |

## Acceptance Scenarios

| Scenario | Expected result |
| --- | --- |
| Unrelated check is added to the catalog | correction is allowed only when current selected IDs, matched paths, and commands are identical |
| New check now matches the historical candidate | correction is refused |
| Existing selected command or matched path changes | correction is refused |
| Historical attempt lacks the exact executed command | stale-catalog correction is refused |
| Receipt is tampered, incomplete, drifted, passing, or already reviewed | existing refusal remains unchanged |
| Equivalent route accepted | only a strict descendant is submitted and fresh verification plus normal review remain required |

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

Stop if the route would accept an affected-check selection, matched-path set, or
materialized command change; tolerate another receipt error; bypass fresh
descendant verification or technical review; rewrite evidence; or exceed the
recorded correction scope.

## Required Handoff

Report the equivalence predicate, retained refusal cases, focused and aggregate
results, exact candidate and receipt, documentation impact, assumptions, and
remaining gaps. Keep technical-review records only in ignored local storage.

## Planning History

- 2026-10-16: Authored after WRK-0112's catalog coverage improvement changed
  the global digest and unintentionally blocked an unrelated product packet's
  otherwise valid failed-verification correction. The packet preserves every
  affected-route invariant and adds no approval stage.
