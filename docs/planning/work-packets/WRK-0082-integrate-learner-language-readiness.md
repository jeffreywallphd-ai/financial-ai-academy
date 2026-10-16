---
id: WRK-0082
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: SLI-0125
capability: CAP-0030
depends_on: ["WRK-0079"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/agent/README.md", "dev-tools/agent/check_ready.py", "dev-tools/agent/test_check_ready.py", "dev-tools/control-plane/financial_academy_checks.py", "dev-tools/control-plane/test_verification.py", "dev-tools/learner-language/README.md", "docs/assurance/architecture-verification.md", "docs/planning/work-packets/WRK-0082-integrate-learner-language-readiness.md", "docs/planning/vertical-slices/SLI-0125-sustain-plain-language-interface-quality.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: b95fbc41dc0f23aa33b6348d4f836e1ca84bf1b4
claim_id: WRK-0082:9c3f2f14-5045-4361-bbb3-c426c79e6d7f
claimed_by: codex-plain-language-ui
claimed_at: 2026-10-16T11:42:56Z
---

# Agent Work Packet: Integrate Learner-Language Readiness

## Objective and Deliverable

Integrate the completed diff-aware learner-language checker into the fixed
agent-readiness allowlist and affected-check catalog. The readiness runner must
forward an optional base revision, the affected catalog must select the
language check only for owned learner-facing TSX or the checker itself, and
focused tests must prove that advisory text, whitespace, CSS, and unrelated
technical changes do not turn the control into a broad delivery gate.

The observable result is one privacy-minimized readiness check that runs in
local and CI profiles, plus a focused affected check that can qualify a changed
learner-facing source without selecting aggregate readiness merely because UI
copy changed.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository
root `docs/README.md`. Route through the baseline, delivery-planning,
testing-quality, and interface-design packs. Read CAP-0030, SLI-0125, WRK-0079,
the user-facing language and testing standards, content style guide, change-
impact matrix, decision-readiness register, concurrent-work guidance, agent-
readiness and learner-language READMEs, the readiness runner, affected-check
catalog, selection tests, and checker tests.

## Decisions and Assumptions

- WRK-0079's CLI and exit contract are the accepted input: changed scope by
  default, optional exact `--base-ref`, advisory-only success, and `--all` only
  for controlled direct qualification.
- Agent readiness remains a fixed repository-owned allowlist. It forwards the
  same base revision used for lifecycle validation and never invokes `--all`.
- The affected catalog uses tracked path patterns and a fixed command; it does
  not inspect prose, infer intent, or execute repository-provided commands.
- No public contract, application runtime, UI copy, design token, browser
  behavior, dependency, provider, or external service changes.

## In Scope

- Add the changed-copy learner-language command to fixed readiness for local
  and CI profiles, forwarding `--base-ref` when supplied.
- Add direct readiness-runner tests for command presence, base forwarding,
  local no-base behavior, profile parity, and absence of `--all`.
- Add a `learner-language:changed` affected-check definition for the checker,
  configuration, direct tests, and owned TSX source.
- Add catalog tests proving owned TSX selection and non-selection for CSS,
  whitespace-only scope represented by non-TSX paths, generated source,
  fixtures, documentation, and unrelated implementation.
- Reconcile tool, readiness, assurance, slice, packet, and register evidence;
  run controlled full-scope qualification and aggregate readiness.

## Out of Scope

Application copy or behavior; CSS, styling, tokens, icons, screenshots, browser
or backend changes; automatic rewriting; external grammar or AI services;
repository-wide prose checking; making advisories blocking; adding CI workflow
steps outside the existing readiness entry point; or introducing any new
approval, review, deployment, publication, or migration gate.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Checker contract | learner-language CLI, rules, tests, README | README only | Document aggregate and affected-check consumers |
| Aggregate readiness | runner, README, CI consumer | runner, focused runner test, README | Add fixed check and base-ref forwarding |
| Affected verification | catalog, path matcher, selection tests | catalog and selection tests | Select the narrow check deterministically |
| Assurance | architecture verification map | architecture verification map | Record direct sustained-language evidence |
| Planning | CAP-0030, SLI-0125, WRK-0079, register | this packet, parent slice, register | Keep lifecycle and evidence synchronized |

## Contracts and Interfaces

The readiness check is named `learner-language quality` and invokes
`check_learner_language.py` with no full-scope flag. When readiness receives
`--base-ref <revision>`, it appends the exact pair to the learner-language
command. Machine readiness output retains only the existing command result
hashes, sizes, status, and duration.

The affected-check catalog adds `learner-language:changed` with a fixed Python
command and low risk. Its paths cover `dev-tools/learner-language/**` and owned
non-generated application TSX source. CSS, tests/fixtures, generated clients,
documentation, and unrelated code must not match this definition. The catalog
remains selection authority only, not approval or proof of copy semantics.

## Dependencies and Parallel Safety

WRK-0079 is complete and defines the consumed CLI. This packet is the final
dependency-ordered seam in SLI-0125 and is not parallel-safe because it edits
shared readiness, affected-check, planning, and assurance surfaces. Exact-file
lease acquisition is required before implementation.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Local readiness | No base revision is supplied | Checks are constructed | Learner-language runs changed scope without `--all` | runner unit test |
| CI/base readiness | A base revision is supplied | Checks are constructed | The exact base is forwarded to planning and learner-language checks | runner unit test |
| Owned UI copy | An application feature TSX path changes | Affected selection runs | `learner-language:changed` is selected without `agent:readiness` | catalog test |
| Styling-only change | Only CSS changes | Affected selection runs | The learner-language check is not selected | anti-rigidity catalog test |
| Technical/excluded change | Generated client, test fixture, docs, or unrelated Python changes | Affected selection runs | The learner-language check is not selected | exclusion catalog test |
| Advisory-only copy | The checker reports only advisories | Readiness runs | The check passes and does not escalate evidence | existing checker test plus readiness result |
| Full qualification | Maintainer explicitly checks all owned source | Direct checker runs with `--all` | Full scope passes independently of everyday readiness | direct CLI evidence |

## Verification Commands

- `python dev-tools/agent/test_check_ready.py`
- `python dev-tools/learner-language/test_learner_language.py`
- `python dev-tools/control-plane/test_verification.py`
- `python dev-tools/learner-language/check_learner_language.py --all`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/agent/check_ready.py --base-ref <packet-base-revision>`
- `python -m compileall -q dev-tools/agent dev-tools/control-plane dev-tools/learner-language`
- `git diff --check`

No browser, backend, database, Docker, deployment, or external qualification is
required because this packet changes only development controls and evidence
routing.

## Documentation and Evidence Update

Keep the readiness and learner-language READMEs, architecture-verification map,
SLI-0125, this packet, and the planning register synchronized. Record exact
focused, controlled-full-scope, aggregate, compilation, documentation, design,
and whitespace results without copying local approval or reviewer metadata into
tracked files.

## Stop Conditions

Stop for a conflicting checker contract, a base revision that cannot be
forwarded deterministically, affected patterns that require prose inference,
advisories changing an exit code, generated/test/CSS/documentation paths
selecting the language check, a new dependency or external service, active file
overlap, an unresolved durable decision, or material CAP-0030 drift.

Do not stop, request approval, or create another review cycle for whitespace,
advisory language, or nonfunctional visual styling. Leave optional polish
unchanged or route it to CAP-0031.

## Required Handoff

Report readiness command and base-ref behavior, affected path selection and
exclusions, anti-rigidity evidence, exact checks and results, documentation
impact, assumptions, residual lexical-check limitations, and confirmation that
runtime product, contracts, generated clients, CSS, browser behavior, external
services, and dependencies did not change. Then close SLI-0125 and CAP-0030 if
all approved acceptance criteria remain satisfied.

## Implementation Evidence

- Fixed readiness now runs its focused catalog test and the changed-copy
  learner-language check in local and CI profiles. An exact base revision is
  forwarded to both planning lifecycle validation and learner-language
  selection; everyday readiness never supplies `--all`.
- Affected-check catalog v4 selects `learner-language:changed` for the checker,
  rule configuration, and owned app/component/feature TSX only. Tests prove
  CSS, generated clients, UI fixtures, documentation, and unrelated control-
  plane source do not select it or aggregate readiness.
- All 3 readiness-catalog tests, 14 checker tests, and 22 affected-verification
  tests pass; 2 platform-capability cases are skipped as designed. Controlled
  full scope inspected 269 visible regions in 12 files with zero blocking and
  zero advisory findings.
- Planning validated 160 artifacts, documentation validated 303 Markdown files
  plus catalogs, design validation checked 125 tokens and 56 icons, Python
  compilation and Git whitespace passed, and all 29 aggregate readiness checks
  passed against the packet base.
- Initial focused attempts using the OS sandbox temporary directory failed on
  Windows permissions. The same tests passed in the repository-owned prepared
  temporary root; no source correction or broader rerun was required for that
  environment-only failure.
- No runtime application source, public contract, generated client, CSS,
  browser behavior, dependency, backend, database, Docker, or external service
  changed. The checker remains deliberately lexical and human review retains
  responsibility for meaning, financial nuance, comprehension, and tone.

## Planning History

- 2026-10-16: Authored just in time as SLI-0125 JIT-B after WRK-0079 completed.
  The packet consumes the stable changed-copy CLI, adds bounded readiness and
  affected-selection integration, and qualifies the slice without expanding
  CAP-0030 or adding a lower-level approval gate.
- 2026-10-16: Activated from base
  `b95fbc41dc0f23aa33b6348d4f836e1ca84bf1b4` after the implementation gate
  prerequisites confirmed current CAP authority, completed dependencies,
  bounded scope, and no active file overlap.
- 2026-10-16: Implemented fixed readiness and affected-check integration,
  exact base-ref forwarding, direct runner tests, excluded-path tests, and
  documentation. Focused, controlled full-scope, planning, documentation,
  design, compilation, whitespace, and aggregate readiness evidence passed;
  the packet is ready for exact-candidate verification and one independent
  technical disposition.
- 2026-10-16: Submitted the bounded implementation candidate after its focused
  and aggregate evidence passed. The packet is verifying against the complete
  ten-file scope declared at activation.
