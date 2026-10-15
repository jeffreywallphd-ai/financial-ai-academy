# Vertical Slice Plans

Vertical slices are the smallest end-to-end increments that produce observable user or operator value while respecting module and contract boundaries.

Name files `SLI-####-short-name.md` and start from [the vertical-slice template](../templates/vertical-slice-template.md). Each slice links one parent capability, identifies the contracts and layers it crosses, defines scenario-based acceptance, and lists its agent work packets in dependency order.

Avoid horizontal slices such as “build all persistence” or “build all UI” unless they are independently valuable platform-enabling outcomes with explicit consumers and acceptance evidence.

Use `select-vertical-slice` to refine the next manifest slice just before it starts. Deterministic readiness, CAP conformance, verification, and closure remain required, but no slice-selection or completion approval exists.
