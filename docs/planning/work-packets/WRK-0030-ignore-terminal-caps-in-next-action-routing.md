---
id: WRK-0030
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0010
capability: CAP-0003
depends_on: ["WRK-0018"]
decision_gates: []
parallel_safe_with: []
write_scope: ["docs/planning/skills/README.md", "docs/planning/skills/guide-next-planning-action/scripts/recommend_next.py", "docs/planning/skills/test_suite.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0010-explain-ready-work-and-order.md", "docs/planning/work-packets/WRK-0030-ignore-terminal-caps-in-next-action-routing.md"]
generated_artifacts: [".agents/skills/guide-next-planning-action"]
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0030:9b412511-e3d4-4c46-8cdd-96a804809810
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T16:20:20Z
---

# Agent Work Packet: Ignore Terminal CAPs in Next-Action Routing

## Objective and Deliverable

Correct the governed next-action router so completed and superseded capability
packages never become new approval gates merely because their historical local
approval record is absent. The router must continue to require current approval
for nonterminal shaped packages and must select the next actionable approved
capability deterministically.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Read CAP-0003, SLI-0010, WRK-0018, planning
skill compatibility rules, the canonical router, local approval contract,
skill behavior tests, and the planning/testing context packs.

## Decisions and Assumptions

- Terminal capabilities are historical satisfaction evidence, not candidates
  for fresh planning approval or new delivery.
- Missing local approval for a terminal CAP must not block an unrelated current
  approved CAP. This is a bounded anti-rigidity correction inside CAP-0003's
  explainable ordering outcome.
- Nonterminal `ready`, `active`, or `verifying` CAP packages still require a
  current capability approval. No approval is inferred, synthesized, or copied
  into tracked files.

## In Scope

- Exclude terminal CAP states from the router's missing-approval candidate set.
- Add a deterministic regression containing an unapproved completed CAP and an
  approved actionable CAP; require the actionable CAP's next manifest step.
- Preserve shaping, decision, active work, verifying work, approval, manifest,
  and empty-planning precedence.
- Synchronize the canonical skill into repository-local discovery and run the
  skill, prompt, planning, documentation, and aggregate readiness gates.

## Out of Scope

- Creating or editing approval records, retroactively approving CAP-0002,
  changing capability lifecycle states, changing planning precedence beyond
  terminal filtering, product prioritization, roadmap mutation, or delivery
  implementation.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Canonical router | Capability approval candidate selection | `recommend_next.py` | Do not route terminal history to approval |
| Skill behavior tests | CAP-package routing fixtures | `test_suite.py` | Prove missing terminal history is nonblocking |
| Skill contract | Shared compatibility wording | Planning skills README if needed | Make terminal semantics explicit |
| Discovery copy | Managed ignored skill installation | `generated_artifacts` only | Keep local invocation synchronized |
| Planning | Owning slice, packet, register | Named artifacts | Preserve correction evidence |

## Contracts and Interfaces

Preserve the next-action report schema, precedence order, local-only approval
ledger, stable-ID tie behavior, and all existing skill names. The behavioral
correction is limited to filtering `complete` and `superseded` CAPs before the
missing-approval route.

## Dependencies and Parallel Safety

WRK-0018 is complete and established hierarchy-aware ordering. This descendant
is serial because it changes the shared planning router and suite behavior. It
has no parallel-safe peer.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Completed historical CAP | A complete CAP lacks a local approval record | Routing runs | The CAP is ignored as terminal history | Router regression |
| Approved actionable CAP | A current approved CAP has a missing next manifest slice | Routing runs beside terminal history | `select-vertical-slice` names the approved CAP | Router regression |
| Unapproved active package | A nonterminal shaped package lacks approval | Routing runs | `approve-planned-work` remains required | Existing/new regression |
| Active or verifying work | A packet/slice is active or verifying | Routing runs | Existing higher-precedence implementation/closure route wins | Existing suite |
| No hidden authority | Terminal history is skipped | Results are inspected | No approval is created or inferred and no ledger detail is emitted | Ledger/result assertions |

## Verification Commands

```powershell
python docs/planning/skills/test_suite.py
python docs/planning/skills/validate_suite.py
python docs/planning/skills/evaluate_scenarios.py --responses docs/planning/skills/evals/reference-responses.json
python docs/planning/skills/sync_skills.py --mode auto
python docs/planning/skills/sync_skills.py --check
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
python dev-tools/agent/check_ready.py
git diff --check
```

## Documentation and Evidence Update

Update SLI-0010 completion evidence and the shared compatibility contract only
if needed to state terminal routing semantics. No product, architecture,
external, or approval record changes are expected.

## Stop Conditions

- The fix would bypass approval for a nonterminal CAP, create approval data,
  reorder higher-precedence active/verifying/decision routes, or infer product
  priority.
- Tests require personal or approval metadata in tracked fixtures.
- The change expands beyond deterministic terminal filtering or exposes a
  durable decision/material CAP-0003 change.

## Required Handoff

Report the prior blocked route, exact filter, regression results, preserved
approval behavior, skill synchronization, documentation impact, assumptions,
residual risk, and the resumed CAP-0001 next action.

## Completion Evidence

- The prior live route selected `approve-planned-work` for completed CAP-0002
  solely because its historical local capability record was absent, even though
  CAP-0001 was current, approved, and ready for its next manifest action.
- The canonical router now excludes only `complete` and `superseded` CAPs from
  the missing-approval candidate set. Every nonterminal CAP continues to
  require the exact current capability approval, and higher-precedence
  verifying, active, decision, and shaping routes are unchanged.
- The behavior suite adds a terminal unapproved CAP beside an approved current
  CAP and proves the result is `select-vertical-slice` for the current CAP with
  `approval_required: none`. It creates no approval record and exposes no
  ledger detail.
- Planning skill behavior, 8-skill compatibility validation, 17 prompt-level
  scenarios, canonical-to-local synchronization, and installed-copy checking
  passed. Planning integrity passed for 58 artifacts, documentation for 181
  Markdown files, diff whitespace checking, and all 27 aggregate readiness
  checks passed.
- No product priority, public application contract, lifecycle state, approval
  record, external action, or durable decision changed. The only generated
  output is the ignored managed skill-discovery copy.

## Planning History

- 2026-10-15: Authored as a bounded CAP-0003 descendant after the router tried
  to send completed CAP-0002 back through approval instead of selecting the
  next current approved CAP-0001 manifest action.
- 2026-10-15: Deterministic packet and planning validation passed; the packet
  is ready for a bounded CAP-0003 claim without lower-level approval.
- 2026-10-15: Delivered terminal-CAP filtering, the anti-rigidity regression,
  canonical skill synchronization, and complete planning/readiness evidence.
