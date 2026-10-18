---
id: WRK-0170
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0083
capability: CAP-0020
depends_on: [WRK-0168]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/guidance/adapters/__init__.py", "backend/src/financial_ai_academy/modules/guidance/adapters/contextual_help_contract.py", "backend/src/financial_ai_academy/modules/guidance/adapters/immutable_context_registry.py", "backend/src/financial_ai_academy/modules/guidance/adapters/immutable_corpus.py", "backend/src/financial_ai_academy/modules/guidance/domain/__init__.py", "backend/src/financial_ai_academy/modules/guidance/domain/contextual_help.py", "backend/src/financial_ai_academy/modules/guidance/resources/README.md", "backend/src/financial_ai_academy/modules/guidance/resources/contextual-help/v1", "backend/src/financial_ai_academy/modules/guidance/resources/platform-help/v1/data-meaning.json", "backend/src/financial_ai_academy/modules/guidance/resources/platform-help/v1/source-and-history.json", "backend/tests/contract/contextual_help", "backend/tests/unit/guidance/test_contextual_help.py", "backend/tests/unit/guidance/test_immutable_corpus.py", "contracts/README.md", "contracts/compatibility/README.md", "contracts/compatibility/contextual-help/v1", "contracts/guidance/README.md", "contracts/guidance/contextual-help/v1", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/platform-help-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0083-open-contextual-method-and-limitation-help.md", "docs/planning/work-packets/WRK-0170-freeze-contextual-help-contracts-and-registry.md"]
generated_artifacts: []
base_revision: 547fbe0ff3df9f13d5d8349c36f8ffffeb7d68bd
claim_id: WRK-0170:ff3743d0-a778-47a6-9fbb-0314d4f8d578
claimed_by: codex-cap-0020
claimed_at: 2026-10-18T04:07:22Z
---

# Agent Work Packet: Freeze Contextual Help Contracts and Registry

## Objective and Deliverable

Establish the additive `contextual-help/v1` exact-context contract, pure
Guidance validation/digest core, reviewed starter explanation topics, and an
atomically admitted immutable context registry. Later packets can expose and
render one exact context without inventing mappings in feature APIs or the
browser.

The deliverable is a transport-neutral, source-bound read model. It does not
add an application operation, HTTP route, OpenAPI operation, generated client,
feature link, persistence schema, provider/model call, or live topology.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Revalidate the routed architecture-contract,
interface, security-risk, testing-quality, and delivery-planning context; the
change-impact matrix; decision readiness; CAP-0020; SLI-0083; completed
SLI-0082; current `platform-help/v1` contracts, core, checked-in corpus,
consumers and tests; canonical method, AI, provenance, data-distinction, and
education-versus-advice sources; and every nearest README.

The Required Startup was performed and reported before this planning change.
The parent CAP package remains approved and current, SLI-0083 is ready, its
SLI-0082 dependency is complete, and no unresolved decision applies. Stop for
conflicting authority, stale CAP binding, active ownership collision, or
material CAP/slice drift.

## Decisions and Assumptions

- Guidance owns the safe contextual map and explanatory projection only.
  Feature modules and canonical product, domain, architecture, method, AI, and
  risk sources retain meaning and behavior authority.
- Context identity is exact `(context_key, context_version)`. There is no
  `latest`, route-derived, search-derived, or browser-owned substitution.
- A context record contains only safe public feature applicability and ordered
  exact Help topic references. It contains no route, URL, component, raw
  markup, repository path, learner identity, permission, prompt, provider,
  model, mutable feature state, command, or external action.
- The initial closed context set covers already-delivered lesson publication,
  practice result, Project artifact/result, and AI-assistance preference
  surfaces. It may reference current exact method, AI-control, and
  education-not-advice topics plus the new source/history and data-meaning
  topics authored from current canonical sources.
- Registry admission occurs only after the exact platform-help corpus is
  admitted. Every reference must resolve to one exact approved topic in that
  corpus; one invalid context rejects the complete registry.
- New explanation topics preserve plain learner meaning and exact source
  fingerprints without turning whole prose, fixture counts, incidental JSON
  order, or optional wording into rigid compatibility rules.

## In Scope

- Add a strict `contextual-help/v1` JSON Schema for one exact context with a
  closed relationship/purpose set, learner-readable link labels, feature
  applicability, publication facts, source references, exact topic references,
  and canonical digest.
- Add synthetic approved and denied compatibility fixtures covering exact
  identity, unknown fields, confidentiality, canonicalization, chronology,
  duplicate/dangling references, unsafe text, and flexible valid shapes.
- Add pure immutable Guidance context values, strict mapping projection,
  canonical bytes/digest, exact lookup, whole-registry validation, and atomic
  exact-topic correlation against an already admitted platform-help corpus.
- Add reviewed source/history and data-meaning exact Help topics with current
  canonical source bindings, then update the corpus manifest/fingerprint
  admission without changing existing topic identities or meaning.
- Add a checked-in immutable starter context registry covering the bounded
  feature contexts and admitting it through a filesystem adapter at
  composition-independent construction time.
- Add focused schema, contract, domain, mapping, corpus-source-binding,
  registry-admission, Unicode, and anti-rigidity tests.
- Reconcile direct Guidance resource, contract, architecture, planning, and
  contribution documentation.

## Out of Scope

- Guidance application/public operation, authorization, HTTP API, OpenAPI,
  generated client, route model, browser component, feature integration, live
  runner, database, migration, event, analytics store, or deployment change.
- Changing an existing feature contract or domain record, serving repository
  documents, mutable authoring, external URLs/content, semantic/vector search,
  personalization, tracking, recommendation, or search-ranking changes.
- Model/provider execution, AI-generated canonical help, operational command
  execution, learner-specific advice, grading, eligibility, mastery,
  competency, suitability, financial calculation/action, or support guarantee.
- SLI-0084 degraded/troubleshooting behavior, SLI-0085 cumulative closure,
  managed cloud, tenancy, recovery, licensing, legal/commercial policy, or
  separate headless-AI behavior.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Context contract | Existing platform-help and compatibility conventions | `contracts/guidance/contextual-help/v1`, matching fixtures, direct indexes | Freeze executable exact external meaning |
| Guidance pure core | Current topic values, canonicalization, corpus validation | new contextual-help domain and mapping adapter files plus exports | Validate exact immutable contexts without host dependencies |
| Reviewed resources | Current corpus, source fingerprint admission, canonical sources | two exact Help topics, immutable context registry, direct resource docs and adapter admission | Provide source-bound starter meaning and mappings |
| Focused tests | Platform-help schema/domain/corpus suites | new contextual-help contract/unit suites | Prove safety, integrity, exact correlation, and anti-rigidity |
| Architecture | Guidance contract/module ownership docs | direct contract architecture, platform-help contract, module map | Record context ownership and non-authority boundaries |
| Planning | SLI-0083, this packet, register | listed planning files | Keep delivery state and evidence synchronized |

No unlisted public API, application service, feature module, Web, generated
client, persistence, migration, deployment, dependency, design-system, or
other planning file is writable.

## Contracts and Interfaces

The additive `contextual-help/v1` schema represents one immutable exact
context. Required fields are schema version, context key/version, feature
label, applicability, ordered Help references, approved publication facts,
safe canonical-source facts, and canonical context digest. Each Help reference
contains an exact topic ID/version, a closed purpose (`method`, `source`,
`data_meaning`, `ai_boundary`, or `education_boundary`), and a bounded safe
learner-facing label.

Canonical JSON uses UTF-8, sorted keys, compact separators, and admitted text
without implicit Unicode rewriting. The context digest excludes only its own
field. Exact lookup never substitutes a version. A registry rejects duplicate
keys, duplicate reference identities or purposes when prohibited, self-
inconsistent applicability/source facts, bad chronology/digests, and any
reference absent from the admitted Help corpus before exposing any context.

The pure registry accepts immutable values and an exact topic-identity set; it
has no filesystem, FastAPI, SQLAlchemy, provider, network, clock, random,
browser, feature, grading, learner-state, or financial-action dependency. JSON
projection and checked-in resource loading remain adapters around that core.

## Dependencies and Parallel Safety

WRK-0168 is complete and supplies the exact platform-help corpus/API/client
baseline and live evidence. This packet owns shared Guidance domain/resource,
contract-index, architecture, slice, and register paths, so it is not parallel-
safe with another writer on those surfaces. The API packet must wait for this
packet's exact contracts and registry to complete.

Claim from the current clean recorded base, run packet-start, atomically acquire
the exact files immediately before edits, and retain one owner through
verification. Approval and reviewer records remain only in ignored local
storage.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Valid exact context | All allowed purposes, applicability, publication, source, and exact topic facts are present | Mapping and registry admission run | One immutable context round-trips to the schema and exact digest | schema/contract/unit |
| Exact lookup | A valid context key is paired with an absent version | Registry lookup runs | No other version is substituted | unit |
| Topic correlation | Every referenced exact topic exists in the admitted corpus | Registry admission runs | Ordered references retain exact identity and safe label/purpose | unit/composition |
| Dangling topic | A context names an unknown ID or wrong version | Registry admission runs | The complete registry is rejected before partial visibility | unit |
| Canonical digest | JSON key order and whitespace vary | Canonicalization runs | Equal admitted meaning has the same digest without Unicode rewriting | contract/unit |
| Safe public shape | A route, URL, path, component, identity, permission, prompt, provider, command, or unknown field is supplied | Schema and parser run | The record is rejected | schema/contract |
| Reviewed starter topics | Source/history and data-meaning topics are loaded | Corpus admission runs | Exact source fingerprints and topic digests validate and current topics remain unchanged | source-binding/unit |
| Atomic registry | One of several contexts is duplicated, malformed, stale, or digest-inconsistent | Adapter loads the registry | No context becomes visible | unit |
| Flexible valid registry | Context/reference counts, order, Unicode labels, extra valid contexts, and optional wording vary within bounds | Admission and lookup run | Declared invariants hold without fixed fixture counts or prose | property/unit |
| No feature authority | Domain imports and record fields are inspected | Architecture/security checks run | No feature internals, mutable state, model/provider, learner policy, or financial action enters Guidance | architecture/security |

## Verification Commands

Run packet and planning validation; focused contextual-help JSON Schema and
compatibility tests; pure Guidance context and immutable-registry tests; the
existing platform-help contract/domain/corpus suites; Python compilation; and
architecture/import and source-authority checks selected by the diff.

Also run security, active-content, private-path, advice-language, AI-authority,
learner-language, documentation, planning, dependency, and whitespace checks;
controller-selected exact-candidate verification; one independent technical
review; and `python dev-tools/agent/check_ready.py`. Use the repository-prepared
Python runtime. Record only successful checks.

Harmless whitespace, optional prose, fixture ordering, and nonfunctional
presentation do not reopen approval or require an unrelated full review loop.

## Documentation and Evidence Update

Document the exact context contract; purpose/reference semantics;
canonicalization/digest; registry atomicity and topic correlation; reviewed
source/history and data-meaning source bindings; contribution rules;
confidentiality and non-authority boundaries; exact candidate and receipt;
focused, architecture, security, documentation, planning, and aggregate checks;
assumptions; and remaining API/client/UI/live work. Keep packet, slice, and
register state synchronized without tracked approval or reviewer metadata.

## Stop Conditions

Stop for ambiguity in canonical method, provenance, data distinction, AI, or
advice meaning; a required feature-contract/domain-record change; Help becoming
product/domain/risk/feature authority; breaking platform-help compatibility;
serving repository documents or paths; arbitrary URL or active content;
mutable/user-authored or external help; semantic search, personalization,
tracking, model/provider execution, operational commands, learner-specific
advice, suitability, grading, eligibility, mastery, competency, or financial
action; persistence/API/UI/dependency expansion; identity/tenancy, managed-
cloud, recovery, legal/commercial, or public-hosting behavior; stale CAP
authority; active collision; or material CAP-0020/SLI-0083 drift.

Do not stop for harmless whitespace, optional wording, valid fixture count or
order variation, nonfunctional styling, or another inconsequential issue. Fix
it in bounded scope or defer optional polish to CAP-0031.

## Required Handoff

Report `CAP-0020.SLI-0083.WRK-0170`; exact candidate and receipt; context/topic
contract shapes; exact lookup and topic correlation; source fingerprints and
digests; canonicalization; registry atomicity; confidentiality; Unicode and
anti-rigidity; focused, architecture, security, documentation, planning, and
aggregate checks; changed files; assumptions; and remaining application/API,
client/UI, and live gaps. Confirm no feature behavior, persistence, identity,
provider/model, external content/action, learner authority, or financial
behavior changed.

## Planning History

- 2026-10-18: Authored just in time as the first dependency seam of approved
  SLI-0083. The packet freezes one transport-neutral exact context contract,
  source-bound starter meaning, and immutable registry while deferring API and
  feature delivery to dependent packets. It conforms to the approved CAP
  package and requires no lower-level approval.
- 2026-10-18: Activated from clean recorded base `547fbe0` after the packet
  start gate confirmed current CAP authority, refined slice membership,
  completed dependencies, exact bounded scope, and no active collision.
- 2026-10-18: Refined the exact test scope before implementation to include the
  existing immutable-corpus manifest test that must recognize the two new
  required source-bound topics. The packet outcome and CAP boundary are
  unchanged and no approval is required.
