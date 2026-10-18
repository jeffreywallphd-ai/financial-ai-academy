---
id: WRK-0178
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0085
capability: CAP-0020
depends_on: [WRK-0177]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/guidance/resources/README.md", "dev-tools/agent/check_ready.py", "dev-tools/agent/test_check_ready.py", "dev-tools/control-plane/README.md", "dev-tools/control-plane/financial_academy_checks.py", "dev-tools/control-plane/test_verification.py", "dev-tools/guidance/README.md", "dev-tools/guidance/check_guidance_quality.py", "dev-tools/guidance/source_authority.json", "dev-tools/guidance/test_guidance_quality.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0085-qualify-platform-help-quality.md", "docs/planning/work-packets/WRK-0178-build-guidance-quality-gate.md"]
generated_artifacts: []
base_revision: be5e38fe3501e986bb868e6c3a3b3c48f14c1a45
claim_id: WRK-0178:160f0ad6-97a2-45bb-9790-e46c3e1d4ecd
claimed_by: codex-cap-0020
claimed_at: 2026-10-18T07:15:49Z
---

# Agent Work Packet: Build the Guidance Quality Gate

## Objective and Deliverable

Create one fast, deterministic contributor-facing command that qualifies the
checked-in Guidance graph before delivery. It must bind every safe source key
to one current canonical file, load all three registries through production
adapters, verify exact reads and complete search traversal without fixed corpus
counts, and return a privacy-minimized result. Register that command in fixed
agent readiness and affected-check selection, with direct tests that prove
stale, missing, escaping, duplicate, and malformed authority data fail closed.

This packet does not change public Guidance schemas, records, API behavior,
generated clients, browser presentation, persistence, identity, or provider
behavior.

## Required Context

Before this planning edit, the repository `AGENTS.md` and `docs/README.md`
Required Startup was completed and reported. The review covered the baseline,
Guidance, API/security/testing, planning, and developer-workflow context; the
change-impact matrix and decision-readiness register; CAP-0020; completed
SLI-0082 through SLI-0084; SLI-0085; Guidance contracts, adapters, resources,
tests, browser consumers, control-plane catalog, fixed readiness command, and
nearest READMEs.

CAP-0020 remains current, all dependencies are complete, and no unresolved
durable decision applies. Detailed packet planning is incremental within the
already-refined final slice and requires no packet-level approval.

## Decisions and Assumptions

- Canonical source paths are repository-only quality metadata. Runtime values
  retain safe source keys and fingerprints but never expose local paths.
- Production Guidance adapters and domain validation remain the sole parsers
  and exact-link authorities; the command must not create a competing content
  model.
- The gate stays fast enough for fixed readiness by loading checked-in files
  and exercising deterministic exact/search behavior without starting a host,
  browser, database, network client, or package manager.
- Full contract, security, browser, and live evidence remains separately
  selectable by the control plane and is closed in the next packet.

## In Scope

- Add a versioned repository-only source-authority manifest with one normalized
  repository-relative path per safe source key.
- Add a Guidance quality command that validates the manifest shape and root
  containment, compares current canonical file SHA-256 values to runtime source
  fingerprints, atomically loads all Guidance registries, confirms exact reads
  and resolution, and traverses every browse result through contract cursors.
- Emit only stable counts, manifest versions, and canonical digests on success;
  emit bounded safe source keys or quality dimensions on failure without
  record bodies, credentials, learner data, or deployment paths.
- Add focused tests for the current repository, varied valid topic count and
  file order, missing/stale/duplicate/unknown/escaping source authority,
  malformed JSON, exact graph failure, search traversal, and stable output.
- Add the command to fixed aggregate readiness and to affected-check selection
  for Guidance resources/adapters/contracts, canonical source files, Web Help
  rendering, and the quality tool itself.
- Update contributor and control-plane instructions plus SLI/register evidence.

## Out of Scope

- Editing Help, context, feature-guidance, or canonical source meaning solely
  to satisfy the gate; changing public contracts or runtime source keys.
- Starting PostgreSQL, the local host, Chromium, or any remote/network service.
- External crawling, link checking outside the exact internal graph, semantic
  search, AI evaluation, authoring workflow, hosted support, or telemetry.
- UI styling/copy cleanup, generated static Web output, or SLI/CAP completion.
- Identity, tenancy, cloud, queue, encryption, recovery, legal, commercial,
  data licensing, provider/model, external execution, or financial policy.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Guidance runtime | contracts, models, immutable adapters, resources | resource contributor README only | Reuse production validation without changing runtime meaning |
| Quality tool | current source-binding unit test and developer checks | new `dev-tools/guidance/` command, manifest, tests, README | Provide one deterministic contributor result |
| Control plane | affected-check catalog and verification tests | catalog plus bounded catalog tests/docs | Select the quality command for material paths |
| Agent readiness | fixed command and behavior tests | readiness catalog plus bounded tests | Make source/link freshness a fixed handoff gate |
| Planning | SLI-0085, this packet, register | listed artifacts | Keep lifecycle and evidence synchronized |

No public schema, API, generated client, Web application, persistence,
deployment, canonical source, or unrelated planning file is writable.

## Contracts and Interfaces

1. `source-authority-v1` is repository-only JSON with one `sources` object from
   safe source key to normalized repository-relative Markdown path.
2. Its keys must equal the runtime `PLATFORM_HELP_SOURCE_FINGERPRINTS` keys;
   every path must be unique, remain inside the repository, and name a regular
   tracked canonical file.
3. Current file bytes must hash to the runtime fingerprint for the same safe
   key; failure reports the key, not file contents or absolute location.
4. The command must instantiate `ImmutablePlatformHelpCorpus`,
   `ImmutableContextualHelpRegistry`, and
   `ImmutableFeatureGuidanceRegistry` with the admitted topic set.
5. It must reproduce every exact topic/context/feature resolution and traverse
   all browse pages with contract cursors, independent of valid corpus count or
   file order.
6. Success output is deterministic JSON or concise text with schema version,
   manifest versions, item counts, and canonical digests. Failure exits
   nonzero with one bounded diagnostic category.
7. Control-plane commands bind the checked script by repository path and select
   it when any declared Guidance or canonical-source dependency changes.

## Dependencies and Parallel Safety

WRK-0177 and all three preceding slices are complete. This packet owns the
fixed readiness catalog, affected-check catalog, Guidance contributor rules,
and new quality-tool directory, so it is not parallel-safe with another writer
on those files. It must start from one clean recorded base with an exclusive
lease for the declared write scope.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Current graph | All checked-in sources and registries are current | Contributor runs the quality command | One deterministic success summary covers sources, three registries, exact reads, and complete search traversal | direct command test |
| Stale source | One canonical file differs from its bound fingerprint | The command runs | It fails with the safe source key and no file content or absolute path | focused unit test |
| Invalid authority | A path is missing, absolute, escaping, duplicated, unknown, or malformed | The command validates the manifest | It fails before registry qualification with a bounded category | focused unit test |
| Broken registry | One exact link, digest, required identity, or source binding is invalid | Production adapters load the graph | The command fails atomically and exposes no partial result | adapter/command test |
| Complete browse | Valid corpus count, file order, and page size vary | The command traverses search pages | Every exact topic appears once in stable contract order without a fixed starter count | property/command test |
| Fixed readiness | The repository is handed off | Aggregate readiness runs | Guidance quality is a named fixed check and passes | readiness behavior/aggregate |
| Affected selection | Guidance, canonical source, shared Help rendering, or gate files change | The controller plans exact-candidate checks | The Guidance quality check is selected | control-plane verification test |

## Verification Commands

- `python dev-tools/guidance/test_guidance_quality.py`
- `python dev-tools/guidance/check_guidance_quality.py`
- `python dev-tools/agent/test_check_ready.py`
- `python dev-tools/control-plane/test_verification.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Run the existing focused Guidance unit/contract qualification when the command
or fixtures expose an adapter or contract defect. Browser, live topology,
build, and final controller-selected exact-candidate qualification remain the
dependent packet's cumulative evidence.

## Documentation and Evidence Update

Document the source-authority format, safe output, contributor command,
anti-rigidity contract, and affected-selection behavior in the new tool README,
Guidance resource README, and control-plane README. Keep this packet, SLI-0085,
and the register synchronized. Record approval and technical-disposition data
only in ignored local ledgers.

## Stop Conditions

Before implementation, consume the reserved ID, commit this ready packet,
claim it from the clean commit, run `packet-start`, and acquire one exclusive
lease for the declared write scope.

Stop for conflicting source authority, a required runtime/public contract
change, path or private data entering runtime output, a network or hosted
dependency, AI/model authority, identity or persistence change, stale CAP
authority, scope collision, or material CAP-0020/SLI-0085 drift.

Do not stop or reopen review for harmless whitespace, optional wording,
nonfunctional styling, valid fixture count/order, or another inconsequential
quality-tool correction. Fix it within the packet scope.

## Required Handoff

Report `CAP-0020.SLI-0085.WRK-0178`; the quality command and source-authority
contract; affected boundaries; stale/path/link/search/anti-rigidity evidence;
readiness and control-plane integration; exact checks and results;
documentation impact; assumptions; residual gaps; and any unresolved decision.
Confirm that public contracts, runtime Help meaning, learner/feature state,
identity, persistence, provider/model behavior, external actions, and financial
authority did not change before the final cumulative qualification packet.

## Planning History

- 2026-10-18: Authored just in time after SLI-0085 refinement. This is the
  smallest first seam that turns existing freshness, link, and search evidence
  into one contributor-facing result without changing product behavior or
  requiring a lower-level approval.
- 2026-10-18: Claimed from clean base `be5e38f` with one bounded owner and the
  declared write scope after current CAP authority and dependency completion
  were revalidated.
- 2026-10-18: Implemented the repository-only source-authority manifest, fast
  production-adapter quality command, exact graph/search traversal, bounded
  failure and valid-growth tests, affected-check selection, and the fixed
  readiness integration. Exact-candidate verification remains before closure.
- 2026-10-18: Focused Guidance, source/path/link, anti-rigidity, control-plane
  selection, readiness-catalog, security, planning, documentation, compilation,
  and whitespace checks passed. The public projection remains active through
  durable exact-candidate submission, as required by the controller lifecycle.
