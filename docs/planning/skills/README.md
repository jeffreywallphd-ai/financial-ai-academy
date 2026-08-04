# Governed Planning Skill Suite

- Status: accepted
- Canonical for: planning-skill compatibility, packaging, routing, and approval-stage behavior

## Skill Catalog

| Skill | Responsibility | Default file behavior |
| --- | --- | --- |
| [`guide-next-planning-action`](guide-next-planning-action/SKILL.md) | Recommend the next governed action and route to another skill | Read-only |
| [`shape-capability`](shape-capability/SKILL.md) | Shape one bounded capability | Writes only when authorized |
| [`review-decision-gates`](review-decision-gates/SKILL.md) | Classify and route unresolved decisions | Writes only when authorized |
| [`select-vertical-slice`](select-vertical-slice/SKILL.md) | Score candidates and recommend one vertical slice | Writes only when authorized |
| [`author-agent-work-packet`](author-agent-work-packet/SKILL.md) | Author bounded agent work packets | Writes only when authorized |
| [`approve-planned-work`](approve-planned-work/SKILL.md) | Record an explicit authorized human decision | Writes only after explicit approval |
| [`implement-vertical-slice`](implement-vertical-slice/SKILL.md) | Execute approved packets for one slice | Requires a current explicit implementation request |
| [`verify-and-close-slice`](verify-and-close-slice/SKILL.md) | Verify evidence and request completion acceptance | Writes only when authorized |

Use `guide-next-planning-action` for broad prompts such as “what would you suggest we do next?” It recommends one action but never treats advice as implementation authority.

## Shared Compatibility Contract

The suite uses:

- IDs `CAP-*`, `DEC-*`, `SLI-*`, and `WRK-*`;
- planning states `captured`, `shaping`, `decision-blocked`, `ready`, `active`, `verifying`, `complete`, and `superseded`;
- approval decisions `pending`, `approved`, `changes-requested`, and `rejected`;
- six independent approval prefixes: `capability`, `decision`, `selection`, `planning`, `implementation`, and `completion`;
- flat `<stage>_approval`, `<stage>_approved_by`, and `<stage>_approved_at` metadata;
- a separate `implementation_authority` reference on work packets.
- repository-relative `write_scope` and `generated_artifacts`, plus durable activation evidence in `base_revision`, `claim_id`, `claimed_by`, and `claimed_at`.

An agent may prepare a review and record an explicit human decision. It may not self-approve. Planning readiness, a roadmap, or an earlier approval never supplies a later approval automatically.

Every file-changing skill prominently requires applicable `AGENTS.md` and repository-root `docs/README.md` to be read and followed before editing.

## Portability

Each immediate child skill folder is self-contained and has no required sibling-file import. The router has soft dependencies: when another skill is unavailable, it names the missing skill instead of silently reproducing its mutating workflow.

The folders follow the [Agent Skills specification](https://agentskills.io/specification) and include Codex UI metadata. This documentation location is the canonical source. Synchronize all eight skills into this repository's supported discovery path with:

```text
python docs/planning/skills/sync_skills.py --mode auto
python docs/planning/skills/sync_skills.py --check
```

The helper uses canonical symlinks where supported and falls back to managed copies. It refuses to overwrite unmanaged skill folders. `.agents/skills/` is ignored so installed copies never compete with the canonical documentation source.

Create standalone archives with:

```text
python docs/planning/skills/package_skills.py --output <directory>
```

Each archive places `SKILL.md` at its root. Archives are generated artifacts and are not committed by default.

## Validation

```text
python docs/planning/skills/validate_suite.py
python docs/planning/skills/test_suite.py
python docs/planning/skills/evaluate_scenarios.py --responses docs/planning/skills/evals/reference-responses.json
python dev-tools/documentation/check_docs.py
```

The suite validator checks skill metadata, required resources, UI prompts, Python syntax, repository-entry gates, ownership fields, and cross-skill routing references. The prompt-level evaluation catalog exercises routing, approval separation, advice-only behavior, implementation authority, and completion claims. Its grader accepts the same structured response contract for captured agent runs; the committed reference responses verify the harness deterministically without network or model access. Each skill also includes a task-specific deterministic validator or gate checker.
