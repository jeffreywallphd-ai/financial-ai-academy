# Architecture Verification Map

- Status: proposed
- Canonical for: mapping architecture claims to executable evidence

Coverage values are `direct`, `representative`, or `gap`. A general passing test suite does not make a specific architectural claim direct.

| Invariant | Intended evidence | Current coverage |
| --- | --- | --- |
| Content and Curriculum domain layers do not depend on frameworks, hosts, adapters, provider SDKs, schema parsers, or database drivers | `backend/tests/architecture/test_module_boundaries.py` | direct |
| Domain isolation for modules beyond Content and Curriculum | Expanded import/dependency architecture check | gap |
| Curriculum imports only the Content public surface and neither repository reads the other module's schema | `backend/tests/architecture/test_module_boundaries.py` | direct |
| Public-surface and persistence isolation for modules beyond the implemented Content/Curriculum seam | Expanded forbidden-import and persistence checks | gap |
| The first learning loop preserves ADR-0005 ownership for Content, Curriculum, Assessment, Learner model, and Audit | Module tests, event ownership checks, projection rebuild tests, and Audit source-of-truth checks | gap |
| Every identity adapter preserves ADR-0006 learner-context, session, denial, and exactly-one-mode semantics | Reusable identity-provider conformance, session lifecycle, OIDC, recovery, redaction, and local/cloud parity tests | gap |
| Explicit `single_profile` Identity creates stable opaque bindings, stores only hashed session tokens, enforces idle/absolute expiry and revocation, rejects client-selected identity, and emits normalized learner context only inside the accepted loopback boundary | `backend/tests/unit/identity` and `backend/tests/integration/api` against PostgreSQL 18.4 | direct |
| Versioned lesson-package admission preserves ADR-0007 schema/capability bounds, normalized paths, file closure, measured integrity/media, resource limits, constrained CommonMark, canonical digest, safe diagnostics, and immutable identity/version/digest conflict behavior | `backend/tests/contract/lesson_package` over `contracts/learning/lesson-package/v1` and `contracts/compatibility/lesson-package/v1` | direct |
| Content admission preserves immutable publication behavior across PostgreSQL metadata and restrictive local filesystem objects; exact reads revalidate stored bytes and return closed safe body nodes without storage leakage | `backend/tests/unit/content` and `backend/tests/integration/lesson_read` against PostgreSQL 18.4 | direct |
| Curriculum exact placement/open behavior uses the public Content seam with no `latest` fallback or cross-module table access | `backend/tests/unit/curriculum`, `backend/tests/integration/lesson_read`, and `backend/tests/architecture` | direct |
| Managed object-storage adapters preserve versioned lesson-package and passive-asset meaning | Managed storage-adapter conformance | gap |
| The browser validates and exhaustively renders the closed lesson body-node union without raw HTML, arbitrary schemes, implicit remote embeds, or partial unknown-node output | `apps/web/tests/unit`, `apps/web/tests/component`, and `apps/web/tests/browser/lesson-reading` | direct |
| Community retained evidence preserves ADR-0008 protection, coordinated-set, empty-target restore, identity, session-revocation, content-version, projection, and no-RPO/RTO semantics | Supported-platform permissions, least-privilege roles, backup/restore conformance, corruption and failure fixtures, projection reconciliation, redaction tests, and controlled restore drills | gap |
| Application artifacts preserve ADR-0009 runtime/framework lines, generated-client authority, static browser rendering, and absence of a Node production server | Exact manifests/lockfiles, clean Node 24 install and Vite build, OpenAPI-client reproduction, framework/browser tests, dependency inspection, and forbidden-boundary checks | direct |
| The private-host approved-lesson qualification runs PostgreSQL 18.4, restrictive filesystem objects, one loopback Python API/static application process, and the exact reviewed browser build without a Node application server | `tests/e2e/approved-lesson/run.py`, `apps/web/tests/browser/approved-lesson`, `deployments/local/serve.py`, and `tests/architecture/test_approved_lesson_boundaries.py` | direct |
| The browser REST client is generated only from the reviewed OpenAPI snapshot and remains byte-stable under Node 24 and TypeScript 7 | `financial_ai_academy.hosts.api.generate_openapi --check`, `apps/web/scripts/generate-api-client.mjs --check`, TypeScript compilation, and `apps/web/tests/contract` | direct |
| The delivered lesson route preserves content/action parity across light, dark, and system themes and provides automated keyboard, focus, accessibility-tree, reflow, reduced-motion, forced-color, denial, and safe-failure evidence | Vitest theme/component checks, explicit light/dark/system Playwright Chromium/axe checks, reviewed platform-specific visual baselines under `apps/web/tests/browser/lesson-reading`, and live approved-fixture axe evidence | direct |
| Events and provider manifests validate against registered schemas | Contract catalog and fixture checks | gap |
| Providers pass reusable conformance suites | Provider-family contract tests | gap |
| Local and cloud use the same domain/application packages | Local build/composition inspection plus a future managed-cloud deployment-manifest comparison | representative |
| Adaptation applies deterministic eligibility and policy after ranking | Application tests with unsafe ranking fixtures | gap |
| AI output cannot directly mutate authoritative state | Application-port and use-case boundary tests | gap |
| Portfolio consumes canonical rather than raw provider data | Import and type-boundary checks | gap |
| Content and Curriculum lesson-read metadata runs from empty migrations on a real PostgreSQL server, including downgrade/reapply behavior | `backend/tests/integration/lesson_read` against PostgreSQL 18.4 | direct |
| Single-profile Identity binding/session metadata runs from its isolated empty migration stream on a real PostgreSQL server, including reapply and downgrade behavior | `backend/tests/integration/api` against PostgreSQL 18.4 | direct |
| PostgreSQL configuration and deployment remain the transactional target across complete local and managed profiles | Real PostgreSQL 18.4 local qualification plus future managed-cloud deployment checks | representative |
| Documentation links, context paths, adjacency, and pack budgets remain valid | `python dev-tools/documentation/check_docs.py` | direct |

Update this map when implementation or verification is introduced. Do not promote coverage without a check that owns the stated invariant.
