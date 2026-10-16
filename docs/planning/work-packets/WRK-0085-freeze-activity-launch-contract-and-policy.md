---
id: WRK-0085
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: SLI-0024
capability: CAP-0005
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/adaptation/README.md", "backend/src/financial_ai_academy/modules/adaptation/domain/activity_launch.py", "backend/src/financial_ai_academy/modules/adaptation/public.py", "backend/tests/architecture/test_module_boundaries.py", "backend/tests/contract/adaptation_activity_launch/__init__.py", "backend/tests/contract/adaptation_activity_launch/runner.py", "backend/tests/contract/adaptation_activity_launch/test_conformance.py", "backend/tests/contract/adaptation_navigation/test_conformance.py", "backend/tests/unit/adaptation/test_activity_launch_policy.py", "contracts/learning/README.md", "contracts/learning/adaptation/v1/README.md", "contracts/learning/adaptation/v1/activity-launch.schema.json", "contracts/compatibility/adaptation-activity-launch/v1/README.md", "contracts/compatibility/adaptation-activity-launch/v1/approved/launch.json", "contracts/compatibility/adaptation-activity-launch/v1/cases/denials.json", "docs/architecture/contracts/adaptive-navigation-state-contract.md", "docs/assurance/architecture-verification.md", "docs/planning/work-packets/WRK-0085-freeze-activity-launch-contract-and-policy.md", "docs/planning/vertical-slices/SLI-0024-open-and-return-to-an-eligible-activity.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 532cfc8786e45761fd778511fe04ca596a769979
claim_id: WRK-0085:835077da-624a-4f5a-94f3-07634e94312d
claimed_by: codex-cap-0005
claimed_at: 2026-10-16T12:09:01Z
---

# Agent Work Packet: Freeze the Activity-Launch Contract and Policy

## Objective and Deliverable

Define and implement the transport-neutral `activity-launch-v1` success
contract and a pure Adaptation domain decision that resolves one exact eligible
lesson activity into one exact same-origin lesson destination. The decision
must consume the already validated Curriculum graph and Navigation-state v1
projection, revalidate their identity/digest closure, and refuse locked,
unavailable, missing, malformed, or unsupported activities without returning a
destination.

The completed packet is independently useful: the public Adaptation surface can
resolve a launch from exact accepted inputs and the reusable conformance corpus
can qualify later application/API adapters. It does not compose repositories,
resolve learner identity, expose HTTP, generate a client, or change the UI.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-root
`docs/README.md`. Route through the baseline, learning-adaptation,
architecture-contracts, interface-design, testing-quality, and delivery-
planning context. Read CAP-0005, SLI-0024, completed SLI-0022/SLI-0023 and
WRK-0062, decision readiness, ADR-0005, ADR-0007, ADR-0014, the Curriculum
graph and Navigation-state contracts/schemas/compatibility fixtures, Adaptation
domain/public surfaces and README, Curriculum public graph types, module-
boundary tests, architecture verification, and the nearest contract READMEs.

## Decisions and Assumptions

- Adaptation owns the launch decision because it already owns deterministic
  eligibility over exact Curriculum and Learner-model facts. Curriculum keeps
  activity/placement meaning; Content and Assessment ownership do not move.
- The pure decision receives one `CurriculumGraph`, one
  `NavigationStateProjection`, and one activity ID. Later application work is
  responsible for producing both accepted inputs from current public gateways.
- Launch is permitted only for an exact lesson activity whose source is
  available and whose eligibility is `eligible`. A completed lesson remains
  eligible under the accepted v1 policy and may resolve for review.
- Version 1 supports lessons only. An assessment activity is a bounded
  unsupported launch, not a new Assessment execution path or inferred
  completion meaning.
- The destination is deterministically `/learn/placements/{placement_id}` from
  the validated lesson reference. No caller or provider supplies a URL.
- The success value retains exact graph, projection, placement, and package
  identity/provenance. It contains no learner identity and creates no durable
  record, grant, recommendation, or evidence.

## In Scope

- Closed JSON Schema for `activity-launch-v1` and a compact approved fixture.
- Dependency-light compatibility runner plus positive and denial fixtures for
  exact output, missing/mismatched closure, locked/unavailable activity,
  unknown activity, unsupported assessment, unsafe identity, and output
  privacy/field closure.
- Pure immutable launch request/result types, stable bounded error codes, exact
  validation, deterministic destination construction, and payload mapping.
- Public Adaptation exports for the pure decision without importing another
  module's internals. The composed service/protocol operation is deferred to
  JIT-B, when current public gateways are available to supply fresh inputs.
- Focused unit tests for eligible entry/prerequisite, completed review,
  optional and unbranched activities, sibling order, projection mismatch,
  refusal paths, deterministic output, and no mutation.
- Architecture/public-surface assertions plus contract, module, assurance,
  slice, packet, and register documentation.

## Out of Scope

Application gateways, repository composition, learner/session resolution,
permissions, HTTP endpoints, OpenAPI, generated TypeScript, browser actions,
lesson return context, CSS, migrations, persistence, events, telemetry,
ranking, recommendation, automatic next-step selection, model inference,
mastery, assessment execution, or live browser qualification.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Existing inputs | Curriculum public graph and Adaptation navigation models/contracts | Adaptation navigation schema-enumeration assertion only | Consume accepted exact v1 meaning without revision and keep the shared schema inventory exact |
| Launch domain | Adaptation domain/public surface and README | new activity-launch module, bounded public exports, README | Own the pure deterministic decision and reusable result |
| Executable contract | learning/adaptation contract family and catalog | one new closed schema plus catalog/readme entry | Freeze portable success shape before application composition |
| Compatibility | existing graph/navigation runners and fixtures | new activity-launch runner, approved fixture, denial corpus, conformance test | Prove implementations share exact success/refusal meaning |
| Architecture evidence | module-boundary tests, navigation contract, verification map | bounded launch assertions and documentation | Preserve owner direction and record direct evidence |
| Planning | CAP-0005, SLI-0024, register | this packet, parent slice, register | Keep JIT seam, lifecycle, and evidence synchronized |

## Contracts and Interfaces

The pure request contains one validated exact graph, one exact Navigation-state
v1 projection, and one activity ID. The decision verifies schema versions;
curriculum ID/version/digest equality; complete, unique, graph-ordered state
coverage; projection digest integrity; selected activity membership; lesson
reference validity; and the selected state's available/eligible result. It must
not infer or recompute eligibility from partial fields.

The closed success mapping contains exactly:

- `schema_version` fixed to `1.0.0`;
- exact curriculum ID, version, and graph digest;
- selected activity ID;
- navigation projection digest and evaluation timestamp;
- lesson placement ID, package ID, package version, and package digest; and
- a same-origin destination matching `/learn/placements/{placement_id}`.

Stable domain errors distinguish invalid context/closure, activity not found,
locked, unavailable, and unsupported kind. Errors expose only a bounded code,
message, and sanitized public reference. They never include a destination,
learner/provider identity, answers, scores, raw source payload, stack trace,
storage detail, or approval/reviewer data.

## Dependencies and Parallel Safety

Completed SLI-0023 supplies the immutable graph and deterministic projection
contracts. This is SLI-0024's first packet and has no packet dependency. It is
not parallel-safe with CAP-0006 work because the current allocator reports
incomplete compatibility evidence and this packet touches shared Adaptation,
architecture, contract-catalog, and planning surfaces. JIT-B must consume this
public contract without changing v1 meaning.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Eligible lesson | Exact matching graph/projection and an available eligible lesson | Launch resolves | The exact placement/package fields and fixed same-origin destination are returned | unit + contract |
| Completed lesson review | Exact completion exists and policy still marks the lesson eligible | Launch resolves | The same exact lesson resolves without changing completion evidence | unit |
| Locked lesson | A prerequisite is incomplete | Launch resolves directly against the current projection | A stable locked error returns with no destination | unit + denial fixture |
| Unavailable lesson | Activity or completion source is unavailable | Launch resolves | A stable unavailable error returns with no fallback version | unit + denial fixture |
| Assessment activity | The selected graph activity is an assessment | Launch resolves | A stable unsupported-kind error returns and no Assessment behavior is inferred | unit + denial fixture |
| Unknown or malformed activity | ID is invalid or absent from the exact graph | Launch resolves | Invalid-context or not-found error is bounded and deterministic | unit + denial fixture |
| Mismatched projection | Curriculum ID/version/digest, coverage, order, timestamp, or projection digest is stale/tampered | Launch resolves | The whole request fails closed before activity state is trusted | unit + denial fixture |
| Flexible graph | Activity is optional, unbranched, in a shared same-kind branch, or siblings are reordered | Launch resolves | Only exact state/reference meaning matters; no graph-shape special case appears | anti-rigidity unit |
| Stable public output | The same exact inputs are resolved repeatedly | Payload is encoded | Canonical fields/order/values match the approved fixture and contain no private data | contract conformance |

## Verification Commands

- `backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/adaptation_activity_launch backend/tests/unit/adaptation/test_activity_launch_policy.py backend/tests/architecture/test_module_boundaries.py`
- `backend/.venv/Scripts/python.exe -m compileall -q backend/src/financial_ai_academy/modules/adaptation backend/tests/contract/adaptation_activity_launch backend/tests/unit/adaptation`
- `backend/.venv/Scripts/python.exe dev-tools/architecture/check_architecture.py`
- `backend/.venv/Scripts/python.exe dev-tools/planning/check_planning.py`
- `backend/.venv/Scripts/python.exe dev-tools/documentation/check_docs.py`
- `backend/.venv/Scripts/python.exe dev-tools/agent/check_ready.py`
- `git diff --check`

No database, Docker, API, generated-client, TypeScript, component, or browser
suite is required because this packet stops at the transport-neutral domain and
contract boundary.

## Documentation and Evidence Update

Update the Adaptation and contract READMEs, navigation/launch architecture
contract, architecture-verification map, SLI-0024, this packet, and planning
register. Record exact positive, refusal, closure, privacy, anti-rigidity,
architecture, compilation, documentation, planning, readiness, and whitespace
results; schema compatibility; no-migration impact; assumptions and known
gaps; and confirmation that application/API/UI and durable evidence remain
unchanged.

## Stop Conditions

Stop for ambiguous owner direction; a need to change graph or navigation-state
v1 meaning; caller-supplied learner, destination, placement, package, or
eligibility; partial/stale projection acceptance; assessment execution; a new
completion meaning; persistence or migration; ranking, recommendation, model,
mastery, provider, external service, permission, identity, tenancy, recovery,
or commercial policy; breaking contract behavior; active file overlap; stale
CAP binding; or material SLI/CAP drift.

Do not stop or request review for harmless formatting, advisory prose, or
nonfunctional style outside this packet. Correct bounded implementation or test
defects within the frozen acceptance set without creating a new approval stage.

## Required Handoff

Report the pure request/result/error surface, schema and compatibility corpus,
destination derivation, exact closure checks, public exports, architecture
boundary, test and readiness results, documentation impact, assumptions,
residual limitation that only lesson activities launch in v1, unresolved
decisions, and confirmation that application, HTTP, generated clients, UI,
persistence, evidence, models, providers, and external services did not change.
Leave JIT-B dependency-ready or return one bounded blocker.

## Planning History

- 2026-10-16: Authored just in time as SLI-0024 JIT-A after its deterministic
  protected-launch design was refined. The packet freezes one reusable pure
  contract and policy seam before application/API composition, conforms to the
  approved CAP package, and adds no decision or lower-level approval gate.
- 2026-10-16: Activated from base
  `a34a94cedf72aef5fbbf3b3210f29cef29ec92b9` after the implementation gate
  prerequisites confirmed current CAP authority, completed slice dependencies,
  bounded write scope, and no unresolved decision or ownership collision.
- 2026-10-16: Released before implementation to add the existing Navigation
  contract test that deliberately enumerates every Adaptation schema. This
  bounded compatibility-test correction does not change the packet outcome,
  contract meaning, acceptance set, or CAP authority and requires no new
  approval or review cycle.
- 2026-10-16: Reclaimed from corrected base
  `532cfc8786e45761fd778511fe04ca596a769979` after the expanded exact scope
  passed planning, documentation, and whitespace checks.
- 2026-10-16: Independent R01 review required four bounded corrections. The
  pure launch function remains public, while its composed service/protocol
  member is deferred together to JIT-B so the current service continues to
  satisfy its declared operations contract. The same correction also closes
  navigation validation, prerelease package compatibility, and unsupported-
  kind precedence without expanding this packet's boundary.
