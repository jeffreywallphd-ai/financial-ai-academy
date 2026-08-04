# Documentation Governance

## Purpose

This documentation is the control system for Financial AI Academy. It preserves product intent, domain language, architecture boundaries, contract policy, AI/ML authority, risk posture, operations, and AI-development routing so the project can evolve without silent design drift.

## Documentation Areas and Authority

| Directory | Role | Canonical? |
| --- | --- | --- |
| `product/` | Vision, users, editions, scope, and non-goals | Yes for product intent |
| `domain/` | Financial-learning vocabulary, rules, evidence, and lifecycle meaning | Yes for domain meaning |
| `architecture/` | System structure, module ownership, contracts, data, AI, and deployment | Yes for technical architecture |
| `contracts/` | Contract catalog, semantic ownership, and conformance policy | Yes for contract governance |
| `ai-ml/` | Model, prompt, dataset, evaluation, and promotion governance | Yes for AI/ML policy |
| `risk-compliance/` | Financial-education claims, data licensing, privacy, and commercial boundaries | Yes for reviewed risk posture |
| `external-sources/` | External source register, applicability, and refresh workflows | Yes for recorded source posture; external sources remain authoritative |
| `security/` | Trust boundaries and threat models | Yes for security architecture |
| `adr/` | Durable product-technical decisions and readiness | Yes for accepted decisions |
| `standards/` | Documentation, coding, testing, contracts, security, and agent rules | Yes for implementation standards |
| `context/` | Compact task routing derived from canonical sources | No; routing only |
| `assurance/` | Verification maps, mismatches, traceability, and known gaps | Yes for evidence status |
| `operations/` | Installation, backup, migrations, outages, rollback, and qualification | Yes after acceptance |
| `planning/` | Capability shaping, vertical slices, agent work packets, and decision requests | Canonical for planning lifecycle only; never product meaning or implementation authority |
| `roadmaps/` | Accepted sequencing for bounded delivery | Only for sequence, never product semantics |
| `templates/` | Reusable authoring structures | No |
| `design/` | Interface style guide, design-system authority, iconography, and directional mockups | Style guide and production asset rules are canonical; mockups are guidance only |

## Authority Precedence

1. Accepted ADRs govern the specific decisions they record until superseded.
2. Product and domain documents govern intent and semantic meaning.
3. Executable schemas under `contracts/` govern exact external shapes.
4. Architecture documents govern ownership and dependency direction.
5. Risk, external-source, and security documents govern reviewed claims and trust boundaries.
6. Standards govern how changes are planned, implemented, and verified.
7. Context packs summarize and route; they never override canonical sources.
8. Chat, issue text, temporary plans, and generated summaries are noncanonical unless deliberately promoted.

External laws, standards, and provider terms are not replaced by repository summaries. Record applicability and review evidence without presenting a local interpretation as external authority.

If canonical sources conflict, stop and reconcile or record the conflict in `assurance/docs-mismatch-register.md`.

## Required Agent Startup

For non-trivial work:

1. Read this file and `context/packs/index.pack.md`.
2. Use `context/prompt-routing.md` and `context/pack-catalog.json`.
3. Apply `standards/change-impact-matrix.md`.
4. Consult `adr/decision-readiness.md` for architecture-sensitive work.
5. For interface work, read `design/README.md`, `design/style-guide.md`, and `standards/interface-design-standards.md`.
6. For planning work, read `planning/README.md`, `planning/register.md`, `planning/concurrent-work.md`, and `planning/skills/README.md`.
7. Read only the task-specific canonical sources and inspect affected implementation/tests.

## Current Foundation

- [Product Vision and Scope](product/product-vision-and-scope.md)
- [Community and Commercial Editions](product/community-and-commercial-editions.md)
- [Non-Goals](product/non-goals.md)
- [Domain Map](domain/README.md)
- [Architecture Map](architecture/README.md)
- [Contract Governance](contracts/README.md)
- [AI/ML Governance](ai-ml/README.md)
- [Risk and Compliance Posture](risk-compliance/README.md)
- [Decision Readiness](adr/decision-readiness.md)
- [Repository Standards](standards/README.md)
- [Interface Design System](design/README.md)
- [Automated Development Planning](planning/README.md)
- [Governed Planning Skill Suite](planning/skills/README.md)
- [Concurrent Automated Work](planning/concurrent-work.md)

## Documentation Update Rule

Update canonical documentation, related ADRs, affected context packs, and verification evidence in the same change when behavior or boundaries change. Do not update a context pack without first reconciling its canonical source.

Shared interface changes must also keep the style guide, executable design tokens, icon assets and manifest, consuming components, and applicable visual/accessibility tests synchronized.

Planning-system changes must keep the planning guide, register, concurrent-work protocol, artifact templates, approval and ownership metadata, suite manifest, router, prompt evaluations, developer tools, and affected context guidance synchronized. Run `python dev-tools/agent/check_ready.py`; add `--base-ref <revision>` when validating lifecycle transitions against a known base.
