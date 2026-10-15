# Planning Register

- Status: current
- Canonical for: inventory and lifecycle state of planning artifacts

Every capability, vertical slice, work packet, and decision request is listed here. Update this register and the artifact metadata together. Approval and reviewer evidence is local-only and must never be summarized in this tracked register.

Reserve new identifiers through `dev-tools/planning/reserve_id.py` before creating artifacts. A reservation is ignored local coordination state and does not replace this durable register entry.

| ID | Kind | Title | Planning status | Parent | Dependencies | Decision gates | Owner | Updated |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAP-0001 | Capability | [Complete a Structured Introductory Lesson](capabilities/CAP-0001-complete-structured-introductory-lesson.md) | ready | none | none | resolved by ADR-0005 through ADR-0008 | unassigned | 2026-08-04 |
| CAP-0002 | Capability | [Operate the AI-Development Control Plane](capabilities/CAP-0002-operate-ai-development-control-plane.md) | complete | none | none | none | codex-control-plane | 2026-10-15 |
| CAP-0003 | Capability | [Plan and Orchestrate Capability Portfolios](capabilities/CAP-0003-plan-and-orchestrate-capability-portfolios.md) | complete | none | CAP-0002 | none | codex-cap-0003 | 2026-10-15 |
| SLI-0001 | Vertical slice | [Open an Approved Versioned Lesson](vertical-slices/SLI-0001-open-approved-versioned-lesson.md) | verifying | CAP-0001 | none | none | codex-agent | 2026-08-05 |
| SLI-0003 | Vertical slice | [Resume and Submit an Interrupted Work Packet](vertical-slices/SLI-0003-resume-submit-interrupted-work-packet.md) | complete | CAP-0002 | none | none | codex-control-plane | 2026-10-15 |
| SLI-0004 | Vertical slice | [Select Affected Checks and Record Verification Receipts](vertical-slices/SLI-0004-select-affected-checks-and-record-receipts.md) | complete | CAP-0002 | SLI-0003 | none | codex-control-plane | 2026-10-15 |
| SLI-0005 | Vertical slice | [Record Review Findings and Corrected Descendants](vertical-slices/SLI-0005-record-review-findings-and-corrected-descendants.md) | complete | CAP-0002 | SLI-0004 | none | codex-control-plane | 2026-10-15 |
| SLI-0006 | Vertical slice | [Enforce Policy and Project Operator Status](vertical-slices/SLI-0006-enforce-policy-and-project-operator-status.md) | complete | CAP-0002 | SLI-0003, SLI-0004, SLI-0005 | none | codex-control-plane | 2026-10-15 |
| SLI-0007 | Vertical slice | [Close Packet Start and Bound Recovery Routes](vertical-slices/SLI-0007-close-packet-start-and-bound-recovery-routes.md) | complete | CAP-0002 | SLI-0006 | none | codex-control-plane | 2026-10-15 |
| SLI-0008 | Vertical slice | [Qualify Control-Plane Safety and Friction](vertical-slices/SLI-0008-qualify-control-plane-safety-and-friction.md) | complete | CAP-0002 | SLI-0007 | none | codex-control-plane | 2026-10-15 |
| SLI-0009 | Vertical slice | [Project the Capability Delivery Hierarchy](vertical-slices/SLI-0009-project-capability-hierarchy.md) | complete | CAP-0003 | none | none | codex-cap-0003 | 2026-10-15 |
| SLI-0010 | Vertical slice | [Explain Ready Work and Proposed Order](vertical-slices/SLI-0010-explain-ready-work-and-order.md) | complete | CAP-0003 | SLI-0009 | none | codex-cap-0003 | 2026-10-15 |
| SLI-0011 | Vertical slice | [Identify Parallel-Safe Work](vertical-slices/SLI-0011-identify-parallel-safe-work.md) | complete | CAP-0003 | SLI-0009 | none | codex-cap-0003 | 2026-10-15 |
| SLI-0012 | Vertical slice | [Coordinate Exclusive File Edits](vertical-slices/SLI-0012-coordinate-exclusive-file-edits.md) | complete | CAP-0003 | SLI-0011 | none | codex-cap-0003 | 2026-10-15 |
| SLI-0013 | Vertical slice | [Propose Hierarchy-Aware Agent Allocations](vertical-slices/SLI-0013-propose-hierarchy-aware-agent-allocations.md) | complete | CAP-0003 | SLI-0010, SLI-0011, SLI-0012 | none | codex-cap-0003 | 2026-10-15 |
| SLI-0014 | Vertical slice | [Qualify the Portfolio Control Plane](vertical-slices/SLI-0014-qualify-portfolio-control-plane.md) | complete | CAP-0003 | SLI-0009, SLI-0010, SLI-0011, SLI-0012, SLI-0013 | none | codex-cap-0003 | 2026-10-15 |
| WRK-0001 | Work packet | [Establish Executable Lesson-Package Contracts](work-packets/WRK-0001-establish-lesson-package-contracts.md) | complete | SLI-0001 | none | none | codex-agent | 2026-08-05 |
| WRK-0002 | Work packet | [Deliver the Approved-Lesson Read Core](work-packets/WRK-0002-deliver-approved-lesson-read-core.md) | complete | SLI-0001 | WRK-0001 | none | codex-agent | 2026-08-05 |
| WRK-0003 | Work packet | [Expose the Single-Profile Lesson API](work-packets/WRK-0003-expose-single-profile-lesson-api.md) | complete | SLI-0001 | WRK-0002 | none | codex-agent | 2026-08-05 |
| WRK-0004 | Work packet | [Deliver the Accessible Lesson-Reading Page](work-packets/WRK-0004-deliver-accessible-lesson-reading-page.md) | complete | SLI-0001 | WRK-0003 | none | codex-agent | 2026-08-05 |
| WRK-0005 | Work packet | [Qualify the Approved-Lesson Vertical Slice](work-packets/WRK-0005-qualify-approved-lesson-slice.md) | complete | SLI-0001 | WRK-0004 | none | codex-agent | 2026-08-05 |
| WRK-0011 | Work packet | [Deliver the Interruption-Safe Packet Lifecycle](work-packets/WRK-0011-deliver-interruption-safe-packet-lifecycle.md) | complete | SLI-0003 | none | none | codex-control-plane | 2026-10-15 |
| WRK-0012 | Work packet | [Deliver Affected Verification Receipts](work-packets/WRK-0012-deliver-affected-verification-receipts.md) | complete | SLI-0004 | WRK-0011 | none | codex-control-plane | 2026-10-15 |
| WRK-0013 | Work packet | [Deliver Review and Resubmission Lineage](work-packets/WRK-0013-deliver-review-and-resubmission-lineage.md) | complete | SLI-0005 | WRK-0012 | none | codex-control-plane | 2026-10-15 |
| WRK-0014 | Work packet | [Deliver Policy Reports and Operator Status](work-packets/WRK-0014-deliver-policy-reports-and-operator-status.md) | complete | SLI-0006 | WRK-0013 | none | codex-control-plane | 2026-10-15 |
| WRK-0015 | Work packet | [Deliver Start, Correction, and Maintenance Routes](work-packets/WRK-0015-deliver-start-correction-and-maintenance-routes.md) | complete | SLI-0007 | WRK-0014 | none | codex-control-plane | 2026-10-15 |
| WRK-0016 | Work packet | [Deliver Control-Plane Qualification](work-packets/WRK-0016-deliver-control-plane-qualification.md) | complete | SLI-0008 | WRK-0015 | none | codex-control-plane | 2026-10-15 |
| WRK-0017 | Work packet | [Deliver the Capability Hierarchy Graph](work-packets/WRK-0017-deliver-capability-hierarchy-graph.md) | complete | SLI-0009 | none | none | codex-cap-0003 | 2026-10-15 |
| WRK-0018 | Work packet | [Deliver Ready-Work Ordering](work-packets/WRK-0018-deliver-ready-work-ordering.md) | complete | SLI-0010 | WRK-0017 | none | codex-cap-0003 | 2026-10-15 |
| WRK-0019 | Work packet | [Deliver Parallel Compatibility](work-packets/WRK-0019-deliver-parallel-compatibility.md) | complete | SLI-0011 | WRK-0017 | none | codex-cap-0003 | 2026-10-15 |
| WRK-0020 | Work packet | [Deliver File-Edit Coordination](work-packets/WRK-0020-deliver-file-edit-coordination.md) | complete | SLI-0012 | WRK-0019 | none | codex-cap-0003 | 2026-10-15 |
| WRK-0021 | Work packet | [Deliver Agent Allocation and Replanning](work-packets/WRK-0021-deliver-agent-allocation-and-replanning.md) | complete | SLI-0013 | WRK-0018, WRK-0019, WRK-0020 | none | codex-cap-0003 | 2026-10-15 |
| WRK-0022 | Work packet | [Deliver Portfolio Control-Plane Qualification](work-packets/WRK-0022-deliver-portfolio-control-plane-qualification.md) | complete | SLI-0014 | WRK-0017, WRK-0018, WRK-0019, WRK-0020, WRK-0021 | none | codex-cap-0003 | 2026-10-15 |
| WRK-0023 | Work packet | [Enforce Active Authority on Lease Renewal](work-packets/WRK-0023-enforce-active-authority-on-lease-renewal.md) | complete | SLI-0012 | WRK-0020 | none | codex-cap-0003 | 2026-10-15 |
| DEC-0001 | Decision request | [Assign Ownership for the First Learning Loop](decision-requests/DEC-0001-learning-module-ownership.md) | complete | none | none | resolved by ADR-0005 | unassigned | 2026-08-04 |
| DEC-0002 | Decision request | [Establish Local Learner Identity](decision-requests/DEC-0002-local-learner-identity.md) | complete | none | none | resolved by ADR-0006 | unassigned | 2026-08-04 |
| DEC-0003 | Decision request | [Choose the Initial Versioned Lesson Package](decision-requests/DEC-0003-versioned-lesson-package-format.md) | complete | none | none | resolved by ADR-0007 | unassigned | 2026-08-04 |
| DEC-0004 | Decision request | [Set the Local Learner-Evidence Protection and Recovery Baseline](decision-requests/DEC-0004-local-learner-evidence-protection-recovery.md) | complete | none | none | resolved by ADR-0008 | unassigned | 2026-08-04 |
| DEC-0005 | Decision request | [Set the Initial Application Framework and Runtime Baseline](decision-requests/DEC-0005-initial-application-framework-runtime-baseline.md) | complete | none | none | resolved by ADR-0009 | unassigned | 2026-08-04 |
| DEC-0006 | Decision request | [Choose the Capability-Level Approval Topology](decision-requests/DEC-0006-capability-level-approval-topology.md) | complete | none | none | none | unassigned | 2026-10-15 |
