---
id: DEC-0008
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
decision_record: ../../adr/ADR-0011-inert-applied-project-artifacts.md
---

# Decision Request: Set the Project Artifact and Notebook Execution Boundary

## Decision Needed

Choose the initial CAP-0007 boundary for learner datasets, notebooks, code,
saved results, and other project artifacts: inert platform storage and external
learner execution, platform-managed isolated execution, or a configured
external execution provider.

Use one option label exactly as written below:

- **Option A — Inert artifacts with learner-managed execution**
- **Option B — Platform-managed isolated execution**
- **Option C — Configured external execution provider**

## Why Now

The product catalog includes datasets, notebooks, saved results, and
reproducibility in applied projects. Current authority identifies notebooks,
imports, external providers, and generated artifacts as trust boundaries but
does not authorize code execution, egress, secrets, runtime images, quotas, or a
provider. CAP-0007 cannot make artifact promises or define qualification until
this boundary is explicit.

Deferring is safe and keeps CAP-0007 `decision-blocked`. Choosing an execution
model after implementation would require redesign of contracts, security,
storage, provenance, operations, and learner expectations.

## Current Authority and Constraints

- The platform is educational and must not execute trades, control real
  financial accounts, or imply suitability or guaranteed outcomes.
- Arbitrary notebook/code input is untrusted. Validation of a file format does
  not make its code, outputs, dependencies, links, or embedded data safe.
- Provider-specific payloads and credentials stay behind platform-owned ports;
  external data/model use requires accepted terms and explicit egress.
- Community evidence protection relies on a private host and user-controlled
  storage protection; it does not supply an application sandbox, key-management
  service, RPO, RTO, or compromised-host protection.
- Managed-cloud provider, tenancy, encryption, queue, recovery, and commercial
  choices remain decision-required.
- Every artifact and result must retain type, version, provenance, assumptions,
  and observed/calculated/simulated/predicted/generated distinctions.
- Client, notebook, model, or AI output cannot authorize completion or durable
  state changes.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| Option A — Inert artifacts with learner-managed execution | Delivers guided projects, reproducibility metadata, artifact manifests, saved results, and notebook portability without creating a code-execution service. Works offline in the community profile, minimizes egress/secrets risk, and keeps runtime choice with the learner. | Learners must run notebooks/tools outside the platform; environment reproduction is evidence rather than guaranteed execution; imported outputs can be false or unsafe and require explicit untrusted labeling and validation. | Artifact/media schemas; size/resource/path limits; content-addressed storage; environment and dataset manifests; import/export; provenance; UI download/upload/inspection; no execution port. | High. Stable inert artifact and provenance contracts can later feed a sandbox or provider without changing historical evidence meaning. |
| Option B — Platform-managed isolated execution | Provides an integrated reproducible learning experience, controlled environment images, captured logs/results, deterministic resource limits, and potentially stronger replay evidence. | Introduces a high-risk sandbox and supply-chain surface, compute cost, quotas, image/dependency maintenance, denial-of-service controls, egress/secrets policy, job delivery, observability, cleanup, multi-tenant isolation, and recovery obligations that are currently unresolved. | Execution/job contracts; sandbox/runtime images; dependency admission; dataset mounts; network/secret policy; quotas; storage; telemetry; local/cloud operations; security threat model; incident response. | Low after learners and evidence depend on runtime-specific outputs. Replacing the sandbox requires compatibility and result-provenance migration. |
| Option C — Configured external execution provider | Avoids operating a full sandbox while enabling integrated notebook execution through an established environment and may offer richer tooling. | Sends learner artifacts/data to another trust boundary; requires credentials, provider terms, egress consent, availability/failure handling, quotas/cost, callback security, result validation, and provider-neutral normalization. Community offline behavior may be degraded or unavailable. | Provider capability/manifest schemas; auth/secret references; egress and consent; dataset licensing; submission/result callbacks; health/quota; conformance suite; fallback and export. | Moderate to low depending on how much provider identity and runtime metadata enters project evidence. A platform-owned contract improves portability but cannot erase data already sent. |

## Recommendation

**Recommend Option A — Inert artifacts with learner-managed execution.**

Verified facts: the repository has no accepted execution sandbox, external
notebook provider, queue semantics, managed-cloud platform, tenancy model, or
provider data-use decision. The product can still support milestones, datasets,
portable notebooks, saved results, reflections, submissions, and reproducibility
evidence without running code.

Assumption: the first project outcome can require learners to execute tools in
their own environment and import a closed evidence manifest, with clear setup
guidance and no claim that the platform independently reproduced every result.

Inference: Option A supplies meaningful applied-project value and leaves the
most reversible path. A later execution capability can build on the same
artifact/provenance contracts after its security, provider, cost, and operations
decisions are accepted.

## Evidence Required

- A threat model for upload, storage, inspection, download, export, and restore
  of untrusted datasets, notebook/code files, results, and archives.
- A portable artifact-manifest sketch with normalized paths, media/type rules,
  sizes, digests, environment/dependency declarations, dataset provenance,
  licensing fields, and result classifications.
- Resource-limit and diagnostics proposals covering file count/size, archive or
  link denial, unsafe previews, malware handling posture, and secret scanning.
- For Option B: a sandbox technology study, escape/isolation analysis, runtime
  supply-chain policy, egress/secrets model, queue semantics, quota/cost plan,
  cleanup, incident response, and local/cloud qualification plan.
- For Option C: provider capability and conformance proposal, provider terms and
  data-use review, credential/consent model, egress map, quota/cost limits,
  outage/fallback behavior, and result-normalization evidence.

## Required Authority

Product, architecture, and security owners must choose the execution boundary.
Option B additionally requires operations and managed-cloud authority. Option C
additionally requires provider, privacy, and data-license review. Qualified
legal/commercial review is required if a selected provider or dataset license
creates those obligations. This tracked request records no personal identity or
approval.

## Decision Record and Promotion

After a local authorized choice is recorded, promote it to an accepted ADR and
the applicable security architecture, decision-readiness, operations, provider,
data/provenance, and risk documents. The record must define allowed effects,
trust boundaries, egress, secrets, resource limits, evidence claims, failure
behavior, and future expansion gates before DEC-0008 is complete.

## Dependent Planning Updates

- Reconcile CAP-0007 in-scope/out-of-scope behavior, each slice stop boundary,
  capability acceptance, and qualification to the selected option before CAP
  approval.
- Couple artifact ownership and persistence to the owner selected by DEC-0007.
- Route any future managed sandbox or provider implementation through its own
  bounded capability if Option A is selected now.
- Update future personal-workspace, financial AI/ML experiment, provider, and
  managed-cloud capabilities so they consume the decision rather than bypass it.

## Planning History

- 2026-10-15: Created from CAP-0007 decision-gate review as one member of the
  related applied-project decision set with DEC-0007.
