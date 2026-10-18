---
id: WRK-0177
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0084
capability: CAP-0020
depends_on: [WRK-0176]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/dist", "apps/web/tests/browser/approved-lesson/assistance-preferences.e2e.ts", "apps/web/tests/browser/approved-lesson/platform-help.e2e.ts", "backend/src/financial_ai_academy/modules/guidance/README.md", "deployments/local/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/platform-help-contract.md", "docs/architecture/modules/module-map.md", "docs/assurance/known-verification-gaps.md", "docs/planning/capabilities/CAP-0020-understand-platform-methods-and-limitations.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0084-understand-feature-limits-and-safe-recovery.md", "docs/planning/work-packets/WRK-0177-qualify-feature-guidance-live-flow.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: ["apps/web/dist"]
base_revision: 9d155b56b54dcb65c4544e69a99c7888f2752c4a
claim_id: WRK-0177:d1a85d0a-e528-4070-9b5f-955746152e89
claimed_by: codex-cap-0020
claimed_at: 2026-10-18T06:58:17Z
---

# Agent Work Packet: Qualify the Feature-Guidance Live Flow

## Objective and Deliverable

Close SLI-0084 with reproducible evidence that all five delivered feature
conditions resolve one exact reviewed Guidance mapping and record through the
same protected public API for generated-browser and ordinary headless clients.
Prove mapping/record/source/topic integrity, confidential denial, normal local
restart, loopback-only reads, read-only feature-state containment, safe optional
failure, and exact cleanup through the existing disposable PostgreSQL, Python
host, static browser build, and pinned Chromium topology.

This packet adds qualification evidence only. It does not change product or
contract meaning, feature status, action ownership, persistence, identity,
provider/model behavior, artifact execution, or financial authority.

## Required Context

Before this planning edit, the repository `AGENTS.md` and `docs/README.md`
Required Startup was completed and reported. The
review covered repository and planning authority, routed Guidance/API/security/
testing/deployment/interface context, change-impact and decision-readiness
rules, CAP-0020, SLI-0084, completed WRK-0174 through WRK-0176, the feature-
guidance contract and implementation, all five browser placements, the
approved-lesson live runner, pure replay tests, affected assurance sources, and
nearest READMEs.

CAP-0020 remains approved, WRK-0176 is complete with no open technical finding,
and no unresolved durable decision applies. This packet refines the final seam
already enumerated in SLI-0084 and requires no lower-level approval.

## Decisions and Assumptions

- The accepted local single-profile identity, deterministic checked-in
  Guidance, provider-disabled boundary, and existing local runtime are
  sufficient for this read-only qualification.
- Offline-local evidence means normally restarted loopback services use the
  checked-in registry without a non-loopback request; it is not an operating-
  system firewall or production-availability claim.
- WRK-0176's focused suites remain the direct evidence that optional Guidance
  failure cannot block an owning feature. This packet adds cumulative public-
  API and containment evidence without repeating every owning feature flow.

## In Scope

- Extend the approved-lesson browser capture with the five exact
  surface/condition/version Guidance resolutions and only their public mapping,
  record, ordered action/reference, source/publication, and digest facts.
- Revalidate every captured response with the existing browser runtime guard;
  correlate every Help action/reference to its exact captured local topic.
- Extend the Python runner with a closed capture validator and a fresh
  cookie-backed headless observer for all five exact reads plus missing-session
  and invalid-session denial without registry or rejected-key disclosure.
- Require browser/headless equality, exact mapping/record/digest correlation,
  normal-restart equality, loopback-only GET observation, no non-Identity
  database change during Guidance-only reads, and finally-path cleanup.
- Add pure tests for varied valid action/reference counts and order, closed
  shapes, digest/identity/source/topic mismatch, denial confidentiality,
  restart equality, path escape, private fields, and bounded cleanup.
- Regenerate the static browser artifact and reconcile direct Guidance,
  runtime, assurance, CAP/slice, and planning claims with executed evidence.

## Out of Scope

- Product, schema, registry, record, mapping, Help-topic, API, OpenAPI,
  generated-client, identity, permission, session, database, dependency,
  deployment-composition, or design-system changes.
- New conditions, feature error interpretation, latest-version fallback,
  automatic retry/reload/download/save/submit, arbitrary destinations or
  commands, provider/model calls, artifact execution, or external content.
- UI restyling or optional copy cleanup; nonfunctional polish remains CAP-0031
  unless the user explicitly reprioritizes it.
- Operating-system network isolation, public hosting, managed cloud,
  production availability/load/recovery, multi-browser certification, or a
  separate headless-AI mode.

## Expected File and Boundary Impact

| Boundary | Allowed change | Evidence target |
| --- | --- | --- |
| Live Chromium | existing approved-lesson Platform Help journey | Five exact protected Guidance reads, local topic correlation, GET-only/loopback observation, and unchanged Help accessibility evidence |
| Live orchestration | approved-lesson runner | closed capture, headless parity, denial, restart, database containment, cleanup |
| Pure qualification | approved-lesson replay tests | flexible valid records plus strict identity/digest/source/topic/private/path rejection |
| Static browser | `apps/web/dist` generated output | qualify the exact accepted candidate |
| Direct documentation | listed Guidance/runtime/assurance sources | match claims to executed evidence and explicit exclusions |
| Planning | this packet, SLI-0084, CAP-0020, and register | deterministic slice and capability closure |

No unlisted product, contract, registry, source, feature, test, deployment, or
planning path is writable.

## Contracts and Interfaces

1. Browser and headless qualification use only
   `GET /api/v1/guidance/feature-guidance/{surface_key}/conditions/{condition_key}/versions/{mapping_version}`
   after the existing local session bootstrap.
2. The exact five keys are lesson `exact-version-unavailable`, practice
   `write-outcome-uncertain`, Saved learning `source-unavailable`, Project
   `artifact-inert`, and AI help `provider-execution-not-enabled`, each at
   mapping version `1.0.0`.
3. Complete response equality is required for browser and headless reads;
   normal restart preserves the same public meaning.
4. Mapping and record identities, both canonical digests, publication/source
   facts, ordered actions/references, and exact local Help topics must correlate
   before evidence is accepted.
5. The capture contains no cookie, credential, learner identifier, permission,
   feature payload, exception, private enum, local path, repository metadata,
   provider/model value, or approval/review data.
6. Guidance-only reads are GET-only, loopback-only, and leave every non-
   Identity database schema unchanged. They never invoke a feature action.
7. Missing or denied Guidance remains optional: focused WRK-0176 evidence keeps
   the owning task and original action usable, and live qualification must not
   invent a substitute record.

## Dependencies and Parallel Safety

WRK-0176 is complete and supplies all five generated-client placements. This
packet owns the shared approved-lesson journey, runner, static build, assurance
sources, and SLI/CAP closure paths, so it is not parallel-safe with another
writer on those surfaces. It must start from a clean recorded base with one
owner and one exclusive lease covering the exact declared scope.

## Acceptance Scenarios

| Scenario | Required result |
| --- | --- |
| Five exact conditions | Browser and headless clients receive identical exact mapping/record pairs for every delivered condition |
| Integrity | Mapping/record identities, both digests, source/publication facts, actions, references, and exact Help topics correlate |
| Authorization | Missing or invalid sessions deny without registry counts, keys, identities, sources, digests, or rejected input |
| Restart | A normal local host restart preserves every exact public response without reseeding |
| Containment | All observed Guidance requests are loopback GETs and no non-Identity durable feature state changes |
| Flexible validity | Safe wording and action/reference counts/order may vary within contracts without fixed starter prose or count assumptions |
| Closed evidence | Extra, private, stale, inconsistent, digest-mismatched, path-escaping, or unbounded capture data fails before comparison |
| Cleanup | Success and failure remove only the named topology, capture, browser artifacts, build, and bounded temporary root |

## Verification Commands

- Run the pure replay module and complete isolated approved-lesson workflow,
  including its normal restart and finally cleanup.
- Run feature-guidance contract/domain/application/API/source-binding checks,
  OpenAPI and generated-client reproduction, focused Platform Help Chromium,
  and the five WRK-0176 feature component/browser suites.
- Run TypeScript and Python checks, zero-warning lint, production build,
  architecture/import/source-authority, security/privacy/active-content,
  advice and AI authority, learner language, design system, documentation,
  planning, dependency, whitespace, controller-selected exact-candidate
  verification, and aggregate readiness.
- Tests must protect meaning, identity, confidentiality, state containment,
  accessibility, and cleanup without freezing whole prose, incidental timing,
  starter item counts, layout pixels, or unrelated requests.

## Documentation and Evidence Update

Record the exact candidate and receipt, five identities, browser/headless and
restart equality, mapping/record/source/topic digest facts, denial,
loopback-only observation, read-only containment, optional-failure correlation,
cleanup, checks, assumptions, unsupported profiles, and residual gaps. Update
only direct sources in `write_scope`; keep approval and technical-disposition
records in ignored local control-plane storage.

## Stop Conditions

Before implementation, consume the reserved ID, commit this packet, claim it
from the clean commit, run `packet-start`, and acquire one exclusive lease for
the declared write scope. Complete this final packet before selecting another
CAP.

Stop for a required product/contract/registry/API/client/identity/database or
deployment-composition change; inconsistent browser/headless meaning; source,
digest, or Help-topic mismatch; non-loopback request; feature-state mutation;
private disclosure; provider/model or artifact execution; arbitrary command or
external action; managed-cloud, tenancy, recovery, licensing, legal, or
commercial expansion; stale CAP authority; an ownership collision; or material
CAP-0020 drift.

Do not stop or reopen review solely for whitespace, optional wording,
nonfunctional styling, generated values, varied valid counts/order, or another
inconsequential qualification correction. Fix it in bounded scope or defer
optional polish to CAP-0031.

## Required Handoff

Report `CAP-0020.SLI-0084.WRK-0177`; exact candidate and receipt; five exact
conditions; browser/headless parity; identity/digest/source/topic integrity;
authorization; restart; loopback-only/read-only containment; optional-failure
correlation; accessibility and anti-rigidity; cleanup; checks; changed files;
documentation impact; assumptions; unsupported profiles; and residual gaps.
Confirm no product/contract meaning, feature state/action, identity,
persistence, provider/model, artifact execution, external action, learner
policy, or financial behavior changed, then close SLI-0084 and proceed to the
already-approved SLI-0085 qualification slice before CAP-0020 closure.

## Verification Evidence

Implementation is complete on exact candidate
`1f746a029ff3dbfd3d683eb07cf23213dfab7dfa`. The pure replay module passes all
87 cases. The direct
isolated live topology passes every Chromium flow and proves all five exact
feature-condition resolutions through authenticated browser and fresh ordinary
headless sessions, confidential missing and invalid-session denial, exact
mapping/record/source/topic correlation, equal meaning after normal restart,
loopback-only GET observation, unchanged non-Identity database fingerprints,
and finally-path cleanup.

The first live run exposed one stale assistance-preference read allowlist. The
bounded correction admits only the delivered exact AI-help Feature Guidance
GET alongside the existing export and contextual-Help GETs; it preserves the
no-write, no-provider, and no-notification-execution assertions. TypeScript,
zero-warning lint, Python compilation, work-packet validation, and the corrected
full live topology pass.

The controller selected and passed 11 exact-candidate checks: planning tools
and integrity, documentation integrity, feature-Guidance qualification,
architecture and local architecture, feature-Guidance security, Web typecheck
and zero-warning lint, the complete approved-lesson live topology, and
aggregate readiness. The immutable receipt is
`.local-codex/control-plane/receipts/WRK-0177/1f746a029ff3dbfd3d683eb07cf23213dfab7dfa/20261018T071021Z-43f7fec6-108e-41f5-a995-042b6e3212aa.json`
with receipt digest
`sha256:c886da4956467d370d9665f1ade11b9467a32fa8decc9044f2b40732f37bb322`.
The aggregate readiness gate reports all 29 checks ready, and no open technical
finding remains. Direct supplemental evidence also passes all 507 Web tests,
90 focused Guidance checks, 17 architecture checks, and documentation,
planning, design-system, Python-compilation, build, and whitespace checks.

## Planning History

- 2026-10-18: Authored just in time after WRK-0176 completed. This is the
  smallest final SLI-0084 seam and reuses the established approved-lesson
  topology without a new product decision or lower-level approval.
- 2026-10-18: The first live pass reached the AI-help preference flow and
  exposed one stale read allowlist that admitted exact contextual Help but not
  the newly delivered exact Feature Guidance GET. Scope now includes only that
  assertion; its no-write and no-provider-execution boundary remains unchanged.
- 2026-10-18: Implemented the five-condition browser/headless capture,
  closed/digest-validating replay checks, missing and invalid-session denial,
  exact topic/source correlation, restart equality, loopback GET observation,
  database containment, and cleanup evidence. Exact-candidate qualification
  remains before closure.
- 2026-10-18: Closed on exact candidate `1f746a0` after all 11 selected checks
  and the 29-check aggregate readiness gate passed with no open technical
  finding. SLI-0084 now has complete packet evidence.
