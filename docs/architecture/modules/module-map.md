# Initial Module Map

- Status: proposed
- Canonical for: initial module ownership hypotheses
- Decision gate: refine domain boundaries before implementing a module whose ownership is unclear

| Module | Primary responsibility | Publishes |
| --- | --- | --- |
| Identity | Users, organizations, memberships, roles, entitlement references | Identity and membership changes |
| Content | Versioned learning resources, provenance, publication state | Content-version events |
| Curriculum | Competencies, prerequisites, pathways, course structure | Curriculum-version events |
| Assessment | Items, attempts, scoring evidence, review state | Assessment evidence |
| Learner model | Derived mastery, preferences, accommodations, progress projections | Learner-state changes |
| Adaptation | Eligibility, ranking, deterministic policy, recommendations | Recommendation decisions and outcomes |
| Market data | Instruments, observations, calendars, corporate actions, provider provenance | Canonical market-data events |
| Portfolio | Simulated accounts, positions, transactions, valuation, backtests | Portfolio and simulation results |
| AI orchestration | Model-provider gateway, prompt/model policy, grounded generation, evaluation hooks | AI execution records |
| Audit | Append-oriented decision, provenance, and administrative evidence | Exportable audit records |

## Boundary Notes

- Assessment evidence is an input to the learner model; assessment does not directly decide mastery.
- Adaptation reads approved learner and curriculum projections; it does not mutate curriculum or assessment history.
- AI orchestration supplies bounded capabilities. It does not own learning, grading, market, or portfolio rules.
- Market data normalizes provider observations. Portfolio behavior consumes canonical market data, never raw provider responses.
- Audit captures evidence from owning modules without becoming a second business database.

This map is intentionally provisional. Domain documentation and early vertical slices should validate names and ownership before the map is marked accepted.

