---
id: WRK-0067
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-control-plane-correction
updated: 2026-10-16
parent: SLI-0004
capability: CAP-0002
depends_on: ["WRK-0012"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/README.md", "dev-tools/control-plane/check_approved_lesson.py", "dev-tools/control-plane/financial_academy_checks.py", "dev-tools/control-plane/test_verification.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0004-select-affected-checks-and-record-receipts.md", "docs/planning/work-packets/WRK-0067-cover-web-and-live-affected-verification.md"]
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
runs the existing live PostgreSQL/Python/Chromium qualification, and restores
the candidate's tracked build tree before the controller rechecks Git
stability.

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
- Static build restoration is mandatory on success, failure, and interruption;
  the exact-candidate post-run stability check remains authoritative.

## In Scope

- Map changed web source/tests to typecheck, lint, and Vitest checks.
- Map changed approved-lesson browser/runner inputs to the existing live
  qualification and aggregate readiness checks.
- Add a bounded build/live/restore wrapper with deterministic tests for
  absent/present build trees and failing subprocesses.
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
| Live boundary | Approved-lesson browser or runner behavior changes | affected checks are selected | live cross-system qualification and aggregate readiness are selected | selector regression |
| Narrow browser check | An unrelated mocked browser test changes | affected checks are selected | web checks run without Docker/live qualification | anti-rigidity regression |
| Static build lifecycle | Existing tracked build bytes are present | composed qualification succeeds or fails | the original tree is restored byte-for-byte | wrapper unit regression |
| Missing build lifecycle | No static build exists | composed qualification runs | generated output is removed afterward | wrapper unit regression |
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

Report selected/deferred path behavior, build restoration on success and
failure, exact live evidence, focused and aggregate results, receipt/review
disposition, changed paths, and confirmation that the product and generic
verification contracts did not change.

## Planning History

- 2026-10-16: Authored from the bounded completed-work correction route after
  WRK-0066 review found that changed browser and live-runner paths selected no
  behavior-exercising affected checks. The correction stays within CAP-0002's
  repository-adapter design and adds no approval or decision gate.
