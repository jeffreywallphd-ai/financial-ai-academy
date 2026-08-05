# Product Capability Catalog

- Status: proposed
- Canonical for: candidate product capability inventory and capability boundaries

## Purpose

This catalog translates the current product vision, page concepts, and cross-cutting features into outcome-oriented product capabilities. It is an input to governed planning, not a delivery sequence, implementation specification, release commitment, or record of approval.

A capability from this catalog becomes planned work only after it is shaped as a bounded `CAP-*` artifact, reviewed against current canonical sources and decision readiness, and explicitly approved through the planning lifecycle.

## Learner Experience Capabilities

| Capability | Brief description |
| --- | --- |
| Discover learning opportunities | Let learners search, filter, compare, and understand available courses, lessons, labs, and projects by topic, level, duration, prerequisites, and availability. |
| Navigate a competency-based curriculum | Show learning objectives, competency relationships, prerequisites, optional branches, completion states, and the requirements for advancing through a curriculum. |
| Participate in structured lessons | Let learners work through versioned educational content, examples, citations, notes, embedded activities, and knowledge checks in a coherent lesson workspace. |
| Practice and demonstrate understanding | Provide diagnostic and formative questions, scenarios, exercises, feedback, targeted review, and repeatable opportunities to produce learning evidence. |
| Complete applied projects | Support guided and open-ended financial, quantitative, AI, and ML projects with milestones, datasets, notebooks, saved results, reflections, and submissions. |
| Track progress and competency evidence | Give learners an explainable view of completions, attempts, feedback, evidence history, strengths, review needs, and competency or mastery projections. |
| Follow an adaptive learning pathway | Recommend eligible next activities based on evidence, goals, prerequisites, and deterministic policy, while explaining why each recommendation was made and allowing learner choice. |
| Learn with grounded AI assistance | Offer learner-controlled tutoring and content interaction grounded in approved educational sources, with citations, limitations, safe fallbacks, and clear separation from authoritative grading or financial advice. |

## Financial and Analytical Capabilities

| Capability | Brief description |
| --- | --- |
| Explore canonical market data | Let learners retrieve, inspect, chart, compare, and export provider-neutral market data while seeing timestamps, coverage, quality indicators, attribution, and provenance. |
| Perform financial and quantitative analysis | Provide educational workflows for financial metrics, valuation concepts, comparisons, and reproducible calculations using explicit assumptions and traceable inputs. |
| Build and evaluate simulated portfolios | Let learners create educational portfolios, allocate assets, select benchmarks, rebalance, inspect performance and risk measures, and record decisions without representing custody or live trading. |
| Run backtests and scenario analyses | Let learners test historical strategies, stress scenarios, and portfolio assumptions with reproducible inputs, transparent limitations, and clear separation between simulation and observed results. |
| Conduct financial AI and ML experiments | Support dataset selection, feature work, model experiments, evaluation, leakage and overfitting checks, model cards, reproducibility, and comparison of results in a guided learning context. |

## Personal Learning and Knowledge Capabilities

| Capability | Brief description |
| --- | --- |
| Maintain a personal learning workspace | Preserve a learner's notes, bookmarks, charts, datasets, simulations, notebooks, projects, and AI conversations so work can be resumed and connected across activities. |
| Set learning goals and preferences | Let learners record goals, experience, interests, accessibility needs, theme choices, AI-assistance preferences, notification choices, and appropriate privacy controls. |
| Export and retain portable learning records | Let learners export their evidence, progress, saved work, and supported data in documented portable formats, with local backup and recovery appropriate to the deployment profile. |
| Understand platform methods and limitations | Provide searchable help, financial and AI/ML glossaries, adaptive-learning explanations, methodology, provenance guidance, AI limitations, and education-versus-advice boundaries. |

## Instructor and Content Capabilities

| Capability | Brief description |
| --- | --- |
| Author and maintain learning experiences | Let authorized creators develop, review, version, and publish curricula, lessons, examples, assessments, projects, competency mappings, and supporting sources through an accepted content format. |
| Review learner evidence and provide feedback | Let instructors inspect permitted evidence and project work, provide feedback, request revision, and make approved overrides with authorization and audit evidence. |
| Guide cohorts and learning organizations | Give authorized instructors or organization leaders privacy-aware views of cohort participation, progress, review needs, and learning outcomes without replacing individual evidence. |

## Platform and Operator Capabilities

| Capability | Brief description |
| --- | --- |
| Connect and govern replaceable providers | Let authorized operators configure market-data, model, content, storage, identity, and job providers through platform-owned contracts, with capability, health, quota, attribution, licensing, and failure visibility. |
| Manage identities, organizations, roles, and entitlements | Support the appropriate local and cloud identity, membership, authorization, organization, and edition-entitlement experiences after the governing identity and tenancy decisions are accepted. |
| Preserve provenance and accountable history | Maintain traceable origins, versions, transformations, and relevant audit history for learning evidence, recommendations, content, market data, datasets, model output, simulations, and administrative actions. |
| Operate the community edition locally | Enable an individual or contributor to install, configure, use, back up, restore, and upgrade the open-source platform locally with supported free-data and externally configured provider connections. |
| Operate a managed cloud service | Enable qualified operators to run the shared platform core as a secure, observable, scalable, recoverable, and supportable managed service without creating different domain behavior. |
| Administer platform health and usage | Provide authorized operational visibility into provider health, jobs, storage, model and data usage, failures, audit events, and edition-appropriate service limits. |

## Cross-Capability Expectations

Every shaped capability should preserve the applicable expectations below rather than recreating them as separate features:

- educational use without brokerage, custody, personalized suitability, guaranteed outcomes, or autonomous financial action;
- deterministic authority for eligibility, authorization, grading, financial calculations, and durable state changes;
- provenance and versioning for learning, financial-data, simulation, dataset, model, recommendation, and generated-content evidence;
- explicit distinction among observed data, calculated results, simulations, model predictions, and AI-generated interpretation;
- shared semantic behavior across local community and managed-cloud deployment profiles;
- provider-neutral internal meaning and replaceable external integrations;
- accessible, responsive light, dark, and system-theme experiences;
- safe failure, understandable limitations, learner control, and portable data where applicable.

## Use in Planning

When planning draws from this catalog:

1. Select one observable user or operator outcome; do not treat an entire table or page as one capability.
2. Confirm the outcome against the current product vision, domain meaning, risk posture, architecture, and decision-readiness register.
3. Shape a new `CAP-*` artifact with explicit in-scope and out-of-scope boundaries, decision gates, risks, acceptance evidence, and proposed slices.
4. Reserve formal planning identifiers through the repository planning tools and update the planning register with the artifact.
5. Request capability-framing approval separately; catalog inclusion does not supply approval or implementation authority.

The catalog intentionally does not assign priority or delivery order. Sequencing begins only after individual capabilities are shaped and approved.
