---
id: WRK-0171
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0083
capability: CAP-0020
depends_on: [WRK-0170]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/generated/api-client/schema.d.ts", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/modules/guidance/README.md", "backend/src/financial_ai_academy/modules/guidance/application/service.py", "backend/src/financial_ai_academy/modules/guidance/ports/__init__.py", "backend/src/financial_ai_academy/modules/guidance/ports/contextual_help.py", "backend/src/financial_ai_academy/modules/guidance/public.py", "backend/tests/architecture/test_module_boundaries.py", "backend/tests/integration/api/test_single_profile_guidance_api.py", "backend/tests/unit/guidance/test_service.py", "contracts/api/README.md", "contracts/api/openapi.json", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/platform-help-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0083-open-contextual-method-and-limitation-help.md", "docs/planning/work-packets/WRK-0171-compose-contextual-help-api.md"]
generated_artifacts: ["apps/web/src/generated/api-client/schema.d.ts", "contracts/api/openapi.json"]
base_revision: 8b3aa2e4d17de2494e6360f1415e8c2861d0995d
claim_id: WRK-0171:04392acc-49fb-4c7f-8e87-c59c19572226
claimed_by: codex-cap-0020
claimed_at: 2026-10-18T04:20:08Z
---

# Agent Work Packet: Compose the Contextual Help API

## Objective and Deliverable

Compose the completed `contextual-help/v1` registry into a Guidance-owned
application/public exact-context read and one protected read-only FastAPI
operation. Regenerate the reviewed OpenAPI snapshot and shared TypeScript
client so browser, command-line, service, and future headless AI callers use
the same validated versioned context document and referenced topic identities.

The deliverable is an API-first local composition seam. It is not a browser
feature, mutable Help authoring system, database, remote-content path, model or
provider feature, personalization system, or live end-to-end qualification.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Revalidate the routed architecture-contract,
interface, security-risk, testing-quality, and delivery-planning context; the
change-impact matrix; decision readiness; CAP-0020; SLI-0083; completed
WRK-0170; the existing platform-help application/API/client seam; identity and
API contracts; generated-artifact workflows; affected consumers and tests;
and the nearest Guidance, API, contract, and client READMEs.

The Required Startup was performed and reported before this planning change.
Stop for a canonical conflict, stale CAP package, unresolved durable decision,
active file collision, or material scope drift.

## Decisions and Assumptions

- WRK-0170 is complete and owns exact context identity, validation, digest,
  source binding, topic correlation, starter records, and atomic admission.
- Guidance remains the sole owner of context lookup. The API transports the
  admitted record without feature-specific remapping or reinterpretation.
- The route is
  `GET /api/v1/guidance/contextual-help/{context_key}/versions/{context_version}`;
  it exposes no `latest` alias, browse operation, or arbitrary destination.
- Context reads use the existing server-owned
  `guidance.platform_help.read` permission because the result is a routing
  document for the same approved Help corpus. No client-supplied identity or
  permission selector is added.
- The context response contains ordered exact topic references and their
  purpose, not embedded topic bodies. Callers use the existing protected exact
  topic operation for the reviewed content.
- OpenAPI and TypeScript client outputs are generated artifacts; generators,
  canonical schemas, and public Python values remain authoritative.

## In Scope

- Add a transport-neutral context-registry read port and extend the Guidance
  service/public protocol with an exact context request and response.
- Compose the immutable context registry with the already admitted platform-
  help topics and fail startup before API availability on any registry error.
- Add closed Pydantic response models that preserve exact context identity,
  safe feature label, ordered topic references and purposes, publication,
  source facts, and context digest without private implementation metadata.
- Add the protected exact-version route, strict path bounds, bounded 404 and
  validation errors, and authorization-before-registry-access behavior.
- Regenerate the reviewed OpenAPI snapshot and TypeScript client; prove the
  operation and closed response shape are available to non-browser callers.
- Add focused service, composition, API, contract-generation, authorization,
  exact-version absence, malformed path, flexible valid reference-order/count,
  confidentiality, and module-boundary tests.
- Reconcile direct Guidance, API, contract, module, architecture assurance,
  planning, and generated-artifact documentation.

## Out of Scope

- Browser routes, feature links, safe-return behavior, styling, accessibility,
  or feature-specific adapters; the next SLI-0083 packet owns those changes.
- Browser/headless live parity, restart, offline/no-outbound observation,
  durable-state containment, and final cleanup; the final SLI-0083 packet owns
  that qualification.
- A context browse/search endpoint, semantic/vector search, generated answers,
  personalization, recommendation, analytics, tracking, evidence, grading,
  eligibility, mastery, competency, or learner policy.
- Persistence, migrations, mutable or user-authored Help, repository Markdown
  serving, remote content, arbitrary URLs, active content, provider/model
  execution, external action, financial advice, suitability, or conclusions.
- Identity/tenancy expansion, managed-cloud operation, recovery, licensing,
  legal/commercial policy, or public/external publication.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Guidance | Completed context registry, platform-help service/public/ports | Context read port, request/protocol, service composition, direct README | Expose one exact transport-neutral read |
| Composition | Local bootstrap and existing immutable corpus | Compose one registry from the admitted topic corpus | Fail startup atomically and reuse source-bound topics |
| API | Host, models, error mapping, OpenAPI generator | Closed context model and protected exact route | Serve browser and headless clients identically |
| Contracts/client | API snapshot and generation output | OpenAPI snapshot, TypeScript types, API README | Preserve one reviewed public shape |
| Tests | Guidance unit, protected API, generation and architecture suites | Focused success, denial, absence, variation, startup, and boundary tests | Prove exact fail-closed behavior without brittle fixtures |
| Architecture | Help contract, module map, assurance table | Direct implementation and verification statements | Record ownership and non-authority |
| Planning | SLI-0083, WRK-0171, register | Status and neutral evidence only | Keep governed delivery state synchronized |

No browser feature, persistence, migration, provider/model, deployment-profile,
design-system, or unrelated domain-module file may change.

## Contracts and Interfaces

WRK-0170's `ContextualHelpRecord`, registry, strict mapping adapter,
`context_payload`, exact identity, digest, source binding, purpose enumeration,
and failure codes are binding inputs. This packet adds a minimal
`ContextualHelpRegistryPort` and `OpenContextualHelpRequest` to the stable
Guidance public seam.

The route accepts only bounded canonical `context_key` and stable
`major.minor.patch` `context_version`. The response is the exact closed v1
document. It contains no learner/session identity, repository path, Git or
review metadata, authoring locator, provider payload, prompt, model output, raw
markup, arbitrary URL, or owning feature state. Errors never echo rejected
payloads, context labels, topic identities, corpus counts, or private paths.

The generated client must reproduce the operation ID and all closed response
models from `contracts/api/openapi.json`; no handwritten browser API shape is
introduced.

## Dependencies and Parallel Safety

WRK-0170 is complete. This packet changes shared Guidance composition, API
host/models, OpenAPI snapshot, generated client, architecture, slice, and
register surfaces, so it is not parallel-safe with another writer on those
paths. The feature-link packet must wait for this packet's exact generated
operation and response types.

Claim from a recorded base revision, run `packet-start`, acquire exact-file
leases immediately before edits, retain one owner through verification, and
keep approval and reviewer records only in ignored local storage.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Exact context | A permitted session names an admitted key and version | The route is called | The complete exact v1 document and digest are returned without reinterpretation | service/API/contract |
| No substitution | A valid key names an absent version | The route is called | A bounded 404 is returned and no other version is substituted | service/API |
| Protected read | Session is missing or lacks Help read permission | The route is called | 401/403 occurs before registry access or context facts are exposed | API/security |
| Invalid identity | Key or version violates path bounds | The route is called | A bounded validation error is returned without echoing unsafe input | API/security |
| Atomic composition | Any context is malformed, stale, duplicated, or dangling | Local composition starts | Startup fails before a partial Guidance service or route becomes available | composition/unit |
| Topic correlation | A valid context references admitted exact topics | The context and topic APIs are read | Ordered IDs, versions, purposes, and digests remain source-bound and consistent | API/unit |
| Flexible valid registry | Safe feature labels and valid reference counts/order vary | Service/API reads run | Invariants hold without freezing total context count, fixture prose, or layout | unit/anti-rigidity |
| Headless contract | OpenAPI and generated client regenerate | Artifacts are inspected | Non-browser and browser callers receive one identical protected operation and shape | OpenAPI/client |
| No new authority | Imports, outputs, and calls are inspected | Checks run | No persistence, network, provider/model, learner-policy, grading, eligibility, or financial seam exists | architecture/security |

## Verification Commands

Run focused tests first:

`backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/guidance backend/tests/integration/api/test_single_profile_guidance_api.py backend/tests/architecture/test_module_boundaries.py`

Regenerate and verify the OpenAPI snapshot and TypeScript client with the
repository's pinned workflows. Run generated-client contract tests, Python
compilation, architecture, security, documentation, planning, learner-language,
whitespace, controller-selected exact-candidate verification, one independent
technical review, and `python dev-tools/agent/check_ready.py`.

Record only passing commands. A bounded whitespace, optional wording, or
generated formatting correction may be fixed in scope without a new approval
or unrelated full-review loop.

## Documentation and Evidence Update

Document the Guidance context-read port and application/public operation,
startup composition, shared permission, route and error semantics, closed
Pydantic/OpenAPI/client shape, headless parity, exact-version behavior,
confidentiality, generated-artifact commands, assumptions, and remaining
browser/live work. Update packet, slice, and register together; never copy
local approval or reviewer records into tracked files.

## Stop Conditions

Stop for ambiguous context meaning or feature mapping; required change to an
owning feature's domain/public contract; request-time repository parsing;
mutable, remote, arbitrary, or active content; embedded topic reinterpretation;
browser-only mapping; semantic/vector search; model/provider execution;
personalization or analytics; learner advice, grading, eligibility, mastery,
competency, or financial action; persistence or migration need; breaking v1
compatibility; new permission/identity/tenancy semantics; managed-cloud,
recovery, licensing, legal/commercial, or external-publication behavior; stale
CAP authority; active collision; or material CAP-0020/SLI-0083 drift.

Do not stop or reopen review solely for harmless whitespace, optional copy,
generated ordering, fixture count, nonfunctional styling, or another
inconsequential correction. Fix it within scope or defer optional presentation
polish to CAP-0031.

## Required Handoff

Report `CAP-0020.SLI-0083.WRK-0171`; exact candidate and receipt; application,
public, composition, API, OpenAPI, and generated-client seams; context/topic
correlation; permission and failure mapping; browser/headless contract parity;
confidentiality and anti-rigidity evidence; focused and repository checks;
changed files; documentation impact; assumptions; and remaining feature-link
and live-qualification gaps. Confirm no persistence, migration, browser
feature, provider/model, external content/action, learner authority, or
financial behavior changed.

## Planning History

- 2026-10-18: Authored just in time after WRK-0170 completed. The packet
  composes its exact, source-bound contextual-help registry into one protected
  API-first read shared by browser and future headless callers while deferring
  feature links and live qualification to dependent packets. It remains inside
  the approved CAP-0020 package and requires no lower-level approval.
- 2026-10-18: Activated from clean recorded base `8b3aa2e` after confirming the
  current CAP binding, completed WRK-0170 dependency, API-first exact-read
  scope, executable checks, and no unresolved decision or ownership collision.
