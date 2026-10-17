---
id: WRK-0153
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: SLI-0075
capability: CAP-0018
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/learner_model/README.md", "backend/src/financial_ai_academy/modules/learner_model/adapters/presentation_preference_contract.py", "backend/src/financial_ai_academy/modules/learner_model/domain/presentation_preferences.py", "backend/src/financial_ai_academy/modules/learner_model/ports/presentation_preference_contract.py", "backend/tests/contract/learner_presentation_preferences", "backend/tests/unit/learner_model/test_presentation_preference_contract.py", "backend/tests/unit/learner_model/test_presentation_preferences.py", "contracts/compatibility/learner-presentation-preferences/v1", "contracts/learning/README.md", "contracts/learning/learner-presentation-preferences/v1", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/learner-presentation-preferences-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0075-set-accessible-display-preferences.md", "docs/planning/work-packets/WRK-0153-freeze-learner-presentation-preference-contracts.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Freeze Learner Presentation Preference Contracts

## Objective and Deliverable

Freeze the additive `learner-presentation-preferences/v1` contract family and
pure Learner-model core for explicit text-size, text-spacing, reading-width,
and motion choices. Deliver executable JSON Schemas, a synthetic compatibility
corpus, deterministic conformance evidence, immutable framework-free domain
values, closed replacement/reset semantics, canonical hashing, and a narrow
transport-neutral parser/projector port and adapter.

The result is the stable input to the persistence/API packet and documents the
platform presentation boundary without changing runtime rendering. It creates
no database row, learner session, permission, HTTP operation, generated client,
browser route, design token, theme value, evidence, recommendation, provider
call, or external action.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-
root `docs/README.md`; route through the baseline, learning-adaptation,
architecture-contracts, interface-design, security-risk, testing-quality, and
delivery-planning context. Read the change-impact matrix, decision readiness,
CAP-0018, SLI-0075, SLI-0074, ADR-0005, ADR-0006, the Learner-model module
README and current preference implementation, contract architecture and
compatibility/versioning guidance, design-system standards, nearest contract
and test READMEs, and the concurrent-work protocol.

## Decisions and Assumptions

- Add a separate `learner-presentation-preferences/v1` family rather than
  widening the closed `learner-preferences/v1` family or adding presentation
  facts to Assessment, Curriculum, Adaptation, Identity, or Personal workspace.
- The four stored choices are explicit learner input: `text_size` is `default`
  or `larger`; `text_spacing` is `default` or `increased`; `reading_width` is
  `standard` or `focused`; and `motion` is `system` or `reduce`.
- Every valid choice preserves or improves the accepted accessible baseline.
  No value permits smaller text, tighter spacing, wider-than-standard reading,
  forced animation, hidden content, reduced contrast, or smaller targets.
- `default` means no application override beyond the accepted design-system
  baseline. `system` motion follows the device signal and `reduce` can only
  remove optional motion. Browser/OS zoom, forced colors, and protective motion
  settings remain authoritative for consuming adapters.
- Theme remains the existing platform-owned browser-local
  `system|light|dark` setting. It is not part of this learner-owned contract,
  history, export, digest, API, evidence, or headless meaning.
- A profile contains server-owned profile/learner identity, positive revision,
  the four closed choices, canonical creation/update times, and one lowercase
  SHA-256 digest. Empty persistence later projects revision-one safe defaults
  without a read-side write.
- Mutation intents contain one idempotency key, exact expected revision, and
  either a complete four-choice replacement or `reset_profile`. They cannot
  carry learner identity, medical/accessibility labels, CSS, design tokens,
  theme, policy, evidence, provider, model, or generated server facts.
- History contains at most 100 non-content summaries with revision, operation,
  time, and resulting digest. Export binds the exact current profile and
  history to explicit purpose and limitations.
- Canonical JSON hashing uses compact sorted-key direct UTF-8 bytes, excludes
  the digest itself, and performs no implicit Unicode normalization or ASCII
  escaping. Synthetic fixed vectors cover both accepted operations.
- The pure core may reuse established learner-preference helper patterns but
  must keep its public types and schema family distinct. It performs no I/O,
  identity resolution, permission check, clock/ID generation, or target
  mutation.

## In Scope

- Add Draft 2020-12 profile, mutation-intent, history, and export schemas under
  one versioned contract family.
- Add synthetic valid examples, fixed digest vectors, compatibility fixtures,
  and table-driven denials for unsupported versions/operations, extra fields,
  invalid identity/time/digest, incomplete replacement, arbitrary styling,
  theme, medical/inferred meaning, history mismatch, and forbidden internal
  data.
- Add a dependency-light conformance runner that validates schema versions,
  closed shapes, canonical digest, history/export correlation, bounds, and
  confidential shape without the application host or database.
- Introduce immutable framework-free presentation-preference values,
  canonical serialization/hashing, deterministic projection, complete
  replacement, and reset with explicit server facts.
- Add a narrow parser/projector port and adapter that maps JSON-compatible
  bytes and values to the pure domain without FastAPI, Pydantic, or PostgreSQL.
- Add focused contract and unit tests for defaults, every valid combination,
  replacement, reset, export/history, fixed digests, malformed inputs,
  confidentiality, side-effect freedom, and anti-rigidity across IDs, times,
  revisions, valid combinations, and compatible surrounding application copy.
- Document Learner-model ownership, explicit-versus-inferred meaning, safe
  value semantics, theme exclusion, consuming-adapter precedence, privacy and
  authority limits, hashing, and later consumer obligations.

## Out of Scope

Application services; session or permission composition; repositories;
PostgreSQL; migrations; replay persistence; public facades; HTTP/FastAPI/
Pydantic; OpenAPI; generated clients; browser storage; browser routes; preview
or settings UI; executable design tokens or root attributes; theme changes;
AI-assistance or notification preferences; inferred needs; assistive-technology
detection; Assessment evidence; competency/mastery; Adaptation; models or
providers; arbitrary CSS; font downloads; organizations/tenancy; external
actions; deployment composition; dependency or lockfile changes.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | existing learner-preference and compatibility families | new `learner-presentation-preferences/v1` and compatibility directories plus learning contract catalog | Freeze additive explicit presentation meaning without widening the existing family |
| Contract evidence | dependency-light runners, canonical digest vectors, closed-shape and confidentiality denials | new learner-presentation contract runner, fixtures, and focused tests | Prove closure, hashing, safe values, privacy, and anti-rigidity |
| Learner-model core | current preference domain and parser/projector conventions | new presentation domain, contract port/adapter, focused unit tests, bounded README update | Establish inward-pointing typed meaning without application or persistence |
| Architecture guidance | contract ownership and application boundaries | new presentation contract page plus bounded contract-architecture update | Record learner ownership, local-theme exclusion, and protective precedence |
| Planning evidence | SLI-0075, WRK-0153, register | listed planning files | Keep lifecycle and next seam synchronized |

No existing learner-preference, completion, practice, project, Curriculum,
Assessment, Adaptation, Identity, or Personal-workspace schema/fixture/runtime;
public facade; OpenAPI/client; persistence/migration; UI; design token; theme
adapter; dependency; provider; or deployment composition may change.

## Contracts and Interfaces

`learner-presentation-preference-profile-v1` is one closed document containing
exact server identity/revision/time facts and the four closed presentation
choices. Profile identity and learner identity are distinct bounded opaque
identifiers. All four choice fields are required, so consumers never merge a
partial preference object or invent a missing-value precedence rule.

`learner-presentation-preference-mutation-intent-v1` contains an idempotency
key, exact expected revision, and one closed operation. `replace_preferences`
contains all four choices. `reset_profile` contains no replacement body and
returns the safe `default`, `default`, `standard`, `system` combination in the
next revision. Neither operation can select a learner or set identity,
revision, time, digest, CSS, theme, evidence, or policy.

`learner-presentation-preference-history-v1` contains ordered summaries whose
revisions are positive, unique, increasing, and no newer than the current
profile. `learner-presentation-preference-export-v1` binds that exact profile
and history to explicit purpose, limitations, schema version, and canonical
export time. History and export contain no prior values, medical label,
inferred trait, session, permission, storage, provider, evidence, score,
recommendation, financial meaning, or browser-local theme.

The pure mutation function receives a validated current profile, validated
intent, and explicit canonical time. It returns the next profile plus a change
summary or a stable bounded `learner_presentation_preferences.*` error. Exact
replay remains the next application/repository packet's responsibility. The
parser/projector accepts JSON-compatible bytes/values and returns immutable
values or safe contract errors; later adapters may apply validated choices but
may not let them weaken accessibility baselines or acquire evidence/policy
authority.

## Dependencies and Parallel Safety

CAP-0001, CAP-0017, and SLI-0074 are complete; CAP-0018 authority is current;
SLI-0075 is ready; and no durable decision gate remains inside this boundary.
WRK-0153 has no WRK dependency. It owns the new contract family and shared
Learner-model/architecture/planning files, so it is not parallel-safe with
another packet changing those paths. It must complete before JIT-B is reserved
or authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Safe default profile | Valid server identity, revision, and times with the four baseline choices | Profile parsing/projecting runs | One deterministic profile round-trips with its exact digest and no write | schema/runner/unit |
| All valid choices | Every allowed four-choice combination | Validation, projection, hashing, and round-trip run | All combinations retain exact explicit meaning without diagnosis, inference, or evidence | parameterized contract/unit |
| Closed replacement | A complete valid replacement and explicit server time | Pure mutation runs | One deterministic next profile and non-content summary result | schema/unit |
| Safe reset | A non-default profile receives `reset_profile` | Pure mutation runs | The next revision contains exactly the four baseline choices and a reset summary | unit/contract |
| Partial or unsafe input | A missing choice, unknown value, arbitrary CSS/scale, theme, medical label, or extra field is supplied | Parsing or validation runs | Input fails closed with a bounded confidential error and no state change | schema/runner/unit |
| History and export | Current profile and correlated bounded summaries are supplied | History/export projection runs | Revisions, digests, purpose, limitations, and export time correlate without prior values or internal data | schema/runner/unit |
| Canonical digest | Fixed profile vectors are hashed independently and in production | Hashing runs | Compact sorted direct UTF-8 bytes produce the expected lowercase digest | vectors/runner/unit |
| Protective semantics | The contract and architecture docs are inspected | Consumer obligations are evaluated | No valid value can request a weaker baseline; device/browser protections retain precedence | contract/architecture |
| Theme separation | Profile, mutation, history, export, errors, and docs are scanned | Theme fields and local-storage authority are inspected | No browser-local theme value enters the learner-owned family or headless meaning | runner/unit/docs |
| No side effects | Parser, projector, hashing, and mutation run repeatedly | Process capabilities and collaborators are inspected | No database, clock, network, filesystem, provider, event, AI, UI, or other-module effect occurs | unit/architecture |
| Anti-rigidity | IDs, revisions, canonical times, valid combinations, fixture order, and compatible surrounding copy vary | The focused corpus runs | Meaningful invariants hold without exact prose, fixture-count, generated-value, or UI assumptions | parameterized contract/unit |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/learner_presentation_preferences backend/tests/unit/learner_model/test_presentation_preference_contract.py backend/tests/unit/learner_model/test_presentation_preferences.py
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0153-freeze-learner-presentation-preference-contracts.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Run the affected-check plan and any focused contract-catalog or architecture
regression it selects. Submit one exact candidate, create a fresh qualifying
receipt, and obtain one independent technical disposition. Add no dependency
or lockfile change.

## Documentation and Evidence Update

Document explicit-versus-inferred meaning, Learner-model ownership, the four
safe value sets, complete replacement/reset semantics, theme exclusion,
protective browser/OS precedence, history/export limitations, canonical
hashing, confidentiality, and unchanged evidence/policy owners. Keep the
module README, contract architecture, learning contract catalog, SLI-0075,
WRK-0153, and register synchronized.

Completion evidence records exact focused and affected checks, compatibility,
confidentiality and anti-rigidity meaning, changed files, assumptions,
environment qualifications not performed, and residual risks. Verification
receipts and technical review records remain only in ignored local control-
plane storage; tracked files contain no approval or reviewer metadata/history.

## Stop Conditions

Stop for inferred or medical traits; assistive-technology detection; arbitrary
CSS/scale/font values; smaller text/targets; tighter spacing; reduced contrast;
forced animation; hidden content/actions; browser state or theme used as
domain/API authority; preferences used as Assessment evidence, competency,
mastery, eligibility, permission, grading, recommendation, financial
suitability, or irreversible action; widening the existing preference family;
persistence/API/UI/design-token change; cross-module storage access; a
breaking contract; identity/tenancy/managed-cloud expansion; provider/model/
network/credential use; new dependency; private-data leakage; conflicting
canonical sources; active scope collision; stale authority; or material
CAP-0018/SLI-0075 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally within scope or defer optional polish to
CAP-0031.

## Required Handoff

Report the exact candidate; contract identifiers and safe value sets;
replacement, reset, history/export, digest, confidentiality, theme-separation,
protective-precedence, and denial invariants; focused, architecture, security,
affected, aggregate, receipt, and independent-review results; changed files;
documentation impact; assumptions; unqualified environment checks; and
residual gaps. Confirm that no persistence, migration, public application or
HTTP operation, OpenAPI/generated client, browser UI, design token, runtime
theme/accessibility behavior, AI/notification preference, evidence/competency
state, recommendation, inferred trait, provider, external action, or execution
behavior changed. Leave JIT-B dependency-ready.

## Planning History

- 2026-10-17: Authored just in time after SLI-0075 refinement. The packet
  freezes the additive learner-owned presentation-preference contract and pure
  core while leaving persistence/API, runtime presentation, UI, and live
  qualification to dependency-ordered packets. It remains inside CAP-0018 and
  requires no lower-level approval.
