# AI and ML System Boundaries

- Status: accepted
- Canonical for: authority and placement of AI/ML capabilities

## Capability Boundary

All model access passes through platform-owned application ports and the AI-orchestration module. Domain modules do not import provider SDKs or depend on provider-specific prompts, model names, response types, or billing behavior.

## Appropriate Uses

- tutoring and explanation,
- grounded question or content drafting,
- recommendation ranking,
- embeddings and retrieval support,
- content classification,
- experiment analysis,
- bounded summarization of learner-authorized information.

## Prohibited Authority

Model output is not authoritative for:

- authentication or authorization,
- grades or mastery evidence without defined scoring policy,
- financial calculations or accounting identities,
- portfolio transactions or durable state mutation,
- provider licensing interpretation,
- prerequisites or safety gates,
- claims of educational, investment, regulatory, or legal suitability.

## Execution Record

Record the model-provider identity, model/policy version, prompt/template version, input references or hashes, retrieval sources, parameters, output status, validation result, latency, cost where available, and safety/policy outcome. Sensitive prompts and learner data require redaction and retention controls.

## Local and Cloud

The same model-provider port supports local and external models. Product behavior reports capability differences honestly rather than presenting an unsupported local capability as equivalent. Deterministic fallback behavior is preferred for essential learning flows.

