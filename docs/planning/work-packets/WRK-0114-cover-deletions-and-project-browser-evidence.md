---
id: WRK-0114
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-control-plane-correction
updated: 2026-10-16
parent: SLI-0004
capability: CAP-0002
depends_on: ["WRK-0067"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/README.md", "dev-tools/control-plane/check_approved_lesson.py", "dev-tools/control-plane/financial_academy_checks.py", "dev-tools/control-plane/git_candidate.py", "dev-tools/control-plane/test_control_plane.py", "dev-tools/control-plane/test_verification.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0004-select-affected-checks-and-record-receipts.md", "docs/planning/work-packets/WRK-0114-cover-deletions-and-project-browser-evidence.md"]
generated_artifacts: []
base_revision: f31c7b2c73c225bbf9adf8f0a4060c9d2638b4e7
claim_id: WRK-0114:f24cb3a0-4dde-4f03-9869-3873c78859cb
claimed_by: codex-control-plane-correction
claimed_at: 2026-10-16T21:40:40Z
---

# Agent Work Packet: Cover Deletions and Project Browser Evidence

## Objective and Deliverable

Correct exact-candidate and affected-check evidence so file deletions are
included in scope enforcement and receipts, and Project browser changes select
a focused Chromium qualification that exercises the Project flow. This packet
implements the bounded WRK-0012 correction route with digest
`sha256:e014422183874520808627e73230276de33a347444087d33d4b0e2368ad0c1bf`.

## Required Context

Read `AGENTS.md`, `docs/README.md`, the routed startup sources, CAP-0002,
SLI-0004, WRK-0012, WRK-0067, the recorded correction route, testing and
concurrent-work guidance, the Git candidate adapter, affected-check catalog and
executor, their focused tests, and the nearest control-plane README before
editing.

## Decisions and Assumptions

- Deletions are first-class candidate changes. They must appear in
  `changed_paths`, participate in declared-scope enforcement, and select checks
  from the deleted path even though no candidate blob exists there.
- Existing copy/rename/type-change behavior remains supported; declared inputs
  still must exist in the candidate.
- Project browser coverage is a narrow repository adapter check, not a reason
  to run every Chromium suite or the live approved-lesson suite.
- The focused check reuses the prepared Node and dependency isolation already
  provided by the repository web-check wrapper.

## In Scope

- Include deleted paths in exact Git submission evidence and scope checks.
- Add real-Git regression coverage for in-scope and out-of-scope deletions.
- Classify Project browser specs and Project browser-affecting source changes.
- Add a focused Project Chromium command and catalog entry with deterministic
  selector tests and bounded timeout.
- Document the two retained evidence invariants and anti-rigidity boundary.

## Out of Scope

Product behavior, changing Project test meaning, expanding the live
approved-lesson suite, mandatory full-browser execution for unrelated web
changes, remote execution, receipt reuse, or a new approval stage.

## Expected File and Boundary Impact

| Area | Allowed to change | Reason |
| --- | --- | --- |
| Reusable Git adapter | `git_candidate.py`, lifecycle tests | include deletions in complete candidate evidence and scope enforcement |
| Repository check adapter | catalog, web wrapper, verification tests | select and execute one focused Project browser check |
| Operator guidance | control-plane README | explain deleted-path and focused-browser evidence |
| Planning lineage | this packet, parent slice, register | retain bounded correction provenance |

## Contracts and Interfaces

The existing submission schema is unchanged: `changed_paths` becomes complete
for Git statuses already accepted by the adapter, including deletions. Deleted
paths are normalized and checked against `write_scope` but are never treated as
declared candidate inputs. The repository catalog adds one allowlisted Project
browser check whose command is fully materialized in the normal plan and
receipt; no product API or external contract changes.

## Dependencies and Parallel Safety

WRK-0067 is complete and provides the existing isolated web-check wrapper and
path taxonomy. This correction overlaps shared control-plane files and is not
parallel-safe with another control-plane packet. It may run while WRK-0111 is
awaiting correction because it does not edit product files; WRK-0111 must use a
fresh catalog and adapter after this packet completes.

## Acceptance Scenarios

| Scenario | Expected result |
| --- | --- |
| In-scope deletion | submission and receipt include the deleted path |
| Out-of-scope deletion | submission is refused with `git.scope-escape` |
| Project source or Project browser spec changes | focused Project Chromium evidence is selected |
| Unrelated unit/component-only web change | Project Chromium is not selected |
| Existing browser boundary changes | current mocked, roadmap, and live routing remains unchanged |

## Verification Commands

- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/control-plane/test_verification.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- affected exact-candidate verification and independent technical review
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

## Stop Conditions

Stop if deletion handling weakens exact ancestry, clean-worktree, input, or
scope checks; Project routing requires broad unrelated browser/live execution;
the correction escapes the recorded path set; or CAP-0002 materially drifts.

## Documentation and Evidence Update

Update reusable operator guidance, the parent slice, this packet, and the
planning register. Store exact receipts and independent reviewer records only
under ignored local control-plane state; tracked files contain no reviewer or
approval identity, disposition, or history.

## Required Handoff

Report deletion evidence and scope-denial behavior, focused Project browser
selection and execution, retained narrow routing, exact candidate and receipt,
focused and aggregate results, independent disposition, documentation impact,
and residual environment gaps.

## Completion Evidence

Exact candidate evidence now parses NUL-delimited Git name-status output,
includes direct deletions, and records both source and destination for detected
copies and renames. Real-Git regressions prove in-scope paths are complete and
an out-of-scope source cannot be hidden by moving it into an allowed path.

The Financial AI Academy adapter selects a focused `project:browser` command
for Project feature code, its behavioral stylesheet, its Chromium specs, and
changes to the catalog or executor that define the command. The corrected exact
candidate's seven selected checks passed, including the focused six-scenario
Project Chromium suite and isolated approved-lesson live qualification.
Focused lifecycle tests passed 13 cases, verification tests passed 29 with
three platform-specific skips, planning and documentation checks passed, the
aggregate readiness gate passed 29 of 29 checks, and whitespace validation was
clean. Exact receipts remain ignored local evidence. No product contract,
remote execution, approval stage, or broad full-browser requirement was added.

## Planning History

- 2026-10-16: Authored from the bounded WRK-0012 correction route after a
  candidate audit found that exact-candidate evidence omitted
  deletions and that Project browser behavior was not selected for the packet.
  The correction stays inside SLI-0004 and adds no approval stage.
- 2026-10-16: Returned to active correction after exact-candidate audit found
  rename-source, Project stylesheet, and candidate-bound browser-execution
  gaps. The refined implementation remains inside the recorded correction
  route and preserves narrow routing for unrelated web work.
