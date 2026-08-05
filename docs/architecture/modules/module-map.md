# Module Map

- Status: partially accepted
- Canonical for: accepted first learning-loop ownership and remaining module hypotheses
- Related ADRs: [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md), [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md), [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
- Decision gate: use accepted first-loop boundaries; refine every still-proposed boundary before implementation

| Module | Status | Primary responsibility | Publishes |
| --- | --- | --- | --- |
| Identity | accepted for first learner context | Provider-neutral actors and learners, provider bindings, authentication context, sessions, and application permission inputs | Identity, binding, and session changes |
| Content | accepted; lesson read core implemented | Versioned learning resources, provenance, publication state, safe body nodes, and private content storage references | Content-version events remain future work |
| Curriculum | accepted; lesson placement/read core implemented | Competencies, prerequisites, pathways, course structure, and exact versioned activity placement | Curriculum-version events remain future work |
| Assessment | accepted for first learning loop | Items, attempts, responses, deterministic scoring evidence, review state, and bounded completion evidence | Assessment evidence |
| Learner model | accepted for first learning loop | Derived mastery, preferences, accommodations, completion, and progress projections | Learner-state changes |
| Adaptation | proposed | Eligibility, ranking, deterministic policy, recommendations | Recommendation decisions and outcomes |
| Market data | proposed | Instruments, observations, calendars, corporate actions, provider provenance | Canonical market-data events |
| Portfolio | proposed | Simulated accounts, positions, transactions, valuation, backtests | Portfolio and simulation results |
| AI orchestration | proposed | Model-provider gateway, prompt/model policy, grounded generation, evaluation hooks | AI execution records |
| Audit | accepted for first learning loop | Append-oriented decision, provenance, administrative evidence, and source-event integrity references | Exportable audit records |

## Boundary Notes

- Assessment evidence is an input to the learner model; assessment does not directly decide mastery.
- Curriculum may retain immutable Content and Assessment version identifiers but cannot access those modules' internals or persistence.
- Learner-model completion and progress are projections that retain source-evidence references and never replace Assessment evidence.
- Adaptation reads approved learner and curriculum projections; it does not mutate curriculum or assessment history.
- AI orchestration supplies bounded capabilities. It does not own learning, grading, market, or portfolio rules.
- Market data normalizes provider observations. Portfolio behavior consumes canonical market data, never raw provider responses.
- Audit captures references and integrity evidence from owning modules without becoming a second business database.
- Content owns ADR-0007 package identity, publication, lesson body, educational-source provenance, and storage references. Assessment owns the meaning and runtime use of packaged assessment definitions.

ADR-0005 accepts the Content, Curriculum, Assessment, Learner model, and Audit boundaries only for the first learning loop. Other rows remain hypotheses until their own discovery and decisions establish implementation authority.

ADR-0006 additionally accepts Identity ownership for the first learner context. Organization membership, tenancy, enterprise administration, and other Identity responsibilities remain proposed.

ADR-0007 additionally accepts the portable versioned lesson-package boundary.
Executable version 1 schemas, admission validation, PostgreSQL Content metadata,
and local filesystem objects now exist for the approved lesson-read seam.
Archive transport, managed object storage, removal policy, and broader content
operations remain subject to later approved delivery planning.

## Implemented Lesson-Read Seams

- Content exposes package admission and exact published-version reads through
  `backend/src/financial_ai_academy/modules/content/public.py`.
- Curriculum exposes exact placement creation and safe placed-lesson reads
  through `backend/src/financial_ai_academy/modules/curriculum/public.py`.
- Curriculum uses its Content gateway and imports only the Content public
  surface. Automated architecture tests reject Content-internal imports and
  cross-module repository access.
- Content owns `content.lesson_package_versions` and its private object key.
  Curriculum owns `curriculum.lesson_placements` and stores only package ID,
  semantic version, and digest. There is deliberately no cross-module database
  foreign key.
- Admission creates a closed safe body-node union before publication. API and
  browser layers must consume that union and cannot request raw CommonMark or
  an HTML fragment.

Assessment execution, learner evidence, projections, Audit delivery, module
events, API hosts, and managed-cloud adapters remain outside this implemented
seam.
