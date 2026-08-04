# Capability Plans

Capability plans describe coherent user or operator outcomes without selecting implementation details prematurely.

Name files `CAP-####-short-name.md` and start from [the capability template](../templates/capability-template.md). A capability should identify its intended users, observable value, scope boundaries, relevant canonical intent, decision gates, risks, and proposed vertical slices.

A capability is not a page inventory, a component list, or a release commitment. Split it when independent outcomes have different users, decisions, or acceptance evidence.

Use `shape-capability` to prepare the artifact. Candidate slice selection requires explicit `capability_approval`; the skill cannot approve its own proposal.
