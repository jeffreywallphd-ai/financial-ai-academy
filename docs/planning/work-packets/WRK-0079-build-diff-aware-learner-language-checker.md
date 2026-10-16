---
id: WRK-0079
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: SLI-0125
capability: CAP-0030
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/learner-language/README.md", "dev-tools/learner-language/rules.json", "dev-tools/learner-language/check_learner_language.py", "dev-tools/learner-language/test_learner_language.py", "dev-tools/README.md", "docs/planning/work-packets/WRK-0079-build-diff-aware-learner-language-checker.md", "docs/planning/vertical-slices/SLI-0125-sustain-plain-language-interface-quality.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Build the Diff-Aware Learner-Language Checker

## Objective and Deliverable

Implement a repository-local deterministic CLI that examines changed
learner-facing TypeScript/TSX copy by default, blocks only a small configured
set of high-confidence defects, reports judgment-dependent language heuristics
as advisory, and supports narrow source-local reasoned exceptions. Supply a
configuration contract, human and JSON result shapes, direct tests, and tool
documentation that make the checker independently usable before aggregate
readiness integration.

The observable result is a contributor command that fails for one owned raw
field/internal term in primary learner copy, succeeds for ordinary clear copy,
and also succeeds—with optional advisory output—for specialist, explanatory,
formatting-only, CSS-only, generated, test, developer, and explicit technical-
record content outside the check's narrow scope.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-root
`docs/README.md`. Route through the baseline, interface-design, testing-quality,
and delivery-planning packs. Read CAP-0030, SLI-0125, the learner-facing
language standard, content style guide, interface standards, change-impact
matrix, testing standards, architecture-verification guidance, development-
tools index, agent-readiness documentation, planning/concurrent-work guides,
and current ready/completed CAP-0030 packets. Inspect current learner-facing
TSX source, technical-record disclosures, tests/fixtures, generated-client
paths, Git diff behavior, and the future `check_ready.py` consumer before
changing the tool.

## Decisions and Assumptions

- The checker implements only the explicitly automatable subset of the
  accepted language standard. Product, domain, contract, risk, security, and
  accessibility sources remain authoritative for meaning.
- Default scope is changed learner-facing copy. An explicit `--all` mode is
  available for controlled qualification; callers may provide a Git base
  revision without making it a universal repository scan.
- Blocking rules are exact or carefully bounded configured patterns with an
  approved learner-facing replacement. Sentence length, passive voice,
  possible jargon, acronym, noun-cluster, and reading-level signals remain
  advisory and cannot change the exit code.
- The first implementation may use deterministic source-aware lexical
  extraction rather than a TypeScript compiler as long as refusal and
  exclusion tests prove it does not treat identifiers or whole source files as
  prose.
- A local exception is attached to one source occurrence and one rule, gives a
  reason, and points to an explanation. It cannot disable file selection or an
  unrelated rule.
- No text leaves the repository, no copy is rewritten, and no runtime product
  behavior is changed.

## In Scope

- CLI modes for local changed-copy selection, explicit base-revision selection,
  explicitly requested full owned-source qualification, and JSON output.
- Repository-root discovery, normalized repository-relative paths, stable
  ordering, clear exit codes, and bounded Git/configuration failures.
- Owned source roots and excluded generated, test, fixture, distribution,
  developer, and non-TypeScript paths in tracked configuration.
- Source-aware extraction of primary JSX text and user-visible accessibility/
  help attributes, with exclusion of comments, identifiers, imports, and
  explicitly labeled technical-record regions.
- High-confidence rule corpus for the approved replacement examples and a
  small advisory corpus/heuristic set.
- One narrow source-local exception syntax with validation for rule identity,
  reason, explanation location, and immediate target occurrence.
- Positive, negative, selection, exclusion, exception, malformed-input,
  stable-output, JSON, and anti-rigidity tests.
- Tool README and development-tools index entry.

## Out of Scope

Aggregate readiness or CI integration; edits to application copy; design,
CSS, tokens, icons, components, browser tests, screenshots, contracts,
generated clients, backend, database, Docker, deployment, dependencies, or
canonical language guidance; automatic rewriting; external services; a
mandatory reading grade; universal prose scanning; and any new approval stage.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Language authority | language standard, content guide, interface standards | none | Configure only the accepted automatable subset |
| Checker | current developer-tool patterns and Git behavior | new checker and tracked rule configuration | Provide deterministic changed-copy selection and tiered results |
| Checker evidence | current Python test conventions and representative TSX shapes | new focused checker tests | Prove detection, exclusions, exceptions, output, and anti-rigidity |
| Tool documentation | development-tools index and agent-readiness consumer | checker README and development-tools index only | Make direct use and later integration contract explicit |
| Planning evidence | CAP-0030, SLI-0125, planning register | this packet, parent slice, register | Keep exact scope and lifecycle coherent |

No application source, public contract, runtime, generated artifact,
dependency, CI workflow, or aggregate runner may change in this packet.

## Contracts and Interfaces

The CLI accepts an optional `--base-ref <revision>`, explicit `--all`, and
optional `--json`. Without `--all`, it selects only changed lines in owned
learner-facing source from the requested base or the local index/worktree. It
returns `0` when no blocking finding exists, `1` when blocking findings exist,
and `2` for invalid invocation, configuration, source selection, or Git
failure.

Each finding has a stable rule identifier, severity (`blocking` or
`advisory`), repository-relative path, one-based line, bounded message, and
replacement/help text. JSON output additionally has a schema version,
selection mode, selected-file/region counts, blocking/advisory counts, and
sorted findings. It contains no source payload, approval data, identity,
secrets, or telemetry.

The rule configuration owns source globs/exclusions and blocking term/replacement
pairs. The local exception syntax must bind one immediately following candidate
occurrence to one known rule and include a non-empty reason plus explanation
location. Unknown, broad, or malformed exceptions fail as configuration/source
errors rather than silently suppressing checks.

## Dependencies and Parallel Safety

SLI-0122 through SLI-0124 are complete; they provide the accepted language
contract and representative interface patterns. CAP-0030 approval is current
and includes SLI-0125. This first SLI-0125 packet has no packet dependency.

The packet is not declared parallel-safe because `dev-tools/README.md` and the
planning register are shared coordination surfaces. Its application/runtime
scope is disjoint from the independently dispatched roadmap-site correction,
but the owner must acquire exact-file leases and pause if that correction needs
the same shared files.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Blocking primary term | Changed JSX primary text or accessible label contains an owned internal term | Default or base-ref check runs | One stable blocking finding names its replacement and exit is `1` | focused CLI test |
| Clear learner copy | Changed learner-facing strings use accepted task language | Check runs | No blocking finding and exit is `0` | positive corpus test |
| Advisory-only copy | A long sentence or possible acronym/jargon heuristic is present without a blocking term | Check runs | Advisory may be reported, blocking count stays zero, and exit is `0` | anti-rigidity test |
| Specialist explanation | A necessary precise term is explained and locally excepted for one rule | Check runs | Only that occurrence is suppressed and another owned defect still reports | exception-scope test |
| Technical record | A technical term is inside a `Technical record` disclosure | Check runs | The intentionally technical region is not treated as primary copy | extraction/exclusion test |
| Identifier and fixture | The same spelling appears in an import, identifier, test, generated file, or contract-mirroring fixture | Check runs | The candidate is not selected as learner prose | exclusion test |
| Whitespace or CSS only | The diff has no changed owned learner-facing string | Default check runs | Selected copy count is zero and exit is `0` | diff-scope test |
| Invalid exception | An exception names an unknown rule, lacks reason/explanation, or does not bind an immediate occurrence | Check runs | Exit is `2` with a bounded diagnostic | refusal test |
| Stable machine report | The same inputs are checked repeatedly | JSON mode runs | Sorted payload and counts are deterministic and source text is absent | JSON contract test |
| Full qualification | Existing owned learner source is checked explicitly | `--all` runs | Only owned visible regions are evaluated; advisory output cannot fail the command | CLI integration test |

## Verification Commands

Run:

```powershell
python dev-tools/learner-language/test_learner_language.py
python dev-tools/learner-language/check_learner_language.py --all
python dev-tools/learner-language/check_learner_language.py --all --json
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
python dev-tools/design/check_design_system.py
python dev-tools/agent/check_ready.py
git diff --check
```

For direct tests, use isolated temporary Git repositories and fixture files so
changed-only, base-ref, staged, unstaged, untracked, whitespace, CSS, generated,
and source-region behavior is deterministic without mutating the real worktree.
Aggregate readiness remains unchanged in this packet; it is a regression gate
only until JIT-B integrates the checker.

## Documentation and Evidence Update

Document command modes, owned/excluded scope, finding/exit contracts, rule
configuration, exception syntax, advisory semantics, JSON privacy boundary,
and examples that do not imply formal plain-language conformance. Record exact
focused/full-scope/readiness results and any bounded false-positive or source-
extraction limitation in the packet and parent slice. Do not copy local
approval or reviewer metadata into tracked files.

## Stop Conditions

Stop for conflicting canonical language; a required domain/risk/accessibility
semantic judgment; automatic rewriting; external text processing; new
dependencies; TypeScript compilation or application behavior changes;
repository-wide or technical-document blocking; a mandatory universal
readability measure; exception syntax that can suppress a file or multiple
rules; active file overlap; an unexecutable deterministic check; or material
CAP-0030/SLI-0125 drift.

Do not stop or request re-review for whitespace, advisory-only output, or
nonfunctional styling outside the packet. Leave those unchanged or route
optional visual cleanup to CAP-0031.

## Required Handoff

Report the checker path, configuration, selection modes, extraction boundary,
blocking and advisory rules, exception contract, exit/JSON shape, exact tests
and results, full-scope result, documentation changes, assumptions, residual
false-positive/false-negative risks, unresolved decisions, and confirmation
that runtime product code, contracts, generated clients, CSS, browser behavior,
and aggregate readiness integration did not change. Leave JIT-B dependency-
ready or return one bounded blocker.

## Planning History

- 2026-10-16: Authored just in time as SLI-0125 JIT-A. The packet isolates the
  reusable deterministic checker and direct anti-rigidity evidence from later
  aggregate-readiness integration. Its exact scope conforms to CAP-0030 and
  introduces no decision or lower-level approval gate.
