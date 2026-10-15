---
id: SLI-0017
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: CAP-0001
depends_on: ["SLI-0001", "SLI-0015", "SLI-0016"]
decision_gates: []
---

# Vertical Slice: Qualify the Complete Introductory Lesson Loop

## Outcome and User Scenario

The first structured learning loop is demonstrably complete: an authorized
private-host learner opens the exact approved lesson, submits its deterministic
knowledge check, receives bounded feedback, closes and reopens the lesson, and
sees the same retained completion evidence with exact provenance. An operator
can distinguish directly qualified behavior from unsupported identity,
recovery, browser, and managed-cloud profiles.

## Scope Boundaries

### In Scope

- Reconcile CAP-0001 acceptance against the delivered Content, Curriculum,
  Identity, Assessment, Learner-model, Audit, API/generated-client, browser,
  static-build, local-composition, migration, security, and provenance evidence.
- Re-run the minimum cumulative checks needed after SLI-0016 and its bounded
  anti-rigidity correction, including aggregate readiness and live private-host
  loop evidence where freshness is required.
- Record an acceptance trace from each capability criterion to direct tests and
  explicitly retain unqualified profiles and recovery limits.
- Close SLI-0017 and CAP-0001 deterministically only when every manifest slice
  and acceptance criterion has current evidence.

### Out of Scope

- New product behavior, contracts, schemas, migrations, interface patterns, or
  dependency changes.
- Built-in/OIDC, remote or multi-user identity, organization tenancy,
  managed-cloud deployment/recovery, production credentials or database roles.
- Background event delivery, backup/restore tooling, broader Assessment types,
  retakes, mastery, adaptation, recommendations, market data, or projects.
- Manual screen-reader, non-Chromium, or production deployment claims.

## Canonical Context and Decisions

CAP-0001 and ADR-0005 through ADR-0009 define the exact first-loop ownership,
identity, immutable package, community protection/recovery boundary, and runtime
shape. SLI-0001, SLI-0015, and SLI-0016 are complete. Decision readiness still
blocks cloud/tenancy, queue guarantees, and expanded recovery or identity
profiles, none of which is required for cumulative private-host acceptance.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Reconcile and qualify the delivered exact private-host loop | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add built-in/OIDC and multi-user qualification before closure | no | 1 | 2 | 0 | 1 | 0 | 1 | 1 | 6 |
| C. Implement backup/restore so all ADR-0008 implications are operational | no | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 4 |
| D. Introduce background event delivery for production-like projection | no | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 5 |

## Selection Rationale

Candidate A is the only eligible final slice. It proves the complete approved
capability with direct evidence and honest limits. Candidates B through D add
explicitly excluded profiles or cross unresolved identity, recovery, or queue
decisions and would materially reshape the CAP instead of qualifying it.

## Boundary Path

`approved package -> exact Curriculum placement -> server-resolved Identity ->
Assessment presentation/submission/evidence -> versioned completion event ->
Audit reconcile -> Learner-model rebuild -> protected API/OpenAPI client ->
accessible static browser -> private-host PostgreSQL/Python qualification`.
The slice adds no new runtime boundary; it verifies the entire accepted path.

## Contracts, Data, and Provenance

The immutable lesson package, Assessment v1 definition/presentation/submission/
result/event, server learner context, completion response, and static generated
client remain unchanged. Acceptance requires exact package, definition, item,
policy, event, attempt, evidence, score, and time provenance; append-oriented
Assessment/Audit evidence; rebuildable Learner-model state; and no storage,
provider, answer, mastery, advice, suitability, or performance leakage.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Exact lesson open | Protected learner sees approved objectives, sources, version/digest, and publication provenance | contract/API/browser/live E2E |
| Deterministic response | Exact selection produces stable score and reviewed feedback with one evidence/event chain | contract/application/PostgreSQL/API/browser |
| Interruption and reopen | Fresh and repeated reloads reproduce the same bounded completion source set | PostgreSQL/API/browser/live E2E |
| Identity and version denial | Missing/client authority and stale/nonexistent placement fail without disclosure or substitution | security/API/live E2E |
| Replay and storage failure | Duplicate/conflict/tamper/interruption paths remain idempotent or fail closed without false completion | contract/application/PostgreSQL/API |
| Ownership and portability | First-loop modules use only public seams and identical core artifacts remain deployable behind future adapters | architecture/static-build checks |
| Accessible educational framing | Themes, focus, keyboard, reflow, forced colors, axe, and education-not-advice wording remain intact | component/Chromium/live E2E |
| Honest qualification | Unsupported identity, recovery, cloud, browser, and production-role profiles remain explicit | assurance/security/operations docs |

## Agent Work Packets

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0042 | Reconcile cumulative CAP acceptance and close the complete lesson loop | SLI-0001, SLI-0015, SLI-0016 | none | complete |

## Verification and Qualification

Validate all four manifest slices and packet evidence; run current OpenAPI/
client, backend, web, Chromium/live, architecture, security, design,
documentation, planning, dependency, diff, and aggregate readiness checks only
where the evidence route requires freshness. Record exact results without
claiming unavailable profiles.

## Rollback and Migration

No runtime or data change is planned. Qualification documents may be reverted
without altering learner evidence. Existing module migrations and rollback
limits remain governed by their completed slices: Assessment/Audit evidence is
append-oriented and not disposable, while Learner-model state is rebuildable.

## Stop Conditions

Stop if any manifest slice or acceptance criterion lacks evidence, a fixed
check fails for a product/control defect, documentation overstates a profile,
or closure requires new identity, tenancy, queue, recovery, cloud, commercial,
or external-execution authority. Bounded evidence/test defects route through
the correction workflow rather than weakening acceptance.

## Documentation Impact and Completion Evidence

Update the slice, one qualification packet, register, capability acceptance
trace, assurance/security/operations sources made stale, and CAP lifecycle.
Completion must identify exact checks, environments, cleanup, schema and
migration compatibility, unchanged product behavior, unsupported profiles,
residual risks, and current CAP-package conformance.

## Completion Evidence

- WRK-0042 traced all ten CAP-0001 acceptance criteria to the completed
  SLI-0001, SLI-0015, and SLI-0016 contract, application, PostgreSQL, API,
  generated-client, browser, live, architecture, security, design, and
  readiness evidence. No criterion depended on inference or an unavailable
  profile.
- The unchanged candidate passed 196 backend tests on Python 3.14.3 and
  PostgreSQL 18.4, 26 web tests, eight focused Chromium scenarios, and two live
  same-origin scenarios. OpenAPI/client currency, Node 24 typecheck/lint/build,
  zero-vulnerability audit, eight architecture functions, ten security groups,
  and 125-token/56-icon design checks also passed.
- The live learner opened `intro-risk-return@1.1.0`, submitted the exact
  deterministic check, reloaded twice, and retained the same exact completion
  source-set identity without another answer form. Missing context and a stale
  placement failed closed.
- Built-in/OIDC, remote or multi-user identity, managed cloud, background
  delivery, production database roles, automated backup/restore or RPO/RTO,
  non-Chromium and manual screen-reader qualification, broader assessments,
  mastery, adaptation, advice, suitability, and performance claims remain
  explicitly outside the qualified profile.
- This slice changed planning evidence only. All disposable containers and
  temporary build output were removed. No new decision gate, runtime change,
  migration, contract drift, or material CAP-package revision was found.

## Planning History

- 2026-10-15: Refined as the final approved CAP-0001 manifest slice after
  SLI-0001, SLI-0015, and SLI-0016 completed. The cumulative qualification cut
  scored 14/14 and adds no decision, runtime behavior, or material CAP change.
- 2026-10-15: Authored WRK-0042 as one evidence-only cumulative acceptance
  packet; no new product boundary or decision gate was introduced.
- 2026-10-15: Reconciled every CAP-0001 criterion to direct unchanged evidence;
  cumulative qualification passed with unsupported profiles retained as limits.
- 2026-10-15: Closed after the completion structure passed and the fixed
  aggregate readiness gate passed all 27 checks.
