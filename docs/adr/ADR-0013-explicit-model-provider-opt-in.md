# ADR-0013: Explicit Model-Provider Opt-In

- Status: accepted
- Date: 2026-10-15
- Decision request: [DEC-0011](../planning/decision-requests/DEC-0011-model-provider-and-ai-data-use-posture.md)

## Context

Grounded tutoring, AI/ML experiments, adaptive techniques, and later provider
governance need a common posture for local and externally hosted models. The
shared core must support both deployment profiles without allowing a provider,
model name, billing shape, or data-use term to become domain meaning.

Model invocation can expose learner information, approved educational sources,
licensed material, project artifacts, prompts, retrieval context, and generated
output. Provider terms, retention, training use, security posture, capability,
cost, and availability vary and can change. Enabling an adapter merely because
credentials are present would make data egress implicit and would undermine the
deterministic learning paths that must remain usable without a model.

## Decision

Admit both local and external model-provider adapters behind the same
platform-owned model port, subject to explicit per-provider opt-in.

The community edition enables no model provider by default. Setup or an
authorized later configuration action must select one provider instance,
display its declared capability and data-use posture, and grant permission for
each data class the provider may receive. Credentials alone do not enable an
adapter or authorize a new data class.

Every admitted model-provider adapter declares and enforces:

- provider identity, adapter and contract versions, model capabilities and
  limitations, and whether execution is local or external;
- configuration and secret requirements, outbound hosts, payload and rate
  bounds, quotas, cost signals where available, and health behavior;
- every input and output data class, including whether learner information,
  educational content, licensed sources, project artifacts, or retrieval
  context may cross the boundary;
- current retention, training-use, secondary-use, deletion, and diagnostic-
  logging terms, with an explicit no-training/no-retention claim only when
  supported by current evidence;
- redaction and minimization policy, consent or preference requirements,
  evaluation status, safety limitations, and supported disablement behavior.

Provider admission and provider selection are separate. An adapter is admitted
only after current terms, security, privacy, capability, cost, evaluation, and
conformance evidence is reviewed. An admitted adapter is invoked only when the
selected provider instance is enabled and the operation's data classes are
permitted. A terms or policy change can suspend the adapter without changing
domain behavior or destroying prior execution provenance.

All model access continues through AI orchestration. The execution record
retains provider, model, policy, prompt/template, input-reference, retrieval,
parameter, validation, latency, cost, safety, and outcome provenance subject to
redaction and retention policy. Provider payloads remain untrusted, and model
output remains advisory rather than authority for grades, competency,
eligibility, authorization, financial calculations, suitability, portfolio
action, or durable protected-state mutation.

Every essential learner flow has a deterministic no-model fallback. A disabled,
unconfigured, unhealthy, over-quota, or policy-ineligible provider causes a
bounded unavailable or degraded result; it never triggers silent provider
substitution, broader egress, hidden retention, or fabricated capability.

## Consequences

- Local and external models can share product and application contracts while
  honestly exposing different capability, latency, privacy, and cost profiles.
- Community installation remains private and deterministic until a person
  deliberately configures and enables a provider.
- Provider admission requires recurring evidence because terms, models, and
  safety characteristics can change independently of adapter code.
- Fine-grained data-class permission and redaction add configuration,
  conformance, UI, and operational work to every provider integration.
- Disabling an adapter may remove AI-assisted features, but it does not block
  deterministic learning, corrupt records, or erase which provider produced an
  earlier output.
- Managed deployments may pre-admit an adapter operationally, but they may not
  bypass the declared data-use policy, applicable learner controls, or the
  platform-owned authorization and execution boundaries.

## Alternatives Rejected

- **Local-model-only initial posture.** This minimizes external transfer but
  would make hardware-dependent capability the sole baseline, increase support
  burden, and prevent a governed external option. Local providers remain a
  supported provider class rather than the only class.
- **Enable a default external provider when credentials are available.**
  Rejected because secret presence is not informed provider selection or data-
  class permission and cannot establish current terms.
- **Allow features to call provider SDKs directly.** Rejected because it leaks
  provider semantics into domains, fragments policy and provenance, and makes
  safe disablement and fallback unreliable.
- **Treat provider admission as permanent.** Rejected because terms, models,
  security posture, cost, and capabilities change and require requalification.

## Boundaries

This decision selects provider classes and the common opt-in/data-use posture.
It does not admit a named provider, approve current provider terms, choose a
default model, license data for model use, approve an online experiment, define
organization tenancy, or authorize autonomous tools or external actions.

Local execution is not assumed safe merely because it is local. Local adapters
must still declare resources, data access, model provenance, capability,
logging, and failure behavior and pass the same applicable contract tests.

## Verification Implications

- Prove that a fresh community installation invokes no provider and transfers
  no model data until explicit configuration and enablement.
- Prove per-provider and per-data-class allow/deny behavior, including redaction,
  consent/preference, licensed-source, learner-data, and project-artifact cases.
- Prove credentials do not imply enablement and that one provider's permission
  cannot authorize another provider or another data class.
- Exercise malformed output, timeout, cancellation, quota, cost-limit, health,
  terms suspension, disablement, and outage paths with deterministic fallback.
- Prove provider-specific payloads and SDK types do not enter domain or public
  contracts and that model output cannot mutate protected state directly.
- Verify execution provenance, safe diagnostics, retention/deletion behavior,
  secret redaction, local/cloud semantic parity, and honest capability display.
- Re-run provider admission evidence when material terms, model, adapter,
  security, capability, or data-use posture changes.

## Supersession

A default-enabled provider, a new model data class, silent failover, materially
different consent posture, direct feature-to-provider access, or authoritative
model action requires a superseding decision. Admission of a concrete provider
requires its own current evidence but does not supersede this ADR when it stays
within these boundaries.
