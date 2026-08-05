---
id: SLI-0001
kind: vertical-slice
planning_status: verifying
authority: noncanonical
owner: codex-agent
updated: 2026-08-05
parent: CAP-0001
depends_on: []
decision_gates: []
---

# Vertical Slice: Open an Approved Versioned Lesson

## Outcome and User Scenario

An individual learner using a private-host community installation in explicitly configured `single_profile` mode can open one approved introductory lesson and read its objectives, constrained lesson body, educational sources, package version, and provenance through the learner-facing web application.

The learner receives useful educational content through the first complete read path from a validated platform-owned package to the browser. The experience does not collect assessment responses, record learner evidence, calculate completion, claim mastery, or provide personalized financial advice.

## Scope Boundaries

### In Scope

- One reviewed introductory lesson package admitted through the ADR-0007 validation boundary.
- Exact version 1 manifest, source, content, passive-asset, and package-integrity schemas and fixtures needed by this slice.
- Stable package identity, semantic version, deterministic digest, educational-source provenance, immutable publication state, and exact-version resolution.
- One minimal Curriculum placement that references the exact approved Content package version without reading Content persistence.
- A public Content/Curriculum application query, authenticated API operation, reviewed OpenAPI snapshot, and generated TypeScript client for opening the exact lesson.
- A local filesystem object-storage adapter and the minimum transactional metadata needed to identify the approved package and placement.
- Explicitly configured local `single_profile` identity resolution through the provider-neutral learner-context contract; missing, malformed, or unsupported identity context fails closed.
- A responsive lesson reading page using the accepted design tokens and icon pack with equivalent light, dark, and system-theme behavior.
- Objectives, source links, version/provenance information, loading, unavailable, validation-failure, and safe not-found states.
- Focused contract, domain/application, adapter, API, generated-client, renderer-security, accessibility, theme, and end-to-end verification.

### Out of Scope

- Knowledge-check submission, deterministic scoring, feedback, attempt or completion evidence, learner-state projections, resume behavior, notes, bookmarks, or progress tracking.
- Built-in credential, OIDC, managed-cloud identity, public registration, multiple learners, organization tenancy, or identity-mode migration delivery. Their accepted provider-neutral semantics must remain unobstructed.
- Interactive setup UI or a general installation/upgrade workflow beyond the explicit configuration needed to exercise the selected local mode.
- Mutable authoring, content review or publication UI, arbitrary package import, archive transport, external learning standards, localization, or additional assessment and media types.
- AI tutoring, generated content, adaptive recommendations, mastery, certification, market data, portfolios, brokerage behavior, or personalized investment guidance.
- Backup/restore tooling, learner-data recovery claims, managed-cloud operations, or any community RPO/RTO claim.
- Production deployment, external publication, credentialed service use, or provider network calls.

## Canonical Context and Decisions

- [CAP-0001](../capabilities/CAP-0001-complete-structured-introductory-lesson.md) defines the parent outcome and Candidate A.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md) assigns package and publication ownership to Content and placement ownership to Curriculum.
- [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md), the [identity-provider contract](../../architecture/contracts/identity-provider-contract.md), and the [local identity security architecture](../../security/local-identity-architecture.md) govern the bounded local learner context.
- [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md) and the [content-package contract](../../architecture/contracts/content-package-contract.md) govern package identity, immutability, validation, provenance, rendering, and Assessment ownership.
- [ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md) remains canonical for later retained evidence; this read-only slice creates no learner evidence and makes no recovery claim.
- [ADR-0009](../../adr/ADR-0009-initial-application-framework-runtime-baseline.md) fixes the Python API and static React/TypeScript client baseline while preserving generated-client data authority and one production server boundary.
- [Contract architecture](../../architecture/contracts/contract-architecture.md) requires reviewed executable schemas, OpenAPI, and generated clients at public seams.
- [Local/cloud parity](../../architecture/deployment/local-cloud-capability-parity.md) requires shared domain and contract meaning while allowing the initial delivery to qualify only the local community adapter path.
- [Education versus financial advice](../../risk-compliance/education-versus-financial-advice.md) governs instructional wording and source presentation.
- [Interface design system](../../design/README.md), [style guide](../../design/style-guide.md), and [interface standards](../../standards/interface-design-standards.md) govern learner-visible presentation.

Every applicable durable decision is ready or constrained within this boundary. ADR-0009 supplies the runtime/framework baseline for the first executable path. Exact executable schema fields, API models, storage models, limits, dependency patches, and non-framework library choices remain delivery details to be fixed and reviewed in work packets without broadening accepted semantics.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Open one approved versioned lesson | yes | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 13 |
| B. Submit and score one knowledge check | no — Candidate A is an undelivered dependency | — | — | — | — | — | — | — | — |
| C. Reopen and review retained completion evidence | no — Candidates A and B are undelivered dependencies | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A is the only currently eligible increment.

- **Observable value — 2:** a learner can read a complete, source-attributed introductory lesson rather than observe an internal platform layer.
- **End-to-end completeness — 2:** the slice crosses package schema and validation, Content/Curriculum ownership, storage and metadata adapters, learner context, API/OpenAPI, generated client, and accessible web presentation.
- **Decision readiness — 2:** ADR-0005 through ADR-0008 resolve ownership, identity, package, and community protection boundaries applicable to CAP-0001.
- **Contract clarity — 1:** semantic ownership, versioning, integrity, and learner-context rules are accepted, but exact executable schemas and API shapes must be established and reviewed during packet planning.
- **Dependency independence — 2:** Candidate A has no preceding slice and does not require Assessment evidence or Learner-model projections.
- **Verification observability — 2:** package admission, exact-version resolution, authorization denial, safe rendering, API shape, provenance display, themes, accessibility, and browser behavior can be tested independently.
- **Reversibility and bounded risk — 2:** the learner path is read-only, creates no learner evidence, and can be withdrawn without evidence migration; immutable package/version compatibility still must be preserved.

Candidate B is deferred, not rejected: it depends on the lesson-opening path and introduces Assessment-owned response, score, feedback, and evidence contracts. Candidate C is deferred, not rejected: it additionally depends on Candidate B and introduces retained evidence, Learner-model projection, restart, and recovery qualification. Selecting either now would hide prerequisite work inside a larger slice and weaken independent verification.

## Boundary Path

1. **Accepted decisions and domain meaning:** preserve Content ownership of published lesson resources, Curriculum ownership of placement, Identity ownership of learner context, and the education-only claim boundary.
2. **Executable package contracts:** define the minimum version 1 schemas, deterministic package-index/digest rules, representative approved fixture, malicious fixtures, compatibility behavior, and bounded resource limits required for one lesson.
3. **Content and Curriculum application behavior:** atomically admit one exact package version, retain publication/provenance metadata, create one exact placement reference, and query a safe lesson-reading result through public module operations.
4. **Adapters and persistence:** store package bytes through the object-storage port and store only owning metadata in the appropriate transactional boundary; no module reads another module's tables or filesystem paths.
5. **Identity and host composition:** resolve an explicitly configured `single_profile` learner context, authorize the read operation, expose a reviewed API model, and keep host/provider details out of domain results.
6. **Generated client and interface:** consume the committed OpenAPI through a generated TypeScript client and render the reading template with semantic tokens, reviewed icons, safe content sinks, sources, and version/provenance cues.
7. **End-to-end qualification:** prove the successful path plus authorization, malformed package, unsafe content, stale/missing version, integrity, accessibility, theme, responsive, and advice-boundary scenarios.

Assessment execution, learner-evidence mutation, Learner-model projection, Audit evidence delivery, workers, AI/ML, market-data providers, analytical storage, backup/restore, and managed-cloud composition are intentionally absent.

## Contracts, Data, and Provenance

- Add versioned JSON Schemas under `contracts/learning/` only for the manifest, source/provenance, file declarations, and package fields required to open this lesson safely. Assessment payloads may be structurally referenced only as required for package closure; runtime assessment semantics remain outside this slice.
- Define deterministic digest vectors, positive fixtures, malicious/invalid fixtures, unsupported-version fixtures, and immutable-conflict fixtures. Exact bytes and canonicalization become compatibility-sensitive once accepted.
- Define typed public Content and Curriculum application requests/results with stable package, placement, version, digest, source, and provenance identifiers. Cross-module calls use public operations only.
- Add one authenticated read operation to the reviewed OpenAPI snapshot and generate the TypeScript client deterministically. Client models never become a second source of contract truth.
- Treat package and source inputs as untrusted until atomic admission succeeds. Renderer output uses a constrained intermediate representation and safe sinks; it performs no implicit network or filesystem access.
- Preserve the source URL/title/publisher or equivalent reviewed provenance needed to identify educational sources without copying provider-specific payloads into domain models.
- Persist no assessment response, score, attempt, completion, learner-state projection, recommendation, financial transaction, or AI execution data.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Open approved exact version | An authorized local learner opens the selected activity and sees its title, objectives, constrained body, educational sources, package version, and provenance | Browser end-to-end plus API/application integration |
| Theme and responsive parity | Light, dark, and system themes expose identical content/actions; the reading page reflows without loss at supported widths and 200 percent zoom | Browser visual/accessibility verification |
| Keyboard and assistive access | Landmarks, headings, links, source labels, focus order, focus visibility, and status announcements are usable without a pointer | Component and browser accessibility verification |
| Missing or invalid learner context | The API denies the request without revealing package internals or creating any learner/evidence state | Identity/API contract tests |
| Missing or stale exact version | The system returns a bounded unavailable/not-found result and never substitutes `latest` | Content/Curriculum application and API tests |
| Malformed or unsupported package | Admission fails atomically with structured redacted diagnostics; the package is not visible to learners | Schema/semantic validator tests |
| Unsafe path, link, markup, or asset | Validation or rendering fails closed without traversal, active content, implicit fetch, execution, or unsafe DOM insertion | Contract fixtures and renderer-security tests |
| Integrity or immutable-version conflict | Digest/file mismatch or conflicting bytes for an existing identity/version are rejected without replacing the accepted package | Content domain and adapter integration tests |
| Source and claim boundary | Sources remain reviewable and lesson wording is educational; no completion, mastery, certification, suitability, or investment-performance claim appears | Content review fixture plus browser assertion |
| Local/cloud semantic portability | The package, query result, and generated client use provider-neutral identifiers and contract versions; no local filesystem path or identity-provider payload crosses the public boundary | Contract and architecture tests |

## Agent Work Packets

The selected slice decomposes into the following bounded, serial work packets.

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| [WRK-0001](../work-packets/WRK-0001-establish-lesson-package-contracts.md) | Establish executable lesson-package schemas, digest rules, fixtures, and conformance evidence | none | none | complete |
| [WRK-0002](../work-packets/WRK-0002-deliver-approved-lesson-read-core.md) | Deliver Content/Curriculum read behavior plus PostgreSQL and filesystem adapters | WRK-0001 | none | complete |
| [WRK-0003](../work-packets/WRK-0003-expose-single-profile-lesson-api.md) | Compose single-profile learner context, FastAPI/OpenAPI, and generated TypeScript client | WRK-0002 | none | complete |
| [WRK-0004](../work-packets/WRK-0004-deliver-accessible-lesson-reading-page.md) | Deliver the accessible lesson-reading page in light, dark, and system modes | WRK-0003 | none | complete |
| [WRK-0005](../work-packets/WRK-0005-qualify-approved-lesson-slice.md) | Qualify the cross-system, security, architecture, accessibility, and local-runtime path | WRK-0004 | none | complete |

## Verification and Qualification

- JSON Schema, semantic, normalized-path, media, resource-bound, safe-rendering, digest-vector, and immutable-version fixtures.
- Content/Curriculum public-surface, dependency-direction, ownership, exact-version, and persistence integration tests.
- Identity-context denial and authorization tests for the explicitly configured local mode.
- OpenAPI snapshot and deterministic generated-client checks.
- UI component and browser tests covering loading, success, denial, unavailable, malformed-content, and source/provenance states.
- Light, dark, and system theme parity; keyboard, visible focus, screen-reader semantics, 200 percent zoom, responsive reflow, reduced motion, and forced-color checks.
- Local filesystem/PostgreSQL integration and provider-neutral contract evidence sufficient to preserve later cloud adapter conformance.
- Documentation, planning, design-system, architecture, and aggregate agent-readiness checks.

The slice may close only with executable evidence. A passing generic test suite cannot upgrade an unowned contract, security, accessibility, or parity claim.

## Rollback and Migration

The slice writes no learner evidence, so it requires no learner-state or evidence migration. Package versions are immutable: rollback may withdraw feature exposure or remove an unpublished development fixture, but it must never replace accepted bytes for an existing package identity/version or silently reinterpret a contract version.

Any PostgreSQL metadata migration must have a tested downgrade or forward-fix strategy before delivery. An older application must fail safely on unsupported package or API versions. Removing a published package that is referenced by later evidence is outside this slice and requires a separately governed retention/migration policy.

## Stop Conditions

- A required package or API shape would broaden ADR-0007's accepted markup, media, archive, assessment, authoring, or interoperability profile.
- The read path cannot preserve Content/Curriculum ownership without cross-module internal imports or persistence access.
- Identity delivery cannot stay within explicit `single_profile` configuration and the accepted provider-neutral learner-context contract.
- Instructional content or sources are not reviewable, educational, and inside the advice boundary.
- Rendering would require raw HTML, active content, implicit network access, unsafe sinks, or unreviewed third-party assets.
- Exact-version resolution, immutable identity/version/digest behavior, or local/cloud semantic portability cannot be verified.
- The work expands into knowledge-check execution, learner evidence, completion projection, backup/restore, managed cloud, AI/ML, market data, or another named non-scope.
- Canonical sources conflict, a new durable decision becomes necessary, or executable evidence reveals an unresolved security or compatibility boundary.

## Documentation Impact and Completion Evidence

### Delivered Outcome and Boundaries

An individual learner on the private-host community `single_profile` profile can
open `intro-risk-return-primary` and read the approved
`intro-risk-return@1.0.0` package through the complete package → Content →
Curriculum → Identity → FastAPI/OpenAPI → generated TypeScript client → React
browser path. The page presents exact version/digest, objectives, closed safe
body nodes, reviewed HTTPS sources, publication provenance, and the
education-only boundary. The application runs as one loopback Python
API/static process with PostgreSQL 18.4 and restrictive filesystem objects;
Node is build/test tooling only.

All required packets are complete: [WRK-0001](../work-packets/WRK-0001-establish-lesson-package-contracts.md),
[WRK-0002](../work-packets/WRK-0002-deliver-approved-lesson-read-core.md),
[WRK-0003](../work-packets/WRK-0003-expose-single-profile-lesson-api.md),
[WRK-0004](../work-packets/WRK-0004-deliver-accessible-lesson-reading-page.md),
and [WRK-0005](../work-packets/WRK-0005-qualify-approved-lesson-slice.md).
The WRK-0005 completion-evidence section retains exact topology, dependency,
build, hash, failure, and residual-risk details.

### Scenario Evidence

| Slice scenario | Owning evidence | Result |
| --- | --- | --- |
| Open approved exact version | Real PostgreSQL/filesystem backend integration plus live Chromium `approved-lesson.e2e.ts` | Direct pass |
| Theme and responsive parity | Six focused Playwright scenarios, explicit light/dark/system axe scans, reviewed Windows baselines, narrow and 200-percent-equivalent reflow | Direct automated pass; actual zoom control and other platforms remain gaps |
| Keyboard and assistive access | Component semantics, keyboard/skip/focus browser path, axe in all themes and live fixture | Direct automated pass; manual screen-reader use remains a gap |
| Missing or invalid learner context | Identity/API missing, tampered, expired, revoked, client-selected, Host, and Origin denial plus live no-cookie request | Direct pass with bounded responses and no lesson internals |
| Missing or stale exact version | Curriculum/application tests and live missing-placement browser path | Direct pass; no `latest` substitution |
| Malformed or unsupported package | Twenty-nine schema, semantic, resource, compatibility, and malicious-fixture contract tests | Direct pass with atomic denial |
| Unsafe path, link, markup, or asset | Contract denial corpus, closed body-node validator/renderer, security runner, unknown-node browser test | Direct pass |
| Integrity or immutable conflict | Real PostgreSQL/filesystem corruption, immutable-conflict, and database-failure tests | Direct pass without accepted-state replacement |
| Source and claim boundary | Approved fixture, API result, browser copy/action assertions, and visible reviewed source/provenance | Direct pass |
| Local/cloud semantic portability | Provider-neutral contract/generated-client checks and architecture fitness functions | Direct contract/local pass; managed-cloud composition remains representative/gap and is not claimed |

### Exact Verification Results

- `py -m uv sync --project backend --frozen` passed under Python 3.14.3.
- `pytest backend/tests` passed 105 tests against a disposable real PostgreSQL
  18.4 server: architecture, package contract, API/Identity, filesystem/
  PostgreSQL integration, and focused module suites.
- The OpenAPI and generated-client `--check` commands passed byte-stably.
- A clean `npm --prefix apps/web ci` under Node 24.14/npm 10.8.2 passed
  TypeScript, oxlint, 18 Vitest tests, 6 focused Playwright Chromium tests, the
  2-scenario live Playwright path, and the 97-module static Vite build.
- `python dev-tools/architecture/check_architecture.py` passed 7 fitness
  functions; `python dev-tools/security/check_slice_security.py` passed 10
  control groups.
- npm audit and pip-audit over the exact runtime export found zero known
  vulnerabilities. Uvicorn and Click declare BSD-3-Clause; the prior npm
  license inventory is unchanged.
- Design-system, documentation, planning, aggregate agent-readiness, and
  `git diff --check` gates passed. The new GitHub Actions workflow parsed
  locally; execution by GitHub-hosted infrastructure was not performed.
- `npm --prefix apps/web run dev:full -- --verify-only` passed the entire
  pinned install and qualification sequence. A separate smoke-start reached
  the Python readiness endpoint and Vite lesson route, then removed its exact
  Compose project and ignored synthetic data root. The verification host's
  default shell Node 20.20.1 was correctly rejected; the passing run used
  Node 24.14.0 and npm 10.8.2 as required by ADR-0009.

### Contracts, Data, Migration, and Rollback

The executable lesson package remains schema `1.0.0` with the fixed approved
digest
`576d543b404a7f70f2e5bebee55c32a3f945d8e8da73654c43ef92e656aee008`.
The reviewed OpenAPI contract remains `1.0` and its generated client is current.
Content/Curriculum and Identity migration streams apply from empty PostgreSQL,
reapply idempotently where defined, and exercise downgrade/rollback behavior.
This read-only learner slice writes no learner evidence, score, completion,
projection, recommendation, or financial transaction. Feature exposure can be
withdrawn without learner-evidence migration, while immutable published package
bytes must never be replaced.

### Documentation and Evidence Classification

Canonical local deployment, content-package, and `single_profile` security
sources; backend/web/local READMEs; architecture verification; known gaps; and
derived architecture, security, deployment, interface, and testing packs are
synchronized. Coverage is direct only for the exact local approved-lesson
profile, representative for shared local/cloud artifact meaning, and a gap for
managed-cloud composition and every named unimplemented boundary.

### Qualification Not Performed and Residual Risk

No controlled manual screen-reader run, actual browser zoom-control run,
non-Chromium engine, non-Windows visual baseline, supported-platform
permissions qualification, real passive-asset delivery, built-in/OIDC
identity, worker/analytics composition, backup/restore, complete local
distribution, remote/public exposure, managed cloud, external provider,
production deployment, CI-host execution, commit, push, or publication was
performed. No recovery, availability, RPO/RTO, cloud-parity, investment
suitability, performance, mastery, or personalized-advice claim is made.

The primary residual risks are the unqualified browser/platform matrix,
host-administrator trust in community mode, absent passive-asset delivery
evidence, and lack of managed-cloud/deployment/recovery qualification. Later
CAP-0001 slices must separately introduce Assessment evidence and retained
learner completion; this slice does not complete the whole capability.

The slice is ready for an explicit completion-acceptance decision but remains
`verifying` until that separate human decision is supplied and recorded only
in the ignored local ledger.

## Planning History

- 2026-08-04: Shaped from CAP-0001 Candidate A after deterministic eligibility and scoring against the deferred assessment and retained-evidence candidates.
- 2026-08-04: Framework/runtime audit identified DEC-0005; SLI-0001 moved to `decision-blocked` and its provisional score was withdrawn pending canonical resolution.
- 2026-08-04: ADR-0009 resolved DEC-0005; eligibility and scoring were re-run. Candidate A scored 13 and returned to shaping for the next governed stage.
- 2026-08-05: WRK-0001 through WRK-0005 completed. The slice moved to verifying for the separate completion-verification workflow and explicit completion acceptance.
- 2026-08-05: WRK-0005 was reopened and requalified within its existing scope to add the one-command Git Bash/PowerShell development runner; slice completion acceptance remains separate.
- 2026-08-05: WRK-0005 was reopened within its existing scope for an fnm-managed runtime bootstrap; slice completion acceptance remains separate.
- 2026-08-05: WRK-0005 completed after the fnm-managed bootstrap, complete check handoff, and development smoke start passed; the slice returned to verifying for separate completion acceptance.
