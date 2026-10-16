---
id: WRK-0067
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-control-plane-correction
updated: 2026-10-16
parent: SLI-0004
capability: CAP-0002
depends_on: ["WRK-0012"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/tests/browser/roadmap-review/roadmap-review.e2e.ts", "dev-tools/control-plane/README.md", "dev-tools/control-plane/check_approved_lesson.py", "dev-tools/control-plane/financial_academy_checks.py", "dev-tools/control-plane/test_verification.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0004-select-affected-checks-and-record-receipts.md", "docs/planning/work-packets/WRK-0067-cover-web-and-live-affected-verification.md"]
generated_artifacts: []
base_revision: d98fb06d5370358c02b0cc7840feb7cae5e3cf68
claim_id: WRK-0067:47dd5928-895f-43cd-a3e2-1eb258efe3ff
claimed_by: codex-control-plane-correction
claimed_at: 2026-10-16T01:33:39Z
---

# Agent Work Packet: Cover Web and Live Affected Verification

## Objective and Deliverable

Correct the affected-check catalog so changed web tests and approved-lesson
cross-system tests produce evidence that actually exercises those boundaries.
Provide a repository adapter check that builds the exact static application,
runs the existing live PostgreSQL/Python/Chromium qualification from an
isolated tracked-candidate snapshot, and leaves the working tree untouched
before the controller rechecks Git stability.

## Required Context

Read and follow the repository `AGENTS.md`, `docs/README.md`, routed context
packs, testing/change-impact standards, CAP-0002, SLI-0004, WRK-0012, the
correction route, verification core and tests, local-development runner, and
approved-lesson runner before editing.

## Decisions and Assumptions

- The project-neutral selector and receipt model remain unchanged. Only the
  Financial AI Academy catalog and a repository-specific composed check are
  extended.
- The existing approved-lesson runner remains the sole live qualification.
  The composed check only prepares and restores its static build input.
- Node/npm and Python remain environment-owned prerequisites. The wrapper uses
  the current Python and either the existing explicit Node/npm pair or the
  available npm command, and fails with an actionable message when they are
  incompatible.
- Working-tree build non-mutation is mandatory on success, failure, and
  interruption; the exact-candidate post-run stability check remains
  authoritative. The correction builds and runs from an isolated
  tracked-candidate snapshot with the prepared dependencies linked into that
  snapshot.

## In Scope

- Map changed web source/tests to typecheck, lint, and Vitest checks.
- Map changed approved-lesson browser/runner inputs to the existing live
  qualification.
- Classify first-class web build, generated-client, mocked-browser,
  roadmap-review, local-runtime, local-script, and documentation paths without
  routing documentation-only or Python-only changes through unrelated checks.
- Keep the roadmap-review hierarchy browser fixture aligned with current
  dynamic planning data so the newly selected behavior check proves both
  refined and honestly unrefined routes.
- Add bounded isolated build/live wrappers with deterministic tests for
  absent, present, unexpected, linked, and concurrently changing worktree
  build paths plus failing subprocesses.
- Prove narrow documentation and ordinary control-plane changes remain narrow,
  while browser-unit changes do not automatically select Docker/live evidence.
- Document the repository-specific check behavior and prerequisites.

## Out of Scope

Changes to product behavior, browser or live test meaning, the generic
verification contract, dependency installation, CI services, remote execution,
evidence reuse, approval topology, or any arbitrary command surface.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Repository check adapter | catalog definitions and path patterns | `financial_academy_checks.py` | Select real web/live evidence for affected paths |
| Composed live check | development/runtime prerequisites and current runner | `check_approved_lesson.py` | Build and restore exact tracked static input around the existing runner |
| Anti-rigidity evidence | selector and wrapper tests | `test_verification.py` | Prove precision, cleanup, and failure behavior |
| Roadmap browser fixture | current dynamic plan routes and honest missing states | `roadmap-review.e2e.ts` | Keep the newly selected real behavior check executable without weakening assertions |
| Operator reference | affected-verification guidance | control-plane README | Explain selection and prerequisites |
| Planning lineage | completed parent slice, packet, register | named planning files | Preserve a bounded descendant correction |

## Dependencies and Parallel Safety

WRK-0012 is complete. Correction route
`sha256:026c6c90a9f4a4d8bd91be1ff5727e819f6aa73442b5b4cda6e66b2f899ac10f`
confines implementation to the four control-plane paths. This packet is serial
with WRK-0066 verification because the corrected catalog must qualify that
candidate.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Web behavior | A web source or test changes | affected checks are selected | typecheck, lint, and Vitest are selected with exact matched paths | selector regression |
| Live boundary | Approved-lesson browser or runner behavior changes | affected checks are selected | live cross-system qualification is selected without unrelated aggregate readiness | selector regression |
| Narrow browser check | An unrelated mocked browser test changes | affected checks are selected | web checks run without Docker/live qualification | anti-rigidity regression |
| Isolated build lifecycle | The candidate has an existing, missing, file, symlink, junction, or concurrently changing worktree build path | composed qualification succeeds or fails | only the temporary snapshot receives generated output and the working tree remains untouched | wrapper safety regressions |
| Exact candidate | The controller runs selected checks | execution ends | Git remains at the submitted clean revision | fresh receipt/stability check |

## Verification Commands

Run the focused verification tests, control-plane lifecycle suite, planning and
documentation checks, diff hygiene, and aggregate readiness. Execute the
composed live check once with the repository's prepared Node 24/npm 10.8.2,
Python environment, Docker, and pinned Chromium. Submit, verify, and obtain one
independent technical review for the exact correction candidate.

## Stop Conditions

Stop for a generic verification-schema change, arbitrary command execution,
dependency installation, unbounded build deletion, product/test semantic
changes, a path outside the correction route, unresolved durable decision,
active edit collision, or material CAP-0002 drift.

## Required Handoff

Report selected/deferred path behavior, isolated build safety on success and
failure, exact live evidence, focused and aggregate results, receipt/review
disposition, changed paths, and confirmation that the product and generic
verification contracts did not change.

## Planning History

- 2026-10-16: Authored from the bounded completed-work correction route after
  WRK-0066 review found that changed browser and live-runner paths selected no
  behavior-exercising affected checks. The correction stays within CAP-0002's
  repository-adapter design and adds no approval or decision gate.
- 2026-10-16: R01 review required the live wrapper to select its own real
  qualification, complete first-class web-path classification, separate
  TypeScript/runtime/documentation impacts, and avoid unsafe mutation of the
  tracked static build tree. The correction uses an isolated candidate
  snapshot instead of a broader generated-output claim; these are bounded
  correctness and anti-rigidity refinements within the same routed adapter
  scope.
- 2026-10-16: R02 review and a real roadmap-mode probe found an invalid config
  path, a predictable collision with an open review site, and a stale dynamic
  roadmap expectation. The same bounded correction now runs roadmap Chromium
  from an isolated ephemeral-port snapshot and refreshes the fixture to assert
  one current governed capability, one refined slice, and one honestly
  unrefined declared slice.
- 2026-10-16: R03 review accepted the ephemeral-port and current-hierarchy
  corrections, then found that roadmap implementation paths still selected
  only structural qualification and that nested processes could bypass the
  explicitly selected runtime. The bounded repository adapter now selects
  server, typecheck, DOM-unit, and Chromium evidence by owning roadmap boundary
  and propagates the prepared Node directory and exact Python executable to
  child processes. Documentation-only and test-only routing stays narrow.
- 2026-10-16: R04 review accepted the complete path classification but found
  the separately selected roadmap server suite still bypassed the prepared
  runtime wrapper. The server check now enters through that wrapper, so its
  nested TypeScript compilation receives the same explicit Node path and exact
  Python executable as roadmap browser execution.
