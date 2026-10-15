# ADR-0016: Learner-Managed Experiment Execution with a Future Sandbox Seam

- Status: accepted
- Date: 2026-10-15
- Decision request: [DEC-0014](../planning/decision-requests/DEC-0014-financial-ai-ml-experiment-execution-boundary.md)
- Extends: [ADR-0011](ADR-0011-inert-applied-project-artifacts.md)

## Context

Financial AI/ML experiments require exact datasets, features, code or method
identity, environment declarations, parameters, metrics, outputs, and evaluation
provenance. The platform can preserve and validate that evidence without
executing learner code. A managed runtime would additionally require a sandbox,
image and dependency supply chain, queue and job guarantees, network and secret
policy, resource quotas, abuse handling, cost controls, isolation, cleanup,
incident response, and local/cloud operating posture that are not yet accepted.

The initial choice should not make those unresolved controls accidental product
behavior. It should also avoid a dead-end import format that would force
experiment identity and result meaning to change if a governed analytics
interface or sandbox is introduced later.

## Decision

Use learner-managed execution with validated import for the initial financial
AI/ML experiment capability. ADR-0011 remains authoritative: datasets,
notebooks, code, environment declarations, models, and results are untrusted
inert artifacts, and the platform does not execute them.

The initial platform may:

- define a versioned experiment plan and immutable Project snapshot;
- validate data-use references, dataset/split/feature/target declarations,
  method/model and environment identities, parameters, baseline/metric choices,
  leakage controls, limitations, and expected result classifications;
- export a closed, integrity-bound run bundle for use in a learner-controlled
  environment;
- import a closed result bundle and validate its shape, digests, references,
  declared environment, execution provenance, metrics, artifacts, and linkage
  to the exact plan/snapshot;
- retain and compare imported evidence while labeling it learner-supplied and
  not independently reproduced by the platform; and
- apply deterministic evaluation and claims policy without treating validation
  as proof that code is safe, execution occurred as declared, or results are
  true, causal, suitable, or predictive.

The platform supplies no kernel, interpreter, subprocess, package installation,
runtime image, scheduler, execution job, network access, secret injection,
provider callback, or sandbox for these artifacts. Import, preview, comparison,
and validation paths cannot trigger execution.

### Future Analytics Interface and Sandbox Seam

Experiment meaning is isolated from execution placement through provider-
neutral, versioned plan/run/result contracts:

- the experiment plan and immutable Project snapshot identify what is intended;
- an integrity-bound run bundle contains the permitted inputs and declarations
  without credentials or hidden host state;
- an execution-provenance record identifies the execution mode, environment,
  toolchain, input/output digests, timestamps supplied by the executor, and
  limitations; and
- a normalized result bundle returns outputs, metrics, logs or summaries only
  within reviewed types and bounds, retaining the exact plan, snapshot, data,
  feature, method/model, environment, and parameter lineage.

The initial admitted execution mode is learner-managed external execution. A
future analytics interface may add capability discovery and an execution port
that consumes the same semantic run bundle and returns the same normalized
result contract. A future sandbox may implement that port as an optional
adapter. Neither the port design nor manifest reserves authority for a runtime:
adding any executable adapter still requires a new durable decision covering
trust, images, dependencies, egress, secrets, identity/tenancy, jobs, quotas,
cost, monitoring, cleanup, incident response, provider terms, and qualification.

The core experiment workflow never requires a sandbox. If a future adapter is
missing, disabled, unqualified, incompatible, over quota, or unavailable, the
learner-managed export/import path remains usable. Provider-specific job,
environment, error, billing, or payload types never enter experiment or Project
domain records.

## Consequences

- CAP-0016 can teach reproducible experimental practice without operating an
  untrusted-code execution service.
- Learners must use tools they control, and imported results require clear
  guidance and conservative trust language.
- Stable run and result semantics reduce later migration cost and permit a
  governed sandbox or analytics provider to be evaluated as an adapter rather
  than a new experiment model.
- Reproducibility is represented by complete declarations, immutable inputs,
  digests, and retained outputs; the platform does not claim independent replay.
- Validation, storage, export, import, passive preview, and diagnostics must
  remain bounded against malicious, oversized, misleading, private, or
  improperly licensed artifacts.
- Optional execution capabilities remain locally degradable and cannot become a
  prerequisite for experiment planning, evidence review, comparison, or export.

## Alternatives Rejected

- **Bounded managed isolated runtime now.** Rejected because the sandbox,
  supply-chain, network/secret, scheduling, quota, cost, tenancy, operations,
  cleanup, and incident boundaries are unresolved.
- **Use a provider-specific notebook or job format as the experiment model.**
  Rejected because it would leak provider semantics, constrain local/cloud
  parity, and make imported and future managed results incompatible.
- **Omit any future execution seam.** Rejected because a closed run/result
  contract and optional execution port can preserve evolution without granting
  current execution authority.
- **Treat imported results as platform-reproduced evidence.** Rejected because
  structural and provenance validation cannot attest to external execution or
  result correctness.

## Boundaries

This decision does not select a sandbox, container or VM technology, notebook
server, job queue, runtime image, package source, model-training service,
execution provider, external callback, secret store, network policy, compute
budget, tenancy model, or production model-serving path. It does not grant code
execution, active preview, artifact egress, or independent-reproduction claims.

Exact manifest schemas and limits remain CAP/slice contract work inside this
boundary. Dataset and model-provider permissions remain separately governed.
Production model promotion, serving, financial action, advice, and autonomous
tools are outside this decision.

## Verification Implications

- Prove every import, preview, comparison, and validation path is non-executable
  and cannot reach an interpreter, subprocess, installer, runtime, network,
  secret store, provider execution port, or callback.
- Verify plan, snapshot, run bundle, result bundle, environment, data, feature,
  model/method, parameter, metric, output, and execution-mode provenance with
  exact digests and bounded version compatibility.
- Reject malformed, oversized, partial, conflicting, stale, cross-learner,
  unlicensed, path-traversing, linked, active, or mismatched artifacts without
  replacing valid retained evidence.
- Prove imported output is labeled learner-supplied and not independently
  reproduced, and that deterministic checks cannot make it authoritative for
  financial or protected state.
- Prove a future execution port can be absent or disabled without changing the
  run/result semantics or blocking export, import, review, and comparison.
- Before admitting any executable adapter, qualify isolation, supply chain,
  identity/tenancy, egress, secrets, jobs, quotas, cost, monitoring, cleanup,
  incident response, provider terms, cancellation, idempotency, and local/cloud
  behavior under a new accepted decision.

## Supersession

Any platform- or provider-managed execution, active preview, package install,
runtime image, network or secret access, remote callback, or claim of independent
reproduction requires a superseding or extending ADR. Adding passive artifact
types or versioned fields within the inert run/result seam does not necessarily
require supersession when authority and trust remain unchanged.
