---
id: WRK-0092
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0026
capability: CAP-0006
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/assessment/README.md", "backend/src/financial_ai_academy/modules/assessment/adapters/practice_contract.py", "backend/src/financial_ai_academy/modules/assessment/domain/practice.py", "backend/src/financial_ai_academy/modules/assessment/ports/practice_definition.py", "backend/tests/contract/assessment_practice", "backend/tests/unit/assessment/test_practice_contract.py", "contracts/compatibility/assessment-practice/v1", "contracts/learning/README.md", "contracts/learning/assessment/practice/v1", "docs/architecture/contracts/assessment-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0026-open-versioned-practice-activity.md", "docs/planning/work-packets/WRK-0092-freeze-versioned-practice-contracts.md"]
generated_artifacts: []
base_revision: 4aeec17b8e32947dcfc7277abd57eebbe5f4dbe3
claim_id: WRK-0092:351cabf6-0a5d-4e66-ad20-101fac593e2c
claimed_by: codex-cap-0006
claimed_at: 2026-10-16T14:07:40Z
---

# Agent Work Packet: Freeze Versioned Practice Contracts

## Objective and Deliverable

Freeze a new additive Assessment-owned practice-definition and answer-safe
presentation contract family for single-select, multiple-select, and fixed-
decimal numeric items. Deliver executable schemas, a synthetic compatibility
corpus, deterministic conformance and parser/domain evidence, and synchronized
contract/module documentation. The result is the stable transport-neutral
input to the next API-composition packet; it exposes no HTTP operation and
creates no attempt, score, completion, or learner state.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-
root `docs/README.md`; route through the baseline, learning-adaptation,
architecture-contract, security-risk, testing-quality, and delivery-planning
context. Read the change-impact matrix, decision readiness, CAP-0006,
SLI-0026, ADR-0005, ADR-0007, the Assessment and content-package contracts,
contract/versioning standards, Assessment module README, current Assessment v1
schemas and compatibility runner, private definition parser, domain values,
public surface, service, contract/unit tests, nearest contract READMEs, and
concurrent-work rules.

## Decisions and Assumptions

- Create a separate additive `assessment/practice/v1` family rather than
  broadening the closed CAP-0001 single-select knowledge-check v1 family in
  place. Existing definition, presentation, submission, result, event, digest,
  and denial fixtures must remain byte- and behavior-compatible.
- The new private definition's `definition_digest` is lowercase SHA-256 over
  compact sorted-key UTF-8 JSON for its private `practice` object, matching the
  established deterministic canonicalization rule without sharing identities
  with the knowledge-check family.
- One practice contains 1 through 20 ordered items. Every item has stable ID
  and version, plain-text prompt/instructions, exactly one point, and one of
  three closed response definitions:
  - single select: 2 through 8 ordered options and one private correct option;
  - multiple select: 3 through 12 ordered options and one nonempty private
    exact correct set; no partial credit;
  - numeric entry: canonical fixed-decimal text at declared scale 0 through 6
    with one private exact value or inclusive range and no unit conversion.
- Practice metadata includes stable purpose/instructions, a versioned bounded
  attempt policy, and exact approved source/review resource references. Policy
  is visible but not enforced until later packets; source/review destinations
  remain opaque exact references until owning public operations resolve them.
- The public presentation repeats exact versions/digests, learner-visible
  metadata, policy summary, references, and safe response constraints. It
  excludes correct option IDs/sets, accepted numeric values/ranges, private
  scoring declarations, and feedback branches.
- The pure parser/projector owns schema plus semantic validation and returns
  immutable typed values. It performs no persistence, clock, network, provider,
  model, API, identity, or scoring side effect.

## In Scope

- Add Draft 2020-12 private-definition and answer-safe presentation schemas
  under the new practice family with closed unions and bounded resources.
- Add one synthetic educational fixture containing all three item types, its
  independently fixed safe presentation, canonical digest vector, and a
  table-driven denial corpus for unsupported and malformed meaning.
- Add a dependency-light contract runner that validates schemas, versions,
  canonical digest, semantic invariants, exact definition-to-presentation
  correlation, and answer secrecy.
- Add immutable Assessment domain values and a closed parser/projector adapter
  behind a narrow Assessment-owned parsing port.
- Add contract and unit tests for all accepted and denied meanings, including
  direct anti-rigidity coverage for valid item/option/reference counts and
  ordering.
- Update the Assessment contract, module README, and learning-contract catalog
  with exact ownership, supported meaning, compatibility, and remaining gaps.

## Out of Scope

Lesson-package admission changes; Content/Curriculum placement or persistence;
Assessment application services or public operation signatures; HTTP/OpenAPI,
generated client, browser UI, session/authorization composition, live fixtures;
submission, scoring execution, feedback selection, evidence, events, retries,
resume/history, projections, or replay; new database migrations; AI/model or
manual grading; adaptive selection; arbitrary execution; external item banks;
and separate headless AI-mode planning.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | current Assessment v1 and lesson-package references | new practice schema directory and learning catalog | Add an independent closed practice family without widening knowledge-check v1 |
| Compatibility evidence | current Assessment corpus conventions | new practice corpus | Fix approved meanings, canonical digest, secrecy, and stable denials |
| Contract tests | Assessment runner/test pattern | new `assessment_practice` runner/tests | Provide dependency-light cross-record evidence |
| Assessment domain | current immutable values and parser port/adapter | new practice-specific domain, port, adapter, and unit test files | Parse and project accepted meaning without changing the existing service |
| Canonical guidance | Assessment contract and module README | listed documentation | Record ownership, exact support, and gaps |
| Planning evidence | SLI-0026, WRK-0092, register | listed planning files | Keep JIT packet lifecycle synchronized |

No existing Assessment v1 schema, fixture, result, event, parser, service,
public operation, persistence, API, client, UI, migration, dependency, or
generated artifact may change.

## Contracts and Interfaces

The private `assessment-practice-definition-v1` document contains
`schema_version`, `definition_digest`, and one closed `practice` object. The
practice owns stable identity/version, title, purpose, instructions,
`attempt_policy`, exact source/review references, and ordered items. Every
security-relevant union and policy is closed; unknown fields fail through
`additionalProperties: false`.

The public `assessment-practice-presentation-v1` document contains exact
practice/package/placement correlation slots needed by later composition plus
the learner-visible policy, references, prompts, ordered options, and numeric
input constraints. Contract-only placement/package fields may be populated by
the approved corpus and projector input but do not grant the parser Content or
Curriculum access. Private answers, ranges, scoring data, and feedback are
forbidden recursively, not only at the top level.

Canonical decimal strings use an optional leading minus sign, `0` or a
nonzero-leading integer, and exactly the declared fractional scale. Positive
signs, exponent notation, grouping/locale separators, NaN, infinity, negative
zero, leading zeroes, implicit rounding, and binary floats are rejected.
Inclusive range lower bound must be less than or equal to upper bound after
exact decimal parsing. The learner-visible unit is plain text only and does not
authorize conversion.

The parser port accepts bytes and returns a private immutable definition or a
bounded safe failure with stable `assessment.practice.*` code and reference.
The projector accepts exact placement/package correlation values plus the
private definition and returns an immutable answer-safe presentation. Neither
interface logs or returns private answers on failure.

## Dependencies and Parallel Safety

CAP-0001 is complete; CAP-0006 is approved and dependency-ready; SLI-0026 is
selected. This first packet has no WRK dependency. It owns the shared Assessment
contract documentation and planning register, so it is not parallel-safe with
another packet changing those files. WRK-0092 must complete before the package,
placement, application, and API packet is authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete definition | One synthetic practice contains all three supported types | Definition validation and parsing run | Stable immutable private values and the canonical definition digest match independently fixed evidence | schema/runner/unit |
| Safe presentation | The private definition contains option answers, numeric accepted values/range, and feedback branches | The projector builds and validates the learner view | Exact public meaning correlates while no private answer/scoring/feedback token appears recursively | runner/unit secrecy tests |
| Single select | Valid option counts and order vary | Schema and semantics run | One declared correct option is accepted; duplicates and unknown correct IDs fail | corpus/unit |
| Multiple select | Valid option and correct-set counts/order vary | Schema and semantics run | A nonempty unique declared exact set is accepted without partial-credit meaning; duplicates/unknown IDs fail | corpus/unit |
| Numeric exact/range | Canonical values use supported scales and signs | Exact decimal semantics run | Exact and inclusive-range rules compare as decimals; malformed syntax, scale mismatch, negative zero, inverted bounds, or float input fails | corpus/unit |
| Resource bounds | Item, option, text, and reference counts sit at accepted edges | Validation runs | Valid edges pass; zero/overflow counts and unsafe text fail closed | parameterized contract tests |
| Closed world | Unknown type, policy, field, schema version, item version, or security-relevant capability appears | Validation runs | A stable bounded unsupported/schema/semantic diagnostic is returned with no private value | denial corpus |
| Existing family unchanged | The complete Assessment v1 corpus and parser tests run | New practice files are present | Current single-select knowledge-check behavior and fixed digests remain unchanged | existing regression suite |
| Side-effect freedom | Parser/projector are invoked repeatedly | Results and repository state are inspected | Results are deterministic and no persistence, clock, network, event, attempt, score, or completion is created | unit/architecture |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/assessment_practice backend/tests/unit/assessment/test_practice_contract.py
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/assessment backend/tests/unit/assessment/test_assessment_service.py
python dev-tools/architecture/check_architecture.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0092-freeze-versioned-practice-contracts.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Submit one exact candidate, generate a fresh affected-verification receipt, and
obtain one independent technical review. Add no dependency or lockfile change.

## Documentation and Evidence Update

Document the new family's exact supported types, resource limits, decimal and
exact-set semantics, answer-secrecy boundary, canonical digest, safe diagnostic
codes, module ownership, unchanged knowledge-check v1 family, and unimplemented
application/API/evidence boundaries. Record exact commands and results,
candidate and receipt, review disposition, assumptions, and residual gaps in
this packet and SLI-0026. Keep approval and reviewer records only in the
ignored local ledger.

## Stop Conditions

Stop for a breaking existing Assessment v1 change; ambiguous scoring or decimal
meaning; private-answer leakage; a requirement for free text, files, code,
notebooks, randomized items, arbitrary execution, AI/model/manual authority,
external provider semantics, client-side scoring, Content/Curriculum internals,
database/API/client/UI change, new dependency, active scope collision,
conflicting canonical source, or material CAP-0006/SLI-0026 drift.

Do not stop or reopen review solely for harmless whitespace, nonfunctional
styling, optional prose polish, or another inconsequential in-scope correction.
Fix it locally or defer optional cleanup to CAP-0031.

## Required Handoff

Report the exact candidate; accepted types and limits; canonical digest and
decimal semantics; secrecy and denial evidence; existing Assessment v1
regression; focused, architecture, affected, aggregate, receipt, and review
results; changed files; documentation impact; assumptions; and residual gaps.
Confirm that no package admission, placement, public operation, API, generated
client, UI, persistence, migration, evidence, AI mode, model authority, or
external execution changed, then leave JIT-B dependency-ready.

## Implementation Evidence

- Added an independent `assessment/practice/v1` Draft 2020-12 contract family
  and compatibility corpus without changing any Assessment knowledge-check-v1
  schema, fixture, digest, parser, or public operation.
- The private definition closes meaning to 1-20 ordered items: single select
  with 2-8 options, multiple select with 3-12 options and exact-set scoring,
  and canonical fixed-decimal numeric entry at scale 0-6 with an exact value or
  inclusive range. Every item has maximum score one.
- The presentation schema and production projector correlate item type to its
  exact policy and recursively omit correct option IDs/sets, numeric answers or
  ranges, private feedback, and private policy objects. A dedicated denial
  proves mismatched public item/policy pairs fail schema validation.
- Added immutable Assessment domain values plus a transport-neutral parser and
  projector port/adapter. The adapter performs no persistence, clock, network,
  identity, API, scoring, attempt, evidence, event, or learner-state action.
  Its JSON-compatible output is suitable for the later protected API shared by
  browser and non-browser clients.
- The new focused contract and unit suites pass 25 tests. The combined new and
  existing Assessment suites pass 59 tests, preserving the accepted
  knowledge-check family. Architecture passes 15 tests; work-packet,
  documentation, and planning validation pass; whitespace integrity is clean;
  and aggregate readiness passes all 29 checks.
- The canonical definition digest is
  `82cdc82c402aacdb0070fb19671d896ae22a4c16d338ccbf27f02a51a396d527`.
  Numeric meaning rejects exponent syntax, noncanonical scale, negative zero,
  disallowed negatives, and inverted ranges without echoing private values.
- No package admission, Content/Curriculum placement, public operation, HTTP,
  OpenAPI, generated client, browser UI, persistence, migration, scoring,
  feedback selection, retry enforcement, evidence, event, AI mode, model
  authority, dependency, or external execution changed.

## Planning History

- 2026-10-16: Authored just in time after SLI-0026 selection. The packet uses a
  separate additive practice family, freezes three closed deterministic
  response types and answer-safe presentation semantics, and preserves the
  existing knowledge-check v1 contract without adding a lower-level approval.
- 2026-10-16: Claimed from base revision `4aeec17` after packet validation,
  current CAP conformance, dependency, decision, and exact-file collision
  checks passed. Packet-start selected the affected contract/domain route.
- 2026-10-16: Implemented and qualified the additive contract/domain boundary.
  Direct compatibility, anti-rigidity, answer-secrecy, decimal, policy-pair,
  legacy-regression, architecture, documentation, planning, whitespace, and
  aggregate-readiness checks pass; the result is ready for exact-candidate
  submission and independent technical review.
