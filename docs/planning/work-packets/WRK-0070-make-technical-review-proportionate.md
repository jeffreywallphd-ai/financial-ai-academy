---
id: WRK-0070
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-control-plane-correction
updated: 2026-10-16
parent: SLI-0005
capability: CAP-0002
depends_on: ["WRK-0013"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane", "docs/standards/testing-and-verification-standards.md", "docs/planning/work-packets/WRK-0070-make-technical-review-proportionate.md", "docs/planning/vertical-slices/SLI-0005-record-review-findings-and-corrected-descendants.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 903f3f6cee75281372da8a899da936f25629ff1c
claim_id: WRK-0070:af5e26cf-023c-4cfa-9def-1b043fc65ac7
claimed_by: codex-control-plane-correction
claimed_at: 2026-10-16T09:20:05Z
---

# Agent Work Packet: Make Technical Review Proportionate

## Objective and Deliverable

Correct the reusable review service so inconsequential cleanup findings cannot
force an adverse disposition or a full correction/re-review loop. An accepted
candidate may carry explicitly classified non-blocking cleanup findings. A
strict descendant mechanically proven to change only whitespace or blank lines
must receive fresh affected verification but may inherit the accepted technical
review. Other cleanup is deferred or uses the ordinary review path.

This packet implements the bounded correction route recorded for WRK-0013. It
preserves exact-candidate lineage, append-only reviewer evidence, independent
review for substantive change, and all existing blocking controls.

## Required Context

Read `AGENTS.md`, `docs/README.md`, the routed repository startup sources,
CAP-0002, SLI-0005, WRK-0013, the recorded bounded correction route,
concurrent-work and testing guidance, the complete review/state/receipt/status
implementation, its tests, and the nearest README.

## Decisions and Assumptions

- `substantive` remains the default finding class for backward compatibility.
- `cleanup` is explicit, non-blocking, and limited to changes that do not alter
  functionality, semantics, accessibility, security, data, contracts, policy,
  or required evidence.
- An adverse disposition requires a blocking substantive finding. Whitespace,
  formatting, cosmetic presentation, or equivalent low-consequence cleanup
  cannot by itself produce `changes-requested` or `rejected`.
- Review inheritance is allowed only for a strict descendant of an accepted
  candidate, only while every addressed open finding is cleanup, only when Git
  proves the incremental delta changes whitespace or blank lines, and only
  after fresh affected verification of the descendant.
- Repeated verified cleanup descendants retain the original accepted candidate
  and review-round basis; an inherited candidate is never used as a fake round.
- The repository-specific alpha/beta UI deferral policy belongs in the testing
  guidance; the reusable review core exposes only the generic cleanup class.

## In Scope

- Additive finding classification with backward-compatible defaults and stable
  validation/refusal codes.
- Enforcement that cleanup findings are non-blocking and cannot support an
  adverse disposition.
- A whitespace-only corrected-descendant route after acceptance, with explicit
  inherited-review lineage, mechanical delta proof, and fresh-verification
  requirement.
- Status projection that distinguishes exact, pending inherited, and verified
  inherited review without rewriting reviewer history.
- Anti-rigidity tests for whitespace cleanup, repeated inherited descendants,
  semantic-change denial, and retained hard stops for substantive
  functionality, accessibility, security, data, contract, and semantic
  findings.
- Reusable documentation and repository-specific alpha/beta UI deferral rules.

## Out of Scope

Automatic source edits, subjective automatic severity assignment, removal of
independent review, bypass of affected verification, remote review services,
tracked reviewer records, visual-regression infrastructure, or implementation
of the eventual product-cleanup capability.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable review core | findings, rounds, resubmission, receipts | `dev-tools/control-plane/` | Add proportionate cleanup classification and review inheritance |
| Focused evidence | review/status tests | `dev-tools/control-plane/` | Prove cleanup does not create a re-review loop and substantive risk still does |
| Repository policy | testing and verification standard | named standard | Define alpha/beta UI deferral and escalation boundary |
| Planning evidence | packet, parent slice, register | named planning files | Preserve correction lineage and completion evidence |

## Contracts and Interfaces

The existing review round remains append-only. Finding records gain an additive
class with `substantive` as the legacy default. Cleanup-only resubmission gains
an explicit CLI flag and records the original accepted-review basis in the
submission. The repository adapter must mechanically prove the incremental
Git delta is whitespace-only. The exact descendant still requires a qualifying
receipt before inherited acceptance becomes effective.

## Dependencies and Parallel Safety

WRK-0013 is complete. This packet is serial because it changes the shared review
service and status projections. The correction route confines implementation
to the completed packet's original control-plane and guidance boundary.

## Acceptance Scenarios

| Scenario | Expected result |
| --- | --- |
| Blank line or formatting cleanup | The finding is accepted as cleanup and cannot cause an adverse disposition |
| Alpha/beta cosmetic UI concern | It is non-blocking unless it impairs function, meaning, access, safety, contrast, hierarchy, or responsive use; repository guidance routes it to final cleanup |
| Whitespace cleanup fixed immediately | A strict descendant is mechanically proven whitespace-only, submitted with inherited-review lineage, receives fresh affected verification, and needs no new review round |
| Cleanup deferred | The accepted candidate remains completable with the non-blocking finding visible for backlog capture |
| Substantive defect | A blocking substantive finding still requires a strict descendant, fresh verification, explicit closure, and independent re-review |
| Semantic or styling edit | It cannot inherit review through the whitespace-only route; styling is deferred to final cleanup unless explicitly moved earlier |
| Attempted bypass | Cleanup inheritance is refused for adverse reviews, blocking findings, non-descendants, unverified descendants, or a delta that is not mechanically whitespace-only |
| Legacy finding | A finding without the additive class retains substantive behavior |

## Verification Commands

- `python dev-tools/control-plane/test_review.py`
- `python dev-tools/control-plane/test_policy.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

## Documentation and Evidence Update

Document classification, cleanup-only review inheritance, retained exact-commit
verification, and the alpha/beta UI deferral boundary. Record behavior and test
results without copying reviewer or approval records into tracked files.

## Stop Conditions

Stop for a path outside the correction route, review inheritance without fresh
verification, loss or mutation of prior review evidence, a cleanup class that
can hide functional/accessibility/security/data/contract/semantic risk, or a
new approval/external-action boundary.

## Required Handoff

Report the additive contracts, exact anti-rigidity and retained-safety tests,
affected and aggregate results, documentation impact, assumptions, residual
risk, and the deferred cleanup CAP reference.

## Planning History

- 2026-10-16: Authored from the bounded WRK-0013 correction route after a
  whitespace-only review loop exposed avoidable workflow friction. The packet
  keeps substantive re-review intact and adds no approval stage.
