# Implementation Preflight

- Current user instruction explicitly authorizes implementation of the named slice and frozen packet bundle.
- Applicable `AGENTS.md` and repository-root `docs/README.md` were read and followed.
- Slice selection approval is recorded in the ignored local ledger.
- Every in-scope packet has local planning and implementation approval; bundle membership exactly matches the supplied packet set.
- Every local implementation approval records an actor label, date, scoped authority, and a scope exactly equal to the current packet `write_scope`.
- No approval or reviewer evidence appears in tracked artifacts or the planning register.
- No artifact is decision-blocked and decision readiness remains current.
- Canonical sources, contracts, implementation, consumers, tests, and nearest README were inspected.
- Before each claim, dependencies are complete, the packet remains in the approved bundle, and active write scopes do not overlap.
- Each packet declares bounded write scope and generated artifacts; activation will record base revision, claim ID, owner, and UTC claim time.
- Focused and repository verification commands are executable.
- External, destructive, credentialed, production, publication, commit, and push actions retain separate authority.
- Execute, verify, and complete one packet at a time; changed or newly added packets require renewed approval.
