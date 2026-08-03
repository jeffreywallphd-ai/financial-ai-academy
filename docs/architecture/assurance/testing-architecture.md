# Testing Architecture

- Status: accepted
- Canonical for: placement and purpose of architecture-relevant tests

## Layers

| Test layer | Primary evidence |
| --- | --- |
| Domain unit | Invariants, calculations, state transitions, edge cases |
| Application unit | Use-case orchestration, policy, authorization inputs, port behavior |
| Contract | Schema validity, compatibility, generated bindings, provider conformance |
| Adapter integration | Database, storage, provider, queue, timeout, failure, and mapping behavior |
| Architecture | Dependency direction, public surfaces, forbidden imports, module ownership |
| Host integration | Composition, configuration, authentication context, lifecycle |
| End-to-end | Important learner, administrator, portfolio, and local/cloud workflows |
| Model evaluation | Quality, grounding, learning outcomes, safety, robustness, and fallback |

## Rules

- Test the invariant at the layer that owns it.
- Important financial calculations use deterministic fixtures and independent expected results.
- Provider tests include malformed, delayed, partial, quota-exhausted, and unavailable behavior.
- Adaptive-learning tests cover eligibility and policy separately from ranking quality.
- Model evaluations do not replace deterministic application tests.
- Local and cloud qualification run the same shared contract and domain suites.

