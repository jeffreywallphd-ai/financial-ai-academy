---
id: WRK-0003
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-agent
updated: 2026-08-05
parent: SLI-0001
capability: CAP-0001
depends_on: ["WRK-0002"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/pyproject.toml", "backend/uv.lock", "backend/src/financial_ai_academy/modules/identity", "backend/src/financial_ai_academy/hosts/api", "backend/src/financial_ai_academy/bootstrap", "backend/src/financial_ai_academy/platform/security", "backend/migrations", "backend/tests/unit/identity", "backend/tests/integration/api", "contracts/api/openapi.json", "apps/web/package.json", "apps/web/package-lock.json", "apps/web/tsconfig.json", "apps/web/scripts/generate-api-client.mjs", "apps/web/src/generated/api-client", "apps/web/tests/contract", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md"]
generated_artifacts: ["backend/uv.lock", "backend/migrations", "contracts/api/openapi.json", "apps/web/package-lock.json", "apps/web/src/generated/api-client"]
base_revision: a9503220007fedb9b67113a1b3f1e6e498fc6205
claim_id: WRK-0003:0d608503-6c51-492a-965f-e125a7dfac2f
claimed_by: codex-agent
claimed_at: 2026-08-05T00:50:07Z
---

# Agent Work Packet: Expose the Single-Profile Lesson API

## Objective and Deliverable

Compose the WRK-0002 lesson-read operation behind the accepted `single_profile` learner-context boundary, a thin FastAPI operation, a committed OpenAPI 3.1 snapshot, and a deterministically generated TypeScript client. The observable deliverable is an authorized cookie-based API flow that bootstraps the one private-host learner and returns the exact lesson-reading result while missing, malformed, expired, revoked, or client-selected identity fails closed.

## Required Context

Before changing files, prominently read and follow every applicable `AGENTS.md` and repository-root `docs/README.md`. Route through the baseline pack with `architecture-contracts` as primary and `security-risk` as adjacent. Read SLI-0001, WRK-0002 and its public operations, ADR-0001, ADR-0005, ADR-0006, ADR-0009, the identity-provider and learner-context contract, local identity security architecture, contract architecture, local profile, module dependency rules, API and web READMEs, exact affected migrations, consumers, tests, and generated-artifact guidance.

## Decisions and Assumptions

- Only explicitly configured `single_profile` mode is delivered. Built-in credentials, OIDC, multiple learners, public registration, and identity-mode migration remain out of scope but the provider-neutral context contract must remain extensible to them.
- Identity creates and persists stable opaque installation, actor, learner, binding, and server-side session identifiers. Learning operations receive normalized context only.
- `POST /api/v1/session/single-profile` is an explicit, same-origin local-bootstrap transaction. It validates configured mode, loopback/private-host restrictions, allowed Origin/Host, installation state, and limitation acknowledgement before issuing a protected opaque cookie.
- `GET /api/v1/curriculum/placements/{placement_id}/lesson` requires resolved learner context and invokes the public Curriculum operation. A path placement ID never selects the actor or learner.
- Cookies are HttpOnly and SameSite=Strict, have bounded server-enforced idle and absolute expiry, rotate when authentication state changes, and are revocable. Secure cookies are mandatory outside a separately validated loopback HTTP development profile.
- API errors use one versioned safe envelope with a stable code, bounded message, and correlation ID. They never expose package bytes, storage/database paths, session values, provider material, stack traces, or raw validation content.
- OpenAPI is generated from validated FastAPI/Pydantic models, committed for review, and is the sole source for generated TypeScript API models. Node 24, TypeScript 7, and npm exact locking are fixed for client generation; the generator is a replaceable tool pinned in `package-lock.json`.

## In Scope

- The minimum Identity domain/application/port/adapter and PostgreSQL migration behavior for configured single-profile bootstrap, stable binding, server-owned session resolution, expiry, rotation, and revocation.
- Validated bootstrap composition selecting exactly the single-profile adapter and refusing unsafe configuration or populated-installation mode mismatch.
- Thin FastAPI host, versioned routes, cookie authentication, Origin/Host checks, authorization, error mapping, redacted structured diagnostics, and health/readiness needed by this slice.
- Reviewed OpenAPI 3.1 snapshot, deterministic client-generation command, generated TypeScript client, and generation drift test.
- Focused identity, API success/denial/failure, OpenAPI, and generated-client contract tests.

## Out of Scope

- Passwords, recovery codes, login forms, OIDC callbacks/tokens, multiple modes at runtime, multiple learners, organization tenancy, MFA, public registration, or identity migration.
- Content/Curriculum internal changes except consuming their WRK-0002 public facades.
- Browser routing, lesson page components, theme UI, deployment packaging, Node production server, SSR, BFF, server actions, or direct browser parsing of CommonMark.
- Knowledge checks, learner evidence, Audit delivery, backup/restore, cloud identity, provider network calls, or production exposure.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Identity module | ADR-0006 and identity contract | `backend/src/financial_ai_academy/modules/identity/` | Single-profile binding and normalized session context |
| Host/composition | Backend host/bootstrap READMEs | Named API, bootstrap, and security roots | Thin FastAPI transport and validated adapter selection |
| Persistence | Existing WRK-0002 migrations | `backend/migrations/` | Identity binding and session tables owned by Identity |
| Public API | Contract architecture and Content/Curriculum facades | `contracts/api/openapi.json` | Reviewed exact HTTP contract |
| Generated client | Web README and OpenAPI snapshot | Named generator, metadata, generated client, and contract tests | Deterministic TypeScript consumer seam |
| Verification/docs | Identity/API tests and assurance maps | Named test/document roots | Direct context, denial, generation, and redaction evidence |

## Contracts and Interfaces

WRK-0003 consumes only WRK-0002's public `OpenPlacedLesson` operation and typed result.

It produces:

- an Identity `LearnerContext` with actor, learner, session, authentication/expiry times, normalized method, and application permissions;
- an opaque session-cookie security scheme in OpenAPI;
- an idempotent local-bootstrap response that returns no secret or provider identifier;
- an exact lesson-read response containing placement/package/version/digest, objectives, safe body-node union, source/provenance records, and application-controlled asset locators;
- stable HTTP mappings for unauthorized, forbidden, not found, unavailable, unsupported, invalid, immutable conflict, and internal safe failure; and
- a generated TypeScript client with no hand-maintained duplicate API models.

## Dependencies and Parallel Safety

WRK-0002 must complete first because the API consumes its stable public operation and error model. This packet owns OpenAPI, identity migrations, shared runtime metadata, and the generated client, so no later web or qualification packet may run in parallel with it. WRK-0004 begins only after the snapshot and generated client reproduce cleanly.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Local bootstrap and read | Safe configured single-profile mode and an approved placement | The browser bootstrap is followed by lesson GET | One protected session is issued and the exact lesson result is returned | FastAPI/PostgreSQL integration test |
| Missing context | No valid session cookie exists | Lesson GET runs | The API returns a generic unauthorized envelope and creates no learning/evidence state | API authorization test |
| Tampered, expired, or revoked context | The cookie or server session is invalid | Lesson GET runs | Access fails closed with no package internals or identifier leakage | Identity/API denial tests |
| Client-selected identity | A request supplies actor or learner fields/headers | Bootstrap or GET runs | Client identity is ignored or rejected; server context remains authoritative | Contract/security test |
| Unsafe exposure | Host, Origin, bind address, mode, or limitation acknowledgement violates the local boundary | Bootstrap or startup runs | Composition fails safely and no session is issued | Configuration and Origin/Host tests |
| Missing exact lesson | The authorized placement/version cannot be resolved | Lesson GET runs | A bounded not-found/unavailable response appears; no `latest` substitution occurs | API mapping test |
| Redaction | Sentinel identity, cookie, path, and package values trigger failures | Diagnostics are captured | Secrets and sensitive internals are absent while correlation remains possible | Sentinel redaction test |
| Deterministic generation | The committed OpenAPI snapshot is regenerated twice | Client generation runs | Snapshot and generated TypeScript are byte-stable and a clean diff remains | Generation drift test |
| Runtime boundary | The web client is inspected and built | It calls the lesson API | Only generated client code crosses the seam; no backend import, database access, or Node server exists | Architecture and build tests |

## Verification Commands

```powershell
uv sync --project backend --frozen
uv run --project backend pytest backend/tests/unit/identity
uv run --project backend pytest backend/tests/integration/api
uv run --project backend python -m financial_ai_academy.hosts.api.generate_openapi --check
npm --prefix apps/web ci
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
npm --prefix apps/web test -- --run apps/web/tests/contract
python dev-tools/documentation/check_docs.py
python dev-tools/agent/check_ready.py
git diff --check
```

## Documentation and Evidence Update

Update only assurance claims directly established by the single-profile, API, OpenAPI, and generated-client evidence. Do not promote built-in/OIDC, remote-host, UI, deployment, cloud, or end-to-end coverage. Generated files must identify their source and command and must never be hand-edited.

## Stop Conditions

- Identity provider payloads, cookie/session values, or client-selected actor/learner identifiers would cross into learning operations.
- Safe single-profile use cannot be restricted to the accepted private-host/loopback boundary.
- The API needs Content/Curriculum internals, database access in routes, duplicated TypeScript models, or a Node production server.
- OpenAPI or client generation is nondeterministic, or an exact response shape requires changing WRK-0002 semantics.
- Work expands into built-in/OIDC, organization tenancy, multiple learners, identity migration, learner evidence, backup/recovery, or production exposure.
- Canonical sources conflict, sensitive diagnostics cannot be redacted, or another active packet overlaps scope.

## Required Handoff

Report the identity/session schema, bootstrap restrictions, cookie policy, API operations and error mappings, OpenAPI/client hashes and regeneration results, denial/redaction evidence, dependency inspection, documentation impact, residual loopback limitations, and exact client interface handed to WRK-0004.

## Completion Evidence

- Identity owns `identity.installations`, `identity.bindings`, and `identity.sessions` in the isolated `identity_0001_single_profile_sessions` migration stream. Stable actor/learner bindings use opaque UUIDs; only SHA-256 token digests are stored. Bootstrap rotates prior binding sessions, and resolution enforces 30-minute idle plus eight-hour absolute expiry and explicit revocation.
- Composition accepts only `single_profile`, a PostgreSQL DSN, loopback bind/public-origin values, exact allowed hosts, and cookie security coherent with HTTP or HTTPS. The state-changing bootstrap requires the configured Origin, same-origin fetch metadata when supplied, and explicit limitation acknowledgement. Client actor, learner, session, and provider headers are rejected.
- `POST /api/v1/session/single-profile` issues an HttpOnly, SameSite=Strict, path-root opaque cookie. It is Secure for HTTPS and may omit Secure only in the separately validated loopback HTTP development profile. `GET /api/v1/curriculum/placements/{placement_id}/lesson` resolves server-owned learner context, requires `curriculum.lesson.read`, and calls only the public Curriculum facade.
- The API maps invalid, unauthorized, forbidden, not-found, conflict, integrity/unavailable, and unexpected failures into the versioned bounded envelope with a correlation ID. PostgreSQL integration covers bootstrap/read, missing/tampered/expired/revoked sessions, identity-selection denial, Host/Origin denial, missing exact placement, migration reapply/downgrade, redaction, and absence of raw cookie persistence.
- The reviewed OpenAPI 3.1 snapshot SHA-256 is `BECC54105BE82B95F3DECCEA3A73A6C7142A98C232B7354400329474E16E8A9F`. Generated `schema.d.ts`, `client.ts`, and `index.ts` hashes are `0454DE2E0E8456DBC2DA6BDA62D8ED518F7636D83AC09B5786EB95F41A114033`, `6E507A54BD39156AA880595DAD7C16187E9980FB233617CD7472E96A18B24153`, and `86FD34B0B4A0753011879D121EBC181836B030702338BA9AC6C06E277C9C3D54`. Snapshot and client regeneration checks are byte-stable.
- The Node 24/npm 10.8.2 clean install, TypeScript 7.0.2 compilation, and generated-client contract test pass. The browser handoff is `createFinancialAcademyApiClient(baseUrl)` followed by the generated `GET("/api/v1/curriculum/placements/{placement_id}/lesson", ...)` operation; it imports no backend, database, or Node-server code.
- Verification passed 22 Identity unit tests, two consecutive six-test API runs against disposable PostgreSQL 18.4, and 69 predecessor unit/architecture/PostgreSQL regressions. Python and npm audits found no known vulnerabilities. Reviewed WRK-0003 Python dependencies are MIT/BSD-3-Clause; Node dependencies are MIT/Apache-2.0.
- This evidence promotes only the local loopback `single_profile` API and generated-client path. Built-in credentials, OIDC, multiple learners, remote/public hosting, production deployment, browser UI, and cloud parity remain unimplemented. The current approved fixture has no passive assets; its typed application-controlled asset-locator field is present, while asset retrieval remains a later delivery concern.

## Planning History

- 2026-08-04: Shaped from SLI-0001 boundary seam 5 and the generated-client portion of seam 6; planning approval and implementation activation remain separate local-only stages.
- 2026-08-05: Implemented and verified the bounded single-profile Identity, FastAPI/OpenAPI, PostgreSQL session, and deterministic generated-client seam; WRK-0003 completed and handed off to WRK-0004.
