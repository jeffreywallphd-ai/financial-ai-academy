# Security and Privacy Standards

- Status: proposed
- Canonical for: baseline security and privacy behavior

Apply a proportional security and privacy screen to every change.

At minimum, identify:

- protected data and assets,
- actors and authority,
- trust boundaries,
- untrusted inputs and external outputs,
- provider/model/data egress,
- abuse and failure cases,
- owning controls and denial evidence,
- logging/redaction implications,
- retention, rollback, and residual risk.

Keep learner context, provider secrets, market-data licenses, model inputs, prompts, diagnostics, and tenant identity least-privileged and explicitly scoped. New public exposure, executable plugins, identity flows, encryption, or external processing requires an accepted threat/architecture decision.

