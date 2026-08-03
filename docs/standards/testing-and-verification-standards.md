# Testing and Verification Standards

- Status: accepted
- Canonical for: evidence expected from repository changes

## General Rules

- Test the invariant at the layer that owns it.
- Add regression evidence for meaningful defects.
- Verify failure, denial, timeout, malformed input, and degraded-provider behavior where relevant.
- Use deterministic fixtures for financial calculations and independent expected results.
- Separate schema validation, business invariants, authorization, and model-quality evaluation.
- Do not substitute end-to-end tests for focused domain or contract evidence.
- Do not substitute model evaluation for deterministic application tests.

## Change Completion

A change reports:

- focused checks run during implementation,
- applicable architecture, contract, documentation, security, and full-suite gates,
- environment or external qualifications not performed,
- raw failures separately from normalized repository-runner output.

## Test Data

Do not commit personal learner information, secrets, provider credentials, restricted datasets, or production payloads. Synthetic and licensed fixtures retain source/creation and permitted-use metadata.

