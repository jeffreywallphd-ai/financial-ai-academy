# Architecture Verification

- Status: current
- Canonical for: architecture-evidence routing

The current invariant-to-evidence map is maintained in `docs/architecture/assurance/architecture-verification.md`.

At this foundation stage, application architecture checks are gaps because no application code, generated contracts, or deployment manifests exist. Documentation links and context-catalog structure have direct evidence through `python dev-tools/documentation/check_docs.py`. New implementation must add or update the owning verification row in the same change.

Planned verification categories:

- module dependency direction,
- contract schema/catalog integrity,
- deterministic generation,
- provider conformance,
- local/cloud shared-core composition,
- AI authority boundaries,
- financial-data normalization and calculation invariants,
- documentation/context integrity.
