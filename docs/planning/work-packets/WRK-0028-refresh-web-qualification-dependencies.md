---
id: WRK-0028
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0001
capability: CAP-0001
depends_on: ["WRK-0005"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/package.json", "apps/web/package-lock.json", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0001-open-approved-versioned-lesson.md", "docs/planning/work-packets/WRK-0028-refresh-web-qualification-dependencies.md"]
generated_artifacts: ["apps/web/package-lock.json", "apps/web/node_modules/.package-lock.json", "apps/web/node_modules/.vite/deps/_metadata.json", "apps/web/node_modules/@jridgewell/sourcemap-codec", "apps/web/node_modules/@vitest/expect", "apps/web/node_modules/@vitest/mocker", "apps/web/node_modules/@vitest/pretty-format", "apps/web/node_modules/@vitest/runner", "apps/web/node_modules/@vitest/snapshot", "apps/web/node_modules/@vitest/spy", "apps/web/node_modules/@vitest/utils", "apps/web/node_modules/chai", "apps/web/node_modules/nanoid", "apps/web/node_modules/source-map-js", "apps/web/node_modules/tinyrainbow", "apps/web/node_modules/undici", "apps/web/node_modules/vitest"]
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0028:edc764f0-9a8b-4b1d-bbc6-d27961725173
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T16:00:22Z
---

# Agent Work Packet: Refresh Web Qualification Dependencies

## Objective and Deliverable

Restore the approved-lesson qualification gate after current advisory data
identified vulnerable locked development dependencies. The observable
deliverable is a minimally updated, reproducible web dependency graph that
retains the accepted Node 24, TypeScript 7, Vite 8, React 19, React Router 8,
static-client, and Python production-runtime boundaries while producing no
high-severity npm audit finding and preserving every SLI-0001 check.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Route through the baseline context pack with
`testing-quality` as primary and `security-risk` as adjacent. Read CAP-0001,
SLI-0001, WRK-0005, ADR-0009, the dependency/build row of the change-impact
matrix, the web and local-deployment READMEs, the exact package manifest and
lock, the npm audit report, and the affected unit, component, browser, build,
architecture, security, and live-qualification consumers.

## Decisions and Assumptions

- ADR-0009 continues to fix the runtime and framework families. Compatible
  patch-level dependency updates are implementation detail when they preserve
  those families and public behavior.
- The advisory failure is a bounded defect found while closing SLI-0001. It
  does not change the CAP outcome, slice manifest, identity mode, deployment
  claim, public contract, or risk posture.
- Registry advisory metadata and the committed lock determine the exact
  vulnerable paths. Automated `--force` upgrades and unrelated dependency
  refreshes are not authorized.
- Tracked installed-package artifacts are regenerated only for the exact
  affected packages already present in the repository; this packet does not
  decide the repository-wide vendoring policy.

## In Scope

- Move Vitest to the smallest compatible fixed patch and resolve fixed
  transitive versions for `@vitest/mocker`, `nanoid`, `source-map-js`, and
  `undici`.
- Regenerate the npm lock with the pinned Node 24.14.0/npm 10.8.2 toolchain.
- Reproduce the exact installed graph and retain only affected generated
  package artifacts.
- Run advisory, type, lint, unit/component, browser, build, architecture,
  security, documentation, planning, live PostgreSQL/browser, and aggregate
  readiness checks required to close SLI-0001.
- Record exact correction and closure evidence in this packet, SLI-0001, and
  the planning register.

## Out of Scope

- Framework-family or production-runtime changes, new dependencies, public API
  changes, feature behavior, UI redesign, broad lock refresh, or automated
  `npm audit fix --force`.
- A repository-wide decision to vendor or stop tracking installed dependency
  trees.
- Docker Desktop installation policy, production deployment, cloud
  qualification, publication, or changes to any learner-data semantics.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Web dependency contract | `apps/web/package.json`, `apps/web/package-lock.json` | Exact fixed versions and resolved lock entries | Remove the advisory paths without changing framework families |
| Installed generated graph | Exact affected package directories and npm metadata | Paths listed in `generated_artifacts` only | Keep the tracked installed graph consistent with the lock |
| Consumers | Web tests, Vite config, browser configs, generated API client | No behavior changes expected | Prove compatibility rather than redesign consumers |
| Qualification | `deployments/local`, `tests/e2e/approved-lesson`, security and architecture checks | No implementation changes expected | Re-run the complete accepted evidence path |
| Planning evidence | This packet, SLI-0001, planning register | Lifecycle and exact results | Preserve governed correction and closure evidence |

## Contracts and Interfaces

This packet consumes WRK-0005's exact Node/npm toolchain and complete
qualification path. It changes no public schema, OpenAPI operation, generated
client shape, application interface, database migration, event, or browser
route. Its output is a compatible locked development graph and fresh evidence
for the existing SLI-0001 acceptance contract.

## Dependencies and Parallel Safety

WRK-0005 is complete and supplied the failing advisory gate. This correction
is serial because it changes the shared web manifest, lock, installed graph,
and slice closure evidence. It has no parallel-safe peer.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Fixed locked graph | Current advisory data identifies the five vulnerable paths | The smallest compatible versions are resolved under the pinned toolchain | `npm ci` reproduces and `npm audit --audit-level=high` reports no high finding | Manifest/lock diff, install, audit |
| No forced drift | A fixed version would require a framework-family, runtime, or unrelated major change | Resolution is evaluated | The packet stops rather than using `--force` or broadening CAP-0001 | Diff review and stop-condition evidence |
| Existing behavior | The corrected graph is installed | Focused and complete checks run | Types, lint, unit/component, Chromium, build, generated-client, live API/database/browser, architecture, security, docs, planning, and readiness remain green | Exact command outputs |
| Safe failure evidence | Current registry metadata is unavailable or still reports a high advisory | Qualification runs | Closure remains blocked with the exact remaining dependency path reported | Audit result and packet state |

## Verification Commands

```powershell
npm --prefix apps/web ci
npm --prefix apps/web audit --audit-level=high
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web test -- --run
npm --prefix apps/web run build
npm --prefix apps/web run test:browser -- apps/web/tests/browser/lesson-reading
npm --prefix apps/web run setup:dev -- --verify-only
python dev-tools/planning/check_planning.py
python dev-tools/agent/check_ready.py
git diff --check
```

Review the dependency diff and resolved tree explicitly. The complete
`setup:dev -- --verify-only` path owns real PostgreSQL, live browser,
architecture, security, design, documentation, planning, advisory, and cleanup
evidence.

## Documentation and Evidence Update

No canonical product, domain, architecture, contract, security, or interface
meaning changes. Update SLI-0001 and the planning register with lifecycle and
exact verification evidence. Update a canonical or derived source only if the
resolved dependency graph changes a documented boundary; otherwise record no
documentation impact.

## Stop Conditions

- A fixed graph requires a new runtime/framework family, production Node
  server, public contract change, or `--force` upgrade.
- Advisory resolution requires a package with incompatible provenance,
  licensing, runtime support, or unreviewed external behavior.
- Existing application, browser, architecture, security, or live qualification
  behavior regresses without a bounded local fix.
- The change expands beyond the exact manifest, lock, affected generated
  packages, or planning evidence paths.
- Canonical sources conflict, an unresolved durable decision appears, or
  another active packet owns an overlapping path.

## Required Handoff

Report the exact version changes and dependency paths, audit result, all
focused and cumulative check results, public-contract and runtime impact,
documentation impact, generated files retained, residual risks, and the next
SLI-0001 closure action.

## Verification Progress

- The lock resolves Vitest and the `@vitest/*` family at `4.1.12`, nanoid at
  `3.3.18`, source-map-js at `1.2.2`, and undici at `7.29.1` under Node
  `24.14.0` and npm `10.8.2`. Ordinary `npm ci` reproduced the graph.
- Current registry audit data reported zero vulnerabilities. TypeScript,
  oxlint, 18 Vitest tests, the 97-module static build, and 6 focused Chromium
  scenarios passed.
- The complete local qualification passed 105 backend tests, OpenAPI and
  generated-client currency, 18 web tests, 6 focused and 2 live Chromium
  scenarios, real PostgreSQL 18.4/filesystem integration, 8 architecture
  functions, 10 security groups, design-system validation, documentation, and
  planning integrity.
- Aggregate readiness then reproduced a file-lease process-race defect owned by
  completed SLI-0012: exactly one acquisition succeeded, but the loser was not
  deterministically classified as `edit.lease-contended`. The unchanged
  focused suite passed once and then failed on stress iteration 18 of 25. This
  packet remains `verifying` while the bounded owning-slice correction runs;
  no web, lesson, public-contract, runtime-family, or CAP-0001 behavior failed.
- After WRK-0029 corrected and qualified that separately owned race, the full
  `setup:dev -- --verify-only` path passed without exception. It restored the
  exact locks, reported zero npm vulnerabilities, repeated all product and
  live checks, passed all 27 aggregate-readiness checks, and removed the exact
  disposable PostgreSQL container/network. The retained installed-tree diff is
  limited to npm metadata, Vite metadata, the patched packages, and the
  compatible Vitest transitive packages named in `generated_artifacts`.

## Planning History

- 2026-10-15: Created as the bounded descendant correction routed from
  WRK-0005 after current advisory metadata blocked SLI-0001 closure.
- 2026-10-15: Deterministic packet validation passed; the correction is ready
  for a bounded claim under the current CAP-0001 package.
- 2026-10-15: Dependency and product qualification passed; the packet moved to
  `verifying` after aggregate readiness exposed a reproducible, separately
  owned control-plane race-classification defect.
- 2026-10-15: Fresh full qualification passed after WRK-0029; exact generated
  artifacts and zero-advisory evidence were reconciled for deterministic
  completion.
