---
id: WRK-0005
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-agent
updated: 2026-08-05
parent: SLI-0001
capability: CAP-0001
depends_on: ["WRK-0004"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/pyproject.toml", "backend/uv.lock", "backend/tests/architecture", "apps/web/package.json", "apps/web/package-lock.json", "apps/web/tests/browser", "tests/e2e/approved-lesson", "tests/architecture", "deployments/local", ".github/workflows/approved-lesson-slice.yml", "dev-tools/architecture", "dev-tools/security", "backend/README.md", "apps/web/README.md", "deployments/local/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/assurance/known-architecture-gaps.md", "docs/assurance/known-verification-gaps.md", "docs/architecture/deployment/local-open-source-profile.md", "docs/security/local-identity-architecture.md", "docs/architecture/contracts/content-package-contract.md", "docs/context/packs/architecture-contracts.pack.md", "docs/context/packs/security-risk.pack.md", "docs/context/packs/deployment-operations.pack.md", "docs/context/packs/interface-design.pack.md", "docs/context/packs/testing-quality.pack.md", "docs/context/pack-catalog.json"]
generated_artifacts: ["backend/uv.lock", "apps/web/package-lock.json"]
base_revision: a9503220007fedb9b67113a1b3f1e6e498fc6205
claim_id: WRK-0005:9b09f77b-6c55-4914-ac9b-d6563f377aea
claimed_by: codex-agent
claimed_at: 2026-08-05T02:58:15Z
---

# Agent Work Packet: Qualify the Approved-Lesson Vertical Slice

## Objective and Deliverable

Add the cross-boundary, architecture, security, browser-accessibility, static-runtime, and local-composition evidence needed to verify SLI-0001 as one complete read-only vertical slice. The observable deliverable is a reproducible local qualification path that starts PostgreSQL and the Python application, serves the WRK-0004 static web artifacts without a Node production server, admits the approved fixture, and proves the authorized learner success path plus the named denial and failure paths.

## Required Context

Before changing files, prominently read and follow every applicable `AGENTS.md` and repository-root `docs/README.md`. Route through the baseline pack with `testing-quality` as primary and `deployment-operations` as adjacent. Read SLI-0001 and WRK-0001 through WRK-0004 handoffs, ADR-0005 through ADR-0009, module dependency and contract rules, identity and content-package security authorities, local/cloud parity, local profile, education-versus-advice boundary, interface standards, testing standards, architecture verification, deployment READMEs, all affected executable contracts, application/build files, focused tests, and generated artifacts.

## Decisions and Assumptions

- This packet verifies and reconciles the already implemented slice; it does not move focused invariant tests out of their owning packets or redesign failed seams.
- The supported qualification target is the private-host community `single_profile` path with loopback-default exposure, PostgreSQL, local filesystem object storage, Python API/static serving, and the exact browser artifacts built under Node 24.
- Node is absent from the production runtime composition. The same Vite output that passed WRK-0004 is served same-origin by the Python application or a static-serving adapter owned by that composition.
- Test fixtures are synthetic, source-attributed, and contain no personal data, credentials, provider payloads, restricted datasets, or investment recommendations.
- Browser automation and accessibility tooling are pinned exact development dependencies. Automated accessibility supports but does not replace documented keyboard, zoom, forced-color, and assistive-technology qualification.
- Cloud operation, built-in/OIDC identity, backup/restore, external services, production publication, and RPO/RTO claims are not qualified.

## In Scope

- Cross-system success from configured single-profile bootstrap through package admission/placement, authenticated API, generated client, and browser rendering.
- Cross-boundary denial/failure scenarios for invalid context, stale version, malicious/invalid package, unsafe content, integrity conflict, persistence/storage failure, safe error mapping, and redaction.
- Architecture fitness functions for layer direction, module public surfaces, no cross-module persistence, generated-client-only browser access, no backend imports from web, and no Node production/server entry point.
- Static production build inspection and a reproducible local test composition with PostgreSQL, isolated filesystem data root, health/readiness, deterministic fixture seeding, and safe teardown instructions.
- Browser qualification across supported representative engines/viewports for light, dark, system, keyboard, focus, status announcements, responsive reflow, 200 percent zoom, reduced motion, forced colors, and external-source behavior.
- CI orchestration for focused contract/backend/API/web checks plus cross-system qualification where the environment supports containers and browsers.
- Evidence-map, known-gap, security, deployment, application README, and derived-context reconciliation based only on checks that directly pass.

## Out of Scope

- New product behavior, contract semantics, persistence ownership, API operations, UI features, design tokens/icons, or broad refactoring of earlier packets.
- Knowledge-check submission, attempts, scores, completion, learner projections, Audit delivery, workers, AI/ML, market data, portfolio tools, or advice-like content.
- Built-in credentials, OIDC, multiple learners, remote/public hosting, organization tenancy, managed cloud, production deployment, provider network access, or external publication.
- Backup/restore implementation or claims, data migration beyond the slice's tested empty-database migrations, high availability, RPO/RTO, monitoring service selection, or container registry publication.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Focused evidence | All earlier packet tests | Named backend/web test roots | Add only missing cross-boundary assertions near owning surfaces |
| Cross-system tests | API, client, UI, PostgreSQL, filesystem composition | `tests/e2e/approved-lesson/` | One complete learner success/failure flow |
| Architecture/security | Dependency rules and threat outcomes | Named test and dev-tool roots | Executable boundary, redaction, and runtime fitness functions |
| Local qualification | Local profile and deployment scaffold | `deployments/local/` | Reproducible test composition with no Node production server |
| CI | Existing readiness workflow | New `approved-lesson-slice.yml` only | Deterministic slice-specific checks without weakening existing gates |
| Documentation/context | Canonical assurance/security/deployment sources | Exact named documents and derived packs | Reconcile direct evidence and residual gaps |

## Contracts and Interfaces

The packet consumes all accepted outputs from WRK-0001 through WRK-0004 without changing their public meaning. The local qualification interface must expose documented commands for clean dependency installation, database startup/migration, fixture admission and placement, Python/API/static startup, browser test execution, shutdown, and data-root cleanup.

Cross-system test setup may use internal test-only fixture seeding but cannot add a production import or authoring contract. Failure injection must remain test-only. CI and architecture runners return nonzero on drift and print redacted actionable diagnostics.

## Dependencies and Parallel Safety

WRK-0004 and all of its predecessors must complete first. This packet intentionally touches shared manifests, browser tests, local composition, and assurance sources, so it has no parallel-safe peer. If qualification reveals a focused defect, return the owning packet to the appropriate lifecycle state rather than silently redesigning that seam inside this packet.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete success path | A clean local composition and approved fixture | The learner opens the configured placement | Browser displays objectives, safe body, sources, version/digest, and provenance through every accepted boundary | Cross-system browser test |
| Unauthorized context | Session is absent, tampered, expired, or revoked | Lesson route/API is requested | Access fails closed, UI is bounded, and no package internals or learner evidence appears | API plus browser denial test |
| Exact-version failure | Placement points to missing/stale version | The learner opens it | No `latest` substitution occurs and unavailable UI is safe | End-to-end stale-version test |
| Malicious package | Traversal, active markup, unsafe link, undeclared asset, oversized input, or integrity mismatch is seeded | Admission is attempted | Package remains invisible and diagnostics are bounded/redacted | Contract-to-application failure test |
| Immutable conflict | Conflicting bytes reuse package identity/version | Admission runs | Existing lesson remains intact and conflict reaches no learner-visible partial state | Persistence/object integration test |
| Infrastructure failure | PostgreSQL or filesystem fails during admission/read | The flow runs | No partial publication appears; API/UI show safe bounded failure | Controlled failure-injection test |
| Theme/accessibility matrix | Success and failure states run in supported themes/viewports/settings | Automated and manual qualification runs | Equivalent content/actions and required keyboard/focus/reflow/status behavior pass | Browser report plus manual evidence |
| Static production boundary | Clean web artifacts are built and local composition starts | Runtime processes/images are inspected | Python and PostgreSQL/filesystem are present; no Node application server, SSR, BFF, or server action exists | Build/composition inspection |
| Architecture boundaries | The completed repository is scanned | Fitness functions run | Forbidden imports, cross-module persistence, handwritten API models, generated drift, and unaccepted server entries fail the build | Architecture runner |
| Educational claim boundary | The approved lesson and UI copy are reviewed | Browser assertions run | Sources remain visible and no mastery, certification, suitability, performance, or buy/sell/hold claim appears | Content fixture and UI assertion |

## Verification Commands

```powershell
uv sync --project backend --frozen
uv run --project backend pytest backend/tests
npm --prefix apps/web ci
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web test -- --run
npm --prefix apps/web run build
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python tests/e2e/approved-lesson/run.py
python dev-tools/design/check_design_system.py
python dev-tools/documentation/check_docs.py
python dev-tools/planning/check_planning.py
python dev-tools/agent/check_ready.py
git diff --check
```

The handoff must identify container, browser-engine, operating-system, manual assistive-technology, dependency-advisory, and external qualification that was not performed. CI cannot silently skip a required slice job after its prerequisites are available.

## Documentation and Evidence Update

Update the architecture verification map and known gaps at invariant granularity: direct only for checks that own the claim, representative when evidence is partial, and gap otherwise. Update local deployment, identity security, content-package, backend/web/deployment READMEs, and derived context only when executable behavior makes them stale. Do not claim cloud parity beyond provider-neutral contract semantics or claim backup/recovery support.

SLI-0001 moves to `verifying` only after all implementation packets have completed their authorized work and the required evidence is being gathered. Completion still requires the separate verification workflow and explicit completion acceptance.

## Stop Conditions

- A cross-system failure requires changing accepted product, architecture, contract, identity, security, risk, design, or compatibility meaning.
- A focused seam lacks its owning tests or handoff, or generated artifacts do not reproduce.
- Qualification would require public/remote exposure, credentials, provider access, destructive cleanup outside the isolated test root, backup/restore claims, or production publication.
- Node is required as a production server or local/cloud meaning diverges.
- Accessibility, redaction, fail-closed behavior, immutable versioning, or educational-claim boundaries cannot be proven.
- A check would be weakened, skipped, or reclassified merely to claim completion; canonical sources conflict; or active scope overlaps.

## Required Handoff

Report the exact local topology, clean-start and teardown commands, contract/application/API/client/browser path, architecture and security runner results, browser/theme/accessibility matrix, dependency/build inspection, documentation and evidence classifications, raw and normalized failures, unperformed external qualification, residual risks, and whether SLI-0001 is ready for the separate completion-verification workflow.

## Completion Evidence

- The reproducible local topology is pinned Chromium over one loopback origin
  served by a CPython 3.14/FastAPI 0.141/Uvicorn 0.41 process. That process
  serves the exact Vite build and generated-client API, composes
  `single_profile` Identity plus public Content/Curriculum operations, stores
  transactional metadata in PostgreSQL 18.4, and stores package objects below
  one isolated filesystem root. No Node application server, SSR, BFF, server
  action, or framework server entry is present.
- `deployments/local/serve.py` rejects non-loopback hosts, applies empty
  Content/Curriculum/Identity migrations, emits CSP, no-sniff, frame, referrer,
  correlation, and no-store controls, serves static assets and SPA fallback on
  the API origin, and seeds only the committed synthetic approved fixture when
  explicitly requested. `deployments/local/README.md` records clean install,
  startup, inspection, shutdown, exact compose teardown, data-root caution,
  and the limits of the qualification.
- `npm --prefix apps/web run dev:full` now invokes one cross-shell Node
  orchestrator from Git Bash or PowerShell. It validates the pinned machine
  runtimes, installs uv 0.11.29 only in ignored `.local-codex`, restores both
  committed locks, installs pinned Chromium, assigns a unique Compose project
  and unused PostgreSQL port, executes the full qualification sequence,
  recreates a clean database, and starts the loopback Python API plus Vite
  hot-reload client. Ctrl+C terminates the owned process trees and removes only
  the runner's uniquely named database and synthetic data root.
- The new runner's `--verify-only` qualification passed all 105 backend,
  OpenAPI, generated-client, type, lint, 18 Vitest, build, 6 focused Chromium,
  2 live Chromium, 7 architecture, 10 security, design, documentation,
  planning, 10-check readiness, npm-advisory, and Git whitespace gates. Its
  separate `--skip-checks --smoke-start` path reached both
  `http://127.0.0.1:8000/ready` and the Vite application at
  `http://127.0.0.1:5173`, then left no runner-owned container or data root.
- `tests/e2e/approved-lesson/run.py` selects unused loopback ports, creates a
  unique `postgres:18.4` container with ephemeral storage, creates an ignored
  isolated filesystem root, starts the Python process, runs the live browser
  path, and validates exact-name/path bounds before cleanup. Its final run
  reported Python as the application process, same-origin static serving, the
  `intro-risk-return@1.0.0` fixture, and static `index.html` SHA-256
  `BA7020C5E4953C33A5ABDD513FC2424969EA0E23506EA02F5C34D2FE37B89896`.
- The live Chromium suite passed 2 scenarios: complete package admission,
  placement, session bootstrap, reviewed API/generated client, title,
  objectives, constrained body, HTTPS sources, exact version/digest,
  provenance, education-only notice, opaque HttpOnly `SameSite=Strict` cookie,
  security headers, and zero axe violations; plus missing-context denial and
  missing-placement refusal without lesson internals or `latest` substitution.
- The full backend suite passed 105 tests against CPython 3.14.3 and a real
  disposable PostgreSQL 18.4 server: 6 module architecture, 29 lesson-package
  contract, 6 API/Identity integration, 5 PostgreSQL/filesystem integration,
  and 59 focused Content/Curriculum/Identity unit tests. It directly exercises
  malicious packages, immutable conflicts, corrupt objects, database failure,
  stale versions, session denial/expiry/revocation, boundary enforcement,
  OpenAPI stability, and sentinel redaction.
- A clean Node 24.14/npm 10.8.2 install passed generated-client drift,
  TypeScript, oxlint, 18 Vitest unit/component/contract tests, the 6-scenario
  focused Playwright Chromium matrix, and the static Vite build. The focused
  matrix explicitly scans light, dark, and system modes with axe and covers
  keyboard/focus, source-link safety, responsive and 200-percent-equivalent
  reflow, reduced motion, forced colors, loading/denial, and unknown-node
  failure. Revised visual-baseline SHA-256 values are
  `24BECD386E9599065201E008A81F8796F45DA5480D68966B99517114F24272BC`
  (light) and
  `F4D23288110B3B943471AE74B9665C6A1AAEC86BC5F78DA5DF678A877BC0C4A2`
  (dark).
- The clean static build transformed 97 modules into `index.html`, one reviewed
  SVG sprite, CSS, JavaScript, and a source map only. The corresponding hashes
  are `E957891B4C9E02B50D575553C8CBAAFEBFABBDCB4160236469E9EBF7D03FAF40`
  (SVG), `8587F070A02294E23CC4A4D68A6BC379EB64568D1A1032AA1F134F59CCBD584C`
  (CSS), `048D2059E8D21659AD9AA9DD7B5AF8F42C28CE94AB2A4E79B93555E12153979F`
  (JavaScript), and
  `1BA6FF55142EE5408A76794D54220041FB2CCFF71FC886355890CB9F614DE146`
  (source map). Architecture fitness functions passed 7 cross-boundary rules;
  security checks passed 10 control groups.
- The Python lock SHA-256 is
  `30E37AD78559A2134946E2EC85982BCB2657770B25FCD127EDAC8D8AFED8A179`;
  the npm lock remains
  `FBC50B9DA87CA62BE69E092284C26E04A8BDDA59A75A99A8AF6B1EEFDB138374`.
  npm audit and a pip-audit scan of the exact runtime export found zero known
  vulnerabilities. Uvicorn 0.41.0 and its new Click 8.4.2 dependency both
  declare BSD-3-Clause; the previously reviewed npm license inventory is
  unchanged because no JavaScript dependency changed.
- `approved-lesson-slice.yml` deterministically composes exact Python/Node
  setup, PostgreSQL service health, backend/OpenAPI/client checks, static build,
  focused and live Chromium tests, architecture/security/advisory checks, and
  documentation/planning/design/readiness gates. Its YAML parsed locally and
  has SHA-256
  `ED3DBF0E0C06AEDB4CB9212EB5FF9A80982175E73B2D3D0128F8C55D24319FD8`;
  execution by the external GitHub Actions service is not claimed.
- The architecture map now classifies the exact local approved-lesson
  composition as direct, shared local/cloud artifact meaning as representative,
  and unimplemented managed-cloud and broader-module evidence as gaps.
  Canonical local deployment, lesson-package, and `single_profile` security
  sources plus derived architecture/security/deployment/interface/testing
  packs were reconciled without extending claims to other identity or storage
  adapters.
- Raw qualification failures were retained as engineering evidence. PostgreSQL
  18 initially rejected a legacy tmpfs mount path; the runner and compose file
  now use the PostgreSQL-18 layout and clean up partial starts. Live selectors
  initially matched duplicate semantic title/source occurrences; they now
  scope to the exact page title and labeled sources region. Most importantly,
  live axe found a 4.21:1 light-theme contrast defect that mock-system-dark
  evidence had missed. WRK-0005 returned to ready, WRK-0004 reopened inside its
  approved scope, reused the existing secondary-text token, added explicit
  light/dark axe regression scans, regenerated both baselines, and re-completed
  before WRK-0005 resumed.
- The one-command verification also exposed a Windows `shell=False` handoff:
  Python could not invoke `npm.cmd` by basename. The orchestrator now passes
  the exact Node executable and npm CLI already used by the parent process to
  the live runner. Temporary-log cleanup retries bounded Windows handle
  release for five seconds; the corrected full run and exact teardown passed.
- `npm --prefix apps/web run setup:dev` now provides the identical Git Bash
  and PowerShell entry point above the qualified runner. Its first setup-only
  execution installed fnm 1.39.0 through the exact `Schniz.fnm` WinGet
  package, installed Node 24.14.0 under fnm, installed npm 10.8.2 below
  ignored `.local-codex`, and verified that npm through the selected Node
  executable. A second setup-only execution was idempotent and performed no
  installation. Neither path changed the system Node/npm installation or a
  shell profile.
- The new wrapper's full `--verify-only` handoff passed 105 backend tests,
  reviewed OpenAPI and generated-client drift, TypeScript, lint, 18 Vitest
  tests, the static build, 6 focused Chromium scenarios, 2 live Chromium
  scenarios, 8 architecture rules, 10 security control groups, design,
  documentation, planning, 10-check readiness, npm audit, and Git whitespace.
  A separate `--skip-checks --smoke-start` run reached both loopback servers
  and removed its uniquely named PostgreSQL composition and synthetic data
  root.
- The bootstrap qualification retained its raw failures. Windows fnm could not
  launch the extensionless npm shim, and a user-level npm global prefix
  redirected a global pin outside the selected runtime. The final bootstrap
  invokes an exact project-local npm CLI with fnm's Node executable, avoiding
  both shell resolution and global-prefix behavior. Docker also rejected one
  OS-reported free port; bounded disposable-PostgreSQL retries were added, and
  the following full qualification and smoke start passed with exact cleanup.
- Controlled manual screen-reader use, actual browser zoom controls,
  non-Chromium engines, non-Windows visual baselines, supported-platform
  permission profiles, passive-asset delivery, built-in/OIDC identity,
  backup/restore, complete local distribution, remote/public operation,
  managed cloud, CI-host execution, and external publication were not
  performed. No recovery, availability, RPO/RTO, cloud-parity, production, or
  personalized-financial-advice claim is made.

## Planning History

- 2026-08-04: Shaped from SLI-0001 boundary seam 7; planning approval, implementation activation, and completion acceptance remain separate local-only stages.
- 2026-08-05: Added the isolated PostgreSQL/Python/static-client composition, live browser qualification, architecture/security runners, deterministic CI workflow, dependency/advisory evidence, and reconciled documentation. Focused accessibility remediation was routed back through WRK-0004 before aggregate qualification resumed.
- 2026-08-05: Reopened within the existing write scope to add a cross-shell, one-command development bootstrap and qualification runner before slice completion review.
- 2026-08-05: Added and directly qualified the cross-shell npm runner, API-only loopback development composition, exact process/database/data cleanup, and Windows Node/npm subprocess handoff.
- 2026-08-05: Reopened within the existing scope to add an fnm-managed Node/npm bootstrap in front of the cross-shell development runner.
- 2026-08-05: Added and directly qualified the idempotent fnm/Node/project-local npm bootstrap, bounded Windows Docker port retry, complete check handoff, development smoke start, and exact cleanup.
