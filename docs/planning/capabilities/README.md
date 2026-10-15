# Capability Plans

Capability plans describe coherent user or operator outcomes without selecting implementation details prematurely.

Name files `CAP-####-short-name.md` and start from [the capability template](../templates/capability-template.md). A capability should identify its intended users, observable value, scope boundaries, relevant canonical intent, decision gates, risks, and proposed vertical slices.

A capability is not a page inventory, a component list, or a release commitment. Split it when independent outcomes have different users, decisions, or acceptance evidence.

Use `shape-capability` to prepare the complete package, including the exact `slice_ids` manifest and coarse sequence for every intended slice. One explicit CAP approval is recorded in the ignored local ledger; the skill cannot approve its own proposal. Detailed slice and packet planning occurs just in time without another approval unless it materially changes the CAP package.
