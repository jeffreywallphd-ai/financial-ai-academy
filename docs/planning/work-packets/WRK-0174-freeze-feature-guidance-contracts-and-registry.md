---
id: WRK-0174
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0084
capability: CAP-0020
depends_on: [WRK-0173]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/guidance/adapters/__init__.py", "backend/src/financial_ai_academy/modules/guidance/adapters/feature_guidance_contract.py", "backend/src/financial_ai_academy/modules/guidance/adapters/immutable_corpus.py", "backend/src/financial_ai_academy/modules/guidance/adapters/immutable_feature_guidance_registry.py", "backend/src/financial_ai_academy/modules/guidance/domain/__init__.py", "backend/src/financial_ai_academy/modules/guidance/domain/feature_guidance.py", "backend/src/financial_ai_academy/modules/guidance/resources/README.md", "backend/src/financial_ai_academy/modules/guidance/resources/feature-guidance/v1", "backend/src/financial_ai_academy/modules/guidance/resources/platform-help/v1/project-artifact-use.json", "backend/src/financial_ai_academy/modules/guidance/resources/platform-help/v1/safe-recovery.json", "backend/tests/contract/feature_guidance", "backend/tests/unit/guidance/test_feature_guidance.py", "backend/tests/unit/guidance/test_immutable_corpus.py", "contracts/README.md", "contracts/compatibility/README.md", "contracts/compatibility/feature-guidance/v1", "contracts/guidance/README.md", "contracts/guidance/feature-guidance/v1", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/platform-help-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0084-understand-feature-limits-and-safe-recovery.md", "docs/planning/work-packets/WRK-0174-freeze-feature-guidance-contracts-and-registry.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Freeze Feature-Guidance Contracts and Registry

## Objective and Deliverable

Establish the additive `feature-guidance/v1` exact record and mapping contracts,
pure Guidance validation/digest core, reviewed safe-recovery and inert-artifact
topics, and one atomically admitted immutable starter registry. Later packets
can expose and render reviewed limitation/recovery meaning without inventing
policy in feature APIs or the browser.

The deliverable is transport-neutral and read-only. It does not add an
application operation, HTTP route, OpenAPI operation, generated client, feature
integration, persistence schema, provider/model call, remediation command, or
live topology.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Revalidate routed architecture-contract,
interface, security-risk, testing-quality, and delivery-planning context; the
change-impact matrix; decision readiness; CAP-0020; SLI-0084; completed
SLI-0083; current platform/contextual Help contracts, Guidance core, corpus,
consumers and tests; the affected feature public statuses; AI/provider,
Project-artifact, idempotency/uncertainty, privacy, language, accessibility, and
education-versus-advice sources; and every nearest README.

The Required Startup was performed and reported before this planning change.
The parent CAP package is current, SLI-0084 is ready, its SLI-0083 dependency is
complete, and no unresolved decision applies. Stop for conflicting authority,
stale CAP binding, active ownership collision, or material CAP/slice drift.

## Decisions and Assumptions

- Feature owners remain authoritative for public condition, exact version,
  write/retry behavior, idempotency, availability, authorization, and state.
  Guidance owns only reviewed safe explanatory projection and exact mapping.
- Mapping identity is exact `(surface_key, condition_key, mapping_version)`.
  There is no route-, HTTP-status-, exception-, browser-, search-, or
  `latest`-derived substitution.
- Records contain only bounded public learner meaning, closed presentation-
  action kinds, exact Help references, applicability, publication and safe
  source facts. They contain no route, URL, raw exception, request, private
  state, learner identity, provider payload, command, or guarantee.
- Starter mappings cover the five SLI-0084 conditions: missing exact lesson
  version, uncertain practice write, stale/unavailable Saved-learning source,
  inert Project artifact, and provider/model execution not enabled by the
  AI-help choice.
- Safe-recovery and Project-artifact topics derive only from current canonical
  standards/ADRs. New text must preserve uncertainty and non-execution without
  freezing whole prose or fixture counts.

## In Scope

- Add strict executable schemas for one exact feature-guidance record and one
  exact surface-condition mapping, including closed status/action kinds,
  bounded safe text, exact Help references, applicability,
  source/publication facts, and canonical digests.
- Add approved and denied compatibility fixtures for exact identity,
  canonicalization, unknown/private fields, unsafe text, commands, arbitrary
  destinations, guarantee language, chronology, duplicate/dangling references,
  source drift, and varied valid record/action/topic shapes.
- Add framework-free immutable values, strict mapping adapters, canonical
  bytes/digests, exact lookup, whole-registry validation, and atomic exact-topic
  correlation against an already admitted Help corpus.
- Add reviewed safe-recovery and Project-artifact-use Help topics, update the
  corpus manifest/source fingerprints, and keep existing exact topics
  unchanged.
- Add a checked-in immutable starter registry for the five bounded conditions
  and admit it only after the complete Help corpus is valid.
- Add focused schema, compatibility, pure-domain, mapping, corpus-source,
  registry-admission, Unicode, confidentiality, failure, and anti-rigidity
  tests; reconcile direct contract, Guidance, architecture, and planning docs.

## Out of Scope

- Guidance application/public service, permission, HTTP API, OpenAPI, generated
  client, browser component, feature/error response, database, migration,
  event, job, analytics, deployment, dependency, or live-runner changes.
- Runtime health inspection, raw diagnostics, operational/support workflows,
  arbitrary commands/URLs, automatic retry/repair, provider/model execution or
  substitution, active artifact rendering/execution, external content, or
  availability/recovery/performance guarantees.
- Changing learner, feature, Project, Assessment, Personal-workspace, Content,
  identity, permission, write, retry, financial, grading, eligibility, or
  recommendation meaning.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Contract | Existing platform/contextual Help schemas and compatibility conventions | new `feature-guidance/v1` schemas, fixtures, and direct indexes | Freeze safe exact external meaning |
| Guidance pure core | Current topic/context values, canonicalization, and registry admission | new feature-guidance domain/mapping adapters plus exports | Validate exact records without host dependencies |
| Reviewed resources | Current corpus/manifest and canonical safety sources | two topics, feature-guidance registry, manifest and direct resource docs | Supply source-bound starter meaning and mappings |
| Focused tests | Existing Help schema/domain/corpus suites | new contract/unit suites and required corpus assertions | Prove safety, integrity, correlation, and flexibility |
| Architecture/planning | Guidance ownership and SLI-0084 state | direct listed architecture, slice, packet, and register paths | Keep ownership and evidence synchronized |

No unlisted feature module, application service, public API, generated client,
Web, persistence, migration, deployment, dependency, design-system, or planning
file is writable.

## Contracts and Interfaces

The additive record schema requires exact `guidance_id` and semantic
`guidance_version`; one closed `limited|unavailable|degraded` status; bounded
heading, reason, and protected/uncertain outcome; ordered safe action records;
exact Help references; applicability; publication; safe source references; and
the record digest.

The mapping schema requires exact `surface_key`, `condition_key`, semantic
`mapping_version`, exact record identity, safe source facts, publication facts,
and its mapping digest. Closed action kinds express presentation intent only:
retry the unchanged owning request, reload current owning state, return to the
owning task, open one exact Help topic, or download an inert artifact for
learner-managed use. No action holds a URL, route, command, credential, mutable
request, promise, or automatic side effect.

Canonical JSON uses UTF-8, sorted keys, compact separators, and admitted text
without implicit Unicode rewriting. A record or mapping digest excludes only
its own field. Exact lookup never substitutes a version or condition. Complete
registry admission rejects duplicate identities, invalid source facts,
guarantee/command/private content, bad chronology/digests, and any exact record
or Help topic reference that is absent.

## Dependencies and Parallel Safety

WRK-0173 and SLI-0083 are complete. This packet owns shared Guidance domain,
resource/corpus, contract-index, architecture, slice, and register paths, so it
is not parallel-safe with another writer on those surfaces. The API packet must
wait for these exact contracts and registry.

Claim from the current clean recorded base, run packet-start, atomically acquire
the exact write-scope files immediately before edits, complete this packet
before its successor, and keep local authority/disposition records ignored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Valid record and mapping | Every safe status/action, applicability, publication, source and exact topic fact is present | Projection and registry admission run | Immutable values round-trip to schemas and exact digests | schema/contract/unit |
| Exact lookup | A known surface/condition is paired with an absent mapping version | Registry lookup runs | No newer record or other condition is substituted | unit |
| Topic and record correlation | Mapping record and record topic identities all exist | Complete registry admission runs | Exact ordered identities and safe meaning are retained | unit/composition |
| Atomic failure | One record/mapping is duplicated, dangling, stale, unsafe, command-bearing, guarantee-bearing, or digest-inconsistent | Adapter loads the registry | Nothing becomes visible | schema/unit |
| Confidential shape | Route, URL, path, component, HTTP status, exception, identity, request, provider, command, secret, or unknown field is supplied | Schema/parser run | The value is rejected | schema/contract |
| Reviewed topics | Safe-recovery and Project-artifact topics load | Corpus admission runs | Current source fingerprints/digests validate and prior topics remain unchanged | source-binding/unit |
| Starter conditions | The immutable starter registry loads | Exact reads run for all five conditions | Each resolves to one reviewed record with exact Help references | unit |
| Flexible valid registry | Record/mapping/action/topic counts, order, Unicode, added valid conditions, and optional wording vary within bounds | Admission and lookup run | Invariants hold without fixed counts or prose | property/unit |
| No feature authority | Imports and fields are inspected | Architecture/security checks run | No runtime feature state, provider/model, write/retry, learner policy, or financial action enters Guidance | architecture/security |

## Verification Commands

Run packet/planning validation; focused feature-guidance JSON Schema and
compatibility tests; pure Guidance record/mapping/registry tests; existing
platform/contextual Help contract/domain/corpus tests; Python compilation; and
architecture/import/source-authority checks selected by the diff.

Also run security, active-content, private-path, advice-language, AI-authority,
learner-language, documentation, planning, dependency, whitespace,
controller-selected exact-candidate verification, independent technical
review, and aggregate readiness. Use the prepared Python runtime and record
only successful evidence.

## Documentation and Evidence Update

Document exact record/mapping semantics; closed actions; canonicalization;
atomic admission and topic correlation; source bindings; contribution and
confidentiality rules; non-authority/non-execution boundaries; exact candidate
and receipt; focused and aggregate checks; assumptions; and remaining
application/API/client/UI/live work. Keep packet, slice, and register state
synchronized without tracked local authority or disposition metadata.

## Stop Conditions

Stop for ambiguous feature status, retry/idempotency, exact-version, provider,
AI, artifact-execution, privacy, or advice meaning; a required feature/public-
contract change; Help becoming feature/operational/support authority; private
diagnostics; arbitrary URL/command; automatic remediation; guarantee claims;
runtime health checks; provider/model calls; active artifact behavior;
external content/support; persistence/API/UI/dependency expansion; identity,
tenancy, managed-cloud, queue, recovery, commercial, or public-hosting
behavior; stale CAP authority; collision; or material CAP-0020/SLI-0084 drift.

Do not stop for harmless whitespace, optional wording, valid fixture count or
order variation, nonfunctional styling, or another inconsequential issue. Fix
it in bounded scope or defer optional polish to CAP-0031.

## Required Handoff

Report `CAP-0020.SLI-0084.WRK-0174`; exact candidate and receipt; record/mapping
shapes; exact lookup and correlation; starter conditions; source fingerprints
and digests; canonicalization; atomicity; confidentiality; Unicode and anti-
rigidity; focused/architecture/security/documentation/planning/aggregate
checks; changed files; assumptions; and remaining API/client/UI/live seams.
Confirm no feature behavior, persistence, identity, provider/model execution,
artifact execution, remediation command, external content/action, learner
authority, or financial behavior changed.

## Planning History

- 2026-10-18: Authored just in time as the first dependency seam of SLI-0084.
  It freezes one transport-neutral exact guidance record/mapping contract,
  source-bound starter meaning, and immutable registry while deferring API and
  feature delivery. It conforms to the current CAP package and requires no
  lower-level approval.
